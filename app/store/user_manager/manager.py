import json
from typing import Any, Literal
from uuid import uuid4

from base.base_accessor import BaseAccessor
from core.settings import AuthorizationSettings
from pydantic import EmailStr, SecretStr
from icecream import ic

ic.includeContext = True
Field_names = Literal["id", "name", "email", "password", "created", "modified"]

USER_DATA_KEY = Literal[
    "name",
    "email",
    "password",
    "is_superuser",
    "refresh_token",
    "access_token",
]


class UserManager(BaseAccessor):
    def _init(self):
        self.settings = AuthorizationSettings()
        self.expire = 180

    async def create_user(self, name: str, email: EmailStr, password: str):
        """Create temporary user data.

        1. Check email address in cache.
        2. Check email in database.
        3. Create token for verification email address
        4. Save the temporary data in Redis
        5. Send letter in email for verification email addresses.

        Args:
            name: User
            email: User email address
            password: hash of password
        """
        seconds = await self.app.store.cache.ttl(email)
        assert -1 > seconds, (
            f"A letter has been sent to this email address '{email}',"
            f" check the email or the address is not specified correctly."
            f"Resending an email is possible after {seconds} seconds"
        )
        user = await self.app.store.auth.get_user_by_email(email)
        assert not user, f"Email is already in use, try other email address, not these '{email}'"
        token = self.app.store.token.create_verification_token(uuid4().hex, email)
        ic("create verification token ", token)
        user_str = json.dumps(
            {
                "name": name or "Пользователь",
                "email": email,
                "password": password,
                "id": uuid4().hex,
            }
        )
        await self.app.store.cache.set(email, user_str, self.expire)
        await self.app.store.ems.send_message_to_confirm_email(email, name, token, link="test")

    async def user_registration(self, email: EmailStr) -> tuple[dict[USER_DATA_KEY, Any], str]:
        """Registration new user.

        Save in database user data, creates tokens."""
        user_data = await self.app.store.cache.get(email)
        assert user_data, "User data, not found, please try again creating user"
        user_data = json.loads(user_data)
        try:
            async with self.app.postgres.session.begin().session as session:
                query_user = self.app.store.auth.get_query_create_user(
                    user_data["name"], email, user_data["password"]
                )
                query_user_blog = self.app.store.blog.get_query_create_user(
                    user_data["name"], email
                )
                user, user_blog = [
                    (await session.execute(q)).scalar_one_or_none()
                    for q in [query_user, query_user_blog]
                ]
                access, refresh = self._create_access_and_refresh_tokens(user.id.hex, user.email)
                await self.app.store.auth.update_refresh_token(user.id, refresh)
                await session.commit()
                await self.app.store.cache.delete(email)
        except Exception as e:
            await session.rollback()
            raise e
        else:
            return {**user.as_dict(), "access_token": access}, refresh

    async def login(
            self, email: EmailStr, password: SecretStr
    ) -> tuple[dict[USER_DATA_KEY, Any], str]:
        """Login user amd create new tokens.

        1. Check email in database
        2. Compare password in database
        3. Update refresh token in database

        Args:
            email: user email address
            password: hash password, for compare in database

        Returns:
             objects: user data, new refresh token
        """
        user = await self.app.store.auth.get_user_by_email(email)
        assert user, "User not found"
        assert user.password == password.get_secret_value(), "Password is incorrect"
        access, refresh = self._create_access_and_refresh_tokens(user.id.hex, user.email)
        user = await self.app.store.auth.update_refresh_token(user.id, refresh)
        return {**user.as_dict(), "access_token": access}, refresh

    async def logout(self, user_id: str, token: str, expire: int):
        """Logout the user.

        Args:
            user_id: Unique identifier for the user, UUID
            token: refresh token
            expire: number of seconds
        """
        await self.app.store.cache.set(token, user_id, expire + 5)
        await self.app.store.auth.update_refresh_token(user_id)

    async def refresh(self, email: EmailStr) -> tuple[dict[USER_DATA_KEY, Any], str]:
        """Refresh the user tokens.

        1. Compare refresh and token from user in Database
        2. Create new refresh, access tokens and update database and cookies

        Args:
            email: user email address

        Returns:
            objects: user data, new refresh token
        """
        user = await self.app.store.auth.get_user_by_email(email)
        assert not user, "User not found"
        access, refresh = self._create_access_and_refresh_tokens(user.id.hex, user.email)
        user = await self.app.store.auth.update_refresh_token(user.id, refresh)
        assert not user, "User not found"
        return {**user.as_dict(), "access_token": access}, refresh

    async def reset_password(self, email: EmailStr):
        """Initializing reset user password.

        1. Check user_id in cache.
        2. Check user email
        3. Create token for new password
        4. Add cache token.
        5. Send an email with a token to change password
        """
        # try:
        user = await self.app.store.auth.get_user_by_email(email)
        assert user, f"User with email address {email} not found."
        seconds = await self.app.store.cache.ttl(user.email)
        assert -1 > seconds, (
            f"A letter has been sent to this email address '{user.email}',"
            f" check the email or the address is not specified correctly."
            f"Resending an email is possible after {seconds} seconds"
        )
        token = self.app.store.token.create_reset_token(user.id.hex, user.email)
        ic(token)
        flag = False
        try:
            await self.app.store.cache.set(user.email, token, 180)
            flag = True
            await self.app.store.ems.send_message_to_reset_password(
                user.email, user.name, token, "reset_ password"
            )
        except Exception as e:
            if flag:
                await self.app.store.cache.delete(user.email)
            raise e

    def _create_access_and_refresh_tokens(self, user_id: str, email: EmailStr) -> tuple[str, str]:
        """Create access, refresh tokens.

        Args:
            user_id: user unique identifier, UUID
            email: user email address

        Returns:
            list of tokens
        """
        access_token = self.app.store.token.create_access_token(user_id, email)
        refresh_token = self.app.store.token.create_refresh_token(user_id, email)
        return access_token, refresh_token
