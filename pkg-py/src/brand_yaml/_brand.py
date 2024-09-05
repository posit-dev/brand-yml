from __future__ import annotations

from typing import Any, List, Literal, Union

from pydantic import BaseModel, ConfigDict, HttpUrl, RootModel


class Brand(BaseModel):
    model_config = ConfigDict(extra="ignore")

    meta: BrandMeta = None
    logo: str | BrandLogo = None
    color: BrandColor = None
    typography: BrandTypography = None
    defaults: dict[str, Any] = None

class BrandStringLightDark(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    light: str | dict = None
    dark: str | dict = None


class BrandLogo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    with_: dict[str, str | BrandStringLightDark] = None
    small: str | BrandStringLightDark = None
    medium: str | BrandStringLightDark = None
    large: str | BrandStringLightDark = None


type BrandColorValue = str


class BrandColor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    with_: dict[str, BrandColorValue] = None
    foreground: BrandColorValue = None
    background: BrandColorValue = None
    primary: BrandColorValue = None
    secondary: BrandColorValue = None
    tertiary: BrandColorValue = None
    success: BrandColorValue = None
    info: BrandColorValue = None
    warning: BrandColorValue = None
    danger: BrandColorValue = None
    light: BrandColorValue = None
    dark: BrandColorValue = None
    emphasis: BrandColorValue = None
    link: BrandColorValue = None


type BrandNamedColorType = Literal[
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
BrandNamedColorValues: BrandNamedColorType = (
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
)


class BrandTypography(BaseModel):
    with_: BrandFont | list[BrandFont] = None
    base: BrandTypographyOptions = None
    headings: BrandTypographyOptionsNoSize = None
    monospace: BrandTypographyOptions = None
    emphasis: BrandTypographyEmphasis = None
    link: BrandTypographyLink = None


class BrandTypographyOptions(BaseModel):
    family: str = None
    size: str = None
    line_height: str = None
    weight: BrandTypographyFontWeightType | list[BrandTypographyFontWeightType] = None
    style: BrandTypographyFontStyleType | list[BrandTypographyFontStyleType] = None
    color: str | BrandNamedColorType = None
    background_color: str | BrandNamedColorType = None


class BrandTypographyOptionsNoSize(BaseModel):
    family: str = None
    line_height: str = None
    weight: BrandTypographyFontWeightType | list[BrandTypographyFontWeightType] = None
    style: BrandTypographyFontStyleType | list[BrandTypographyFontStyleType] = None
    color: str | BrandNamedColorType = None
    background_color: str | BrandNamedColorType = None


class BrandTypographyEmphasis(BaseModel):
    weight: BrandTypographyFontWeightType | list[BrandTypographyFontWeightType] = None
    color: str | BrandNamedColorType = None
    background_color: str | BrandNamedColorType = None


class BrandTypographyLink(BaseModel):
    weight: BrandTypographyFontWeightType | list[BrandTypographyFontWeightType] = None
    decoration: str = None
    color: str | BrandNamedColorType = None
    background_color: str | BrandNamedColorType = None


type BrandTypographyFontWeightType = Literal[
    100, 200, 300, 400, 500, 600, 700, 800, 900
]
BrandTypographyFontWeightValues: BrandTypographyFontWeightType = (
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


type BrandTypographyFontStyleType = Literal["normal", "italic"]
BrandTypographyFontStyleValues: BrandTypographyFontStyleType = ("normal", "italic")


class BrandTypographyFontGoogle(BaseModel):
    family: str
    weight: BrandTypographyFontWeightType | list[BrandTypographyFontWeightType] = 400
    style: BrandTypographyFontStyleType | list[BrandTypographyFontStyleType] = "normal"
    display: Literal["auto", "block", "swap", "fallback", "optional"] = "auto"


class BrandFontFile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    family: str
    files: str | list[str] = None


class BrandFontFamily(RootModel):
    root: str


class BrandFont(RootModel):
    root: List[Union[BrandTypographyFontGoogle, BrandFontFile, BrandFontFamily]]
