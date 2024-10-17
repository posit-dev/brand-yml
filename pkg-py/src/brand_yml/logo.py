"""
Brand Logos

Pydantic models for the brand's logos, stored adjacent to the `_brand.yml` file
or online, possibly with light or dark variants.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal, Union

from pydantic import (
    AnyUrl,
    ConfigDict,
    Discriminator,
    Tag,
    field_validator,
    model_validator,
)

from ._defs import BrandLightDark, defs_replace_recursively
from ._utils_docs import add_example_yaml
from .base import BrandBase
from .file import FileLocation, FileLocationLocalOrUrlType


class BrandLogoResource(BrandBase):
    """A logo resource, a file with optional alternative text"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        frozen=True,
        extra="forbid",
        use_attribute_docstrings=True,
    )

    path: FileLocationLocalOrUrlType
    """The path to the logo resource. This can be a local file or a URL."""

    alt: str | None = None
    """Alterative text for the image, used for accessibility."""


def brand_logo_type_discriminator(
    x: Any,
) -> Literal["file", "light-dark", "resource"]:
    if isinstance(x, dict):
        if "path" in x:
            return "resource"
        if "light" in x or "dark" in x:
            return "light-dark"

    if isinstance(x, BrandLightDark):
        return "light-dark"
    if isinstance(x, BrandLogoResource):
        return "resource"

    raise TypeError(f"{type(x)} is not a valid brand logo type")


BrandLogoImageType = Union[FileLocationLocalOrUrlType, BrandLogoResource]
"""
A logo image file can be either a local or URL file location, or a dictionary
with `path` and `alt`, the path to the file (local or URL) and an associated
alternative text for the logo image to be used for accessibility.
"""


BrandLogoFileType = Annotated[
    Union[
        Annotated[BrandLogoResource, Tag("resource")],
        Annotated[BrandLightDark[BrandLogoResource], Tag("light-dark")],
    ],
    Discriminator(brand_logo_type_discriminator),
]
"""
A logo image file can be either a local or URL file location with optional
alternative text or a light-dark variant that includes both a light and dark
color scheme.
"""


@add_example_yaml(
    {"path": "brand-logo-single.yml", "name": "Single Logo"},
    {"path": "brand-logo-simple.yml", "name": "Minimal"},
    {"path": "brand-logo-light-dark.yml", "name": "Light/Dark Variants"},
    {"path": "brand-logo-full.yml", "name": "Complete"},
    {"path": "brand-logo-full-alt.yml", "name": "Complete with Alt Text"},
)
class BrandLogo(BrandBase):
    """
    Brand Logos

    `logo` stores a single brand logo or a set of logos at three different size
    points and possibly in different color schemes. Store all of your brand's
    logo or image assets in `images` with meaningful names. Logos can be mapped
    to three preset sizes -- `small`, `medium`, and `large` -- and each can be
    either a single logo file or a light/dark variant
    (`brand_yml.BrandLightDark`).

    To attach alternative text to an image, provide the image as a dictionary
    including `path` (the image location) and `alt` (the short, alternative
    text describing the image).

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

    images: dict[str, BrandLogoResource] | None = None
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
            if isinstance(value, dict):
                # pydantic will handle validation of dict values
                continue

            if not isinstance(value, (str, FileLocation, Path)):
                raise ValueError(f"images[{key}] must be a file location")

            # Promote bare file locations to BrandLogoResource locations
            images[key] = {"path": value}

        defs_replace_recursively(data, defs=images, name="logo", exclude="path")

        return data

    @field_validator("small", "medium", "large", mode="before")
    @classmethod
    def _promote_bare_files_to_logo_resource(cls, value: Any):
        """
        Takes any bare file location references and promotes them to the
        structure required for BrandLogoResource.

        This results in a more nested but consistent data structure where each
        image is always a `BrandLogoResource` instance that's guaranteed to have
        a `path` item and optionally may include `alt` text.
        """
        if isinstance(value, (str, Path, AnyUrl)):
            # Bare strings/paths become BrandLogoResource without `alt`
            return {"path": value}

        if isinstance(value, dict):
            for k in ("light", "dark"):
                if k not in value:
                    continue
                value[k] = cls._promote_bare_files_to_logo_resource(value[k])

        if isinstance(value, BrandLightDark):
            for k in ("light", "dark"):
                prop = getattr(value, k)
                if prop is not None:
                    setattr(
                        value, k, cls._promote_bare_files_to_logo_resource(prop)
                    )

        return value
