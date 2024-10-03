from __future__ import annotations

import pytest
from brand_yaml._defs import CircularReferenceError, check_circular_references


def test_brand_with_errors_on_circular_references():
    with pytest.raises(CircularReferenceError, match="a -> b -> a"):
        check_circular_references({"a": "b", "b": "a"})

    with pytest.raises(CircularReferenceError, match="a -> b -> c -> a"):
        check_circular_references({"a": "b", "b": "c", "c": "a"})

    with pytest.raises(CircularReferenceError, match="a -> d -> b -> a"):
        check_circular_references(
            {"a": "d", "b": "a", "d": {"x": "e", "y": "b"}}
        )
