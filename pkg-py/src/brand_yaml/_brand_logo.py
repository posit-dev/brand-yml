from __future__ import annotations

from typing import Union

from pydantic import ConfigDict
from ._brand_utils import BrandLightDarkString, BrandWith

class BrandLogo(BrandWith[Union[str, BrandLightDarkString]]):
    """
    Brand Logos

    `logo` stores a single brand logo or a set of logos in different sizes and
    possibly in different color schemes.

    Attributes:

    small
    :    A small logo, typically used as an favicon or mobile app icon.
    
    medium
    :    A medium-sized logo, typically used in the header of a website.

    large
    :    A large logo, typically used in a larger format such as a title slide
        or in marketing materials.
    """
    model_config = ConfigDict(extra="ignore")

    # TODO: Currently we're using a string for the logo path, but we should
    # update this to use a validated Path or URL in the future.
    small: str | BrandLightDarkString = None
    medium: str | BrandLightDarkString = None
    large: str | BrandLightDarkString = None

