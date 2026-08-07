from typing import Any

import pytest
from brand_yml import Brand, brand_css_variables


@pytest.fixture
def brand() -> Brand:
    return Brand.from_yaml_str(
        """
color:
  palette:
    red: "#ff0000"
  foreground:
    light: "#111111"
    dark: "#eeeeee"
  background:
    light: "#ffffff"
  primary: "#0066cc"
typography:
  headings:
    color: foreground
  link:
    color:
      light: primary
      dark: "#66b2ff"
"""
    )


def test_css_variables_uses_root_and_system_preference_by_default(
    brand: Brand,
):
    css = brand.css_variables()

    assert ":root {" in css
    assert "--brand-red: #ff0000;" in css
    assert "--brand-color-foreground: #111111;" in css
    assert "--brand-typography-headings-color: #111111;" in css
    assert "@media (prefers-color-scheme: dark)" in css
    assert "--brand-color-background: #ffffff;" in css
    assert "--brand-typography-link-color: #66b2ff;" in css


def test_css_variables_uses_custom_selectors(brand: Brand):
    css = brand_css_variables(
        brand,
        mode_scopes={
            "light": ".quarto-light",
            "dark": ".quarto-dark",
        },
    )

    assert ".quarto-light {" in css
    assert ".quarto-dark {" in css
    assert "@media" not in css


def test_css_variables_uses_branch_name_for_media_query(brand: Brand):
    css = brand.css_variables(
        mode_scopes={
            "light": "prefers-color-scheme",
            "dark": "",
        }
    )

    assert "@media (prefers-color-scheme: light)" in css


def test_css_variables_validates_mode_scopes(brand: Brand):
    missing_scope: Any = {"light": ""}
    with pytest.raises(ValueError, match="exactly.*light.*dark"):
        brand.css_variables(missing_scope)

    invalid_scope: Any = {"light": "", "dark": 42}
    with pytest.raises(TypeError, match=r"mode_scopes\['dark'\]"):
        brand.css_variables(invalid_scope)


def test_css_variables_emits_complete_sets_for_each_mode(brand: Brand):
    css = brand.css_variables({"light": ".light", "dark": ".dark"})
    light, dark = css.split("\n.dark {")

    light_names = {
        line.strip().split(":", 1)[0]
        for line in light.splitlines()
        if line.strip().startswith("--")
    }
    dark_names = {
        line.strip().split(":", 1)[0]
        for line in dark.splitlines()
        if line.strip().startswith("--")
    }

    assert light_names == dark_names
