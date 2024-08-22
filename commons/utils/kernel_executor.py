import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Iterable, List, Literal, cast
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel
from tornado.escape import json_encode, url_escape
from tornado.httpclient import HTTPRequest
from tornado.websocket import WebSocketClientConnection, websocket_connect

from commons.utils.utils import get_packages

load_dotenv()


class Config(BaseModel):
    ws_url: str = "ws://{host}".format(host=os.getenv("GATEWAY_HOST"))
    http_url: str = "http://{host}".format(host=os.getenv("GATEWAY_HOST"))


class Header(BaseModel):
    msg_id: str
    msg_type: str
    username: str
    session: str
    date: datetime
    version: str


class ExecutionStateContent(BaseModel):
    execution_state: str


class ExecutionRequestContent(BaseModel):
    code: str
    execution_count: int


class CodeResult(BaseModel):
    data: Dict
    execution_count: int = 0
    metadata: Dict
    transient: Dict = {}


class StreamContent(BaseModel):
    name: str
    text: str


class ErrorContent(BaseModel):
    ename: str
    evalue: str
    traceback: List[str]


class CommContent(BaseModel):
    comm_id: str
    data: Dict
    target_name: str
    target_module: str | None = None


class CommMsg(BaseModel):
    data: Dict
    comm_id: str


class ShellContent(BaseModel):
    status: str
    execution_count: int
    user_expressions: Dict
    payload: List


class Message(BaseModel):
    header: Header
    msg_id: str
    msg_type: str
    parent_header: Dict[str, str]
    metadata: Dict
    content: (
        ExecutionStateContent
        | ExecutionRequestContent
        | StreamContent
        | ShellContent
        | CodeResult
        | ErrorContent
        | CommContent
        | CommMsg
    )
    channel: Literal["iopub", "shell"]


img_template = """
<img src="data:image/png;base64, {img}" />
"""

base_template = """
<!DOCTYPE html><html><head><title>Output</title></head><body>{content}</body></html>
"""

text_template = """
<p>{text}</p>
"""


