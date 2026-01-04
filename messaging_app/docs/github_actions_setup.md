# GitHub Actions CI/CD Setup Guide

This guide explains the GitHub Actions workflow configuration for automated testing of the messaging app.

## Workflow Location

**Important**: GitHub Actions workflows must be located at the repository root in `.github/workflows/`, not in subdirectories.

- ✅ **Correct location**: `.github/workflows/ci.yml` (at repository root)
- ❌ **Won't work**: `messaging_app/.github/workflows/ci.yml` (GitHub won't recognize it)

The workflow file has been created at the repository root: `.github/workflows/ci.yml`

## Workflow Overview

The CI workflow (`ci.yml`) performs the following:

1. **Triggers**: Runs on push and pull requests to `main` and `develop` branches
2. **Environment**: Sets up Python 3.10 and MySQL 8.0 service
3. **Dependencies**: Installs system and Python dependencies
4. **Database**: Configures and waits for MySQL to be ready
5. **Migrations**: Runs Django database migrations
6. **Tests**: Executes pytest tests
7. **Reports**: Uploads test results as artifacts and publishes them

## Workflow Configuration

### Triggers

The workflow runs when:
- Code is pushed to `main` or `develop` branches
- Pull requests are opened/updated targeting `main` or `develop`
- Only when files in `messaging_app/` directory are changed

### Services

**MySQL 8.0**:
- Database: `messaging_test`
- User: `messaging_test`
- Password: `messaging_test`
- Port: `3306`
- Character set: `utf8mb4`

### Environment Variables

The workflow sets the following environment variables:
- `DJANGO_SECRET_KEY`: Test secret key
- `DJANGO_DEBUG`: False
- `DB_ENGINE`: `django.db.backends.mysql`
- `DB_NAME`: `messaging_test`
- `DB_USER`: `messaging_test`
- `DB_PASSWORD`: `messaging_test`
- `DB_HOST`: `127.0.0.1`
- `DB_PORT`: `3306`

## Workflow Steps

1. **Checkout code**: Clones the repository
2. **Set up Python**: Installs Python 3.10 with pip caching
3. **Install system dependencies**: Installs MySQL client libraries
4. **Install Python dependencies**: Installs packages from `requirements.txt`
5. **Wait for MySQL**: Ensures MySQL service is ready
6. **Run migrations**: Creates and applies database migrations
7. **Run tests**: Executes pytest with JUnit XML and HTML reports
8. **Upload test results**: Saves test artifacts for 7 days
9. **Publish test results**: Adds test results to PR comments

## Viewing Workflow Results

### In GitHub

1. Go to your repository on GitHub
2. Click on the **"Actions"** tab
3. Select a workflow run to see details
4. Click on a job to see step-by-step logs

### Test Results

- **Artifacts**: Download test results from the workflow run page
- **PR Comments**: Test results are automatically posted as comments on pull requests
- **Checks**: See test status in the "Checks" section of pull requests

## Customization

### Change Python Version

Edit `.github/workflows/ci.yml`:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Change version here
```

### Change MySQL Version

Edit the `services` section:
```yaml
services:
  mysql:
    image: mysql:8.0  # Change version here
```

### Add More Test Steps

Add additional steps before or after the test step:
```yaml
- name: Run linting
  working-directory: ./messaging_app
  run: |
    flake8 .
    black --check .
```

### Run Tests on Multiple Python Versions

Use a matrix strategy:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

## Troubleshooting

### Workflow Not Running

- Ensure the workflow file is at `.github/workflows/ci.yml` (repository root)
- Check that you're pushing to `main` or `develop` branch
- Verify that files in `messaging_app/` were changed

### MySQL Connection Errors

- The workflow waits for MySQL to be ready automatically
- If issues persist, check the MySQL service health in logs
- Verify environment variables are set correctly

### Test Failures

- Check the workflow logs for specific error messages
- Ensure all dependencies are in `requirements.txt`
- Verify database migrations run successfully
- Check that test files are in the correct location

### Import Errors

- Ensure `DJANGO_SETTINGS_MODULE` is set to `messaging_app.settings`
- Verify the working directory is set to `./messaging_app`
- Check that all Python packages are installed

## Best Practices

1. **Keep workflows fast**: Only run necessary tests
2. **Use caching**: Pip cache is enabled for faster builds
3. **Fail fast**: Stop on first error to save time
4. **Clean artifacts**: Test results are kept for 7 days
5. **Path filters**: Only run when relevant files change

## Next Steps

- Add code coverage reporting
- Set up deployment workflows
- Add security scanning
- Configure branch protection rules
- Add status badges to README

## Example Status Badge

Add this to your README.md to show CI status:

```markdown
![CI](https://github.com/BillyMwangiDev/alx-backend-python/workflows/CI%20-%20Django%20Tests/badge.svg)
```


