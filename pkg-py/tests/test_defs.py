from __future__ import annotations

import pytest
from brand_yaml._defs import (
    CircularReferenceError,
    check_circular_references,
    defs_get,
    defs_replace_recursively,
)
from pydantic import BaseModel


def test_brand_with_errors_on_circular_references():
    with pytest.raises(CircularReferenceError, match="a -> b -> a"):
        check_circular_references({"a": "b", "b": "a"})

    with pytest.raises(CircularReferenceError, match="a -> b -> c -> a"):
        check_circular_references({"a": "b", "b": "c", "c": "a"})

    with pytest.raises(CircularReferenceError, match="a -> d -> b -> a"):
        check_circular_references(
            {"a": "d", "b": "a", "d": {"x": "e", "y": {"y1": "b"}}}
        )

    try:
        check_circular_references({"a": "b", "b": 2})
    except Exception:
        assert False, "should not raise an error "


class MyThing(BaseModel):
    a: str | int
    b: str | int
    c: dict[str, str]
    d: dict[str, str | MySubThing]


class MySubThing(BaseModel):
    s1: str | None = None
    s2: str | None = None


def test_defs_replace_recursively():
    items = MyThing(
        a="a",
        b="b",
        c={"c1": "x", "c2": "y"},
        d={"d1": MySubThing(s1="s1", s2="s2")},
    )
    defs = {"a": 1, "b": 2, "x": "X", "s2": MySubThing(s2="SS22")}

    assert defs_get(defs, "y") == "y"

    defs_replace_recursively(items, defs)
    assert items.a == 1
    assert items.b == 2
    assert items.c == {"c1": "X", "c2": "y"}
    assert isinstance(items.d["d1"], MySubThing)
    assert items.d["d1"].model_dump(warnings=False) == {
        "s1": "s1",
        "s2": {"s1": None, "s2": "SS22"},
    }

    with pytest.raises(ValueError, match="must be a dictionary"):
        defs_replace_recursively(MySubThing(s2="foo"))

    assert defs_replace_recursively(None) is None
