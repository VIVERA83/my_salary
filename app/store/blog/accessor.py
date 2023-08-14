from typing import Optional

from base.base_accessor import BaseAccessor
from base.type_hint import Sorted_order
from store.blog.models import TopicModel, UserModel
from store.database.postgres import Query


class BlogAccessor(BaseAccessor):
    """Blog service."""

    async def create_user(self, name: str, email: str):
        """Create a new user.

        Args:
            name: Name of the new user
            email: Email address, EmailStr

        Returns:
            object: User object, UserModel
        """
        query = self.get_query_create_user(name, email)
        result = await self.app.postgres.query_execute(query)
        return result.scalar_one_or_none()

    async def create_topic(self, title: str, description: str) -> Optional[TopicModel]:
        """Create topic.

        Args:
            title: name of topic
            description: description topic

        Returns:
            object: Topic object, TopicModel
        """
        insert_data = {
            name: value for index, (name, value) in enumerate(locals().items()) if index
        }
        query = self.app.postgres.get_query_insert(TopicModel, **insert_data)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()

    async def update_topic(
        self, id: str, title: str = None, description: str = None
    ) -> Optional[TopicModel]:
        update_data = {
            name: value
            for index, (name, value) in enumerate(locals().items())
            if int(index) > 1 and value
        }
        query = self.app.postgres.get_query_update_by_field(TopicModel, "id", id, **update_data)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()

    async def delete_topic(self, id: str) -> Optional[TopicModel]:
        query = self.app.postgres.get_query_delete_by_field(TopicModel, "id", id)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()

    async def get_topic_by_id(self, id: str) -> Optional[TopicModel]:
        query = self.app.postgres.get_query_select_by_field(TopicModel, "id", id)
        result = await self.app.postgres.query_execute(query)
        return result.scalar_one_or_none()

    async def get_topics(
        self, page: int = 0, size: int = 10, sort_params: Sorted_order = None
    ) -> list[TopicModel]:
        query = self.app.postgres.get_query_filter(TopicModel, page, size, sort_params)
        result = await self.app.postgres.query_execute(query)
        return result.scalars().all()  # noqa

    def get_query_create_user(self, name: str, email: str) -> Query:
        return self.app.postgres.get_query_insert(UserModel, name=name, email=email).returning(
            UserModel
        )
