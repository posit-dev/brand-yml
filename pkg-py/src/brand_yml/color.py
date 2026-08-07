"""
Color Management for Brand YAML

This module defines the `BrandColor` class, which manages the brand's color
palette and mappings to common theme colors.
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal, Union

from pydantic import (
    ConfigDict,
    Discriminator,
    Tag,
    field_validator,
    model_validator,
)

from ._defs import (
    BrandLightDark,
    check_circular_references,
    defs_replace_recursively,
)
from ._utils_docs import add_example_yaml
from .base import BrandBase

rgx_valid_sass_name = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_-]*$")


class BrandColorLightDark(BrandLightDark[str]):
    """
    Light/Dark variant container for color values.

    This class extends BrandLightDark[str] to hold color values that differ
    between light and dark color schemes.
    """

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        """String representation returns light value if present, otherwise dark."""
        if self.light is not None:
            return self.light
        elif self.dark is not None:
            return self.dark
        return ""


def brand_color_type_discriminator(x: Any) -> Literal["color", "light-dark"]:
    """Discriminator function to determine if a value is a color string or light/dark variant."""
    if isinstance(x, dict):
        if "light" in x or "dark" in x:
            return "light-dark"
        # If it's a dict but not light/dark, it's invalid
        raise TypeError(f"{x} is not a valid brand color type")

    if isinstance(x, (BrandLightDark, BrandColorLightDark)):
        return "light-dark"

    # Assume it's a string color value
    return "color"


BrandColorType = Annotated[
    Union[
        Annotated[str, Tag("color")],
        Annotated[BrandColorLightDark, Tag("light-dark")],
    ],
    Discriminator(brand_color_type_discriminator),
]
"""
A color value can be either a string (hex, rgb, color name, etc.) or a
light-dark variant that includes both a light and dark color value.
"""


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

    Once imported via `brand_yml.Brand.from_yaml()`, you can access the named
    color palette via `brand.color.palette["purple"]` and the `primary` field
    will be ready for use.

    ```{python}
    #| echo: false
    from brand_yml import Brand
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
    fields of `brand_yml.typography.BrandTypography`, where you can refer to
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
    from brand_yml import Brand
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
        The foreground color, used for text. For best results, this color should
        be close to black and should have a high contrast with `background`.

    background
        The background color, used for the page or main background. For best
        results, this color should be close to white and should have a high
        contrast with `foreground`.

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
    """

    model_config = ConfigDict(
        extra="forbid",
        revalidate_instances="always",
        validate_assignment=True,
        use_attribute_docstrings=True,
    )

    palette: dict[str, str] | None = None

    foreground: BrandColorType | None = None
    background: BrandColorType | None = None
    primary: BrandColorType | None = None
    secondary: BrandColorType | None = None
    tertiary: BrandColorType | None = None
    success: BrandColorType | None = None
    info: BrandColorType | None = None
    warning: BrandColorType | None = None
    danger: BrandColorType | None = None
    light: BrandColorType | None = None
    dark: BrandColorType | None = None

    @field_validator("palette")
    @classmethod
    def _enforce_palette_sass_var_names(cls, value: dict[str, str] | None):
        """Enforce palette color names that are valid Sass/CSS variables."""
        if value is None:
            return

        for key in value.keys():
            if not rgx_valid_sass_name.match(key):
                suggestion = re.sub(r"^\d+", "_", key)
                suggestion = re.sub(r"[^a-zA-Z0-9_-]+", "-", suggestion)
                raise ValueError(
                    "Palette color names should be valid Sass or CSS variable names. "
                    f"Invalid name: {key!r}. "
                    f"Consider using {suggestion!r} instead."
                )

        return value

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

    def to_dict(
        self,
        include: Literal["all", "theme", "palette"] = "all",
    ) -> dict[str, str | dict[str, str]]:
        """
        Returns a flat dictionary of color definitions.

        Parameters
        ----------
        include
            Which colors to include: all brand colors (`"all"`), the brand's
            theme colors (`"theme"`) or the brand's color palette (`"palette"`).

        Returns
        -------
        :
            A flat dictionary of color definitions. Which colors are returned
            depends on the value of `include`:

            * `"all"` returns a flat dictionary of colors with theme colors overlaid
              on `color.palette`.
            * `"theme"` returns a dictionary of only the theme colors, excluding
              `color.palette`.
            * `"palette"` returns a dictionary of only the palette colors

            Colors may be strings or dictionaries with `light` and `dark` keys when
            light/dark variants are used.
        """
        defs: dict[str, str | dict[str, str]] = {}
        defs_theme: dict[str, str | dict[str, str]] = {}

        if include in ("all", "palette"):
            if self.palette is not None:
                # Copy palette entries as-is (they're all strings)
                for key, value in self.palette.items():
                    defs[key] = value
            else:
                defs = {}
        if include in ("all", "theme"):
            theme_dump = self.model_dump(exclude={"palette"}, exclude_none=True)
            # Convert BrandColorLightDark instances to dicts for resolution
            for key, value in theme_dump.items():
                if isinstance(value, dict) and (
                    "light" in value or "dark" in value
                ):
                    defs_theme[key] = value
                else:
                    defs_theme[key] = value

        defs.update(defs_theme)
        return defs

    @model_validator(mode="after")
    def resolve_palette_values(self):
        theme = {
            key: getattr(self, key)
            for key in self.__class__.model_fields
            if key != "palette"
        }
        palette = self.palette or {}

        def resolve(
            key: str | None,
            mode: Literal["auto", "light", "dark"] = "auto",
            visited: tuple[str, ...] = (),
        ) -> str | BrandColorLightDark | None:
            if key is None:
                return None

            in_theme = key in theme and theme[key] is not None
            theme_unseen = in_theme and key not in visited
            in_palette = key in palette

            if in_palette and not theme_unseen:
                node = f"palette.{key}"
                if node in visited:
                    path = " -> ".join((*visited, node))
                    raise ValueError(f"Circular color reference: {path}")
                return resolve(palette[key], mode, (*visited, node))

            if not in_theme:
                return key

            if key in visited:
                path = " -> ".join((*visited, key))
                raise ValueError(f"Circular color reference: {path}")

            value = theme[key]
            next_visited = (*visited, key)
            if isinstance(value, str):
                return resolve(value, mode, next_visited)

            if not isinstance(value, BrandColorLightDark):
                return value

            if mode == "auto":
                light = resolve(value.light, "light", next_visited)
                dark = resolve(value.dark, "dark", next_visited)
                return BrandColorLightDark(light=light, dark=dark)

            fallback_mode = "dark" if mode == "light" else "light"
            resolved_mode = (
                mode if getattr(value, mode) is not None else fallback_mode
            )
            return resolve(
                getattr(value, resolved_mode),
                resolved_mode,
                next_visited,
            )

        for key, value in theme.items():
            if value is not None:
                object.__setattr__(self, key, resolve(key))

        return self
