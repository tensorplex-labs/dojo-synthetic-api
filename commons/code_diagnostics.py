import asyncio
import subprocess
import json
import time
from typing import Annotated

from loguru import logger
import uuid


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
        logger.info(f"Got code diagnostics: {diagnostics}")
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


CONFIGURE = "configure"
OPEN = "open"
CHANGE = "change"
GETERR = "geterr"
SEMANTIC_DIAGNOSTICS_SYNC = "semanticDiagnosticsSync"
SYNTACTIC_DIAGNOSTICS_SYNC = "syntacticDiagnosticsSync"
SUGGESTION_DIAGNOSTICS_SYNC = "suggestionDiagnosticsSync"


def tsserver_diagnostics(code: str):
    process = start_tsserver()

    # Initialize the project
    send_command(
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
    send_command(
        process,
        {
            "seq": 1,
            "type": "request",
            "command": OPEN,
            "arguments": {"file": file_path},
        },
    )

    # Send the content of the JavaScript as a change to the opened file
    send_command(
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
    send_command(
        process,
        {
            "seq": 3,
            "type": "request",
            "command": GETERR,
            "arguments": {"files": [file_path], "delay": 0},
        },
    )

    # Request semantic diagnostics
    send_command(
        process,
        {
            "seq": 4,
            "type": "request",
            "command": SEMANTIC_DIAGNOSTICS_SYNC,
            "arguments": {"file": file_path},
        },
    )

    # Request syntactic diagnostics
    send_command(
        process,
        {
            "seq": 5,
            "type": "request",
            "command": SYNTACTIC_DIAGNOSTICS_SYNC,
            "arguments": {"file": file_path},
        },
    )

    # Request suggestion diagnostics
    send_command(
        process,
        {
            "seq": 6,
            "type": "request",
            "command": SUGGESTION_DIAGNOSTICS_SYNC,
            "arguments": {"file": file_path},
        },
    )

    # TODO handle multiple responses
    responses = read_response(process)

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
    formatted_diagnostics = []
    logger.info(f"Raw response: {response=}")
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
                                f"Error {item['code']}: {text} at line {item['start']['line']}, column {item['start']['offset']}"
                            )
                        elif event == "suggestionDiag":
                            formatted_diagnostics.append(
                                f"Suggestion {item['code']}: {text} at line {item['start']['line']}, column {item['start']['offset']}"
                            )
                        elif event == "syntaxDiag":
                            formatted_diagnostics.append(
                                f"Syntax {item['category']}, code - {item['code']}: {text} at line {item['start']['line']}, column {item['start']['offset']} to line {item['end']['line']}, column {item['end']['offset']}"
                            )
                    elif isinstance(item, str):
                        formatted_diagnostics.append(item)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON")
    except Exception as e:
        logger.error(f"Error occurred: {e}")

    logger.info(f"Successfully parsed diagnostics\n{formatted_diagnostics=}")
    return formatted_diagnostics
