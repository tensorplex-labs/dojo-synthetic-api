"""
Implementation of plan & solve approach using ReWOO, instead of suffering from abstraction hell that is LangChain.
This exists to decouple our implementation of the code iterator from the main function in `iterator.py`
"""

import asyncio
import datetime
import functools
import re
import textwrap
from typing import Callable, Iterable

import instructor
from dotenv import load_dotenv
from langfuse.decorators import langfuse_context, observe
from loguru import logger
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from commons.code_iterator.tools import call_llm, fix_code, web_search_and_format
from commons.code_iterator.types import HtmlCode, Plan, ReWOOState, Step, Tool
from commons.config import get_settings
from commons.llm import Provider, _get_llm_api_kwargs, get_llm_api_client
from commons.utils import func_to_pydantic_model, get_function_signature
from commons.utils.logging import get_kwargs_from_partial

load_dotenv()

# define the initial input state here
initial_state_key = "#E0"
lock = asyncio.Lock()
solve_prompt = """Solve the following task or problem. To solve the problem, we have made step-by-step Plan and \
retrieved corresponding Evidence to each Plan. Use them with caution since long evidence might \
contain irrelevant information.

Plan:
{plan}


Execution Results:
{execution_results}

Now solve the question or task according to provided Evidence above. Respond with the answer directly with no extra words.

Task: {task}
Response:
"""

plan_prompt = """For the following task, make plans that can solve the problem step by step. For each plan, indicate \
which external tool together with tool input to retrieve evidence. You can store the evidence into a \
variable #E that can be called by later tools. (Plan, #E1, Plan, #E2, Plan, ...) \
You must ensure reusability by defining similar input variables used across different evidence retrieval steps into a variable #I that can be called by later tools. (Plan, #E1[#I1] Plan, #E2[#I1,#I2], Plan, ...)

<available_tools>
Tools can be one of the following:
You are an advanced AI assistant designed to solve coding problems efficiently. You have access to the following tools:

1. ExecuteCode[input]:
- Executes code in a live environment, providing real-time error feedback, runtime behavior, and output.
- Essential for verifying code correctness, debugging, and ensuring solutions are free of runtime errors.
- Use this tool frequently, especially when:
 a) Validating your initial solution or any significant code changes
 b) Encountering errors or unexpected behavior
 c) Before considering any code solution complete

2. SearchWeb[input]:
- Searches the web for up-to-date information, similar to using Google.
- Use for finding specific facts, documentation, or examples related to coding problems.
- Helpful when you need to quickly find information about particular coding concepts, libraries, or best practices.

3. UseLLM[input]:
- Accesses your general knowledge and reasoning capabilities as a pre-trained language model.
- Use for high-level problem-solving, algorithm design, brainstorming ideas, or clarifying concepts.
- Rely on this when you're confident in generating solutions based on your existing knowledge.

</available_tools>


<tool_usage_guidelines>
Guidelines for solving coding problems:
1. Always start by using ExecuteCode to validate your initial solution.
2. Use ExecuteCode after each significant code modification or when you encounter errors.
3. Utilize SearchWeb to find relevant documentation or examples if unsure about syntax or best practices.
4. Employ UseLLM for overall problem-solving strategy and explaining your approach.
5. Before finalizing any solution, verify its correctness with ExecuteCode.

Remember: Frequent use of ExecuteCode is crucial for ensuring accurate and working solutions. Prioritize it over other tools when dealing with code implementation and debugging. These tools are designed to complement your capabilities and enhance problem-solving efficiency. Select the appropriate tool based on the problem context.

</tool_usage_guidelines>

<example_plan_1>
For example,
Task: Thomas, Toby, and Rebecca worked a total of 157 hours in one week. Thomas worked x
hours. Toby worked 10 hours less than twice what Thomas worked, and Rebecca worked 8 hours
less than Toby. How many hours did Rebecca work?
Plan: Define the initial variables.
#I1 = 157

Plan: Given Thomas worked x hours, translate the problem into algebraic expressions and solve
with Wolfram Alpha.
#I2 = (2x - 10)
#E1 = WolframAlpha[Solve x + #I2 + (#I2 − 8) = #I1]

Plan: Find out the number of hours Thomas worked.
#E2 = LLM[What is x, given #E1]

Plan: Calculate the number of hours Rebecca worked.
#E3 = Calculator[(2 * #E2 − 10) − 8]
</example_plan_1>

Begin!
Describe your plans with rich details. Each Plan must be followed by only one #E, where one #E may use one or more #I.

Task: {task}"""


# ---------------------------------------------------------------------------- #
#                           PROMPT BUILDER FUNCTIONS                           #
# ---------------------------------------------------------------------------- #


def _build_task_prompt(html_code: str) -> str:
    task = f"let {initial_state_key} be the following html: {html_code}, \nidentify any existing or potential errors or bugs in the code, fix them and return the fully working code"
    return textwrap.dedent(task)


