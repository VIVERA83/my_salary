from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from store.database.database import Base


class UserModel(Base):
    """User sqlalchemy model."""

    __tablename__ = 'users'

    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    is_superuser: Mapped[bool] = mapped_column(default=False, index=True)
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
