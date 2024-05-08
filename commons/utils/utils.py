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
