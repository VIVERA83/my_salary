"""The base class responsible for linking logic to the base application."""


class BaseAccessor:
    """The base class responsible for linking logic to the base application."""

    def __init__(self, app):
        """Initialization of the connected service in the main Fast-Api application.

        Args:
            app: The application
        """
        self.app = app
        self.logger = app.logger
        app.on_event("startup")(self.connect)
        app.on_event("shutdown")(self.disconnect)
        self._init()

    def _init(self):
        """Description of additional actions for initialization."""

    async def connect(self):
        """The logic responsible for connecting and configuring.

        The module to the application context
        as an example, setting up a connection to a third-party API
        """

    async def disconnect(self):
        """Setting up the correct closing of all connections."""
