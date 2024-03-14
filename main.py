import asyncio
from contextlib import asynccontextmanager

import bittensor as bt
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from commons.discovery import DiscoveryService
from commons.patch_logging import apply_patch

apply_patch()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # BEFORE YIELD == ON STARTUP
    bt.logging.info("Performing startup tasks...")
    yield
    # AFTER YIELD == ON SHUTDOWN
    bt.logging.info("Performing shutdown tasks...")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def main():
    config = uvicorn.Config(
        app=app,
        # TODO @dev change port
        host="0.0.0.0",
        port="6942",
        workers=4,
        log_level="info",
        reload=False,
    )
    server = uvicorn.Server(config)
    discovery_service = DiscoveryService()
    discovery_task = asyncio.create_task(discovery_service.run())

    await server.serve()

    discovery_task.cancel()
    try:
        await discovery_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
