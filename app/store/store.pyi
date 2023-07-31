from core.components import Application
from store.user.accessor import UserAccessor
from store.user_manager.manager import AuthManager
from store.invalid_token.accessor import InvalidTokenAccessor
from store.jwt.jwt import JWTAccessor

class Store:
    """Store, data service and working with it."""

    def __init__(self, app: Application):
        """Initializing data sources.

        Args:
            app: The application
        """

        self.auth = UserAccessor(app)
        self.jwt = JWTAccessor(app)
        self.auth_manager = AuthManager(app)
        self.invalid_token = InvalidTokenAccessor(app)

def setup_store(app: Application): ...
