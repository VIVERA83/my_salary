"""A module describing services for working with data."""

from store.auth.accessor import AuthAccessor
from store.auth_manager.manager import AuthManager
from store.database.postgres import Postgres
from store.database.redis import RedisAccessor
from store.invalid_token.accessor import InvalidTokenAccessor
from store.jwt.jwt import JWTAccessor


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
        self.invalid_token = InvalidTokenAccessor(app)


def setup_store(app):
    """Configuring the connection and disconnection of storage.

    Here we inform the application about the databases of the database and other
    data sources which we run when the application is launched,
    and how to disable them.

    Args:
        app: The application
    """
    app.postgres = Postgres(app)
    app.redis = RedisAccessor(app)
    app.store = Store(app)
