# Security Hardening Summary — 2026-03-24

**PR**: #1315
**Branch**: `claude/fix-security-vulnerabilities-8Oywz`
**Files Changed**: 95 (534 additions, 236 deletions)

---

## 1. Container CVE Remediation (74 Dockerfiles)

### Python Services

| Package | Previous | Patched | CVE |
|---------|----------|---------|-----|
| setuptools | < 78.1.1 | >= 78.1.1 | CVE-2024-6345, PYSEC-2025-49 |
| wheel | < 0.46.2 | >= 0.46.2 | CVE-2026-24049 |
| pip | varies | >= 24.3.1 | Multiple |

**Build tool stripping** applied to 5 Trivy-scanned services to eliminate CVE footprint entirely:
- `weather-service`
- `billing-core`
- `vegetation-analysis-service`
- `crop-intelligence-service`
- `field-management-service` (Node.js — npm audit fix)

### Node.js Services (12 Dockerfiles)

Added `npm audit fix --omit=dev --legacy-peer-deps --ignore-scripts` to:
- field-management-service, user-service, chat-service, marketplace-service
- crop-growth-model, disaster-assessment, iot-service, lai-estimation
- research-core, yield-prediction, yield-prediction-service
- docker/Dockerfile.node.base (base image)

---

## 2. JWT Secret Hardening

### Before (Vulnerable)

```python
# shared/auth/config.py — hardcoded constant
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")

# shared/security/jwt.py — hardcoded fallback
default="sahool-dev-jwt-secret-key-change-in-production-min-32-chars"
```

### After (Secure)

```python
# Both modules now use:
# - production/staging: empty string → validate() raises JWTConfigError
# - development/test: secrets.token_hex(32) — random per-process, not forgeable
```

**Files changed**:
- `shared/auth/config.py` — New `_resolve_jwt_secret()` with environment-aware logic
- `shared/security/jwt.py` — New `_get_required_env()` with random fallback

---

## 3. Authentication Hardening (12+ Endpoints)

Previously unauthenticated endpoints now require `get_current_user`:

| Service | Endpoints |
|---------|-----------|
| vegetation-analysis-service | `weather_endpoints.py`, `spray_endpoints.py`, `parcel_endpoints.py`, `gdd_endpoints.py`, `boundary_endpoints.py` |
| inventory-service | `alert_endpoints.py` (mutating operations) |
| llm-orchestrator-service | `integrations.py` (NLP, satellite, ML, crew endpoints) |

---

## 4. Error Response Sanitization (20+ Endpoints)

Removed `str(e)` from HTTP 500 responses to prevent internal detail leakage:

```python
# Before (leaks internals)
raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")

# After (generic + logged)
logger.error(f"Failed: {e}", exc_info=True)
raise HTTPException(status_code=500, detail="Internal server error")
```

**Services affected**: provider-config, vegetation-analysis-service (5 files), inventory-service

---

## 5. Silent Exception Fixes

Replaced bare `except: pass` with proper logging:

| Service | File | Change |
|---------|------|--------|
| copilot-api | `chat.py` | `logger.warning("RAG context retrieval failed", exc_info=True)` |
| weather-service | `main.py` | `logger.warning("Failed to publish NATS event", exc_info=True)` |
| equipment-service | `main.py` | `logger.warning("...", exc_info=True)` |
| iot-sensor-hub | `main.py` | `logger.warning("...", exc_info=True)` |

---

## 6. CI/Infrastructure Fixes

| Component | Before | After |
|-----------|--------|-------|
| Checkov timeout | 25 min | 45 min |
| Checkov skip-paths | limited | Excludes vendored helm subdeps |
| Trivy scanner | `aquasecurity/trivy-action` | Direct binary v0.69.3 download |
| Web nonce validation | Bypassed in non-production | Fail-closed in all environments |

---

## 7. Test Fix (Quality Gate Unblock)

**Root cause**: `test_generate_text_function` and `test_generate_with_ollama_fallback` in
`tests/unit/ai/test_llm_provider.py` patched `get_llm_manager` but the module-level
`_global_manager` cache held a real instance from a previous test.

**Fix**: Added `patch("shared.ai.llm_provider._global_manager", None)` to reset the cache.

**Result**: 11,391 passed, 0 failed (previously 2 failed).

---

## Security Audit Checklist

| Check | Status |
|-------|--------|
| SQL injection (f-string SQL) | All use parameterized queries ✅ |
| yaml.load without SafeLoader | None found ✅ |
| pickle deserialization | None found ✅ |
| eval()/exec() with user input | None found ✅ |
| subprocess shell=True | None found ✅ |
| verify=False (TLS bypass) | None found ✅ |
| Hardcoded secrets | Replaced with random fallbacks ✅ |
| CORS wildcard with credentials | None found ✅ |
| dangerouslySetInnerHTML | Sanitized with nonce ✅ |
| Semgrep findings | False positive resolved ✅ |
