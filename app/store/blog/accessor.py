from typing import Optional
from varname.helpers import varname
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
        insert_data = {name: value for index, (name, value) in enumerate(locals().items()) if index}
        query = self.app.postgres.get_query_insert(TopicModel, **insert_data)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()

    async def update_topic(self, title: str = None, description: str = None):
        update_data = {name: value for index, (name, value) in enumerate(locals().items()) if index and value}
        query = self.app.postgres.get_query_update(TopicModel, **update_data)
        result = await self.app.postgres.query_execute(query.returning(TopicModel))
        return result.scalar_one_or_none()

#
# def create_params(**kwargs):
#

    # [name for name, value in locals().items() if value is x]
    # return {name: value for name, value in locals().items()}

# async def create_user(
#         self, user_id: str, name: str, email: str, is_commit: bool = True
# ) -> UserModel:
#     """Adding a new user to the database.
#
#     The user is created based on an entry from User in the authorization service.
#
#     Args:
#         user_id: id, unique identifier, giving in UserModel in database AUTH schema.
#         name: name
#         email: user email
#         is_commit: if True, the user saves in the database
#
#     Returns:
#         object: UserModel
#     """
#     smtp = (
#         insert(UserModel)
#         .values(
#             id=user_id,
#             name=name,
#             email=email,
#         )
#         .returning(UserModel)
#     )
#     if is_commit:
#         return await self.commit(smtp)
#     return (await self.app.postgres.session.execute(smtp)).fetchone()[0]
#
# async def commit(self, smtp):
#     data = await self.app.postgres.insert(smtp)
#     ic(data)
#     return data
#
# # async def commit(self, smtp: Union[Insert, Delete, Update]):
# #     """Commit and return the model instance.
# #
# #     Args:
# #         smtp: SMTP connection
# #     """
# #     async with self.app.postgres.session as session:
# #         user = (await session.execute(smtp)).fetchone()[0]
# #         await session.commit()
# #         return user
#
# # async def create_topic(self, title: str, description: str) -> Optional[TopicModel]:
# #     async with (self.app.postgres.session.begin().session as session):
# #         smtp = (
# #             insert(TopicModel)
# #             .values(
# #                 title=title,
# #                 description=description,
# #             )
# #             .returning(TopicModel)
# #         )
# #
# #         topic = await session.execute(smtp)
# #         await session.commit()
# #         return topic.fetchone()[0]
#
# def topic(self, title: str, description: str):
#     smtp = (
#         insert(TopicModel)
#         .values(
#             title=title,
#             description=description,
#         )
#         .returning(TopicModel)
#     )
#     return smtp
#
# async def create_topic(self, title: str, description: str) -> Optional[TopicModel]:
#     # async with (self.app.postgres.session.begin().session as session):
#     # smtp = (
#     #     insert(TopicModel)
#     #     .values(
#     #         title=title,
#     #         description=description,
#     #     )
#     #     .returning(TopicModel)
#     # )
#     data = await self.commit(await self.topic(title, description))
#     for item in data.first():
#         ic(item)
#     return data
#     # topic = await session.execute(smtp)
#     # await session.commit()
#     # return topic.fetchone()[0]
#
# async def update_topic(
#         self, title: str = None, description: str = None
# ) -> Optional[TopicModel]:
#     ...
