from __future__ import annotations

from copy import deepcopy
from typing import Union

from pydantic import ConfigDict, field_validator, model_validator

from ._defs import (
    BrandLightDark,
    check_circular_references,
    defs_replace_recursively,
)
from ._utils import BrandBase

BrandLogoImageType = Union[str, BrandLightDark[str]]


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
        revalidate_instances="always",
        validate_assignment=True,
        use_attribute_docstrings=True,
    )

    images: dict[str, BrandLogoImageType] | None = None

    # TODO: FilePath validation
    # Currently we're using a string for the logo path, but we should update
    # this to use a validated Path or URL in the future.
    small: str | BrandLightDark[str] | None = None
    medium: str | BrandLightDark[str] | None = None
    large: str | BrandLightDark[str] | None = None

    @field_validator("images")
    @classmethod
    def validate_images(
        cls,
        value: dict[str, BrandLogoImageType] | None,
    ) -> dict[str, BrandLogoImageType] | None:
        if value is None:
            return

        check_circular_references(value)
        # We resolve `logo.images` on load or on replacement only
        # TODO: Replace with class with getter/setters
        #       Retain original values, return resolved values, and re-validate on update.
        defs_replace_recursively(value, value, name="images")

        return value

    @model_validator(mode="after")
    def resolve_image_values(self):
        if self.images is None:
            return self

        _logo_fields = [k for k in self.model_fields.keys() if k != "images"]

        full_defs = deepcopy(self.images) if self.images is not None else {}
        full_defs.update(
            {
                k: v
                for k, v in self.model_dump().items()
                if k in _logo_fields and v is not None
            }
        )
        defs_replace_recursively(
            full_defs,
            self,
            name="logo",
            exclude="images",
        )
        return self
