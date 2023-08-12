from typing import TypeVar

from sqlalchemy import insert, ValuesBase, Insert

from base.base_accessor import BaseAccessor
from store.blog.models import TopicModel

Query = TypeVar("Query", bound=ValuesBase)


class TopicAdapter(BaseAccessor):

    @staticmethod
    def query_insert_topic(title: str, description: str) -> Query:
        return insert(TopicModel).values(title=title, description=description)

    async def query_execute(self, query: Query):
        if isinstance(query, Insert):
            async with self.app.postgres.session.begin().session as session:
                result = await session.execute(query)
                await session.commit()
                session.flush(result)


topic = TopicAdapter.query_insert_topic("topic", "description")
TopicAdapter.query_execute(topic.returning())
