from __future__ import annotations

import pytest
from brand_yml import Brand, BrandColor
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
