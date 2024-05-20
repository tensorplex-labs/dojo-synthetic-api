import ast
from sys import stdlib_module_names
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


def generate_simple_json(model: BaseModel) -> dict:
    schema = model.model_json_schema()
    descriptions = {
        field: schema["properties"][field]["description"]
        for field in schema["properties"]
    }
    return descriptions

def get_packages(code : str):
    replaced_code = code.replace('\\n', '\n').replace('\\t', '\t')
    modules = set()
    
    def visit_Import(node):
        for name in node.names:
            modules.add(name.name.split(".")[0])

    def visit_ImportFrom(node):
        # if node.module is missing it's a "from . import ..." statement
        # if level > 0 it's a "from .submodule import ..." statement
        if node.module is not None and node.level == 0:
            modules.add(node.module.split(".")[0])
            
    node_iter = ast.NodeVisitor()
    node_iter.visit_Import = visit_Import
    node_iter.visit_ImportFrom = visit_ImportFrom
    
    try:
        node_iter.visit(ast.parse(replaced_code))
    except SyntaxError as e:
        print("Syntax Error in", code)
        print(replaced_code)
        raise e
    
    # return modules not part of the standard library
    return modules - stdlib_module_names