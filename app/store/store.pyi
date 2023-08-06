from core.components import Application
from store.blog.accessor import BlogAccessor
from store.cache.accessor import CacheAccessor
from store.jwt.jwt import JWTAccessor
from store.user.accessor import UserAccessor
from store.user_manager.manager import UserManager

class Store:
    """Store, data service and working with it."""

    blog: BlogAccessor
    auth: UserAccessor
    jwt: JWTAccessor
    auth_manager: UserManager
    invalid_token: CacheAccessor

    def __init__(self, app: Application): ...

def setup_store(app: Application): ...
