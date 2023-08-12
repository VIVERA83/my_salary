from typing import Dict, Literal, Optional

from base.base_accessor import BaseAccessor
from sqlalchemy import select, text
from store.blog.models import TopicModel, UserModel

Field_names = Literal["id", "title", "description", "created", "modified"]
Sorted_direction = Literal["ASK", "DESC"]
Sorted_order = Dict[Field_names, Sorted_direction]


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

    async def update_topic(
        self, id: str, title: str = None, description: str = None
    ) -> Optional[TopicModel]:
        update_data = {
            name: value for index, (name, value) in enumerate(locals().items()) if index and value
        }
        query = self.app.postgres.get_query_update_by_id(TopicModel, **update_data)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()

    async def delete_topic(self, id: str) -> Optional[TopicModel]:
        query = self.app.postgres.get_query_delete_by_id(TopicModel, id)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()

    async def get_topic_by_id(self, id: str) -> Optional[TopicModel]:
        query = self.app.postgres.get_query_select_by_id(TopicModel, id)
        result = await self.app.postgres.query_execute(query)
        return result.scalar_one_or_none()

    async def get_topics(
        self, page: int = 0, size: int = 10, sort_params: Sorted_order = None
    ) -> list[TopicModel]:
        query = select(TopicModel).limit(size).offset(page * size)
        query_sort = ", ".join([f"{name} {value}" for name, value in sort_params.items()])
        query = query.order_by(text(query_sort))
        result = await self.app.postgres.query_execute(query)
        return result.scalars().all()  # noqa
