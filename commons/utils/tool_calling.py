import inspect
import json
from typing import Annotated, Callable, Union, get_args, get_origin

from loguru import logger
from pydantic import BaseModel, Field, create_model


def get_function_signature(func: Callable) -> str:
    """
    Returns a string representation of the function signature.
    """
    logger.debug(f"Getting function signature for {func}")
    signature = inspect.signature(func)
    params = []
    for name, param in signature.parameters.items():
        param_type = param.annotation
        if param_type is inspect.Parameter.empty:
            param_type_str = "Any"
        else:
            param_type_str = _get_type_name(param_type)
        params.append(f"{name}: {param_type_str}")

    return_annotation = signature.return_annotation
    if return_annotation is inspect.Signature.empty:
        return_annotation_str = "Any"
    else:
        return_annotation_str = _get_type_name(return_annotation)

    return f"({', '.join(params)}) -> {return_annotation_str}"


def _get_type_name(tp):
    """
    Returns the name of the type, handling Union and other special cases.
    """
    origin = get_origin(tp)
    if origin is None:
        return getattr(tp, "__name__", str(tp))
    elif origin is Union:
        args = get_args(tp)
        return f"Union[{', '.join(_get_type_name(arg) for arg in args)}]"
    else:
        return str(tp)


def func_to_pydantic_model(func: Callable) -> BaseModel:
    """Generate a pydantic model dynamically from a function's signature"""

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

    logger.trace(f"Inferred properties from function: {model_props}")
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