def _build_step_prompt(step: Step) -> str:
    inputs = step.inputs or []
    tool_inputs_str = ", ".join([_input.refers_to for _input in inputs])
    output_str = step.output.identifier if step.output else ""
    step_str = f"""
Step {step.step_id}:
Title: {step.title}
Purpose: {step.purpose}
Tool: {step.tool.name}[{tool_inputs_str}]
Outputs: {output_str}\n
    """
    return textwrap.dedent(step_str)


def _resolve_state_key(value: str, rewoo_state: ReWOOState):
    assert isinstance(rewoo_state, ReWOOState)
    assert isinstance(value, str)

    logger.debug(f"Resolving state key for {value=}")

    state_key_pattern = re.compile(r"<state_key>(.*?)<\/state_key>")
    matches: Iterable[str] = state_key_pattern.findall(value)
    if len(matches) == 0:
        raise ValueError("No state keys found in value")

    unknown_keys = set(matches) - set(rewoo_state.results.keys())
    if len(unknown_keys) > 0:
        logger.warning(
            f"State keys that don't exist but were found in LLM's output: {unknown_keys}"
        )

    for match in matches:
        if match not in rewoo_state.results:
            continue
        value = value.replace(
            f"<state_key>{match}</state_key>", rewoo_state.results[match]
        )

    logger.debug(f"Resolved state key for {value=}")

    return value


def _map_tool_to_function(tool: Tool):
    if tool.name == "SearchWeb":
        return web_search_and_format
    elif tool.name == "UseLLM":
        return call_llm
    elif tool.name == "ExecuteCode":
        return fix_code
    else:
        raise NotImplementedError(f"Tool {tool.name} not implemented")


async def build_func_call(func: Callable, step: Step, rewoo_state: ReWOOState):
    logger.info(f"Building tool call for step {step.step_id}")

    state_prompt = ""
    for key, value in rewoo_state.results.items():
        state_prompt += f"<state_key>{key}</state_key>: {value}\n"

    tool_prompt = f"""
    Based on the following function signature, help me build the tool call.
    If the input parameter is present in the "App State" below, you do not need to specify the whole "value" again, just use "<state_key>key</state_key>" as the input, for example: "<state_key>#I0</state_key>"

    App State:
    {state_prompt}

    Function Signature: {get_function_signature(func)}
    Title: {step.title}
    Purpose: {step.purpose}
    """

    # if no results yet, it's probably the first step, provide additional context
    if len(rewoo_state.results.items()) == 0:
        tool_prompt += f"""
        Context: {rewoo_state.task}
        """

    tool_client = instructor.from_openai(  # type: ignore
        AsyncOpenAI(
            **_get_llm_api_kwargs(Provider.OPENROUTER),  # type: ignore
        ),
        mode=instructor.Mode.PARALLEL_TOOLS,
    )

    response_model = func_to_pydantic_model(func)
    logger.debug(f"Inferred JSON schema: {response_model.model_json_schema()}")

    # parallel tool only for gpt-4-turbo tho
    exec_args = await tool_client.chat.completions.create(
        messages=[{"role": "user", "content": tool_prompt}],
        model=get_settings().rewoo.func_call_builder,
        response_model=Iterable[response_model],
        max_tokens=8192,
    )

    collected_args = []
    for exec_arg in exec_args:
        logger.debug(f"Got tool call params: {exec_arg} for step {step.tool=}")
        collected_args.append(exec_arg.model_dump())

    logger.debug(f"Collected args: {collected_args}")
    assert len(collected_args) == 1
    return collected_args[0]


async def _execute_step_naive(step: Step, rewoo_state: ReWOOState):
    """Execute a step without awareness of other dependencies"""

    # resolve inputs
    func = _map_tool_to_function(step.tool)
    func_signature = get_function_signature(func)
    logger.info(f"Executing step {step.step_id} with {func_signature}")
    # based on the following step in the plan, determine the input
    exec_kwargs = await build_func_call(func, step, rewoo_state)

    # resolve kwargs by looking in state, this is because we're having some trouble with LLM truncating the long HTML output
    for key, value in exec_kwargs.items():
        try:
            exec_kwargs[key] = _resolve_state_key(value, rewoo_state)
        except ValueError:
            logger.error(f"No state key found for key: {key}, value: {value[:40]}...")
            pass
        except AssertionError:
            logger.error(
                f"Tried to resolve state key for unexpected value, key: {key} value: {value=}"
            )
            pass

    logger.debug(f"Resolved kwargs: {exec_kwargs}")

    result = await func(**exec_kwargs)
    logger.debug(f"Got result: {result} from tool exec")

    # parse output to string
    exec_output = ""
    if isinstance(result, ChatCompletion):
        exec_output = result.choices[0].message.content
    else:
        exec_output = str(result)

    assert step.output is not None

    # update our state
    state_key = step.output.identifier
    if state_key not in rewoo_state.results:
        rewoo_state.results[state_key] = exec_output
    else:
        logger.warning(f"State key {state_key} already exists, skipping")
    return


