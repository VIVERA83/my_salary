"""Модуль запуска приложения."""
import uvicorn

from core.app import setup_app
from core.settings import Settings

if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(app=setup_app(),
                host=settings.host,
                port=settings.port,
                workers=settings.uvicorn_workers,
                )
