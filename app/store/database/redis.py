from typing import Optional

import redis.asyncio as redis
from base.base_accessor import BaseAccessor
from core.settings import RedisSettings
from redis.client import Redis


class RedisAccessor(BaseAccessor):
    connector: Optional[Redis] = None
    settings: RedisSettings = None

    async def connect(self):
        self.settings = RedisSettings()
        self.connector = await redis.from_url(self.settings.dsn(True), decode_responses=True)
        self.logger.info("Connected to Redis, {dsn}".format(dsn=self.settings.dsn()))

    async def disconnect(self):
        await self.connector.close()
        self.logger.info("Disconnected from Redis")
