from typing import Optional

import redis.asyncio as redis
from base.base_accessor import BaseAccessor
from redis.client import Redis


class RedisAccessor(BaseAccessor):
    connector: Optional[Redis] = None
    settings = None

    async def connect(self):
        self.settings = None
        self.connector = await redis.from_url("redis://0.0.0.0", decode_responses=True)
        self.logger.info("Connected to Redis")

    async def disconnect(self):
        await self.connector.close()
        self.logger.info("Disconnected from Redis")

