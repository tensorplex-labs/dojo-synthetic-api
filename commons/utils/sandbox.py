import importlib
import logging
import os
import uuid

from RestrictedPython import compile_restricted
from RestrictedPython.Eval import default_guarded_getitem
from RestrictedPython.Guards import safe_builtins

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def execute_code_sandboxed(code: str) -> tuple[str | None, str | None]:
    """
    Executes the code using RestrictedPython and returns the path to the generated file.
    """
    # Define the directory and file path
    output_dir = "./temp/data"
    unique_file_name = f"{uuid.uuid4()}.html"
    file_path = os.path.join(output_dir, unique_file_name)

    try:
        compiled_code = compile_restricted(code, filename="<inline>", mode="exec")

        # Create a safe globals dictionary
        safe_globals = {
            "__builtins__": safe_builtins,
            "_getitem_": default_guarded_getitem,
            "output_file_path": file_path,
        }

        # Add the required modules to the safe globals dictionary
        add_module_to_safe_globals("bokeh.plotting", safe_globals)
        add_module_to_safe_globals("bokeh.models", safe_globals)
        add_module_to_safe_globals("bokeh.layouts", safe_globals)
        add_module_to_safe_globals("bokeh.transform", safe_globals)
        add_module_to_safe_globals("bokeh.palettes", safe_globals)
        add_module_to_safe_globals("bokeh.embed", safe_globals)
        add_module_to_safe_globals("numpy", safe_globals, "np")

        # Execute the compiled code
        exec(compiled_code, safe_globals)
        logger.info(f"Code executed successfully, output file: {file_path}")
        return file_path, unique_file_name
    except Exception as e:
        logger.error(f"Failed to execute code: {e}", exc_info=True)
        return None, None


def add_module_to_safe_globals(module_name, safe_globals, alias=None):
    """
    Imports a module and adds all its functions to the safe_globals dictionary.
    Optionally, an alias can be used to reference the module.
    """
    module = importlib.import_module(module_name)
    if alias:
        safe_globals[alias] = module
    else:
        for name, func in module.__dict__.items():
            if callable(func):
                safe_globals[name] = func
