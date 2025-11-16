#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient helper."""

import os
import sys
from typing import Dict
import unittest

from unittest.mock import Mock, PropertyMock, call, patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from client import GithubOrgClient  # noqa: E402
from fixtures import TEST_PAYLOAD  # noqa: E402


class TestGithubOrgClient(unittest.TestCase):
    """Test cases covering the GithubOrgClient behaviors."""

    def test_org(self) -> None:
        """GithubOrgClient.org should retrieve organization JSON once."""
        cases = [
            ("google", {"login": "google"}),
            ("abc", {"login": "abc"}),
        ]
        for org_name, payload in cases:
            with self.subTest(org=org_name):
                with patch("client.get_json") as mock_get_json:
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

    def test_public_repos(self) -> None:
        """public_repos should list repository names from API payload."""
        repos_payload = [
            {"name": "repo-one"},
            {"name": "repo-two"},
            {"name": "repo-three"},
        ]
        expected_url = "https://api.github.com/orgs/google/repos"
        with patch("client.get_json") as mock_get_json:
            mock_get_json.return_value = repos_payload
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

    def test_has_license(self):
        """has_license should report whether repo has the provided license."""
        cases = [
            ({"license": {"key": "my_license"}}, "my_license", True),
            ({"license": {"key": "other_license"}}, "my_license", False),
        ]
        for repo, license_key, expected in cases:
            with self.subTest(repo=repo, license_key=license_key):
                self.assertEqual(
                    GithubOrgClient.has_license(repo, license_key),
                    expected,
                )


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient relying on fixtures."""

    def test_public_repos(self):
        """public_repos should return repository names from fixtures."""
        for org_payload, repos_payload, expected_repos, _ in TEST_PAYLOAD:
            with self.subTest(payload=org_payload):
                def _mock_get(url, *args, **kwargs):
                    response = Mock()
                    if url == GithubOrgClient.ORG_URL.format(org="google"):
                        response.json.return_value = org_payload
                    elif url == org_payload["repos_url"]:
                        response.json.return_value = repos_payload
                    else:
                        response.json.return_value = {}
                    return response
                with patch("requests.get") as mock_get:
                    mock_get.side_effect = _mock_get
                    client = GithubOrgClient("google")
                    self.assertEqual(client.public_repos(), expected_repos)
                    self.assertEqual(
                        mock_get.call_args_list,
                        [
                            call(GithubOrgClient.ORG_URL.format(org="google"), timeout=10),
                            call(org_payload["repos_url"], timeout=10),
                        ],
                    )

    def test_public_repos_with_license(self):
        """public_repos should filter repositories by license when provided."""
        for org_payload, repos_payload, _, apache2_repos in TEST_PAYLOAD:
            with self.subTest(payload=org_payload):
                def _mock_get(url, *args, **kwargs):
                    response = Mock()
                    if url == GithubOrgClient.ORG_URL.format(org="google"):
                        response.json.return_value = org_payload
                    elif url == org_payload["repos_url"]:
                        response.json.return_value = repos_payload
                    else:
                        response.json.return_value = {}
                    return response
                with patch("requests.get") as mock_get:
                    mock_get.side_effect = _mock_get
                    client = GithubOrgClient("google")
                    self.assertEqual(
                        client.public_repos(license="apache-2.0"),
                        apache2_repos,
                    )


if __name__ == "__main__":
    unittest.main()
