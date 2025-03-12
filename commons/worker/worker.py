import asyncio
from typing import Any, Awaitable, Callable

from loguru import logger
from openai import AuthenticationError, PermissionDeniedError

from commons.cache import RedisCache
from commons.config import get_settings


class Worker:
    """This class exists because each QA pair takes a long time to generate, so
    upon startup of the app, we want to ensure that we have a buffer of QA pairs
    ready to be consumed by callers of the API endpoint.

    The workers will also constantly replenish the queue with new QA pairs.

    Algorithm:
    1. calculate number of QA pairs needed i.e. buffer size - current queue length - number of workers currently working (in redis)
    2. for each unit of work needed, update the number of workers currently working (in redis) and spawn a new worker
    3. each worker will try to generate a QA pair and put it in the shared buffer (redis)
    4. the router will consume the QA pairs from the shared buffer (redis)
    5. the router will return the QA pairs to the caller
    6. repeat steps 1-5
    """

    _instance: "Worker | None" = None
    # we want to ensure that the number of workers is in sync with number of uvicorn workers
    _num_workers = get_settings().uvicorn.num_workers
    _buffer_size = get_settings().generation.buffer_size
    # callable function to allow other functions to be passed in
    _do_work: Callable[..., Awaitable[Any]]
    _running_workers: list = []

    def __new__(cls, do_work: Callable) -> "Worker":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(do_work)
        return cls._instance

    def __init__(self, do_work: Callable):
        self._do_work = do_work

    async def run(self):
        # ensure to reset number of workers active to 0 upon startup
        cache = RedisCache()
        await cache.update_num_workers_active(-self._num_workers)

        workers: list[asyncio.Task[None]] = [
            asyncio.create_task(self.worker()) for _ in range(self._num_workers)
        ]
        self._running_workers = workers
        await asyncio.gather(*workers)

    async def worker(self):
        """Continuously check for work to do, and do it.
        Allows for worker to be cancelled using asyncio.Task.cancel()
        """
        try:
            while True:
                try:
                    work_todo = await self.calc_work_todo()
                    if work_todo > 0:
                        await self.advertise_and_do_work()
                    else:
                        await asyncio.sleep(3)
                except asyncio.CancelledError:
                    logger.opt().info("Running worker was cancelled")
                    break
                except (AuthenticationError, PermissionDeniedError):
                    raise
                except Exception as exc:
                    logger.opt(exception=True).error(f"ERROR: {exc}")
        finally:
            logger.info("Worker is shutting down")

    async def stop(self):
        for worker in self._running_workers:
            worker.cancel()

    async def calc_work_todo(self) -> int:
        """Calculate number of units of work needed to be done, based on
        the desired buffer size, current buffer size, and number of active
        workers.
        """
        cache = RedisCache()
        current_buffer_size = await cache.get_queue_length()
        num_active_workers = await cache.get_num_workers_active()
        num_work_todo = max(
            self._buffer_size - current_buffer_size - num_active_workers, 0
        )
        return num_work_todo

    async def advertise_and_do_work(self):
        """Tell other workers that I (current worker) am picking up some work"""
        cache = RedisCache()
        await cache.update_num_workers_active(1)

        # Find the parent task in self._running_workers
        worker_id = next(
            (
                i
                for i, task in enumerate(self._running_workers)
                if task == asyncio.current_task()
            ),
            None,
        )

        try:
            logger.debug(f"Worker-{worker_id} doing work")
            value = await self._do_work()
            await cache.enqueue(value)
        except (AuthenticationError, PermissionDeniedError):
            raise
        except Exception as exc:
            logger.opt(exception=True).error(
                f"Error processing one unit of work: {exc}"
            )
        finally:
            await cache.update_num_workers_active(-1)
