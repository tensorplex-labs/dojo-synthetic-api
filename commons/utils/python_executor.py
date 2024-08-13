import base64
import sys

sys.path.append("./")
import json
import os
import re
import time
from collections import defaultdict
from typing import Any, DefaultDict, List, Optional

import httpx
import pandas as pd
from dotenv import load_dotenv
from e2b_code_interpreter import CodeInterpreter
from e2b_code_interpreter.models import Result
from loguru import logger

from commons.utils.utils import ExecutionError, get_packages
from e2b.sandbox.filesystem_watcher import FilesystemEvent

load_dotenv()

PLOTLY_TEMPLATE = """
<!DOCTYPE html>
<html>

<head>
    <title>Python Executor</title>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js" charset="utf-8"></script>
</head>

<body>
    <div id="tester" style="width:600px;height:250px;"></div>
    <script>
        var plotData = {plotData};

        Plotly.newPlot('tester', plotData.data, plotData.layout);
    </script>
</body>

</html>
"""

IMG_TEMPLATE = """
<img src="data:image/png;base64, {img}" />
"""

SCRIPT_TEMPLATE = """
<script>
    {script}
</script>
"""

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>

<head>
    <title>Python Executor</title>
</head>

<body>
    {content}
</body>

</html>
"""


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


class PythonExecutor:
    def __init__(
        self,
        code: Optional[str] = None,
        file: Optional[str] = None,
        debug: bool = False,
    ):
        if code is None and file is None:
            raise ValueError("Either code or file should be provided")

        if code is not None and file is not None:
            raise ValueError("Only one of code or file should be provided")

        if code is not None:
            self.code = code
        elif file is not None:
            with open(file, "r") as f:
                self.code = f.read()

        self.created_files: DefaultDict[str, Any] = defaultdict(list)
        self.debug = debug
        self.preprocess_code()
        # print("Code preprocessed")
        # print(self.code)

    @staticmethod
    def modify_plotly_to_html(code: str):
        def replacement_func(match):
            full_match = match.group(0)
            args = match.group(2)

            # Check if include_plotlyjs is already present
            include_plotlyjs_pattern = r'include_plotlyjs\s*=\s*(["\']?)([^,\'"]+)\1'
            include_plotlyjs_match = re.search(include_plotlyjs_pattern, args)

            if include_plotlyjs_match:
                current_value = include_plotlyjs_match.group(2)
                if current_value.lower() != "cdn":
                    # Replace the existing include_plotlyjs value with 'cdn'
                    args = re.sub(
                        include_plotlyjs_pattern, "include_plotlyjs='cdn'", args
                    )
                    return f"{match.group(1)}{args})"
                else:
                    return full_match  # Return unchanged if already includes cdn
            else:
                # Add include_plotlyjs='cdn' if it's not present
                if args.strip():
                    return f"{match.group(1)}{args}, include_plotlyjs='cdn')"
                else:
                    return f"{match.group(1)}include_plotlyjs='cdn')"

        pattern = r"(fig\.write_html\s*\()([^)]*)\)"
        return re.sub(pattern, replacement_func, code)

    def preprocess_code(self):
        self.code = self.replace_mpld3_show(self.code)
        self.code = self.modify_plotly_to_html(self.code)

    def initialize_sandbox(self):
        sandbox = CodeInterpreter(cwd="/home/user")
        kernel_id = sandbox.notebook.create_kernel(cwd="/home/user")
        self.sandbox = sandbox
        self.kernel_id = kernel_id

        watch_tmp = False
        packages = " ".join(get_packages(self.code))

        if "bokeh" in packages:
            watch_tmp = True

        if "ipywidgets" in packages:
            raise ExecutionError("ipywidgets is not supported", self.code)

        logger.debug(f"Installing packages {packages}")
        sandbox.notebook.exec_cell(
            f"!pip install {packages}", kernel_id=kernel_id, timeout=300
        )
        self.start_watcher(watch_tmp=watch_tmp)

    def execute(self):
        self.initialize_sandbox()
        ports = self.get_running_ports()
        execution = self.sandbox.notebook.exec_cell(
            self.code, on_stderr=print, on_stdout=print
        )
        if execution.error:
            raise ExecutionError(execution.error.traceback, self.code)

        results = execution.results
        final_ports = self.get_running_ports()
        if z := final_ports - ports:
            port = z.pop()
            url = "https://" + self.sandbox.get_hostname(port)
            return self.get_webpage(url)

        return self.handle_responses(results)

    def close_sandbox(self):
        print("Closing sandbox")
        self.sandbox.close()

    def get_running_ports(self) -> set[int]:
        self.install_lsof()
        initial_ports = self.sandbox.process.start_and_wait(
            cmd="lsof -i -P -n | grep LISTEN | awk '{print $9}' | sed 's/.*://'"
        )
        all_ports = initial_ports.stdout.split("\n")
        return set(
            [
                int(port)
                for port in all_ports
                if port != "" and len(port) < 5 and port != "8888"
            ]
        )

    @staticmethod
    def replace_mpld3_show(code: str):
        pattern = r"mpld3\.show\((\w*)\)"
        replacement = r"mpld3.display(\1)"
        return re.sub(pattern, replacement, code)

    @staticmethod
    def _list_dir(sandbox: CodeInterpreter, dir: str):
        content = sandbox.filesystem.list(dir)
        for item in content:
            print(f"Is '{item.name}' directory?", item.is_dir)
        print("------------------------------------")

    @run_once
    def install_lsof(self):
        logger.debug("Installing lsof")
        self.sandbox.process.start_and_wait(cmd="sudo apt-get install lsof")

    def get_webpage(self, url: str):
        response = httpx.get(url)
        if response.status_code == 200:
            logger.info(f"Returning webpage from {url}")
            return response.text

        return BASE_TEMPLATE.format(content="")

    def start_watcher(self, dir: str = "/home/user", watch_tmp: bool = False):
        def download_file(event: FilesystemEvent):
            logger.info(f"Operation {event.operation} {event.path}")
            if event.operation == "Write":
                file_path = event.path
                file_name = os.path.basename(file_path)
                if file_name.endswith(".html"):
                    bytes_file = self.sandbox.download_file(file_path, timeout=None)
                    self.created_files[file_name] = bytes_file.decode("utf-8")

                if file_name.endswith(".png"):
                    bytes_file = self.sandbox.download_file(file_path, timeout=None)
                    img_tag = IMG_TEMPLATE.format(
                        img=base64.b64encode(bytes_file).decode("utf-8")
                    )
                    self.created_files[file_name] = BASE_TEMPLATE.format(
                        content=img_tag
                    )

        if watch_tmp:
            tmp_watcher = self.sandbox.filesystem.watch_dir("/tmp")
            tmp_watcher.add_event_listener(lambda event: download_file(event))
            logger.debug("Watching /tmp directory")
            tmp_watcher.start()

        watcher = self.sandbox.filesystem.watch_dir(dir)
        watcher.add_event_listener(lambda event: download_file(event))
        watcher.start()

    def handle_responses(self, results: List[Result]) -> str:
        if len(self.created_files) != 0:
            # print(self.created_files.keys())
            keys = list(self.created_files.keys())
            logger.info(f"Returning file {keys[0]}")
            return self.created_files[keys[0]]
        else:
            raise ExecutionError(
                "Visualisation must be saved to an external html file", self.code
            )

        ## Uncomment this block to handle kernel outputs
        # return self.handle_output(results)

    def handle_output(self, results: List[Result]):
        datatypes = defaultdict(list)
        for result in results:
            df = pd.json_normalize(result.raw, max_level=0)
            result_dict = df.to_dict(orient="records")[0]
            for key, value in result_dict.items():
                datatypes[key].append(value)

        if self.debug:
            with open("output.json", "w") as f:
                dump = [vars(result) for result in results]
                json.dump(dump, f)
            with open("output_formatted.json", "w") as f:
                json.dump(datatypes, f)

        if "application/vnd.plotly.v1+json" in datatypes:
            plot_data = datatypes["application/vnd.plotly.v1+json"][0]
            dumps = json.dumps(plot_data)
            return PLOTLY_TEMPLATE.format(plotData=dumps)

        content_parts = []
        if "text/html" in datatypes:
            content_parts.extend(datatypes["text/html"])
        if "image/png" in datatypes:
            content_parts.append(IMG_TEMPLATE.format(img=datatypes["image/png"].pop()))
        if "application/javascript" in datatypes:
            content_parts.append(
                SCRIPT_TEMPLATE.format(
                    script="\n".join(datatypes["application/javascript"])
                )
            )
        content = "\n".join(content_parts)
        logger.info("Returning content from kernel output")
        return BASE_TEMPLATE.format(content=content)

    def main(self):
        MAX_RETRIES = 3
        RETRY_DELAY = 3  # seconds

        for retry_count in range(MAX_RETRIES):
            try:
                output = self.execute()
                return output  # If execution succeeds, break out of the retry loop
            except ExecutionError as e:
                self.close_sandbox()
                raise e
            except Exception as e:
                logger.exception(e)
                self.close_sandbox()

                if retry_count < MAX_RETRIES - 1:
                    logger.warning(
                        f"Execution failed. Retrying in {RETRY_DELAY} seconds... (Attempt {retry_count + 1}/{MAX_RETRIES})"
                    )
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(
                        f"Execution failed after {MAX_RETRIES} attempts. Raising exception."
                    )
                    raise e

        self.close_sandbox()
        return BASE_TEMPLATE.format(content="")


if __name__ == "__main__":
    test_code = "import matplotlib.pyplot as plt\nimport numpy as np\n\n# Mock data\nage_groups = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100']\npeople_counts = [150, 200, 340, 300, 320, 280, 220, 190, 100, 60]\nmedian_income = [30000, 32000, 34000, 36000, 38000, 40000, 42000, 44000, 46000, 48000]\naverage_education_level = ['Elementary', 'Middle School', 'High School', 'College', 'Bachelor', 'Master', 'PhD', 'PhD', 'PhD', 'PhD']\n\nfig, ax = plt.subplots()\nrects = ax.bar(age_groups, people_counts)\n\n# Adding interactivity\ndef on_click(event):\n    bar = rects.patches\n    for i, rect in enumerate(bar):\n        if rect.contains(event)[0]:\n            print(f'Age Group: {age_groups[i]}\\nMedian Income: {median_income[i]}\\nEducation Level: {average_education_level[i]}')\n\ndef hover(event):\n    ax.set_title(f'Hovering over: {event.xdata} age group')\n\nfig.canvas.mpl_connect('button_press_event', on_click)\nfig.canvas.mpl_connect('motion_notify_event', hover)\n\nplt.show()"
    # for _ in range(5):
    executor = PythonExecutor(code=test_code, debug=True)
    output = None
    try:
        output = executor.main()
    except ExecutionError as e:
        print(e.err)

    del executor
    if output is not None:
        with open("output.html", "w") as f:
            f.write(output)
