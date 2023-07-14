"""Модуль начальных настроек приложения."""
import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))


class Postgres(BaseModel):
    """Параметры потключения к PostgresQL"""

    db: str
    user: str
    password: str
    host: str
    port: int
    db_schema: str

    @property
    def dsn(self) -> str:
        """Возвращает link настройки."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class Log(BaseModel):
    """Параметры логирования."""

    level: str = "INFO"
    guru: bool = False
    traceback: bool = False


class Settings(BaseSettings):
    """Объединяющий класс, в котором собраны настройки приложения."""

    name: str
    host: str
    port: int
    postgres: Postgres
    logging: Log

    class Config:
        """Настройки для чтения переменных окружения из файла."""

        env_nested_delimiter = "__"
        env_file = BASE_DIR + "/.env"
        enf_file_encoding = "utf-8"
        extra = "allow"

    @property
    def base_url(self) -> str:
        """Начальный url адрес приложения."""
        return f"http://{self.host}:{self.port}"
