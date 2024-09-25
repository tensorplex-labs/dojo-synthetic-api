import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from rich.traceback import install

from commons.routes.health import health_router
from commons.routes.synthetic_gen import cache, generator, synthetic_gen_router

install(show_locals=True)

logger.remove()
logger.add(sys.stderr, level="DEBUG", backtrace=True, diagnose=True)


@asynccontextmanager
async def startup_lifespan(app: FastAPI):  # noqa: ARG001
    await generator.arun()
    await cache.connect()
    yield
    await cache.close()


app = FastAPI(lifespan=startup_lifespan)


# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Include the code_gen router
app.include_router(health_router)
app.include_router(synthetic_gen_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
