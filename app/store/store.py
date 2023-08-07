"""A module describing services for working with data."""
from store.blog.accessor import BlogAccessor
from store.cache.accessor import CacheAccessor
from store.database.postgres import Postgres
from store.database.redis import RedisAccessor
from store.ems.ems import EmailMessageService
from store.token.accessor import TokenAccessor
from store.user.accessor import UserAccessor
from store.user_manager.manager import UserManager


class Store:
    """Store, data service and working with it."""

    def __init__(self, app):
        """Initializing data sources.

        Args:
            app: The application
        """

        self.auth = UserAccessor(app)
        self.token = TokenAccessor(app)
        self.auth_manager = UserManager(app)
        self.cache = CacheAccessor(app)
        self.blog = BlogAccessor(app)
        self.ems = EmailMessageService(app)


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
