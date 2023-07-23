"""Модуль начальных настроек приложения."""
import os

from core.utils import ALGORITHMS, HEADERS, METHOD
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings

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
    traceback: bool = True


class Settings(Base):
    """Объединяющий класс, в котором собраны настройки приложения."""

    app_name: str = "My_salary"
    description: str = "Сервис проверки авторизации на тему узнай свою заплату"
    version: str = "beta"

    app_host: str = "localhost"
    app_port: int = 8004
    app_uvicorn_workers: int = 1
    server_host: str = "0.0.0.0"

    secret_key: str = "secret_key"
    allowed_origins: str | list[str] = "*"
    allow_methods: str | list[METHOD] = "*"
    allow_headers: str | list[HEADERS] = "*"
    allow_credentials: bool = True

    logging: LogSettings = LogSettings()

    @field_validator('allow_headers', "allowed_origins", "allow_methods")
    def to_list(cls, data: str | list[METHOD | HEADERS]) -> list[METHOD | HEADERS | str]:
        """Перевод строки в список."""
        if isinstance(data, str):
            return data.replace(" ", "").split(",")
        return data

    @property
    def base_url(self) -> str:
        """Начальный url адрес приложения."""
        return f"http://{self.server_host}:{self.app_port}"


class PostgresSettings(Base):
    """Параметры подключения к PostgresQL"""

    postgres_db: str = "test_db"
    postgres_user: str = "test_user"
    postgres_password: str = "test_password"
    postgres_host: str = "127.0.0.1"
    postgres_port: str = "5432"
    postgres_db_schema: str = "public"

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

    key: str = "authorization key"
    algorithms: str = "HS256"
    access_expires_delta: int = 120
    refresh_expires_delta: int = 3600

    @field_validator("algorithms")
    def to_list(cls, data: str | list[ALGORITHMS]) -> list[ALGORITHMS]:
        """Перевод строки в список."""
        if isinstance(data, str):
            return data.replace(" ", "").split(",")  # noqa
        return data
