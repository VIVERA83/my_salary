from typing import Optional
from uuid import UUID

from icecream import ic

from base.base_accessor import BaseAccessor
from sqlalchemy import insert
from store.blog.models import UserModel, TopicModel

ic.includeContext = True


class BlogAccessor(BaseAccessor):
    """Blog service."""

    async def create_user(
            self,
            user_id: UUID,
            name: str,
            email: str,
    ) -> Optional[UserModel]:
        """Adding a new user to the database.

        The user is created based on an entry from User in the authorization service.

        Args:
            user_id: id, unique identifier, giving in UserModel in database AUTH schema.
            name: name
            email: user email

        Returns:
            object: UserModel
        """
        async with self.app.postgres.session.begin().session as session:
            smtp = (
                insert(UserModel)
                .values(
                    id=user_id,
                    name=name,
                    email=email,
                )
                .returning(UserModel)
            )
            user = await session.execute(smtp)
            await session.commit()
            return user.unique().fetchone()[0]

    async def create_topic(self, title: str, description: str) -> Optional[TopicModel]:
        async with (self.app.postgres.session.begin().session as session):
            smtp = insert(TopicModel).values(
                title=title,
                description=description,
            ).returning(TopicModel)

            topic = await session.execute(smtp)
            await session.commit()
            return topic.fetchone()[0]

    async def update_topic(self, title: str = None, description: str = None) -> Optional[TopicModel]:
        ...
