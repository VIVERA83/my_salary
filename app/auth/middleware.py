"""Middleware приложения."""
import json
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from jose import jws, JWSError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint, DispatchFunction
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.types import ASGIApp

from auth.schemes import TokenSchema
from auth.utils import get_access_token, check_path, get_refresh_token
from core import Application, Request
from core.settings import AuthorizationSettings

HTTP_EXCEPTION = {
    status.HTTP_401_UNAUTHORIZED: '401 Unauthorized',
    status.HTTP_403_FORBIDDEN: '403 Forbidden',
    status.HTTP_404_NOT_FOUND: '404 Not Found',
}


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Authorization MiddleWare."""

    def __init__(self, app: ASGIApp, dispatch: Optional[DispatchFunction] = None):
        super().__init__(app, dispatch)
        self.settings = AuthorizationSettings()

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

    async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
    ) -> Response:
        """Checking access rights to a resource.

        Here a token is added to the request.

        Args:
            request: 'Request'
            call_next: RequestResponseEndpoint

        Returns:
            object: Response
        """

        if check_path(request) or self.verification_public_access(request):
            return await call_next(request)
        try:
            assert self.verify_access_token(request)
            request.state.refresh_token = get_refresh_token(request)
            return await call_next(request)
        except HTTPException as error:
            status_code = error.status_code
            content_data = {
                'detail': HTTP_EXCEPTION.get(status_code, 'Unknown error'),
                'message': error.detail,
            }
            return JSONResponse(content=content_data, status_code=status_code)

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

    def verify_access_token(
            self,
            request: Request,
    ) -> bool:
        """Token verification.

        In case of successful verification, True.

        Args:
            request: Request

        Returns:
            optional: True if successful
        """
        access_token = get_access_token(request)
        request.state.access_token = TokenSchema(access_token)
        request.state.user_id = request.state.access_token.payload.user_id.hex
        try:
            payload = json.loads(jws.verify(access_token, self.settings.key, self.settings.algorithms), )
        except JWSError as ex:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ex.args[0],
            )
        if not payload.get("exp", 1) > int(datetime.now().timestamp()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Access token from the expiration date, please login or refresh',
            )
        return True


def setup_middleware(app: Application):
    """Configuring middleware.

    Args:
        app: Fast Api application
    """
    app.add_middleware(AuthorizationMiddleware)
