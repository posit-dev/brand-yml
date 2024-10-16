import json
import os
from contextlib import contextmanager
from pathlib import Path

from pydantic import BaseModel


def path_examples(*args) -> Path:
    repo_root = Path(__file__).parent.parent.parent.parent
    return repo_root / "examples" / Path(*args)


def pydantic_data_from_json(model: BaseModel) -> dict:
    data = model.model_dump_json(
        by_alias=True,
        indent=2,
        exclude_unset=True,
        exclude_none=True,
    )
    return json.loads(data)


@contextmanager
def set_env_var(key, value):
    # Store the original value
    original_value = os.environ.get(key)
    # Set the new value
    os.environ[key] = value
    try:
        yield
    finally:
        # Restore the original value
        if original_value is not None:
            os.environ[key] = original_value
        else:
            del os.environ[key]
