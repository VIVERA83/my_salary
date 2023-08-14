""""Routes приложения """
from blog.topic.views import topic_route
from core.components import Application
from user.views import auth_route


def setup_routes(app: Application):
    """Настройка подключаемых route к приложению."""
    app.include_router(auth_route)
    app.include_router(topic_route)
