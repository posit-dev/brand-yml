from __future__ import annotations

from copy import deepcopy
from typing import Optional

from pydantic import ConfigDict, Field, model_validator

from ._defs import BrandWith, defs_replace_recursively


class BrandColor(BrandWith[str]):
    """
    Brand Colors

    The brand's custom color palette and theme.

    Attributes
    ----------

    foreground
        The foreground color, used for text.

    background
        The background color, used for the page or main background.

    primary
        The primary accent color, i.e. the main theme color. Typically used for
        hyperlinks, active states, primary action buttons, etc.

    secondary
        The secondary accent color. Typically used for lighter text or disabled
        states.

    tertiary
        The tertiary accent color. Typically an even lighter color, used for
        hover states, accents, and wells.

    success
        The color used for positive or successful actions and information.

    info
        The color used for neutral or informational actions and information.

    warning
        The color used for warning or cautionary actions and information.

    danger
        The color used for errors, dangerous actions, or negative information.

    light
        A bright color, used as a high-contrast foreground color on dark
        elements or low-contrast background color on light elements.

    dark
        A dark color, used as a high-contrast foreground color on light elements
        or high-contrast background color on light elements.

    emphasis
        A color used to emphasize or highlight text or elements.

    link
        The color used for hyperlinks. If not defined, the `primary` color is
        used.

    """

    model_config = ConfigDict(
        extra="forbid",
        revalidate_instances="always",
        validate_assignment=True,
    )

    _color_fields = [
        "foreground",
        "background",
        "primary",
        "secondary",
        "tertiary",
        "success",
        "info",
        "warning",
        "danger",
        "light",
        "dark",
        "emphasis",
        "link",
    ]

    @model_validator(mode="after")
    def resolve_with_values(self):
        if self.with_ is not None:
            defs_replace_recursively(self.with_, self, name="with_")

        full_defs = deepcopy(self.with_) if self.with_ is not None else {}
        full_defs.update(
            {
                k: v
                for k, v in self.model_dump().items()
                if k in self._color_fields and v is not None
            }
        )
        defs_replace_recursively(full_defs, self, name="color")
        return self

    foreground: Optional[str] = Field(
        default=None,
        description="The foreground color, used for text.",
    )
    background: Optional[str] = Field(
        default=None,
        description="The background color, used for the page or main background.",
    )
    primary: Optional[str] = Field(
        default=None,
        description="The primary accent color, i.e. the main theme color. Typically used for hyperlinks, active states, primary action buttons, etc.",
    )
    secondary: Optional[str] = Field(
        default=None,
        description="The secondary accent color. Typically used for lighter text or disabled states.",
    )
    tertiary: Optional[str] = Field(
        default=None,
        description="The tertiary accent color. Typically an even lighter color, used for hover states, accents, and wells.",
    )

    success: Optional[str] = Field(
        default=None,
        description="The color used for positive or successful actions and information.",
    )
    info: Optional[str] = Field(
        default=None,
        description="The color used for neutral or informational actions and information.",
    )
    warning: Optional[str] = Field(
        default=None,
        description="The color used for warning or cautionary actions and information.",
    )
    danger: Optional[str] = Field(
        default=None,
        description="The color used for errors, dangerous actions, or negative information.",
    )

    light: Optional[str] = Field(
        default=None,
        description="A bright color, used as a high-contrast foreground color on dark elements or low-contrast background color on light elements.",
    )
    dark: Optional[str] = Field(
        default=None,
        description="A dark color, used as a high-contrast foreground color on light elements or high-contrast background color on light elements.",
    )
    emphasis: Optional[str] = Field(
        default=None,
        description="A color used to emphasize or highlight text or elements.",
    )
    link: Optional[str] = Field(
        default=None,
        description="The color used for hyperlinks. If not defined, the `primary` color is used.",
    )
