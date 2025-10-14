"""
Brand Logos

Pydantic models for the brand's logos, stored adjacent to the `_brand.yml` file
or online, possibly with light or dark variants.
"""

from __future__ import annotations

import base64
import mimetypes
import warnings
from pathlib import Path
from typing import Annotated, Any, Literal, Union

import htmltools
from pydantic import (
    AnyUrl,
    ConfigDict,
    Discriminator,
    Tag,
    field_validator,
    model_validator,
)

from ._defs import BrandLightDark, defs_replace_recursively
from ._html_deps import html_dep_brand_light_dark
from ._utils_docs import add_example_yaml
from .base import BrandBase
from .file import FileLocation, FileLocationLocal, FileLocationLocalOrUrlType


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

    attrs: dict[str, Any] | None = None
    """Additional attributes for HTML/markdown rendering.

    Values should be compatible with htmltools.TagAttrValue types when using HTML output.
    """

    def to_html(self, **kwargs: Any) -> htmltools.Tag:
        """
        Generate HTML img tag for the logo resource.

        Parameters
        ----------
        **kwargs
            Additional HTML attributes to include in the img tag. Values should be
            compatible with htmltools.TagAttrValue types.

        Returns
        -------
        :
            HTML img tag as a string.
        """
        # Get image source, handling base64 encoding for local files if needed
        if isinstance(self.path, FileLocationLocal):
            img_src = self._maybe_base64_encode_image(self.path)
        else:
            img_src = str(self.path)

        attrs, _ = htmltools.consolidate_attrs(self.attrs, kwargs)

        # Set src and alt on attrs to ensure they aren't overridden
        attrs["src"] = img_src
        if self.alt:
            attrs["alt"] = self.alt
        elif not attrs.get("alt"):
            attrs["alt"] = ""

        return htmltools.tags.img(
            {"class": "brand-logo"},
            attrs,
            html_dep_brand_light_dark(),
        )

    def to_markdown(self, **kwargs: Any) -> str:
        """
        Generate markdown image syntax for the logo resource.

        Parameters
        ----------
        **kwargs
            Additional attributes to include in the markdown image syntax.

        Returns
        -------
        :
            Markdown image syntax as a string.
        """
        # Get image source, handling base64 encoding for local files if needed
        if isinstance(self.path, FileLocationLocal):
            img_src = self._maybe_base64_encode_image(self.path)
        else:
            img_src = str(self.path)

        all_attrs, _ = htmltools.consolidate_attrs(
            {"alt": self.alt or "", "class": "brand-logo"},
            self.attrs,
            kwargs,
        )
        attrs_str = self._attrs_as_markdown(all_attrs)

        return f"![]({img_src}){{{attrs_str}}}"

    def to_str(self, format_type: str = "html", **kwargs: Any) -> str:
        """
        Convert logo resource to string representation.

        Parameters
        ----------
        format_type
            Output format, either "html" or "markdown".
        **kwargs
            Additional attributes for the output format.

        Returns
        -------
        :
            String representation in the specified format.
        """
        if format_type == "html":
            return str(self.to_html(**kwargs))
        elif format_type == "markdown":
            return self.to_markdown(**kwargs)
        else:
            raise ValueError("format_type must be 'html' or 'markdown'")

    def tagify(self) -> htmltools.Tag:
        """
        Convenience method for `.to_html()`, for use in Shiny apps.

        Returns
        -------
        :
            HTML img tag as a string.
        """
        return self.to_html()

    def _repr_html_(self) -> str:
        """Jupyter notebook HTML representation."""
        return str(self.to_html())

    def __str__(self) -> str:
        """String representation defaults to markdown."""
        return self.to_markdown()

    def _maybe_base64_encode_image(self, path: FileLocationLocal) -> str:
        """
        Encode local images as base64 data URIs for embedding.

        Parameters
        ----------
        path
            The image file path.

        Returns
        -------
        :
            The original path for URLs, or base64 data URI for local files.
        """
        if not path.exists():
            return str(path.relative())

        try:
            mime_type = (
                mimetypes.guess_type(path.absolute())[0]
                or "application/octet-stream"
            )

            with open(path.absolute(), "rb") as f:
                encoded = base64.b64encode(f.read()).decode("ascii")

            return f"data:{mime_type};base64,{encoded}"
        except Exception:
            warnings.warn(
                f"Could not base64 encode image at {path}. Using the relative file path instead."
            )
            # If anything goes wrong, just return the original path
            return str(path.relative())

    def _attrs_as_markdown(self, attrs: dict[str, Any]) -> str:
        """
        Format attributes for markdown image syntax.

        Parameters
        ----------
        attrs
            Dictionary of attributes.

        Returns
        -------
        :
            Formatted attribute string for markdown.
        """
        parts = []
        for key, value in attrs.items():
            if key == "class":
                # "my-class" --> ".my-class"
                classes = (
                    value.split() if isinstance(value, str) else [str(value)]
                )
                parts.extend(f".{cls}" for cls in classes)
            else:
                # Regular attribute
                parts.append(f'{key}="{value}"')

        return " ".join(parts)


