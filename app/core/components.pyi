import logging
from typing import Optional
from fastapi import Request as FastAPIRequest, FastAPI

from auth.schemes import TokenSchema
from core.settings import Settings

from store.database.database import Database
from store.store import Store


class Application(FastAPI):
    """Application главный класс.

    Описываем сервисы, которые будут использоваться в приложении.
    Так же это нужно для корректной подсказки IDE.
    """
    settings: Settings
    logger: logging
    database: Database
    store: Store


class Request:
    """Переопределения Request.

    Для корректной подсказки IDE по методам `Application`."""

    app: Optional["Application"] = None
    user_id: Optional[str] = None
    token: Optional[str] = None
    _state: Optional['CustomState'] = None

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

    access_token: Optional['TokenSchema']
    user_id: Optional[str] = None
