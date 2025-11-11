#!/usr/bin/env python3
"""Unit tests for utility helpers."""

from typing import Any, Dict

import pytest

from utils import access_nested_map, memoize


def test_access_nested_map_success() -> None:
    """access_nested_map should return the value for an existing path."""
    nested: Dict[str, Any] = {"a": {"b": {"c": 1}}}
    assert access_nested_map(nested, ("a", "b", "c")) == 1


def test_access_nested_map_missing_key() -> None:
    """access_nested_map should raise KeyError for an invalid path."""
    nested: Dict[str, Any] = {"a": 1}
    with pytest.raises(KeyError):
        access_nested_map(nested, ("a", "b"))


def test_memoize_decorator() -> None:
    """memoize should cache method results on the instance."""

    class Sample:
        """Sample class exposing a memoized method."""

        def __init__(self) -> None:
            self.calls: int = 0

        @memoize
        def expensive(self) -> int:
            """Increment call counter and return constant value."""
            self.calls += 1
            return 42

    sample = Sample()
    assert sample.expensive == 42
    assert sample.calls == 1
    assert sample.expensive == 42
    assert sample.calls == 1
