from typing import Any, List

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------- #
#                          REWOO PLAN & SOLVE RELATED                          #
# ---------------------------------------------------------------------------- #


"""
descriptions matter a for these types here, because they will actually get sent over
to the LLM when using instructor
"""


class Tool(BaseModel):
    """
    Represents a tool used in a step.
    """

    name: str = Field(
        ...,
        description="The name of the tool used in the step, e.g. SearchWeb, UseLLM, ExecuteCode",
    )
    purpose: str = Field(..., description="Purpose of the tool call")


class Execution(BaseModel):
    """
    Represents an execution output from a step.
    """

    identifier: str = Field(
        ...,
        description="A unique identifier for the execution output (e.g., '#E1').",
    )
    description: str = Field(
        ..., description="Detailed explanation of the execution output."
    )


class InputReference(BaseModel):
    """
    Represents an input reference for a step.
    """

    identifier: str = Field(
        ..., description="A unique identifier for the input reference (e.g., '#I1')."
    )
    refers_to: str = Field(
        ...,
        description="The identifier of the execution output that this input references (e.g., '#E1').",
    )
    description: str = Field(
        ..., description="Detailed explanation of the input reference."
    )


class Step(BaseModel):
    """
    Represents a single step in the plan.
    """

    step_id: int = Field(..., description="The unique idenfier of the step.")
    title: str = Field(..., description="The title of the step.")
    purpose: str = Field(..., description="The purpose of the step.")
    tool: Tool = Field(..., description="The tool used in this step.")
    # can consider these dependencies
    inputs: list[InputReference] | None = Field(
        None,
        description="A list of input references from previous steps that this step depends on.",
    )
    output: Execution | None = Field(
        None, description="The execution output produced by this step."
    )


class Plan(BaseModel):
    """
    Represents the entire plan consisting of multiple steps.
    """

    steps: List[Step] = Field(..., description="A list of all steps in the plan.")


class ReWOOState(BaseModel):
    task: str
    plan: Plan
    # store the `output` identifiers here, for easy lookups
    results: dict[str, Any]


# ---------------------------------------------------------------------------- #
#                                 TOOLS RELATED                                #
# ---------------------------------------------------------------------------- #


class DuckduckgoSearchResult(BaseModel):
    title: str
    snippet: str
    url: str
    content: str | None = None


# ---------------------------------------------------------------------------- #
#                             TOOLS & REWOO RELATED                            #
# ---------------------------------------------------------------------------- #


class HtmlCode(BaseModel):
    html_code: str = Field(..., description="The HTML code solution")


class CodeIteration(BaseModel):
    code: str
    error: str


class CodeIterationStates(BaseModel):
    iterations: list[CodeIteration] = []
    current_iteration_num: int = 0

    def add_iteration(self, iteration: CodeIteration):
        self.iterations.append(iteration)
        self.current_iteration_num += 1

    def set_initial_state(self, iteration: CodeIteration):
        self.iterations.append(iteration)

    @property
    def latest_iteration(self) -> CodeIteration | None:
        return self.iterations[-1] if self.iterations else None