class BrandLogoResourceLightDark(BrandLightDark[BrandLogoResource]):
    """
    Light/Dark variant container specifically for BrandLogoResource.

    This class extends BrandLightDark[BrandLogoResource] with formatting methods
    for HTML and Markdown output.
    """

    def __repr__(self) -> str:
        return super().__repr__()

    def to_html(self, **kwargs: Any) -> htmltools.Tag:
        """
        Generate HTML for light/dark logo resources.

        Creates a span container with light and dark images that can be
        shown/hidden via CSS.

        Parameters
        ----------
        **kwargs
            Additional HTML attributes for the images.

        Returns
        -------
        :
            HTML span containing both light and dark images.
        """
        children = []

        if self.light:
            light_tag = self.light.to_html(**kwargs)
            light_tag.add_class("light-content")
            children.append(light_tag)

        if self.dark:
            dark_tag = self.dark.to_html(**kwargs)
            dark_tag.add_class("dark-content")
            children.append(dark_tag)

        span_tag = htmltools.tags.span(
            {"class": "brand-logo-light-dark"},
            *children,
            html_dep_brand_light_dark(),
        )

        return span_tag

    def to_markdown(self, **kwargs: Any) -> str:
        """
        Generate markdown for light/dark logo resources.

        Creates two adjacent images with light-content and dark-content classes.

        Parameters
        ----------
        **kwargs
            Additional attributes for the markdown images.

        Returns
        -------
        :
            Markdown with both light and dark images.
        """
        light_md = ""
        dark_md = ""

        if self.light:
            light_class_attrs, _ = htmltools.consolidate_attrs(
                {"class": "light-content"},
                kwargs,
            )
            light_md = self.light.to_markdown(**light_class_attrs)

        if self.dark:
            dark_class_attrs, _ = htmltools.consolidate_attrs(
                {"class": "dark-content"},
                kwargs,
            )
            dark_md = self.dark.to_markdown(**dark_class_attrs)

        return f"{light_md} {dark_md}".strip()

    def to_str(self, format_type: str = "html", **kwargs: Any) -> str:
        """
        Convert light/dark logo resources to string representation.

        Parameters
        ----------
        format_type
            Output format, either "html" or "markdown".
        **kwargs
            Additional attributes for the output format.

        Returns
        -------
        :
            String representation in the specified format.
        """
        if format_type == "html":
            return str(self.to_html(**kwargs))
        elif format_type == "markdown":
            return self.to_markdown(**kwargs)
        else:
            raise ValueError("format_type must be 'html' or 'markdown'")

    def tagify(self) -> htmltools.Tag:
        """
        Convenience method for `.to_html()`, for use in Shiny apps.

        Returns
        -------
        :
            HTML span with light and dark images.
        """
        return self.to_html()

    def _repr_html_(self) -> str:
        """Jupyter notebook HTML representation."""
        return str(self.to_html())

    def __str__(self) -> str:
        """String representation defaults to markdown."""
        return self.to_markdown()


def brand_logo_type_discriminator(
    x: Any,
) -> Literal["file", "light-dark", "resource"]:
    if isinstance(x, dict):
        if "path" in x:
            return "resource"
        if "light" in x or "dark" in x:
            return "light-dark"

    if isinstance(x, (BrandLightDark, BrandLogoResourceLightDark)):
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
        Annotated[BrandLogoResourceLightDark, Tag("light-dark")],
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

    For a convenient way to use logos from a `Brand` instance, see
    `Brand.use_logo`.

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

        if isinstance(value, (BrandLightDark, BrandLogoResourceLightDark)):
            for k in ("light", "dark"):
                prop = getattr(value, k)
                if prop is not None:
                    setattr(
                        value, k, cls._promote_bare_files_to_logo_resource(prop)
                    )

        return value
