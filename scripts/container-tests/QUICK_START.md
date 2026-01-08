# Quick Start Guide - Container Tests

## 🚀 Quick Commands

### Test Everything
```bash
cd /home/user/sahool-unified-v15-idp/scripts/container-tests

# Complete test workflow
./lint-dockerfiles.sh && \
./build-all.sh && \
./security-scan.sh && \
./smoke-test.sh
```

### Individual Tests

```bash
# 1. Lint all Dockerfiles
./lint-dockerfiles.sh

# 2. Build all images
./build-all.sh

# 3. Security scan
./security-scan.sh

# 4. Smoke test
./smoke-test.sh

# 5. Cleanup
./cleanup.sh
```

## 📋 Common Workflows

### Development Testing
```bash
# Quick validation
./lint-dockerfiles.sh --strict
./build-all.sh -t dev
./smoke-test.sh -s api,web -n  # Keep running for debugging
```

### CI/CD Pipeline
```bash
# Full automated test
./lint-dockerfiles.sh --strict && \
./build-all.sh -t $VERSION && \
./security-scan.sh --fail-on CRITICAL && \
./smoke-test.sh -t 300 && \
./cleanup.sh -a -f
```

### Production Release
```bash
# Build, scan, test, and push
./lint-dockerfiles.sh --strict
./build-all.sh -t v1.0.0 -r ghcr.io/sahool
./security-scan.sh --severity CRITICAL,HIGH
./smoke-test.sh
./build-all.sh -t v1.0.0 -r ghcr.io/sahool --push
./cleanup.sh -f
```

### Parallel Build (Faster)
```bash
# Build all images in parallel
./build-all.sh -t latest --parallel --max-jobs 8
```

## 🔍 Troubleshooting

### Script not executable?
```bash
chmod +x *.sh
```

### Docker not running?
```bash
# Linux
sudo systemctl start docker

# Check status
docker info
```

### Out of disk space?
```bash
# Check usage
./cleanup.sh --show-usage

# Full cleanup
./cleanup.sh -a -f
```

### Want to see what will happen?
```bash
# Dry run
./cleanup.sh --dry-run -a
```

## 📊 Quick Reference

| Script | Purpose | Key Options |
|--------|---------|-------------|
| `lint-dockerfiles.sh` | Lint Dockerfiles | `--strict`, `--generate` |
| `build-all.sh` | Build images | `-t TAG`, `--parallel`, `--push` |
| `security-scan.sh` | Security scan | `--severity LEVELS`, `--format json` |
| `smoke-test.sh` | Health checks | `-s SERVICES`, `-t TIMEOUT` |
| `cleanup.sh` | Cleanup | `-a`, `-f`, `--dry-run` |

## 🎯 First Time Setup

```bash
# Navigate to container tests
cd /home/user/sahool-unified-v15-idp/scripts/container-tests

# Make all scripts executable (if needed)
chmod +x *.sh

# Run your first test
./lint-dockerfiles.sh
```

## 💡 Tips

- All scripts have `--help` flag for detailed usage
- Use `--dry-run` with cleanup to see what would be removed
- Check `security-reports/` directory after security scans
- Use `--no-cleanup` with smoke tests to debug failing containers
- Enable `--parallel` for faster builds on multi-core systems
- Scripts auto-install hadolint and trivy if missing

## 📝 Get Help

```bash
# Show help for any script
./lint-dockerfiles.sh --help
./build-all.sh --help
./security-scan.sh --help
./smoke-test.sh --help
./cleanup.sh --help
```

---

**For detailed documentation, see [README.md](README.md)**
