"""
human_feedback.py is the route for receiving human feedback requests from dojo.

It receives and returns relevant human feedback data to dojo.

2 endpoints:
1 to recieve request and start generating response
1 to return the resposne back to dojo which will poll redis for completed tasks
"""

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
        For the vali to request the generation of human feedback.
        API will then store completed human feedback in redis.
    Input:
        HumanFeedbackRequest
    Output:
        acknowledgement of receipt
    """
    logger.info(f"Received human feedback request: {human_feedback_request}")
    _ = await generate_human_feedback(human_feedback_request)

    response = {
        "message": "Human feedback request received",
        "human_feedback_request": human_feedback_request.model_dump(),
    }
    return JSONResponse(status_code=200, content=response)


# @human_feedback_router.get("/human-feedback")
# async def return_human_feedback(
#     human_feedback_request: HumanFeedbackRequest,
# ) -> HumanFeedbackResponse:
#     """
#     GET /human-feedback:
#         For the validator to retrieve the hf_task from redis
#     Input:
#         3 x miner_response_id
#         1 x validator_task_id?
#     Output:
#         the HumanFeedbackResponse that corresponds to the input
#     """
#     return HumanFeedbackResponse(
#         base_prompt="",
#         base_code="",
#         human_feedback_tasks=[],
#     )
