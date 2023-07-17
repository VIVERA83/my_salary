"""Middleware приложения."""

from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from auth.schemes import TokenSchema
from core import Application, Request

HTTP_EXCEPTION = {
    status.HTTP_401_UNAUTHORIZED: '401 Unauthorized',
    status.HTTP_403_FORBIDDEN: '403 Forbidden',
    status.HTTP_404_NOT_FOUND: '404 Not Found',
}


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
        if await self.check_path(request):
            return await call_next(request)
        if request.app.store.auth.verification_public_access(request):
            return await call_next(request)
        try:
            access_token = request.app.store.auth.get_access_token(request)
            await request.app.store.auth.verify_token(access_token)
            request.state.token = TokenSchema(access_token)
            request.state.user_id = request.state.token.payload.user_id.hex
            return await call_next(request)
        except HTTPException as error:
            status_code = error.status_code
            content_data = {
                'detail': HTTP_EXCEPTION.get(status_code, 'Unknown error'),
                'message': error.detail,
            }
            return JSONResponse(content=content_data, status_code=status_code)

    @staticmethod
    async def check_path(
            request: Request,
    ) -> bool:
        """Checking if there is a requested path.

        Args:
            request: Request object

        Returns:
            object: True if there is a path
        """
        is_not_fount = True
        for route in request.app.routes:
            route: Route
            if route.path == request.url.path:
                if request.method.upper() in route.methods:
                    is_not_fount = False
                    break
        return is_not_fount


def setup_middleware(app: Application):
    """Configuring middleware.

    Args:
        app: Fast Api application
    """
    app.add_middleware(AuthorizationMiddleware)
