""""Routes приложения """

from core.components import Application
from user.views import auth_route


def setup_routes(app: Application):
    """Настройка подключаемых route к приложению."""
    app.include_router(auth_route)
