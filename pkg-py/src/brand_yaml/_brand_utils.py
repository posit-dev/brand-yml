from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from typing import TypeVar, Generic

T = TypeVar('T')  # Define a type variable T

class BrandLightDark(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    light: T = None
    dark: T = None

class BrandStringLightDark(BrandLightDark[str]):
    pass


class BrandWith(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    with_: dict[str, T] = None
