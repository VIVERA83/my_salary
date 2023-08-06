"""Middleware приложения."""
from core.components import Application
from core.components import Request as RequestApp
from core.settings import AuthorizationSettings, Settings
from core.utils import (
    PUBLIC_ACCESS,
    ExceptionHandler,
    check_path,
    get_access_token,
    update_request_state,
    verification_public_access,
    verify_token,
)
from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from store.cache.accessor import CacheAccessor


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Обработка внутренних ошибок при выполнении обработчиков запроса."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = Settings()
        self.exception_handler = ExceptionHandler()

    async def dispatch(self, request: RequestApp, call_next: RequestResponseEndpoint) -> Response:
        """Обработка ошибок при исполнении handlers (views)."""
        try:
            response = await call_next(request)
            return response
        except Exception as error:
            return self.exception_handler(
                error, request.url, request.app.logger, self.settings.app_logging.traceback
            )


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Authorization MiddleWare."""

    def __init__(self, app: ASGIApp, invalid_token: CacheAccessor):
        self.invalid_token = invalid_token
        self.settings = AuthorizationSettings()
        self.is_traceback = Settings().app_logging.traceback
        self.public_access = PUBLIC_ACCESS
        self.exception_handler = ExceptionHandler()
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
            verify_token(
                token, self.settings.auth_key.get_secret_value(), self.settings.auth_algorithms
            )
        except Exception as error:
            return self.exception_handler(
                error,
                request.url,
                request.app.logger,
                self.is_traceback,
            )
        update_request_state(request, token)
        return await call_next(request)


def setup_middleware(app: Application):
    """Настройка подключаемый Middleware."""
    app.add_middleware(
        SessionMiddleware, secret_key=app.settings.app_secret_key.get_secret_value()
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app.settings.app_allowed_origins,
        allow_methods=app.settings.app_allow_methods,
        allow_headers=app.settings.app_allow_headers,
        allow_credentials=app.settings.app_allow_credentials,
    )
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(AuthorizationMiddleware, invalid_token=app.store.invalid_token)
