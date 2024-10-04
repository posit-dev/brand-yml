from __future__ import annotations

import itertools
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
    overload,
)
from urllib.parse import urlencode, urljoin

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    HttpUrl,
    PlainSerializer,
    PositiveInt,
    RootModel,
    Tag,
    field_validator,
    model_serializer,
    model_validator,
)

from .base import BrandBase
from .file import FileLocationLocalOrUrl

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

font_weight_round_int = (
    100,
    200,
    300,
    400,
    500,
    600,
    700,
    800,
    900,
)

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


class BrandUnsupportedFontFileFormat(ValueError):
    supported = ("opentype", "truetype", "woff", "woff2")

    def __init__(self, value: Any):
        super().__init__(
            f"Unsupported font file {value!r}. Expected one of {', '.join(self.supported)}."
        )


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
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal["none", "warn", "error"] = True,
            serialize_as_any: bool = False,
        ) -> str: ...

    @field_validator("root", mode="before")
    @classmethod
    def validate_root_before(cls, value: Any) -> Any:
        if isinstance(value, str) and ".." in value:
            value = value.split("..")
            return (v for v in value if v)
        return value

    @field_validator("root", mode="before")
    @classmethod
    def validate_root(
        cls, value: Any
    ) -> (
        BrandTypographyFontWeightSimpleAutoType
        | BrandTypographyFontWeightSimplePairedType
    ):
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


FontSourceType = Union[Literal["file"], Literal["google"], Literal["bunny"]]


class BrandTypographyFontSource(BaseModel, ABC):
    source: FontSourceType = Field(frozen=True)
    family: str = Field(frozen=True)

    @abstractmethod
    def css_include(self) -> str:
        pass


class BrandTypographyFontFiles(BrandTypographyFontSource):
    model_config = ConfigDict(extra="forbid")

    source: Literal["file"] = Field("file", frozen=True)  # type: ignore[reportIncompatibleVariableOverride]
    files: list[BrandTypographyFontFilesPath] = Field(default_factory=list)

    def css_include(self) -> str:
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

    path: FileLocationLocalOrUrl
    weight: BrandTypographyFontFileWeight = Field(
        default_factory=lambda: BrandTypographyFontFileWeight(root="auto"),
        validate_default=True,
    )
    style: BrandTypographyFontStyleType = "normal"

    def to_css(self) -> str:
        # TODO: Handle `file://` vs `https://` or move to correct location
        weight = self.weight.to_str_url()
        src = f"url('{self.path.root}') format('{self.format}')"
        return "\n".join(
            [
                f"font-weight: {weight};",
                f"font-style: {self.style};",
                f"src: {src};",
            ]
        )

    @field_validator("path", mode="after")
    @classmethod
    def validate_path(
        cls, value: FileLocationLocalOrUrl
    ) -> FileLocationLocalOrUrl:
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
    model_config = ConfigDict(json_schema_mode_override="serialization")

    root: list[BrandTypographyFontWeightInt]

    def __str__(self) -> str:
        return f"{self.root[0]}..{self.root[1]}"

    @model_serializer(mode="plain", when_used="always")
    def to_serialized(self) -> str:
        return f"{self.root[0]}..{self.root[1]}"

    def to_url_list(self) -> list[str]:
        return [str(self)]

    @field_validator("root", mode="before")
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
            by_alias: bool = False,
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
    family: str
    weight: Annotated[
        Union[
            Annotated[BrandTypographyGoogleFontsWeightRange, Tag("range")],
            Annotated[BrandTypographyGoogleFontsWeight, Tag("weights")],
        ],
        Discriminator(google_font_weight_discriminator),
        PlainSerializer(
            lambda x: x.to_serialized(),
            return_type=Union[str, int, list[int | str]],
        ),
    ] = Field(default=list(font_weight_round_int), validate_default=True)
    style: SingleOrList[BrandTypographyFontStyleType] = ["normal", "italic"]
    display: Literal["auto", "block", "swap", "fallback", "optional"] = "auto"
    version: PositiveInt = 2
    url: HttpUrl = Field("https://fonts.googleapis.com/", validate_default=True)

    def css_include(self) -> str:
        return f"@import url('{self.to_import_url()}');"

    def to_import_url(self) -> str:
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
    model_config = ConfigDict(extra="forbid")

    source: Literal["google"] = Field("google", frozen=True)  # type: ignore[reportIncompatibleVariableOverride]


class BrandTypographyFontBunny(BrandTypographyGoogleFontsApi):
    model_config = ConfigDict(extra="forbid")

    source: Literal["bunny"] = Field("bunny", frozen=True)  # type: ignore[reportIncompatibleVariableOverride]
    version: PositiveInt = 1
    url: HttpUrl = Field("https://fonts.bunny.net/", validate_default=True)


