#!/usr/bin/env python3
"""Utility helpers for interacting with GitHub API payloads."""
from functools import wraps
from typing import Any, Callable, Dict, Mapping, Sequence

import requests

__all__ = ["access_nested_map", "get_json", "memoize"]


def access_nested_map(
    nested_map: Mapping[str, Any],
    path: Sequence[str],
) -> Any:
    """Return the value found at the provided key path inside nested_map."""
    current: Any = nested_map
    for key in path:
        if not isinstance(current, Mapping):
            raise KeyError(key)
        current = current[key]
    return current


def get_json(url: str) -> Dict[str, Any]:
    """Perform a GET request against url and return the decoded JSON payload."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def memoize(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Convert an instance method into a cached property."""
    cache_attr = f"_{fn.__name__}"

    @wraps(fn)
    def memoized(self: Any) -> Any:
        """Compute, store, and return fn result on first access."""
        if not hasattr(self, cache_attr):
            setattr(self, cache_attr, fn(self))
        return getattr(self, cache_attr)

    return property(memoized)
