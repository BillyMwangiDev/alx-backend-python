#!/usr/bin/env python3
"""Run a sample query against the GitHub Org API."""

from client import GithubOrgClient


def main() -> None:
    """Fetch and print public repositories for the Google organization."""
    client = GithubOrgClient("google")
    for name in client.public_repos():
        print(name)


if __name__ == "__main__":
    main()
