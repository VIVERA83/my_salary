"""Место окончательной сборки приложения."""

from core.components import Application
from core.exceptions import setup_exception
from core.logger import setup_logging
from core.middelware import setup_middleware
from core.routes import setup_routes
from core.settings import Settings
from store.store import setup_store


def setup_app() -> Application:
    """Место сборки приложения, подключения бд, роутов, и т.д"""
    application = Application()
    application.settings = Settings()
    setup_logging(application)
    setup_store(application)
    setup_middleware(application)
    setup_exception(application)
    setup_routes(application)
    application.logger.info(f"Swagger link: {application.settings.base_url}{application.docs_url}")
    return application


app = setup_app()
