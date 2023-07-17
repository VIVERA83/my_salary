# """A module describing services for working with data."""
# from typing import TYPE_CHECKING
#
# from store.database.database import Database
#
# if TYPE_CHECKING:
#     from core.components import Application
#
#
# class Store:
#     """Store, data service and working with it."""
#
#     def __init__(self, app: 'Application'):
#         """Initializing data sources.
#
#         Args:
#             app: The application
#         """
#         from store.auth.accessor import AuthAccessor
#
#         self.auth = AuthAccessor(app)
#
#
# def setup_store(app: 'Application'):
#     """Configuring the connection and disconnection of storage.
#
#     Here we inform the application about the databases of the database and other
#     data sources which we run when the application is launched,
#     and how to disable them.
#
#     Args:
#         app: The application
#     """
#     app.database = Database(app)
#     app.store = Store(app)
