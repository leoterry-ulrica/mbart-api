import pydantic
from typing import Type

# --------------- Pydantic v2 compatibility ---------------

PYDANTIC_V2 = pydantic.VERSION.startswith("2.")

def disable_warnings(model: Type[pydantic.BaseModel]):
    # Disable warning for model_name settings
    if PYDANTIC_V2:
        model.model_config["protected_namespaces"] = ()