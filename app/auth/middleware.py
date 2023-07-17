"""Middleware приложения."""

from fastapi import HTTPException

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from auth.utils import check_path, verification_public_access, verify_access_token
from core import Application, Request

from core.utils import HTTP_EXCEPTION


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Authorization MiddleWare."""

    async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
    ) -> Response:
        """Checking access rights to a resource.

        Here a token is added to the request.

        Args:
            request: 'Request'
            call_next: RequestResponseEndpoint

        Returns:
            object: Response
        """

        if check_path(request) or verification_public_access(request):
            return await call_next(request)
        try:
            verify_access_token(request)
            return await call_next(request)
        except HTTPException as error:
            status_code = error.status_code
            content_data = {
                'detail': HTTP_EXCEPTION.get(status_code, 'Unknown error'),
                'message': error.detail,
            }
            return JSONResponse(content=content_data, status_code=status_code)


def setup_middleware(app: Application):
    """Configuring middleware.

    Args:
        app: Fast Api application
    """
    app.add_middleware(AuthorizationMiddleware)
