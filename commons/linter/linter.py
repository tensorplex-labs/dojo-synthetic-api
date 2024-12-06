import os
import subprocess
import tempfile

# class JavaScriptLinter:
#     """A Python class to lint JavaScript code using ESLint."""

#     def __init__(self, eslint_path: str | None = None):
#         """
#         Initialize the linter.

#         Args:
#             eslint_path: Optional path to eslint executable. If None, will try to find it automatically.
#         """
#         self.eslint_path = eslint_path or self._find_eslint()

#     def _find_eslint(self) -> str:
#         """Find the ESLint executable."""
#         # Try common locations
#         possible_paths = [
#             "eslint",  # If in PATH
#             "./node_modules/.bin/eslint",  # Local installation
#             "../node_modules/.bin/eslint",  # One level up
#         ]

#         for path in possible_paths:
#             try:
#                 # Check if eslint is available
#                 subprocess.run([path, "--version"], capture_output=True, text=True)
#                 return path
#             except (subprocess.SubprocessError, FileNotFoundError):
#                 continue

#         raise RuntimeError(
#             "ESLint not found. Please install it using 'npm install eslint' "
#             "or provide the path to the eslint executable."
#         )

#     def lint_code(self, code: str) -> Dict:
#         """
#         Lint JavaScript code and return the results.

#         Args:
#             code: JavaScript code as a string.

#         Returns:
#             Dict containing lint results with errors and warnings.
#         """
#         # Create a temporary file to store the code
#         with tempfile.NamedTemporaryFile(
#             mode="w", suffix=".js", delete=False
#         ) as temp_file:
#             temp_file.write(code)
#             temp_file_path = temp_file.name

#         try:
#             # Run ESLint on the temporary file
#             result = subprocess.run(
#                 [
#                     self.eslint_path,
#                     "-f",
#                     "json",
#                     "--no-eslintrc",  # Don't use local config
#                     "--env",
#                     "es2022,node",
#                     temp_file_path,
#                 ],
#                 capture_output=True,
#                 text=True,
#             )

#             # Parse the JSON output
#             try:
#                 lint_results = json.loads(result.stdout or "[]")
#             except json.JSONDecodeError:
#                 return {
#                     "success": False,
#                     "error": "Failed to parse ESLint output",
#                     "raw_output": result.stdout,
#                 }

#             # Format the results
#             if lint_results and isinstance(lint_results, list):
#                 file_result = lint_results[0]
#                 return {
#                     "success": True,
#                     "error_count": file_result.get("errorCount", 0),
#                     "warning_count": file_result.get("warningCount", 0),
#                     "messages": [
#                         {
#                             "line": msg.get("line"),
#                             "column": msg.get("column"),
#                             "severity": "error"
#                             if msg.get("severity") == 2
#                             else "warning",
#                             "message": msg.get("message"),
#                             "rule": msg.get("ruleId"),
#                         }
#                         for msg in file_result.get("messages", [])
#                     ],
#                 }

#             return {
#                 "success": True,
#                 "error_count": 0,
#                 "warning_count": 0,
#                 "messages": [],
#             }

#         except subprocess.SubprocessError as e:
#             return {"success": False, "error": f"ESLint execution failed: {str(e)}"}

#         finally:
#             # Clean up the temporary file
#             try:
#                 os.unlink(temp_file_path)
#             except OSError:
#                 pass


# def setup_linting():
#     """Set up the linting environment by ensuring ESLint is installed."""
#     try:
#         # Check if npm is available
#         subprocess.run(["npm", "--version"], capture_output=True, check=True)

#         # Install ESLint locally if not present
#         subprocess.run(["npm", "install", "eslint"], capture_output=True, check=True)
#         return True
#     except subprocess.SubprocessError as e:
#         print(f"Failed to set up linting environment: {e}")
#         return False


def main():
    # linter = JavaScriptLinter()

    # print(linter.lint_code("console.log('Hello, world!');"))
    sample_code = """
    console.log('Hello, world!'
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as temp_file:
        temp_file.write(sample_code)
        temp_file_path = temp_file.name
        print(temp_file_path)
    try:
        result = subprocess.run(
            ["npx", "eslint", temp_file_path], capture_output=True, check=True
        )
        print(result.stdout.decode("utf-8"))
    except Exception as e:
        print(f"Failed to set up linting environment: {e}")
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


if __name__ == "__main__":
    main()
