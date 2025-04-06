"""
Typography module for brand configuration and management.

This module provides classes and utilities for defining and managing typographic
choices in brand guidelines.

1. Font definitions (local files, Google Fonts, and Bunny Fonts)
2. Typography options (family, weight, size, line height, color, etc.)
3. Specific typography settings for base text, headings, monospace, and links
4. CSS generation for font includes and typography styles
"""

from __future__ import annotations

import itertools
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from re import split as re_split
from textwrap import indent
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
    overload,
)
from urllib.parse import urlencode, urljoin

from htmltools import HTMLDependency
from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    HttpUrl,
    PlainSerializer,
    PositiveInt,
    RootModel,
    SerializationInfo,
    Tag,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
)

from ._utils import maybe_convert_font_size_to_rem
from ._utils_docs import BaseDocAttributeModel, add_example_yaml
from .base import BrandBase
from .file import FileLocationLocal, FileLocationLocalOrUrlType

# Types ------------------------------------------------------------------------


T = TypeVar("T")

SingleOrList = Union[T, list[T]]
SingleOrTuple = Union[T, tuple[T, ...]]


BrandTypographyFontStyleType = Literal["normal", "italic"]
BrandTypographyFontWeightNamedType = Literal[
    "thin",
    "extra-light",
    "ultra-light",
    "light",
    "normal",
    "regular",
    "medium",
    "semi-bold",
    "demi-bold",
    "bold",
    "extra-bold",
    "ultra-bold",
    "black",
]

BrandTypographyFontWeightInt = Annotated[int, Field(ge=1, le=999)]

BrandTypographyFontWeightAllType = Union[
    BrandTypographyFontWeightInt, BrandTypographyFontWeightNamedType
]

BrandTypographyFontWeightSimpleType = Union[
    BrandTypographyFontWeightInt, Literal["normal", "bold"]
]

BrandTypographyFontWeightSimplePairedType = tuple[
    BrandTypographyFontWeightSimpleType,
    BrandTypographyFontWeightSimpleType,
]

BrandTypographyFontWeightSimpleAutoType = Union[
    BrandTypographyFontWeightInt, Literal["normal", "bold", "auto"]
]

BrandTypographyFontWeightRoundIntType = Literal[
    100, 200, 300, 400, 500, 600, 700, 800, 900
]

font_weight_round_int = (100, 200, 300, 400, 500, 600, 700, 800, 900)

# https://developer.mozilla.org/en-US/docs/Web/CSS/font-weight#common_weight_name_mapping
font_weight_map: dict[str, BrandTypographyFontWeightRoundIntType] = {
    "thin": 100,
    "extra-light": 200,
    "ultra-light": 200,
    "light": 300,
    "normal": 400,
    "regular": 400,
    "medium": 500,
    "semi-bold": 600,
    "demi-bold": 600,
    "bold": 700,
    "extra-bold": 800,
    "ultra-bold": 800,
    "black": 900,
}

# https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/src#font_formats
font_formats = {
    ".otc": "collection",
    ".ttc": "collection",
    ".eot": "embedded-opentype",
    ".otf": "opentype",
    ".ttf": "truetype",
    ".svg": "svg",
    ".svgz": "svg",
    ".woff": "woff",
    ".woff2": "woff2",
}


# Custom Errors ----------------------------------------------------------------


class BrandInvalidFontWeight(ValueError):
    def __init__(self, value: Any, allow_auto: bool = True):
        allowed = list(font_weight_map.keys())
        if allow_auto:
            allowed = ["auto", *allowed]

        super().__init__(
            f"Invalid font weight {value!r}. Expected a number divisible "
            + "by 100 and between 100 and 900, or one of "
            + f"{', '.join(allowed)}."
        )


class BrandUnsupportedFontFileFormat(ValueError):
    supported = ("opentype", "truetype", "woff", "woff2")

    def __init__(self, value: Any):
        super().__init__(
            f"Unsupported font file {value!r}. Expected one of {', '.join(self.supported)}."
        )


# Font Weights -----------------------------------------------------------------
@overload
def validate_font_weight(
    value: Any,
    allow_auto: Literal[True] = True,
) -> BrandTypographyFontWeightSimpleAutoType: ...


@overload
def validate_font_weight(
    value: Any,
    allow_auto: Literal[False],
) -> BrandTypographyFontWeightSimpleType: ...


def validate_font_weight(
    value: Any,
    allow_auto: bool = True,
) -> (
    BrandTypographyFontWeightSimpleAutoType
    | BrandTypographyFontWeightSimpleType
):
    if value is None:
        return "auto"

    if not isinstance(value, (str, int, float, bool)):
        raise BrandInvalidFontWeight(value, allow_auto=allow_auto)

    if isinstance(value, str):
        if allow_auto and value == "auto":
            return value
        if value in ("normal", "bold"):
            return value
        if value in font_weight_map:
            return font_weight_map[value]

    try:
        value = int(value)
    except ValueError:
        raise BrandInvalidFontWeight(value, allow_auto=allow_auto)

    if value < 100 or value > 900 or value % 100 != 0:
        raise BrandInvalidFontWeight(value, allow_auto=allow_auto)

    return value


# Fonts (Files) ----------------------------------------------------------------


