import asyncio
import functools
import os
import shlex
import subprocess
import sys
import uuid
from asyncio import CancelledError
from typing import Literal

from bs4 import BeautifulSoup
from loguru import logger

try:
    from .headless_browser_visit import visit_page
except ImportError:
    from commons.code_executor.headless_browser_visit import visit_page


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
SANDBOX_WORK_DIR = FILE_DIR + "/untrusted"
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


def run_sandbox(html_code: str, run_uuid: str) -> subprocess.Popen | None:
    executor_dir = os.path.dirname(os.path.abspath(__file__))
    # inject
    modified_code = inject_error_logging_js(html_code)

    with open(executor_dir + "/untrusted/index.html", "w") as f:
        f.write(modified_code)

    try:
        run_sandbox_cmd = shlex.split(
            f"docker run --rm --name web-sandbox-container-{run_uuid} -p 3000:3000 -v {executor_dir}/untrusted:/untrusted {IMAGE_FULL_NAME}"
        )

        return subprocess.Popen(run_sandbox_cmd, check=True)
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


async def get_feedback(html_code: str, browser_delay: int = 5) -> str:
    await ensure_docker_image_built()

    run_uuid = str(uuid.uuid4())
    sandbox_task = asyncio.create_task(
        asyncio.to_thread(run_sandbox, html_code, run_uuid)
    )

    # visit the webpage
    await asyncio.sleep(browser_delay)
    await visit_page()

    # read the app.log to feed to the LLM
    feedback_log_file = SANDBOX_WORK_DIR + "/app.log"
    with open(feedback_log_file) as f:
        log_content = f.read()

    logger.info(f"Reading code feedback from log file, content: {log_content}")

    # clear the app.log to prepare for the next run
    os.remove(feedback_log_file)
    open(feedback_log_file, "w").close()
    try:
        # Cancel the sandbox task to stop the subprocess.run call
        sandbox_task.cancel()
        await sandbox_task
    except asyncio.CancelledError:
        logger.info("Sandbox task cancelled successfully")
    except Exception as e:
        logger.error(f"Error while cancelling sandbox task: {e}")

    try:
        stop_sandbox_cmd = shlex.split(f"docker stop web-sandbox-container-{run_uuid}")
        subprocess.run(stop_sandbox_cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error stopping the Docker container: {e}")

    return log_content


async def ensure_docker_image_built():
    async with lock:
        is_image_exists, _ = await _check_docker_image_exists()
        if is_image_exists:
            logger.debug("Docker image already exists, skipping build")
        else:
            await _build_docker_image()


@handle_cancelled_error
async def main():
    # res = _check_docker_image_exists()
    # logger.info(f"Docker image exists ? {res}")
    # _build_docker_image()
    # res = _check_docker_image_exists()
    # logger.info(f"Docker image exists ? {res}")
    # sandbox_code = inject_error_logging_js(html_code)
    # logger.info(f"Sandboxed code: {sandbox_code}")

    # feedback = await get_feedback(sandbox_code)
    # logger.info(feedback)
    # pass

    # async def test_lock():
    #     tasks = []
    #     for _ in range(5):  # Create 5 concurrent tasks
    #         tasks.append(asyncio.create_task(ensure_docker_image_built()))

    #     await asyncio.gather(*tasks)
    #     logger.info("All tasks completed")

    # # Run the test
    # await test_lock()

    pass


if __name__ == "__main__":
    asyncio.run(main())


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

        // intentional typo here to test uncaught error
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>

</html>

"""


bad_html_code = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solar System Visualization - With Intentional Errors</title>
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
        // Intentional error: 'const' used instead of 'let' where reassignment occurs
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
            // Intentional error: Misspelled 'MeshBasicMaterial'
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
                // Intentional error: Missing 'Math.' before 'cos' and 'sin'
                mesh.position.x = cos(Date.now() * 0.001 * (1 / planet.distance)) * planet.distance;
                mesh.position.z = sin(Date.now() * 0.001 * (1 / planet.distance)) * planet.distance;
            });
            renderer.render(scene, camera);
        }

        // animate();

        window.addEventListener('resize', ( => {
            // Intentional error: Misspelled 'innerWidth'
            camera.aspect = window.inerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>

</html>
"""
