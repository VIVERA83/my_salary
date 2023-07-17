"""Модуль начальных настроек приложения."""
import os
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from auth.utils import ALGORITHMS, METHODS, HEADERS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))


class Base(BaseSettings):
    class Config:
        """Настройки для чтения переменных окружения из файла."""

        env_nested_delimiter = "__"
        env_file = BASE_DIR + "/.env_local"
        enf_file_encoding = "utf-8"
        extra = "ignore"


class LogSettings(BaseModel):
    """Параметры логирования."""

    level: str = "INFO"
    guru: bool = True
    traceback: bool = False


class Settings(Base):
    """Объединяющий класс, в котором собраны настройки приложения."""

    app_name: str
    app_host: str
    app_port: int
    app_uvicorn_workers: int = 1

    secret_key: str
    allowed_origins: list[str]
    allow_methods: list[METHODS]
    allow_headers: list[HEADERS]
    allow_credentials: bool

    logging: LogSettings

    @property
    def base_url(self) -> str:
        """Начальный url адрес приложения."""
        return f"http://{self.app_host}:{self.app_port}"


class PostgresSettings(Base):
    """Параметры подключения к PostgresQL"""

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db_schema: str

    @property
    def dsn(self) -> str:
        """Возвращает link настройки."""
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(
            user=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            db=self.postgres_db
        )


class AuthorizationSettings(Base):
    """Authorization settings."""

    key: str
    algorithms: list[ALGORITHMS]
    access_expires_delta: int = 120
    refresh_expires_delta: int = 3600


