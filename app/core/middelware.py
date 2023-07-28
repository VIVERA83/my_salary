"""Middleware приложения."""
from logging import Logger

from core.components import Application
from core.exceptions import CustomIntegrityError
from core.settings import AuthorizationSettings, Settings
from core.utils import (
    PUBLIC_ACCESS,
    check_path,
    error_response,
    get_access_token,
    update_request_state,
    verification_public_access,
    verify_token,
)
from fastapi import status
from icecream import ic
from sqlalchemy.exc import IntegrityError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from store.invalid_token.accessor import InvalidTokenAccessor


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Обработка внутренних ошибок при выполнении обработчиков запроса."""

    def __init__(self, app: ASGIApp, logger: Logger = Logger(__name__)):
        super().__init__(app)
        self.logger = logger
        self.settings = Settings()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Обработка ошибок при исполнении handlers (views)."""

        try:
            response = await call_next(request)
            return response
        except Exception as error:
            ic(error)
            if isinstance(error, IntegrityError):
                error = CustomIntegrityError(error)

            return error_response(
                error,
                request.url,
                self.logger,
                self.settings.logging.traceback,
            )


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Authorization MiddleWare."""

    def __init__(self, app: ASGIApp, invalid_token: InvalidTokenAccessor):
        self.invalid_token = invalid_token
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
            token = get_access_token(request)
            assert not await self.invalid_token.get_token(token), [
                "Access token is invalid",
                status.HTTP_401_UNAUTHORIZED,
            ]
            verify_token(token, self.settings.key, self.settings.algorithms)
        except AssertionError as error:
            return error_response(
                error,
                request.url,
                request.app.logger,
                request.app.settings.logging.traceback,
            )
        update_request_state(request, token)
        return await call_next(request)


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
    app.add_middleware(AuthorizationMiddleware, invalid_token=app.store.invalid_token)
