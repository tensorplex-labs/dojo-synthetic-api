from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from commons.dataset.synthetic_test import CodingQuestion, build_prompt_responses_pair

synthetic_gen_router = APIRouter(prefix="/api")


class SyntheticGenRequest(BaseModel):
    code: str = Field(..., example="coding example")


class SyntheticGenResponse(BaseModel):
    success: bool
    body: Optional[dict] = None
    error: Optional[str] = None


@synthetic_gen_router.get("/synthetic-gen", response_model=SyntheticGenResponse)
async def execute_python_code():
    try:
        res = await build_prompt_responses_pair()
        return {
            "success": True,
            "body": res,
            "error": None,
        }
    except Exception as e:
        return {"success": False, "body": None, "error": str(e)}
