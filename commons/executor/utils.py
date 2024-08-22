import ast
from sys import stdlib_module_names

from dotenv import load_dotenv

load_dotenv()


class ExecutionError(Exception):
    def __init__(self, err: str, code: str) -> None:
        self.err = err
        self.code = code


def get_packages(code: str) -> set[str]:
    replaced_code = code.replace("\\n", "\n").replace("\\t", "\t")
    modules = set()

    def visit_import(node):
        for name in node.names:
            modules.add(name.name.split(".")[0])

    def visit_importfrom(node):
        # if node.module is missing it's a "from . import ..." statement
        # if level > 0 it's a "from .submodule import ..." statement
        if node.module is not None and node.level == 0:
            modules.add(node.module.split(".")[0])

    node_iter = ast.NodeVisitor()
    node_iter.visit_Import = visit_import
    node_iter.visit_ImportFrom = visit_importfrom

    try:
        node_iter.visit(ast.parse(replaced_code))
    except SyntaxError as err:
        print("Syntax Error in", code)
        raise ExecutionError(str(err), code) from err

    # return modules not part of the standard library
    return modules - stdlib_module_names
