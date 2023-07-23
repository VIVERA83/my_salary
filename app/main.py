"""Модуль запуска приложения."""
import uvicorn
from core.settings import Settings

if __name__ == "__main__":
    settings = Settings()
    print(settings.logging.level)
    uvicorn.run(app="core.app:app",
                host=settings.app_host,
                port=settings.app_port,
                workers=settings.app_uvicorn_workers,
                log_level=settings.logging.level.lower())
