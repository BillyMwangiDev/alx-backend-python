#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient helper."""

import os
import sys
from typing import Dict
import unittest

from parameterized import parameterized
from unittest.mock import Mock, PropertyMock, call, patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from client import GithubOrgClient  # noqa: E402
from fixtures import TEST_PAYLOAD  # noqa: E402


class TestGithubOrgClient(unittest.TestCase):
    """Test cases covering the GithubOrgClient behaviors."""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch("client.get_json")
    def test_org(
        self,
        org_name: str,
        payload: Dict[str, str],
        mock_get_json,
    ) -> None:
        """GithubOrgClient.org should retrieve organization JSON once."""
        mock_get_json.return_value = payload

        client = GithubOrgClient(org_name)

        self.assertEqual(client.org, payload)
        expected_url = "https://api.github.com/orgs/{}".format(org_name)
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        """Expose the repos_url retrieved from organization payload."""
        expected_url = "https://api.github.com/orgs/google/repos"
        payload = {"repos_url": expected_url}

        with patch.object(
            GithubOrgClient,
            "org",
            new_callable=PropertyMock,
            return_value=payload,
        ):
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, expected_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json) -> None:
        """public_repos should list repository names from API payload."""
        repos_payload = [
            {"name": "repo-one"},
            {"name": "repo-two"},
            {"name": "repo-three"},
        ]
        mock_get_json.return_value = repos_payload

        expected_url = "https://api.github.com/orgs/google/repos"

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value=expected_url,
        ) as mock_url:
            client = GithubOrgClient("google")
            self.assertEqual(
                client.public_repos(),
                [repo["name"] for repo in repos_payload],
            )
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(expected_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """has_license should report whether repo has the provided license."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected,
        )


# Integration tests are intentionally omitted in this ALX directory
# per the assignment scope focusing on unit tests.


if __name__ == "__main__":
    unittest.main()
