import os
from typing import List, Optional, Dict
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
from tornado.escape import url_escape, json_encode
from tornado.websocket import websocket_connect
from tornado.httpclient import HTTPRequest
import aiohttp
from uuid import uuid4

load_dotenv()


class Config(BaseModel):
    ws_url: str = "ws://{host}".format(host=os.getenv("GATEWAY_HOST"))
    http_url: str = "http://{host}".format(host=os.getenv("GATEWAY_HOST"))


class PythonExecutor:
    def __init__(self, kernel_id: str, config: Config):
        self.kernel_id = kernel_id
        self.config = config

    async def _upgrade_request(self) -> HTTPRequest:
        url = "{http_url}/api/kernels/{kernel_id}/channels".format(
            http_url=self.config.http_url, kernel_id=url_escape(self.kernel_id)
        )
        request = HTTPRequest(url, method="GET")
        return request
    
    @staticmethod
    def __create_execute_request(msg_id, code):
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
    
    async def execute_code(self, code: str) -> List[str]:
        ws_req = await self._upgrade_request()
        conn = yield websocket_connect(ws_req)

        msg_body = await self.__create_execute_request(code, msg_id = uuid4().hex)
        
        while True:
            await conn.write_message(msg_body)
            msg = await conn.read_message()
            if msg is None: break


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
