from dataclasses import dataclass
from typing import Optional, Union

from icecream import ic

from base.base_accessor import BaseAccessor
from base.utils import TryRun
from sqlalchemy import Delete, Insert, Update, insert, select, update, Select
from store.user.models import UserModel


# @TryRun(total_timeout=15, group="postgres")
class UserAccessor(BaseAccessor):
    """Authorization service."""

    async def create_user(
        self,
        name: str,
        email: str,
        password: str,
        is_superuser: Optional[bool] = None,
        is_commit: bool = True,
    ) -> Optional[UserModel]:
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
            if result := await self.commit(smtp):
                return result[0]
            return None

        return (await self.app.postgres.session.execute(smtp)).fetchone()[0]

    async def get_user_by_email(self, email: str, is_commit: bool = True) -> Optional[UserModel]:
        """Get a user by email.

        Args:
            email: user email
            is_commit: commit operation
        Returns:
            optional: user model
        """
        smtp = select(UserModel).where(UserModel.email == email)
        if is_commit:
            if data := await self.commit(smtp):
                return data[0]
            return None
        return (await self.app.postgres.session.execute(smtp)).fetchone()[0]

    async def update_refresh_token(
        self, user_id: str, refresh_token: str = None, is_commit: bool = True
    ) -> UserModel:
        smtp = (
            update(UserModel)
            .filter(UserModel.id == user_id)
            .values(refresh_token=refresh_token)
            .returning(UserModel)
        )
        if is_commit:
            await self.commit(smtp)
        return (await self.app.postgres.session.execute(smtp)).fetchone()[0]

    async def update_password(
        self, user_id: str, password: str, is_commit: bool = True
    ) -> Optional[UserModel]:
        smtp = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(password=password)
            .returning(UserModel)
        )
        if is_commit:
            if result := await self.commit(smtp):
                return result[0]
            return None
        return (await self.app.postgres.session.execute(smtp)).fetchone()[0]

    async def commit(self, smtp: Union[Insert, Delete, Update, Select]) -> list[dataclass]:
        """Commit and return the model instance.

        Args:
            smtp: SMTP connection
            one: boolean, if True return one object
        """
        data = []
        async with self.app.postgres.session.begin().session as session:
            result = await session.execute(smtp)
            await session.commit()
            for row in result:
                for item in row:
                    data.append(item)
        return data

    async def get_users(self, is_commit: bool = True) -> list[UserModel]:
        smtp = select(UserModel).limit(1)
        if is_commit:
            return await self.commit(smtp)
        return (await self.app.postgres.session.execute(smtp)).unique.all()
