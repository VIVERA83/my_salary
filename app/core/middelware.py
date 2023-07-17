"""Middleware приложения."""
import traceback

from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

from core import Application, Request


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Обработка внутренних ошибок при выпоолнение обработсиков запроса."""

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Обработка ошибок при исполнении handlers (views)."""
        try:
            response = await call_next(request)
            return response
        except Exception as error:
            if isinstance(error, IntegrityError):
                content = {
                    "detail": "UnProcessable Entity",
                    "message": "Perhaps one of the parameters does not meet the uniqueness rules",
                }
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            else:
                content = {
                    "detail": "Internal server error",
                    "message": "The server is temporarily unavailable try contacting later",
                }
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            if request.app.settings.logging.traceback:
                request.app.logger.error(traceback.format_exc())
            else:
                request.app.logger.error(f"{request.url=}, {error=}")
        return JSONResponse(content=content, status_code=status_code)


def setup_middleware(app: Application):
    """Настройка подключаемый Middleware."""
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(SessionMiddleware, secret_key=app.settings.secret_key)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app.settings.secret_key,
        allow_methods=app.settings.allow_methods,
        allow_headers=app.settings.allow_headers,
        allow_credentials=app.settings.allow_credentials,
    )
