from __future__ import annotations

from copy import deepcopy
from typing import Optional

from pydantic import (
    ConfigDict,
    field_validator,
    model_validator,
)

from ._defs import check_circular_references, defs_replace_recursively
from .base import BrandBase


class BrandColor(BrandBase):
    """
    Brand Colors

    The brand's custom color palette and theme.
    """

    model_config = ConfigDict(
        extra="forbid",
        revalidate_instances="always",
        validate_assignment=True,
        use_attribute_docstrings=True,
    )

    palette: dict[str, str] | None = None

    foreground: Optional[str] = None
    """The foreground color, used for text."""

    background: Optional[str] = None
    """The background color, used for the page or main background."""

    primary: Optional[str] = None
    """
    The primary accent color, i.e. the main theme color. Typically used for
    hyperlinks, active states, primary action buttons, etc.
    """

    secondary: Optional[str] = None
    """
    The secondary accent color. Typically used for lighter text or disabled
    states.
    """

    tertiary: Optional[str] = None
    """
    The tertiary accent color. Typically an even lighter color, used for
    hover states, accents, and wells.
    """

    success: Optional[str] = None
    """The color used for positive or successful actions and information."""

    info: Optional[str] = None
    """The color used for neutral or informational actions and information."""

    warning: Optional[str] = None
    """The color used for warning or cautionary actions and information."""

    danger: Optional[str] = None
    """The color used for errors, dangerous actions, or negative information."""

    light: Optional[str] = None
    """
    A bright color, used as a high-contrast foreground color on dark elements
    or low-contrast background color on light elements.
    """

    dark: Optional[str] = None
    """
    A dark color, used as a high-contrast foreground color on light elements
    or high-contrast background color on light elements.
    """

    emphasis: Optional[str] = None
    """A color used to emphasize or highlight text or elements."""

    link: Optional[str] = None
    """
    The color used for hyperlinks. If not defined, the `primary` color is
    used.
    """

    @field_validator("palette")
    @classmethod
    def create_brand_palette(cls, value: dict[str, str] | None):
        if value is None:
            return

        if not isinstance(value, dict):
            raise ValueError("`palette` must be a dictionary")

        check_circular_references(value)
        # We resolve `color.palette` on load or on replacement only
        # TODO: Replace with class with getter/setters
        #       Retain original values, return resolved values, and re-validate on update.
        defs_replace_recursively(value, name="palette")

        return value

    def _color_defs(self, resolved: bool = False) -> dict[str, str]:
        defs = deepcopy(self.palette) if self.palette is not None else {}
        defs.update(
            {
                k: v
                for k, v in self.model_dump().items()
                if k != "palette" and v is not None
            }
        )

        if resolved:
            defs_replace_recursively(defs)
            return defs
        else:
            return defs

    @model_validator(mode="after")
    def resolve_palette_values(self):
        defs_replace_recursively(
            self,
            defs=self._color_defs(resolved=False),
            name="color",
            exclude="palette",
        )
        return self
