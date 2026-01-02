# Docker Sequential Build Troubleshooting Guide
## دليل استكشاف الأخطاء وإصلاحها لبناء Docker المتسلسل

**Last Updated**: 2026-01-02  
**Applies to**: docker-one-by-one.sh, docker-one-by-one.ps1

---

## 📋 Overview | نظرة عامة

The sequential build scripts (`docker-one-by-one.sh` and `docker-one-by-one.ps1`) build and start Docker containers one at a time to prevent resource conflicts. This is especially useful on:
- M1/M2 Mac machines
- Windows systems with limited resources
- Development environments with memory constraints

النصوص البرمجية للبناء المتسلسل تقوم ببناء وتشغيل حاويات Docker واحدة تلو الأخرى لمنع تعارضات الموارد.

---

## 🚨 Common Issues | المشاكل الشائعة

### 1. Script Not Found or Permission Denied

#### Symptoms
```bash
bash: ./docker-one-by-one.sh: Permission denied
# OR
./docker-one-by-one.sh: No such file or directory
```

#### Solution
```bash
# Make the script executable
chmod +x docker-one-by-one.sh

# Verify permissions
ls -l docker-one-by-one.sh
# Should show: -rwxr-xr-x
```

---

### 2. Docker Compose Not Found

#### Symptoms
```
ERROR: docker compose command not available
Please ensure Docker Desktop is installed and running
```

#### Solution

**For Linux:**
```bash
# Check if Docker is installed
docker --version

# Install Docker Compose plugin
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker compose version
```

**For macOS:**
```bash
# Update Docker Desktop to latest version
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker compose version
```

**For Windows:**
```powershell
# Update Docker Desktop to latest version
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker compose version
```

---

### 3. docker-compose.yml Not Found

#### Symptoms
```
ERROR: docker-compose.yml not found in current directory
```

#### Solution
```bash
# Ensure you're in the project root
cd /path/to/sahool-unified-v15-idp

# Verify docker-compose.yml exists
ls -la docker-compose.yml

# If not found, check for other compose files
ls -la docker-compose*.yml
```

---

### 4. No Services Found

#### Symptoms
```
ERROR: No services found in docker-compose.yml
```

#### Solution
```bash
# Validate docker-compose.yml syntax
docker compose config

# Check for YAML syntax errors
# Common issues:
# - Incorrect indentation
# - Missing colons
# - Invalid service definitions

# If using multiple compose files, specify them
export COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml
./docker-one-by-one.sh
```

---

### 5. Build Failures

#### Symptoms
```
[FAIL] Failed to build: service-name
Build failed with exit code 1
```

#### Solutions

**Check Build Logs:**
```bash
# View detailed build output for specific service
docker compose build service-name --progress=plain

# Check for common issues:
# - Missing dependencies
# - Network errors
# - Dockerfile syntax errors
```

**Clear Build Cache:**
```bash
# Remove all cached layers
docker builder prune -af

# Remove all images and rebuild
docker compose down --rmi all
./docker-one-by-one.sh
```

**Check Dockerfile:**
```bash
# Verify Dockerfile exists for the service
ls -la path/to/service/Dockerfile

# Common Dockerfile issues:
# - Invalid FROM image
# - Copy/ADD paths don't exist
# - RUN commands fail
```

---

### 6. Container Start Failures

#### Symptoms
```
[FAIL] Failed to start: service-name
```

#### Solutions

**Check Container Logs:**
```bash
# View logs for failed service
docker compose logs service-name

# Common issues:
# - Port already in use
# - Missing environment variables
# - Database connection errors
```

**Check Port Conflicts:**
```bash
# Find what's using the port
lsof -i :8080  # Replace 8080 with your port

# Kill the process or change port in docker-compose.yml
```

**Check Environment Variables:**
```bash
# Ensure .env file exists
ls -la .env

# Copy from example if needed
cp .env.example .env

# Edit required variables
nano .env
```

**Check Dependencies:**
```bash
# Ensure dependent services are running
docker compose ps

# Start dependencies first
docker compose up -d postgres redis nats
```

---

### 7. Memory/Resource Issues

#### Symptoms
```
ERROR: Container killed due to OOM (Out of Memory)
# OR
Build takes extremely long time
```

#### Solutions

**Increase Docker Resources:**

**For Docker Desktop (Mac/Windows):**
1. Open Docker Desktop Settings
2. Go to Resources
3. Increase:
   - CPUs: 4+ cores recommended
   - Memory: 8GB+ recommended
   - Swap: 2GB+ recommended
4. Click "Apply & Restart"

**For Linux:**
```bash
# Check available memory
free -h

# Close unnecessary applications
# OR upgrade system memory
```

