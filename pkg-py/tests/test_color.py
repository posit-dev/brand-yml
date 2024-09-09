from __future__ import annotations

from utils import path_examples

from brand_yaml import read_brand_yaml


def test_brand_color_posit_direct():
    brand = read_brand_yaml(path_examples("brand-color-posit-direct.yml"))

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


def test_brand_color_posit_with():
    brand = read_brand_yaml(path_examples("brand-color-posit-with.yml"))

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

    assert brand.color.with_ is not None
    assert brand.color.with_ == {
        "white": "#FFFFFF",
        "black": "#151515",
        "blue": "#447099",
        "orange": "#EE6331",
        "green": "#72994E",
        "teal": "#419599",
        "burgundy": "#9A4665",
    }


def test_brand_color_posit_internal():
    brand = read_brand_yaml(path_examples("brand-color-posit-internal.yml"))

    # Named theme colors are reused in BrandColor
    assert brand.color is not None
    assert brand.color.background == "#FFFFFF"
    assert brand.color.primary == "#447099"
    assert brand.color.info == brand.color.primary
    assert brand.color.light == brand.color.background

    assert brand.color.with_ is not None
    assert brand.color.with_ == {
        "white": "#FFFFFF",
        "black": "#151515",
        "blue": "#447099",
        "orange": "#EE6331",
        "green": "#72994E",
        "teal": "#419599",
        "burgundy": "#9A4665",
    }
