"""Middleware приложения."""
import re
from datetime import datetime
from fastapi import HTTPException, status
from icecream import ic
from jose import JWSError, jws
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from store.cache.accessor import CacheAccessor

from core.components import Application
from core.components import Request as RequestApp
from core.settings import AuthorizationSettings, Settings
from core.utils import PUBLIC_ACCESS, Token
from core.exception_handler import ExceptionHandler


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Обработка ошибок при выполнении обработчиков запроса."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = Settings()
        self.exception_handler = ExceptionHandler()

    async def dispatch(self, request: RequestApp, call_next: RequestResponseEndpoint) -> Response:
        """Обработка ошибок при исполнении handlers (views)."""
        try:
            self.is_endpoint(request)
            response = await call_next(request)
            return response
        except Exception as error:
            return self.exception_handler(
                error, request.url, request.app.logger, self.settings.app_logging.traceback
            )

    @staticmethod
    def is_endpoint(request: "Request") -> bool:
        """Checking if there is a requested endpoint.

        Args:
            request: Request object

        Returns:
            object: True if there is a endpoint
        """
        detail = "{message}, See the documentation: http://{host}:{port}{uri}"
        message = "Not Found"
        status_code = status.HTTP_404_NOT_FOUND
        for route in request.app.routes:
            if re.match(route.path_regex, request.url.path):
                if request.method.upper() in route.methods:
                    return True
                status_code = status.HTTP_405_METHOD_NOT_ALLOWED
                message = "Method Not Allowed"
                break
        raise HTTPException(
            status_code,
            detail.format(
                message=message,
                host=request.app.settings.app_server_host,
                port=request.app.settings.app_port,
                uri=request.app.docs_url,
            ),
        )


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Authorization MiddleWare."""

    def __init__(self, app: ASGIApp, cache: CacheAccessor):
        self.cache = cache
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
        token = self.extract_token(request)
        if token.token:
            await self.verify_token(token)
        self.check_permission(token.type, request.url.path, request.method)
        self.update_request_state(request, token)
        return await call_next(request)

    async def verify_token(self, token: Token):
        try:
            ic(token)
            assert -2 == await self.cache.ttl(token.token), \
                f"The token {token.type} is blocked, an attempt to log in using the old token, a new token is needed"
            assert token.exp > int(
                datetime.now().timestamp()
            ), f"The '{token.type}' token has expired."
            jws.verify(
                token.token,
                self.settings.auth_key.get_secret_value(),
                self.settings.auth_algorithms,
            )
            return
        except JWSError as e:
            detail = status.HTTP_400_BAD_REQUEST
            message = e.args[0]
        except AssertionError as e:
            detail = status.HTTP_401_UNAUTHORIZED
            message = e.args[0]
        raise HTTPException(detail, message)

    def check_permission(self, token_type: str, path: str, method: str) -> bool:
        """Check permissions in the given path and token type.

        Args:
            token_type: one of the 'recovery', verif', 'access'
            path: endpoint path to check permissions
            method: method to check permissions
        """
        match token_type, path:
            case "anonymous", path:
                if bool(self.public_access.count([path, method.upper()])):
                    return True
                detail = "Access denied"
            case "recovery", "/api/v1/reset_password":
                return True
            case "verif", "/api/v1/reset_password":
                return True
            case "verification", "/api/v1/registration_user":
                return True
            case "access", path:
                if path not in [
                    "/api/v1/reset_password",
                    "/api/v1/create_user",
                    "/api/v1/registration_user",
                ]:
                    return True
            case _:
                return False
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    @staticmethod
    def extract_token(request: "Request") -> "Token":
        """Попытка получить token из headers (authorization Bear).

        Args:
            request: Request

        Returns:
            object: access token
        """
        authorization = request.headers.get("Authorization", None)
        if not authorization:
            return Token()
        bearer, *token = authorization.split(" ")
        try:
            assert "Bearer" == bearer, "Bearer header not specified"
            assert token, "Token header not specified"
        except AssertionError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args[0])
        return Token("".join(token))

    @staticmethod
    def update_request_state(request: "Request", token: Token):
        request.state.token = token
        request.state.user_id = token.user_id


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
    app.add_middleware(AuthorizationMiddleware, cache=app.store.cache)
    app.add_middleware(ErrorHandlingMiddleware)
