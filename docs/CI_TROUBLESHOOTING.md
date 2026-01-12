# CI Troubleshooting Guide - دليل استكشاف أخطاء CI

This document captures common CI failures and their solutions to prevent recurring issues.

---

## Table of Contents

1. [Disk Space Issues](#1-disk-space-issues)
2. [Flutter Code Generation (Drift/Freezed)](#2-flutter-code-generation-driftfreezed)
3. [Flutter Provider Exports](#3-flutter-provider-exports)
4. [Python Module Import Errors](#4-python-module-import-errors)
5. [TypeScript Path Mappings](#5-typescript-path-mappings)
6. [FastAPI Complex Query Parameters](#6-fastapi-complex-query-parameters)
7. [GitHub Actions Workflow Issues](#7-github-actions-workflow-issues)

---

## 1. Disk Space Issues

### Symptom
```
ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device
```

### Cause
GitHub Actions runners have limited disk space (~14GB). Large builds (Flutter, Docker) can exhaust this.

### Solution
Add a disk cleanup step at the beginning of jobs that need significant disk space:

```yaml
- name: Free disk space
  run: |
    echo "Freeing disk space..."
    sudo rm -rf /usr/share/dotnet          # ~2-3 GB
    sudo rm -rf /usr/local/lib/android     # ~10 GB
    sudo rm -rf /opt/ghc                   # ~2 GB
    sudo rm -rf /opt/hostedtoolcache/CodeQL # ~5 GB
    df -h
```

### Affected Workflows
- `frontend-tests.yml` (Flutter builds)
- `container-tests.yml` (Docker builds)

---

## 2. Flutter Code Generation (Drift/Freezed)

### Symptom
```
Error: Method not found: 'TasksCompanion'.
Error: 'Task' isn't a type.
```

### Cause
Drift and Freezed require code generation via `build_runner`. The generated `.g.dart` files are not committed to the repository.

### Solution

1. **Always run code generation before build:**
```yaml
- name: Generate code (Drift, Freezed, etc.)
  run: |
    dart run build_runner clean || true
    dart run build_runner build --delete-conflicting-outputs
```

2. **Verify generated files exist:**
```yaml
- name: Verify generated code exists
  run: |
    if [ ! -f "lib/core/storage/database.g.dart" ]; then
      echo "ERROR: database.g.dart was not generated!"
      dart run build_runner build --delete-conflicting-outputs
      if [ ! -f "lib/core/storage/database.g.dart" ]; then
        exit 1
      fi
    fi
```

### Key Files
- `apps/mobile/sahool_field_app/lib/core/storage/database.dart` → generates `database.g.dart`
- `apps/mobile/sahool_field_app/build.yaml` - build_runner configuration

### Prevention
- Run `dart run build_runner build` locally before committing database schema changes
- Check that `pubspec.yaml` has matching versions of `drift` and `drift_dev`

---

## 3. Flutter Provider Exports

### Symptom
```
Error: The getter 'securityConfigProvider' isn't defined for the class 'WalletScreen'.
```

### Cause
Riverpod providers defined in one file are not automatically available when importing another file from the same package.

### Solution
Re-export providers from the main service file:

```dart
// In screen_security_service.dart
import 'security_config.dart';

// Re-export for screens that use SecureScreen
export 'security_config.dart' show securityConfigProvider, SecurityConfig;
```

### Prevention
- When creating a service with providers, export related providers from the main file
- Document which providers are exported in file comments

---

## 4. Python Module Import Errors

### Symptom
```
ModuleNotFoundError: No module named 'crops'
```

### Cause
Python services have two shared directories:
- `/shared/` - Root shared modules (auth, middleware, errors_py)
- `/apps/services/shared/` - Service-specific modules (crops.py, yemen_varieties.py)

### Solution

1. **Update Dockerfile to copy both directories:**
```dockerfile
# Copy root shared libraries
COPY shared/ ./shared/

# Copy services-shared modules (crops.py, yemen_varieties.py, etc.)
COPY apps/services/shared/ ./services_shared/
```

2. **Update Python path in main.py:**
```python
# Add services_shared modules to path
SERVICES_SHARED_PATH = Path("/app/services_shared")
if not SERVICES_SHARED_PATH.exists():
    # Fallback for local development
    SERVICES_SHARED_PATH = Path(__file__).parent.parent.parent.parent / "shared"
if str(SERVICES_SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SERVICES_SHARED_PATH))
```

### Affected Services
- `agro-advisor`
- `advisory-service`
- Any service importing from `crops.py` or `yemen_varieties.py`

### Prevention
- Check Dockerfile paths when adding new shared module imports
- Test Docker builds locally: `docker build -f apps/services/SERVICE/Dockerfile .`

---

## 5. TypeScript Path Mappings

### Symptom
```
error TS2307: Cannot find module '@sahool/shared-types' or its corresponding type declarations.
```

### Cause
TypeScript monorepo packages need explicit path mappings in `tsconfig.json`.

### Solution
Add path mappings to each package/app's `tsconfig.json`:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@sahool/shared-types": ["../../packages/shared-types/src"],
      "@sahool/shared-types/*": ["../../packages/shared-types/src/*"],
      "@sahool/i18n": ["../../packages/i18n/src"],
      "@sahool/i18n/*": ["../../packages/i18n/src/*"]
    }
  }
}
```

### Affected Files
- `apps/web/tsconfig.json`
- `apps/admin/tsconfig.json`
- `packages/api-client/tsconfig.json`

### Prevention
- When adding a new shared package, update all consumer tsconfigs
- Consider using a shared tsconfig base that includes common paths

---

## 6. FastAPI Complex Query Parameters

### Symptom
```
AssertionError: assert is_scalar_field(field) or is_scalar_sequence_field(field)
```

### Cause
FastAPI's `Query()` doesn't support complex nested types like `list[list[float]]`.

### Solution
Use a Pydantic model with `Body()` instead:

```python
# Before (fails)
@app.post("/v1/boundaries/refine")
async def refine_boundary(
    coords: list[list[float]] = Query(...),  # FAILS
    buffer_m: float = Query(50)
):
    pass

# After (works)
class RefineBoundaryRequest(BaseModel):
    coords: list[list[float]] = Field(..., description="Coordinates")
    buffer_m: float = Field(50, description="Buffer in meters")

@app.post("/v1/boundaries/refine")
async def refine_boundary(request: RefineBoundaryRequest):
    coords = request.coords
    buffer_m = request.buffer_m
```

### Prevention
- Use Pydantic models for any complex request parameters
- `Query()` is only for simple scalar types and lists of scalars

---

## 7. GitHub Actions Workflow Issues

### 7.1 Workflows Requiring Secrets

**Symptom:** Workflow fails on PRs from forks or when secrets aren't configured.

**Solution:** Disable PR triggers for workflows that require secrets:
```yaml
on:
  push:
    branches: [main, develop]
  # pull_request disabled - requires secrets
  workflow_dispatch:
```

**Affected Workflows:**
- `deploy-preview.yml` (SURGE_TOKEN, NETLIFY_AUTH_TOKEN)
- `lighthouse-ci.yml` (optional)

### 7.2 GitLeaks False Positives

**Symptom:** GitLeaks reports secrets in config files.

**Solution:** Update `.gitleaks.toml` allowlist:
```toml
[allowlist]
paths = [
    '''\.github/workflows/''',
    '''docker-compose.*\.yml$''',
    '''config/nats/.*\.conf$''',
]
```

### 7.3 E2E Tests Missing Artifacts

**Symptom:** E2E tests fail because web-build artifact doesn't exist.

**Solution:** Add fallback build:
```yaml
- name: Download Web Build
  uses: actions/download-artifact@v4
  with:
    name: web-build
    path: apps/web/.next
  continue-on-error: true

- name: Build Web App if artifact missing
  run: |
    if [ ! -d "apps/web/.next" ]; then
      cd apps/web && npm run build
    fi
  continue-on-error: true
```

### 7.4 Shared Package Build Failures (Web/Admin)

**Symptom:** Web App or Admin Dashboard build fails with module not found errors for @sahool packages.

**Cause:** Shared packages (shared-utils, shared-ui, api-client, shared-hooks, i18n) need to be built before the apps that depend on them.

**Solution:** Ensure `build:packages` script in root package.json includes all required packages:

```json
"build:packages": "npm run build --workspace=packages/shared-utils && npm run build --workspace=packages/i18n && npm run build --workspace=packages/shared-ui && npm run build --workspace=packages/api-client && npm run build --workspace=packages/shared-hooks"
```

**Prevention:**
- When adding new shared packages that other apps depend on, add them to `build:packages`
- Ensure the CI workflow runs `build:packages` before building apps
- Don't use `continue-on-error: true` on the `build:packages` step

---

## Quick Reference: Common Fixes

| Error | Quick Fix |
|-------|-----------|
| No space left on device | Add disk cleanup step |
| TasksCompanion not found | Run `dart run build_runner build` |
| Provider not defined | Add `export` statement |
| Module not found (Python) | Check Dockerfile COPY paths |
| Cannot find module (TS) | Add path mapping to tsconfig |
| Query param assertion | Use Pydantic model with Body() |
| @sahool/package not found | Add to `build:packages` script |

---

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Main development guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment procedures
- [OBSERVABILITY.md](OBSERVABILITY.md) - Monitoring and logging

---

*Last Updated: January 2026*
*Version: 1.0.0*
