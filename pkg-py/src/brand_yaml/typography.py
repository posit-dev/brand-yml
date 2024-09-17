from __future__ import annotations

import itertools
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
    RootModel,
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

BrandTypographyFontWeightRoundInt = (
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
BrandTypographyFontWeightMap: dict[
    str, BrandTypographyFontWeightRoundIntType
] = {
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
FontFormats = {
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
            + f"{', '.join(BrandTypographyFontWeightMap.keys())}."
        )


# Fonts ------------------------------------------------------------------------


class BrandUnsupportedFontFileFormat(ValueError):
    def __init__(self, value: Any):
        supported = ("opentype", "truetype", "woff", "woff2")
        super().__init__(
            f"Unsupported font file {value!r}. Expected one of {', '.join(supported)}."
        )


def validate_font_weight(
    value: int | str,
) -> BrandTypographyFontWeightSimpleType:
    if isinstance(value, str):
        if value in ("normal", "bold"):
            return value
        if value in BrandTypographyFontWeightMap:
            return BrandTypographyFontWeightMap[value]

    try:
        value = int(value)
    except ValueError:
        raise BrandInvalidFontWeight(value)

    if value < 100 or value > 900 or value % 100 != 0:
        raise BrandInvalidFontWeight(value)

    return value


class BrandTypographyFontFiles(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Literal["file"] = "file"
    family: str
    files: list[BrandTypographyFontFilesPath]


class BrandTypographyFontFilesPath(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str | HttpUrl  # TODO: FilePath validation
    weight: BrandTypographyFontWeightSimpleType = "normal"
    style: BrandTypographyFontStyleType = "normal"

    @field_validator("weight", mode="before")
    @classmethod
    def validate_weight(cls, value: int | str):
        return validate_font_weight(value)

    @field_validator("path", mode="after")
    @classmethod
    def validate_source(cls, value: str) -> str:
        if not Path(value).suffix:
            raise BrandUnsupportedFontFileFormat(value)

        if Path(value).suffix not in FontFormats:
            raise BrandUnsupportedFontFileFormat(value)

        return value

    @property
    def format(self) -> Literal["opentype", "truetype", "woff", "woff2"]:
        path = str(self.path)
        path_ext = Path(path).suffix

        if path_ext not in FontFormats:
            raise BrandUnsupportedFontFileFormat(path)

        fmt = FontFormats[path_ext]
        if fmt not in ("opentype", "truetype", "woff", "woff2"):
            raise BrandUnsupportedFontFileFormat(path)

        return fmt


class BrandTypographyGoogleFontsApi(BaseModel):
    family: str
    weight: SingleOrList[BrandTypographyFontWeightSimpleType] = Field(
        default=list(BrandTypographyFontWeightRoundInt)
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

    source: Literal["google"] = "google"


class BrandTypographyFontBunny(BrandTypographyGoogleFontsApi):
    model_config = ConfigDict(extra="forbid")

    source: Literal["bunny"] = "bunny"
    version: PositiveInt = 1
    url: HttpUrl = Field("https://fonts.bunny.net/")


# Typography Options -----------------------------------------------------------


class BrandNamedColor(RootModel):
    root: str


class BrandTypographyOptionsBackgroundColor(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    background_color: BrandNamedColor | None = Field(
        None, alias="background-color"
    )


class BrandTypographyOptionsColor(BaseModel):
    color: BrandNamedColor | None = None


class BrandTypographyOptionsFamily(BaseModel):
    family: str | None = None


class BrandTypographyOptionsLineHeight(BaseModel):
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
