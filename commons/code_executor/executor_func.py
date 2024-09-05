import os
import shlex
import subprocess

import lxml
from headless_browser_visit import visit_page
from loguru import logger

IMAGE_NAME = "web-sandbox"
IMAGE_TAG = "latest"
IMAGE_FULL_NAME = f"{IMAGE_NAME}:{IMAGE_TAG}"


def _build_docker_image():
    build_cmd = shlex.split(f"docker build -t {IMAGE_FULL_NAME} .")

    build_success = False
    try:
        subprocess.run(build_cmd, shell=True, check=True)
        build_success = True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error building Docker image: {e}")

    return build_success


def _is_valid_html(html_code: str) -> bool:
    """
    Parse the HTML string using html5lib and BeautifulSoup to validate it.

    Args:
        html (str): A single HTML file that contains HTML, JS and CSS inlined.

    Returns:
        bool: True if the HTML is valid, False otherwise.
    """
    try:
        # Parse the HTML using lxml
        parser = lxml.etree.HTMLParser()
        lxml.etree.fromstring(html_code, parser)

        # If parsing succeeds without raising an exception, the HTML is considered valid
        return True
    except lxml.etree.ParseError as e:
        logger.error(f"HTML parsing error: {str(e)}")
        pass
    except Exception as e:
        logger.error(f"Unexpected error during HTML parsing: {str(e)}")
        pass

    return False


async def get_feedback(html_code: str) -> str:
    # TODO to inject the error logging JS into the index.html RIGHT AFTER the HTML tag
    # ensure we are inside the `code_executor/`
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    # write the html code to a file called index.html
    if not _is_valid_html(html_code):
        raise ValueError("Invalid HTML")

    with open("index.html", "w") as f:
        f.write(html_code)

    try:
        run_sandbox_cmd = shlex.split(
            f"docker run --rm --name web-sandbox-container -p 3000:3000 -v $(pwd)/untrusted:/untrusted {IMAGE_FULL_NAME}"
        )

        subprocess.run(run_sandbox_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running the sandbox via subprocess, error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error running the sandbox via subprocess, error: {e}")
        raise

    # visit the webpage
    await visit_page()

    # read the app.log to feed to the LLM
    feedback_log_file = "app.log"
    with open(feedback_log_file) as f:
        log_content = f.read()

    # clear the app.log to prepare for the next run
    open(feedback_log_file, "w").close()
    return log_content
