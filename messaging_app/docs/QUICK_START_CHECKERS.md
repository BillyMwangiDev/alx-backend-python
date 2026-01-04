# Quick Start Guide for Checkers

This is a condensed checklist to get all checkers passing quickly.

## ⚡ Quick Steps (15 minutes)

### 1. Docker Desktop (2 minutes)

```bash
# Verify Docker is running
docker --version
docker ps
```

If Docker Desktop is not running, start it now.

---

### 2. Jenkins Setup (10 minutes)

#### Step 1: Start Jenkins
```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

#### Step 2: Get Password
```bash
docker logs jenkins 2>&1 | Select-String -Pattern "password" -Context 0,5
```
**Copy the password!**

#### Step 3: Complete Setup
1. Open: http://localhost:8080
2. Paste password
3. Click "Install suggested plugins"
4. Wait for installation
5. Continue as admin

#### Step 4: Install Required Plugins
1. **Manage Jenkins** → **Manage Plugins** → **Available**
2. Install:
   - ✅ Git
   - ✅ Pipeline
   - ✅ ShiningPanda
3. Restart Jenkins

#### Step 5: Add Credentials

**GitHub Credentials:**
1. **Manage Jenkins** → **Manage Credentials** → **(global)** → **Add Credentials**
2. Kind: Username with password
3. Username: `YourGitHubUsername`
4. Password: `YourGitHubPersonalAccessToken`
5. **ID: `github-credentials`** (exactly this!)
6. Create

**Docker Hub Credentials:**
1. **Add Credentials** again
2. Kind: Username with password
3. Username: `YourDockerHubUsername`
4. Password: `YourDockerHubPassword`
5. **ID: `dockerhub-credentials`** (exactly this!)
6. Create

**How to get GitHub Token:**
- GitHub.com → Settings → Developer settings → Personal access tokens → Generate new token (classic)
- Select: `repo` scope
- Copy token (use as password above)

**How to get Docker Hub credentials:**
- Sign up at https://hub.docker.com
- Use your username and password

#### Step 6: Create Pipeline
1. **New Item** → Name: `messaging-app-pipeline`
2. Type: **Pipeline**
3. **Pipeline** section:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: `https://github.com/BillyMwangiDev/alx-backend-python.git`
   - Credentials: `github-credentials`
   - Branch: `*/main`
   - Script Path: `messaging_app/Jenkinsfile`
4. **Save**
5. Click **"Build Now"**

---

### 3. GitHub Actions Setup (3 minutes)

#### Step 1: Add Secrets
1. Go to: https://github.com/BillyMwangiDev/alx-backend-python/settings/secrets/actions
2. **New repository secret**
   - Name: `DOCKER_USERNAME`
   - Value: Your Docker Hub username
3. **New repository secret**
   - Name: `DOCKER_PASSWORD`
   - Value: Your Docker Hub password

#### Step 2: Trigger Workflows
1. Go to: https://github.com/BillyMwangiDev/alx-backend-python/actions
2. Click **"CI - Django Tests"** → **"Run workflow"**
3. Click **"Build and Push Docker Image"** → **"Run workflow"**

---

## ✅ Verification

### Jenkins Verification
- [ ] Jenkins accessible at http://localhost:8080
- [ ] Plugins installed (Git, Pipeline, ShiningPanda)
- [ ] Credentials created (`github-credentials`, `dockerhub-credentials`)
- [ ] Pipeline job created
- [ ] Build executed successfully (blue/green ball)

### GitHub Actions Verification
- [ ] Secrets added (`DOCKER_USERNAME`, `DOCKER_PASSWORD`)
- [ ] Workflows visible in Actions tab
- [ ] CI workflow passes (green checkmark)
- [ ] Docker workflow passes (green checkmark)

---

## 🔧 Common Issues

**"Jenkins port 8080 in use"**
- Stop other service or use different port: `-p 8081:8080`

**"Cannot connect to Jenkins"**
- Check Docker is running: `docker ps`
- Restart Jenkins: `docker restart jenkins`

**"Credentials not found"**
- Check credential IDs are exactly: `github-credentials` and `dockerhub-credentials`
- Check credentials are in "(global)" scope

**"GitHub Actions: Username and password required"**
- Verify secrets are named exactly: `DOCKER_USERNAME` and `DOCKER_PASSWORD`
- Check secrets are in the correct repository

**"Workflow not running"**
- Check files exist: `messaging_app/.github/workflows/ci.yml` and `dep.yml`
- Push a commit to trigger workflows

---

## 📝 File Locations (Already Done ✅)

These files should already be in your repository:

- ✅ `messaging_app/Jenkinsfile`
- ✅ `messaging_app/.github/workflows/ci.yml`
- ✅ `messaging_app/.github/workflows/dep.yml`

If they're missing, check the main setup guide for how to add them.

---

## 🎯 Next Steps

After setup:
1. Jenkins pipeline should run automatically when you push code
2. GitHub Actions workflows run on push to main/develop
3. Checkers should pass once pipelines complete successfully

For detailed instructions, see: `CHECKER_SETUP_GUIDE.md`

