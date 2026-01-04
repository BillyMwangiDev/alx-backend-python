# Code Quality Checks in GitHub Actions

This document explains the code quality checks integrated into the GitHub Actions CI workflow.

## Overview

The CI workflow includes two main code quality checks:

1. **flake8 Linting**: Checks code style and detects errors
2. **Code Coverage**: Measures test coverage and generates reports

## flake8 Linting

### Purpose

flake8 is a Python linting tool that checks code for:
- Style violations (PEP 8)
- Programming errors
- Complexity issues
- Code quality problems

### Configuration

The linting uses the `.flake8` configuration file in the `messaging_app/` directory:

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.venv,venv,build,dist,**/migrations/**
extend-ignore = E203,W503
```

### Workflow Step

The linting step runs **before** tests and will **fail the build** if any errors are detected:

```yaml
- name: Run flake8 linting
  working-directory: ./messaging_app
  run: |
    flake8 . --count --show-source --statistics
  continue-on-error: false
```

### Behavior

- **Fails on errors**: Any linting error will cause the workflow to fail
- **Shows statistics**: Displays count of errors and their locations
- **Shows source**: Displays the problematic code lines
- **Respects .flake8 config**: Uses project-specific configuration

### Running Locally

To run flake8 locally before pushing:

```bash
cd messaging_app
flake8 . --count --show-source --statistics
```

### Common Issues and Fixes

1. **Line too long**: Break long lines or adjust max-line-length
2. **Unused imports**: Remove unused imports
3. **Missing whitespace**: Add proper spacing
4. **Complex functions**: Refactor to reduce complexity

## Code Coverage

### Purpose

Code coverage measures how much of your code is executed by tests. It helps:
- Identify untested code
- Ensure comprehensive testing
- Track testing progress over time

### Configuration

Coverage is configured in `.coveragerc`:

```ini
[run]
source = .
omit =
    */migrations/*
    */venv/*
    */.venv/*
    */__pycache__/*
    */tests/*
    */test_*.py
    manage.py
    */settings.py
    */wsgi.py
    */asgi.py
    */admin.py
    */apps.py
```

### Workflow Step

Coverage is generated during test execution:

```yaml
- name: Run tests with pytest and coverage
  working-directory: ./messaging_app
  run: |
    pytest \
      --cov=. \
      --cov-report=xml:coverage.xml \
      --cov-report=html:htmlcov \
      --cov-report=term \
      -v
```

### Coverage Reports

The workflow generates three types of coverage reports:

1. **XML Report** (`coverage.xml`):
   - Machine-readable format
   - Used by CI/CD tools
   - Uploaded as artifact

2. **HTML Report** (`htmlcov/`):
   - Interactive, visual report
   - Shows line-by-line coverage
   - Uploaded as artifact

3. **Terminal Report**:
   - Displayed in workflow logs
   - Shows summary statistics

### Accessing Coverage Reports

1. **In GitHub Actions**:
   - Go to the workflow run
   - Click on "Artifacts"
   - Download "coverage-reports"
   - Extract and open `htmlcov/index.html` in a browser

2. **Locally**:
   ```bash
   cd messaging_app
   pytest --cov=. --cov-report=html
   open htmlcov/index.html  # macOS
   # or
   start htmlcov/index.html  # Windows
   ```

### Coverage Metrics

The coverage report shows:
- **Total coverage percentage**: Overall code coverage
- **File-by-file coverage**: Coverage per module
- **Line-by-line coverage**: Which lines are covered/uncovered
- **Missing lines**: Specific lines not covered by tests

### Best Practices

1. **Aim for high coverage**: Target 80%+ coverage
2. **Focus on critical paths**: Ensure business logic is well-tested
3. **Don't obsess over 100%**: Some code (like migrations) doesn't need testing
4. **Review uncovered code**: Regularly check what's not covered

### Running Locally

To generate coverage reports locally:

```bash
cd messaging_app
pytest --cov=. --cov-report=html --cov-report=term
```

## Workflow Order

The code quality checks run in this order:

1. **Checkout code**
2. **Set up Python**
3. **Install dependencies**
4. **Run flake8 linting** ⚠️ (Fails build on errors)
5. **Wait for MySQL**
6. **Run migrations**
7. **Run tests with coverage** ✅
8. **Upload artifacts** (test results + coverage reports)

## Failing the Build

The build will fail if:

- **flake8 finds any linting errors**: The workflow stops immediately
- **Tests fail**: Coverage is still generated, but build fails
- **MySQL connection fails**: Database setup issues

## Artifacts

The workflow uploads the following artifacts (retained for 7 days):

1. **test-results**:
   - `test-results.xml` (JUnit format)
   - `test-report.html` (HTML test report)

2. **coverage-reports**:
   - `coverage.xml` (XML coverage data)
   - `htmlcov/` (HTML coverage report directory)

## Integration with Pull Requests

- **Linting errors** block PRs from merging
- **Test failures** block PRs from merging
- **Coverage reports** are available for review
- **Test results** are posted as PR comments

## Customization

### Adjust flake8 Rules

Edit `.flake8`:
```ini
[flake8]
max-line-length = 120  # Increase line length
extend-ignore = E203,W503,E501  # Ignore more rules
```

### Adjust Coverage Thresholds

Add to `.coveragerc`:
```ini
[report]
fail_under = 80  # Fail if coverage < 80%
```

Then update workflow to check:
```yaml
- name: Check coverage threshold
  run: |
    coverage report --fail-under=80
```

### Add More Linters

You can add additional linting tools:

```yaml
- name: Run black check
  run: black --check .

- name: Run isort check
  run: isort --check-only .
```

## Troubleshooting

### flake8 Fails Locally But Passes in CI

- Check that you're using the same `.flake8` config
- Ensure you're running from the correct directory
- Verify flake8 version matches

### Coverage Shows 0%

- Ensure `--cov=.` is included in pytest command
- Check that tests are actually running
- Verify `.coveragerc` is in the correct location

### Coverage Missing Some Files

- Check `.coveragerc` omit patterns
- Ensure files are in the source directory
- Verify file extensions are `.py`

## Next Steps

- Set up coverage badges in README
- Configure coverage thresholds
- Add more linting tools (black, isort, mypy)
- Set up pre-commit hooks for local checks

