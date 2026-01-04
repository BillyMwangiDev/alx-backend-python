# Step-by-Step Setup Guide (Follow Along)

This guide will walk you through each step to get all checkers passing.

---

## 🔍 Step 1: Verify Docker Desktop is Running

### Check Docker Status

Open PowerShell or Command Prompt and run:

```powershell
docker ps
```

**Expected Result:**
- If Docker is running: You'll see a table (may be empty if no containers)
- If Docker is NOT running: Error message "Cannot connect to the Docker daemon"

**If Docker is NOT running:**
1. Open Docker Desktop application
2. Wait for it to start (whale icon in system tray should be stable)
3. Run `docker ps` again to verify

---

## 🐳 Step 2: Start Jenkins Container

### Check if Jenkins Already Exists

```powershell
docker ps -a --filter "name=jenkins"
```

**If Jenkins container exists:**
- If status is "Up": Jenkins is already running! Skip to Step 3
- If status is "Exited": Start it with: `docker start jenkins`
- If you want to start fresh: `docker stop jenkins && docker rm jenkins` (then continue below)

### Start Jenkins Container

Run this command:

```powershell
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

**What this does:**
- Downloads Jenkins LTS image (first time only)
- Creates a container named "jenkins"
- Exposes Jenkins on port 8080 (web interface)
- Persists data in a Docker volume

**Wait 30-60 seconds** for Jenkins to start.

### Verify Jenkins is Running

```powershell
docker ps
```

You should see the jenkins container with status "Up".

---

## 🔑 Step 3: Get Jenkins Admin Password

### Get the Password

Run this command:

```powershell
docker logs jenkins 2>&1 | Select-String -Pattern "password" -Context 0,5
```

**Look for a line like:**
```
*************************************************************
*************************************************************
*************************************************************

Your initial admin password is:

a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

This may also be found at: /var/jenkins_home/secrets/initialAdminPassword
*************************************************************
*************************************************************
*************************************************************
```

**COPY THE PASSWORD** - you'll need it in the next step!

**Alternative method:**
```powershell
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 🌐 Step 4: Access Jenkins Web Interface

1. **Open your web browser** (Chrome, Firefox, Edge, etc.)
2. **Go to:** http://localhost:8080
3. **You'll see the "Unlock Jenkins" page**
4. **Paste the password** you copied in Step 3
5. **Click "Continue"**

---

## 📦 Step 5: Install Jenkins Plugins

1. On the "Customize Jenkins" page, click **"Install suggested plugins"**
2. **Wait for installation** (this takes 2-5 minutes)
   - You'll see progress bars for each plugin
   - Don't close the browser!
3. When installation completes, you'll see "Getting Started"
4. Click **"Continue as admin"** (or create a new admin user if you prefer)

---

## 🔌 Step 6: Install Required Plugins

1. On the Jenkins dashboard, click **"Manage Jenkins"** (left sidebar)
2. Click **"Manage Plugins"**
3. Click the **"Available"** tab (at the top)
4. In the search box, search for each plugin and check the box:

   **Plugin 1: Git**
   - Search: `Git`
   - Check the box (it may already be checked)
   
   **Plugin 2: Pipeline**
   - Search: `Pipeline`
   - Check the box (it may already be checked)
   
   **Plugin 3: ShiningPanda**
   - Search: `ShiningPanda`
   - Check the box

5. **Click "Install without restart"** (bottom of page)
6. Wait for installation to complete
7. **Check the checkbox:** "Restart Jenkins when installation is complete and no jobs are running"
8. Wait for Jenkins to restart (you may need to refresh the page)

---

## 🔐 Step 7: Add GitHub Credentials to Jenkins

### Create GitHub Personal Access Token (if you don't have one)

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `Jenkins CI/CD`
4. Select scopes:
   - ✅ **repo** (Full control of private repositories)
   - ✅ **workflow** (Update GitHub Action workflows)
5. Scroll down and click **"Generate token"**
6. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Add Credentials to Jenkins

1. In Jenkins, go to: **Manage Jenkins** → **Manage Credentials**
2. Under "Stores scoped to Jenkins", click **"(global)"**
3. Click **"Add Credentials"** (left sidebar)
4. Fill in the form:
   - **Kind:** Select "Username with password" from dropdown
   - **Scope:** Global (should be selected by default)
   - **Username:** Your GitHub username (e.g., `BillyMwangiDev`)
   - **Password:** Paste the GitHub token you just created
   - **ID:** Type exactly: `github-credentials` (very important!)
   - **Description:** `GitHub credentials for repository access`
5. Click **"Create"**

You should see "github-credentials" in the credentials list.

---

## 🐋 Step 8: Add Docker Hub Credentials to Jenkins

### Create Docker Hub Account (if you don't have one)

1. Go to: https://hub.docker.com/signup
2. Create a free account
3. Note your username

### Add Credentials to Jenkins

1. In Jenkins, go to: **Manage Jenkins** → **Manage Credentials**
2. Click **"(global)"** → **"Add Credentials"**
3. Fill in the form:
   - **Kind:** Username with password
   - **Scope:** Global
   - **Username:** Your Docker Hub username
   - **Password:** Your Docker Hub password
   - **ID:** Type exactly: `dockerhub-credentials` (very important!)
   - **Description:** `Docker Hub credentials for pushing images`
4. Click **"Create"**

