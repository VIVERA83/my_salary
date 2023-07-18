"""Модуль запуска приложения."""
import uvicorn

from core.app import setup_app
from core.settings import Settings

app = setup_app()

if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(app=app,
                host=settings.app_host,
                port=settings.app_port,
                workers=settings.app_uvicorn_workers,
                )
