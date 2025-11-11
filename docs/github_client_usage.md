#!/usr/bin/env python3
"""Usage guide for the GitHub organization client."""

## Quickstart
1. Activate the Python 3.7 virtual environment.
2. Copy `.env.example` to `.env` and optionally set `GITHUB_TOKEN`.
3. Run `python scripts/demo_github_org_client.py` to list sample repositories.

## Notes
- The client memoizes organization metadata and repository listings to minimize redundant calls.
- Supply a GitHub token to avoid strict rate limiting during automated tests.
- Use `GithubOrgClient.public_repos(license="apache-2.0")` to filter repositories by license key.
