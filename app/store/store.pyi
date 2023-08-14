from core.components import Application
from store.blog.accessor import BlogAccessor
from store.cache.accessor import CacheAccessor
from store.ems.ems import EmailMessageService
from store.token.accessor import TokenAccessor
from store.user.accessor import UserAccessor
from store.user_manager.manager import UserManager

class Store:
    """Store, data service and working with it."""

    blog: BlogAccessor
    auth: UserAccessor
    token: TokenAccessor
    auth_manager: UserManager
    cache: CacheAccessor
    ems: EmailMessageService

    def __init__(self, app: Application): ...

def setup_store(app: Application): ...
