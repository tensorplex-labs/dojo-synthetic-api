import os
import sys
import uuid
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

sys.path.append("./")
from commons.utils.aws_s3_helper import S3Helper


code_gen_router = APIRouter(prefix="/api")


class PythonCodeGenRequest(BaseModel):
    code: str = Field(..., example="coding example")


class PythonCodeGenResponse(BaseModel):
    success: bool
    body: Optional[dict] = None
    error: Optional[str] = None


@code_gen_router.post("/codegen-python", response_model=PythonCodeGenResponse)
async def execute_python_code(request: PythonCodeGenRequest):
    output_dir = "./temp/data"
    os.makedirs(output_dir, exist_ok=True)
    unique_file_name = f"{uuid.uuid4()}.html"
    file_path = os.path.join(output_dir, unique_file_name)

    try:
        modified_code = request.code.replace(
            "output_file(filename=output_file,", f"output_file(filename='{file_path}',"
        )
        exec(modified_code, globals())

        if os.path.exists(file_path):
            print(f"File {file_path} exists.")
            s3_helper = S3Helper()
            await s3_helper.upload_file_to_s3(file_path, unique_file_name)
            os.remove(file_path)
            return {
                "success": True,
                "body": {"file_name": unique_file_name},
                "error": None,
            }
        else:
            return {
                "success": False,
                "body": None,
                "error": "Failed to generate HTML file.",
            }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"success": False, "body": None, "error": str(e)}