class BrandTypographyFontFileWeight(RootModel):
    root: (
        BrandTypographyFontWeightSimpleAutoType
        | BrandTypographyFontWeightSimplePairedType
    )

    def __str__(self) -> str:
        if isinstance(self.root, tuple):
            vals = [
                str(font_weight_map[v]) if isinstance(v, str) else str(v)
                for v in self.root
            ]
            return " ".join(vals)
        return str(self.root)

    @model_serializer
    def to_str_url(self) -> str:
        if isinstance(self.root, tuple):
            return f"{self.root[0]}..{self.root[1]}"
        return str(self.root)

    if TYPE_CHECKING:  # pragma: no cover
        # https://docs.pydantic.dev/latest/concepts/serialization/#overriding-the-return-type-when-dumping-a-model
        # Ensure type checkers see the correct return type
        def model_dump(
            self,
            *,
            mode: Literal["json", "python"] | str = "python",
            include: Any = None,
            exclude: Any = None,
            context: dict[str, Any] | None = None,
            by_alias: bool | None = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal["none", "warn", "error"] = True,
            serialize_as_any: bool = False,
        ) -> str: ...

    @model_validator(mode="before")
    @classmethod
    def validate_root_before(
        cls, value: Any
    ) -> (
        BrandTypographyFontWeightSimpleAutoType
        | BrandTypographyFontWeightSimplePairedType
    ):
        if isinstance(value, str) and ".." in value:
            value = tuple(value.split(".."))

        if isinstance(value, tuple) or isinstance(value, list):
            if len(value) != 2:
                raise ValueError(
                    "Font weight ranges must have exactly 2 elements."
                )
            vals = (
                validate_font_weight(value[0], allow_auto=False),
                validate_font_weight(value[1], allow_auto=False),
            )
            return vals

        return validate_font_weight(value, allow_auto=True)


FontSourceType = Union[
    Literal["file"], Literal["google"], Literal["bunny"], Literal["system"]
]

FontSourceDefaultsType = Literal["file", "google", "bunny"]


class BrandTypographyFontSource(BaseModel, ABC):
    """
    A base class representing a font source.

    This class serves as a template for various font sources, encapsulating
    common properties and behaviors.
    """

    model_config = ConfigDict(use_attribute_docstrings=True)

    source: FontSourceType = Field(frozen=True)
    """
    The source of the font family, one of `"system"`, `"file"`, `"google"`, or
    `"bunny"`.
    """

    family: str = Field(frozen=True)
    """
    The font family name.

    Use this name in the `family` field of the other typographic properties,
    such as `base`, `headings`, `monospace`, etc.
    """

    @abstractmethod
    def to_css(self) -> str:
        """Create the CSS declarations needed to use the font family."""
        pass


class BrandTypographyFontSystem(BrandTypographyFontSource):
    """
    A system font family.

    This class is used to signal that a font should be retrieved from the
    system. This assumes that the font is installed on the system and will be
    resolved automatically; [`brand_yml.Brand`](`brand_yml.Brand`) won't do
    anything to embed the font or include it in any CSS.
    """

    source: Literal["system"] = Field("system", frozen=True)  # type: ignore[reportIncompatibleVariableOverride]

    def to_css(self) -> str:
        return ""


class BrandTypographyFontFiles(BrandTypographyFontSource):
    """
    A font family defined by a collection of font files.

    This class represents a font family that is specified using individual font
    files, either from local files or files hosted online. A font family is
    generally composed of multiple font files for different weights and styles
    within the same family. Currently, TrueType (`.ttf`), OpenType (`.otf`), and
    WOFF (`.woff` or `.woff2`) formats are supported.

    Examples
    --------

    ```yaml
    typography:
      fonts:
        # Local font files
        - family: Open Sans
          files:
            - path: fonts/open-sans/OpenSans-Bold.ttf
              style: bold
            - path: fonts/open-sans/OpenSans-Italic.ttf
              style: italic

        # Online files
        - family: Closed Sans
          files:
            - path: https://example.com/Closed-Sans-Bold.woff2
              weight: bold
            - path: https://example.com/Closed-Sans-Italic.woff2
              style: italic
    ```
    """

    model_config = ConfigDict(extra="forbid")

    source: Literal["file"] = Field("file", frozen=True)  # type: ignore[reportIncompatibleVariableOverride]
    files: list[BrandTypographyFontFilesPath] = Field(default_factory=list)

    def to_css(self) -> str:
        if len(self.files) == 0:
            return ""

        return "\n".join(
            "\n".join(
                [
                    "@font-face {",
                    f"  font-family: '{self.family}';",
                    indent(font.to_css(), 2 * " "),
                    "}",
                ]
            )
            for font in self.files
        )


