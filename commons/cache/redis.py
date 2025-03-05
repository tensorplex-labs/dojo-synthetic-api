import json
from collections.abc import Awaitable
from datetime import datetime
from typing import Any, cast

import uuid_utils
from fastapi.encoders import jsonable_encoder
from loguru import logger
from redis import asyncio as aioredis
from redis.asyncio.client import Redis

from commons.config import RedisSettings, get_settings, parse_cli_args


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
    # key prefix to historical data
    _hist_key_prefix: str = "history"
    # key to figure out how many workers are working
    _num_workers_active_key: str = "num_workers_active"
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
        try:
            # clear all active workers
            delta = -1 * await self.get_num_workers_active()
            await self.update_num_workers_active(delta)

            if self.redis:
                await self.redis.close()
        except Exception as exc:
            logger.opt(exception=True).error(f"Error closing Redis connection: {exc}")

    async def get_queue_length(self) -> int:
        key = self._build_key(self._queue_key)
        num_items: int = await cast(Awaitable[int], self.redis.llen(key))
        logger.trace(f"Queue length: {num_items}, time: {(datetime.now().timestamp())}")
        return num_items

    async def get_num_workers_active(self) -> int:
        key = self._build_key(self._num_workers_active_key)
        value = await self.redis.get(key)
        num_active = 0 if value is None else int(value)
        logger.trace(
            f"Number of active workers: {num_active}, time: {(datetime.now().timestamp())}"
        )
        return num_active

    async def update_num_workers_active(self, delta: int) -> int:
        """Update the number of workers active by delta.

        Args:
            delta (int): Amount to increment/decrement the count by. To decrement use a negative number.

        Returns:
            int: The new number of workers active.
        """
        key = self._build_key(self._num_workers_active_key)

        lock_key = self._build_key(key, "lock")
        num_workers_active_lock = self.redis.lock(
            name=lock_key,
            timeout=60,
            blocking=True,
        )
        num_active: int = 0
        try:
            if await num_workers_active_lock.acquire():
                num_active = await self.get_num_workers_active() + delta
                # ensure it doesn't go below 0
                num_active = max(num_active, 0)
                await self.redis.set(key, num_active)
        finally:
            # ensure we always release the lock
            try:
                await num_workers_active_lock.release()
            except Exception:
                pass

        return num_active

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
        # Check if queue is already full (max 10 items)
        if await self.is_queue_full(max_size=10):
            logger.info("Queue is full, skipping enqueue operation")
            return await self.get_queue_length()

        if data is None:
            raise ValueError("Data is required")

        # keep the historical data as is
        # use uuid7 so keys in redis are sorted by time
        hist_key = self._build_key(self._hist_key_prefix, uuid_utils.uuid7().__str__())
        try:
            logger.debug(f"Writing persistent data into {hist_key}")
            # place into persistent key
            str_data = json.dumps(jsonable_encoder(data)).encode(self._encoding)
            args = parse_cli_args()
            if args.env_name and args.env_name == "prod":
                # expire in 4 hours time
                await self.redis.set(
                    hist_key, str_data, ex=3600 * 4
                )  # pyright: ignore[reportUnknownMemberType]
            else:
                await self.redis.set(
                    hist_key, str_data
                )  # pyright: ignore[reportUnknownMemberType]

            queue_key = self._build_key(self._queue_key)
            logger.debug(f"Writing queue data into {queue_key}")
            # fuck it and push the data into the queue as well, instead of it being a reference to the persistent data
            # this also simplifies dequeuing logic
            num_items: int = await self.redis.rpush(queue_key, str_data)  # type: ignore

            # collect cids for each answer and log successful upload to DB
            ids: list[str] = [response["cid"] for response in data["responses"]]
            logger.success(f"Pushed Task {ids} to DB")
            return num_items
        except Exception as exc:
            logger.opt(exception=True).error(
                f"Error enqueuing data into key: {hist_key}, error: {exc}"
            )
            raise

    async def dequeue(self) -> str | None:
        """Dequeue an item from the specified queue key, assumes it is a queue and
        returns the value as as a string

        FOR TESTNET: added re-enqueuing of the item to push it back to the queue
        """
        current_key: str = self._build_key(self._queue_key)
        try:
            value_raw = await cast(
                Awaitable[str | bytes | list[Any] | None],
                self.redis.lpop(
                    current_key
                ),  # pyright: ignore[reportUnknownMemberType]
            )

            value: str | None = None
            if isinstance(value_raw, list):
                raise NotImplementedError("not implemented")
            elif isinstance(value_raw, bytes):
                value = value_raw.decode(self._encoding)

            # Re-enqueue the item to create a rotating queue
            if value is not None:
                # Convert value back to bytes if needed before re-enqueueing
                value_to_push = (
                    value.encode(self._encoding)
                    if isinstance(value, str)
                    else value_raw
                )
                await self.redis.rpush(current_key, value_to_push)
                logger.debug(
                    f"Re-enqueued item to create rotation in queue: {current_key}"
                )

            return value
        except Exception as exc:
            logger.opt(exception=True).error(
                f"Error dequeuing data from key: {current_key}, error: {exc}"
            )
            raise

    async def is_queue_full(self, max_size: int = 10) -> bool:
        """
        FOR TESTNET: maintain a queue of 10 items
        Check if the queue has reached the maximum size limit.

        Args:
            max_size: Maximum number of items allowed in the queue. Default is 10.

        Returns:
            bool: True if queue length is greater than or equal to max_size, False otherwise.
        """
        queue_length = await self.get_queue_length()
        return queue_length >= max_size
