from typing import Optional

from base.base_accessor import BaseAccessor
from base.type_hint import Sorted_order
from sqlalchemy import select
from store.user.models import UserModel


class UserAccessor(BaseAccessor):
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
        query = self.app.postgres.get_query_insert(
            UserModel, name=name, email=email, password=password, is_superuser=is_superuser
        )
        result = await self.app.postgres.query_execute(query.returning(UserModel))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email.

        Args:
            email: user email
        Returns:
            optional: user model
        """
        query = self.app.postgres.get_query_select_by_field(UserModel, "email", email)
        result = await self.app.postgres.query_execute(query)
        return result.scalar_one_or_none()

    async def update_refresh_token(self, user_id: str, refresh_token: str = None) -> UserModel:
        """Update the refresh token.

        Args:
            user_id: user identifier, UUID
            refresh_token: refresh token

        Returns:
            object: UserModel
        """
        update_data = {
            name: value
            for index, (name, value) in enumerate(locals().items())
            if int(index) > 1 and value
        }
        query = self.app.postgres.get_query_update_by_field(
            UserModel, "id", user_id, **update_data
        )
        result = await self.app.postgres.query_execute(query)
        return result.scalar_one_or_none()

    async def update_password(self, user_id: str, password: str) -> Optional[UserModel]:
        update_data = {
            name: value
            for index, (name, value) in enumerate(locals().items())
            if int(index) > 1 and value
        }
        query = self.app.postgres.get_query_update_by_field(
            UserModel, "id", user_id, **update_data
        )
        result = await self.app.postgres.query_execute(query)
        return result.scalar_one_or_none()

    async def get_users(
        self, page: int = 0, size: int = 10, sort_params: Sorted_order = None
    ) -> list[UserModel]:
        query = self.app.postgres.get_query_filter(UserModel, page, size, sort_params)
        result = await self.app.postgres.query_execute(query)
        return result.scalars().all()  # noqa
