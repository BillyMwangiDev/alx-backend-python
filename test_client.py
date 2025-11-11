#!/usr/bin/env python3
"""Compatibility wrapper for running test_client via unittest discovery."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = (
    Path(__file__).resolve().parent
    / "0x03-Unittests_and_integration_tests"
    / "test_client.py"
)
SPEC = importlib.util.spec_from_file_location(
    "compat_test_client",
    MODULE_PATH,
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None  # noqa: S101 - guard for type checkers
sys.modules["compat_test_client"] = MODULE
SPEC.loader.exec_module(MODULE)

globals().update({
    name: getattr(MODULE, name)
    for name in dir(MODULE)
    if not name.startswith("_")
})

__all__ = [name for name in globals() if name.startswith("Test")]


if __name__ == "__main__":
    unittest.main(module=MODULE)
