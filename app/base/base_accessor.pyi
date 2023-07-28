from logging import Logger
from typing import Optional

from core.components import Application

class BaseAccessor:
    logger: Optional[Logger]
    app: Optional[Application]

    def __init__(self, app: Application): ...
    def _init(self):
        """Description of additional actions for initialization."""
    async def connect(self):
        """The logic responsible for connecting and configuring.

        The module to the application context
        as an example, setting up a connection to a third-party API
        """
    async def disconnect(self):
        """Setting up the correct closing of all connections."""
