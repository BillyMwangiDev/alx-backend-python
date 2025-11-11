#!/usr/bin/env python3
"""ADR: Technology stack for the GitHub org client project."""

# 0001 - Choose Python 3.7, requests, pytest, and GitHub Actions

## Status
Accepted

## Context
The project must target Python 3.7 on Ubuntu 18.04, follow pycodestyle 2.5, and integrate with modern tooling for HTTP calls, testing, and CI.

## Decision
- Python 3.7 runtime to match grading environment.
- `requests` for synchronous HTTP interactions.
- `pytest` with `responses` for comprehensive automated tests.
- GitHub Actions to automate linting, testing, and security scans.
- `python-decouple` for environment variable management.

## Consequences
- Simple, synchronous architecture keeps maintenance effort low (KISS).
- Standard tooling ensures contributors ramp quickly and meets ALX guidelines.
- Memoization and dependency injection remain testable and extendable.
