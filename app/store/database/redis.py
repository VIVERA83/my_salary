from typing import Optional

import redis.asyncio as redis
from base.base_accessor import BaseAccessor
from redis.client import Redis

from core.settings import RedisSettings


class RedisAccessor(BaseAccessor):
    connector: Optional[Redis] = None
    settings: RedisSettings = None
    redis.Redis()

    async def connect(self):
        self.settings = RedisSettings()
        self.connector = await redis.from_url(self.settings.dsn, decode_responses=True)
        self.logger.info("Connected to Redis")

    async def disconnect(self):
        await self.connector.close()
        self.logger.info("Disconnected from Redis")
