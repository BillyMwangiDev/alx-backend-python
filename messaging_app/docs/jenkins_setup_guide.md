# Jenkins CI/CD Setup Guide for Messaging App

This guide walks you through setting up Jenkins in Docker and configuring a CI/CD pipeline for the messaging app.

## Prerequisites

- Docker installed and running
- GitHub account with access to the `alx-backend-python` repository
- Basic knowledge of Jenkins

## Step 1: Install Jenkins in Docker Container

Run the following command to start Jenkins in a Docker container:

```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

**What this command does:**
- `-d`: Runs Jenkins in detached mode (background)
- `--name jenkins`: Names the container "jenkins"
- `-p 8080:8080`: Maps port 8080 (Jenkins web UI)
- `-p 50000:50000`: Maps port 50000 (for Jenkins agents)
- `-v jenkins_home:/var/jenkins_home`: Creates a Docker volume to persist Jenkins data
- `jenkins/jenkins:lts`: Uses the Long-Term Support Jenkins image

**Verify Jenkins is running:**
```bash
docker ps
```

You should see the jenkins container running.

## Step 2: Access Jenkins Dashboard

1. Open your web browser and navigate to: `http://localhost:8080`

2. You'll be prompted to unlock Jenkins. Get the initial admin password:

   **On Windows (PowerShell):**
   ```powershell
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```

   **On Linux/Mac:**
   ```bash
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```

3. Copy the password and paste it into the Jenkins unlock page.

4. Click **"Install suggested plugins"** or select **"Install specific plugins"** if you prefer.

5. Wait for plugins to install (this may take a few minutes).

6. Create an admin user:
   - Username: (choose your username)
   - Password: (choose a strong password)
   - Full name: (your name)
   - Email: (your email)

7. Click **"Save and Finish"** and then **"Start using Jenkins"**.

## Step 3: Install Required Plugins

1. From the Jenkins dashboard, click **"Manage Jenkins"** (left sidebar).

2. Click **"Manage Plugins"**.

3. Go to the **"Available"** tab.

4. Search for and install the following plugins (check the boxes and click **"Install without restart"**):
   - **Git Plugin** (usually pre-installed, but verify)
   - **Pipeline** (usually pre-installed, but verify)
   - **ShiningPanda Plugin** (for Python environment management)
   - **HTML Publisher Plugin** (for test report publishing)
   - **JUnit Plugin** (for test result reporting)

5. Search for and install **Docker Pipeline Plugin** (for Docker build and push operations):
   - Go to **"Available"** tab
   - Search for "Docker Pipeline"
   - Install the plugin

6. After installation, restart Jenkins if prompted:
   ```bash
   docker restart jenkins
   ```

**Important**: For Docker operations, Jenkins needs access to Docker. If running Jenkins in Docker, you need to mount the Docker socket:
```bash
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

**On Windows**, you may need to use Docker Desktop and configure it differently. Consider using a Jenkins agent with Docker installed, or use Docker-in-Docker.

## Step 4: Configure GitHub Credentials

1. From Jenkins dashboard, click **"Manage Jenkins"**.

2. Click **"Manage Credentials"**.

3. Under **"Stores scoped to Jenkins"**, click **"(global)"**.

4. Click **"Add Credentials"** (left sidebar).

5. Configure the credentials:
   - **Kind**: Username with password
   - **Scope**: Global
   - **Username**: Your GitHub username
   - **Password**: Your GitHub Personal Access Token (PAT)
     - To create a PAT: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
     - Required scopes: `repo` (full control of private repositories)
   - **ID**: `github-credentials` (must match the ID in Jenkinsfile)
   - **Description**: "GitHub credentials for alx-backend-python"

6. Click **"OK"** to save.

## Step 5: Configure Docker Hub Credentials

1. From Jenkins dashboard, click **"Manage Jenkins"**.

2. Click **"Manage Credentials"**.

3. Under **"Stores scoped to Jenkins"**, click **"(global)"**.

4. Click **"Add Credentials"** (left sidebar).

5. Configure the credentials:
   - **Kind**: Username with password
   - **Scope**: Global
   - **Username**: Your Docker Hub username
   - **Password**: Your Docker Hub password or access token
   - **ID**: `dockerhub-credentials` (must match the ID in Jenkinsfile)
   - **Description**: "Docker Hub credentials for pushing images"

6. Click **"OK"** to save.

## Step 6: Update Jenkinsfile with Your Docker Hub Username

1. Open `messaging_app/Jenkinsfile` in your editor.

2. Update the `DOCKER_HUB_USERNAME` environment variable (around line 16):
   ```groovy
   DOCKER_HUB_USERNAME = 'your-dockerhub-username'
   ```
   Replace `your-dockerhub-username` with your actual Docker Hub username.

3. Optionally, you can customize the image name:
   ```groovy
   DOCKER_IMAGE_NAME = 'messaging-app'
   ```

4. Commit and push the updated Jenkinsfile to GitHub:
   ```bash
   git add messaging_app/Jenkinsfile
   git commit -m "Update Jenkinsfile with Docker Hub username"
   git push origin main
   ```

## Step 7: Update Jenkinsfile with Your GitHub Repository

1. Open `messaging_app/Jenkinsfile` in your editor.

2. The Jenkinsfile is already configured with your repository URL:
   ```groovy
   url: 'https://github.com/BillyMwangiDev/alx-backend-python.git'
   ```

3. If your repository uses a different branch (not `main`), update the branch name:
   ```groovy
   branches: [[name: '*/main']],  // Change 'main' to your branch name if different
   ```

4. Commit and push the updated Jenkinsfile to GitHub:
   ```bash
   git add messaging_app/Jenkinsfile
   git commit -m "Add Jenkinsfile for CI/CD pipeline"
   git push origin main
   ```

## Step 8: Create a New Pipeline Job

1. From Jenkins dashboard, click **"New Item"**.

2. Enter a name for your job (e.g., `messaging-app-pipeline`).

3. Select **"Pipeline"** as the job type.

4. Click **"OK"**.

5. In the job configuration:
   - **Description**: "CI/CD pipeline for messaging app"
   - **Pipeline Definition**: Select **"Pipeline script from SCM"**
   - **SCM**: Select **"Git"**
   - **Repository URL**: `https://github.com/BillyMwangiDev/alx-backend-python.git`
   - **Credentials**: Select `github-credentials` from the dropdown
   - **Branches to build**: `*/main` (or your branch name)
   - **Script Path**: `messaging_app/Jenkinsfile`