class PythonExecutor:
    def __init__(self, kernel_id: str, config: Config):
        self.kernel_id = kernel_id
        self.config = config

    async def _upgrade_request(self) -> HTTPRequest:
        url = f"{self.config.ws_url}/api/kernels/{url_escape(self.kernel_id)}/channels"
        request = HTTPRequest(url, method="GET")
        return request

    @staticmethod
    async def __create_execute_request(msg_id, code):
        return json_encode(
            {
                "header": {
                    "username": "",
                    "version": "5.0",
                    "session": "",
                    "msg_id": msg_id,
                    "msg_type": "execute_request",
                },
                "parent_header": {},
                "channel": "shell",
                "content": {
                    "code": "".join(code),
                    "silent": False,
                    "store_history": False,
                    "user_expressions": {},
                    "allow_stdin": False,
                },
                "metadata": {},
                "buffers": {},
            }
        )

    async def install_packages(
        self, packages: Iterable[str], conn: WebSocketClientConnection
    ) -> None:
        default_packages = ["numpy", "pandas", "matplotlib", "scipy", "plotly"]
        packages = set(packages).union(default_packages)
        packages_str = " ".join(packages)
        if packages_str:
            msg_body = await self.__create_execute_request(
                msg_id=uuid4().hex, code=f"!pip install {packages_str}"
            )
            await self.handle_responses(msg_body, conn, timeout=40, execute_only=True)

    async def execute_code(self, code: str):
        print(code)
        ws_req = await self._upgrade_request()
        conn = await websocket_connect(ws_req)
        try:
            await self.install_packages(get_packages(code), conn)
        except SyntaxError as e:
            output = base_template.format(content=text_template.format(text=str(e)))
            return output.replace("\\n", "\n").replace("\\t", "\t")

        msg_body = await self.__create_execute_request(msg_id=uuid4().hex, code=code)
        output = await self.handle_responses(msg_body, conn)
        conn.close()
        print("closing connection")

        if output is None:
            raise Exception("No output")

        return output.replace("\\n", "\n").replace("\\t", "\t")

    async def handle_responses(
        self,
        msg_body: str,
        conn: WebSocketClientConnection,
        timeout: float = 5.0,
        execute_only: bool = False,
    ) -> str | None:
        await conn.write_message(msg_body)
        idle = False
        responses: List[Message] = []
        while True:
            try:
                msg = await asyncio.wait_for(conn.read_message(), timeout=timeout)
            except asyncio.TimeoutError:
                print("Timeout")
                break

            if msg:
                msg_model = await self.process_message(cast(str, msg))
                if (
                    msg_model.msg_type == "status"
                    and cast(ExecutionStateContent, msg_model.content).execution_state
                    == "idle"
                ):
                    idle = True
                    print("Idle")
                    continue

                responses.append(msg_model)

            if (
                msg is None
            ):  # We timed out.  If post idle, its ok, else make mention of it
                if not idle:
                    print("Unexpected end")
                break

        if not execute_only:
            return await self.convert_to_html(responses)

    @staticmethod
    async def convert_to_html(responses: List[Message]) -> str:
        with open("output.json", "w") as file:
            output = []
            for response in responses:
                dict_response = vars(response.content)
                dict_response["type"] = type(response.content).__name__
                output.append(dict_response)
            json.dump(output, file)

        for response in responses:
            # if response.msg_type == "stream":
            #     assert isinstance(response.content, StreamContent)
            #     print("is instance", isinstance(response.content, StreamContent), response)
            #     return base_template.format(text_template.format(text = response.content.text))
            print(vars(response).keys())
            print(type(response.content))
            # print(response.content.model_dump())
            if response.msg_type == "display_data":
                assert isinstance(response.content, CodeResult)

                filetypes = response.content.data.keys()
                if "text/html" in filetypes:
                    print("html")
                    print(vars(response).keys())
                    return response.content.data["text/html"]
                elif "image/png" in filetypes:
                    print("png")
                    print(vars(response).keys())
                    img = response.content.data["image/png"]
                    print(img)
                    return base_template.format(content=img_template.format(img=img))
                elif "text/plain" in filetypes:
                    print("text")
                    print(vars(response).keys())
                    text = response.content.data["text/plain"]
                    return base_template.format(content=text_template.format(text=text))
                else:
                    raise Exception("Unknown file type")
            elif response.msg_type == "error":
                assert isinstance(response.content, ErrorContent)
                print(vars(response).keys())
                return base_template.format(
                    content=text_template.format(text=response.content.evalue)
                )

        return base_template.format(content="")

    @staticmethod
    async def process_message(msg: str) -> Message:
        obj = json.loads(msg)
        try:
            msg_obj = Message.model_validate(obj)
        except Exception as e:
            print(msg)
            raise e

        return msg_obj


class GatewayClient:
    def __init__(self) -> None:
        self.config = Config()

    async def get_executor(
        self, env_vars: Dict[str, str] | None = None
    ) -> PythonExecutor:
        request_body: Dict[str, str | Dict[str, str]] = {"name": "python"}
        if env_vars is not None:
            request_body["env"] = env_vars

        async with httpx.AsyncClient(
            base_url=self.config.http_url, timeout=50
        ) as client:
            try:
                response = await client.request(
                    "POST", "/api/kernels", json=request_body
                )
            except httpx.ConnectError as err:
                raise Exception("Is docker running?") from err
            kernel_info = response.json()

        try:
            kernel_id = kernel_info["id"]
        except KeyError as err:
            print(kernel_info)
            raise Exception("Kernel ID not found in response") from err

        return PythonExecutor(kernel_id, self.config)


if __name__ == "__main__":
    client = GatewayClient()
    env_vars = {"KERNEL_USERNAME": "jovyan"}
    executor = asyncio.run(client.get_executor())

    with open("plot_test.py") as file:
        code = file.read()

    htmls = asyncio.run(executor.execute_code(code))
    # print(htmls)
