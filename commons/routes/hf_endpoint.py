"""
human_feedback.py is the route for receiving human feedback requests from dojo.

It receives and returns relevant human feedback data to dojo.
"""

from fastapi import APIRouter
from loguru import logger

from commons.human_feedback.human_feedback import generate_human_feedback
from commons.human_feedback.types import HumanFeedbackRequest, HumanFeedbackResponse

human_feedback_router = APIRouter(prefix="/api")


@human_feedback_router.get("/human-feedback")
async def get_human_feedback(
    human_feedback_request: HumanFeedbackRequest,
) -> HumanFeedbackResponse:
    logger.info(f"Received human feedback request: {human_feedback_request}")
    response = await generate_human_feedback(human_feedback_request)

    return response
