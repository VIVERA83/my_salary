from typing import Optional, Union

from base.base_accessor import BaseAccessor
from base.utils import TryRun
from sqlalchemy import Delete, Insert, Update, and_, insert, select, update
from store.user.models import UserModel


@TryRun(total_timeout=15, group="postgres")
class UserAccessor(BaseAccessor):
    """Authorization service."""

    async def create_user(
        self,
        name: str,
        email: str,
        password: str,
        is_superuser: Optional[bool] = None,
        is_commit: bool = True,
    ) -> UserModel:
        """Adding a new user to the database.

        Args:
            name: name
            email: user email
            password: user password
            is_superuser: boolean if true user is superuser
            is_commit: if True, the user saves in the database

        Returns:
            object: UserModel
        """
        smtp = (
            insert(UserModel)
            .values(
                name=name,
                email=email,
                password=password,
                is_superuser=is_superuser,
            )
            .returning(UserModel)
        )
        if is_commit:
            return await self.commit(smtp)
        return (await self.app.postgres.session.execute(smtp)).fetchone()[0]

    # @before_execution(raise_exception=True)
    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email.

        Args:
            email: user email

        Returns:
            optional: user model
        """
        async with self.app.postgres.session.begin().session as session:
            smtp = select(UserModel).where(UserModel.email == email)
            if user := (await session.execute(smtp)).unique().fetchone():
                return user[0]

    async def get_user_by_id_and_refresh_token(
        self, user_id: str, refresh_token: str
    ) -> Optional[UserModel]:
        """Get a user by id."""
        async with self.app.postgres.session.begin().session as session:
            smtp = select(UserModel).where(
                and_(
                    UserModel.id == user_id,
                    UserModel.refresh_token == refresh_token,
                )
            )
            if user := (await session.execute(smtp)).unique().fetchone():
                return user[0]

    async def add_refresh_token_to_user(self, user_id: str, refresh_token: str = None):
        async with self.app.postgres.session.begin().session as session:
            query = (
                update(UserModel)
                .filter(UserModel.id == user_id)
                .values(refresh_token=refresh_token)
                .returning(UserModel)
            )
            await session.execute(query)
            await session.commit()

    async def commit(self, smtp: Union[Insert, Delete, Update]):
        """Commit and return the model instance.

        Args:
            smtp: SMTP connection
        """
        async with self.app.postgres.session as session:
            user = (await session.execute(smtp)).fetchone()[0]
            await session.commit()
            return user
