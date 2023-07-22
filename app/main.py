"""Модуль запуска приложения."""
import uvicorn

from core.settings import Settings

if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(app="core.app:app",
                host=settings.app_host,
                port=settings.app_port,
                workers=settings.app_uvicorn_workers,
                )
