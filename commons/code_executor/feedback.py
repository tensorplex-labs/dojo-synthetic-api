import asyncio
import os
import re
import shutil
import socket
import subprocess
import uuid
from asyncio.subprocess import Process
from typing import Literal

import aiofiles
import aiofiles.os
from bs4 import BeautifulSoup
from loguru import logger
from pydantic import BaseModel
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page


class ErrorInfo(BaseModel):
    message: str
    lineno: int
    colno: int
    source: str
    stack: str


IMAGE_NAME = "web-sandbox"
IMAGE_TAG = "latest"
IMAGE_FULL_NAME = f"{IMAGE_NAME}:{IMAGE_TAG}"
# location of this file, irrespective of where the code is run from
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
SANDBOX_WORK_DIR = FILE_DIR + "/sandbox-workspace"
lock = asyncio.Lock()


async def _visit_page(url: str) -> list[str]:
    """
    Visits the given URL using pyppeteer to trigger rendering of the webpage and
    subsequently log the status based on specific events and conditions.

    Optional list of functions to call where the outputs need to be "True" to be considered passing

    Args:
        url (str): The URL to be visited.

    Returns:
        list[str]: A list of feedback messages from the browser which uses puppeteer.

    Raises:
        Exception: If there's an error visiting the page.
    """
    browser: Browser | None = None
    # TODO add bunch of selector checks, domcontentloaded within X secs, etc.
    browser_feedback: list[str] = []
    try:
        browser = await launch(headless=True)
        page: Page = await browser.newPage()
        logger.debug(f"Attempting to visit page {url}")

        # Navigate to the URL and wait for the 'networkidle0' event
        await page.goto(url, {"waitUntil": "networkidle0"})

        return browser_feedback
    except Exception as e:
        logger.error(f"Error visiting the page: {e}")
    finally:
        if browser:
            await browser.close()

    return []


async def _build_docker_image() -> tuple[Literal[True], int]:
    """
    Builds the Docker image for the web sandbox on the host machine.

    Raises:
        e: _description_

    Returns:
        tuple[Literal[True], int]: True to indicate the image was built successfully,
        and the return code of the build command.
    """
    build_cmd = f"docker build -t {IMAGE_FULL_NAME} {FILE_DIR}"
    try:
        logger.debug(f"Trying to run command: {build_cmd}")
        process = await asyncio.create_subprocess_shell(build_cmd)
        return True, await process.wait()
    except Exception as e:
        logger.error(f"Error building Docker image: {e}")
        raise e


async def _check_docker_image_exists(image_name: str = IMAGE_NAME) -> tuple[bool, int]:
    """
    Checks if the Docker image exists on the host machine.

    Args:
        image_name (str, optional): The name of the Docker image to check. Defaults to IMAGE_NAME.

    Returns:
        tuple[bool, int]: True to indicate the image exists, and the return code of the check command.
    """
    try:
        check_image_cmd = f"docker images -q {image_name}"
        process = await asyncio.create_subprocess_shell(
            check_image_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode and process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, check_image_cmd, stdout, stderr
            )
        exists = bool(stdout.decode().strip())
        logger.debug(
            f"Checking if Docker image {image_name} exists ? {exists}, stdout: {stdout.decode()}, stderr: {stderr.decode()}"
        )
        return exists, await process.wait()
    except Exception as e:
        logger.error(f"Check docker command failed to run: {e}")
        raise


error_logging_js: str = ""
try:
    with open(FILE_DIR + "/errorLogging.js") as f:
        error_logging_js = f.read()
except Exception as e:
    logger.error(f"Error reading errorLogging.js: {e}")


def _inject_error_logging_js(html_code: str) -> str:
    """
    Injects the error logging JavaScript into the HTML code.

    Args:
        html_code (str): The HTML code to inject the error logging JavaScript into.

    Returns:
        str: The modified HTML code with the error logging JavaScript injected.
    """
    soup = BeautifulSoup(html_code, "html.parser")
    html_tag = soup.find("html")

    if html_tag:
        # Check for existing commented logging code
        existing_script = soup.find("script")
        if (
            existing_script
            and existing_script.string
            and re.search(
                r"/\*\s*function\s+logErrorToServer\s*\(errorData\)",
                existing_script.string,
                re.DOTALL,
            )
        ):
            # Uncomment the existing code
            uncommented_code = re.sub(r"/\*|\*/", "", existing_script.string)
            existing_script.string = uncommented_code
        else:
            # If no commented code found, then inject logging code
            new_tag = soup.new_tag("script")
            new_tag.string = error_logging_js
            html_tag.insert(1, new_tag)
    else:
        logger.warning("No <html> tag found in the HTML code")

    return str(soup)


