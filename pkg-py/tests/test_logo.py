from __future__ import annotations

from utils import path_examples

from brand_yaml import read_brand_yaml
from brand_yaml._defs import BrandLightDark
from brand_yaml.logo import BrandLogo


def test_brand_logo_single():
    brand = read_brand_yaml(path_examples("brand-logo-single.yml"))

    assert brand.logo == "posit.png"


def test_brand_logo_simple():
    brand = read_brand_yaml(path_examples("brand-logo-simple.yml"))

    assert isinstance(brand.logo, BrandLogo)
    assert brand.logo.small == "icon.png"
    assert brand.logo.medium == "logo.png"
    assert brand.logo.large == "display.svg"


def test_brand_logo_light_dark():
    brand = read_brand_yaml(path_examples("brand-logo-light-dark.yml"))

    assert isinstance(brand.logo, BrandLogo)
    assert brand.logo.small == "icon.png"

    assert isinstance(brand.logo.medium, BrandLightDark)
    assert brand.logo.medium.light == "logo-light.png"
    assert brand.logo.medium.dark == "logo-dark.png"

    assert brand.logo.large == "display.svg"


def test_brand_logo_full():
    brand = read_brand_yaml(path_examples("brand-logo-full.yml"))

    assert isinstance(brand.logo, BrandLogo)
    assert brand.logo.small == "favicon.png"

    assert isinstance(brand.logo.medium, BrandLightDark)
    assert brand.logo.medium.light == "full-color.png"
    assert brand.logo.medium.dark == "full-color-reverse.png"

    assert brand.logo.large == "full-color.svg"

    # replace small with new value from "with"
    brand.logo.small = "black"
    assert brand.logo.small == "black.png"
