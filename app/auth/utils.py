# import json
# from datetime import datetime
#
# from fastapi import HTTPException
# from typing import Optional, Literal
#
# from jose import JWSError, jws
# from starlette import status
# from starlette.routing import Route
#
# from auth.schemes import TokenSchema
# from core.components import Request
#
# ALGORITHMS = Literal[
#     "HS256",
#     "HS128",
# ]
# METHODS = Literal[
#     "HEAD",
#     "OPTIONS",
#     "GET",
#     "POST",
#     "DELETE",
#     "PATCH",
#     "PUT",
#     "*",
# ]
# HEADERS = Literal[
#     "Accept-Encoding",
#     "Content-Type",
#     "Set-Cookie",
#     "Access-Control-Allow-Headers",
#     "Access-Control-Allow-Origin",
#     "Authorization",
#     "*",
# ]
#
# HTTP_EXCEPTION = {
#     status.HTTP_401_UNAUTHORIZED: '401 Unauthorized',
#     status.HTTP_403_FORBIDDEN: '403 Forbidden',
#     status.HTTP_404_NOT_FOUND: '404 Not Found',
#     status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error",
# }
#
#
# def get_access_token(request: 'Request') -> Optional[str]:
#     """Попытка получить token из headers (authorization Bear).
#
#     Args:
#         request: Request
#
#     Returns:
#         object: access token
#     """
#     try:
#         return request.headers.get('Authorization').split('Bearer ')[1]
#     except (IndexError, AttributeError):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail='Invalid Authorization.'
#                    'Expected format: {"Authorization": "Bearer <your token>"}',
#         )
#
#
# def check_path(
#         request: Request,
# ) -> bool:
#     """Checking if there is a requested path.
#
#     Args:
#         request: Request object
#
#     Returns:
#         object: True if there is a path
#     """
#     is_not_fount = True
#     for route in request.app.routes:
#         route: Route
#         if route.path == request.url.path:
#             if request.method.upper() in route.methods:
#                 is_not_fount = False
#                 break
#     return is_not_fount
#
#
# def verification_public_access(request: 'Request') -> bool:
#     """Проверка на доступ к открытым источникам.
#
#     Args:
#         request: Request object
#
#     Returns:
#         object: True if accessing public methods.
#     """
#     request_path = '/'.join(request.url.path.split('/')[1:])
#     for path, method in request.app.store.auth.free_paths:
#         left, *right = path.split('/')
#         if right and '*' in right:
#             p_left, *temp = request_path.split('/')
#             if p_left == left:
#                 return True
#         elif path == request_path and method.upper() == request.method.upper():
#             return True
#     return False
#
#
# def verify_token(
#         token: str,
#         key: str,
#         algorithms: str
#
# ) -> bool:
#     try:
#         payload = json.loads(jws.verify(token, key, algorithms), )
#     except JWSError as ex:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=ex.args[0],
#         )
#     if not payload.get("exp", 1) > int(datetime.now().timestamp()):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail='Access token from the expiration date, please login or refresh',
#         )
#     return True
#
#
# def update_request_state(request: 'Request', token: str):
#     token = TokenSchema(token)
#     request.state.access_token = token
#     request.state.user_id = token.payload.user_id.hex
