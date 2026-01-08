# Container Test Scripts

This directory contains comprehensive scripts for testing, building, and securing Docker containers in the SAHOOL project.

## Scripts Overview

### 1. lint-dockerfiles.sh
Lints all Dockerfiles using [hadolint](https://github.com/hadolint/hadolint).

**Features:**
- Auto-installs hadolint if not present
- Scans all Dockerfiles in the project
- Provides detailed linting reports
- Supports strict mode for CI/CD
- Can generate hadolint configuration

**Usage:**
```bash
# Lint all Dockerfiles
./lint-dockerfiles.sh

# Strict mode (fail on warnings)
./lint-dockerfiles.sh --strict

# Generate hadolint config
./lint-dockerfiles.sh --generate

# Show hadolint version
./lint-dockerfiles.sh --version
```

**Options:**
- `-h, --help` - Show help message
- `-s, --strict` - Enable strict mode (fail on warnings)
- `-g, --generate` - Generate hadolint configuration file
- `-v, --version` - Show hadolint version

---

### 2. build-all.sh
Builds all Docker images with proper tagging and optional registry push.

**Features:**
- Discovers all Dockerfiles automatically
- Supports custom tagging
- Registry prefix support
- Parallel builds option
- Build argument passing
- Image labeling with metadata
- Push to registry capability

**Usage:**
```bash
# Build all images with 'latest' tag
./build-all.sh

# Build with specific tag
./build-all.sh -t v1.0.0

# Build and push to registry
./build-all.sh -t v1.0.0 -r ghcr.io/myorg --push

# Parallel build (faster)
./build-all.sh --parallel --max-jobs 8

# Build without cache
./build-all.sh --no-cache

# Pass build arguments
./build-all.sh --build-arg NODE_ENV=production --build-arg VERSION=1.0.0
```

**Options:**
- `-h, --help` - Show help message
- `-t, --tag TAG` - Tag for images (default: latest)
- `-r, --registry REG` - Registry prefix (e.g., ghcr.io/org)
- `-p, --push` - Push images to registry after building
- `-j, --parallel` - Build images in parallel
- `-n, --no-cache` - Build without using cache
- `-b, --build-arg ARG` - Pass build argument (repeatable)
- `--max-jobs N` - Maximum parallel jobs (default: 4)

---

### 3. security-scan.sh
Performs security scanning on Docker images using [Trivy](https://github.com/aquasecurity/trivy).

**Features:**
- Auto-installs Trivy if not present
- Scans all Docker images for vulnerabilities
- Configurable severity levels
- Multiple output formats (table, json, sarif)
- Generates detailed security reports
- Can scan filesystem/repository
- Database auto-update
- Old report cleanup

**Usage:**
```bash
# Scan all images
./security-scan.sh

# Scan with specific severity levels
./security-scan.sh --severity CRITICAL,HIGH

# Generate JSON reports
./security-scan.sh --format json

# Ignore unfixed vulnerabilities
./security-scan.sh --ignore-unfixed

# Update Trivy database first
./security-scan.sh --update-db

# Scan filesystem/repository
./security-scan.sh --filesystem /path/to/project

# Clean old reports
./security-scan.sh --clean-reports 7
```

**Options:**
- `-h, --help` - Show help message
- `-s, --severity LEVELS` - Severity levels (default: CRITICAL,HIGH,MEDIUM)
- `-f, --format FORMAT` - Output format: table, json, sarif (default: table)
- `-t, --type TYPE` - Scan type: image, fs (default: image)
- `--fail-on LEVELS` - Fail on severity levels (default: CRITICAL,HIGH)
- `--ignore-unfixed` - Ignore unfixed vulnerabilities
- `--update-db` - Update Trivy database before scanning
- `--filesystem PATH` - Scan filesystem/repository
- `--clean-reports DAYS` - Clean reports older than N days

**Reports Location:**
Security reports are saved to: `${PROJECT_ROOT}/security-reports/`

---

### 4. smoke-test.sh
Starts containers and performs health checks to ensure they're working correctly.

**Features:**
- Uses docker-compose to manage services
- Waits for containers to be healthy
- Checks health endpoints
- Monitors container logs for errors
- Selective service testing
- Configurable timeout
- Quick health check mode
- Optional cleanup

**Usage:**
```bash
# Test all services
./smoke-test.sh

# Test specific services
./smoke-test.sh -s api,web,database

# Extended timeout (5 minutes)
./smoke-test.sh -t 300

# Keep containers running after test
./smoke-test.sh --no-cleanup

# Quick health check only
./smoke-test.sh --quick

# Use custom compose file
./smoke-test.sh -f docker-compose.test.yml
```

**Options:**
- `-h, --help` - Show help message
- `-f, --file FILE` - Docker Compose file (default: docker-compose.yml)
- `-s, --services SERVICES` - Comma-separated list of services to test
- `-t, --timeout SECONDS` - Health check timeout (default: 120)
- `-n, --no-cleanup` - Don't cleanup containers on exit
- `-q, --quick` - Quick health check only

---

### 5. cleanup.sh
Comprehensive Docker cleanup tool for containers, images, volumes, and networks.

**Features:**
- Interactive or forced cleanup
- Docker Compose service cleanup
- Container removal (running and exited)
- Image removal (including dangling)
- Volume cleanup
- Network pruning
- Build cache clearing
- Security report cleanup
- Dry-run mode
- Disk usage reporting

**Usage:**
```bash
# Interactive cleanup
./cleanup.sh

# Force cleanup without prompts
./cleanup.sh -f

# Full cleanup (everything)
./cleanup.sh -a -f

# Remove images only
./cleanup.sh -i

# Remove volumes only
./cleanup.sh -v

# System prune
./cleanup.sh -p

# Dry run (see what would happen)
./cleanup.sh --dry-run -a

# Show disk usage only
./cleanup.sh --show-usage

# Clean security reports
./cleanup.sh -r
```

**Options:**
- `-h, --help` - Show help message
- `-a, --all` - Clean up everything
- `-f, --force` - Force cleanup without confirmation
- `-p, --prune` - Run Docker system prune
- `-i, --images` - Remove images
- `-v, --volumes` - Remove volumes
- `-n, --networks` - Remove networks
- `-r, --reports` - Clean security reports
- `--dry-run` - Show what would be done without doing it
- `--show-usage` - Show disk usage only

---

## Complete Workflow

Here's a typical workflow using all scripts:

```bash
# 1. Lint all Dockerfiles
./lint-dockerfiles.sh

# 2. Build all images
./build-all.sh -t v1.0.0

# 3. Run security scan
./security-scan.sh

# 4. Run smoke tests
./smoke-test.sh

# 5. If tests pass, tag and push
./build-all.sh -t v1.0.0 -r ghcr.io/sahool --push

# 6. Cleanup
./cleanup.sh -f
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Container Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Lint Dockerfiles
        run: ./scripts/container-tests/lint-dockerfiles.sh --strict

      - name: Build Images
        run: ./scripts/container-tests/build-all.sh -t ${{ github.sha }}

      - name: Security Scan
        run: ./scripts/container-tests/security-scan.sh --format sarif

      - name: Smoke Tests
        run: ./scripts/container-tests/smoke-test.sh -t 300

      - name: Cleanup
        if: always()
        run: ./scripts/container-tests/cleanup.sh -a -f
```

### GitLab CI Example

```yaml
container-tests:
  image: docker:latest
  services:
    - docker:dind
  script:
    - ./scripts/container-tests/lint-dockerfiles.sh --strict
    - ./scripts/container-tests/build-all.sh -t $CI_COMMIT_SHA
    - ./scripts/container-tests/security-scan.sh
    - ./scripts/container-tests/smoke-test.sh
  after_script:
    - ./scripts/container-tests/cleanup.sh -a -f
```

---

## Prerequisites

### Required
- Docker (20.10+)
- Docker Compose (2.0+) or docker compose plugin
- Bash (4.0+)
- curl or wget (for tool installation)

### Optional
- jq (for better JSON formatting)
- hadolint (auto-installed by lint script)
- trivy (auto-installed by security-scan script)

### Installing Prerequisites

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose jq
```

**macOS:**
```bash
brew install docker docker-compose jq
```

**Arch Linux:**
```bash
sudo pacman -S docker docker-compose jq
```

---

## Configuration

### Environment Variables

All scripts support these environment variables:

```bash
# Docker registry (default: none)
export REGISTRY="ghcr.io/myorg"

# Image tag (default: latest)
export TAG="v1.0.0"

# Hadolint version (default: 2.12.0)
export HADOLINT_VERSION="2.12.0"

# Trivy version (default: 0.48.0)
export TRIVY_VERSION="0.48.0"
```

### Hadolint Configuration

Generate a `.hadolint.yaml` configuration file:

```bash
./lint-dockerfiles.sh --generate
```

This creates a configuration file at the project root with sensible defaults.

### Trivy Configuration

Trivy uses its default configuration but can be customized via `.trivyignore` file:

```bash
# Create .trivyignore in project root
cat > .trivyignore << 'EOF'
# Ignore specific CVEs
CVE-2021-1234

# Ignore by package
golang.org/x/text
EOF
```

---

## Troubleshooting

### Permission Denied

If you get "Permission denied" errors:

```bash
# Make scripts executable
chmod +x scripts/container-tests/*.sh

# Or run with bash
bash scripts/container-tests/lint-dockerfiles.sh
```

### Docker Daemon Not Running

```bash
# Linux
sudo systemctl start docker

# macOS
open -a Docker
```

### Tool Installation Fails

If auto-installation fails, install tools manually:

```bash
# Hadolint
wget https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64
chmod +x hadolint-Linux-x86_64
sudo mv hadolint-Linux-x86_64 /usr/local/bin/hadolint

# Trivy
wget https://github.com/aquasecurity/trivy/releases/download/v0.48.0/trivy_0.48.0_Linux-64bit.tar.gz
tar -xzf trivy_0.48.0_Linux-64bit.tar.gz
sudo mv trivy /usr/local/bin/
```

### Out of Disk Space

Clean up Docker resources:

```bash
# See disk usage
./cleanup.sh --show-usage

# Full cleanup
./cleanup.sh -a -f

# Or use Docker commands directly
docker system prune -af --volumes
```

---

## Best Practices

1. **Regular Linting**: Run `lint-dockerfiles.sh` before committing changes
2. **Security First**: Always run `security-scan.sh` before deploying
3. **Smoke Tests**: Run `smoke-test.sh` after building to catch runtime issues
4. **Tag Properly**: Use semantic versioning for tags (e.g., v1.0.0)
5. **Clean Regularly**: Run `cleanup.sh` to free disk space
6. **Parallel Builds**: Use `--parallel` for faster builds in CI/CD
7. **Report Review**: Check security reports in `security-reports/` directory
8. **Version Control**: Don't commit security reports (add to .gitignore)

---

## Contributing

When adding new scripts:

1. Follow the existing script structure
2. Include comprehensive error handling
3. Add colored output for better UX
4. Support `--help` flag
5. Include dry-run mode where applicable
6. Update this README

---

## License

Part of the SAHOOL Unified Platform project.

---

## Support

For issues or questions:
- Create an issue in the project repository
- Contact the DevOps team
- Check the main project documentation

---

## Script Dependencies

```
lint-dockerfiles.sh
  └─ hadolint (auto-installed)

build-all.sh
  ├─ docker
  └─ docker-compose

security-scan.sh
  ├─ trivy (auto-installed)
  └─ jq (optional, for JSON parsing)

smoke-test.sh
  ├─ docker
  ├─ docker-compose
  └─ curl (for HTTP endpoint checks)

cleanup.sh
  ├─ docker
  └─ docker-compose
```

---

## Version History

- **v1.0.0** (2026-01-06)
  - Initial release
  - All five core scripts implemented
  - Full error handling and colored output
  - Auto-installation of tools
  - Comprehensive documentation

---

**Happy Container Testing! 🐳**
