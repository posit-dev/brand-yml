from __future__ import annotations

from typing import Annotated, Any, Union

from pydantic import (
    ConfigDict,
    Discriminator,
    Tag,
    model_validator,
)

from ._defs import BrandLightDark, defs_replace_recursively
from ._path import FileLocationLocalOrUrl
from .base import BrandBase

BrandLogoFileType = Annotated[
    Union[
        Annotated[FileLocationLocalOrUrl, Tag("file")],
        Annotated[BrandLightDark[FileLocationLocalOrUrl], Tag("light-dark")],
    ],
    Discriminator(
        lambda x: "light-dark"
        if isinstance(x, (dict, BrandLightDark))
        else "file"
    ),
]


class BrandLogo(BrandBase):
    """
    Brand Logos

    `logo` stores a single brand logo or a set of logos in different sizes and
    possibly in different color schemes.

    Attributes
    ----------

    small
        A small logo, typically used as an favicon or mobile app icon.

    medium
        A medium-sized logo, typically used in the header of a website.

    large
        A large logo, typically used in a larger format such as a title slide
        or in marketing materials.

    """

    model_config = ConfigDict(
        extra="forbid",
        use_attribute_docstrings=True,
    )

    images: dict[str, FileLocationLocalOrUrl] | None = None
    small: BrandLogoFileType | None = None
    medium: BrandLogoFileType | None = None
    large: BrandLogoFileType | None = None

    @model_validator(mode="before")
    @classmethod
    def resolve_image_values(cls, data: Any):
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
            if not isinstance(value, (str, FileLocationLocalOrUrl)):
                raise ValueError(f"images[{key}] must be a file location")

        defs_replace_recursively(data, defs=images, name="logo")

        return data
