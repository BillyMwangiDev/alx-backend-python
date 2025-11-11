#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient module."""

from typing import Dict
from unittest.mock import patch, PropertyMock

import pytest

from client import GithubOrgClient


@patch("client.get_json")
def test_org_fetch(mock_get_json) -> None:
    """GithubOrgClient.org should delegate to get_json once."""
    payload: Dict[str, str] = {"repos_url": "https://example.com/repos"}
    mock_get_json.return_value = payload

    client = GithubOrgClient("google")
    assert client.org == payload
    mock_get_json.assert_called_once_with("https://api.github.com/orgs/google")


@patch("client.GithubOrgClient.repos_payload", new_callable=PropertyMock)
def test_public_repos(mock_repos_payload) -> None:
    """public_repos should return repository names from payload."""
    mock_repos_payload.return_value = [
        {"name": "repo1"},
        {"name": "repo2"},
    ]

    client = GithubOrgClient("google")
    assert client.public_repos() == ["repo1", "repo2"]


@pytest.mark.parametrize(
    "repo, license_key, expected",
    [
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"key": "bsd-3-clause"}}, "apache-2.0", False),
        ({}, "apache-2.0", False),
    ],
)
def test_has_license(repo: Dict, license_key: str, expected: bool) -> None:
    """has_license should return True only when license matches."""
    client = GithubOrgClient("google")
    assert client.has_license(repo, license_key) is expected


def test_has_license_none_key() -> None:
    """has_license should raise ValueError when license_key is None."""
    client = GithubOrgClient("google")
    with pytest.raises(ValueError):
        client.has_license({}, None)  # type: ignore[arg-type]
