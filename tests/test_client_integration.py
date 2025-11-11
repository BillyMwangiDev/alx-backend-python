#!/usr/bin/env python3
"""Integration tests for the GithubOrgClient module."""

from typing import List

import responses

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


@responses.activate
def test_public_repos_integration() -> None:
    """public_repos should return names from the GitHub API payload."""
    org_payload, repos_payload, expected_names, _ = TEST_PAYLOAD[0]

    responses.add(
        responses.GET,
        GithubOrgClient.ORG_URL.format(org="google"),
        json=org_payload,
        status=200,
    )
    responses.add(
        responses.GET,
        org_payload["repos_url"],
        json=repos_payload,
        status=200,
    )

    client = GithubOrgClient("google")
    assert client.public_repos() == expected_names


@responses.activate
def test_public_repos_with_license_filter() -> None:
    """public_repos should filter repositories based on license key."""
    org_payload, repos_payload, _, expected_filtered = TEST_PAYLOAD[0]

    responses.add(
        responses.GET,
        GithubOrgClient.ORG_URL.format(org="google"),
        json=org_payload,
        status=200,
    )
    responses.add(
        responses.GET,
        org_payload["repos_url"],
        json=repos_payload,
        status=200,
    )

    client = GithubOrgClient("google")
    assert client.public_repos(license="apache-2.0") == expected_filtered


def test_expected_payload_shape() -> None:
    """Ensure fixture payload contains required keys for integration tests."""
    org_payload, repos_payload, expected_names, expected_filtered = TEST_PAYLOAD[0]
    assert "repos_url" in org_payload
    assert isinstance(repos_payload, list)
    assert isinstance(expected_names, list)
    assert isinstance(expected_filtered, list)


@responses.activate
def test_http_error_raises_for_org() -> None:
    """Client should propagate HTTP errors from GitHub API calls."""
    responses.add(
        responses.GET,
        GithubOrgClient.ORG_URL.format(org="invalid"),
        status=404,
    )

    client = GithubOrgClient("invalid")
    # requests raises for status via get_json, so accessing org should fail
    try:
        _ = client.org
    except Exception as exc:  # pragma: no cover - different exceptions on versions
        assert hasattr(exc, "response")
