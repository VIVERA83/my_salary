import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from fastapi.openapi.utils import get_openapi
from fastapi_jwt import JwtAccessBearer
from jose import JWSError, jws
from sqlalchemy import insert, select, update
from starlette.responses import Response

from base import BaseAccessor
from core import Request
from core.settings import AuthorizationSettings
from store.auth.utils import METHODS, get_token
from auth.models import UserModel as UserModel


class AuthAccessor(BaseAccessor):
    """Authorization service."""

    access_security: Optional[JwtAccessBearer] = None
    settings: Optional[AuthorizationSettings] = None
    free_access: Optional[list[list[str]]] = None

    def _init(self):
        self.settings = AuthorizationSettings()

        self.access_security = JwtAccessBearer(
            secret_key=self.settings.key,
            auto_error=True,
            access_expires_delta=timedelta(seconds=self.settings.access_expires_delta),
            refresh_expires_delta=timedelta(seconds=self.settings.refresh_expires_delta),
        )
        self.app.openapi = self._custom_openapi

        self.app.router.add_api_route(
            '/api/v1/token',
            get_token,
            methods=['GET'],
            include_in_schema=True,
            tags=['AUTH'],
        )

    async def create_user(
            self,
            name: str,
            email: str,
            password: str,
            is_superuser: Optional[bool] = None,
    ) -> Optional[UserModel]:
        """Adding a new user to the database.

        Args:
            name: name
            email: user email
            password: user password
            is_superuser: boolean if true user is superuser

        Returns:
            object: UserModel
        """
        async with self.app.database.session.begin().session as session:
            smtp = (
                insert(UserModel)
                .values(
                    name=name,
                    email=email,
                    password=password,
                    is_superuser=is_superuser,
                )
                .returning(UserModel)
            )
            user = await session.execute(smtp)
            await session.commit()
            if user:
                return user.unique().fetchone()[0]

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email.

        Args:
            email: user email

        Returns:
            optional: user model
        """
        async with self.app.database.session.begin().session as session:
            smtp = select(UserModel).where(UserModel.email == email)
            user = (await session.execute(smtp)).unique().fetchone()
            if user:
                return user[0]

    async def update_refresh_token(
            self,
            user_id: str,
            refresh_token: Optional[str] = None,
    ):
        """Updating the refresh token in the user account.

        Args:
            user_id: The ID of the user in the database
            refresh_token: The refresh token
        """
        async with self.app.database.session.begin().session as session:
            query = (
                update(UserModel)
                .filter(UserModel.id == user_id)
                .values(refresh_token=refresh_token)
                .returning(UserModel)
            )
            await session.execute(query)
            await session.commit()

    async def refresh(self, refresh_token: str) -> Optional[list[str]]:
        """Updating Access Tokens.

        The method updates the access token and refresh token,
        and makes an update in the database related to refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            object: list of tokens
        """
        payload: dict = json.loads(jws.get_unverified_claims(refresh_token))
        return await self.create_tokens(
            payload.get('subject', {}).get('user_id'),
        )

    async def create_tokens(self, user_id: str) -> list[str]:
        """Token generation: access_token and refresh_token.

        Args:
            user_id: user identifier

        Returns:
            object: list of tokens
        """
        subject = {'user_id': user_id}
        access_token = self.access_security.create_access_token(
            subject,
        )
        refresh_token = self.access_security.create_refresh_token(
            subject,
        )
        await self.update_refresh_token(user_id, refresh_token)
        return [access_token, refresh_token]

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

    async def verify_token(
            self,
            access_token: str,
    ) -> Optional[str]:
        """Token verification.

        In case of successful verification, access_token is returned.

        Args:
            access_token: The access token

        Returns:
            optional: The token
        """
        try:
            payload: dict = json.loads(
                jws.verify(access_token, self.settings.key, self.settings.algorithms),
            )
        except JWSError as ex:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ex.args[0],
            )
        if payload.get('exp') and payload['exp'] > int(datetime.now().timestamp()):
            return access_token
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access token from the expiration date, please login or refresh',
        )

    @staticmethod
    def get_access_token(request: 'Request') -> Optional[str]:
        """Попытка получить token из headers (authorization Bear).

        Args:
            request: Request

        Returns:
            object: access token
        """
        try:
            return request.headers.get('Authorization').split('Bearer ')[1]
        except (IndexError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid Authorization.'
                       'Expected format: {"Authorization": "Bearer <your token>"}',
            )

    @staticmethod
    def get_refresh_token(request: 'Request') -> Optional[str]:
        """Попытка получить refresh token из cookies.

        Args:
            request: Request

        Returns:
            object: refresh token
        """
        try:
            return request.cookies['refresh_token_cookie']
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid Authorization. Refresh token not found.',
            )

    def verification_public_access(self, request: 'Request') -> bool:
        """Проверка на доступ к открытым источникам.

        Args:
            request: Request object

        Returns:
            object: True if accessing public methods.
        """
        request_path = '/'.join(request.url.path.split('/')[1:])
        for path, method in self.free_access:
            left, *right = path.split('/')
            if right and '*' in right:
                p_left, *temp = request_path.split('/')
                if p_left == left:
                    return True
            elif path == request_path and method.upper() == request.method.upper():
                return True
        return False

    async def compare_refresh_token(self, user_id: str, refresh_token: str) -> bool:
        """Token Comparison.

        The sent token is compared with the token from the database.
        True if the token is equal to the value from the token database.

        Args:
            user_id: User_id whose token is being compared with the standard from DB.
            refresh_token: The refresh token.

        Returns:
            object: True if the token is equal to the value from the refresh token.
        """
        async with self.app.database.session.begin().session as session:
            smtp = select(UserModel.refresh_token).where(UserModel.id == user_id)
            return refresh_token == (await session.execute(smtp)).scalar()

    async def logout(self, request: 'Request', response: Response):
        """Logout.

        Clear refresh_token in cookie

        Args:
             request: Request
             response: Response
        """
        request.session.clear()
        self.access_security.unset_refresh_cookie(response)
        await self.update_refresh_token(request.state.user_id)

    def connect(self):
        """Configuring the authorization service."""
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
        self.logger.info('Auth service is running')

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
