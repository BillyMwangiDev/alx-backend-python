# Jenkins Quick Start Guide

## Quick Setup Checklist

### 1. Start Jenkins Container
```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

### 2. Get Initial Admin Password
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 3. Access Jenkins
- Open browser: `http://localhost:8080`
- Paste the admin password
- Install suggested plugins
- Create admin user

### 4. Install Required Plugins
Go to: **Manage Jenkins → Manage Plugins → Available**
- ✅ Git Plugin
- ✅ Pipeline
- ✅ ShiningPanda Plugin
- ✅ HTML Publisher Plugin
- ✅ JUnit Plugin

### 5. Add GitHub Credentials
Go to: **Manage Jenkins → Manage Credentials → (global) → Add Credentials**
- Kind: Username with password
- Username: Your GitHub username
- Password: GitHub Personal Access Token (with `repo` scope)
- ID: `github-credentials`
- Save

### 5b. Add Docker Hub Credentials
Go to: **Manage Jenkins → Manage Credentials → (global) → Add Credentials**
- Kind: Username with password
- Username: Your Docker Hub username
- Password: Your Docker Hub password
- ID: `dockerhub-credentials`
- Save

### 6. Update Jenkinsfile
Edit `messaging_app/Jenkinsfile`:
- Update `DOCKER_HUB_USERNAME` with your Docker Hub username (line ~16)
- Repository URL is already configured
- Update branch name if not `main`

### 7. Create Pipeline Job
- **New Item** → Name: `messaging-app-pipeline` → **Pipeline**
- **Pipeline script from SCM**
- **Git** → Repository URL: `https://github.com/BillyMwangiDev/alx-backend-python.git`
- **Credentials**: `github-credentials`
- **Script Path**: `messaging_app/Jenkinsfile`
- **Save**

### 8. Run Pipeline
- Click **Build Now**
- View progress in **Console Output**
- Check **Test Result** and **Pytest Test Report** after completion

## Common Issues

**Port 8080 in use?**
```bash
# Use different port
docker run -d --name jenkins -p 8081:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
# Then access: http://localhost:8081
```

**Can't connect to GitHub?**
- Verify PAT has `repo` scope
- Check credentials ID matches Jenkinsfile (`github-credentials`)

**Tests fail?**
- Check console output for errors
- Verify `requirements.txt` is up to date
- Ensure database is set up if needed

**Docker build/push fails?**
- Ensure Docker socket is mounted: `-v /var/run/docker.sock:/var/run/docker.sock`
- Verify Docker Hub credentials ID is `dockerhub-credentials`
- Check Docker Hub username in Jenkinsfile matches your account
- Verify Docker Hub rate limits (free tier has limits)

## Useful Commands

```bash
# View logs
docker logs jenkins

# Restart Jenkins
docker restart jenkins

# Stop Jenkins
docker stop jenkins

# Start Jenkins
docker start jenkins
```

