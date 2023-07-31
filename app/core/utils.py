import json
import logging
import re
import traceback
from datetime import datetime
from logging import Logger
from typing import Literal, Optional

from auth.schemes import TokenSchema
from httpcore import URL
from jose import JWSError, jws
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

ALGORITHMS = Literal[
    "HS256",
    "HS128",
]
METHOD = Literal[
    "HEAD",
    "OPTIONS",
    "GET",
    "POST",
    "DELETE",
    "PATCH",
    "PUT",
    "*",
]
HEADERS = Literal[
    "Accept-Encoding",
    "Content-Type",
    "Set-Cookie",
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Origin",
    "Authorization",
    "*",
]

PUBLIC_ACCESS = [
    ["openapi.json", "GET"],
    ["docs", "GET"],
    ["docs/oauth2-redirect", "GET"],
    ["redoc", "GET"],
    ["api/v1/create_user", "POST"],
    ["api/v1/login", "POST"],
    ["api/v1/refresh", "GET"],
    ["admin/*", "*"],
    # delete
    ["api/v1/test", "GET"],
]

METHODS = [
    "HEAD",
    "OPTIONS",
    "GET",
    "POST",
    "DELETE",
    "PATCH",
    "PUT",
]

HTTP_EXCEPTION = {
    status.HTTP_400_BAD_REQUEST: "400 Bad Request",
    status.HTTP_401_UNAUTHORIZED: "401 Unauthorized",
    status.HTTP_403_FORBIDDEN: "403 Forbidden",
    status.HTTP_404_NOT_FOUND: "404 Not Found",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "422 Unavailable Entity",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error",
}


def get_access_token(request: "Request") -> Optional[str]:
    """Попытка получить token из headers (authorization Bear).

    Args:
        request: Request

    Returns:
        object: access token
    """
    assert request.headers.get("Authorization"), [
        "Authorization header not specified",
        status.HTTP_401_UNAUTHORIZED,
    ]
    bearer, *token = request.headers.get("Authorization").split(" ")
    assert "Bearer" == bearer, [
        "Bearer header not specified",
        status.HTTP_400_BAD_REQUEST,
    ]
    assert token, ["Token header not specified", status.HTTP_400_BAD_REQUEST]
    return "".join(token)


def check_path(
    request: "Request",
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


def verification_public_access(request: "Request", free_paths: list[str]) -> bool:
    """Проверка на доступ к открытым источникам."""

    request_path = "/".join(request.url.path.split("/")[1:])
    for path, method in free_paths:
        # for path, method in request.app.store.auth.free_paths:
        left, *right = path.split("/")
        if right and "*" in right:
            p_left, *temp = request_path.split("/")
            if p_left == left:
                return True
        elif path == request_path and method.upper() == request.method.upper():
            return True
    return False


def verify_token(token: str, key: str, algorithms: str) -> bool:
    try:
        payload = json.loads(
            jws.verify(token, key, algorithms),
        )
    except JWSError as e:
        raise AssertionError([e.args[0], status.HTTP_400_BAD_REQUEST])
    assert payload.get("exp", 1) > int(datetime.now().timestamp()), [
        "Access token from the expiration date, please login or refresh",
        status.HTTP_401_UNAUTHORIZED,
    ]
    return True


def update_request_state(request: "Request", token: str):
    token = TokenSchema(token)
    request.state.access_token = token
    request.state.user_id = token.payload.user_id.hex


def get_error_content(message: str) -> tuple[str, str]:
    m = re.findall(r"\(([A-Za-z0-9_@.]+)\)", message)
    return m[1], m[2]


def error_response(
    error: Exception,
    url: URL,
    logger: Logger = Logger,
    traceback_: bool = False,
):
    if isinstance(error.args[0], list):
        message, *status_code = error.args[0]
        status_code = status_code[0]
    else:
        message = error.args[0]
        status_code = status.HTTP_400_BAD_REQUEST

    content_data = {
        "detail": HTTP_EXCEPTION.get(status_code),
        "message": message,
    }
    if traceback_:
        logger.error(traceback.format_exc())
    else:
        logger.error(
            "{exc}: url={url}, message={error}".format(url=url, error=error, exc=error.__class__)
        )
    return JSONResponse(content=content_data, status_code=status_code)


class ExceptionHandler:
    exception: Exception

    def __new__(
        cls,
        exception: Exception,
        url: URL,
        logger: Logger = Logger(__name__),
        is_traceback: bool = False,
    ) -> JSONResponse:
        exc = cls.handlers.get(exception.__class__.__name__, cls.handler_unknown_error)(exception)
        return error_response(exc, url, logger, is_traceback)

    @staticmethod
    def handler_connection_refused_error(exception: Exception) -> Exception:
        message = "Failed to connect, try again later..."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        exception.args = ([message, status_code],)
        return exception

    @staticmethod
    def handler_assertion_error(exception: Exception) -> Exception:
        if isinstance(exception.args[0], list):
            message, *status_code = exception.args[0]
            status_code = status_code[0]
        else:
            message = exception.args[0]
            status_code = status.HTTP_400_BAD_REQUEST
        exception.args = ([message, status_code],)
        return exception

    @staticmethod
    def handler_unknown_error(exception: Exception) -> Exception:
        message = "Unknown error..."
        status_code = status.HTTP_400_BAD_REQUEST
        exception.args = ([message, status_code],)
        logging.Logger("handler_unknown_error").error(str(exception))
        return exception

    @staticmethod
    def handler_integrity_error_error(exception: Exception) -> Exception:
        key, value = get_error_content(exception.args[0])
        message = f"{key.capitalize()} is already in use, try other {key}, not these `{value}`"
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        exception.args = ([message, status_code],)
        return exception

    handlers = {
        "ConnectionRefusedError": handler_connection_refused_error,
        "AssertionError": handler_assertion_error,
        "ConnectionError": handler_connection_refused_error,
        "IntegrityError": handler_integrity_error_error,
    }
