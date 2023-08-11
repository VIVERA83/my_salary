from typing import Optional, Union

from base.base_accessor import BaseAccessor
from base.utils import TryRun
from sqlalchemy import Delete, Insert, Update, insert
from store.blog.models import TopicModel, UserModel


@TryRun(total_timeout=20, group="postgres")
class BlogAccessor(BaseAccessor):
    """Blog service."""

    async def create_user(
        self, user_id: str, name: str, email: str, is_commit: bool = True
    ) -> UserModel:
        """Adding a new user to the database.

        The user is created based on an entry from User in the authorization service.

        Args:
            user_id: id, unique identifier, giving in UserModel in database AUTH schema.
            name: name
            email: user email
            is_commit: if True, the user saves in the database

        Returns:
            object: UserModel
        """
        smtp = (
            insert(UserModel)
            .values(
                id=user_id,
                name=name,
                email=email,
            )
            .returning(UserModel)
        )
        if is_commit:
            return await self.commit(smtp)
        return (await self.app.postgres.session.execute(smtp)).fetchone()[0]

    async def commit(self, smtp: Union[Insert, Delete, Update]):
        """Commit and return the model instance.

        Args:
            smtp: SMTP connection
        """
        async with self.app.postgres.session as session:
            user = (await session.execute(smtp)).fetchone()[0]
            await session.commit()
            return user

    async def create_topic(self, title: str, description: str) -> Optional[TopicModel]:
        async with (self.app.postgres.session.begin().session as session):
            smtp = (
                insert(TopicModel)
                .values(
                    title=title,
                    description=description,
                )
                .returning(TopicModel)
            )

            topic = await session.execute(smtp)
            await session.commit()
            return topic.fetchone()[0]

    async def update_topic(
        self, title: str = None, description: str = None
    ) -> Optional[TopicModel]:
        ...
