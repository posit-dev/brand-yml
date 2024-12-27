"""
Brand Logos

Pydantic models for the brand's logos, stored adjacent to the `_brand.yml` file
or online, possibly with light or dark variants.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Annotated, Any, Literal, Union

import htmltools
from datauri import DataURI
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    Tag,
    field_validator,
    model_validator,
)

from ._defs import BrandLightDark, defs_replace_recursively
from ._utils import rand_hex
from ._utils_docs import add_example_yaml
from .base import BrandBase
from .file import (
    FileLocation,
    FileLocationLocal,
    FileLocationLocalOrUrlType,
)


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

    def as_data_uri(self) -> str:
        if not isinstance(self.path, FileLocationLocal):
            return ""
        return str(DataURI.from_file(str(self.path.absolute())))

    def to_html(
        self,
        *,
        selectors: Literal["prefers-color-scheme"]
        | dict[str, str | list[str]]
        | None = None,
        which: str = "",
        **kwargs: htmltools.TagAttrValue,
    ) -> htmltools.Tag:
        """
        Generate an HTML img tag for the logo resource.

        This method creates an HTML img tag based on the logo's path and
        alternative text. If the logo is stored locally, it will be converted to
        a data URI. For remote logos, the source URL will be used directly.

        Parameters
        ----------
        selectors
            Ignored, included for stable function signature across logo
            variations.
        which
            Ignored, included for stable function signature across logo
            variations.
        **kwargs
            Additional keyword arguments to be passed to the img tag.

        Returns
        -------
        :
            An HTML img tag representing the logo.

        Examples
        --------

        ```{python}
        from brand_yml import BrandLogoResource
        small = BrandLogoResource(
            path="../../logos/icon/brand-yml-icon-color.png",
            alt="brand.yml icon"
        )
        print(small.to_html(class_="my-brand-icon"))
        ```

        ```{python}
        small = BrandLogoResource(
            path="https://posit-dev.github.io/brand-yml/logos/icon/brand-yml-icon-color.png",
            alt="brand.yml remote icon"
        )
        small.to_html(width="32px", height="32px")
        ```
        """
        if isinstance(self.path, FileLocationLocal):
            return htmltools.img(**kwargs, alt=self.alt, src=self.as_data_uri())

        return htmltools.img(**kwargs, src=str(self.path), alt=self.alt or "")

    def tagify(self) -> htmltools.TagList:
        return htmltools.TagList(self.to_html())


class BrandLightDarkSelectors(BaseModel):
    id: str = Field(default_factory=lambda: rand_hex(4))
    light: list[str] = ['[data-bs-theme="light"]', ".quarto-light"]
    dark: list[str] = ['[data-bs-theme="dark"]', ".quarto-dark"]

    @field_validator("light", "dark")
    @classmethod
    def _validate_light_dark(cls, value: Any):
        if not isinstance(value, list):
            return [value]
        return value


def light_dark_css(
    selectors: Literal["prefers-color-scheme"]
    | dict[str, str | list[str]]
    | BrandLightDarkSelectors = BrandLightDarkSelectors(),
) -> tuple[str, str]:
    if isinstance(selectors, dict):
        selectors = BrandLightDarkSelectors.model_validate(selectors)

    if isinstance(selectors, BrandLightDarkSelectors):
        key = selectors.id
    else:
        key = rand_hex(4)

    if selectors == "prefers-color-scheme":
        light_dark_css = f"""
        @media not all and (prefers-color-scheme: dark) {{
            [data-when-theme-id="{key}"][data-when-theme="dark"] {{
                display: none;
            }}
        }}

        @media (prefers-color-scheme: dark) {{
            [data-when-theme-id="{key}"][data-when-theme="light"] {{
                display: none;
            }}
        }}
        """
    else:
        selectors_strs = [
            *[
                f'{s} [data-when-theme-id="{key}"][data-when-theme="dark"]'
                for s in selectors.light
            ],
            *[
                f'{s} [data-when-theme-id="{key}"][data-when-theme="light"]'
                for s in selectors.dark
            ],
        ]
        light_dark_css = f"""
        {', '.join(selectors_strs)} {{
            display: none;
        }}
        """

    return key, dedent(light_dark_css)


class BrandLogoLightDarkResource(BrandLightDark[BrandLogoResource]):
    """A pair of light and dark logo resources"""

    def to_html(
        self,
        *,
        selectors: Literal["prefers-color-scheme"]
        | dict[str, str | list[str]]
        | None = {
            "light": ['[data-bs-theme="light"]', ".quarto-light"],
            "dark": ['[data-bs-theme="dark"]', ".quarto-dark"],
        },
        which: str = "",
        **kwargs: htmltools.TagAttrValue,
    ) -> htmltools.TagList:
        """
        Generate a set of HTML img tags for the light/dark logo resource.

        This method creates a pair of HTML img tags for each of the `light` and
        `dark` logo variants using the logo's path and alternative text. If the
        logo image is stored locally, it will be converted to a data URI. For
        remote logos, the source URL will be used directly.

        Additional CSS is included to ensure that the `light` logo is shown when
        a light color scheme is used (dark text on a light background) and the
        `dark` logo is shown when a dark color scheme is used (light text on a
        dark background).

        Parameters
        ----------
        selectors
            CSS selectors used to indicate that light or dark mode is active.
            Use `selectors="prefers-color-scheme"` for a variant that uses
            media queries associated with the system color scheme, rather than
            specific CSS selectors.
        which
            Ignored, included for stable function signature across logo
            variations.
        **kwargs
            Additional keyword arguments to be passed to the img tag.

        Returns
        -------
        :
            Two HTML `<img>` tags with additional CSS to selectively hide the
            light or dark images when in the opposite color scheme.

        Examples
        --------

        ```{python}
        from brand_yml import BrandLogoLightDarkResource
        small = BrandLogoLightDarkResource(
            light = BrandLogoResource(
                path="../../logos/icon/brand-yml-icon-black.png",
                alt="brand.yml remote icon (light)"
            ),
            dark = BrandLogoResource(
                path="../../logos/icon/brand-yml-icon-color.png",
                alt="brand.yml remote icon (dark)"
            )
        )

        for item in small.to_html():  # `.to_html()` returns an `htmltools.TagList()`
            print(item)
        ```

        ```{python}
        small = BrandLogoLightDarkResource(
            light = BrandLogoResource(
                path="https://posit-dev.github.io/brand-yml/logos/icon/brand-yml-icon-black.png",
                alt="brand.yml remote icon (light)"
            ),
            dark = BrandLogoResource(
                path="https://posit-dev.github.io/brand-yml/logos/icon/brand-yml-icon-color.png",
                alt="brand.yml remote icon (dark)"
            )
        )
        small.to_html(width="32px", height="32px")
        ```
        """
        light = None
        dark = None

        key, css_light_dark = light_dark_css(
            selectors or BrandLightDarkSelectors()
        )

        if self.light:
            light = self.light.to_html(
                selectors=None,
                which="",
                **{"data-when-theme-id": key, "data-when-theme": "light"},
                **kwargs,
            )

        if self.dark:
            dark = self.dark.to_html(
                selectors=None,
                which="",
                **{"data-when-theme-id": key, "data-when-theme": "dark"},
                **kwargs,
            )

        return htmltools.TagList(
            # We always include the CSS directly because we've tied the choice
            # of `selectors` to this specific `to_html()` call via an `id`. Note
            # that this choice is motivated in part by the fact that Quarto
            # doesn't yet support `htmltools.HTMLDependency()` objects and
            # py-shiny doesn't support singletons.
            htmltools.tags.style(css_light_dark),
            light,
            dark,
        )

    def tagify(self) -> htmltools.TagList:
        return self.to_html()


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


BrandLogoFileType = Annotated[
    Union[
        Annotated[BrandLogoResource, Tag("resource")],
        Annotated[BrandLogoLightDarkResource, Tag("light-dark")],
    ],
    Discriminator(brand_logo_type_discriminator),
]
BrandLogoFileType.__doc__ = """
    A logo image file can be either a local or URL file location with optional
    alternative text ([](`brand_yml.BrandLogoResource`)) or a light-dark variant
    that includes both a light and dark color scheme
    ([](`brand_yml.BrandLogoLightDarkResource`)).
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
    ([brand_yml.BrandLightDark](`brand_yml.BrandLightDark`)).

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

    def to_html(
        self,
        *,
        which: Literal["small", "medium", "large", "smallest", "largest"] | str,
        selectors: Literal["prefers-color-scheme"]
        | dict[str, str | list[str]] = {
            "light": ['[data-bs-theme="light"]', ".quarto-light"],
            "dark": ['[data-bs-theme="dark"]', ".quarto-dark"],
        },
        **kwargs: htmltools.TagAttrValue,
    ) -> Union[htmltools.Tag, htmltools.TagList]:
        """
        Generate an HTML `img` tag or a set of `img` tags

        Creates an HTML `<img>` tag for the brand logo resource named by `which`
        or a set of `<img>` tags if the resource includes light/dark variants.

        Parameters
        ----------
        which
            The image to include by name. In addition to the named sizes---
            `"small"`, `"medium"` and `"large"`---`which` can be `"smallest"` or
            `"largest"` for the smallest or largest size available, or `which`
            can be the name of a named image in the `logo.images` dictionary.
        selectors
            CSS selectors used to indicate that light or dark mode is active.
            Use `selectors="prefers-color-scheme"` for a variant that uses
            media queries associated with the system color scheme, rather than
            specific CSS selectors.
        **kwargs
            Additional keyword arguments to be passed to the img tag.

        Returns
        -------
        :
            Returns an HTML `<img>` tag for a singular
            [](`brand_yml.BrandLogoResource`) or two HTML `<img>` tags with
            additional CSS to selectively hide the light or dark images when in
            the opposite color scheme for a
            [](`brand_yml.BrandLogoLightDarkResource`).

        See also
        --------

        - [BrandLogoResource.to_html](`brand_yml.BrandLogoResource.to_html`)
        - [BrandLogoLightDarkResource.to_html](`brand_yml.BrandLogoLightDarkResource.to_html`)

        """
        if which not in ("small", "medium", "large", "smallest", "largest"):
            if self.images and which in self.images.keys():
                return self.images[which].to_html(
                    selectors=selectors,
                    which="",
                    **kwargs,
                )
            else:
                raise ValueError(
                    f"{which} is not an image in `logo.images` "
                    "nor is it a known size: "
                    "small, medium, large, smallest, or largest."
                )

        if which == "smallest":
            if self.small:
                which = "small"
            elif self.medium:
                which = "medium"
            elif self.large:
                which = "large"

        if which == "largest":
            if self.large:
                which = "large"
            elif self.medium:
                which = "medium"
            elif self.small:
                which = "small"

        if which == "small":
            if not self.small:
                raise ValueError("This brand does not include a small logo.")
            return self.small.to_html(selectors=selectors, which="", **kwargs)

        if which == "medium":
            if not self.medium:
                raise ValueError("This brand does not include a medium logo.")
            return self.medium.to_html(selectors=selectors, which="", **kwargs)

        if which == "large":
            if not self.large:
                raise ValueError("This brand does not include a large logo.")
            return self.large.to_html(selectors=selectors, which="", **kwargs)

        raise ValueError("No predefined sizes are included for `brand.logo`.")

    def tagify(self) -> htmltools.TagList:
        if self.medium:
            return self.medium.tagify()
        if self.large:
            return self.large.tagify()
        if self.small:
            return self.small.tagify()

        return htmltools.TagList()

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
