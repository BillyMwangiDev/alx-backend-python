# Complete Checker Setup Guide

This guide walks you through setting up Docker Desktop, Jenkins, and GitHub Actions so all checkers can pass.

## Prerequisites

1. **Docker Desktop** installed and running
2. **GitHub account** with access to your repository
3. **Docker Hub account** (free at https://hub.docker.com)

---

## Part 1: Docker Desktop Setup

### Step 1: Install and Start Docker Desktop

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install Docker Desktop
3. Launch Docker Desktop
4. Wait until Docker Desktop shows "Docker Desktop is running" (green indicator)

### Step 2: Verify Docker is Running

Open a terminal/command prompt and run:

```bash
docker --version
docker ps
```

Both commands should work without errors.

---

## Part 2: Jenkins Setup (For Task 0 & 1)

### Step 1: Run Jenkins in Docker Container

Open a terminal/command prompt and run:

```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

**What this does:**
- Pulls the latest Jenkins LTS image
- Creates a container named "jenkins"
- Exposes Jenkins on port 8080 (web UI) and 50000 (agents)
- Persists Jenkins data in a Docker volume

**Wait 30-60 seconds** for Jenkins to start.

### Step 2: Get Jenkins Initial Admin Password

Run this command to get the initial admin password:

```bash
docker logs jenkins 2>&1 | Select-String -Pattern "password" -Context 0,5
```

Or on Linux/Mac:

```bash
docker logs jenkins 2>&1 | grep -A 5 "password"
```

**Copy the password** - you'll need it in the next step.

The password looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

### Step 3: Complete Jenkins Initial Setup

1. Open your web browser
2. Go to: **http://localhost:8080**
3. You'll see the "Unlock Jenkins" page
4. Paste the admin password you copied
5. Click **"Continue"**

### Step 4: Install Recommended Plugins

1. Click **"Install suggested plugins"**
2. Wait for all plugins to install (this takes 2-5 minutes)
3. When complete, click **"Continue as admin"** (or create an admin user)

### Step 5: Install Required Plugins

**IMPORTANT:** Install these specific plugins:

1. Go to: **Manage Jenkins** → **Manage Plugins**
2. Click on **"Available"** tab
3. Search for and install these plugins (check the box, then click "Install without restart"):
   - **Git** (git plugin)
   - **Pipeline**
   - **ShiningPanda** (ShiningPandaPlugin)
4. After installation, click **"Restart Jenkins when installation is complete and no jobs are running"**
5. Wait for Jenkins to restart (refresh the page if needed)

### Step 6: Configure GitHub Credentials

1. Go to: **Manage Jenkins** → **Manage Credentials**
2. Click on **"(global)"** → **"Add Credentials"**
3. Fill in:
   - **Kind:** Username with password
   - **Scope:** Global
   - **Username:** Your GitHub username (e.g., `BillyMwangiDev`)
   - **Password:** Your GitHub Personal Access Token (see below)
   - **ID:** `github-credentials` (exactly this)
   - **Description:** GitHub credentials
4. Click **"Create"**

**How to create a GitHub Personal Access Token:**

1. Go to GitHub.com → Your profile → **Settings**
2. Click **"Developer settings"** (bottom left)
3. Click **"Personal access tokens"** → **"Tokens (classic)"**
4. Click **"Generate new token"** → **"Generate new token (classic)"**
5. Give it a name: `Jenkins CI/CD`
6. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
7. Click **"Generate token"**
8. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)
9. Use this token as the password in Jenkins credentials

### Step 7: Configure Docker Hub Credentials

1. Go to: **Manage Jenkins** → **Manage Credentials**
2. Click on **"(global)"** → **"Add Credentials"**
3. Fill in:
   - **Kind:** Username with password
   - **Scope:** Global
   - **Username:** Your Docker Hub username
   - **Password:** Your Docker Hub password or access token
   - **ID:** `dockerhub-credentials` (exactly this)
   - **Description:** Docker Hub credentials
4. Click **"Create"**

**To get Docker Hub credentials:**

1. Go to https://hub.docker.com
2. Sign up or log in
3. Your username is your Docker Hub username
4. You can use your password, or create an access token:
   - Go to Account Settings → Security
   - Click "New Access Token"
   - Give it a name (e.g., "Jenkins")
   - Copy the token and use it as the password

### Step 8: Create Jenkins Pipeline Job

1. Click **"New Item"** on the Jenkins dashboard
2. Enter item name: `messaging-app-pipeline`
3. Select **"Pipeline"**
4. Click **"OK"**

### Step 9: Configure Pipeline to Use Jenkinsfile

1. In the pipeline configuration page:
   - Scroll to **"Pipeline"** section
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/BillyMwangiDev/alx-backend-python.git`
   - **Credentials:** Select `github-credentials` from dropdown
   - **Branches to build:** `*/main` (or `*/master` if your main branch is master)
   - **Script Path:** `messaging_app/Jenkinsfile`
2. Click **"Save"**

### Step 10: Trigger Pipeline Manually

1. On the pipeline job page, click **"Build Now"**
2. Click on the build number (#1) in the Build History
3. Click **"Console Output"** to see the build progress
4. Wait for the build to complete

**Expected stages:**
- ✅ Checkout
- ✅ Setup Python Environment
- ✅ Install Dependencies
- ✅ Run Tests
- ✅ Build Docker Image
- ✅ Push Docker Image

### Troubleshooting Jenkins

**Jenkins won't start:**
```bash
docker logs jenkins
docker restart jenkins
```

**Port 8080 already in use:**
- Stop the other service using port 8080, or
- Change the port: `-p 8081:8080` (then use http://localhost:8081)

**Can't access Jenkins:**
- Make sure Docker Desktop is running
- Check: `docker ps` (should show jenkins container running)
- Try: `docker restart jenkins`

**Build fails with "git branch" error:**
- Make sure the Jenkinsfile is in `messaging_app/Jenkinsfile`
- Check the Script Path is exactly: `messaging_app/Jenkinsfile`

**Docker commands fail in Jenkins:**
- Jenkins container needs access to Docker
- Run Jenkins with: `docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:lts`
- Or install Docker inside Jenkins container

---

## Part 3: GitHub Actions Setup (For Task 2, 3, 4)

### Step 1: Add Docker Hub Secrets to GitHub

1. Go to your GitHub repository: https://github.com/BillyMwangiDev/alx-backend-python
2. Click **"Settings"** (top menu)
3. In the left sidebar, click **"Secrets and variables"** → **"Actions"**
4. Click **"New repository secret"**

**Add Secret 1: DOCKER_USERNAME**
- **Name:** `DOCKER_USERNAME`
- **Value:** Your Docker Hub username
- Click **"Add secret"**

**Add Secret 2: DOCKER_PASSWORD**
- Click **"New repository secret"** again
- **Name:** `DOCKER_PASSWORD`
- **Value:** Your Docker Hub password or access token
- Click **"Add secret"**

### Step 2: Verify Workflow Files Exist

Make sure these files exist in your repository:

1. `messaging_app/.github/workflows/ci.yml`
2. `messaging_app/.github/workflows/dep.yml`

**To check:**
- Go to your GitHub repository
- Navigate to `messaging_app/.github/workflows/`
- You should see `ci.yml` and `dep.yml`

**If files don't exist:**
- They need to be committed and pushed to GitHub
- Run: `git add messaging_app/.github/workflows/*.yml && git commit -m "Add workflows" && git push`

### Step 3: Trigger GitHub Actions Workflows

**Automatic trigger:**
- Workflows run automatically on push to `main` or `develop` branch
- Make a small change and push, or

**Manual trigger:**
1. Go to your GitHub repository
2. Click **"Actions"** tab
3. Select **"CI - Django Tests"** (for ci.yml)
4. Click **"Run workflow"** → Select branch → Click **"Run workflow"**
5. Repeat for **"Build and Push Docker Image"** (for dep.yml)

### Step 4: Check Workflow Status

1. Go to **"Actions"** tab
2. Click on a workflow run
3. Click on the job (e.g., "test" or "build-and-push")
4. View the logs to see progress

### Troubleshooting GitHub Actions

**Workflow not running:**
- Check that files are in `messaging_app/.github/workflows/` (not just `.github/workflows/`)
- Check the workflow file syntax (YAML formatting)
- Check branch name (should be `main` or `develop`)

**MySQL service error:**
- This is a known issue with MySQL in GitHub Actions
- The workflow uses MySQL 5.7 which should work
- If it still fails, check the workflow logs for specific errors

**Docker login error:**
- Verify secrets are set: `DOCKER_USERNAME` and `DOCKER_PASSWORD`
- Check that secrets are spelled exactly (case-sensitive)
- Verify Docker Hub credentials are correct

**"No files found" warnings:**
- These are warnings, not errors
- They appear when tests don't run (e.g., due to earlier failure)
- Check earlier steps in the workflow for actual errors

---

## Part 4: Quick Checklist

### Jenkins Checklist

- [ ] Docker Desktop is running
- [ ] Jenkins container is running (`docker ps` shows jenkins)
- [ ] Jenkins is accessible at http://localhost:8080
- [ ] Initial setup completed (admin password entered)
- [ ] Required plugins installed: Git, Pipeline, ShiningPanda
- [ ] GitHub credentials added (ID: `github-credentials`)
- [ ] Docker Hub credentials added (ID: `dockerhub-credentials`)
- [ ] Pipeline job created and configured
- [ ] Pipeline triggered manually ("Build Now")
- [ ] Build completed successfully

### GitHub Actions Checklist

- [ ] `DOCKER_USERNAME` secret added to GitHub
- [ ] `DOCKER_PASSWORD` secret added to GitHub
- [ ] `messaging_app/.github/workflows/ci.yml` exists
- [ ] `messaging_app/.github/workflows/dep.yml` exists
- [ ] Workflows triggered (manually or via push)
- [ ] CI workflow completed (tests, flake8, coverage)
- [ ] Deployment workflow completed (Docker build and push)

---

## Part 5: Common Checker Requirements

### Task 0 & 1 (Jenkins) Requirements

✅ Jenkinsfile must be at: `messaging_app/Jenkinsfile`
✅ Jenkinsfile must contain: `sh "git branch"`
✅ Jenkinsfile must contain: `pip3 install -r messaging_app/requirements.txt`
✅ Jenkinsfile must have stages: Checkout, Setup, Install, Test, Build, Push

### Task 2 & 3 (GitHub Actions CI) Requirements

✅ Workflow file must be at: `messaging_app/.github/workflows/ci.yml`
✅ Must run Django tests on push/PR
✅ Must use MySQL service for testing
✅ Must run flake8 linting (fail on errors)
✅ Must generate code coverage reports

### Task 4 (GitHub Actions Docker) Requirements

✅ Workflow file must be at: `messaging_app/.github/workflows/dep.yml`
✅ Must build Docker image
✅ Must push to Docker Hub
✅ Must use GitHub secrets for credentials

---

## Getting Help

If checkers are still failing:

1. **Check the specific error message** - what exactly is the checker looking for?
2. **Verify file locations** - use `git ls-files` to confirm files are tracked
3. **Check file content** - ensure required strings/patterns are present
4. **Check Jenkins/GitHub Actions logs** - actual errors might be in the logs
5. **Verify credentials** - make sure all credentials are set up correctly

---

## Summary

**For Jenkins:**
1. Run Jenkins in Docker
2. Install plugins (Git, Pipeline, ShiningPanda)
3. Add credentials (GitHub and Docker Hub)
4. Create pipeline job
5. Trigger manually

**For GitHub Actions:**
1. Add Docker Hub secrets to GitHub
2. Ensure workflow files are committed
3. Trigger workflows (push or manually)
4. Monitor in Actions tab

All files are already in place - you just need to configure Jenkins and GitHub secrets!

