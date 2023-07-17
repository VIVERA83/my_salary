from auth.exceptions import setup_exception
from auth.middleware import setup_middleware
from auth.views import auth_route

from core import Application


def setup(app: Application):
    """Setup Auth Service.

    Args:
        app: The application to connect
    """
    setup_exception(app)
    setup_middleware(app)
    app.include_router(auth_route)