# Typography Options -----------------------------------------------------------


class BrandTypographyOptionsBackgroundColor(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    background_color: str | None = Field(None, alias="background-color")


class BrandTypographyOptionsColor(BaseModel):
    color: str | None = None


class BrandTypographyOptionsFamily(BaseModel):
    family: str | None = None


class BrandTypographyOptionsLineHeight(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    line_height: float | None = Field(None, alias="line-height")


class BrandTypographyOptionsSize(BaseModel):
    size: str | None = None


class BrandTypographyOptionsStyle(BaseModel):
    style: SingleOrList[BrandTypographyFontStyleType] | None = None


class BrandTypographyOptionsWeight(BaseModel):
    weight: BrandTypographyFontWeightSimpleType | None = None

    @field_validator("weight", mode="before")
    @classmethod
    def validate_weight(cls, value: Any) -> BrandTypographyFontWeightSimpleType:
        return validate_font_weight(value, allow_auto=False)


class BrandTypographyBase(
    BrandBase,
    BrandTypographyOptionsFamily,
    BrandTypographyOptionsWeight,
    BrandTypographyOptionsSize,
    BrandTypographyOptionsLineHeight,
    BrandTypographyOptionsColor,
):
    model_config = ConfigDict(extra="forbid")


class BrandTypographyHeadings(
    BrandBase,
    BrandTypographyOptionsFamily,
    BrandTypographyOptionsWeight,
    BrandTypographyOptionsStyle,
    BrandTypographyOptionsLineHeight,
    BrandTypographyOptionsColor,
):
    model_config = ConfigDict(extra="forbid")


class BrandTypographyMonospace(
    BrandBase,
    BrandTypographyOptionsFamily,
    BrandTypographyOptionsWeight,
    BrandTypographyOptionsSize,
):
    model_config = ConfigDict(extra="forbid")


class BrandTypographyMonospaceInline(
    BrandTypographyMonospace,
    BrandTypographyOptionsColor,
    BrandTypographyOptionsBackgroundColor,
):
    model_config = ConfigDict(extra="forbid")


class BrandTypographyMonospaceBlock(
    BrandTypographyMonospace,
    BrandTypographyOptionsLineHeight,
    BrandTypographyOptionsColor,
    BrandTypographyOptionsBackgroundColor,
):
    model_config = ConfigDict(extra="forbid")


class BrandTypographyLink(
    BrandBase,
    BrandTypographyOptionsWeight,
    BrandTypographyOptionsColor,
    BrandTypographyOptionsBackgroundColor,
):
    model_config = ConfigDict(extra="forbid")

    decoration: str | None = None


# Brand Typography -------------------------------------------------------------


class BrandTypography(BrandBase):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    fonts: list[
        Annotated[
            Union[
                BrandTypographyFontFiles,
                BrandTypographyFontGoogle,
                BrandTypographyFontBunny,
            ],
            Discriminator("source"),
        ]
    ] = Field(default_factory=list)
    base: BrandTypographyBase | None = None
    headings: BrandTypographyHeadings | None = None
    monospace: BrandTypographyMonospace | None = None
    monospace_inline: BrandTypographyMonospaceInline | None = Field(
        None, alias="monospace-inline"
    )
    monospace_block: BrandTypographyMonospaceBlock | None = Field(
        None, alias="monospace-block"
    )
    link: BrandTypographyLink | None = None

    @model_validator(mode="before")
    @classmethod
    def simple_google_fonts(cls, data: Any):
        if not isinstance(data, dict):  # cover: for type checker
            return data

        defined_families = set()
        file_families = set()

        if (
            "fonts" in data
            and isinstance(data["fonts"], list)
            and len(data["fonts"]) > 0
        ):
            for font in data["fonts"]:
                defined_families.add(font["family"])
                if font["source"] == "file":
                    file_families.add(font["family"])
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
                    "source": "google",
                }
            )
            defined_families.add(data[field]["family"])

        return data

    @model_validator(mode="after")
    def forward_monospace_values(self):
        """
        Forward values from `monospace` to inline and block variants.

        `monospace-inline` and `monospace-block` both inherit `family`, `style`,
        `weight` and `size` from `monospace`.
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

    def css_include_fonts(self) -> str:
        # TODO: Download or move files into a project-relative location

        if len(self.fonts) == 0:
            return ""

        includes = [font.css_include() for font in self.fonts]

        return "\n".join([i for i in includes if i])
