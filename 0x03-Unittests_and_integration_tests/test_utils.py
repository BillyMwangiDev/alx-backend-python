#!/usr/bin/env python3
"""Unit tests for the access_nested_map utility."""

import unittest

from parameterized import parameterized

from unittest.mock import patch

from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test suite for the access_nested_map helper."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """access_nested_map should return the expected value."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """access_nested_map should raise KeyError when key is missing."""
        with self.assertRaises(KeyError) as ctx:
            access_nested_map(nested_map, path)
        self.assertEqual(str(ctx.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Tests for the get_json helper."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """get_json should fetch and return JSON payloads."""
        with patch("utils.requests.get") as mock_get:
            mock_get.return_value.json.return_value = test_payload
            self.assertEqual(get_json(test_url), test_payload)
            mock_get.assert_called_once_with(test_url, timeout=10)


class TestMemoize(unittest.TestCase):
    """Tests for the memoize decorator."""

    def test_memoize(self):
        """memoize should cache the result of the wrapped method."""

        class TestClass:
            """Sample class to exercise memoize decorator."""

            def a_method(self) -> int:
                """Return a sentinel integer value."""
                return 42

            @memoize
            def a_property(self) -> int:
                """Return memoized result of a_method."""
                return self.a_method()

        instance = TestClass()

        with patch.object(TestClass, "a_method", return_value=42) as mocked_method:
            self.assertEqual(instance.a_property, 42)
            self.assertEqual(instance.a_property, 42)
            mocked_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
