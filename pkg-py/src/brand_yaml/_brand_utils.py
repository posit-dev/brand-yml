from __future__ import annotations

from pydantic import GenericModel, ConfigDict
from typing import TypeVar

T = TypeVar('T')  # Define a type variable T

class BrandLightDark(GenericModel[T]):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    light: T = None
    dark: T = None

class BrandStringLightDark(BrandLightDark[str]):
    pass
