import asyncio
import json
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from loguru import logger
from commons.cache import RedisCache
from commons.dataset.synthetic import build_prompt_responses_pair

synthetic_gen_router = APIRouter(prefix="/api")
cache = RedisCache()

TARGET_SIZE = 6
QUEUE_KEY = "synthetic:queue"


class SyntheticGenResponse(BaseModel):
    success: bool
    body: Optional[dict] = None
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
            result = await build_prompt_responses_pair()

        background_tasks.add_task(generator.arun)

        return {
            "success": True,
            "body": result,
            "error": None,
        }
    except Exception as e:
        return {"success": False, "body": None, "error": str(e)}


async def replenish_cache():
    # while cache.qsize() < cache.maxsize:
    while await cache.redis.llen(QUEUE_KEY) < TARGET_SIZE:
        try:
            result = await build_prompt_responses_pair()
            if not result:
                continue
            # unique_id = await cache.redis.incr(COUNTER_KEY)
            # await cache.redis.set(f"{REDIS_PREFIX}:{unique_id}", json.dumps(result))
            await cache.redis.rpush(QUEUE_KEY, json.dumps(result))
        except Exception as e:
            print(f"Error replenishing cache: {e}")


class SyntheticGenerator:
    _instance = None
    _num_workers = 10
    # point it to the shared cache between the generator and the router
    done = cache
    todo = asyncio.Queue()

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
            response = await build_prompt_responses_pair()
            if response:
                # unique_id = await cache.redis.incr(COUNTER_KEY)
                # await cache.redis.set(
                #     f"{REDIS_PREFIX}:{unique_id}", json.dumps(response)
                # )
                await cache.redis.rpush(QUEUE_KEY, json.dumps(response))
            else:
                # we need to get 1 more response bruh
                self.on_found_work(1)

        except Exception as exc:
            # retry handling here...
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
