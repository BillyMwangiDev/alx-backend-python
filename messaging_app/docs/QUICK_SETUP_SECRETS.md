# Quick Setup: GitHub Secrets for Docker Hub

## The Error

If you see this error in GitHub Actions:
```
Error: Username and password required
```

It means the GitHub secrets for Docker Hub haven't been set up yet.

## Quick Fix (5 minutes)

### Step 1: Get Your Docker Hub Credentials

1. Go to https://hub.docker.com
2. Log in (or create an account if you don't have one)
3. Get your username (it's your Docker Hub username)

### Step 2: Create a Docker Hub Access Token (Recommended)

1. In Docker Hub, go to **Account Settings** → **Security**
2. Click **"New Access Token"**
3. Name it: `GitHub Actions` (or any name you prefer)
4. Set permissions: **Read & Write**
5. Click **Generate**
6. **COPY THE TOKEN** - You won't see it again!

### Step 3: Add Secrets to GitHub

1. Go to your GitHub repository: https://github.com/BillyMwangiDev/alx-backend-python
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **"New repository secret"** button
5. Add **Secret 1**:
   - Name: `DOCKER_USERNAME` (must be exact, case-sensitive)
   - Value: Your Docker Hub username
   - Click **"Add secret"**
6. Click **"New repository secret"** again
7. Add **Secret 2**:
   - Name: `DOCKER_PASSWORD` (must be exact, case-sensitive)
   - Value: The access token you copied in Step 2 (or your Docker Hub password)
   - Click **"Add secret"**

### Step 4: Verify Secrets Are Added

You should see:
- ✅ `DOCKER_USERNAME` (shows as `••••••••`)
- ✅ `DOCKER_PASSWORD` (shows as `••••••••`)

### Step 5: Test the Workflow

1. Go to the **Actions** tab in your repository
2. Find the failed workflow run
3. Click **"Re-run jobs"** → **"Re-run all jobs"**
4. Or push a new commit to trigger the workflow again

## Important Notes

- ⚠️ **Secret names are case-sensitive**: Must be exactly `DOCKER_USERNAME` and `DOCKER_PASSWORD`
- 🔒 **Use Access Tokens**: More secure than passwords, can be revoked
- ✅ **Secrets are encrypted**: They're safe and only visible when used in workflows
- ❌ **Never commit secrets**: Never put credentials in code or commit them to Git

## Troubleshooting

### "Username and password required" still appears

- Verify secret names are exactly: `DOCKER_USERNAME` and `DOCKER_PASSWORD`
- Check that secrets were added (Settings → Secrets and variables → Actions)
- Try re-running the workflow after adding secrets

### "authentication required" error

- Verify your Docker Hub username is correct
- Check that the access token/password is correct
- Ensure the access token has Read & Write permissions
- Try generating a new access token

### "denied: requested access to the resource is denied"

- Check that your Docker Hub account is active
- Verify you have permission to push images
- Check Docker Hub rate limits (free tier has limits)

## Quick Reference

**Repository**: https://github.com/BillyMwangiDev/alx-backend-python  
**Secrets Location**: Settings → Secrets and variables → Actions  
**Required Secrets**: `DOCKER_USERNAME`, `DOCKER_PASSWORD`  
**Docker Hub**: https://hub.docker.com


