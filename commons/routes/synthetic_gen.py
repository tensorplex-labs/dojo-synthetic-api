from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from commons.dataset.synthetic import build_prompt_responses_pair

synthetic_gen_router = APIRouter(prefix="/api")


class SyntheticGenResponse(BaseModel):
    success: bool
    body: Optional[dict] = None
    error: Optional[str] = None


@synthetic_gen_router.get("/synthetic-gen", response_model=SyntheticGenResponse)
async def execute_python_code():
    try:
        result = await build_prompt_responses_pair()
        return {
            "success": True,
            "body": result,
            "error": None,
        }
    except Exception as e:
        return {"success": False, "body": None, "error": str(e)}
