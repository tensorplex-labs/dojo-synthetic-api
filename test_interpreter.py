from e2b import Sandbox, ProcessOutput
from e2b_code_interpreter import CodeInterpreter
from dotenv import load_dotenv
import base64
from dotenv import load_dotenv
from anthropic import Anthropic
from typing import List, Tuple
from e2b_code_interpreter import CodeInterpreter, Result
from e2b_code_interpreter.models import Logs
import openai
from dotenv import load_dotenv

load_dotenv()

code = "console.log('hello, world!')"


async def main():
    sandbox = Sandbox()
    sandbox.filesystem.write("/home/user/index.js", code)
    proc: ProcessOutput = sandbox.process.start_and_wait("node /home/user/index.js")
    print("stdout", proc.stdout)
    print("stderr", proc.stderr)

    sandbox.close()


import asyncio

asyncio.run(main())
