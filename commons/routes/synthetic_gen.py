import asyncio
import functools
import json

from fastapi import APIRouter
from pydantic import BaseModel

from commons.cache import RedisCache
from commons.synthetic import (
    build_prompt_responses_pair,
)
from commons.worker import WorkerManager

synthetic_gen_router = APIRouter(prefix="/api")
cache = RedisCache()
worker = WorkerManager(
    do_work=functools.partial(
        build_prompt_responses_pair,
    )
)


class SyntheticGenResponse(BaseModel):
    success: bool
    body: dict | None = None
    error: str | None = None


@synthetic_gen_router.get("/synthetic-gen")
async def generate_synthetic_data():
    try:
        num_elems = await cache.get_queue_length()
        if num_elems == 0:
            for _ in range(100):
                await asyncio.sleep(3)
                num_elems = await cache.get_queue_length()
                if num_elems > 0:
                    break
            else:
                raise Exception("Cache population timeout after 300 seconds")

        qa_pair = await cache.dequeue()
        if qa_pair is None:
            raise Exception("Failed to get QA pair from cache")
        try:
            result = json.loads(qa_pair)
        except json.JSONDecodeError:
            result = {}

        return SyntheticGenResponse(success=True, body=result, error=None)
    except Exception as e:
        return SyntheticGenResponse(success=False, body={}, error=str(e))
