from typing import Optional

from icecream import ic

from base.base_accessor import BaseAccessor
from store.blog.models import TopicModel, UserModel


class BlogAccessor(BaseAccessor):
    """Blog service."""

    async def create_user(self, user_id: str, name: str, email: str):
        query = self.app.postgres.get_query_insert(UserModel, id=user_id, name=name, email=email)
        result = await self.app.postgres.query_execute(query.returning(UserModel))
        return result.scalar_one_or_none()

    async def create_topic(self, title: str, description: str) -> Optional[TopicModel]:
        insert_data = {
            name: value for index, (name, value) in enumerate(locals().items()) if index
        }
        query = self.app.postgres.get_query_insert(TopicModel, **insert_data)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()

    async def update_topic(self, id: str, title: str = None, description: str = None):
        update_data = {
            name: value for index, (name, value) in enumerate(locals().items()) if index and value
        }
        query = self.app.postgres.get_query_update_by_id(TopicModel, **update_data)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()

    async def delete_topic(self, id: str):
        query = self.app.postgres.get_query_delete_by_id(TopicModel, id)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()
