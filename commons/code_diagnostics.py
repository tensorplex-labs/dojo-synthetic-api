import asyncio
import json
import time
import uuid
from typing import Annotated

from loguru import logger

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
            logger.info(f"Code to analyze: {code_to_analyze}")
            # disabled quicklint for now because trying to figure out if tsserver is better
            # ql_diag = await diagnostics_quicklint(code_to_analyze)
            tsserver_diag = await tsserver_diagnostics(code=code_to_analyze)
            if tsserver_diag:
                diagnostics += "\n".join(tsserver_diag)
            # diagnostics += ql_diag
            logger.info(f"Got code diagnostics: {diagnostics}")
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


CONFIGURE = "configure"
OPEN = "open"
CHANGE = "change"
GETERR = "geterr"
SEMANTIC_DIAGNOSTICS_SYNC = "semanticDiagnosticsSync"
SYNTACTIC_DIAGNOSTICS_SYNC = "syntacticDiagnosticsSync"
SUGGESTION_DIAGNOSTICS_SYNC = "suggestionDiagnosticsSync"


async def tsserver_diagnostics(code: str):
    process = await start_tsserver()

    # Initialize the project
    await send_command(
        process,
        {
            "seq": 0,
            "type": "request",
            "command": CONFIGURE,
            "arguments": {"hostInfo": "python"},
        },
    )

    # Simulated file path
    filename = str(uuid.uuid4()).replace("-", "")
    file_path = f"/path/to/nonexistent/{filename}.js"

    # Open a fake file in tsserver
    await send_command(
        process,
        {
            "seq": 1,
            "type": "request",
            "command": OPEN,
            "arguments": {"file": file_path},
        },
    )

    # Send the content of the JavaScript as a change to the opened file
    await send_command(
        process,
        {
            "seq": 2,
            "type": "request",
            "command": CHANGE,
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

    # Request diagnostics
    await send_command(
        process,
        {
            "seq": 3,
            "type": "request",
            "command": GETERR,
            "arguments": {"files": [file_path], "delay": 0},
        },
    )

    # Request semantic diagnostics
    await send_command(
        process,
        {
            "seq": 4,
            "type": "request",
            "command": SEMANTIC_DIAGNOSTICS_SYNC,
            "arguments": {"file": file_path},
        },
    )

    # Request syntactic diagnostics
    await send_command(
        process,
        {
            "seq": 5,
            "type": "request",
            "command": SYNTACTIC_DIAGNOSTICS_SYNC,
            "arguments": {"file": file_path},
        },
    )

    # Request suggestion diagnostics
    await send_command(
        process,
        {
            "seq": 6,
            "type": "request",
            "command": SUGGESTION_DIAGNOSTICS_SYNC,
            "arguments": {"file": file_path},
        },
    )

    # TODO handle multiple responses
    responses = await read_response(process)

    # Give tsserver some time to process and emit diagnostics
    time.sleep(3)

    logger.info(f"Read response from tsserver LSP: \n{responses=}")
    # if not response.strip():
    #     break
    logger.info("Attempting to parse diagnostics...")
    diagnostics = parse_diagnostics(responses)
    logger.info(f"Parsed diagnostics: {diagnostics=}")

    # Close the tsserver
    process.terminate()
    return diagnostics


async def start_tsserver():
    return await asyncio.create_subprocess_exec(
        "tsserver",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        universal_newlines=False,
    )


async def send_command(process, command):
    process.stdin.write((json.dumps(command) + "\n").encode("utf-8"))
    await process.stdin.drain()


async def read_response(process: asyncio.subprocess.Process):
    responses = []
    content_length = 0

    while True:
        try:
            line = await asyncio.wait_for(process.stdout.readline(), timeout=2)
            line = line.strip().decode("utf-8")
            print("line", line)
            if line.startswith("Content-Length:"):
                content_length = int(line.split(":")[1].strip())
            elif line == "":
                if content_length > 0:
                    response = await process.stdout.read(content_length)
                    responses.append(response)
                    content_length = 0  # Reset for the next message
            else:
                continue
        except asyncio.TimeoutError:
            logger.info("Timeout reading response")
            break

    return responses


def parse_diagnostics(responses):
    formatted_diagnostics = []
    logger.info(f"Raw response: {responses=}")
    for response in responses:
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
                                formatted_diagnostics.append(
                                    f"Error: {text} at line {item['start']['line']}, column {item['start']['offset']}"
                                )
                            elif event == "suggestionDiag":
                                formatted_diagnostics.append(
                                    f"Suggestion: {text} at line {item['start']['line']}, column {item['start']['offset']}"
                                )
                            elif event == "syntaxDiag":
                                formatted_diagnostics.append(
                                    f"Syntax {item['category']}: {text} at line {item['start']['line']}, column {item['start']['offset']} to line {item['end']['line']}, column {item['end']['offset']}"
                                )
                        elif isinstance(item, str):
                            formatted_diagnostics.append(item)
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
        except Exception as e:
            logger.error(f"Error occurred: {e}")

    logger.info(f"Successfully parsed diagnostics\n{formatted_diagnostics=}")
    return formatted_diagnostics
