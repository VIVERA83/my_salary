import json
from typing import Any, Dict, Literal
from uuid import uuid4

from base.base_accessor import BaseAccessor
from core.settings import AuthorizationSettings
from core.utils import Token
from fastapi import Response, Request
from icecream import ic
from pydantic import EmailStr
from store.user_manager.utils import User, set_cookie, unset_cookie

NAME = Dict["name", str]
EMAIL = Dict["email", EmailStr]

USER_DATA_KEY = Literal[
    "name",
    "email",
    "password",
    "is_superuser",
    "refresh_token",
    "access_token",
]

CREATE_USER_DATA = Dict[NAME | EMAIL, Any]
USER_DATA = Dict[
    NAME,
    EMAIL,
]
ic.includeContext = True


class UserManager(BaseAccessor):
    def _init(self):
        self.settings = AuthorizationSettings()

    async def create_user(self, **user_data: CREATE_USER_DATA) -> User:
        """Create temporary user data.

        1. Check email address in cache.
        2. Check email in database.
        3. Create token for verification email address
        4. Save the temporary data in Redis
        5. Send letter in email for verification email addresses.

        Args:
            user_data: Requested user data
        """
        user = User(**user_data)
        seconds = await self.app.store.cache.ttl(user.email)
        assert -1 > seconds, \
            (f"A letter has been sent to this email address '{user.email}',"
             f" check the email or the address is not specified correctly."
             f"Resending an email is possible after {seconds} seconds")
        assert not await self.app.store.auth.get_user_by_email(user.email), \
            f"Email is already in use, try other email address, not these '{user.email}'"
        token = self.app.store.token.create_verification_token(uuid4().hex, user.email)
        await self.app.store.cache.set(user.email, user.as_string, 180)
        await self.app.store.ems.send_message_to_confirm_email(user.email, user.name, token, link="test")
        return user

    async def user_registration(self, token: Token, response: Response) -> dict[USER_DATA_KEY, Any]:
        """Registration new user.

        Save in database user data, creates tokens."""
        user_data = await self.app.store.cache.get(token.email)
        assert user_data, "User data, not found, please try again creating user"
        user = User(**json.loads(user_data))

        async with self.app.postgres.session.begin().session as session:
            new_user = await self.app.store.auth.create_user(
                user.name, user.email, user.password, user.is_superuser, False
            )
            user_blog = await self.app.store.blog.create_user(
                new_user.id, new_user.name, new_user.email, False
            )
            session.add_all([new_user, user_blog])
            access_token, refresh_token = self.create_access_refresh_cookie(new_user.id.hex, new_user.email, response)
            await self.app.store.cache.set(token.token, new_user.id.hex, self.settings.auth_access_expires_delta)
            await session.commit()
        return {**new_user.as_dict(), "access_token": access_token}

    async def login(self, response: Response, **user_data) -> dict[USER_DATA_KEY, Any]:
        """Login user amd create new tokens."""
        user = await self.app.store.auth.get_user_by_email(user_data["email"])
        assert user, "User not found"
        assert user.password == user_data["password"], "Password is incorrect"
        access_token, refresh_token = self.create_access_refresh_cookie(user.id.hex, user.email, response)
        return {**user.as_dict(), "access_token": access_token}

    async def logout(self, response: Response, user_id: str, token: str, expire: int):
        unset_cookie("refresh", response)
        await self.app.store.cache.set(token, user_id, expire + 5)
        await self.app.store.auth.add_refresh_token_to_user(user_id)

    async def refresh(self, request: Request, response: Response) -> dict[USER_DATA_KEY, Any]:
        """Refresh the user tokens."""
        token_raw = request.cookies.get("refresh")
        assert token_raw, "Refresh token cookie is missing"
        token = Token(token_raw)
        user = await self.app.store.auth.get_user_by_email(token.email)
        assert user, "User not found"
        access_token, refresh_token = self.create_access_refresh_cookie(user.id.hex, user.email, response,
                                                                        request.client.host)
        return {**user.as_dict(), "access_token": access_token}

    def create_access_refresh_cookie(self,
                                     user_id: str,
                                     email: EmailStr,
                                     response: Response,
                                     domain: str = None) -> [str, str]:
        """Create access and refresh cookie, and add refresh token to cookie.

        Args:
            user_id: the identifier of the user
            email: user email
            response: Response
            domain: domain name
        """
        access_token, refresh_token = self.app.store.token.create_access_and_refresh_tokens(user_id, email)
        set_cookie("refresh", refresh_token, response, self.settings.auth_refresh_expires_delta, domain=domain)
        return access_token, refresh_token
