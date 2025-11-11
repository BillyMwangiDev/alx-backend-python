#!/usr/bin/env python3
# Unit and Integration Tests

This module contains the automated test suites for the `utils` helpers and the
`GithubOrgClient` service. The tests demonstrate best practices around
parameterized test cases, memoization coverage, HTTP call mocking, and
integration testing with static fixtures.

## Structure
- `test_utils.py` exercises the public utilities: `access_nested_map`,
  `get_json`, and `memoize`.
- `test_client.py` validates the `GithubOrgClient` class through both focused
  unit tests and integration tests backed by `fixtures.py`.

## Running the Tests
Activate the project virtual environment, ensure the project root is on the
`PYTHONPATH`, and invoke the suite:

```bash
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
python -m unittest discover -s 0x03-Unittests_and_integration_tests -p "test_*.py"
```

To run with `pytest`:

```bash
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
pytest 0x03-Unittests_and_integration_tests
```

## Notes
- All tests mock external HTTP requests to ensure deterministic behavior.
- Fixtures under `fixtures.py` capture representative API responses and expected
  outputs for integration coverage.