You should now see both credentials in the list:
- `github-credentials`
- `dockerhub-credentials`

---

## 🔧 Step 9: Create Jenkins Pipeline Job

1. On the Jenkins dashboard, click **"New Item"** (left sidebar)
2. **Enter an item name:** `messaging-app-pipeline`
3. Select **"Pipeline"** (below the name field)
4. Click **"OK"**

---

## ⚙️ Step 10: Configure Pipeline Job

In the pipeline configuration page:

1. **Scroll down to "Pipeline" section**
2. **Definition:** Select "Pipeline script from SCM" from dropdown
3. **SCM:** Select "Git" from dropdown
4. Fill in the Git configuration:
   - **Repository URL:** `https://github.com/BillyMwangiDev/alx-backend-python.git`
   - **Credentials:** Select `github-credentials` from dropdown
   - **Branches to build:** `*/main` (default should work)
   - **Script Path:** Type `messaging_app/Jenkinsfile`
5. Scroll down and click **"Save"**

You'll be taken to the pipeline job page.

---

## ▶️ Step 11: Trigger Jenkins Pipeline

1. On the pipeline job page, click **"Build Now"** (left sidebar)
2. You'll see a build appear in "Build History" (bottom left)
   - It will be a blue ball (in progress)
3. Click on the build number (e.g., "#1")
4. Click **"Console Output"** to see the build progress
5. **Watch the build:**
   - It will go through stages: Checkout, Setup Python Environment, Install Dependencies, Run Tests, Build Docker Image, Push Docker Image
   - A successful build shows a green checkmark ✓
   - A failed build shows a red X ✗

**First build may take 5-10 minutes** (downloading dependencies, etc.)

---

## 🚀 Step 12: Set Up GitHub Actions Secrets

1. **Open your browser** and go to:
   https://github.com/BillyMwangiDev/alx-backend-python/settings/secrets/actions

2. **Add Secret 1: DOCKER_USERNAME**
   - Click **"New repository secret"**
   - **Name:** Type exactly: `DOCKER_USERNAME` (case-sensitive!)
   - **Value:** Your Docker Hub username
   - Click **"Add secret"**

3. **Add Secret 2: DOCKER_PASSWORD**
   - Click **"New repository secret"** again
   - **Name:** Type exactly: `DOCKER_PASSWORD` (case-sensitive!)
   - **Value:** Your Docker Hub password
   - Click **"Add secret"**

4. **Verify secrets are added:**
   - You should see two secrets listed:
     - `DOCKER_USERNAME` (shows as ••••••••)
     - `DOCKER_PASSWORD` (shows as ••••••••)

---

## 🔄 Step 13: Trigger GitHub Actions Workflows

1. Go to: https://github.com/BillyMwangiDev/alx-backend-python/actions

2. **Trigger CI Workflow:**
   - Click on **"CI - Django Tests"** in the workflow list
   - Click **"Run workflow"** button (right side)
   - Select branch: `main` (or `master` if that's your default)
   - Click **"Run workflow"** (green button)

3. **Trigger Docker Workflow:**
   - Go back to Actions tab
   - Click on **"Build and Push Docker Image"**
   - Click **"Run workflow"**
   - Select branch: `main`
   - Click **"Run workflow"**

4. **Monitor Workflows:**
   - Click on a workflow run to see progress
   - Green checkmark ✓ = success
   - Red X ✗ = failure (click to see error details)

---

## ✅ Step 14: Verify Everything is Working

### Jenkins Verification

- [ ] Jenkins accessible at http://localhost:8080
- [ ] Plugins installed (Git, Pipeline, ShiningPanda)
- [ ] Credentials added (github-credentials, dockerhub-credentials)
- [ ] Pipeline job created (`messaging-app-pipeline`)
- [ ] Pipeline build completed successfully (green checkmark)

### GitHub Actions Verification

- [ ] Secrets added (DOCKER_USERNAME, DOCKER_PASSWORD)
- [ ] Workflows visible in Actions tab
- [ ] CI workflow completed successfully (green checkmark)
- [ ] Docker workflow completed successfully (green checkmark)

---

## 🆘 Troubleshooting

### Jenkins Won't Start

```powershell
# Check logs
docker logs jenkins

# Restart Jenkins
docker restart jenkins

# If port 8080 is in use, use a different port:
docker stop jenkins
docker rm jenkins
docker run -d --name jenkins -p 8081:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
# Then access: http://localhost:8081
```

### Can't Find Credentials in Jenkins

- Make sure credential IDs are EXACTLY: `github-credentials` and `dockerhub-credentials` (case-sensitive, no spaces)
- Credentials should be in "(global)" scope

### Pipeline Build Fails

- Check Console Output for specific errors
- Verify credentials are correct
- Make sure Jenkinsfile is in `messaging_app/Jenkinsfile` in your repository

### GitHub Actions Fails

- Verify secrets are named exactly: `DOCKER_USERNAME` and `DOCKER_PASSWORD` (case-sensitive!)
- Check workflow logs for specific errors
- Verify Docker Hub credentials are correct

---

## 🎯 What's Next?

Once everything is set up:
- Jenkins pipeline runs automatically when you push code (if configured with webhooks)
- GitHub Actions workflows run on every push to main/develop branches
- Checkers should pass once all pipelines complete successfully

**Congratulations! You're all set! 🎉**

