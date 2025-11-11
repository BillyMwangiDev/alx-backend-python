#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient helper."""

import os
import sys
from typing import Dict
import unittest

from parameterized import parameterized, parameterized_class
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
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

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


@parameterized_class([
    {
        "org_payload": payload,
        "repos_payload": repos,
        "expected_repos": expected,
        "apache2_repos": apache2,
    }
    for payload, repos, expected, apache2 in TEST_PAYLOAD
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient relying on fixtures."""

    @classmethod
    def setUpClass(cls):
        """Start patcher that mocks requests.get across the module."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def _mock_get(url, *args, **kwargs):
            response = Mock()
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                response.json.return_value = cls.repos_payload
            else:
                response.json.return_value = {}
            return response

        cls.mock_get.side_effect = _mock_get

    @classmethod
    def tearDownClass(cls):
        """Stop patcher created in setUpClass."""
        cls.get_patcher.stop()

    def setUp(self) -> None:
        """Reset mock call history before each test."""
        self.mock_get.reset_mock()

    def test_public_repos(self):
        """public_repos should return repository names from fixtures."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)
        self.assertEqual(
            self.mock_get.call_args_list,
            [
                call(GithubOrgClient.ORG_URL.format(org="google"), timeout=10),
                call(self.org_payload["repos_url"], timeout=10),
            ],
        )

    def test_public_repos_with_license(self):
        """public_repos should filter repositories by license when provided."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos,
        )


if __name__ == "__main__":
    unittest.main()