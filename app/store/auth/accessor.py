from typing import Optional

from sqlalchemy import insert, select, update, and_

from base.base_accessor import BaseAccessor

from store.auth.models import UserModel as UserModel


class AuthAccessor(BaseAccessor):
    """Authorization service."""

    async def create_user(
            self,
            name: str,
            email: str,
            password: str,
            is_superuser: Optional[bool] = None,
    ) -> Optional[UserModel]:
        """Adding a new user to the database.

        Args:
            name: name
            email: user email
            password: user password
            is_superuser: boolean if true user is superuser

        Returns:
            object: UserModel
        """
        async with self.app.database.session.begin().session as session:
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
            user = await session.execute(smtp)
            await session.commit()
            if user:
                return user.unique().fetchone()[0]

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email.

        Args:
            email: user email

        Returns:
            optional: user model
        """
        async with self.app.database.session.begin().session as session:
            smtp = select(UserModel).where(UserModel.email == email)
            user = (await session.execute(smtp)).unique().fetchone()
            return user[0]

    async def get_user_by_id_and_refresh_token(self, user_id: str, refresh_token: str) -> Optional[UserModel]:
        """Get a user by id."""
        async with self.app.database.session.begin().session as session:
            smtp = select(UserModel).where(and_(UserModel.id == user_id, UserModel.refresh_token == refresh_token))
            user = (await session.execute(smtp)).unique().fetchone()
            return user[0]

    async def add_refresh_token_to_user(self, user_id: str, refresh_token: str = None):
        async with self.app.database.session.begin().session as session:
            query = (
                update(UserModel)
                .filter(UserModel.id == user_id)
                .values(refresh_token=refresh_token)
                .returning(UserModel)
            )
            await session.execute(query)
            await session.commit()

