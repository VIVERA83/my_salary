"""Обработчик HTTP исключений"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.components import Request, Application


async def http_exception_handler(request: Request, exc: HTTPException):
    """Перехват исключения, с целью вернуть объект с информацией о документации по приложению."""
    return JSONResponse(
        content={
            "detail": f"{exc.detail}.",
            "message": f"See the documentation: "
                       f"http://{request.app.settings.server_host}:{request.app.settings.app_port}{request.app.docs_url}",
        },
        status_code=exc.status_code,
    )


def setup_exception(app: Application):
    """Настройка подключаемый обработчиков исключений."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
