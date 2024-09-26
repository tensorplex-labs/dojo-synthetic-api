import json
from collections.abc import Awaitable
from typing import Any, cast

import uuid_utils
from fastapi.encoders import jsonable_encoder
from loguru import logger
from redis import asyncio as aioredis
from redis.asyncio.client import Redis

from commons.config import RedisSettings, get_settings


def build_redis_url() -> str:
    redis: RedisSettings = get_settings().redis
    if redis.username and redis.password:
        return f"redis://{redis.username}:{redis.password.get_secret_value()}@{redis.host}:{redis.port}"
    elif redis.password:
        return f"redis://:{redis.password.get_secret_value()}@{redis.host}:{redis.port}"
    else:
        return f"redis://{redis.host}:{redis.port}"


class RedisCache:
    _instance: "RedisCache | None" = None
    _key_prefix: str = "synthetic"
    _queue_key: str = "queue"
    # historical data
    _hist_key: str = "history"
    _encoding: str = "utf-8"
    redis: Redis  # pyright: ignore[reportMissingTypeArgument]

    def __new__(cls) -> "RedisCache":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            redis_url = build_redis_url()
            cls._instance.redis = aioredis.from_url(url=redis_url)
        return cls._instance

    def _build_key(self, *parts: str) -> str:
        if len(parts) == 0:
            raise ValueError("Must specify at least one redis key")
        return f"{self._key_prefix}:{':'.join(parts)}"

    async def close(self) -> None:
        if self.redis:  # pyright: ignore[reportUnknownMemberType]
            await self.redis.close()  # pyright: ignore[reportUnknownMemberType]

    async def get_queue_length(self) -> int:
        key = self._build_key(self._queue_key)
        if not self.redis:  # pyright: ignore[reportUnknownMemberType]
            raise ValueError("Redis connection not established")
        num_items: int = await cast(Awaitable[int], self.redis.llen(key))  # pyright: ignore[reportUnknownMemberType]
        logger.debug(f"Queue length: {num_items}")
        return num_items

    async def enqueue(self, data: Any) -> int:
        """Uses Redis list to enqueue data, in order to maintain a buffer of QA
        pairs. This is because each QA pair may take long to generate and we
        want to maintain responsiveness of the FastAPI app.

        Args:
            key (str): Redis key that will be prefixed with `_key_prefix`.
            data (Any): Data to be enqueued.

        Raises:
            ValueError: If data is None.

        Returns:
            int: Number of elements in the queue.
        """

        if data is None:
            raise ValueError("Data is required")

        # keep the historical data as is
        # use uuid7 so keys in redis are sorted by time
        hist_key = self._build_key(self._hist_key, uuid_utils.uuid7().__str__())
        try:
            logger.debug(f"Writing persistent data into {hist_key}")
            # place into persistent key
            str_data = json.dumps(jsonable_encoder(data)).encode(self._encoding)
            await self.redis.set(hist_key, str_data)  # pyright: ignore[reportUnknownMemberType]

            queue_key = self._build_key(self._queue_key)
            logger.debug(f"Writing queue data into {queue_key}")
            # fuck it and push the data into the queue as well, instead of it being a reference to the persistent data
            # this also simplifies dequeuing logic
            num_items: int = await self.redis.rpush(queue_key, str_data)  # type: ignore
            return num_items
        except Exception as exc:
            logger.opt(exception=True).error(
                f"Error enqueuing data into key: {hist_key}, error: {exc}"
            )
            raise

    async def dequeue(self) -> str | None:
        """Dequeue an item from the specified queue key, assumes it is a queue and
        returns the value as as a string
        """
        current_key: str = self._build_key(self._queue_key)
        try:
            value_raw = await cast(
                Awaitable[str | bytes | list[Any] | None],
                self.redis.lpop(current_key),  # pyright: ignore[reportUnknownMemberType]
            )

            value: str | None = None
            if isinstance(value_raw, list):
                raise NotImplementedError("not implemented")
            elif isinstance(value_raw, bytes):
                value = value_raw.decode(self._encoding)

            return value
        except Exception as exc:
            logger.opt(exception=True).error(
                f"Error dequeuing data from key: {current_key}, error: {exc}"
            )
            raise
