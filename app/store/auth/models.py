from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from store.database.database import Base

from dataclasses import dataclass, asdict


@dataclass
class UserModel(Base):
    """User sqlalchemy model."""

    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, )
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    is_superuser: Mapped[bool] = mapped_column(nullable=True, unique=True)
    refresh_token: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        """Representation of a string object.

        Returns:
            object: string object
        """
        return '<User id: {id}, name: {name}, email: {email} >'.format(
            id=self.id,
            name=self.name,
            email=self.email,
        )


