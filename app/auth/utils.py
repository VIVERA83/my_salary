from fastapi import HTTPException
from typing import Optional

from starlette import status
from starlette.routing import Route

from core import Request


def get_access_token(request: 'Request') -> Optional[str]:
    """Попытка получить token из headers (authorization Bear).

    Args:
        request: Request

    Returns:
        object: access token
    """
    try:
        return request.headers.get('Authorization').split('Bearer ')[1]
    except (IndexError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Authorization.'
                   'Expected format: {"Authorization": "Bearer <your token>"}',
        )


def get_refresh_token(request: 'Request') -> Optional[str]:
    """Попытка получить refresh token из cookies.

    Args:
        request: Request

    Returns:
        object: refresh token
    """
    try:
        return request.cookies['refresh_token_cookie']
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Authorization. Refresh token not found.',
        )


def check_path(
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