async def _execute_step_with_deps(step: Step, rewoo_state: ReWOOState):
    if step.inputs is None or len(step.inputs) == 0:
        logger.info(f"Executing step {step.step_id} with no inputs, title:{step.title}")
        try:
            await _execute_step_naive(step, rewoo_state)
        except NotImplementedError as exc:
            logger.error(f"Error mapping tool to function: {exc}")

        return

    logger.info(
        f"Executing step step_id:{step.step_id} with inputs, title:{step.title}"
    )

    # figure out dependencies have already been resolved
    start_time = datetime.datetime.now(datetime.timezone.utc)
    while datetime.datetime.now(
        datetime.timezone.utc
    ) - start_time < datetime.timedelta(
        seconds=get_settings().rewoo.max_dep_resolve_sec
    ):
        unresolved_deps = [
            input.refers_to
            for input in step.inputs
            if not rewoo_state.results.get(input.refers_to)
        ]
        if len(unresolved_deps) == 0:
            logger.info(
                f"All dependencies have been resolved, executing step, title:{step.title}"
            )
            break
        logger.info(
            f"Step id:{step.step_id} title:{step.title} is waiting for unresolved dependencies to be resolved: {unresolved_deps}"
        )
        await asyncio.sleep(3)

    try:
        await _execute_step_naive(step, rewoo_state)
    except Exception as exc:
        logger.error(f"Error executing step: {exc}")

    return


@observe(as_type="generation", capture_input=False, capture_output=False)
async def _generate_plan(task: str) -> Plan | None:
    """Generate plan before executing subsequent tools to solve the task"""
    try:
        client = get_llm_api_client()
        messages = [
            {
                "role": "user",
                "content": plan_prompt.format(task=task),
            }
        ]
        partial_func = functools.partial(
            client.chat.completions.create,
            messages=messages,  # type: ignore
            model=get_settings().rewoo.planner,
            stream=False,
            response_model=Plan,
        )

        completion: Plan = await partial_func()
        kwargs = get_kwargs_from_partial(partial_func)
        langfuse_context.update_current_observation(
            input=kwargs.pop("messages"),
            model=kwargs.pop("model"),
            output=completion.model_dump(),
            metadata={
                **kwargs,
            },
        )

        logger.debug(f"Generated plan... {completion=}")
        return completion

    except Exception as exc:
        logger.error(f"Error generating plan: {exc}")

    return None


@observe(as_type="generation", capture_input=False, capture_output=False)
async def _solve(rewoo_state: ReWOOState) -> str:
    plan_str: str = ""
    results_str: str = ""
    for step in rewoo_state.plan.steps:
        if step.inputs is None:
            continue
        plan_str += _build_step_prompt(step)

    for k, v in rewoo_state.results.items():
        results_str += f"{k}: {v}\n"

    logger.debug("Attempting to solve with the following state:")
    logger.debug(f"Plan: {plan_str}")
    logger.debug(f"Results: {results_str}")
    logger.debug(f"Task: {rewoo_state.task[:40]}...{rewoo_state.task[-40:]}")

    prompt = solve_prompt.format(
        plan=plan_str, execution_results=results_str, task=rewoo_state.task
    )

    client = get_llm_api_client()

    partial_func = functools.partial(
        client.chat.completions.create,
        messages=[{"role": "user", "content": prompt}],
        model=get_settings().rewoo.solver,
        response_model=HtmlCode,
    )

    kwargs = get_kwargs_from_partial(partial_func)
    completion: HtmlCode = await partial_func()
    langfuse_context.update_current_observation(
        input=kwargs.pop("messages"),
        model=kwargs.pop("model"),
        output=completion.model_dump(),
        metadata={
            **kwargs,
        },
    )

    logger.debug(f"Rewoo Solver got {completion=}")
    return completion.html_code


@observe(as_type="generation", capture_input=False, capture_output=False)
async def plan_and_solve(html_code: str):
    # TODO implement backtracking to be able to figure out when LLM's iteration actually makes code worse
    task = _build_task_prompt(html_code)
    plan = await _generate_plan(task)
    if plan is None:
        raise ValueError("Plan is None")

    # initial results
    results = {initial_state_key: html_code}
    rewoo_state = ReWOOState(task=task, plan=plan, results=results)

    sorted_steps = sorted(plan.steps, key=lambda s: s.step_id)

    # let tools execute in parallel
    await asyncio.gather(
        *[_execute_step_with_deps(step, rewoo_state) for step in sorted_steps]
    )

    solution = await _solve(rewoo_state)
    logger.info(f"Plan and Solve approach using ReWOO got solution:{solution=}")
    return solution


if __name__ == "__main__":
    asyncio.run(_generate_plan("hello"))
