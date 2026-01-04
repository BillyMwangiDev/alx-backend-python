# Docker Deployment with GitHub Actions

This guide explains how to set up and use the GitHub Actions workflow for building and pushing Docker images to Docker Hub.

## Overview

The `dep.yml` workflow automatically:
- Builds a Docker image for the messaging app
- Tags it with multiple tags (latest, commit SHA, branch name)
- Pushes it to Docker Hub
- Uses GitHub Actions secrets for secure authentication

## Prerequisites

1. **Docker Hub Account**: Create an account at https://hub.docker.com if you don't have one
2. **GitHub Repository**: Your code must be in a GitHub repository
3. **GitHub Actions Enabled**: Actions should be enabled for your repository

## Setting Up GitHub Secrets

GitHub Actions uses secrets to securely store sensitive information like Docker Hub credentials.

### Step 1: Get Your Docker Hub Credentials

1. Go to https://hub.docker.com
2. Log in to your account
3. Note your Docker Hub username
4. If you don't have an access token, create one:
   - Go to Account Settings → Security
   - Click "New Access Token"
   - Give it a name (e.g., "GitHub Actions")
   - Set permissions (Read & Write)
   - Copy the token (you won't see it again!)

### Step 2: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click on **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add the following secrets:

   **Secret 1: DOCKER_USERNAME**
   - Name: `DOCKER_USERNAME`
   - Value: Your Docker Hub username
   - Click **Add secret**

   **Secret 2: DOCKER_PASSWORD**
   - Name: `DOCKER_PASSWORD`
   - Value: Your Docker Hub password or access token
   - Click **Add secret**

### Step 3: Verify Secrets

After adding secrets, you should see:
- ✅ `DOCKER_USERNAME` (visible as `••••••••`)
- ✅ `DOCKER_PASSWORD` (visible as `••••••••`)

**Important**: 
- Secrets are encrypted and only visible when used in workflows
- Never commit secrets to your repository
- Use access tokens instead of passwords for better security

## Workflow Configuration

### Triggers

The workflow runs automatically when:
- Code is pushed to `main` or `develop` branches
- Pull requests are opened/updated targeting `main` or `develop`
- Only when files in `messaging_app/` directory are changed
- Can be manually triggered via "workflow_dispatch"

### Image Tags

The workflow creates three tags for each build:

1. **`latest`**: Always points to the latest build from the default branch
2. **`<commit-sha>`**: Specific commit (e.g., `abc123def456`)
3. **`<branch-name>`**: Branch name (e.g., `main`, `develop`)

Example tags:
- `your-username/messaging-app:latest`
- `your-username/messaging-app:abc123def456`
- `your-username/messaging-app:main`

### Build Process

1. **Checkout code**: Clones the repository
2. **Set up Docker Buildx**: Enables advanced Docker build features
3. **Log in to Docker Hub**: Authenticates using secrets
4. **Extract branch name**: Determines current branch
5. **Build and push**: Builds image and pushes to Docker Hub
6. **Image info**: Displays pushed image tags

## Workflow File Location

**Important**: GitHub Actions workflows must be at the repository root:
- ✅ **Correct**: `.github/workflows/dep.yml` (at repository root)
- ❌ **Won't work**: `messaging_app/.github/workflows/dep.yml`

The workflow file has been created at: `.github/workflows/dep.yml`

## Running the Workflow

### Automatic Execution

The workflow runs automatically when you:
1. Push code to `main` or `develop` branch
2. Create/update a pull request

### Manual Execution

1. Go to your GitHub repository
2. Click on the **Actions** tab
3. Select **"Build and Push Docker Image"** workflow
4. Click **"Run workflow"**
5. Select branch and click **"Run workflow"**

## Viewing Workflow Results

1. Go to your repository on GitHub
2. Click on the **Actions** tab
3. Select a workflow run to see:
   - Build status (✅ success or ❌ failure)
   - Step-by-step logs
   - Pushed image tags
   - Any errors or warnings

## Verifying Docker Image

After a successful build:

1. Go to https://hub.docker.com
2. Log in to your account
3. Navigate to **Repositories**
4. Find your repository: `your-username/messaging-app`
5. You should see:
   - Multiple tags (latest, commit SHA, branch name)
   - Image size and last updated time
   - Pull command

### Pull and Test Locally

```bash
# Pull the latest image
docker pull your-username/messaging-app:latest

# Run the container
docker run -p 8000:8000 your-username/messaging-app:latest
```

## Troubleshooting

### Workflow Fails: "unauthorized: authentication required"

**Problem**: Docker Hub authentication failed

**Solutions**:
- Verify `DOCKER_USERNAME` secret is correct
- Verify `DOCKER_PASSWORD` secret is correct (use access token, not password)
- Check that secrets are named exactly: `DOCKER_USERNAME` and `DOCKER_PASSWORD`
- Ensure Docker Hub account is active

### Workflow Fails: "denied: requested access to the resource is denied"

**Problem**: Permission denied to push to Docker Hub

**Solutions**:
- Verify you have permission to push to the repository
- Check that the repository name matches your Docker Hub username
- Ensure Docker Hub rate limits haven't been exceeded

### Workflow Fails: "Cannot connect to Docker daemon"

**Problem**: Docker Buildx setup issue

**Solutions**:
- This is usually a GitHub Actions infrastructure issue
- Try re-running the workflow
- Check GitHub Actions status page

### Image Not Appearing on Docker Hub

**Problem**: Build succeeded but image not visible

**Solutions**:
- Check workflow logs to confirm push succeeded
- Verify you're looking at the correct Docker Hub account
- Wait a few minutes for Docker Hub to update
- Check that the workflow actually pushed (not just built)

### Build Context Errors

**Problem**: Docker build fails with file not found errors

**Solutions**:
- Verify `Dockerfile` exists in `messaging_app/` directory
- Check that `requirements.txt` exists
- Ensure `entrypoint.sh` exists and is executable
- Review `.dockerignore` to ensure needed files aren't excluded

## Security Best Practices

1. **Use Access Tokens**: Instead of passwords, use Docker Hub access tokens
2. **Rotate Secrets**: Regularly rotate your Docker Hub access tokens
3. **Limit Permissions**: Give tokens only the permissions they need
4. **Review Workflow Logs**: Check logs for any exposed sensitive information
5. **Use Branch Protection**: Protect main branch to prevent unauthorized pushes

## Customization

### Change Image Name

Edit `.github/workflows/dep.yml`:
```yaml
env:
  DOCKER_IMAGE_NAME: your-custom-name
```

### Add More Tags

Edit the `tags` section in the build step:
```yaml
tags: |
  ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE_NAME }}:latest
  ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE_NAME }}:${{ github.sha }}
  ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE_NAME }}:v1.0.0
```

### Build for Multiple Platforms

Edit the `platforms` section:
```yaml
platforms: linux/amd64,linux/arm64
```

### Add Build Arguments

Add build arguments to pass to Dockerfile:
```yaml
build-args: |
  BUILD_VERSION=${{ github.sha }}
  BUILD_DATE=${{ github.event.head_commit.timestamp }}
```

## Workflow File Structure

```
.github/
└── workflows/
    ├── ci.yml          # Testing and code quality
    └── dep.yml         # Docker build and push
```

## Next Steps

- Set up automated deployments after successful builds
- Add image scanning for security vulnerabilities
- Configure multi-stage builds for optimization
- Set up notifications for build failures
- Add deployment to staging/production environments

## Example Workflow Run

A successful workflow run will show:

```
✅ Checkout code
✅ Set up Docker Buildx
✅ Log in to Docker Hub
✅ Extract branch name
✅ Build and push Docker image
✅ Image info
   ✅ Successfully pushed Docker image to Docker Hub:
     📦 your-username/messaging-app:latest
     📦 your-username/messaging-app:abc123def456
     📦 your-username/messaging-app:main
```

## Support

If you encounter issues:
1. Check the workflow logs in GitHub Actions
2. Verify all secrets are set correctly
3. Test Docker build locally: `docker build -t test ./messaging_app`
4. Review Docker Hub account status and limits

