#!/usr/bin/env python3
"""Client wrapper for interacting with GitHub organization resources."""

from typing import Dict, List, Optional

from decouple import config

from utils import access_nested_map, get_json, memoize


class GithubOrgClient:
    """Facade around the GitHub REST API for organization-scoped calls."""

    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str, token: Optional[str] = None) -> None:
        """Store organization identifier and optional GitHub token."""
        self._org_name = org_name
        self._token = token or config("GITHUB_TOKEN", default="", cast=str)

    @memoize
    def org(self) -> Dict[str, str]:
        """Fetch organization metadata once and memoize the payload."""
        return get_json(self.ORG_URL.format(org=self._org_name))

    @property
    def _public_repos_url(self) -> str:
        """Return the API endpoint listing public repositories."""
        return self.org["repos_url"]

    @memoize
    def repos_payload(self) -> List[Dict[str, Dict[str, str]]]:
        """Retrieve the list of repositories exposed at the org's repos URL."""
        return get_json(self._public_repos_url)

    def public_repos(self, license: Optional[str] = None) -> List[str]:
        """List public repository names, optionally filtered by license key."""
        return [
            repo["name"]
            for repo in self.repos_payload
            if license is None or self.has_license(repo, license)
        ]

    @staticmethod
    def has_license(
        repo: Dict[str, Dict[str, str]],
        license_key: str,
    ) -> bool:
        """Return True when repo contains license matching license_key."""
        if license_key is None:
            raise ValueError("license_key cannot be None")
        try:
            return access_nested_map(repo, ("license", "key")) == license_key
        except KeyError:
            return False
