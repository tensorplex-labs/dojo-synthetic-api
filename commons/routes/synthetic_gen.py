import asyncio
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from commons.dataset.synthetic import build_prompt_responses_pair

synthetic_gen_router = APIRouter(prefix="/api")
cache = asyncio.Queue(maxsize=10)


class SyntheticGenResponse(BaseModel):
    success: bool
    body: Optional[dict] = None
    error: Optional[str] = None


@synthetic_gen_router.get("/synthetic-gen", response_model=SyntheticGenResponse)
async def execute_python_code(background_tasks: BackgroundTasks):
    try:
        if cache.empty():
            await replenish_cache()
        result = await cache.get()
        background_tasks.add_task(replenish_cache)

        return {
            "success": True,
            "body": result,
            "error": None,
        }
    except Exception as e:
        return {"success": False, "body": None, "error": str(e)}


async def replenish_cache():
    while cache.qsize() < cache.maxsize:
        try:
            result = await build_prompt_responses_pair()
            await cache.put(result)
        except Exception as e:
            print(f"Error replenishing cache: {e}")
