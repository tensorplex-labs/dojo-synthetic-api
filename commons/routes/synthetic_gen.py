import asyncio
import json
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger
from commons.cache import RedisCache
from commons.dataset.synthetic import (
    build_2_prompt_responses_pairs,
    build_prompt_responses_pair,
)

synthetic_gen_router = APIRouter(prefix="/api")
cache = RedisCache()

TARGET_SIZE = 6
QUEUE_KEY = "synthetic:queue"


class SyntheticGenResponse(BaseModel):
    success: bool
    body: Optional[List[dict]] = None
    error: Optional[str] = None


@synthetic_gen_router.get("/synthetic-gen", response_model=SyntheticGenResponse)
async def execute_python_code(background_tasks: BackgroundTasks):
    try:
        num_elems = await cache.redis.llen(QUEUE_KEY)
        if num_elems:
            result = await generator.get_one()
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                result = {}
        else:
            result = await build_2_prompt_responses_pairs()

        background_tasks.add_task(generator.arun)

        return {
            "success": True,
            "body": result,
            "error": None,
        }
    except Exception as e:
        return {"success": False, "body": [], "error": str(e)}


class SyntheticGenerator:
    _instance = None
    _num_workers = 10
    # point it to the shared cache between the generator and the router
    done = cache
    todo = asyncio.Queue()
    semaphore = asyncio.Semaphore(TARGET_SIZE)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SyntheticGenerator, cls).__new__(cls)
        return cls._instance

    def run(self):
        asyncio.create_task(self.arun())

    async def arun(self):
        work_todo = await self.calc_work_todo()
        await self.on_found_work(work_todo)
        async with asyncio.TaskGroup() as tg:
            workers = [tg.create_task(self.worker()) for _ in range(self._num_workers)]
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
        num_keys = await cache.redis.llen(QUEUE_KEY)
        num_data = max(TARGET_SIZE - num_keys, 0)
        return num_data

    async def process_one(self):
        await self.todo.get()
        try:
            async with self.semaphore:
                num_keys = await cache.redis.llen(QUEUE_KEY)
                if num_keys < TARGET_SIZE:
                    # TODO restore once done with testing agent
                    # response = await build_prompt_responses_pair()
                    responses = await build_2_prompt_responses_pairs()
                    await cache.redis.rpush(QUEUE_KEY, json.dumps(responses))
        except Exception as exc:
            logger.error(f"ERROR: {exc}")
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
        """Tries to get one item from the done queue.
        Otherwise waits on any of the workers to finish."""
        return await self.done.redis.lpop(QUEUE_KEY)


generator = SyntheticGenerator()
