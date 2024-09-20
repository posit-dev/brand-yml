from __future__ import annotations

import itertools
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Annotated, Any, Literal, TypeVar, Union
from urllib.parse import urlencode, urljoin

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    HttpUrl,
    PositiveInt,
    field_validator,
    model_validator,
)

from ._utils import BrandBase

# Types ------------------------------------------------------------------------


T = TypeVar("T")

SingleOrList = Union[T, list[T]]


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
BrandTypographyFontWeightAllType = Union[
    float, int, BrandTypographyFontWeightNamedType
]

BrandTypographyFontWeightSimpleType = Union[
    float, int, Literal["normal", "bold"]
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
    def __init__(self, value: Any):
        super().__init__(
            f"Invalid font weight {value!r}. Expected a number divisible "
            + "by 100 and between 100 and 900, or one of "
            + f"{', '.join(font_weight_map.keys())}."
        )


# Fonts ------------------------------------------------------------------------


class BrandUnsupportedFontFileFormat(ValueError):
    supported = ("opentype", "truetype", "woff", "woff2")

    def __init__(self, value: Any):
        super().__init__(
            f"Unsupported font file {value!r}. Expected one of {', '.join(self.supported)}."
        )


def validate_font_weight(
    value: int | str | None,
) -> BrandTypographyFontWeightSimpleType:
    if value is None:
        return "normal"

    if isinstance(value, str):
        if value in ("normal", "bold"):
            return value
        if value in font_weight_map:
            return font_weight_map[value]

    try:
        value = int(value)
    except ValueError:
        raise BrandInvalidFontWeight(value)

    if value < 100 or value > 900 or value % 100 != 0:
        raise BrandInvalidFontWeight(value)

    return value


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
            f"@font-face {{\n"
            f"  font-family: '{self.family}';\n"
            f"  font-weight: {font.weight};\n"
            f"  font-style: {font.style};\n"
            f"  src: {font.css_font_face_src()};\n"
            f"}}"
            for font in self.files
        )


class BrandTypographyFontFilesPath(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str | HttpUrl  # TODO: FilePath validation
    weight: BrandTypographyFontWeightSimpleType = "normal"
    style: BrandTypographyFontStyleType = "normal"

    @field_validator("weight", mode="before")
    @classmethod
    def validate_weight(cls, value: str | int | None):
        return validate_font_weight(value)

    @field_validator("path", mode="after")
    @classmethod
    def validate_source(cls, value: str) -> str:
        if not Path(value).suffix:
            raise BrandUnsupportedFontFileFormat(value)

        if Path(value).suffix not in font_formats:
            raise BrandUnsupportedFontFileFormat(value)

        return value

    @property
    def format(self) -> Literal["opentype", "truetype", "woff", "woff2"]:
        path = str(self.path)
        path_ext = Path(path).suffix

        if path_ext not in font_formats:
            raise BrandUnsupportedFontFileFormat(path)

        fmt = font_formats[path_ext]
        if fmt not in BrandUnsupportedFontFileFormat.supported:
            raise BrandUnsupportedFontFileFormat(path)

        return fmt

    def css_font_face_src(self) -> str:
        # TODO: Handle `file://` vs `https://` or move to correct location
        return f"url('{self.path}') format('{self.format}')"


class BrandTypographyGoogleFontsApi(BrandTypographyFontSource):
    family: str
    weight: SingleOrList[BrandTypographyFontWeightSimpleType] = Field(
        default=list(font_weight_round_int)
    )
    style: SingleOrList[BrandTypographyFontStyleType] = ["normal", "italic"]
    display: Literal["auto", "block", "swap", "fallback", "optional"] = "auto"
    version: PositiveInt = 2
    url: HttpUrl = Field("https://fonts.googleapis.com/")

    @field_validator("weight", mode="before")
    @classmethod
    def validate_weight(
        cls, value: SingleOrList[Union[int, str]]
    ) -> SingleOrList[BrandTypographyFontWeightSimpleType]:
        if isinstance(value, list):
            return [validate_font_weight(x) for x in value]
        else:
            return validate_font_weight(value)

    def css_include(self) -> str:
        return f"@import url('{self.import_url()}');"

    def import_url(self) -> str:
        if self.version == 1:
            return self._import_url_v1()
        return self._import_url_v2()

    def _import_url_v1(self) -> str:
        weight = sorted(
            self.weight if isinstance(self.weight, list) else [self.weight]
        )
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
        weight = sorted(
            self.weight if isinstance(self.weight, list) else [self.weight]
        )
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

        axis_range = f":{axis}@{';'.join(values)}"
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
    url: HttpUrl = Field("https://fonts.bunny.net/")


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
    def validate_weight(cls, value: int | str):
        return validate_font_weight(value)


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
        if not isinstance(data, dict):
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

            if not isinstance(data[field], (str, dict)):
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
