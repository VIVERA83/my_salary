"""Модуль начальных настроек приложения."""
import os

from core.utils import ALGORITHM, ALGORITHMS, HEADERS, METHOD
from pydantic import BaseModel, SecretStr, field_validator, EmailStr
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))


class Base(BaseSettings):
    class Config:
        """Настройки для чтения переменных окружения из файла."""

        env_nested_delimiter = "__"
        env_file = BASE_DIR + "/.env"
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
    app_description: str = "Сервис проверки авторизации на тему узнай свою заплату"
    app_version: str = "beta"

    app_host: str = "localhost"
    app_port: int = 8004
    app_uvicorn_workers: int = 1
    app_server_host: str = "0.0.0.0"

    app_secret_key: SecretStr
    app_allowed_origins: str | list[str] = "*"
    app_allow_methods: str | list[METHOD] = "*"
    app_allow_headers: str | list[HEADERS] = "*"
    app_allow_credentials: bool = True

    app_logging: LogSettings = LogSettings()

    @field_validator("app_allow_headers", "app_allowed_origins", "app_allow_methods")
    def to_list(cls, data: str | list[METHOD | HEADERS]) -> list[METHOD | HEADERS | str]:  # noqa
        """Перевод строки в список."""
        if isinstance(data, str):
            return data.replace(" ", "").split(",")
        return data

    @property
    def base_url(self) -> str:
        """Начальный url адрес приложения."""
        return f"http://{self.app_server_host}:{self.app_port}"


class PostgresSettings(Base):
    """Параметры подключения к PostgresQL"""

    postgres_db: str
    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str
    postgres_port: str
    postgres_db_schema: str

    def dsn(self, show_secret: bool = False) -> str:
        """Возвращает link настройки."""
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(
            user=self.postgres_user,
            password=self.postgres_password.get_secret_value()
            if show_secret
            else self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            db=self.postgres_db,
        )


class RedisSettings(Base):
    redis_db: int
    redis_host: str
    redis_port: int
    redis_password: SecretStr
    redis_user: str = "default"

    def dsn(self, show_secret: bool = False) -> str:
        return "redis://{user}:{password}@{host}:{port}/{db}".format(
            user=self.redis_user,
            password=self.redis_password.get_secret_value()
            if show_secret
            else self.redis_password,
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
        )


class AuthorizationSettings(Base):
    """Authorization settings."""

    auth_key: SecretStr
    auth_algorithms: str
    auth_access_expires_delta: int
    auth_refresh_expires_delta: int

    @field_validator("auth_algorithms")
    def to_list(cls, data: str | list[ALGORITHM]) -> list[ALGORITHM]:  # noqa
        """Перевод строки в список."""
        if isinstance(data, str):
            data = data.replace(" ", "").split(",")  # noqa
        for alg in data:
            assert alg in ALGORITHMS, (
                "The encryption algorithm '{alg}' is not supported,"
                " you can use: {algs}.".format(alg=alg, algs=ALGORITHMS)
            )
        return data


class EmailMessageServiceSettings(Base):
    """Email message service settings."""

    ems_is_tls: bool = False
    ems_host: str
    ems_port: int = 587
    ems_user: str
    ems_password: SecretStr
    ems_sender: EmailStr
