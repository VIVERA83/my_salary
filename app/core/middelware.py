"""Middleware приложения."""
import json
import re
import traceback
from logging import Logger

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from icecream import ic
from jose import JWSError
from sqlalchemy.exc import IntegrityError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response
from starlette.requests import Request
from starlette.types import ASGIApp

from core.utils import check_path, verification_public_access, verify_token, get_access_token, update_request_state, \
    PUBLIC_ACCESS
from core.components import Application
from core.settings import AuthorizationSettings, Settings
from core.utils import HTTP_EXCEPTION


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Обработка внутренних ошибок при выполнении обработчиков запроса."""

    def __init__(self, app: ASGIApp, logger: Logger = Logger(__name__)):
        super().__init__(app)
        self.logger = logger
        self.settings = Settings()

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Обработка ошибок при исполнении handlers (views)."""
        try:
            response = await call_next(request)
            return response
        except Exception as error:
            if isinstance(error, IntegrityError):
                key, value = get_error_content(error.args[0])
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                message = f"{key.capitalize()} is not exactly, please try other {key}, not these `{value}`"
            elif isinstance(error, JWSError):
                status_code = status.HTTP_403_FORBIDDEN
                message = error.args[0]
            elif isinstance(error, ValueError):
                status_code = status.HTTP_401_UNAUTHORIZED
                message = error.args[0]
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                message = "The server is temporarily unavailable try contacting later"
            if self.settings.logging.traceback:
                self.logger.error(traceback.format_exc())
            else:
                self.logger.error(f"{request.url=}, {error=}")
        ic(status_code)
        return JSONResponse(content={
            "detail": HTTP_EXCEPTION.get(status_code),
            "message": message,
        }, status_code=status_code)


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Authorization MiddleWare."""

    def __init__(self, app: ASGIApp):
        self.settings = AuthorizationSettings()
        self.public_access = PUBLIC_ACCESS
        super().__init__(app)

    async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
    ) -> Response | None:
        """Checking access rights to a resource.

        Here a token is added to the request.

        Args:
            request: 'Request'
            call_next: RequestResponseEndpoint

        Returns:
            object: Response
        """

        if check_path(request) or verification_public_access(request, self.public_access):
            return await call_next(request)
        try:
            if token := get_access_token(request):
                assert verify_token(token, self.settings.key, self.settings.algorithms)
                update_request_state(request, token)
                return await call_next(request)
        except HTTPException as error:
            content_data = {
                'detail': HTTP_EXCEPTION.get(error.status_code, 'Unknown error'),
                'message': error.detail,
            }
            return JSONResponse(content=content_data, status_code=error.status_code)


def setup_middleware(app: Application):
    """Настройка подключаемый Middleware."""
    app.add_middleware(SessionMiddleware, secret_key=app.settings.secret_key)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app.settings.secret_key,
        allow_methods=app.settings.allow_methods,
        allow_headers=app.settings.allow_headers,
        allow_credentials=app.settings.allow_credentials,
    )
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(AuthorizationMiddleware, )


def get_error_content(message: str) -> tuple[str, str]:
    m = re.findall(r"\(([A-Za-z0-9_@.]+)\)", message)
    return m[1], m[2]
