"""
linter.py:
  - enables use of ESLint library to lint input javascript code
  - will lint according to the rules specified in eslint.config.mjs
  - used in synthetic.py to trigger LLM queries to fix syntax errors when detected.
"""

import subprocess

from loguru import logger
from pydantic import BaseModel, Field


class LintResult(BaseModel):
    return_code: int = Field(description="status code returned from ESLint")
    output: str = Field(description="stdout messages from ESLint")
    error: str = Field(description="stderr messages from ESLint")
    input: str = Field(description="input code passed to ESLint")


def setup_linting():
    """Set up the linting environment by ensuring ESLint is installed."""
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], capture_output=True, check=True)

        # Install ESLint locally if not present
        subprocess.run(["npm", "install", "eslint"], capture_output=True, check=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Failed to set up linting environment: {e}")
        return False


def lint_code(code: str, id: str) -> LintResult:
    """
    calls ESLint on the input code and returns the result as a LintResult object.
    """
    try:
        # Check if eslint is installed
        npm_check = subprocess.run(
            ["npm", "list", "eslint"],
            capture_output=True,
            text=True,
            check=False,
        )
        if npm_check.returncode != 0:
            setup_linting()
        result = subprocess.run(
            [
                "npx",
                "eslint",
                "--quiet",  # only report errors, ignore warnings
                "--stdin",  # read from stdin instead of default behaviour of files
            ],
            input=code,
            capture_output=True,
            text=True,
            check=False,
        )

        return LintResult(
            return_code=result.returncode,
            output=result.stdout,
            error=result.stderr,
            input=code,
        )
    except Exception as e:
        logger.error(f"Error linting answer {id}: {e}")
        return LintResult(
            return_code=0,
            output="",
            error=str(e),
            input=code,
        )


def main():
    """
    main function used to for isolated testing of linter.py
    """
    print(setup_linting())

    bad_code = """
    const fuck = ["citizen", "resident", 'smile's', "undocumented"]
    """
    lint_code(bad_code, "test")


if __name__ == "__main__":
    main()
