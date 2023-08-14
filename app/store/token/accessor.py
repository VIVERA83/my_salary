from datetime import datetime, timedelta
from uuid import uuid4

from base.base_accessor import BaseAccessor
from core.settings import AuthorizationSettings
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
