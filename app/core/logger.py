"""Логирование."""
import logging
import sys

# from core.components import Application
from core.settings import Settings
from loguru import logger


def setup_logging(app:"Application") -> None:
    """Настройка логирования в приложении.

    В данном случае есть вариант использовать loguru.
    https://github.com/Delgan/loguru
    """
    settings = Settings().logging
    if settings.guru:
        logger.configure(
            **{
                "handlers": [
                    {
                        "sink": sys.stderr,
                        "level": settings.level,
                        "backtrace": settings.traceback,
                    },
                ],
            }
        )
        app.logger = logger
    else:
        logging.basicConfig(level=settings.log_level)
        app.logger = logging
    app.logger.info("Starting logging")
