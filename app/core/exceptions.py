"""Обработчик HTTP исключений"""
from core.components import Application, Request
from core.utils import get_error_content
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: HTTPException):
    """Перехват исключения, с целью вернуть объект с информацией о документации по приложению."""
    return JSONResponse(
        content={
            "detail": f"{exc.detail}.",
            "message": "See the documentation: "
            + "http://{host}:{port}{uri}".format(
                host=request.app.settings.server_host,
                port=request.app.settings.app_port,
                uri=request.app.docs_url
            ),
        },
        status_code=exc.status_code,
    )


def setup_exception(app: Application):
    """Настройка подключаемый обработчиков исключений."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)


class CustomIntegrityError(IntegrityError):
    def __init__(self, error: IntegrityError):
        super().__init__("IntegrityError", error.params, error.orig)
        key, value = get_error_content(error.args[0])
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.message = (
            f"{key.capitalize()} is already in use, try other {key}, not these `{value}`"
        )
        self.args = ([self.message, self.status_code],)
