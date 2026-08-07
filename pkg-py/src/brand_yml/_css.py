from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from .color import BrandColorLightDark

if TYPE_CHECKING:
    from . import Brand

ColorMode = Literal["light", "dark"]
DEFAULT_MODE_SCOPES: dict[ColorMode, str] = {
    "light": "",
    "dark": "prefers-color-scheme",
}


def brand_css_variables(
    brand: Brand,
    mode_scopes: Mapping[ColorMode, str] | None = None,
) -> str:
    """
    Generate mode-aware CSS custom properties from a brand.

    Parameters
    ----------
    brand
        A validated brand object.
    mode_scopes
        A mapping with exactly ``"light"`` and ``"dark"`` values. An empty
        value emits variables under ``:root``. ``"prefers-color-scheme"``
        emits a matching media query. Any other value is used as a CSS
        selector.

    Returns
    -------
    :
        CSS rules containing brand custom properties for both color modes.
    """
    scopes = _validate_mode_scopes(mode_scopes)
    return "\n".join(
        _css_scope(_css_declarations(brand, mode), scopes[mode], mode)
        for mode in ("light", "dark")
    )


def _validate_mode_scopes(
    mode_scopes: Mapping[ColorMode, str] | None,
) -> dict[ColorMode, str]:
    if mode_scopes is None:
        return DEFAULT_MODE_SCOPES.copy()

    if set(mode_scopes) != {"light", "dark"}:
        raise ValueError(
            "`mode_scopes` must contain exactly `light` and `dark`."
        )

    scopes: dict[ColorMode, str] = {}
    for mode in ("light", "dark"):
        scope = mode_scopes[mode]
        if not isinstance(scope, str):
            raise TypeError(f"`mode_scopes[{mode!r}]` must be a string.")
        scopes[mode] = scope
    return scopes


def _select_color(value: str | BrandColorLightDark, mode: ColorMode) -> str:
    if isinstance(value, str):
        return value

    fallback_mode: ColorMode = "dark" if mode == "light" else "light"
    selected = getattr(value, mode) or getattr(value, fallback_mode)
    if selected is None:  # Validation requires at least one variant.
        raise ValueError("A light/dark color must define at least one variant.")
    return selected


def _css_declarations(brand: Brand, mode: ColorMode) -> list[str]:
    declarations: dict[str, str] = {}

    if brand.color is not None:
        for name, value in (brand.color.palette or {}).items():
            declarations[f"--brand-{name}"] = value

        for name in brand.color.__class__.model_fields:
            if name == "palette":
                continue
            value = getattr(brand.color, name)
            if value is not None:
                declarations[f"--brand-color-{name.replace('_', '-')}"] = (
                    _select_color(value, mode)
                )

    if brand.typography is not None:
        for field in brand.typography.__class__.model_fields:
            typography_node = getattr(brand.typography, field)
            if not isinstance(typography_node, BaseModel):
                continue

            for property_name in ("color", "background_color"):
                value = getattr(typography_node, property_name, None)
                if value is None:
                    continue
                variable = (
                    f"--brand-typography-{field.replace('_', '-')}-"
                    f"{property_name.replace('_', '-')}"
                )
                declarations[variable] = _select_color(value, mode)

    return [f"  {name}: {value};" for name, value in declarations.items()]


def _css_scope(
    declarations: list[str],
    scope: str,
    mode: ColorMode,
) -> str:
    selector = ":root" if scope in ("", "prefers-color-scheme") else scope
    block = "\n".join([f"{selector} {{", *declarations, "}"])

    if scope != "prefers-color-scheme":
        return block

    indented = "\n".join(f"  {line}" for line in block.splitlines())
    return f"@media (prefers-color-scheme: {mode}) {{\n{indented}\n}}"
