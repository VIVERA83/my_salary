import logging
from typing import Optional

from core.settings import Settings
from fastapi import FastAPI
from fastapi import Request as FastAPIRequest
from redis.client import Redis
from store.database.postgres import Postgres
from store.database.redis import RedisAccessor
from store.store import Store
from user.schemes import TokenSchema

class Application(FastAPI):
    """Application главный класс.

    Описываем сервисы, которые будут использоваться в приложении.
    Так же это нужно для корректной подсказки IDE.
    """

    store: Store
    settings: Settings
    redis: RedisAccessor
    postgres: Postgres
    logger: logging.Logger

class Request:
    """Переопределения Request.

    Для корректной подсказки IDE по методам `Application`."""

    app: Optional["Application"] = None
    user_id: Optional[str] = None
    token: Optional[str] = None
    _state: Optional["CustomState"] = None

    @property
    def state(self) -> "CustomState":
        """Для корректной подсказки IDE по методам `Request`.

        Returns:
             CustomState: state
        """
        return self._state

class CustomState:
    """Переопределения State.

    Для корректной подсказки IDE по методам `Request`.
    """

    access_token: Optional["TokenSchema"]
    user_id: Optional[str] = None
