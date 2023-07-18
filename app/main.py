"""Модуль запуска приложения."""
import uvicorn

from core.settings import Settings
from core.app import setup_app

app = setup_app()
if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(app=setup_app(),
                host=settings.app_host,
                port=settings.app_port,
                workers=1,
                )
