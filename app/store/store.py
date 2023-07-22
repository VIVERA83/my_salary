"""A module describing services for working with data."""

from store.database.database import Database
from store.auth.accessor import AuthAccessor
from store.jwt.jwt import JWTAccessor
from store.auth_manager.manager import AuthManager


class Store:
    """Store, data service and working with it."""

    def __init__(self, app):
        """Initializing data sources.

        Args:
            app: The application
        """

        self.auth = AuthAccessor(app)
        self.jwt = JWTAccessor(app)
        self.auth_manager = AuthManager(app)


def setup_store(app):
    """Configuring the connection and disconnection of storage.

    Here we inform the application about the databases of the database and other
    data sources which we run when the application is launched,
    and how to disable them.

    Args:
        app: The application
    """
    app.database = Database(app)
    app.store = Store(app)
