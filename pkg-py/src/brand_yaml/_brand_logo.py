from __future__ import annotations

from typing import Union

from pydantic import ConfigDict
from ._brand_utils import BrandStringLightDark, BrandWith

class BrandLogo(BrandWith[Union[str, BrandStringLightDark]]):
    model_config = ConfigDict(extra="forbid")

    small: str | BrandStringLightDark = None
    medium: str | BrandStringLightDark = None
    large: str | BrandStringLightDark = None

