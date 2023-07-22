"""Место окончательной сборки приложения."""

from core.components import Application
from core.exceptions import setup_exception
from core.logger import setup_logging
from core.middelware import setup_middleware
from core.routes import setup_routes


def setup_app() -> Application:
    """Место сборки приложения, подключения бд, роутов, и т.д"""
    app = Application()
    setup_logging(app)
    setup_middleware(app)
    setup_exception(app)
    setup_routes(app)
    app.logger.info(f"Swagger link: {app.settings.base_url}{app.docs_url}")
    return app


app = setup_app()