class BrandTypographyFontFilesPath(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: FileLocationLocalOrUrlType
    weight: BrandTypographyFontFileWeight = Field(
        default_factory=lambda: BrandTypographyFontFileWeight(root="auto"),
        validate_default=True,
    )
    style: BrandTypographyFontStyleType = "normal"

    def to_css(self) -> str:
        # TODO: Handle `file://` vs `https://` or move to correct location
        src = f"url('{self.path.root}') format('{self.format}')"
        return "\n".join(
            [
                f"font-weight: {self.weight};",
                f"font-style: {self.style};",
                f"src: {src};",
            ]
        )

    @field_validator("path", mode="after")
    @classmethod
    def validate_path(
        cls, value: FileLocationLocalOrUrlType
    ) -> FileLocationLocalOrUrlType:
        ext = Path(str(value.root)).suffix
        if not ext:  # cover: for type checker
            raise BrandUnsupportedFontFileFormat(value.root)

        if ext not in font_formats:
            raise BrandUnsupportedFontFileFormat(value.root)

        return value

    @property
    def format(self) -> Literal["opentype", "truetype", "woff", "woff2"]:
        path = str(self.path.root)
        path_ext = Path(path).suffix

        if path_ext not in font_formats:
            raise BrandUnsupportedFontFileFormat(path)

        fmt = font_formats[path_ext]
        if fmt not in BrandUnsupportedFontFileFormat.supported:
            raise BrandUnsupportedFontFileFormat(path)

        return fmt


# Fonts (Google) ---------------------------------------------------------------


class BrandTypographyGoogleFontsWeightRange(RootModel):
    """
    Represents a range of font weights for Google Fonts.

    This class is used to specify a continuous range of font weights to be
    imported from Google Fonts for variable fonts that support a range of font
    weights. The weight range is represented as a list of two integers, where
    the first integer is the start of the range and the second is the end.

    Examples
    --------
    - `300..700`: Represents a range from light (300) to bold (700)
    - `100..900`: Represents the full range of weights from thin to black

    Note
    ----

    When serialized, this class will convert the range to a string format
    (e.g., "300..700") for compatibility with the Google Fonts API.

    Attributes
    ----------

    root
        A list containing two integers representing the start and end of the
        weight range.
    """

    model_config = ConfigDict(json_schema_mode_override="serialization")

    root: list[BrandTypographyFontWeightInt]

    def __str__(self) -> str:
        return f"{self.root[0]}..{self.root[1]}"

    @model_serializer(mode="plain", when_used="always")
    def to_serialized(self) -> str:
        return str(self)

    def to_url_list(self) -> list[str]:
        return [str(self)]

    @model_validator(mode="before")
    @classmethod
    def validate_weight(cls, value: Any) -> list[BrandTypographyFontWeightInt]:
        if isinstance(value, str) and ".." in value:
            start, end = re_split(r"\s*[.]{2,3}\s*", value, maxsplit=1)
            value = [start, end]

        if len(value) != 2:
            raise ValueError("Font weight ranges must have exactly 2 elements.")

        value = [validate_font_weight(v, allow_auto=False) for v in value]
        value = [font_weight_map[v] if isinstance(v, str) else v for v in value]
        return value

    if TYPE_CHECKING:  # pragma: no cover
        # https://docs.pydantic.dev/latest/concepts/serialization/#overriding-the-return-type-when-dumping-a-model
        # Ensure type checkers see the correct return type
        def model_dump(
            self,
            *,
            mode: Literal["json", "python"] | str = "python",
            include: Any = None,
            exclude: Any = None,
            context: dict[str, Any] | None = None,
            by_alias: bool | None = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal["none", "warn", "error"] = True,
            serialize_as_any: bool = False,
        ) -> str: ...


class BrandTypographyGoogleFontsWeight(RootModel):
    root: (
        BrandTypographyFontWeightSimpleAutoType
        | list[BrandTypographyFontWeightSimpleType]
    )

    def to_url_list(self) -> list[str]:
        weights = self.root if isinstance(self.root, list) else [self.root]
        vals = [
            str(font_weight_map[w]) if isinstance(w, str) else str(w)
            for w in weights
        ]
        vals.sort()
        return vals

    def to_serialized(
        self,
    ) -> (
        BrandTypographyFontWeightSimpleAutoType
        | list[BrandTypographyFontWeightSimpleType]
    ):
        return self.root

    @field_validator("root", mode="before")
    @classmethod
    def validate_root(
        cls,
        value: str | int | list[str | int],
    ) -> (
        BrandTypographyFontWeightSimpleAutoType
        | list[BrandTypographyFontWeightSimpleType]
    ):
        if isinstance(value, list):
            return [validate_font_weight(v, allow_auto=False) for v in value]
        return validate_font_weight(value, allow_auto=True)


def google_font_weight_discriminator(value: Any) -> str:
    if isinstance(value, str) and ".." in value:
        return "range"
    else:
        return "weights"


class BrandTypographyGoogleFontsApi(BrandTypographyFontSource):
    """
    A font source that utilizes the Google Fonts (or a compatible) API.

    This class provides a way to fetch and manage typography assets from
    Google Fonts, allowing for easy integration with brand-specific typographic
    styles.
    """

    model_config = ConfigDict(use_attribute_docstrings=True)

    family: str
    # Documented in parent class

    weight: Annotated[
        Union[
            Annotated[BrandTypographyGoogleFontsWeightRange, Tag("range")],
            Annotated[BrandTypographyGoogleFontsWeight, Tag("weights")],
        ],
        Discriminator(google_font_weight_discriminator),
        PlainSerializer(
            lambda x: x.to_serialized(),
            return_type=Union[str, int, list[Union[int, str]]],
        ),
    ] = Field(
        default=cast(
            BrandTypographyGoogleFontsWeight,
            list(font_weight_round_int),
        ),
        validate_default=True,
    )
    """
    The desired front weights to be imported for the font family.

    These are the font weights that will be imported from the Google Fonts-
    compatible API. This can be an array of font weights as numbers, e.g.
    `[300, 400, 700]`, or as named weights, e.g. `["light", "normal", "bold"]`.
    For variable fonts with variable font weight, you can import a range of
    weights using a string in the format `{start}..{end}`, e.g. `300..700`.
    """

    style: SingleOrList[BrandTypographyFontStyleType] = Field(
        ["normal", "italic"]
    )
    """
    The font style(s) (italic or normal) to be imported for the font family.

    This attribute can be set to a single style or a list of styles. Valid
    styles are "normal" and "italic". Defaults to `None`, which indicates that
    both normal and italic font styles should be imported.
    """

    display: Literal["auto", "block", "swap", "fallback", "optional"] = "auto"
    """
    Specifies how a font face is displayed based on whether and when it is
    downloaded and ready to use.

    This attribute is passed directly to the Google Fonts API and affects how
    the browser handles the font loading process.

    Options:
    - "auto": The browser default behavior, which is usually equivalent to "block".
    - "block": Gives the font face a short block period and infinite swap period.
    - "swap": Gives the font face an extremely small block period and infinite swap period.
    - "fallback": Gives the font face an extremely small block period and short swap period.
    - "optional": Gives the font face an extremely small block period and no swap period.

    For more details on these options, refer to the CSS `font-display` property
    documentation and [the Google Fonts API
    documentation](https://developers.google.com/fonts/docs/getting_started#use_font-display).
    """

    version: PositiveInt = 2
    """Google Fonts API version. (Primarily for internal use.)"""

    url: HttpUrl = Field(HttpUrl("https://fonts.googleapis.com/"))
    """URL of the Google Fonts-compatible API. (Primarily for internal use.)"""

    def to_css(self) -> str:
        return f"@import url('{self.to_import_url()}');"

    def to_import_url(self) -> str:
        """Returns the URL for the font family to be used in a CSS `@import` statement."""
        if self.version == 1:
            return self._import_url_v1()
        return self._import_url_v2()

    def _import_url_v1(self) -> str:
        weight = self.weight.to_url_list()
        style_str = sorted(
            self.style if isinstance(self.style, list) else [self.style]
        )
        style_map = {"normal": "", "italic": "i"}
        ital: list[str] = sorted([style_map[s] for s in style_str])

        values = []
        if len(weight) > 0 and len(ital) > 0:
            values = [f"{w}{i}" for w, i in itertools.product(weight, ital)]
        elif len(weight) > 0:
            values = [str(w) for w in weight]
        elif len(ital) > 0:
            values = ["regular" if i == "" else "italic" for i in ital]

        family_values = "" if len(values) == 0 else f":{','.join(values)}"
        params = urlencode(
            {
                "family": self.family + family_values,
                "display": self.display,
            }
        )

        return urljoin(str(self.url), f"css?{params}")

    def _import_url_v2(self) -> str:
        weight = self.weight.to_url_list()
        style_str = sorted(
            self.style if isinstance(self.style, list) else [self.style]
        )
        style_map = {"normal": 0, "italic": 1}
        ital: list[int] = sorted([style_map[s] for s in style_str])

        values = []
        axis = ""
        if len(weight) > 0 and len(ital) > 0:
            values = [f"{i},{w}" for i, w in itertools.product(ital, weight)]
            axis = "ital,wght"
        elif len(weight) > 0:
            values = [str(w) for w in weight]
            axis = "wght"
        elif len(ital) > 0:
            values = [str(i) for i in ital]
            axis = "ital"

        axis_range = "" if len(values) == 0 else f":{axis}@{';'.join(values)}"
        params = urlencode(
            {
                "family": self.family + axis_range,
                "display": self.display,
            }
        )

        return urljoin(str(self.url), f"css2?{params}")


class BrandTypographyFontGoogle(BrandTypographyGoogleFontsApi):
    """
    A font family provided by Google Fonts.


    This class represents a font family that is sourced from Google Fonts. It
    allows you to specify the font family name, weight range, and style.

    Subclass of
    [`brand_yml.typography.BrandTypographyGoogleFontsApi`](`brand_yml.typography.BrandTypographyGoogleFontsApi`),
    the generic Google Fonts API font source.

    Examples
    --------

    In this example, the Inter font is imported with all font weights and both
    normal and italic styles (these are the defaults). Additionally, the Roboto
    Slab font is sourced from Google Fonts with three specific font weights --
    400, 600, 800 -- and only the normal style.

    ```yaml typography:
      fonts:
        - family: Inter source: google
        - family: Roboto Slab source: google weight: [400, 600, 800] style:
          normal
    ```
    """

    model_config = ConfigDict(extra="forbid")

    source: Literal["google"] = Field("google", frozen=True)  # type: ignore[reportIncompatibleVariableOverride]


class BrandTypographyFontBunny(BrandTypographyGoogleFontsApi):
    """
    A font family provided by Bunny Fonts.

    This class represents a font family that is sourced from Bunny Fonts. It
    allows you to specify the font family name, weight range, and style.

    Subclass of
    [`brand_yml.typography.BrandTypographyGoogleFontsApi`](`brand_yml.typography.BrandTypographyGoogleFontsApi`),
    the generic Google Fonts API font source.

    Examples
    --------

    In this example, the Fira Code font is sourced from Bunny Fonts. By default
    all available weights and styles will be used.

    ```yaml
    typography:
      fonts:
        - family: Fira Code
          source: bunny
          # weight: [100, 200, 300, 400, 500, 600, 700, 800, 900]
          # style: [normal, italic]
    ```
    """

    model_config = ConfigDict(extra="forbid")

    source: Literal["bunny"] = Field("bunny", frozen=True)  # type: ignore[reportIncompatibleVariableOverride]
    version: PositiveInt = 1
    url: HttpUrl = Field(HttpUrl("https://fonts.bunny.net/"))


# Typography Options -----------------------------------------------------------


class BrandTypographyOptionsFamily(BaseDocAttributeModel):
    family: str | None = None
    """
    The font family to be used for this typographic element. Note that the font
    family name should match a resource in `typography.fonts`.
    """


class BrandTypographyOptionsSize(BaseDocAttributeModel):
    size: str | None = None
    """
    The font size to be used for this typographic element. Should be a
    [CSS length unit](https://developer.mozilla.org/en-US/docs/Web/CSS/length).
    """


class BrandTypographyOptionsColor(BaseDocAttributeModel):
    color: str | None = None
    """
    The color to be used for this typographic element. Can be any CSS-compatible
    color definition, but in general hexidecimal (`"#abc123") or `rgb()`
    (`rgb(171, 193, 35)`) are preferred and most widely compatible.
    """


class BrandTypographyOptionsBackgroundColor(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_attribute_docstrings=True,
    )

    background_color: str | None = Field(None, alias=str("background-color"))
    """
    The background color to be used for this typographic element. Can be any
    CSS-compatible color definition, but in general hexidecimal (`"#abc123") or
    `rgb()` (`rgb(171, 193, 35)`) are preferred and most widely compatible.
    """


class BrandTypographyOptionsStyle(BaseDocAttributeModel):
    style: SingleOrList[BrandTypographyFontStyleType] | None = None
    """
    The font style for this typographic element, i.e. whether the font should be
    styled in a `"normal"` or `"italic"` style.
    """


class BrandTypographyOptionsWeight(BaseDocAttributeModel):
    weight: BrandTypographyFontWeightSimpleType | None = None
    """
    The font weight (or boldness) of this typographic element. Any CSS-
    compatible font weight is allowed. The value could be a string such as
    `"thin"`, `"normal"`, `"bold"`, `"extra-bold"` or an integer between 1 and
    999. Font weights are most often integer values divisible by 100, e.g.
    100 (thin), 400 (normal), 700 (bold), or 800 (extra bold).
    """

    @field_validator("weight", mode="before")
    @classmethod
    def _validate_weight(
        cls, value: Any
    ) -> BrandTypographyFontWeightSimpleType:
        return validate_font_weight(value, allow_auto=False)


class BrandTypographyOptionsLineHeight(BaseDocAttributeModel):
    model_config = ConfigDict(populate_by_name=True)

    line_height: float | None = Field(None, alias=str("line-height"))
    """
    The line height of this typographic element. Line height refers to the
    vertical space between lines of text, which significantly impacts
    readability, aesthetics, and overall design. It often expressed as a
    multiple of the font size (e.g., 1.5 times the font size) or in fixed units
    (such as pixels or points).
    """


class BrandTypographyBase(
    BrandBase,
    BrandTypographyOptionsLineHeight,
    BrandTypographyOptionsSize,
    BrandTypographyOptionsWeight,
    BrandTypographyOptionsFamily,
):
    """
    Typographic settings for base (or body) text.

    Notes
    -----

    In some cases, you may wish to convert the base font size to an appropriate
    unit, such as [`rem`](https://developer.mozilla.org/en-US/docs/Web/CSS/length#rem)
    (i.e. a font size relative to the root element's font size). Use
    `typography_base_size_unit` in
    [pydantic's serialization context](https://docs.pydantic.dev/2.9/concepts/serialization/#serialization-context)
    to request the units for the base font size. (Note that currently only
    `"rem"` is supported.)

    ```{python}
    from brand_yml import Brand

    brand = Brand.from_yaml_str(
        f\"\"\"
        typography:
          base:
            size: 18px
        \"\"\"
    )

    brand.typography.model_dump(
      exclude_none = True,
      context={"typography_base_size_unit": "rem"}
    )
    ```

    Attributes
    ----------
    family
        The font family to be used. Note that the font family name should match
        a resource in `typography.fonts`.
    weight
        The font weight (boldness) of the text.
    size
        The font size of the text. Should be a CSS length unit (e.g., 14px).
    line_height
        The line height of the text. Line height refers to the vertical space
        between lines of text.
    """

    model_config = ConfigDict(extra="forbid")

    @field_serializer("size")
    def as_rem(self, v: str | None, info: SerializationInfo):
        if v is None or not info.context:
            return v

        convert_to: str = info.context.get("typography_base_size_unit", "")
        if convert_to:
            if convert_to == "rem":
                v = maybe_convert_font_size_to_rem(v)
            else:
                raise ValueError(
                    "brand_yml doesn't support converting `typography.base.size` "
                    f"into {convert_to} units. Please open an issue to request "
                    "adding support for this conversion: "
                    "https://github.com/posit-dev/brand-yml."
                )

        return v


class BrandTypographyHeadings(
    BrandBase,
    BrandTypographyOptionsColor,
    BrandTypographyOptionsLineHeight,
    BrandTypographyOptionsStyle,
    BrandTypographyOptionsWeight,
    BrandTypographyOptionsFamily,
):
    """
    Typographic settings for headings and titles.

    Attributes
    ----------
    family
        The font family used for headings. Note that this should match a resource
        in `typography.fonts`.
    weight
        The font weight (or boldness) of the text.
    style
        The font style for the heading, i.e., whether it should be styled in a
        `"normal"` or `"italic"` style.
    line_height
        The line height of the heading. Line height refers to the vertical space
        between lines of text.
    color
        The color of the text.

    Examples
    --------
    This example sets up typography settings for headings using the Inter font
    at a weight of 600 and with a line height that is 1.2 times the font size.

    ```yml
    typography:
      headings:
        family: Inter
        weight: 600
        line_height: 1.2
    ```
    """

    model_config = ConfigDict(extra="forbid")


class BrandTypographyMonospace(
    BrandBase,
    BrandTypographyOptionsSize,
    BrandTypographyOptionsWeight,
    BrandTypographyOptionsFamily,
):
    """
    Typographic settings for monospace text.

    This class defines general typography options for monospace text, typically
    used for code blocks and other programming-related content. These choices
    can be further refined for inline and block monospace text using
    [`brand_yml.typography.BrandTypographyMonospaceInline`](`brand_yml.typography.BrandTypographyMonospaceInline`)
    and
    [`brand_yml.typography.BrandTypographyMonospaceBlock`](`brand_yml.typography.BrandTypographyMonospaceBlock`)
    respectively.

    Attributes
    ----------
    family
        The font family to be used for monospace text. Note that the font family
        name should match a resource in `typography.fonts`.
    weight
        The font weight (boldness) of the monospace text. Can be a numeric value
        between 100 and 900, or a string like "normal" or "bold".
    size
        The font size of the monospace text. Should be a CSS length unit
        (e.g., "0.9em", "14px").

    Examples
    --------
    This example sets up typography settings for monospace text using the
    Fira Code font at a slightly smaller size than the base text:

    ```yaml
    typography:
      fonts:
        - family: Fira Code
          source: bunny
      monospace:
        family: Fira Code
        size: 0.9em
    ```

    You can also specify additional properties like weight:

    ```yaml
    typography:
      monospace:
        family: Fira Code
        size: 0.9em
        weight: 400
    ```

    For more complex setups, you can define different styles for inline and
    block monospace text:

    ```yaml
    typography:
      monospace:
        family: Fira Code
        size: 0.9em
      monospace-inline:
        color: "#7d12ba" # purple
        background-color: "#f8f9fa" # light gray
      monospace-block:
        color: foreground
        background-color: background
    ```
    """

    model_config = ConfigDict(extra="forbid")


class BrandTypographyMonospaceInline(
    BrandTypographyOptionsBackgroundColor,
    BrandTypographyOptionsColor,
    BrandTypographyMonospace,
):
    """
    Typographic settings for inline monospace text.

    This class defines typography options for inline monospace text, typically
    used for code snippets or technical terms within regular text. It inherits
    properties from
    [`brand_yml.typography.BrandTypographyMonospace`](`brand_yml.typography.BrandTypographyMonospace`)
    with additional options for foreground and background colors.

    Attributes
    ----------
    family
        The font family to be used for inline monospace text. Note that the font
        family name should match a resource in `typography.fonts`.
    weight
        The font weight (boldness) of the inline monospace text. Can be a
        numeric value between 100 and 900, or a string like "normal" or "bold".
    size
        The font size of the inline monospace text. Should be a CSS length unit
        (e.g., "0.9em", "14px").
    color
        The color of the inline monospace text. Can be any CSS-compatible color
        definition or a reference to a color defined in the brand's color
        palette.
    background_color
        The background color of the inline monospace text. Can be any
        CSS-compatible color definition or a reference to a color defined in the
        brand's color palette.

    Examples
    --------
    This example sets up typography settings for inline monospace text using the
    Fira Code font at a slightly smaller size than the base text, with custom
    colors:

    ```yaml
    typography:
      fonts:
        - family: Fira Code
          source: bunny
      monospace:
        family: Fira Code
        size: 0.9em
      monospace-inline:
        color: "#7d12ba"  # purple
        background-color: "#f8f9fa"  # light gray
    ```

    You can also use color names defined in your brand's color palette:

    ```yaml
    color:
      palette:
        red-light: "#fff1f0"
      primary: "#FF6F61"
      foreground: "#1b1818"
      background: "#f7f4f4"
    typography:
      monospace-inline:
        color: red
        background-color: red-light
    ```
    """

    model_config = ConfigDict(extra="forbid")


class BrandTypographyMonospaceBlock(
    BrandTypographyOptionsLineHeight,
    BrandTypographyOptionsBackgroundColor,
    BrandTypographyOptionsColor,
    BrandTypographyMonospace,
):
    """
    Typographic settings for block monospace text.

    This class defines typography options for block monospace text, typically
    used for code blocks or other larger sections of monospaced content. It
    inherits properties from
    [`brand_yml.typography.BrandTypographyMonospace`](`brand_yml.typography.BrandTypographyMonospace`)
    and adds options for line height, foreground color, and background color.

    Attributes
    ----------
    family
        The font family to be used for block monospace text. Note that the font
        family name should match a resource in `typography.fonts`.
    weight
        The font weight (boldness) of the block monospace text. Can be a
        numeric value between 100 and 900, or a string like "normal" or "bold".
    size
        The font size of the block monospace text. Should be a CSS length unit
        (e.g., "0.9em", "14px").
    line_height
        The line height of the block monospace text. Line height refers to the
        vertical space between lines of text.
    color
        The color of the block monospace text. Can be any CSS-compatible color
        definition or a reference to a color defined in the brand's color
        palette.
    background_color
        The background color of the block monospace text. Can be any
        CSS-compatible color definition or a reference to a color defined in the
        brand's color palette.

    Examples
    --------
    This example sets up typography settings for block monospace text using the
    Fira Code font at a slightly smaller size than the base text, with custom
    colors:

    ```yaml
    typography:
      fonts:
        - family: Fira Code
          source: bunny
      monospace:
        family: Fira Code
        size: 0.9em
      monospace-block:
        color: foreground
        background-color: background
        line-height: 1.4
    ```
    """

    model_config = ConfigDict(extra="forbid")


class BrandTypographyLink(
    BrandBase,
    BrandTypographyOptionsBackgroundColor,
    BrandTypographyOptionsColor,
    BrandTypographyOptionsWeight,
):
    """
    Typographic settings for hyperlinks.

    This class defines typography options for hyperlinks, allowing customization
    of font weight, colors, and text decoration.

    Attributes
    ----------
    weight
        The font weight (boldness) of the hyperlink text. Can be a numeric value
        between 100 and 900, or a string like "normal" or "bold".
    color
        The color of the hyperlink text. Can be any CSS-compatible color
        definition or a reference to a color defined in the brand's color
        palette.
    background_color
        The background color of the hyperlink text. Can be any CSS-compatible
        color definition or a reference to a color defined in the brand's color
        palette.
    decoration
        The text decoration for the hyperlink. Common values include
        "underline", "none", or "underline".

    Examples
    --------
    This example sets up typography settings for hyperlinks with a custom color
    and text decoration:

    ```yaml
    typography:
      link:
        weight: 600
        color: "#FF6F61"
        decoration: underline
    ```

    You can also use color names defined in your brand's color palette:

    ```yaml
    color:
      palette:
        red: "#FF6F61"
    typography:
      link:
        weight: 600
        color: red
        decoration: underline
    ```
    """

    model_config = ConfigDict(extra="forbid")

    decoration: str | None = None


# Brand Typography -------------------------------------------------------------

BrandTypographyFontFamily = Annotated[
    Union[
        BrandTypographyFontSystem,
        BrandTypographyFontFiles,
        BrandTypographyFontGoogle,
        BrandTypographyFontBunny,
    ],
    Discriminator("source"),
]
"""
A font family resource declaration.

A font family can be one of three different types of resources:

1. A font provided by [Google Fonts](https://fonts.google.com) --
   [`brand_yml.typography.BrandTypographyFontGoogle`](`brand_yml.typography.BrandTypographyFontGoogle`)
1. A font provided by [Bunny Fonts](https://fonts.bunny.net/) --
   [`brand_yml.typography.BrandTypographyFontBunny`](`brand_yml.typography.BrandTypographyFontBunny`)
1. A collection of font files, stored locally or online --
   [`brand_yml.typography.BrandTypographyFontFiles`](`brand_yml.typography.BrandTypographyFontFiles`)
"""


@add_example_yaml(
    {
        "path": "brand-typography-minimal.yml",
        "name": "Minimal",
        "exclude": ["meta"],
        "desc": """
        This minimal example chooses only the font family for the base text,
        headings and monospace. These fonts will be sourced, by default, from
        [Google Fonts](https://fonts.google.com).
        """,
    },
    {
        "path": "brand-typography-minimal-system.yml",
        "name": "Minimal with System Font",
        "exclude": ["meta"],
        "desc": """
        By default, fonts are sourced from Google Fonts, but you can also
        provide font sources in `fonts`. Here we're using a system font for
        "Open Sans" and Google Fonts for the others.
        """,
    },
    {
        "path": "brand-typography-simple.yml",
        "name": "Simple",
        "exclude": ["meta"],
        "desc": """
        In addition to setting the font family for key elements, you can choose
        other typographic properties. This example sets the line height and font
        size for base text, uses the primary accent color for headings and
        reduces the font size for monospace code, in addition to choosing the
        font family for each.
        """,
    },
    {
        "path": "brand-typography-fonts.yml",
        "name": "With Fonts",
        "exclude": ["meta"],
        "desc": """
        Font files may be sourced in a number of different ways.

        1. Local or hosted (online) files
        2. From [Google Fonts](https://fonts.google.com)
        3. Or from [Bunny Fonts](https://fonts.bunny.net/) (a GDPR-compliant)
           alternative to Google Fonts.

        Each font family should be declared in a list item provided to
        `typography.fonts`. Local font files can be stored adjacent to the
        `_brand.yml` file, and each file for a given family needs to be declared
        in the `files` key. Typically these font files cover a specific font
        weight and style.
        """,
    },
    {
        "path": "brand-typography-color.yml",
        "name": "With Color",
        "exclude": ["meta"],
        "desc": """
        Colors in the typographic elements---`color` or `background-color`---can
        use the names of colors in `color.palette` or the theme color names in
        `color`.
        """,
    },
)
class BrandTypography(BrandBase):
    """
    Represents the typographic choices of a brand.

    This class defines the structure and behavior of typography settings,
    including fonts, base text, headings, monospace text, and links.

    Examples
    --------

    Attributes
    ----------
    fonts
        A list of font family definitions. Each definition in the list describes
        a font family that is available to the brand. Fonts may be stored in
        files (either adjacent to `_brand.yml` or hosted online) or may be
        provided by [Google Fonts](https://fonts.google.com/) or [Font
        Bunny](https://fonts.bunny.net/) (a GDPR-compliant Google Fonts
        alternative).

    base
        The type used as the default text, primarily in the document body.

    headings
        The type used for headings. Note that these settings cover all heading
        levels (`h1`, `h2`, etc.).

    monospace
        The type used for code blocks and other monospaced text.

    monospace_inline
        The type used for inline code; inherits properties from `monospace`.

    monospace_block
        The type use for code blocks; inherits properties from `monospace`.

    link
        Type settings used for hyperlinks.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    fonts: list[BrandTypographyFontFamily] = Field(default_factory=list)
    base: BrandTypographyBase | None = None
    headings: BrandTypographyHeadings | None = None
    monospace: BrandTypographyMonospace | None = None
    monospace_inline: BrandTypographyMonospaceInline | None = Field(
        None, alias=str("monospace-inline")
    )
    monospace_block: BrandTypographyMonospaceBlock | None = Field(
        None, alias=str("monospace-block")
    )
    link: BrandTypographyLink | None = None

    @model_validator(mode="before")
    @classmethod
    def _default_fonts_provider(cls, data: Any):
        """
        Use Google Fonts as the default font provider.

        This method processes the input data to automatically add Google Fonts
        entries for font families specified in typography settings but not
        explicitly defined in the fonts list.
        """
        if not isinstance(data, dict):  # cover: for type checker
            return data

        defined_families = set()

        if (
            "fonts" in data
            and isinstance(data["fonts"], list)
            and len(data["fonts"]) > 0
        ):
            for font in data["fonts"]:
                defined_families.add(font["family"])
        else:
            data["fonts"] = []

        for field in (
            "base",
            "headings",
            "monospace",
            "monospace_inline",
            "monospace_block",
        ):
            if field not in data:
                continue

            if not isinstance(data[field], (str, dict)):  # pragma: no cover
                continue

            if isinstance(data[field], str):
                data[field] = {"family": data[field]}

            if "family" not in data[field]:
                continue

            if data[field]["family"] in defined_families:
                continue

            data["fonts"].append(
                {
                    "family": data[field]["family"],
                    "source": os.environ.get(
                        "BRAND_YML_DEFAULT_FONT_SOURCE",
                        "system",
                    ),
                }
            )
            defined_families.add(data[field]["family"])

        return data

    @model_validator(mode="after")
    def _forward_monospace_values(self):
        """
        Forward values from `monospace` to inline and block variants.

        This method ensures that `monospace-inline` and `monospace-block`
        inherit `family`, `style`, `weight`, and `size` from `monospace` if not
        explicitly set.
        """
        if self.monospace is None:
            return self

        monospace_defaults = {
            k: v
            for k, v in self.monospace.model_dump().items()
            if v is not None
        }

        def use_fallback(key: str):
            obj = getattr(self, key)

            if obj is None:
                new_type = (
                    BrandTypographyMonospaceInline
                    if key == "monospace_inline"
                    else BrandTypographyMonospaceBlock
                )
                setattr(self, key, new_type.model_validate(monospace_defaults))
                return

            for field in ("family", "style", "weight", "size"):
                fallback = monospace_defaults.get(field)
                if fallback is None:
                    continue
                if getattr(obj, field) is None:
                    setattr(obj, field, fallback)

        use_fallback("monospace_inline")
        use_fallback("monospace_block")
        return self

    def fonts_css_include(self) -> str:
        """
        Generates CSS include statements for the defined fonts.

        This method creates CSS `@import` or `@font-face` rules for all fonts
        defined in the typography configuration.

        Returns
        -------
        :
            A string containing CSS include statements for all defined fonts.
        """
        # TODO: Download or move files into a project-relative location

        if len(self.fonts) == 0:
            return ""

        fonts = sorted([*self.fonts], key=lambda x: x.source == "file")

        includes = [font.to_css() for font in fonts]

        return "\n".join([i for i in includes if i])

    def fonts_write_css(
        self,
        path_dir: str | Path,
        file_css: str = "fonts.css",
    ) -> Path | None:
        """
        Writes `fonts.css` into a directory, with copies of local fonts.

        Writes a `fonts.css` file (or `file_css`) into `path_dir` and copies any
        local fonts into the directory as well.

        Parameters
        ----------
        path_dir
            Path to the directory with the CSS file and copies of the local
            fonts should be written. If it does not exist it will be created.

        file_css
            The name of the CSS file with the font `@import` and `@font-face`
            rules should be written.

        Returns
        -------
        :
            Returns the path to the directory where the files were written, i.e.
            `path_dir`.
        """
        if len(self.fonts) == 0:
            return

        path_dir = Path(path_dir).expanduser().resolve()

        if not path_dir.is_dir():
            raise NotADirectoryError(f"{path_dir} is not a directory")

        path_dir.mkdir(parents=True, exist_ok=True)

        font_css = path_dir / file_css
        font_css.write_text(self.fonts_css_include())

        # Copy local files from typography.fonts into the output directory
        for font in self.fonts:
            if isinstance(font, BrandTypographyFontFiles):
                for file in font.files:
                    if isinstance(file.path, FileLocationLocal):
                        dest_path = path_dir / file.path.relative()
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(file.path.absolute(), dest_path)

        return path_dir

    def fonts_html_dependency(
        self,
        path_dir: str | Path,
        name: str = "brand-fonts",
        version: str = "0.0.1",
    ) -> HTMLDependency | None:
        """
        Generate an HTMLDependency for the font CSS and font files.

        This method creates an [HTMLDependency
        object](https://shiny.posit.co/py/api/core/Htmltools.html#htmltools.HTMLDependency)
        for the font CSS file and supporting font files written by the
        [`.fonts_html_dependency()`](`brand_yml.BrandTypography.fonts_html_dependency`)
        method. It's useful for integrating the font styles into web or
        [Shiny](https://shiny.posit.co/py) applications that use
        [htmltools](https://pypi.org/project/htmltools/).

        Parameters
        ----------
        path_dir
            The directory path where the CSS file will be written.
        name
            The name of the dependency. Defaults to "brand-fonts".
        version
            The version of the dependency. Defaults to "0.0.1".

        Returns
        -------
        :
            An [`htmltools.HTMLDependency`](`htmltools.HTMLDependency`) object
            if `typography` includes font file definitions or `None` if no font
            CSS is needed.

        """
        subdir = self.fonts_write_css(path_dir, "fonts.css")
        if subdir is None:
            return

        return HTMLDependency(
            name=name,
            version=version,
            source={"subdir": str(subdir)},
            stylesheet={"href": "fonts.css"},
            all_files=True,
        )
