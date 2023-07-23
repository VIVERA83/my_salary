""""Routes приложения """

from auth.views import auth_route
from core.components import Application


def setup_routes(app: Application):
    """Настройка подключаемых route к приложению."""
    app.include_router(auth_route)