6. Click **"Save"**.

## Step 9: Run the Pipeline Manually

1. From the job page, click **"Build Now"** (left sidebar).

2. You'll see a new build appear in the **"Build History"** section.

3. Click on the build number to view progress.

4. Click **"Console Output"** to see real-time logs.

5. Wait for the pipeline to complete. It will:
   - Checkout code from GitHub
   - Set up Python virtual environment
   - Install dependencies
   - Run pytest tests
   - Generate test reports

## Step 10: View Test Reports and Docker Image

After a successful build:

1. On the build page, you'll see:
   - **Test Result**: Click to see JUnit test results
   - **Pytest Test Report**: Click to see HTML test report

2. Check the console output to verify:
   - Docker image was built successfully
   - Docker image was pushed to Docker Hub
   - Image tags: `your-username/messaging-app:BUILD_NUMBER` and `your-username/messaging-app:latest`

3. Verify on Docker Hub:
   - Go to https://hub.docker.com
   - Navigate to your repository: `your-username/messaging-app`
   - You should see the newly pushed image with the build number tag

4. If tests fail, check the console output for details.

## Troubleshooting

### Jenkins container won't start
- Check if port 8080 is already in use: `netstat -an | findstr 8080` (Windows) or `lsof -i :8080` (Linux/Mac)
- Stop any service using port 8080 or change the port mapping: `-p 8081:8080`

### Cannot connect to GitHub
- Verify your GitHub credentials are correct
- Ensure your Personal Access Token has `repo` scope
- Check if the repository URL is correct in Jenkinsfile

### Python/pytest not found
- Ensure ShiningPanda plugin is installed
- Check that Python is available in the Jenkins container (may need to install Python in the Jenkins image)

### Docker build/push fails
- Ensure Docker is accessible from Jenkins (mount Docker socket or use Docker-in-Docker)
- Verify Docker Hub credentials are correct (ID must be `dockerhub-credentials`)
- Check that Docker Hub username in Jenkinsfile matches your actual username
- Ensure you have permission to push to the Docker Hub repository
- Check Docker Hub rate limits (free tier has limits)

### Tests fail
- Check console output for specific error messages
- Verify `requirements.txt` is up to date
- Ensure database migrations are run if needed (add migration step to Jenkinsfile if required)

### Permission denied errors
- On Linux/Mac, you may need to adjust Docker volume permissions:
  ```bash
  sudo chown -R 1000:1000 /var/lib/docker/volumes/jenkins_home
  ```

## Additional Configuration

### Add Email Notifications (Optional)

1. Install **Email Extension Plugin**
2. Configure SMTP settings in **Manage Jenkins → Configure System**
3. Add post-build action in Jenkinsfile:
   ```groovy
   post {
       failure {
           emailext (
               subject: "Pipeline Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
               body: "Check console output at ${env.BUILD_URL}",
               to: "your-email@example.com"
           )
       }
   }
   ```

### Schedule Automatic Builds

In the job configuration, under **"Build Triggers"**, select:
- **"Poll SCM"**: Check repository periodically (e.g., `H/15 * * * *` for every 15 minutes)
- **"Build periodically"**: Run at specific times (e.g., `0 2 * * *` for daily at 2 AM)

## Next Steps

- Add more stages (linting, security scanning, deployment)
- Configure webhooks for automatic builds on push
- Set up multiple environments (dev, staging, production)
- Add Docker build and push stages

## Useful Commands

```bash
# Stop Jenkins
docker stop jenkins

# Start Jenkins
docker start jenkins

# View Jenkins logs
docker logs jenkins

# Access Jenkins container shell
docker exec -it jenkins bash

# Remove Jenkins container (WARNING: deletes all data)
docker rm -f jenkins
docker volume rm jenkins_home
```

