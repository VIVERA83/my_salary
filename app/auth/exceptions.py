"""Exception handler."""
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.components import Application, Request


async def http_exception_handler(
        request: Request,
        exc: HTTPException,
) -> JSONResponse:
    """Catching exceptions.

    In order to return an object with
    information about the application documentation

    Args:
        request: Request
        exc: HTTPException

    Returns:
        object: JSONResponse
    """
    return JSONResponse(
        content={
            'detail': '{exc}'.format(exc=exc.detail),
            'message': 'See the documentation {url}{docs}'.format(
                url=request.app.settings.base_url,
                docs=request.app.docs_url,
            ),
        },
        status_code=exc.status_code,
    )


def setup_exception(app: Application):
    """Configuring pluggable exception handlers.

    Args:
        app: Fast Api application
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
