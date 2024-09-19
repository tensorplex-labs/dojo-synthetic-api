import asyncio
import functools
import os
import socket
import subprocess
import sys
import uuid
from asyncio import CancelledError
from asyncio.subprocess import Process
from typing import Literal

import aiofiles
import aiofiles.os
from bs4 import BeautifulSoup
from loguru import logger
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page


async def visit_page(url: str) -> None:
    try:
        browser: Browser = await launch(headless=True)
        page: Page = await browser.newPage()
        logger.debug(f"Attempting to visit page {url}")
        await page.goto(url, {"waitUntil": "networkidle0"})
    except Exception as e:
        logger.error(f"Error visiting the page: {e}")
    finally:
        await browser.close()


bad_html_code = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solar System Visualization</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #000;
            overflw: hidden;
        }

        #solar-system {
            width: 100vw;
            height: 100vh;
        }
    </style>
</head>

<body>
    <canvas id="solar-system"></canvas>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.mjs"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeigh, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('solar-system') });
        renderer.setSize(window.innerWidth, window.innerHeight);

        const sunGeometry = new THREE.SphereGeometry(5, 32, 32);
        const sunMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 });
        const sun = new THREE.Mesh(sunGeometry, sunMaterial);
        scene.add(sun);

        const planets = [
            { name: 'Mercury', radius: 0.5, distance: 10, color: 0x8a8a8a },
            { name: 'Venus', radius: 0.8, distance: 15, color: 0xe39e1c },
            { name: 'Earth', radius: 1, distance: 20, color: 0x6b93d6 },
            { name: 'Mars', radius: 0.7, distance: 25, color: 0xc1440e },
            { name: 'Jupiter', radius: 2, distance: 35, color: 0xd8ca9d },
            { name: 'Saturn', radius: 1.8, distance: 45, color: 0xead6b8 },
            { name: 'Uranus', radius: 1.3, distance: 55, color: 0xd1e7e7 },
            { name: 'Neptune', radius: 1.2, distance: 65, color: 0x5b5ddf }
        ];

        planets.forEach(planet => {
            const geometry = new THREE.SphereGeometry(planet.radius, 32, 32);
            const material = new THREE.MeshBasicMaterrial({ color: planet.color });
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.x = planet.distance;
            scene.add(mesh);
        });

        camera.position.z = 100;

        function animate() {
            requestAnimationFrame(animate);
            planets.forEach((planet, index) => {
                const mesh = scene.children[index + 1];
                mesh.position.x = cos(Date.now() * 0.001 * (1 / planet.distance)) * planet.distance;
                mesh.position.z = sin(Date.now() * 0.001 * (1 / planet.distance)) * planet.distance;
            });
            renderer.render(scene, camera);
        }

        // animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.inerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>

</html>
"""

html_code = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solar System Visualization</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #000;
            overflow: hidden;
        }

        #solar-system {
            width: 100vw;
            height: 100vh;
        }
    </style>
</head>

<body>
    <canvas id="solar-system"></canvas>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('solar-system') });
        renderer.setSize(window.innerWidth, window.innerHeight);

        const sunGeometry = new THREE.SphereGeometry(5, 32, 32);
        const sunMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 });
        const sun = new THREE.Mesh(sunGeometry, sunMaterial);
        scene.add(sun);

        const planets = [
            { name: 'Mercury', radius: 0.5, distance: 10, color: 0x8a8a8a },
            { name: 'Venus', radius: 0.8, distance: 15, color: 0xe39e1c },
            { name: 'Earth', radius: 1, distance: 20, color: 0x6b93d6 },
            { name: 'Mars', radius: 0.7, distance: 25, color: 0xc1440e },
            { name: 'Jupiter', radius: 2, distance: 35, color: 0xd8ca9d },
            { name: 'Saturn', radius: 1.8, distance: 45, color: 0xead6b8 },
            { name: 'Uranus', radius: 1.3, distance: 55, color: 0xd1e7e7 },
            { name: 'Neptune', radius: 1.2, distance: 65, color: 0x5b5ddf }
        ];

        planets.forEach(planet => {
            const geometry = new THREE.SphereGeometry(planet.radius, 32, 32);
            const material = new THREE.MeshBasicMaterial({ color: planet.color });
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.x = planet.distance;
            scene.add(mesh);
        });

        camera.position.z = 100;

        function animate() {
            requestAnimationFrame(animate);
            planets.forEach((planet, index) => {
                const mesh = scene.children[index + 1];
                mesh.position.x = Math.cos(Date.now() * 0.001 * (1 / planet.distance)) * planet.distance;
                mesh.position.z = Math.sin(Date.now() * 0.001 * (1 / planet.distance)) * planet.distance;
            });
            renderer.render(scene, camera);
        }

        animate();

        window.addEventListener('resize', ( => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>

</html>

"""


