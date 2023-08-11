from base.base_accessor import BaseAccessor
from base.utils import TryRun


@TryRun(total_timeout=1)
class CacheAccessor(BaseAccessor):
    """Authorization service."""

    async def set(self, name: str, value: str | None, expires: int) -> bool:
        """Save temporary data in the cache.

        Args:
            name: The name of the cache
            value: The value to set to the cache
            expires: The time the cache expires

        Returns:
            bool: True if the cache was successfully
        """
        return await self.app.redis.connector.set(name=name, value=value, ex=expires)  # noqa

    async def get(self, name: str) -> str | dict | None:
        """Get temporary data from the cache.

        Args:
            name: The name of the cache

        Returns:
            Any: Any temporary data
        """
        return await self.app.redis.connector.get(name=name)

    async def ttl(self, name: str) -> int:
        """Get a lifetime.

        Args:
            name: The name of the cache

        Returns:
            obj: The lifetime in seconds, if not found return -2, if timeless return -1
        """

        return await self.app.redis.connector.ttl(name=name)

    async def delete(self, name: str) -> bool:
        """Delete one or more keys specified by 'names'.

        Args:
            name: The name of the cache
        """
        return await self.app.redis.connector.delete(name)