def _remove_error_logging_js(html_code: str) -> str:
    """
    Removes the error logging JavaScript from the HTML code.

    Args:
        html_code (str): The HTML code to remove the error logging JavaScript from.

    Returns:
        str: The modified HTML code with the error logging JavaScript removed.
    """
    soup = BeautifulSoup(html_code, "html.parser")
    # Find all script tags
    script_tags = soup.find_all("script")

    # Search for the script tag containing the pattern "function logErrorToServer"
    count = 0
    for script in script_tags:
        # make sure this matches whatever is inside errorLogging.js
        # aggressively remove the script tag
        if script.string and re.search(
            r"function.*logErrorToServer.*\(errorData\)", script.string
        ):
            script.decompose()
            count += 1
            logger.debug(
                f"Removed error logging script tag from the HTML code, total: {count}"
            )

    html_code_stripped = str(soup)
    assert (
        html_code_stripped != ""
    ), "Stripped HTML code is completely empty, something went wrong"

    return html_code_stripped


def _find_free_port():
    """
    Finds a free port in the range 3000-3999, because we want to allow running the feedback loop asynchronously using docker. This means that we might run into cases where port <port_no> is already in use by another container, so we need to dynamically find free ports.

    Raises:
        OSError: If no free ports are available in the range 3000-3999.

    Returns:
        int: A free port number in the range 3000-3999.
    """
    for port in range(3000, 4000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    raise OSError("No free ports available in the range 3000-3999")


async def _run_sandbox(
    work_dir: str, run_uuid: str, port_number: int
) -> Process | None:
    assert os.path.exists(work_dir), f"Work dir {work_dir} does not exist"
    assert os.path.exists(
        os.path.join(work_dir, "index.html")
    ), f"Index html file does not exist in {work_dir}"

    try:
        run_sandbox_cmd = f"docker run --rm --name web-sandbox-container-{run_uuid} -p {port_number}:3000 -v {work_dir}:/untrusted {IMAGE_FULL_NAME}"

        process = await asyncio.create_subprocess_shell(
            run_sandbox_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return process
    except subprocess.CalledProcessError as e:
        if e.returncode == 130:
            logger.warning("Docker container was terminated by SIGINT (Ctrl+C)")
            return
        elif e.returncode == 143:
            logger.warning("Docker container was terminated by SIGTERM")
            return

        logger.error(
            f"Error running the sandbox via subprocess. Command failed with return code {e.returncode}. Error output: {e.stderr}"
        )
        raise
    except Exception as e:
        logger.error(f"Error running the sandbox via subprocess, error: {e}")
        raise

    return


async def get_feedback(html_code: str, preserve_files: bool = False) -> tuple[str, str]:
    """
    Retrieves feedback for the given HTML code by executing it in a sandboxed environment.

    Args:
        html_code (str): The original HTML code to be executed and analyzed.
        browser_delay (int, optional): The delay in seconds before visiting the webpage. Defaults to 5.
        preserve_files (bool, optional): Whether to preserve the files generated during execution. Defaults to True.

    Returns:
        str: The feedback generated by the execution of the HTML code.
        str: The modified HTML code that includes the error logging JS as inline script(in order to parse the buggy locations in code for the LLM).

    Raises:
        Any exceptions that occur during the execution process.

    """

    await _ensure_docker_image_built()

    run_uuid = str(uuid.uuid4())
    run_dir = os.path.join(SANDBOX_WORK_DIR, f"run_{run_uuid}")
    index_html_path = os.path.join(run_dir, "index.html")
    log_file_path = os.path.join(run_dir, "app.log")

    # ensure folder exists
    await aiofiles.os.makedirs(run_dir, exist_ok=True)

    async with aiofiles.open(index_html_path, "w") as f:
        # inject error logging js for client side
        modified_code = _inject_error_logging_js(html_code)
        await f.write(modified_code)

        if not modified_code:
            raise ValueError(
                "Failed to inject the error logging JS into the original HTML code."
            )

    # find a free port on the host machine in the range 3000-3999
    port_number = _find_free_port()

    # run the sandbox
    sandbox_process = await _run_sandbox(run_dir, run_uuid, port_number)

    # visit the webpage
    page_url = f"http://localhost:{port_number}"
    # visit page to be able to trigger rendering of page and write logs to app.log
    await _visit_page(page_url)

    # read the app.log to feed to the LLM
    nodejs_server_feedback: str = ""
    async with aiofiles.open(log_file_path) as f:
        nodejs_server_feedback = await f.read()

        logger.info(
            f"Reading code feedback from log file, content: {nodejs_server_feedback}"
        )

    try:
        if sandbox_process:
            sandbox_process.kill()
    except Exception as e:
        logger.error(f"Error while cancelling sandbox process: {e}")

    try:
        stop_sandbox_cmd = f"docker stop web-sandbox-container-{run_uuid}"
        process = await asyncio.create_subprocess_shell(
            stop_sandbox_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(
                f"Error stopping the Docker container: {stderr.decode().strip()}"
            )
    except Exception as e:
        logger.error(f"Error stopping the Docker container: {e}")

    if not preserve_files:
        # remove the sandbox work dir
        await asyncio.to_thread(shutil.rmtree, run_dir, ignore_errors=True)

    # comment out injected code before returning
    commented_html = _comment_injected_code(modified_code)
    return nodejs_server_feedback, commented_html


def _comment_injected_code(code_with_injections: str) -> str:
    """
    comments out the previously inserted JS logging code from the HTML.

    Args:
    code_with_injections (str): The HTML code to comment the error logging JavaScript from.

    Returns:
    str: The modified HTML code with the error logging JavaScript commented out.
    """
    soup = BeautifulSoup(code_with_injections, "html.parser")
    html_tag = soup.find("html")
    if html_tag:
        script_tag = soup.find("script")
        if (
            script_tag
            and script_tag.string
            and re.search(
                r"function.*logErrorToServer.*\(errorData\)", script_tag.string
            )
        ):
            commented_content = f"/*{script_tag.string}*/"
            script_tag.string = commented_content
        else:
            logger.warning("No <script> tag found in the html tag")
    else:
        logger.warning("No <html> tag found in the HTML code")

    return str(soup)


async def _ensure_docker_image_built():
    async with lock:
        is_image_exists, _ = await _check_docker_image_exists()
        if is_image_exists:
            logger.debug("Docker image already exists, skipping build")
        else:
            await _build_docker_image()


# # TODO treesitter parsing to get the whole function that is buggy, and maybe subfunctions
# def _parse_nodejs_server_feedback(
#     html_code: str,
#     feedback: str,
#     before_context_lines: int = 10,  # pyright: ignore[reportUnusedParameter]
#     after_context_lines: int = 10,  # pyright: ignore[reportUnusedParameter]
# ):
#     # parse each line which is a JSON object as defined by winston logging in server.js
#     feedback_lines = []
#     for line in feedback.splitlines():
#         try:
#             # Process the JSON data as needed
#             # For example, you could yield or return it:
#             feedback_lines.append(json.loads(line))
#         except json.JSONDecodeError:
#             # If the line is not valid JSON, skip it
#             continue

#     # for each feedback line grab buggy locations
#     error_messages = []
#     for feedback_line in feedback_lines:
#         # get the line number and the function name
#         message_json = feedback_line["message"]
#         error_info: ErrorInfo | None = None
#         try:
#             message_data = json.loads(message_json)
#             error_info = ErrorInfo(
#                 message=message_data["message"],
#                 lineno=message_data["lineno"],
#                 colno=message_data["colno"],
#                 source=message_data["source"],
#                 stack=message_data["stack"],
#             )
#             error_messages.append(error_info)
#         except json.JSONDecodeError:
#             continue

#     return error_messages


# main for testing commenting and uncommenting injected code.
def main():
    """
    1. call _inject_code and save as file
    2. comment that code and save as file
    3. call _inject on the file from 2.
    """
    html_code: str = ""
    try:
        with open(FILE_DIR + "/clean.html") as f:
            html_code = f.read()
    except Exception as e:
        logger.error(f"Error reading clean.html: {e}")

    # 1. inject code save as injected.html
    injected_code = _inject_error_logging_js(html_code)
    with open(FILE_DIR + "/injected.html", "w") as f:
        f.write(injected_code)
    print(f"logging code injected. Output saved to {FILE_DIR}/injected.html")

    # 2 comment code save as commented.html
    commented_code = _comment_injected_code(injected_code)
    with open(FILE_DIR + "/commented.html", "w") as f:
        f.write(commented_code)
    print(f"logging code commented. Output saved to {FILE_DIR}/commented.html")

    # 3 inject on commented code
    uncommented = _inject_error_logging_js(commented_code)
    with open(FILE_DIR + "/uncommented.html", "w") as f:
        f.write(uncommented)
    print(
        f"Error logging JavaScript removed. Output saved to {FILE_DIR}/uncommented.html"
    )


if __name__ == "__main__":
    asyncio.run(main())
