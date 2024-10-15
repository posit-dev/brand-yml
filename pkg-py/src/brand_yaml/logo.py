"""
Brand Logos

Pydantic models for the brand's logos, stored adjacent to the `_brand.yml` file
or online, possibly with light or dark variants.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Union

from pydantic import (
    ConfigDict,
    Discriminator,
    Tag,
    model_validator,
)

from ._defs import BrandLightDark, defs_replace_recursively
from ._utils_docs import add_example_yaml
from .base import BrandBase
from .file import FileLocation, FileLocationLocalOrUrlType

BrandLogoFileType = Annotated[
    Union[
        Annotated[FileLocationLocalOrUrlType, Tag("file")],
        Annotated[
            BrandLightDark[FileLocationLocalOrUrlType], Tag("light-dark")
        ],
    ],
    Discriminator(
        lambda x: "light-dark"
        if isinstance(x, (dict, BrandLightDark))
        else "file"
    ),
]
"""
A logo image file can be either a local or URL file location, or a light-dark
variant that includes both a light and dark color scheme.
"""


@add_example_yaml(
    {"path": "brand-logo-single.yml", "name": "Single Logo"},
    {"path": "brand-logo-simple.yml", "name": "Minimal"},
    {"path": "brand-logo-light-dark.yml", "name": "Light/Dark Variants"},
    {"path": "brand-logo-full.yml", "name": "Complete"},
)
class BrandLogo(BrandBase):
    """
    Brand Logos

    `logo` stores a single brand logo or a set of logos at three different size
    points and possibly in different color schemes. Store all logo or image
    assets in `images` with meaningful names. Logos can be specified at three
    different sizes -- `small`, `medium`, and `large` -- and each can be either
    a single logo file or a light/dark variant (`brand_yaml.BrandLightDark`).

    Attributes
    ----------

    images
        A dictionary containing any number of logos or brand images. You can
        refer to these images by their key name in `small`, `medium` or `large`.
        Local file paths should be relative to the `_brand.yml` source file.
        Remote files are also permitted; please use a full URL to the image.

        ```yaml
        logo:
          images:
            white: pandas_white.svg
            white_online: "https://upload.wikimedia.org/wikipedia/commons/e/ed/Pandas_logo.svg"
          small: white
        ```

    small
        A small logo, typically used as an favicon or mobile app icon.

    medium
        A medium-sized logo, typically used in the header of a website.

    large
        A large logo, typically used in a larger format such as a title slide
        or in marketing materials.
    """

    model_config = ConfigDict(extra="forbid")

    images: dict[str, FileLocationLocalOrUrlType] | None = None
    small: BrandLogoFileType | None = None
    medium: BrandLogoFileType | None = None
    large: BrandLogoFileType | None = None

    @model_validator(mode="before")
    @classmethod
    def _resolve_image_values(cls, data: Any):
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        if "images" not in data:
            return data

        images = data["images"]
        if images is None:
            return data

        if not isinstance(images, dict):
            raise ValueError("images must be a dictionary of file locations")

        for key, value in images.items():
            if not isinstance(value, (str, FileLocation, Path)):
                raise ValueError(f"images[{key}] must be a file location")

        defs_replace_recursively(data, defs=images, name="logo")

        return data
