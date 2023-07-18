import json
from datetime import timedelta
from typing import Optional, Dict, Any
from fastapi.openapi.utils import get_openapi
from fastapi_jwt import JwtAccessBearer
from fastapi import Response
from jose import jws

from core import Application
from core.settings import AuthorizationSettings
from core.utils import METHODS


class Jwt:
    app: Optional["Application"]
    free_access: Optional[list[list[str]]]
    access_security: Optional[JwtAccessBearer] = None
    settings: Optional[AuthorizationSettings] = None

    def init(self):
        self.settings = AuthorizationSettings()
        self.access_security = JwtAccessBearer(
            secret_key=self.settings.key,
            auto_error=True,
            access_expires_delta=timedelta(seconds=self.settings.access_expires_delta),
            refresh_expires_delta=timedelta(seconds=self.settings.refresh_expires_delta),
        )
        self.free_access = [
            ['openapi.json', 'GET'],
            ['docs', 'GET'],
            ['docs/oauth2-redirect', 'GET'],
            ['redoc', 'GET'],

            ['api/v1/create_user', 'POST'],
            ['api/v1/login', 'POST'],
            ['api/v1/refresh', 'GET'],
            ['admin/*', '*'],
        ]

        self.app.openapi = self._custom_openapi

    def _custom_openapi(self) -> Dict[str, Any]:
        """Обновления схемы в Openapi.

        Добавление в закрытые методы HTTPBearer.

        Returns:
            dict: Dictionary openapi schema
        """
        if self.app.openapi_schema:
            return self.app.openapi_schema
        openapi_schema = get_openapi(
            title=self.app.title,
            description=self.app.description,
            routes=self.app.routes,
            version=self.app.version,
        )

        for key, path in openapi_schema['paths'].items():
            is_free, free_method = self._is_free(key)
            if not is_free:
                self._add_security(free_method, path)

        self.app.openapi_schema = openapi_schema
        return self.app.openapi_schema

    def _is_free(self, url: str):
        is_free = False
        free_method = None
        for f_p, f_m in self.free_access:
            if url[1:] == f_p:
                is_free = True
                free_method = f_m
        return is_free, free_method

    @staticmethod
    def _add_security(name: Optional[str], path: dict):
        """Add a security.

        Args:
            name: str, example: `post`
            path: dict openapi_schema
        """
        for method in METHODS:
            if method != name and path.get(method):
                path[method]['security'] = [{'HTTPBearer': []}]

    @property
    def free_paths(self) -> list[list[str]]:
        return self.free_access

    async def update_response(
            self,
            refresh_token: str,
            response: 'Response',
    ) -> 'Response':
        """Adding a token to cookies.

        response.set_cookie(samesite='none', secure=True,)

        Args:
            refresh_token: The refresh token
            response: The response

        Returns:
            object: The response
        """
        self.access_security.set_refresh_cookie(response, refresh_token, timedelta(self.settings.refresh_expires_delta))
        return response

    def verify_token(self, token: str) -> dict[str, Any]:
        return json.loads(jws.verify(token, self.settings.key, self.settings.algorithms), )
