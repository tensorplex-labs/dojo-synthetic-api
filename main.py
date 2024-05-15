import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Assuming code_gen is a FastAPI router imported from your project's module
from commons.routes.code_gen import code_gen_router
from commons.routes.synthetic_gen import synthetic_gen_router, cache, replenish_cache

import time
from ipaddress import ip_address, ip_network

import httpx
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

MAX_CONTENT_LENGTH = 1 * 1024 * 1024


class IPFilterMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure that only requests from AWS Servers are allowed."""

    _aws_ips_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"
    _allowed_ip_ranges = []
    _last_checked: float = 0
    _allowed_networks = []

    @classmethod
    async def _get_allowed_networks(cls):
        return [ip_network(ip_range) for ip_range in await cls._get_allowed_ip_ranges()]

    # TODO
    # @classmethod
    # async def _get_allowed_ip_ranges(cls):
    #     if (time.time() - cls._last_checked) < 300:
    #         return cls._allowed_ip_ranges

    #     async with httpx.AsyncClient() as client:
    #         start_time = time.time()
    #         response = await client.get(cls._aws_ips_url)
    #         cls._last_checked = time.time()
    #         data = response.json()
    #         cls._allowed_ip_ranges = [
    #             ip_range["ip_prefix"]
    #             for ip_range in data["prefixes"]
    #             if ip_range["region"] in [US_EAST_REGION]
    #         ]
    #     return cls._allowed_ip_ranges

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        client_ip = ip_address(request.client.host)
        allowed_networks = [
            ip_network(ip_range) for ip_range in await self._get_allowed_networks()
        ]
        for network in allowed_networks:
            if client_ip in network:
                response = await call_next(request)
                return response
        return Response("Forbidden", status_code=403)


@asynccontextmanager
async def startup_lifespan(app: FastAPI):
    await replenish_cache()
    yield


app = FastAPI(lifespan=startup_lifespan)


# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Include the code_gen router
app.include_router(code_gen_router)
app.include_router(synthetic_gen_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
