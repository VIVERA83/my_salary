"""Переназначенные компоненты Fast-Api."""
import logging
from typing import Optional

from core.settings import Settings
from fastapi import FastAPI, Request as FastAPIRequest, APIRouter
from starlette.datastructures import State


# from store import Store
# from store.database.database import Database


class Application(FastAPI):
    """Application главный класс.

    Описываем сервисы, которые будут использоваться в приложении.
    Так же это нужно для корректной подсказки IDE.
    """

    settings: Optional["Settings"] = None
    database: Optional["Database"] = None
    store: Optional["Store"] = None
    logger: Optional[logging.Logger] = None
    title: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    router: Optional[APIRouter] = None
    docs_url: Optional[str] = None


class Request(FastAPIRequest):
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


class CustomState(State):
    """Переопределения State.

    Для корректной подсказки IDE по методам `Request`.
    """

    token: Optional['TokenSchema']
    user_id: Optional[str] = None
