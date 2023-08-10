from datetime import datetime, timedelta
from uuid import uuid4

from base.base_accessor import BaseAccessor
from core.settings import AuthorizationSettings
from fastapi import Response
from fastapi_jwt import JwtAccessBearer
from jose import jwt
from pydantic import EmailStr


class TokenAccessor(BaseAccessor):
    def _init(self):
        self.settings = AuthorizationSettings()

    def create_token(self, type_token: str, subject: dict, expire: int) -> str:
        """Create a new token.

        Args:
            type_token: str, example: access.
            subject: dict, example {'user_id': '122222'}.
            expire: time to expiration in seconds

        Returns:
            object: token
        """
        return jwt.encode(
            {
                "subject": subject,
                "type": type_token,
                "exp": datetime.utcnow() + timedelta(seconds=expire),
                "iat": datetime.utcnow(),
                "jti": uuid4().hex,
            },
            self.settings.auth_key.get_secret_value(),
            self.settings.auth_algorithms[0],
        )

    def create_access_token(self, user_id: str, email: EmailStr) -> str:
        subject = {
            "user_id": user_id,
            "email": email,
        }
        return self.create_token("access", subject, 600)

    def create_refresh_token(self, user_id: str, email: EmailStr) -> str:
        subject = {
            "user_id": user_id,
            "email": email,
        }
        return self.create_token("refresh", subject, 172000)

    def create_verification_token(self, user_id: str, email: EmailStr) -> str:
        subject = {
            "user_id": user_id,
            "email": email,
        }
        return self.create_token("verification", subject, 180)

    def create_reset_token(self, user_id: str, email: EmailStr) -> str:
        subject = {
            "user_id": user_id,
            "email": email,
        }
        return self.create_token("reset", subject, 180)

        # self.access_security = JwtAccessBearer(
        #     secret_key=self.settings.auth_key.get_secret_value(),
        #     auto_error=True,
        #     access_expires_delta=timedelta(seconds=self.settings.auth_access_expires_delta),
        #     refresh_expires_delta=timedelta(seconds=self.settings.auth_refresh_expires_delta),
        # )

        # def create_access_token(
        #         self,
        #         user_id: str,
        # ) -> str:
        #     subject = {"user_id": user_id}
        #     return self.access_security.create_access_token(
        #         subject, timedelta(seconds=self.settings.auth_access_expires_delta)
        #     )

        # def create_refresh_token(self, user_id: str) -> str:
        #     subject = {"user_id": user_id}
        #     return self.access_security.create_refresh_token(
        #         subject, timedelta(seconds=self.settings.auth_access_expires_delta)
        #     )

        # def create_tokens(self, user_id: str, email: EmailStr) -> tuple[str, str]:
        #
        #     access_token = self.create_token("access", subject, self.settings.auth_access_expires_delta)
        #     refresh_token = self.create_token("refresh", subject, self.settings.auth_refresh_expires_delta)
        #     return access_token, refresh_token

        # def set_refresh_token_cookie(
        #         self,
        #         refresh_token: str,
        #         response: "Response",
        # ):
        #     """Adding a token to cookies."""
        #     self.access_security.set_refresh_cookie(
        #         response,
        #         refresh_token,
        #         timedelta(self.settings.auth_refresh_expires_delta),
        #     )

        # def unset_refresh_token_cookie(
        #         self,
        #         response: "Response",
        # ):
        #     """Removing a token from cookies."""
        #     self.access_security.unset_refresh_cookie(response)

        # def create_token(self, type_token: str, subject: dict, expire: int) -> str:
        #     """Create a new token.
        #
        #     Args:
        #         type_token: str, example: access.
        #         subject: dict, example {'user_id': '122222'}.
        #         expire: time to expiration in seconds
        #
        #     Returns:
        #         object: token
        #     """
        #     return jwt.encode(
        #         {
        #             'subject': subject,
        #             'type': type_token,
        #             'exp': datetime.utcnow() + timedelta(seconds=expire),
        #             'iat': datetime.utcnow(),
        #             'jti': uuid4().hex,
        #         },
        #         self.settings.auth_key.get_secret_value(),
        #         self.settings.auth_algorithms[0],
        #     )

    def create_access_and_refresh_tokens(self, user_id: str, email: EmailStr) -> [str, str]:
        access_token = self.create_access_token(user_id, email)
        refresh_token = self.create_refresh_token(user_id, email)
        return access_token, refresh_token
