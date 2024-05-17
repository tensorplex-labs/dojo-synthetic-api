import asyncio
import subprocess
import json
import time
from typing import Annotated

from loguru import logger


class CodeDiagnostics:
    @staticmethod
    async def diagnostics(
        code_to_analyze: Annotated[str, "Code to be analyzed"],
    ) -> str:
        diagnostics = ""
        # disabled quicklint for now because trying to figure out if tsserver is better
        # ql_diag = await diagnostics_quicklint(code_to_analyze)
        tsserver_diag = tsserver_diagnostics(code=code_to_analyze)
        if tsserver_diag:
            diagnostics += "\n".join(tsserver_diag)
        # diagnostics += ql_diag
        return diagnostics


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
    file_path = "/path/to/nonexistent/file.js"

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
        parse_diagnostics(response)

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
