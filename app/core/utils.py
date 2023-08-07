import json
import logging
import re
import traceback
from datetime import datetime, timedelta
from logging import Logger
from typing import Literal, Optional

from httpcore import URL
from icecream import ic
from jose import JWSError, jws
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from user.schemes import TokenSchema

ALGORITHMS = [
    "HS512",
    "HS256",
    "HS128",
]
ALGORITHM = Literal[
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


def get_token(request: "Request") -> Optional[str]:
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


def check_path(request: "Request") -> bool:
    """Checking if there is a requested path.

    Args:
        request: Request object

    Returns:
        object: True if there is a path
    """
    is_not_fount = True
    for route in request.app.routes:
        if re.match(route.path_regex, request.url.path):
            if request.method.upper() in route.methods:
                is_not_fount = False
                break
    return is_not_fount


def verification_public_access(request: "Request", free_paths: list[str]) -> bool:
    """Проверка на доступ к открытым источникам."""

    request_path = "/".join(request.url.path.split("/")[1:])
    for path, method in free_paths:
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
    token_type = payload.get("type", "unknown")
    assert payload.get("exp", 1) > int(datetime.now().timestamp()), [
        "The '{token_type}' token has expired.".format(token_type=token_type.capitalize()),
        status.HTTP_401_UNAUTHORIZED,
    ]
    return True


def update_request_state(request: "Request", token: str):
    token = TokenSchema(token)
    request.state.token = token
    request.state.user_id = token.payload.user_id.hex


def get_error_content(message: str) -> tuple[str, str]:
    m = re.findall(r"\(([A-Za-z0-9_@.]+)\)", message)
    return m[1], m[2]


class ExceptionHandler:
    def __init__(
        self,
    ):
        self.exception = Exception("Unknown error...")
        self.logger = Logger(__name__)
        self.level = logging.WARNING
        self.message = "Unknown error..."
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.is_traceback = False

    def __call__(
        self,
        exception: Exception,
        url: URL,
        logger: Logger = None,
        is_traceback: bool = False,
    ) -> JSONResponse:
        self.exception = exception
        self.logger = logger
        self.is_traceback = is_traceback
        if handler := self.handlers.get(exception.__class__.__name__):
            handler(self)  # noqa
        else:
            self.handler_unknown_error()
        return self.error_response(url)

    def handler_unknown_error(self):
        """Обработчик исключений связанных с исключениями которые не учтены в приложении.

        Выводится сообщение в лог, о том что нужно строчно решить проблему.
        """
        self.message = "Unknown error..."
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.level = logging.WARNING

    def handler_connection_to_error(self):
        """Обработчик исключений связанных с подключением к внешним источникам.

        Как пример обработка ошибки подключения к БД PostgresSQL.
        """
        self.message = "Failed to connect, try again later..."
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.level = logging.CRITICAL

    def handler_assertion_error(self):
        """Обработчик исключения AssertionError.

        Чаще всего возникают в случаи обработки неправильных данных от пользователя.
        """
        if isinstance(self.exception.args[0], list):
            self.message, *status_code = self.exception.args[0]
            self.status_code = status_code[0]
        else:
            self.message = self.exception.args[0]
            self.status_code = status.HTTP_400_BAD_REQUEST
        self.level = logging.INFO

    def handler_integrity_error_error(self) -> (str, int):
        """Обработчик исключения IntegrityError."""
        key, value = get_error_content(self.exception.args[0])
        self.message = (
            f"{key.capitalize()} is already in use, try other {key}, not these `{value}`"
        )
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.level = logging.INFO

    def error_response(self, url: URL) -> JSONResponse:
        """Формирует и возвращает JSONResponse объект с ответом.

        Так же выдает лог сообщение об ошибке.
        """
        content_data = {
            "detail": HTTP_EXCEPTION.get(self.status_code),
            "message": self.message,
        }
        if self.is_traceback:
            msg = traceback.format_exc()
        else:
            msg = f"url={url}, exception={self.exception.__class__}, message_to_user={self.exception}"
        match self.level:
            case "CRITICAL" | 50:
                msg = (
                    f" \n_____________\n "
                    f"WARNING: an error has occurred to which there is no correct response of the application."
                    f" WE NEED TO RESPOND URGENTLY"
                    f" \nExceptionHandler:  {str(self.exception)}\n"
                    f" _____________\n" + traceback.format_exc()
                    if not self.is_traceback
                    else ""
                )
                self.logger.critical(msg)
            case "ERROR" | 40:
                self.logger.error(msg)
            case "WARNING" | 30:
                self.logger.warning(msg)
            case _:
                self.logger.info(msg)
        return JSONResponse(content=content_data, status_code=self.status_code)

    handlers = {
        "AssertionError": handler_assertion_error,
        "ConnectionRefusedError": handler_connection_to_error,
        "ConnectionError": handler_connection_to_error,
        "IntegrityError": handler_integrity_error_error,
        "ProgrammingError": handler_connection_to_error,
    }
