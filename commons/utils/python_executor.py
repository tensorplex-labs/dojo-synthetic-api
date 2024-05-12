import os
import asyncio
import json
from datetime import datetime
from typing import List, Optional, Dict, Union, Literal, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx
from tornado.escape import url_escape, json_encode
from tornado.websocket import websocket_connect, WebSocketClientConnection
from tornado.httpclient import HTTPRequest
import aiohttp
from uuid import uuid4

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
    data : Dict[str, str]
    execution_count: int = 0
    metadata: Dict
    transient: Dict = {}

class StreamContent(BaseModel):
    name: str
    text: str
    
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
    content: Union[ExecutionStateContent, ExecutionRequestContent, StreamContent, ShellContent, CodeResult]
    channel : Literal["iopub", "shell"]
    
img_template = """
<!DOCTYPE html><html><head><title>Image</title></head><body><img src="data:image/png;base64, {img}" /></body></html> 
"""

text_template = """
<!DOCTYPE html><html><head><title>Text</title></head><body><p>{text}</p></body></html>
"""

class PythonExecutor:
    def __init__(self, kernel_id: str, config: Config):
        self.kernel_id = kernel_id
        self.config = config

    async def _upgrade_request(self) -> HTTPRequest:
        url = "{ws_url}/api/kernels/{kernel_id}/channels".format(
            ws_url=self.config.ws_url, kernel_id=url_escape(self.kernel_id)
        )
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
        
    async def install_packages(self, packages: List[str], conn : WebSocketClientConnection) -> None:
        packages_str = " ".join(packages)
        msg_body = await self.__create_execute_request(msg_id = uuid4().hex, code = f"!pip install {packages_str}")
        await self.handle_responses(msg_body, conn, timeout=40)
    
    async def execute_code(self, code: str, packages : List[str]) -> List[str]:
        ws_req = await self._upgrade_request()
        conn = await websocket_connect(ws_req)
        await self.install_packages(packages, conn)

        msg_body = await self.__create_execute_request(msg_id = uuid4().hex, code = code)
        
        return await self.handle_responses(msg_body, conn)
            
    async def handle_responses(self,msg_body : str, conn: WebSocketClientConnection, timeout : float = 5.0):
        await conn.write_message(msg_body)
        idle = False
        responses : List[Message] = []
        while True:
            try:
                msg = await asyncio.wait_for(conn.read_message(), timeout=timeout)
            except asyncio.TimeoutError:
                print("Timeout")
                break
            
            if msg:
                msg_model = await self.process_message(msg)
                if msg_model.msg_type == "status" and msg_model.content.execution_state == "idle":
                    idle = True
                    print("Idle")
                    continue
                    
                responses.append(msg_model)
                    
            if msg is None: # We timed out.  If post idle, its ok, else make mention of it
                if not idle:
                    print("Unexpected end")
                break
    
        return await self.convert_to_html(responses)
            
    @staticmethod
    async def convert_to_html(responses : List[Message]):
        htmls = []
        for response in responses:
            if response.msg_type == "stream":
                htmls.append(text_template.format(text = response.content.text))
            elif response.msg_type == "display_data":
                print("Display data")
                for key in response.content.data.keys():
                    if key == "text/plain":
                        htmls.append(text_template.format(text = response.content.data["text/plain"]))
                    elif key == "image/png": 
                        print("Image")
                        img = response.content.data["image/png"]
                        htmls.append(img_template.format(img = img))
                    elif key == "text/html":
                        htmls.append(response.content.data["text/html"])
        
        return htmls
            
    @staticmethod
    async def process_message(msg: Dict[str, Any]) -> Message:
        obj = json.loads(msg)
        try:
            msg = Message.model_validate(obj)
        except Exception as e:
            print(msg, e)
        print(msg)
        return msg
            
class GatewayClient:
    def __init__(self) -> None:
        self.config = Config()

    async def get_executor(
        self, env_vars: Optional[Dict[str, str]] = None
    ) -> PythonExecutor:
        request_body = {"name": "python"}
        if env_vars is not None:
            request_body["env"] = env_vars

        async with httpx.AsyncClient(base_url=self.config.http_url) as client:
            response = await client.request("POST", "/api/kernels", json=request_body)
            kernel_info = response.json()

        kernel_id = kernel_info["id"]

        return PythonExecutor(kernel_id, self.config)


if __name__ == "__main__":
    client = GatewayClient()
    executor = asyncio.run(client.get_executor())
    
    with open("plot_test.py", "r") as file:
        code = file.read()
        
    packages = ['plotly', 'numpy', 'matplotlib', 'mpld3']
    htmls = asyncio.run(executor.execute_code(code, packages))
    print(htmls)