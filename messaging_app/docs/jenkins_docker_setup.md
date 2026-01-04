# Jenkins Docker Build and Push Setup

This guide explains how to configure Jenkins to build and push Docker images for the messaging app.

## Prerequisites

1. **Docker Hub Account**: Create an account at https://hub.docker.com if you don't have one
2. **Jenkins with Docker Access**: Jenkins container must have access to Docker daemon

## Important: Jenkins Docker Access

For Jenkins to build Docker images, it needs access to the Docker daemon. When running Jenkins in Docker, you have two options:

### Option 1: Mount Docker Socket (Recommended for Development)

Restart Jenkins with Docker socket mounted:

```bash
# Stop existing Jenkins container
docker stop jenkins
docker rm jenkins

# Start Jenkins with Docker socket access
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

**Note for Windows**: Docker Desktop on Windows uses a different socket path. You may need to use Docker Desktop's WSL2 backend or configure it differently.

### Option 2: Install Docker Inside Jenkins Container

If mounting the socket doesn't work, you can install Docker inside the Jenkins container:

```bash
docker exec -it -u root jenkins bash
apt-get update
apt-get install -y docker.io
usermod -aG docker jenkins
exit
docker restart jenkins
```

## Step 1: Add Docker Hub Credentials in Jenkins

1. Go to **Manage Jenkins → Manage Credentials**
2. Click **"(global)"** under "Stores scoped to Jenkins"
3. Click **"Add Credentials"**
4. Configure:
   - **Kind**: Username with password
   - **Scope**: Global
   - **Username**: Your Docker Hub username
   - **Password**: Your Docker Hub password
   - **ID**: `dockerhub-credentials` (must match exactly)
   - **Description**: "Docker Hub credentials"
5. Click **"OK"**

## Step 2: Update Jenkinsfile with Your Docker Hub Username

1. Open `messaging_app/Jenkinsfile`
2. Find the `environment` section (around line 16)
3. Update `DOCKER_HUB_USERNAME`:
   ```groovy
   DOCKER_HUB_USERNAME = 'your-actual-dockerhub-username'
   ```
4. Optionally customize the image name:
   ```groovy
   DOCKER_IMAGE_NAME = 'messaging-app'  // Change if desired
   ```
5. Commit and push:
   ```bash
   git add messaging_app/Jenkinsfile
   git commit -m "Configure Docker Hub username in Jenkinsfile"
   git push origin main
   ```

## Step 3: Verify Docker Access in Jenkins

1. Go to your Jenkins pipeline job
2. Click **"Build Now"**
3. Check the console output for the "Build Docker Image" stage
4. If you see errors like "Cannot connect to the Docker daemon", Jenkins doesn't have Docker access

## Step 4: Run the Pipeline

1. In Jenkins, go to your pipeline job
2. Click **"Build Now"**
3. Monitor the build:
   - **Checkout**: Downloads code from GitHub
   - **Setup Python Environment**: Creates virtual environment
   - **Install Dependencies**: Installs Python packages
   - **Run Tests**: Executes pytest tests
   - **Build Docker Image**: Builds the Docker image with tags
   - **Push Docker Image**: Pushes to Docker Hub

## Step 5: Verify on Docker Hub

1. Go to https://hub.docker.com
2. Log in with your account
3. Navigate to **Repositories**
4. Find your repository: `your-username/messaging-app`
5. You should see:
   - Tag: `latest` (updated with each build)
   - Tag: `BUILD_NUMBER` (e.g., `1`, `2`, `3`)

## Image Tags

The pipeline creates two tags for each build:
- `your-username/messaging-app:BUILD_NUMBER` - Specific build version
- `your-username/messaging-app:latest` - Latest build

Example:
- `billymwangi/messaging-app:1`
- `billymwangi/messaging-app:latest`

## Troubleshooting

### "Cannot connect to the Docker daemon"
- Ensure Docker socket is mounted: `-v /var/run/docker.sock:/var/run/docker.sock`
- On Windows, ensure Docker Desktop is running
- Try Option 2 (install Docker inside container)

### "unauthorized: authentication required"
- Verify Docker Hub credentials ID is `dockerhub-credentials`
- Check username and password are correct
- Ensure you have permission to push to the repository

### "denied: requested access to the resource is denied"
- Verify Docker Hub username in Jenkinsfile matches your account
- Ensure the repository name doesn't conflict with existing repositories
- Check Docker Hub rate limits (free tier: 200 pulls per 6 hours)

### "docker: command not found"
- Install Docker inside Jenkins container (Option 2)
- Or ensure Docker is available in the Jenkins agent's PATH

### Build succeeds but push fails
- Check Docker Hub authentication
- Verify network connectivity
- Check Docker Hub service status

## Testing the Docker Image Locally

After a successful build, you can test the image locally:

```bash
# Pull the image
docker pull your-username/messaging-app:latest

# Run the container
docker run -p 8000:8000 your-username/messaging-app:latest
```

## Next Steps

- Set up automatic builds on git push (webhooks)
- Add deployment stages after successful build
- Configure multi-stage builds for different environments
- Add image scanning for security vulnerabilities

