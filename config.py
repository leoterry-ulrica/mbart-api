import os
from typing import Optional

import dotenv
from pydantic import BaseModel, Field

from compatibility import disable_warnings

dotenv.load_dotenv()

disable_warnings(BaseModel)

def get_bool_env(key, default="false"):
    return os.environ.get(key, default).lower() == "true"


def get_env(key, default):
    val = os.environ.get(key, "")
    return val or default


class Settings(BaseModel):
    """ Settings class. """
        
    # device related
    device: Optional[str] = Field(
        default=get_env("DEVICE", "cuda"),
        description="Device to load the model."
    )
    
    # model path
    model_path: Optional[str] = Field(
        default=get_env("MODEL_PATH", "facebook/mbart-large-50-many-to-many-mmt"),
        description="The model path."
    )
