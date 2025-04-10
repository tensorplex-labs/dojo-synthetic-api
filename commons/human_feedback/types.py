"""
human_feedback/types.py contains types used for human feedback generation.
"""

from typing import List

from pydantic import BaseModel

from commons.synthetic import CodeAnswer


class MinerFeedback(BaseModel):
    hotkey: str
    miner_response_id: str
    feedback: str


class HumanFeedbackTask(BaseModel):
    miner_hotkey: str
    feedback: str
    generated_code: CodeAnswer


# expected input from dojo
class HumanFeedbackRequest(BaseModel):
    base_prompt: str
    base_code: str
    miner_feedbacks: List[MinerFeedback]


# expected response to send to dojo
# @TODO: verify type of base_code
class HumanFeedbackResponse(BaseModel):
    base_prompt: str
    base_code: str
    human_feedback_tasks: List[HumanFeedbackTask]