def handle_cancelled_error(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except CancelledError:
            logger.info(f"Operation cancelled: {func.__name__}")

    return wrapper


logger.remove()
logger.add(sys.stdout, level="DEBUG")

IMAGE_NAME = "web-sandbox"
IMAGE_TAG = "latest"
IMAGE_FULL_NAME = f"{IMAGE_NAME}:{IMAGE_TAG}"
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
SANDBOX_WORK_DIR = FILE_DIR + "/sandbox-workspace"
lock = asyncio.Lock()


async def _build_docker_image() -> tuple[Literal[True], int]:
    build_cmd = f"docker build -t {IMAGE_FULL_NAME} {FILE_DIR}"
    try:
        logger.debug(f"Trying to run command: {build_cmd}")
        process = await asyncio.create_subprocess_shell(build_cmd)
        return True, await process.wait()
    except Exception as e:
        logger.error(f"Error building Docker image: {e}")
        raise e


async def _check_docker_image_exists(image_name: str = IMAGE_NAME) -> tuple[bool, int]:
    try:
        check_image_cmd = f"docker images -q {image_name}"
        process = await asyncio.create_subprocess_shell(
            check_image_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
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


with open(FILE_DIR + "/errorLogging.js") as f:
    error_logging_js = f.read()

logger.debug(f"Error logging js:\n{error_logging_js}")


def inject_error_logging_js(html_code: str) -> str:
    soup = BeautifulSoup(html_code, "html.parser")
    html_tag = soup.find("html")

    if html_tag:
        new_tag = soup.new_tag("script")
        new_tag.string = error_logging_js
        html_tag.insert(1, new_tag)
    else:
        logger.warning("No <html> tag found in the HTML code")

    return str(soup)


def find_free_port():
    for port in range(3000, 4000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    raise OSError("No free ports available in the range 3000-3999")


async def run_sandbox(work_dir: str, run_uuid: str, port_number: int) -> Process | None:
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


async def get_feedback(html_code: str, preserve_files: bool = True) -> str:
    """
    Retrieves feedback for the given HTML code by executing it in a sandboxed environment.

    Args:
        html_code (str): The HTML code to be executed and analyzed.
        browser_delay (int, optional): The delay in seconds before visiting the webpage. Defaults to 5.
        preserve_files (bool, optional): Whether to preserve the files generated during execution. Defaults to True.

    Returns:
        str: The feedback generated by the execution of the HTML code.

    Raises:
        Any exceptions that occur during the execution process.

    """

    await ensure_docker_image_built()

    run_uuid = str(uuid.uuid4())
    run_dir = os.path.join(SANDBOX_WORK_DIR, f"run_{run_uuid}")
    index_html_path = os.path.join(run_dir, "index.html")
    log_file_path = os.path.join(run_dir, "app.log")

    # ensure folder exists
    await aiofiles.os.makedirs(run_dir, exist_ok=True)

    async with aiofiles.open(index_html_path, "w") as f:
        # inject error logging js for client side
        modified_code = inject_error_logging_js(html_code)
        await f.write(modified_code)

    port_number = find_free_port()
    sandbox_process = await run_sandbox(run_dir, run_uuid, port_number)

    # visit the webpage
    page_url = f"http://localhost:{port_number}"
    await visit_page(page_url)

    # read the app.log to feed to the LLM
    log_content: str = ""

    async with aiofiles.open(log_file_path) as f:
        log_content = await f.read()

        logger.info(f"Reading code feedback from log file, content: {log_content}")

    try:
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
        await aiofiles.os.rmdir(run_dir)

    return log_content


async def ensure_docker_image_built():
    async with lock:
        is_image_exists, _ = await _check_docker_image_exists()
        if is_image_exists:
            logger.debug("Docker image already exists, skipping build")
        else:
            await _build_docker_image()


async def test_async_lock_build_docker():
    async def test_lock():
        tasks = []
        for _ in range(5):  # Create 5 concurrent tasks
            tasks.append(asyncio.create_task(ensure_docker_image_built()))

        await asyncio.gather(*tasks)
        logger.info("All tasks completed")

    await test_lock()

    pass


@handle_cancelled_error
async def main():
    feedback = await get_feedback(bad_html_code)
    logger.info(feedback)
    # pass

    pass


if __name__ == "__main__":
    asyncio.run(main())
