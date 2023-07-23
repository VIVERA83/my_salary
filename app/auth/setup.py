from auth.middleware import setup_middleware
from core.components import Application


def setup(app: Application):
    """Setup Auth Service.

    Args:
        app: The application to connect
    """
    setup_middleware(app)
