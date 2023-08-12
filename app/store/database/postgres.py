"""Database..."""
from dataclasses import asdict, dataclass, is_dataclass
from typing import Optional, Type, Any, TypeVar
from uuid import uuid4

from base.base_accessor import BaseAccessor
from core.settings import PostgresSettings
from sqlalchemy import DATETIME, TIMESTAMP, MetaData, func, UpdateBase, Result, insert, ValuesBase
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass

Query = TypeVar("Query", bound=ValuesBase)
Model = TypeVar("Model", bound=DeclarativeAttributeIntercept)


@dataclass
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
    created: Mapped[DATETIME] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    modified: Mapped[DATETIME] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    def as_dict(self) -> dict:
        assert is_dataclass(self), f"Wrap the model `{self.__name__}` in a dataclass"
        return asdict(self)  # noqa

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
            self.settings.dsn(True),
            echo=False,
            future=True,
        )
        self.session = AsyncSession(self._engine, expire_on_commit=False)
        self.logger.info("Connected to Postgres, {dsn}".format(dsn=self.settings.dsn()))

    async def disconnect(self):
        """Closing the connection to the database."""
        if self._engine:
            await self._engine.dispose()
        self.logger.info("Disconnected from Postgres")

    @staticmethod
    def get_query_insert(model: Model, **insert_data) -> Query:
        return insert(model).values(**insert_data)

    @staticmethod
    def get_query_update(model: Model, **update_data) -> Query:
        return insert(model).values(**update_data)

    async def query_execute(self, query: Query | UpdateBase, ) -> Result[Any]:
        async with self.app.postgres.session.begin().session as session:
            result = await session.execute(query)
            await session.commit()
            return result
