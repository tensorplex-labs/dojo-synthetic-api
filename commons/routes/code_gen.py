import asyncio
import os
from typing import Optional

from aiofiles.os import remove as aio_remove
from commons.utils.aws_s3_helper import S3Helper
from commons.utils.sandbox import execute_code_sandboxed
from fastapi import APIRouter
from pydantic import BaseModel, Field

code_gen_router = APIRouter(prefix="/api")


class PythonCodeGenRequest(BaseModel):
    code: str = Field(..., example="coding example")


class PythonCodeGenResponse(BaseModel):
    success: bool
    body: Optional[dict] = None
    error: Optional[str] = None


@code_gen_router.post("/codegen-python", response_model=PythonCodeGenResponse)
async def execute_python_code(request: PythonCodeGenRequest):
    file_path = None
    unique_file_name = None

    try:
        file_path, unique_file_name = await execute_code_sandboxed(request.code)
        unique_file_name = f"code-gen/python/{unique_file_name}"

        if await asyncio.get_event_loop().run_in_executor(
            None, os.path.exists, file_path
        ):
            s3_helper = S3Helper()
            await s3_helper.upload_file_to_s3(file_path, unique_file_name)
            s3_url = await s3_helper.get_s3_file_url(unique_file_name)
            await aio_remove(file_path)
            return {
                "success": True,
                "body": {"url_to_file": s3_url},
                "error": None,
            }
        else:
            return {
                "success": False,
                "body": None,
                "error": "Failed to generate HTML file.",
            }
    except Exception as e:
        if await asyncio.get_event_loop().run_in_executor(
            None, os.path.exists, file_path
        ):
            await aio_remove(file_path)
        return {"success": False, "body": None, "error": str(e)}
