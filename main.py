import asyncio
from contextlib import asynccontextmanager

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
from openai import AuthenticationError, PermissionDeniedError

load_dotenv()
install(show_locals=True)


@asynccontextmanager
async def _lifespan_context(app: FastAPI):  # noqa: ARG001 #pyright: ignore[reportUnusedParameter]
    # Start up tasks
    app.state.persona_dataset = load_persona_dataset()   
    # create workers to concurrently generate question-answer pairs; wrap worker.run in a task so it can be cancelled
    worker_task = asyncio.create_task(worker.run())
    # check that generation did not raise any fatal errors.
    worker_task.add_done_callback(_check_fatal_errors)
    logger.info("Performed startup tasks")
    
    yield
    
    # shutdown tasks
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

def _check_fatal_errors(task: asyncio.Task):
    """
    checks worker response for fatal exceptions. Shuts down server if fatal error is detected.
    """
    try:
        task.result()
    except (AuthenticationError, PermissionDeniedError) as e:
        asyncio.create_task(_fatal_shutdown(e))

async def _fatal_shutdown(e: Exception):
    logger.error(f"Shutting down FastAPI server due to fatal error: {e}")
    await worker.stop()
    await cache.close()
        
    # Get all running tasks except current
    tasks = [task for task in asyncio.all_tasks()
             if task is not asyncio.current_task()]

    # Cancel all tasks
    for task in tasks:
        task.cancel()
    
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

    try:
        # ctrl-c will already send keyboard interrupt to uvicorn/fastapi to handle
        await server.serve()
        logger.info("No longer serving FastAPI app...")
    finally:
        # Cancel all running tasks except the current one
        tasks = [
            task for task in asyncio.all_tasks() if task is not asyncio.current_task()
        ]

        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    logger.info("Exiting main function.")


if __name__ == "__main__":
    asyncio.run(main())