**Build in Smaller Batches:**
```bash
# Build only infrastructure services first
docker compose build postgres redis nats kong

# Start them
docker compose up -d postgres redis nats kong

# Then build application services
docker compose build field-ops-service billing-core
```

---

### 8. Network Issues During Build

#### Symptoms
```
ERROR: Failed to download package
ERROR: Connection timeout
```

#### Solutions

**Check Internet Connection:**
```bash
# Test connectivity
ping google.com

# Test Docker Hub access
docker pull hello-world
```

**Configure Docker Proxy (if behind corporate firewall):**
```bash
# Create or edit ~/.docker/config.json
mkdir -p ~/.docker
cat > ~/.docker/config.json << EOF
{
  "proxies": {
    "default": {
      "httpProxy": "http://proxy.example.com:8080",
      "httpsProxy": "http://proxy.example.com:8080",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
EOF
```

**Use Docker Buildkit with Cache:**
```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Run script again
./docker-one-by-one.sh
```

---

### 9. PowerShell Execution Policy (Windows)

#### Symptoms
```
docker-one-by-one.ps1 cannot be loaded because running scripts is disabled
```

#### Solution
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy to RemoteSigned (run as Administrator)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# OR run script with bypass
powershell -ExecutionPolicy Bypass -File .\docker-one-by-one.ps1
```

---

### 10. Slow Build Performance on M1/M2 Macs

#### Symptoms
- Builds take 10x longer than expected
- High CPU usage
- Docker Desktop consuming excessive resources

#### Solutions

**Enable Virtualization Framework:**
1. Open Docker Desktop Settings
2. Go to General
3. Enable "Use Virtualization Framework"
4. Enable "VirtioFS" for file sharing
5. Restart Docker Desktop

**Use Rosetta 2 Emulation (for x86_64 images):**
```bash
# Install Rosetta 2 if not already installed
softwareupdate --install-rosetta

# Enable in Docker Desktop Settings > Features
# Check "Use Rosetta for x86_64/amd64 emulation"
```

**Use Native ARM64 Images:**
```dockerfile
# In Dockerfile, prefer ARM64 base images
FROM --platform=linux/arm64 node:18-alpine
# OR
FROM --platform=linux/arm64 python:3.11-slim
```

---

## 🔍 Debugging Tips | نصائح التصحيح

### Enable Verbose Output

**For Bash:**
```bash
# Run with verbose mode
bash -x ./docker-one-by-one.sh
```

**For PowerShell:**
```powershell
# Run with verbose mode
$VerbosePreference = "Continue"
.\docker-one-by-one.ps1
```

### Check Docker Daemon

```bash
# Check Docker status
docker info

# Check Docker daemon logs
# Linux
sudo journalctl -u docker -f

# Mac
tail -f ~/Library/Containers/com.docker.docker/Data/log/vm/dockerd.log

# Windows
Get-EventLog -LogName Application -Source Docker
```

### Validate Individual Services

```bash
# Build single service
docker compose build service-name

# Start single service
docker compose up -d service-name

# Check logs
docker compose logs -f service-name

# Check health
docker compose ps service-name
```

---

## 📊 Performance Optimization | تحسين الأداء

### Use Multi-Stage Builds

```dockerfile
# Example Dockerfile with multi-stage build
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
CMD ["node", "index.js"]
```

### Optimize Layer Caching

```dockerfile
# Bad: Cache invalidated on any file change
COPY . /app
RUN npm install

# Good: Cache invalidated only when dependencies change
COPY package*.json /app/
RUN npm install
COPY . /app
```

### Use .dockerignore

```bash
# Create .dockerignore file
cat > .dockerignore << EOF
node_modules
npm-debug.log
.git
.env
*.md
tests
coverage
.vscode
EOF
```

---

## 🆘 Getting Help | الحصول على المساعدة

### Collect Debug Information

```bash
# Create debug report
cat > debug-report.txt << EOF
Date: $(date)
Docker Version: $(docker --version)
Docker Compose Version: $(docker compose version)
OS: $(uname -a)
Available Memory: $(free -h | grep Mem)
Running Containers: $(docker ps -a)
EOF

# Check system resources
docker system df

# Export logs
docker compose logs > docker-logs.txt
```

### Contact Support

When reporting issues, include:
1. Operating System and version
2. Docker and Docker Compose versions
3. Complete error message
4. Output of `docker compose config`
5. Contents of debug-report.txt

---

## 📚 Additional Resources | موارد إضافية

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [SAHOOL Docker Guide](docs/DOCKER.md)
- [Post-Merge Verification](POST_MERGE_VERIFICATION.md)

---

**Note**: Keep this guide updated as new issues are discovered and resolved.
