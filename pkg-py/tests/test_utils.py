from __future__ import annotations

import logging
from typing import Union

from brand_yaml._brand_utils import BrandLightDarkString, BrandWith

logging.basicConfig(level=logging.DEBUG)


def test_brand_with_simple():
    class BrandThing(BrandWith[str]):
        small: str = None
        medium: str = None
        large: str = None

    thing = BrandThing(
        with_={"sm": "small", "md": "medium", "lg": "large"},
        small="sm",
        medium="md",
        large="lg",
    )

    assert thing.small == "small"
    assert thing.medium == "medium"
    assert thing.large == "large"


def test_brand_with_simple_mixed():
    class BrandThing(BrandWith[str]):
        small: str = None
        medium: str = None
        large: str = None

    thing = BrandThing(
        with_={"sm": "small", "md": "medium", "lg": "large"},
        small="lg",
        medium="middle",
        large="LG",
    )

    assert thing.small == "large"
    assert thing.medium == "middle"
    assert thing.large == "LG"


def test_brand_with_dict():
    class BrandThing(BrandWith[str]):
        small: dict[str, str] = None
        medium: dict[str, str] = None

    thing = BrandThing(
        with_={"sm": "small", "md": "medium", "lg": "large"},
        small={"one": "sm", "two": "md"},
        medium={"three": "md"},
    )

    assert thing.small == {"one": "small", "two": "medium"}
    assert thing.medium == {"three": "medium"}


def test_brand_with_basemodel():
    class BrandThing(BrandWith[Union[str, BrandLightDarkString]]):
        small: Union[str, BrandLightDarkString] = None
        medium: Union[str, BrandLightDarkString] = None

    thing = BrandThing(
        with_={
            "sm": "small-light",
            "md": {"light": "medium-light", "dark": "medium-dark"}
        },
        small={"light": "sm", "dark": "small-dark"},
        medium="md",
    )

    assert thing.small.light == "small-light"
    assert thing.small.dark == "small-dark"
    assert thing.medium.light == "medium-light"
    assert thing.medium.dark == "medium-dark"

    assert isinstance(thing.small, BrandLightDarkString)
    assert isinstance(thing.medium, BrandLightDarkString)