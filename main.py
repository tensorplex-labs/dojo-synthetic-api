import asyncio
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from rich.traceback import install

from commons.config import get_settings, parse_cli_args
from commons.dataset.personas import load_persona_dataset
from commons.routes.health import health_router
from commons.routes.synthetic_gen import cache, synthetic_gen_router, worker

load_dotenv()
install(show_locals=True)


@asynccontextmanager
async def _lifespan_context(app: FastAPI):  # noqa: ARG001 #pyright: ignore[reportUnusedParameter]
    # Load persona dataset
    # persona_dataset = load_persona_dataset()
    app.state.persona_dataset = load_persona_dataset()
    logger.info("Performed startup tasks")
    # wrap worker.run in a task so it can be cancelled
    asyncio.create_task(worker.run())
    yield
    await worker.stop()
    await cache.close()
    logger.info("Performed shutdown tasks")


app = FastAPI(lifespan=_lifespan_context)
app.router.lifespan_context = _lifespan_context


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


async def main():
    parse_cli_args()
    uvicorn_config = get_settings().uvicorn
    config = uvicorn.Config(
        app=app,
        host=uvicorn_config.host,
        port=uvicorn_config.port,
        workers=uvicorn_config.num_workers,
        log_level=uvicorn_config.log_level,
        reload=False,
    )
    logger.info(f"Using uvicorn config: {config.__dict__}")
    server = uvicorn.Server(config)
    # create any background tasks here
    running_tasks: list[asyncio.Task[Any]] = []

    await server.serve()

    for task in running_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info(f"Cancelled task {task.get_name()}")
        except Exception as e:
            logger.error(f"Task {task.get_name()} raised an exception: {e}")
            pass

    logger.info("Exiting main function.")


if __name__ == "__main__":
    asyncio.run(main())
