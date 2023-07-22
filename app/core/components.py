"""Переназначенные компоненты Fast-Api."""
import logging

from typing import Optional, Any

from fastapi.openapi.utils import get_openapi
from icecream import ic

from auth.schemes import TokenSchema
from core.settings import Settings
from fastapi import FastAPI, Request as FastAPIRequest
from starlette.datastructures import State

from core.utils import PUBLIC_ACCESS, METHODS
from store.store import Store
from store.database.database import Database


class Application(FastAPI):
    """Application главный класс.

    Описываем сервисы, которые будут использоваться в приложении.
    Так же это нужно для корректной подсказки IDE.
    """

    def __init__(self):
        super().__init__()

        self.settings = Settings()
        self.logger = logging.Logger(__name__)
        self.database = Database(self)
        self.store: Store = Store(self)
        self.free_access = PUBLIC_ACCESS
        self.openapi = self._custom_openapi

    def _custom_openapi(self) -> dict[str, Any]:

        """Обновления схемы в Openapi.

        Добавление в закрытые методы HTTPBearer.

        Returns:
            dict: Dictionary openapi schema
        """

        if self.openapi_schema:
            return self.openapi_schema
        openapi_schema = get_openapi(
            title=self.settings.app_name,
            description=self.settings.description,
            routes=self.routes,
            version=self.settings.version,
        )

        for key, path in openapi_schema['paths'].items():
            is_free, free_method = self._is_free(key)

            if not is_free:
                self._add_security(free_method, path)

        self.openapi_schema = openapi_schema
        return self.openapi_schema

    def _is_free(self, url: str):
        assert self.free_access is not None
        is_free = False
        free_method = None
        for f_p, f_m in self.free_access:
            if url[1:] == f_p:
                is_free = True
                free_method = f_m
        return is_free, free_method

    @staticmethod
    def _add_security(name: Optional[str], path: dict):
        """Add a security."""

        for method in METHODS:
            if method.upper() != name and path.get(method.lower()):
                path[method.lower()]['security'] = [{'HTTPBearer': []}]


class Request(FastAPIRequest):
    """Переопределения Request.

    Для корректной подсказки IDE по методам `Application`."""

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

    access_token: Optional['TokenSchema']
    user_id: Optional[str] = None
