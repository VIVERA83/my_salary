"""Database..."""
import logging
from typing import Optional, Type
from uuid import uuid4

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from base.base_accessor import BaseAccessor


class Base(DeclarativeBase):
    """Setting up metadata.

    In particular, we specify a schema for storing tables.
    """

    metadata = MetaData(
        quote_schema=True,
    )
    id: Mapped[uuid4] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    def __repr__(self):
        """Redefinition.

        Returns:
            object: new instance name
        """
        return '{class_name}(id={id})'.format(
            id=self.id,
            class_name=self.__class__.__name__,
        )

    __str__ = __repr__


class Database(BaseAccessor):
    """Description of the rules for connecting.

    PostgreSQL to the Fast-Api application.
    """

    _engine: Optional[AsyncEngine] = None
    _db: Optional[Type[DeclarativeBase]] = None
    session: Optional[AsyncSession] = None

    async def connect(self):
        """Configuring the connection to the database."""
        self._db = Base
        self._engine = create_async_engine(
            self.app.settings.postgres.dsn,
            echo=False,
            future=True,
        )
        self.session = AsyncSession(self._engine, expire_on_commit=False)
        logging.info('Connected to Postgres')

    async def disconnect(self):
        """Closing the connection to the database."""
        if self._engine:
            await self._engine.dispose()
        logging.info('Disconnected from Postgres')
