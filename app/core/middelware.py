"""Middleware приложения."""
import traceback

from fastapi import status
from fastapi.responses import JSONResponse
from jose import JWSError
from sqlalchemy.exc import IntegrityError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

from core import Application, Request
from core.utils import HTTP_EXCEPTION


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
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                message = "Perhaps one of the parameters does not meet the uniqueness rules"

            elif isinstance(error, JWSError):
                status_code = status.HTTP_403_FORBIDDEN
                message = error.args[0]

            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                message = "The server is temporarily unavailable try contacting later"

            if request.app.settings.logging.traceback:
                request.app.logger.error(traceback.format_exc())
            else:
                request.app.logger.error(f"{request.url=}, {error=}")
        return JSONResponse(content={
            "detail": HTTP_EXCEPTION.get(status_code),
            "message": message,
        }, status_code=status_code)


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