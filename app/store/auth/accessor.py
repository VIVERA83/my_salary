from typing import Optional

from sqlalchemy import insert, select, update

from base import BaseAccessor

from store.auth.models import UserModel as UserModel
from store.auth.jwt import Jwt


class AuthAccessor(BaseAccessor, Jwt):
    """Authorization service."""

    def _init(self):
        self.init()
        self.logger.info('Auth service is running')

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
            if user:
                return user[0]

    async def refresh(self, user_id: str, refresh_token: str) -> Optional[list[str]]:
        """Updating Access Tokens."""
        if await self.compare_refresh_token(user_id=user_id, refresh_token=refresh_token):
            return await self.create_tokens(user_id)

    async def create_tokens(self, user_id: str) -> list[str]:
        """Token generation: access_token and refresh_token.

        Args:
            user_id: user identifier

        Returns:
            object: list of tokens
        """
        subject = {'user_id': user_id}
        access_token = self.access_security.create_access_token(
            subject,
        )
        refresh_token = self.access_security.create_refresh_token(
            subject,
        )
        await self.update_refresh_token(user_id, refresh_token)
        return [access_token, refresh_token]

    async def compare_refresh_token(self, user_id: str, refresh_token: str) -> bool:
        """Token Comparison.

        The sent token is compared with the token from the database.
        True if the token is equal to the value from the token database.

        Args:
            user_id: User_id whose token is being compared with the standard from DB.
            refresh_token: The refresh token.

        Returns:
            object: True if the token is equal to the value from the refresh token.
        """
        async with self.app.database.session.begin().session as session:
            smtp = select(UserModel.refresh_token).where(UserModel.id == user_id)
            return refresh_token == (await session.execute(smtp)).scalar()

    async def update_refresh_token(
            self,
            user_id: str,
            refresh_token: Optional[str] = None,
    ):
        """Updating the refresh token in the user account.

        Args:
            user_id: The ID of the user in the database
            refresh_token: The refresh token
        """
        async with self.app.database.session.begin().session as session:
            query = (
                update(UserModel)
                .filter(UserModel.id == user_id)
                .values(refresh_token=refresh_token)
                .returning(UserModel)
            )
            await session.execute(query)
            await session.commit()
