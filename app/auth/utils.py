from datetime import datetime

from fastapi import HTTPException
from typing import Optional

from jose import JWSError
from starlette import status
from starlette.routing import Route

from auth.schemes import TokenSchema
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


# def check_refresh_token(request: 'Request') -> Optional[str]:
#     """Попытка получить refresh token из cookies.
#
#     Args:
#         request: Request
#
#     Returns:
#         object: refresh token
#     """
#     try:
#         request.state.refresh_token = request.cookies['refresh_token_cookie']
#     except KeyError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail='Invalid Authorization. Refresh token not found.',
#         )


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


def verification_public_access(request: 'Request') -> bool:
    """Проверка на доступ к открытым источникам.

    Args:
        request: Request object

    Returns:
        object: True if accessing public methods.
    """
    request_path = '/'.join(request.url.path.split('/')[1:])
    for path, method in request.app.store.auth.free_paths:
        left, *right = path.split('/')
        if right and '*' in right:
            p_left, *temp = request_path.split('/')
            if p_left == left:
                return True
        elif path == request_path and method.upper() == request.method.upper():
            return True
    return False


def verify_access_token(
        request: Request,
) -> bool:
    """Token verification.

    In case of successful verification, True.

    Args:
        request: Request

    Returns:
        optional: True if successful
    """
    access_token = get_access_token(request)
    request.state.access_token = TokenSchema(access_token)
    request.state.user_id = request.state.access_token.payload.user_id.hex
    try:
        payload = request.app.store.auth.verify_token(access_token)
    except JWSError as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ex.args[0],
        )
    if not payload.get("exp", 1) > int(datetime.now().timestamp()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access token from the expiration date, please login or refresh',
        )
    return True
