from typing import Any, Literal

from user.schemes import TokenSchema
from base.base_accessor import BaseAccessor
from fastapi import Response, status

USER_DATA_KEY = Literal[
    "name",
    "email",
    "password",
    "is_superuser",
    "refresh_token",
    "access_token",
]


class UserManager(BaseAccessor):
    async def create_user(self, response: Response, **user_data) -> dict[USER_DATA_KEY, Any]:
        """Create a new user and tokens."""
        user = await self.app.store.auth.create_user(**user_data)
        return await self._create_tokens_update_response(response, user)

    async def login(self, response: Response, **user_data) -> dict[USER_DATA_KEY, Any]:
        """Login user amd create new tokens."""
        user = await self.app.store.auth.get_user_by_email(user_data["email"])
        assert user, ["User not found", status.HTTP_401_UNAUTHORIZED]
        assert user.password == user_data["password"], [
            "Password is incorrect",
            status.HTTP_401_UNAUTHORIZED,
        ]
        return await self._create_tokens_update_response(response, user)

    async def logout(self, response: Response, user_id: str, token: str, expire: int):
        self.app.store.jwt.unset_refresh_token_cookie(response)
        await self.app.store.invalid_token.set_token(token, user_id, expire + 5)
        await self.app.store.auth.add_refresh_token_to_user(user_id)

    async def refresh(self, request, response: Response) -> dict[USER_DATA_KEY, Any]:
        """Refresh the user tokens."""
        token_raw = request.cookies.get("refresh_token_cookie")
        assert token_raw, [
            "Refresh token cookie is missing",
            status.HTTP_400_BAD_REQUEST,
        ]
        token = TokenSchema(token_raw)
        user = await self.app.store.auth.get_user_by_id_and_refresh_token(
            token.payload.user_id.hex, token.token
        )
        assert user, ["User not found", status.HTTP_401_UNAUTHORIZED]
        return await self._create_tokens_update_response(response, user)

    async def _create_tokens_update_response(
        self, response: Response, user
    ) -> dict[USER_DATA_KEY, Any]:
        """Create tokens update response."""
        access_token, refresh_token = self.app.store.jwt.create_tokens(user.id.hex)
        self.app.store.jwt.set_refresh_token_cookie(refresh_token, response)
        await self.app.store.auth.add_refresh_token_to_user(user.id, refresh_token)
        return {**user.as_dict(), "access_token": access_token}
