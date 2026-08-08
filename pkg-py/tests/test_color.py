from __future__ import annotations

import warnings

import pytest
from brand_yml import Brand, BrandColor
from brand_yml.color import BrandColorLightDark
from syrupy.extensions.json import JSONSnapshotExtension
from utils import path_examples, pydantic_data_from_json


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)


def test_brand_color_ex_direct_posit(snapshot_json):
    brand = Brand.from_yaml(path_examples("brand-color-direct-posit.yml"))

    assert brand.color is not None
    assert brand.color.foreground == "#151515"
    assert brand.color.background == "#FFFFFF"
    assert brand.color.primary == "#447099"
    assert brand.color.secondary == "#707073"
    assert brand.color.tertiary == "#C2C2C4"
    assert brand.color.success == "#72994E"
    assert brand.color.info == "#419599"
    assert brand.color.warning == "#EE6331"
    assert brand.color.danger == "#9A4665"
    assert brand.color.light == "#FFFFFF"
    assert brand.color.dark == "#404041"

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_color_ex_palette_posit(snapshot_json):
    brand = Brand.from_yaml(path_examples("brand-color-palette-posit.yml"))

    # Same final values as above, but re-uses color definitions from `with`
    assert brand.color is not None
    assert brand.color.foreground == "#151515"
    assert brand.color.background == "#FFFFFF"
    assert brand.color.primary == "#447099"
    assert brand.color.secondary == "#707073"
    assert brand.color.tertiary == "#C2C2C4"
    assert brand.color.success == "#72994E"
    assert brand.color.info == "#419599"
    assert brand.color.warning == "#EE6331"
    assert brand.color.danger == "#9A4665"
    assert brand.color.light == "#FFFFFF"
    assert brand.color.dark == "#404041"

    assert brand.color.palette is not None
    assert brand.color.palette == {
        "white": "#FFFFFF",
        "black": "#151515",
        "blue": "#447099",
        "orange": "#EE6331",
        "green": "#72994E",
        "teal": "#419599",
        "burgundy": "#9A4665",
    }

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_color_ex_palette_internal(snapshot_json):
    brand = Brand.from_yaml(path_examples("brand-color-palette-internal.yml"))

    # Named theme colors are reused in BrandColor
    assert brand.color is not None
    assert brand.color.background == "#FFFFFF"
    assert brand.color.primary == "#447099"
    assert brand.color.info == brand.color.primary
    assert brand.color.light == brand.color.background

    assert brand.color.palette is not None
    assert brand.color.palette == {
        "white": "#FFFFFF",
        "black": "#151515",
        "blue": "#447099",
        "orange": "#EE6331",
        "green": "#72994E",
        "teal": "#419599",
        "burgundy": "#9A4665",
    }

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_to_dict():
    brand = Brand.from_yaml_str(
        """
        color:
          palette:
            red: "#f00"
            green: "#0f0"
            blue: "#00f"
            azul: blue
            tertiary: "#f0f"
          primary: red
          secondary: green
          tertiary: blue
        """
    )

    assert isinstance(brand.color, BrandColor)
    assert brand.color.to_dict(include="theme") == {
        "primary": "#f00",
        "secondary": "#0f0",
        "tertiary": "#00f",
    }

    assert brand.color.to_dict(include="theme") == {
        "primary": "#f00",
        "secondary": "#0f0",
        "tertiary": "#00f",
    }

    assert brand.color.palette is not None
    # color palette values are resolved on model validation (may change)
    assert brand.color.palette["azul"] == "#00f"

    assert brand.color.to_dict(include="palette") == {
        "red": "#f00",
        "green": "#0f0",
        "blue": "#00f",
        "azul": "#00f",
        "tertiary": "#f0f",
    }

    assert brand.color.to_dict(include="all") == {
        "red": "#f00",
        "green": "#0f0",
        "blue": "#00f",
        "azul": "#00f",
        "primary": "#f00",
        "secondary": "#0f0",
        "tertiary": "#00f",  # brand.color.tertiary wins!
    }


def test_brand_color_palette_names_valid_sass_vars():
    with pytest.raises(ValueError):
        Brand.from_yaml_str(
            """
            color:
              palette:
                "my pink": "#f0f"
            """
        )

    brand = Brand.from_yaml_str(
        """
        color:
          palette:
            my_pink: "#f0f"
        """
    )
    assert isinstance(brand.color, BrandColor)
    assert brand.color.palette == {"my_pink": "#f0f"}


def test_brand_color_light_dark_variants():
    """Test that light/dark color variants parse correctly."""
    brand = Brand.from_yaml_str(
        """
        color:
          foreground:
            light: "#111111"
            dark: "#fafafa"
          background:
            light: "#FFFFFF"
            dark: "#222222"
          primary: "#6339E0"
        """
    )

    assert isinstance(brand.color, BrandColor)

    # Check that light/dark colors are parsed correctly
    assert isinstance(brand.color.foreground, BrandColorLightDark)
    assert brand.color.foreground.light == "#111111"
    assert brand.color.foreground.dark == "#fafafa"

    assert isinstance(brand.color.background, BrandColorLightDark)
    assert brand.color.background.light == "#FFFFFF"
    assert brand.color.background.dark == "#222222"

    # Check that scalar colors still work
    assert isinstance(brand.color.primary, str)
    assert brand.color.primary == "#6339E0"


