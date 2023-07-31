"""Database..."""
from dataclasses import asdict
from typing import Optional, Type
from uuid import uuid4

from base.base_accessor import BaseAccessor
from core.settings import PostgresSettings
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Setting up metadata.

    In particular, we specify a schema for storing tables.
    """

    metadata = MetaData(
        schema=PostgresSettings().postgres_db_schema,
        quote_schema=True,
    )
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    def __repr__(self):
        """Redefinition.

        Returns:
            object: new instance name
        """
        return "{class_name}(id={id})".format(
            id=self.id,
            class_name=self.__class__.__name__,
        )

    __str__ = __repr__

    def as_dict(self) -> dict:
        return asdict(self)  # noqa


class Postgres(BaseAccessor):
    """Description of the rules for connecting.

    PostgreSQL to the Fast-Api application.
    """

    _engine: Optional[AsyncEngine] = None
    _db: Optional[Type[DeclarativeBase]] = None
    session: Optional[AsyncSession] = None
    settings: Optional[PostgresSettings] = None

    async def connect(self):
        """Configuring the connection to the database."""
        self.settings = PostgresSettings()
        self._db = Base
        self._engine = create_async_engine(
            self.settings.dsn,
            echo=False,
            future=True,
        )
        self.session = AsyncSession(self._engine, expire_on_commit=False)
        self.logger.info("Connected to Postgres")

    async def disconnect(self):
        """Closing the connection to the database."""
        if self._engine:
            await self._engine.dispose()
        self.logger.info("Disconnected from Postgres")