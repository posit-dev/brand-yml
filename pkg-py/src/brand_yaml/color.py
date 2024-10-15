"""
Color Management for Brand YAML

This module defines the `BrandColor` class, which manages the brand's color
palette and mappings to common theme colors.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Optional

from pydantic import (
    ConfigDict,
    field_validator,
    model_validator,
)

from ._defs import check_circular_references, defs_replace_recursively
from ._utils_docs import add_example_yaml
from .base import BrandBase


@add_example_yaml(
    {
        "path": "brand-color-direct-posit.yml",
        "name": "Minimal",
        "desc": """
        In this example, we've picked colors from Posit's brand guidelines and
        mapped them directory to theme colors. This is a minimal approach to
        applying brand colors to theme colors.
        """,
    },
    {
        "path": "brand-color-palette-posit.yml",
        "name": "With palette",
        "desc": """
        This example first defines a color palette from Posit's brand guidelines
        and then maps them to theme colors by reference. With this approach,
        not all brand colors need to be used in the theme, but are still
        available via the `brand.color.palette` dictionary. This approach also
        reduces duplication in `brand.color`.
        """,
    },
)
class BrandColor(BrandBase):
    """
    Brand Colors

    The brand's custom color palette and theme. `color.palette` is a list of
    named colors used by the brand and `color.theme` maps brand colors to
    common theme elements (described in [Attributes](#attributes)).

    Examples
    --------

    ## Referencing colors in the brand's color palette

    Once defined in `color.palette`, you can re-use color definitions in any of
    the color fields. For example:

    ```{.yaml filename="_brand.yml"}
    color:
      palette:
        purple: "#6339E0"
      primary: purple
    ```

    Once imported via `brand_yaml.Brand.from_yaml()`, you can access the named
    color palette via `brand.color.palette["purple"]` and the `primary` field
    will be ready for use.

    ```{python}
    #| echo: false
    from brand_yaml import Brand
    brand = Brand.from_yaml_str('''
    color:
      palette:
        purple: "#6339E0"
      primary: purple
    ''')
    ```

    ::: python-code-preview
    ```{python}
    brand.color.palette["purple"]
    ```
    ```{python}
    brand.color.primary
    ```
    :::

    This same principle of reuse applies to the `color` and `background-color`
    fields of `brand_yaml.typography.BrandTypography`, where you can refer to
    any of the colors in `color.palette` or the theme colors directly.

    ```{.yaml filename="_brand.yml"}
    color:
      palette:
        purple: "#6339E0"
      primary: purple
    typography:
      headings:
        color: primary
      link:
        color: purple
    ```

    With this Brand YAML, both headings and links will ultimately be styled
    with the brand's `purple` color.

    ```{python}
    #| echo: false
    from brand_yaml import Brand
    brand = Brand.from_yaml_str('''
    color:
      palette:
        purple: "#6339E0"
      primary: purple
    typography:
      headings:
        color: primary
      link:
        color: purple
    ''')
    ```

    ::: python-code-preview
    ```{python}
    brand.typography.headings.color
    ```
    ```{python}
    brand.typography.link.color
    ```
    :::

    Attributes
    ----------
    palette
        A dictionary of brand colors where each key is a color name and the
        value is a color string (hex colors are recommended but no specific
        format is required at this time). These values can be referred to, by
        name, in the other theme properties

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
        The color used for hyperlinks.
    """

    model_config = ConfigDict(
        extra="forbid",
        revalidate_instances="always",
        validate_assignment=True,
        use_attribute_docstrings=True,
    )

    palette: dict[str, str] | None = None

    foreground: Optional[str] = None
    background: Optional[str] = None
    primary: Optional[str] = None
    secondary: Optional[str] = None
    tertiary: Optional[str] = None
    success: Optional[str] = None
    info: Optional[str] = None
    warning: Optional[str] = None
    danger: Optional[str] = None
    light: Optional[str] = None
    dark: Optional[str] = None
    emphasis: Optional[str] = None
    link: Optional[str] = None

    @field_validator("palette")
    @classmethod
    def _create_brand_palette(cls, value: dict[str, str] | None):
        """Resolve values within `color.palette` and ensure no circular references."""
        if value is None:
            return

        if not isinstance(value, dict):
            raise ValueError("`palette` must be a dictionary")

        check_circular_references(value)
        # We resolve `color.palette` on load or on replacement only
        # TODO: Replace with class with getter/setters
        #       Retain original values, return resolved values, and re-validate on update.
        defs_replace_recursively(value, value, name="palette")

        return value

    def _color_defs(self, resolved: bool = False) -> dict[str, str]:
        """
        Returns a flat dictionary of color definitions with `color.*` overlaid
        over `color.palette`.

        Parameters
        ----------
        resolved
            Whether or not the all resolvable values in the color definitions
            should be resolved. Currently, once the model is initialized,
            top-level values, e.g. `color.primary`, are already resolved but
            `color.palette` values retain internal references.

        Returns
        -------
        :
            A flat dictionary of color definitions.
        """
        defs = deepcopy(self.palette) if self.palette is not None else {}
        defs.update(
            {
                k: v
                for k, v in self.model_dump().items()
                if k != "palette" and v is not None
            }
        )

        if resolved:
            defs_replace_recursively(defs, defs)
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
