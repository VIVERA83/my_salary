from base.base_accessor import BaseAccessor


class CacheAccessor(BaseAccessor):
    """Authorization service."""

    async def set_token(self, token: str, user_id: str, expires: int):
        await self.app.redis.connector.set(name=token, value=user_id, ex=expires)

    async def get_token(self, token: str) -> str | None:
        return await self.app.redis.connector.get(name=token)
