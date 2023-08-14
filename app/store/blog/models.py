from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from store.database.postgres import Base


@dataclass
class UserModel(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)

    def __repr__(self) -> str:
        """Representation of a string object.

        Returns:
            object: string object
        """
        return "<UserBlog id: {id}, name: {name}, email: {email} >".format(
            id=self.id,
            name=self.name,
            email=self.email,
        )


@dataclass
class TopicModel(Base):
    __tablename__ = "topics"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(250))
