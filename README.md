#!/usr/bin/env python3
# GitHub Org Client

## Description
This project provides a typed, well-documented client for querying GitHub organizations while satisfying ALX backend requirements.

## Setup
1. `py -3.7 -m venv venv`
2. `venv\Scripts\activate`
3. `python -m pip install --upgrade pip`
4. `python -m pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure secrets.

## Usage
- `python scripts/demo_github_org_client.py`
- `python manage.py lint`
- `python manage.py test`
- `python manage.py audit`

## Implementation
- Utilities expose `access_nested_map`, `get_json`, and `memoize`.
- `GithubOrgClient` memoizes organization metadata and repository listings.
- All public functions and classes include type hints and documentation.

## Deployment
- Dockerfile and docker-compose (to be added) enable reproducible environments.
- GitHub Actions workflow runs lint, tests, and security audit.
- Follow security best practices: HTTPS, least privilege tokens, daily backups.
