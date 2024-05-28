import sys
sys.path.append("./")
import asyncio
import subprocess
import json
import time
from typing import Annotated

from loguru import logger
import uuid
from commons.utils.python_executor import PythonExecutor


class CodeDiagnostics:
    @staticmethod
    async def diagnostics(
        code_to_analyze: Annotated[str, "Code to be analyzed"],
        language: Annotated[str, "Language of the code"],
    ) -> str:
        if language == "python":
            executor = PythonExecutor(code=code_to_analyze)
            try:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, executor.main)
            except Exception as e:
                logger.error(f"Error occurred while executing Python code: {e}")
                return str(e)
        else:            
            diagnostics = ""
            # disabled quicklint for now because trying to figure out if tsserver is better
            # ql_diag = await diagnostics_quicklint(code_to_analyze)
            tsserver_diag = tsserver_diagnostics(code=code_to_analyze)
            if tsserver_diag:
                diagnostics += "\n".join(tsserver_diag)
            # diagnostics += ql_diag
            return diagnostics
        
test_code = """
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

# Read CSV file
df = pd.read_csv('categories.csv')

# Create the bar chart
plt.bar(df.columns, df.iloc[0])
plt.title('Category Frequencies')
plt.xlabel('Category')
plt.ylabel('Frequency')

# Set up slider
ax_slider = plt.axes([0.7, 0.1, 0.2, 0.03])
slider = widgets.Slider(ax_slider, 'Slider', valmin=0, valmax=100)
slider.on_changed(update)

def update(val):
    filtered_df = df.iloc[:, :int(slider.val)]
    plt.bar(df.columns, filtered_df.iloc[0])
    plt.draw_idle()

# Set up hover functionality
def hover(event):
    if event.inaxes == plt.gca():
        x, y = event.xdata, event.ydata
        frequency = df.iloc[0].iloc[int(x)]
        plt.gca().set_title(f'Category Frequencies Hovered frequency: {frequency}')
        plt.draw_idle()

fig = plt.gcf()
fig.canvas.mpl_connect('motion_notify_event', hover)

# Set up reset button
ax_button = plt.axes([0.7, 0.05, 0.2, 0.03])
button = widgets.Button(ax_button, 'Reset')
button.on_clicked(reset)

def reset(event):
    plt.bar(df.columns, df.iloc[0])
    slider.set_val(50)
    plt.draw_idle()

# Customize chart appearance
plt.xlabel('Category', fontsize=14, fontweight='bold')
plt.ylabel('Frequency', fontsize=14, fontweight='bold')
plt.legend()
plt.show()
"""

if __name__ == "__main__":
    code_diagnostics = CodeDiagnostics()
    print(asyncio.run(code_diagnostics.diagnostics(test_code, "python")))


############################# QUICKLINT ######################################
async def diagnostics_quicklint(
    code_to_analyze: Annotated[str, "Code to be analyzed"],
) -> str:
    try:
        process = await asyncio.create_subprocess_exec(
            "quick-lint-js",
            "--stdin",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate(input=code_to_analyze.encode())

        if process.returncode == 0:
            return stdout.decode()
        else:
            return f"Error occurred: {stderr.decode()}"
    except Exception as e:
        return f"Exception occurred: {e}"


############################# TSSERVER ######################################


def tsserver_diagnostics(code: str):
    process = start_tsserver()

    # Initialize the project
    send_command(
        process,
        {
            "seq": 0,
            "type": "request",
            "command": "configure",
            "arguments": {"hostInfo": "python"},
        },
    )
    read_response(process)

    # Simulated file path
    filename = uuid.uuid4().replace("-", "")
    file_path = f"/path/to/nonexistent/{filename}.js"

    # Open a fake file in tsserver
    send_command(
        process,
        {
            "seq": 1,
            "type": "request",
            "command": "open",
            "arguments": {"file": file_path},
        },
    )
    read_response(process)

    # Send the content of the JavaScript as a change to the opened file
    send_command(
        process,
        {
            "seq": 2,
            "type": "request",
            "command": "change",
            "arguments": {
                "file": file_path,
                "line": 1,
                "offset": 1,
                "endLine": 1,
                "endOffset": 1,
                "insertString": code,
            },
        },
    )
    read_response(process)

    # Request diagnostics
    send_command(
        process,
        {
            "seq": 3,
            "type": "request",
            "command": "geterr",
            "arguments": {"files": [file_path], "delay": 0},
        },
    )

    # Give tsserver some time to process and emit diagnostics
    time.sleep(1)

    # Read the responses containing diagnostics
    while True:
        response = read_response(process)
        if not response.strip():
            break
        diagnostics = parse_diagnostics(response)
        logger.info(f"diagnostics: {diagnostics}")

    # Close the tsserver
    process.terminate()


def start_tsserver():
    return subprocess.Popen(
        ["tsserver"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )


def send_command(process, command):
    process.stdin.write(json.dumps(command) + "\n")
    process.stdin.flush()


def read_response(process):
    response = ""
    content_length = 0

    while True:
        line = process.stdout.readline().strip()
        if line.startswith("Content-Length:"):
            content_length = int(line.split(":")[1].strip())
        elif line == "":
            if content_length > 0:
                response = process.stdout.read(content_length)
                break
        else:
            continue

    return response


def parse_diagnostics(response):
    diagnostics = []
    try:
        messages = json.loads(response)
        if messages.get("type") == "event":
            event = messages.get("event")
            if event in ["semanticDiag", "syntaxDiag", "suggestionDiag"]:
                diagnostics = messages.get("body", {}).get("diagnostics", [])
                for item in diagnostics:
                    if isinstance(item, dict):
                        category = item["category"]
                        text = item["text"]
                        if category == "error":
                            diagnostics.append(
                                f"Error {item['code']}: {text} at line {item['start']['line']}, column {item['start']['offset']}"
                            )
                        elif event == "suggestionDiag":
                            diagnostics.append(
                                f"Suggestion {item['code']}: {text} at line {item['start']['line']}, column {item['start']['offset']}"
                            )
                    elif isinstance(item, str):
                        diagnostics.append(item)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON")
        return diagnostics
    logger.success(f"Successfully parsed diagnostics\n{diagnostics=}")
    return diagnostics
