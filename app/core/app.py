"""Место окончательной сборки приложения."""

from core import Application
from core.exceptions import setup_exception
from core.logger import setup_logging
from core.middelware import setup_middleware
from core.routes import setup_routes
from core.settings import Settings
from auth.setup import setup as setup_auth
from store.store import setup_store


def setup_app() -> Application:
    """Место сборки приложения, подключения бд, роутов, и т.д"""
    app = Application()
    app.settings = Settings()
    app.title = app.settings.name
    setup_logging(app)
    setup_middleware(app)
    setup_exception(app)
    setup_routes(app)
    setup_store(app)
    setup_auth(app)
    app.logger.info(f"Swagger link: {app.settings.base_url}{app.docs_url}")  # noqa
    return app
