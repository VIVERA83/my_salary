from datetime import timedelta

from base.base_accessor import BaseAccessor
from core.settings import AuthorizationSettings
from fastapi import Response
from fastapi_jwt import JwtAccessBearer


class JWTAccessor(BaseAccessor):
    def _init(self):
        self.settings = AuthorizationSettings()
        self.access_security = JwtAccessBearer(
            secret_key=self.settings.key,
            auto_error=True,
            access_expires_delta=timedelta(seconds=self.settings.access_expires_delta),
            refresh_expires_delta=timedelta(seconds=self.settings.refresh_expires_delta),
        )

    def create_access_token(
        self,
        user_id: str,
    ) -> str:
        subject = {"user_id": user_id}
        return self.access_security.create_access_token(
            subject, timedelta(seconds=self.settings.access_expires_delta)
        )

    def create_refresh_token(self, user_id: str) -> str:
        subject = {"user_id": user_id}
        return self.access_security.create_refresh_token(
            subject, timedelta(seconds=self.settings.access_expires_delta)
        )

    def create_tokens(self, user_id: str) -> tuple[str, str]:
        return self.create_access_token(user_id), self.create_refresh_token(user_id)

    def set_refresh_token_cookie(
        self,
        refresh_token: str,
        response: "Response",
    ):
        """Adding a token to cookies."""
        self.access_security.set_refresh_cookie(
            response,
            refresh_token,
            timedelta(self.settings.refresh_expires_delta),
        )

    def unset_refresh_token_cookie(
        self,
        response: "Response",
    ):
        """Removing a token from cookies."""
        self.access_security.unset_refresh_cookie(response)
