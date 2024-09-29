import inspect
import json
from typing import Annotated, Callable, get_args, get_origin

from pydantic import BaseModel, Field, create_model


def get_function_signature(func: Callable) -> str:
    """Get only the required parameters in function signature, and the return type"""
    signature = inspect.signature(func)
    required_params = [
        param
        for param in signature.parameters.values()
        if param.default == inspect.Parameter.empty
    ]
    param_str = ", ".join(str(param) for param in required_params)
    return_str = (
        f" -> {signature.return_annotation.__name__}"
        if signature.return_annotation != inspect.Signature.empty
        else ""
    )
    return f"({param_str}){return_str}"


def func_to_pydantic_model(func: Callable) -> BaseModel:
    signature = inspect.signature(func)

    model_name = f"{func.__name__.capitalize()}Model"
    # Get a list of all parameters and their types
    model_props = []
    for param_name, param in signature.parameters.items():
        param_type = (
            param.annotation
            if param.annotation != inspect.Parameter.empty
            else type(None)
        )

        description = ""
        default = ...  # use ellipsis as a sentinel value
        if get_origin(param_type) is Annotated:
            param_type, *metadata = get_args(param_type)
            if metadata and isinstance(metadata[0], str):
                description = metadata[0]

        if param.default != inspect.Parameter.empty:
            default = param.default

        model_props.append(
            (param_name, param_type, Field(default=default, description=description))
        )

    from loguru import logger

    logger.debug(f"Inferred properties from function: {model_props}")
    dynamic_model = create_model(  # type: ignore
        model_name,
        **{  # type: ignore
            property_name: (property_type, field)
            for property_name, property_type, field in model_props
        },
    )
    return dynamic_model


def func_to_schema(func: Callable):
    """Given a function, return a JSON schema to prepare for tool calling"""
    signature = inspect.signature(func)

    schema = {"type": "object", "properties": {}, "required": []}

    for param_name, param in signature.parameters.items():
        param_type = (
            param.annotation
            if param.annotation != inspect.Parameter.empty
            else type(param.default)
        )

        if param_type is str:
            schema["properties"][param_name] = {"type": "string"}
        elif param_type is int:
            schema["properties"][param_name] = {"type": "integer"}
        elif param_type is float:
            schema["properties"][param_name] = {"type": "number"}
        elif param_type is bool:
            schema["properties"][param_name] = {"type": "boolean"}
        elif param_type is list:
            schema["properties"][param_name] = {"type": "array"}
        elif param_type is dict:
            schema["properties"][param_name] = {"type": "object"}
        else:
            schema["properties"][param_name] = {"type": "any"}

        # Add default value if present
        if param.default != inspect.Parameter.empty:
            schema["properties"][param_name]["default"] = param.default

        if param.default == inspect.Parameter.empty:
            schema["required"].append(param_name)

    return json.dumps(schema, indent=2)
