import logging
import re
import traceback
from logging import Logger

from core.utils import HTTP_EXCEPTION
from httpcore import URL
from icecream import ic
from starlette import status
from starlette.responses import JSONResponse


class ExceptionHandler:
    handlers = {}

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

    def handler_integrity_error_error(self):
        """Обработчик исключения IntegrityError."""
        key, value = get_error_content(self.exception.args[0])
        self.message = (
            f"{key.capitalize()} is already in use, try other {key}, not these `{value}`"
        )
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.level = logging.INFO

    def handler_http_exception(self):
        ic(self.exception)
        if hasattr(self.exception, "status_code"):
            self.status_code = self.exception.status_code
        if hasattr(self.exception, "detail"):
            self.message = self.exception.detail

    def handler_jws_exception(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = "Token error. " + self.exception.args[0]

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
                )
                self.logger.critical(msg)
            case "ERROR" | 40:
                self.logger.error(msg)
            case "WARNING" | 30:
                self.logger.warning(msg)
            case _:
                self.logger.info(msg)
        return JSONResponse(content=content_data, status_code=self.status_code)

    handlers.update(
        {
            "AssertionError": handler_assertion_error,
            "ConnectionRefusedError": handler_connection_to_error,
            "ConnectionError": handler_connection_to_error,
            "IntegrityError": handler_integrity_error_error,
            "ProgrammingError": handler_connection_to_error,
            "HTTPException": handler_http_exception,
            "JWSError": handler_jws_exception,
        }
    )


def get_error_content(message: str) -> tuple[str, str]:
    m = re.findall(r"\(([A-Za-z0-9_@.]+)\)", message)
    return m[1], m[2]
