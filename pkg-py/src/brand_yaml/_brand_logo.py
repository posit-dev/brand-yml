from __future__ import annotations

from typing import Union

from pydantic import ConfigDict
from ._brand_utils import BrandLightDarkString, BrandWith

class BrandLogo(BrandWith[Union[str, BrandLightDarkString]]):
    model_config = ConfigDict(extra="forbid")

    small: str | BrandLightDarkString = None
    medium: str | BrandLightDarkString = None
    large: str | BrandLightDarkString = None

