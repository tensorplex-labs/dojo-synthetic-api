import json

from redis import asyncio as aioredis

from commons.config import get_settings


def build_redis_url() -> str:
    redis = get_settings().redis
    if redis.username and redis.password:
        return f"redis://{redis.username}:{redis.password.get_secret_value()}@{redis.host}:{redis.port}"
    elif redis.password:
        return f"redis://:{redis.password.get_secret_value()}@{redis.host}:{redis.port}"
    else:
        return f"redis://{redis.host}:{redis.port}"


class RedisCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.redis = None
        return cls._instance

    async def connect(self):
        if self.redis is None:
            redis_url = build_redis_url()
            self.redis = await aioredis.from_url(redis_url)

    async def put(self, key: str, value: dict):
        if self.redis is None:
            await self.connect()
        await self.redis.set(key, json.dumps(value))

    async def get(self, key: str) -> dict | None:
        if self.redis is None:
            await self.connect()
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def close(self):
        if self.redis:
            await self.redis.aclose()

    async def check_num_keys(self, key):
        if self.redis is None:
            await self.connect()
        keys = await self.redis.keys(f"{key}*")
        return len(keys)
