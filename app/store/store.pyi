from core.components import Application
from store.cache.accessor import CacheAccessor
from store.jwt.jwt import JWTAccessor
from store.user.accessor import UserAccessor
from store.user_manager.manager import UserManager

class Store:
    """Store, data service and working with it."""

    def __init__(self, app: Application):
        """Initializing data sources.

        Args:
            app: The application
        """

        self.auth = UserAccessor(app)
        self.jwt = JWTAccessor(app)
        self.auth_manager = UserManager(app)
        self.invalid_token = CacheAccessor(app)

def setup_store(app: Application): ...