def test_brand_color_light_dark_with_references():
    """Test that light/dark colors work with palette references."""
    brand = Brand.from_yaml_str(
        """
        color:
          palette:
            purple: "#6339E0"
            sky: "#87CEEB"
            ocean: "#4A90A4"
          foreground:
            light: "#111111"
            dark: "#fafafa"
          primary: purple
          secondary:
            light: sky
            dark: ocean
        """
    )

    assert isinstance(brand.color, BrandColor)

    # Primary references a palette color directly
    assert brand.color.primary == "#6339E0"

    # Secondary has light/dark variants referencing palette colors
    assert isinstance(brand.color.secondary, BrandColorLightDark)
    assert brand.color.secondary.light == "#87CEEB"
    assert brand.color.secondary.dark == "#4A90A4"


def test_brand_color_light_dark_references_use_variant_context():
    brand = Brand.from_yaml_str(
        """
        color:
          primary:
            light: "#111111"
            dark: "#eeeeee"
          secondary:
            light: primary
            dark: primary
          tertiary:
            dark: primary
        """
    )

    assert isinstance(brand.color, BrandColor)
    assert isinstance(brand.color.secondary, BrandColorLightDark)
    assert brand.color.secondary.light == "#111111"
    assert brand.color.secondary.dark == "#eeeeee"

    assert isinstance(brand.color.tertiary, BrandColorLightDark)
    assert brand.color.tertiary.dark == "#eeeeee"


def test_brand_color_light_dark_references_preserve_undefined_variants():
    brand = Brand.from_yaml_str(
        """
        color:
          primary:
            dark: "#eeeeee"
          secondary:
            light: primary
            dark: primary
        typography:
          headings:
            color: primary
        """
    )

    assert brand.color is not None
    assert isinstance(brand.color.secondary, BrandColorLightDark)
    assert brand.color.secondary.light is None
    assert brand.color.secondary.dark == "#eeeeee"

    assert brand.typography is not None
    assert brand.typography.headings is not None
    assert isinstance(brand.typography.headings.color, BrandColorLightDark)
    assert brand.typography.headings.color.light is None
    assert brand.typography.headings.color.dark == "#eeeeee"


def test_brand_color_light_dark_removes_references_with_no_resolved_variants():
    brand = Brand.from_yaml_str(
        """
        color:
          primary:
            dark: "#eeeeee"
          secondary:
            light: primary
        """
    )

    assert brand.color is not None
    assert brand.color.secondary is None


def test_brand_color_light_dark_references_detect_cycles():
    with pytest.raises(ValueError, match="primary -> secondary -> primary"):
        Brand.from_yaml_str(
            """
            color:
              primary:
                light: secondary
                dark: "#eeeeee"
              secondary:
                light: primary
                dark: "#dddddd"
            """
        )


def test_brand_color_light_dark_example_file(snapshot_json):
    """Test the brand-color-light-dark.yml example file."""
    brand = Brand.from_yaml(path_examples("brand-color-light-dark.yml"))

    assert brand.color is not None
    assert brand.meta is not None
    assert brand.meta.name is not None
    assert brand.meta.name.full == "Light/Dark Color Variants Example"

    # Check light/dark colors
    assert isinstance(brand.color.foreground, BrandColorLightDark)
    assert brand.color.foreground.light == "#111111"
    assert brand.color.foreground.dark == "#fafafa"

    assert isinstance(brand.color.background, BrandColorLightDark)
    assert brand.color.background.light == "#FFFFFF"
    assert brand.color.background.dark == "#222222"

    # Check scalar color (primary)
    assert brand.color.primary == "#6339E0"

    # Check secondary with light/dark variants
    assert isinstance(brand.color.secondary, BrandColorLightDark)
    assert brand.color.secondary.light == "#87CEEB"
    assert brand.color.secondary.dark == "#4A90A4"

    # Check typography colors - these are resolved from color references
    assert brand.typography is not None
    assert brand.typography.headings is not None
    headings_color = brand.typography.headings.color
    assert isinstance(headings_color, BrandColorLightDark)
    assert headings_color.light == "#111111"
    assert headings_color.dark == "#fafafa"

    assert brand.typography.link is not None
    assert brand.typography.link.color == "#6339E0"

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_typography_light_dark_references_use_variant_context():
    brand = Brand.from_yaml_str(
        """
        color:
          primary:
            light: "#0066cc"
            dark: "#66b2ff"
        typography:
          link:
            color:
              light: primary
              dark: primary
        """
    )

    assert brand.typography is not None
    assert brand.typography.link is not None
    assert isinstance(brand.typography.link.color, BrandColorLightDark)
    assert brand.typography.link.color.light == "#0066cc"
    assert brand.typography.link.color.dark == "#66b2ff"

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        dumped = brand.model_dump(mode="json", by_alias=True, exclude_none=True)

    round_trip = Brand.model_validate(dumped)
    assert round_trip.typography is not None
    assert round_trip.typography.link is not None
    assert isinstance(round_trip.typography.link.color, BrandColorLightDark)


def test_brand_color_to_dict_with_light_dark():
    """Test that to_dict() handles light/dark colors correctly."""
    brand = Brand.from_yaml_str(
        """
        color:
          palette:
            purple: "#6339E0"
          foreground:
            light: "#111111"
            dark: "#fafafa"
          primary: purple
        """
    )

    assert isinstance(brand.color, BrandColor)

    # Theme colors should include light/dark structures
    theme_dict = brand.color.to_dict(include="theme")
    assert "foreground" in theme_dict
    assert isinstance(theme_dict["foreground"], dict)
    assert theme_dict["foreground"]["light"] == "#111111"
    assert theme_dict["foreground"]["dark"] == "#fafafa"
    assert theme_dict["primary"] == "#6339E0"

    # All colors should include both palette and theme
    all_dict = brand.color.to_dict(include="all")
    assert "purple" in all_dict
    assert "foreground" in all_dict
    assert "primary" in all_dict
