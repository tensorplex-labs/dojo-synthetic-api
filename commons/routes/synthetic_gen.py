import asyncio
import json

from fastapi import APIRouter, BackgroundTasks
from loguru import logger
from pydantic import BaseModel

from commons.cache import RedisCache
from commons.prompt_builders import Language
from commons.synthetic import (
    ResponseStrategy,
    build_prompt_responses_pair,
)

synthetic_gen_router = APIRouter(prefix="/api")
cache = RedisCache()

TARGET_SIZE = 1
QUEUE_KEY = "synthetic:queue"


class SyntheticGenResponse(BaseModel):
    success: bool
    body: dict | None = None
    error: str | None = None


@synthetic_gen_router.get("/synthetic-gen")
async def generate_synthetic_data(background_tasks: BackgroundTasks):
    try:
        num_elems = await cache.get_queue_length()
        if num_elems:
            result = await generator.get_one()
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                result = {}
        else:
            language = Language.JAVASCRIPT
            result = await build_prompt_responses_pair(
                language, response_strategy=ResponseStrategy.AUGMENTATION_DETERIORIATE
            )

        background_tasks.add_task(generator.arun)

        return SyntheticGenResponse(success=True, body=result, error=None)
    except Exception as e:
        return SyntheticGenResponse(success=False, body={}, error=str(e))


class SyntheticGenerator:
    _instance = None
    _num_workers = 10
    # point it to the shared cache between the generator and the router
    todo = asyncio.Queue()
    semaphore = asyncio.Semaphore(TARGET_SIZE)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def run(self):
        asyncio.create_task(self.arun())

    async def arun(self):
        work_todo = await self.calc_work_todo()
        await self.on_found_work(work_todo)
        workers = [asyncio.create_task(self.worker()) for _ in range(self._num_workers)]
        await self.todo.join()
        logger.success("All tasks finished...")
        for w in workers:
            w.cancel()

    async def worker(self):
        while True:
            try:
                await self.process_one()
            except asyncio.CancelledError:
                return

    async def calc_work_todo(self):
        # num_keys = await cache.check_num_keys(REDIS_PREFIX)
        await cache.connect()
        num_keys = await cache.get_queue_length()
        num_data = max(TARGET_SIZE - num_keys, 0)
        return num_data

    async def process_one(self):
        await self.todo.get()
        try:
            async with self.semaphore:
                num_keys = await cache.get_queue_length()
                if num_keys < TARGET_SIZE:
                    language = Language.JAVASCRIPT
                    responses = await build_prompt_responses_pair(
                        language,
                        response_strategy=ResponseStrategy.AUGMENTATION_DETERIORIATE,
                    )
                    # responses = await build_2_prompt_responses_pairs()
                    # TODO test if implentation works
                    await cache.enqueue(responses)

        except Exception as exc:
            logger.opt(exception=True).error(f"ERROR: {exc}")
        finally:
            self.todo.task_done()

    async def on_found_work(self, num_data: int):
        if num_data <= 0:
            return
        for _ in range(num_data):
            await self.put_todo(1)

    async def put_todo(self, todo_data) -> None:
        await self.todo.put(todo_data)

    async def get_one(self):
        """Tries to get one item from the queue.
        Otherwise waits on any of the workers to finish."""
        return await cache.dequeue()


generator = SyntheticGenerator()
