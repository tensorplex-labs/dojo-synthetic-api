"""
human_feedback.py is the route for receiving human feedback requests from dojo.

It receives and returns relevant human feedback data to dojo.

2 endpoints:
1 to recieve request and start generating response
1 to return the resposne back to dojo which will poll redis for completed tasks
"""

import uuid
from asyncio import create_task, sleep

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from loguru import logger

from commons.human_feedback.human_feedback import generate_human_feedback
from commons.human_feedback.types import HumanFeedbackRequest

human_feedback_router = APIRouter(prefix="/api")


@human_feedback_router.post("/human-feedback")
async def request_human_feedback(
    human_feedback_request: HumanFeedbackRequest,
) -> JSONResponse:
    """
    POST /human-feedback:
        Dojo will POST to /human-feedback to request the generation of human feedback tasks
        a unique hf_id is created and returned to the validator.
        Dojo will use this id to retrieve the human feedback task from redis once its completed.
    Input:
        HumanFeedbackRequest obj containing base prompt, base code and miner feedbacks.
    Output:
        JSONResponse containing hf_id: a unique id for this human feedback request.
    """
    # @dev this is a stupid hack to silence ruff warning that this async function doesnt use await / async features
    #      however - this function needs to be async to work correctly.
    await sleep(0)
    miner_response_ids = [
        miner_feedback.miner_response_id
        for miner_feedback in human_feedback_request.miner_feedbacks
    ]
    logger.info(
        f"Received human feedback request for miner_response_ids: {miner_response_ids}"
    )
    hf_id = str(uuid.uuid4())
    response = {
        "message": f"Human feedback request created with id: {hf_id}",
        "human_feedback_request": human_feedback_request.model_dump(),
        "human_feedback_id": hf_id,
    }
    create_task(generate_human_feedback(human_feedback_request, hf_id))

    return JSONResponse(status_code=200, content=response)
