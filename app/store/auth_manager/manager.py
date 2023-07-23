from auth.schemes import TokenSchema
from base.base_accessor import BaseAccessor
from fastapi import Response


class AuthManager(BaseAccessor):
    async def create_user(self, response: Response, **user_data) -> dict:
        """Create a new user and tokens."""
        user = await self.app.store.auth.create_user(**user_data)
        return await self._create_tokens_update_response(response, user)

    async def login(self, response: Response, **user_data) -> dict:
        """Login user amd create new tokens."""
        if user := await self.app.store.auth.get_user_by_email(user_data["email"]):
            if user.password == user_data["password"]:
                return await self._create_tokens_update_response(response, user)
        raise ValueError("The user or password is incorrect")

    async def logout(self, response: Response, user_id: str, token: str, expire: int):
        self.app.store.jwt.unset_refresh_token_cookie(response)
        await self.app.store.invalid_token.set_token(token, user_id, expire + 5)
        await self.app.store.auth.add_refresh_token_to_user(user_id)

    async def refresh(self, request, response: Response):
        """Refresh the user tokens."""
        if token_raw := request.cookies.get('refresh_token_cookie'):
            token = TokenSchema(token_raw)
            if user := await self.app.store.auth.get_user_by_id_and_refresh_token(token.payload.user_id.hex, token_raw):
                return await self._create_tokens_update_response(response, user)
        raise ValueError("The user or refresh token is incorrect")

    async def _create_tokens_update_response(self, response: Response, user) -> dict:
        """Create tokens update response."""
        access_token, refresh_token = self.app.store.jwt.create_tokens(user.id.hex)
        self.app.store.jwt.set_refresh_token_cookie(refresh_token, response)
        await self.app.store.auth.add_refresh_token_to_user(user.id, refresh_token)
        return {**user.as_dict(), "access_token": access_token}
