from __future__ import annotations

from typing import Union

import pytest

from brand_yaml._defs import (
    BrandLightDarkString,
    BrandWith,
    CircularReferenceError,
)

# from brand_yaml._utils_logging import log_set_debug
# log_set_debug()


def test_brand_with_simple():
    class BrandThing(BrandWith[str]):
        small: str | None = None
        medium: str | None = None
        large: str | None = None

    thing = BrandThing.model_validate(
        {
            "with_": {"sm": "small", "md": "medium", "lg": "large"},
            "small": "sm",
            "medium": "md",
            "large": "lg",
        }
    )

    assert thing.small == "small"
    assert thing.medium == "medium"
    assert thing.large == "large"


def test_brand_with_simple_mixed():
    class BrandThing(BrandWith[str]):
        small: str | None = None
        medium: str | None = None
        large: str | None = None

    thing = BrandThing.model_validate(
        {
            "with_": {"sm": "small", "md": "medium", "lg": "large"},
            "small": "lg",
            "medium": "middle",
            "large": "LG",
        }
    )

    assert thing.small == "large"
    assert thing.medium == "middle"
    assert thing.large == "LG"


def test_brand_with_dict():
    class BrandThing(BrandWith[str]):
        small: dict[str, str] | None = None
        medium: dict[str, str] | None = None

    thing = BrandThing.model_validate(
        {
            "with_": {"sm": "small", "md": "medium", "lg": "large"},
            "small": {"one": "sm", "two": "md"},
            "medium": {"three": "md"},
        }
    )

    assert thing.small == {"one": "small", "two": "medium"}
    assert thing.medium == {"three": "medium"}


def test_brand_with_basemodel():
    class BrandThing(BrandWith[Union[str, BrandLightDarkString]]):
        small: str | BrandLightDarkString | None = None
        medium: str | BrandLightDarkString | None = None

    thing = BrandThing.model_validate(
        {
            "with_": {
                "sm": "small-light",
                "md": {"light": "medium-light", "dark": "medium-dark"},
            },
            "small": {"light": "sm", "dark": "small-dark"},
            "medium": "md",
        }
    )

    assert isinstance(thing.small, BrandLightDarkString)
    assert isinstance(thing.medium, BrandLightDarkString)

    assert thing.small.light == "small-light"
    assert thing.small.dark == "small-dark"
    assert thing.medium.light == "medium-light"
    assert thing.medium.dark == "medium-dark"


def test_brand_with_nested():
    class BrandThing(BrandWith[Union[str, BrandLightDarkString]]):
        the: str | BrandLightDarkString | None = None

    thing = BrandThing.model_validate(
        {
            "with_": {
                "light": "the-light",
                "dark": "the-dark",
                "both": {"light": "the-light", "dark": "the-dark"},
            },
            "the": "both",
        }
    )

    assert thing.with_ is not None
    assert isinstance(thing.with_["both"], BrandLightDarkString)
    assert isinstance(thing.the, BrandLightDarkString)

    assert thing.the == thing.with_["both"]
    assert thing.with_["both"].light == "the-light"
    assert thing.with_["both"].dark == "the-dark"


def test_brand_with_errors_on_circular_references():
    with pytest.raises(CircularReferenceError, match="a -> b -> a"):
        BrandWith.model_validate({"with_": {"a": "b", "b": "a"}})

    with pytest.raises(CircularReferenceError, match="a -> b -> c -> a"):
        BrandWith.model_validate({"with_": {"a": "b", "b": "c", "c": "a"}})

    with pytest.raises(CircularReferenceError, match="a -> d -> b -> a"):
        BrandWith.model_validate(
            {"with_": {"a": "d", "b": "a", "d": {"x": "e", "y": "b"}}}
        )
