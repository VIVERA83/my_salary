"""Обработчик HTTP исключений"""
from core.components import Application, Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: HTTPException):
    """Перехват исключения, с целью вернуть объект с информацией о документации по приложению."""
    return JSONResponse(
        content={
            "detail": f"{exc.detail}.",
            "message": "See the documentation: "
            + "http://{host}:{port}{uri}".format(
                host=request.app.settings.app_server_host,
                port=request.app.settings.app_port,
                uri=request.app.docs_url,  # noqa
            ),
        },
        status_code=exc.status_code,
    )


def setup_exception(app: Application):
    """Настройка подключаемый обработчиков исключений."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
