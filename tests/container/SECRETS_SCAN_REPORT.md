# Container Secrets Exposure Security Scan Report

**Date:** 2026-01-06
**Scope:** All Dockerfiles and docker-compose files in `/apps/services/`
**Total Files Scanned:** 57 (54 Dockerfiles + 3 docker-compose files)

---

## Executive Summary

**Status:** ✅ MOSTLY SECURE with ⚠️ 3 MEDIUM-RISK ISSUES

The comprehensive scan of all container configuration files revealed **NO CRITICAL SECRETS EXPOSURE** in Dockerfiles themselves. However, **3 docker-compose files contain hardcoded credentials** that pose a security risk for development and testing environments.

### Key Findings:
- ✅ **NO hardcoded API keys or tokens** in any Dockerfile
- ✅ **NO .env files** being copied into images
- ✅ **NO private keys** being copied into images
- ✅ **NO sensitive credentials** in ARG instructions
- ⚠️ **3 docker-compose files** contain hardcoded database passwords
- ✅ **All services** properly implement non-root users (security best practice)

---

## 1. Hardcoded Passwords, API Keys, and Tokens

### ❌ ISSUES FOUND: 3 Files

#### 1.1 Field Core - Profitability Service
**File:** `/apps/services/field-core/docker-compose.profitability.yml`

**Issues:**
```yaml
# Line 17: Hardcoded database credentials in connection string
DATABASE_URL=${DATABASE_URL:-postgresql://sahool:sahool@db:5432/sahool_fields}

# Line 38: Same issue repeated
DATABASE_URL=${DATABASE_URL:-postgresql://sahool:sahool@db:5432/sahool_fields}

# Lines 56-58: Hardcoded PostgreSQL credentials
POSTGRES_USER=sahool
POSTGRES_PASSWORD=sahool
POSTGRES_DB=sahool_fields
```

**Risk Level:** MEDIUM
**Impact:** If this docker-compose file is used in production, database credentials would be exposed.
**Recommendation:** Use Docker secrets or external secret management (HashiCorp Vault, AWS Secrets Manager, etc.)

---

#### 1.2 Field Management Service - Profitability
**File:** `/apps/services/field-management-service/docker-compose.profitability.yml`

**Issues:**
```yaml
# Line 17: Hardcoded database credentials
DATABASE_URL=${DATABASE_URL:-postgresql://sahool:sahool@db:5432/sahool_fields}

# Line 38: Same issue repeated
DATABASE_URL=${DATABASE_URL:-postgresql://sahool:sahool@db:5432/sahool_fields}

# Lines 56-58: Hardcoded PostgreSQL credentials
POSTGRES_USER=sahool
POSTGRES_PASSWORD=sahool
POSTGRES_DB=sahool_fields
```

**Risk Level:** MEDIUM
**Impact:** Same as above
**Recommendation:** Use environment variables or Docker secrets

---

#### 1.3 Notification Service - Development Environment
**File:** `/apps/services/notification-service/docker-compose.dev.yml`

**Issues:**
```yaml
# Lines 11-14: Hardcoded PostgreSQL credentials
POSTGRES_DB: sahool_notifications
POSTGRES_USER: sahool
POSTGRES_PASSWORD: sahool123

# Lines 57-58: Hardcoded pgAdmin credentials
PGADMIN_DEFAULT_EMAIL: admin@sahool.com
PGADMIN_DEFAULT_PASSWORD: admin123
```

**Risk Level:** MEDIUM
**Impact:** Development credentials exposed. While marked as "dev", these could be accidentally used in production.
**Recommendation:**
- Use `.env` files (not committed to git)
- Add `.env` to `.gitignore`
- Document credential requirements without hardcoding them

---

## 2. COPY of .env Files

### ✅ NO ISSUES FOUND

**Result:** No Dockerfile contains `COPY .env` or similar instructions.

**Analysis:** All 54 Dockerfiles were scanned for patterns:
- `COPY .env`
- `COPY *.env`
- `COPY **/.env`
- `ADD .env`

None found. This is excellent security practice.

---

## 3. ENV Variables with Sensitive Values

### ✅ NO CRITICAL ISSUES FOUND

**Result:** All ENV variables in Dockerfiles are either:
1. Configuration values (ports, paths, Python settings)
2. Placeholders expecting runtime values
3. Non-sensitive system settings

### Examples of SAFE ENV usage:
```dockerfile
# Configuration values (safe)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Placeholders for runtime injection (safe)
ENV DATABASE_URL=${DATABASE_URL}
ENV NATS_URL=${NATS_URL}
```

**No hardcoded secrets found in any Dockerfile ENV statements.**

---

## 4. Private Keys Being Copied

### ✅ NO ISSUES FOUND

**Result:** No private keys, SSH keys, or SSL certificates are being copied into any container images.

**Scanned patterns:**
- `*.key`
- `*.pem`
- `id_rsa`
- `*.crt` (certificates)
- SSH key patterns
- SSL/TLS key patterns

**Best Practice Observed:** All services that need SSL/TLS or SSH access should mount secrets at runtime, not bake them into images.

---

## 5. Credentials in ARG Instructions

### ✅ NO ISSUES FOUND

**Result:** ARG instructions only contain build-time configuration values, not credentials.

### Examples of SAFE ARG usage found:
```dockerfile
ARG PYTHON_VERSION=3.11
ARG NODE_VERSION=20
ARG SERVICE_NAME=field-core
ARG SERVICE_VERSION=16.0.0
```

**No sensitive credentials found in any ARG instructions.**

---

## Security Best Practices Observed

### ✅ Excellent Security Implementations:

1. **Non-Root Users (100% compliance)**
   - All 54 services create and use non-root users
   - Example pattern:
   ```dockerfile
   RUN groupadd --system sahool && \
       useradd --system --gid sahool sahool
   USER sahool
   ```

2. **Multi-Stage Builds**
   - Many services use multi-stage builds to reduce attack surface
   - Builder dependencies not included in final images

3. **Minimal Base Images**
   - Use of `-slim` and `-alpine` variants reduces vulnerabilities
   - Examples: `python:3.11-slim`, `node:20-alpine`

4. **No Secrets in Layers**
   - No `RUN` commands with embedded secrets
   - No curl/wget commands with authentication tokens

5. **Health Checks**
   - All services implement proper health checks
   - No credentials exposed in health check commands

6. **Read-Only Filesystems (docker-compose)**
   - Some services use `read_only: true`
   - Security options like `no-new-privileges:true`

---

## Service-by-Service Analysis

### Total Services Scanned: 54

| Service | Dockerfile | Secrets Found | Risk Level |
|---------|-----------|---------------|------------|
| advisory-service | ✅ Clean | None | LOW |
| agent-registry | ✅ Clean | None | LOW |
| agro-advisor | ✅ Clean | None | LOW |
| agro-rules | ✅ Clean | None | LOW |
| ai-advisor | ✅ Clean | None | LOW |
| ai-agents-core | ✅ Clean | None | LOW |
| alert-service | ✅ Clean | None | LOW |
| astronomical-calendar | ✅ Clean | None | LOW |
| billing-core | ✅ Clean | None | LOW |
| chat-service | ✅ Clean | None | LOW |
| code-review-service | ✅ Clean | None | LOW |
| community-chat | ✅ Clean | None | LOW |
| crop-growth-model | ✅ Clean | None | LOW |
| crop-health | ✅ Clean | None | LOW |
| crop-health-ai | ✅ Clean | None | LOW |
| crop-intelligence-service | ✅ Clean | None | LOW |
| demo-data | ✅ Clean | None | LOW |
| disaster-assessment | ✅ Clean | None | LOW |
| equipment-service | ✅ Clean | None | LOW |
| fertilizer-advisor | ✅ Clean | None | LOW |
| field-chat | ✅ Clean | None | LOW |
| field-core | ✅ Clean | None | LOW |
| field-core (Python) | ✅ Clean | None | LOW |
| field-intelligence | ✅ Clean | None | LOW |
| field-management-service | ✅ Clean | None | LOW |
| field-management (Python) | ✅ Clean | None | LOW |
| field-ops | ✅ Clean | None | LOW |
| field-service | ✅ Clean | None | LOW |
| globalgap-compliance | ✅ Clean | None | LOW |
| indicators-service | ✅ Clean | None | LOW |
| inventory-service | ✅ Clean | None | LOW |
| iot-gateway | ✅ Clean | None | LOW |
| iot-service | ✅ Clean | None | LOW |
| irrigation-smart | ✅ Clean | None | LOW |
| lai-estimation | ✅ Clean | None | LOW |
| marketplace-service | ✅ Clean | None | LOW |
| mcp-server | ✅ Clean | None | LOW |
| ndvi-engine | ✅ Clean | None | LOW |
| ndvi-processor | ✅ Clean | None | LOW |
| notification-service | ✅ Clean | None | LOW |
| provider-config | ✅ Clean | None | LOW |
| research-core | ✅ Clean | None | LOW |
| satellite-service | ✅ Clean | None | LOW |
| task-service | ✅ Clean | None | LOW |
| user-service | ✅ Clean | None | LOW |
| vegetation-analysis-service | ✅ Clean | None | LOW |
| virtual-sensors | ✅ Clean | None | LOW |
| weather-advanced | ✅ Clean | None | LOW |
| weather-core | ✅ Clean | None | LOW |
| weather-service | ✅ Clean | None | LOW |
| ws-gateway | ✅ Clean | None | LOW |
| yield-engine | ✅ Clean | None | LOW |
| yield-prediction | ✅ Clean | None | LOW |
| yield-prediction-service | ✅ Clean | None | LOW |

---

## Docker Compose Files Analysis

| File | Issues | Risk Level |
|------|--------|------------|
| field-core/docker-compose.profitability.yml | ⚠️ Hardcoded DB credentials | MEDIUM |
| field-management-service/docker-compose.profitability.yml | ⚠️ Hardcoded DB credentials | MEDIUM |
| notification-service/docker-compose.dev.yml | ⚠️ Hardcoded DB & pgAdmin credentials | MEDIUM |

---

## Recommendations

### Immediate Actions Required:

1. **Remove Hardcoded Credentials from docker-compose files**
   ```yaml
   # BEFORE (BAD):
   environment:
     POSTGRES_PASSWORD: sahool123

   # AFTER (GOOD):
   environment:
     POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
   ```

2. **Create .env.example files**
   ```bash
   # .env.example (committed to git)
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_DB=your_database

   # .env (NOT committed to git - in .gitignore)
   POSTGRES_USER=sahool
   POSTGRES_PASSWORD=actual_secure_password
   POSTGRES_DB=sahool_notifications
   ```

3. **Update .gitignore**
   ```gitignore
   # Environment files
   .env
   .env.local
   .env.*.local
   *.env
   ```

4. **Use Docker Secrets for Production**
   ```yaml
   # docker-compose.yml
   secrets:
     db_password:
       external: true

   services:
     postgres:
       secrets:
         - db_password
       environment:
         POSTGRES_PASSWORD_FILE: /run/secrets/db_password
   ```

### Long-term Improvements:

1. **Implement Secret Management**
   - Use HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault
   - Rotate credentials regularly
   - Use different credentials for each environment

2. **Container Security Scanning**
   - Integrate tools like Trivy, Snyk, or Aqua Security
   - Scan images for vulnerabilities before deployment
   - Implement automated scanning in CI/CD pipeline

3. **Runtime Secret Injection**
   - Use Kubernetes secrets for K8s deployments
   - Use Docker secrets for Swarm deployments
   - Mount secrets as files, not environment variables

4. **Audit and Monitoring**
   - Log all secret access attempts
   - Monitor for unauthorized access
   - Implement secret rotation policies

---

## Compliance Notes

### Security Standards Alignment:

- ✅ **CIS Docker Benchmark:** Non-root users implemented
- ✅ **OWASP Container Security:** No secrets in images
- ⚠️ **PCI DSS:** Hardcoded credentials in compose files violate requirement 8
- ✅ **NIST SP 800-190:** Minimal attack surface achieved

---

## Scan Methodology

### Tools & Techniques Used:

1. **Pattern Matching**
   - Searched for common secret patterns (passwords, keys, tokens)
   - Regex patterns for API keys, private keys
   - Manual review of all ENV and ARG instructions

2. **Structural Analysis**
   - Reviewed COPY and ADD instructions
   - Analyzed multi-stage builds
   - Checked for secret leakage in layers

3. **Best Practice Verification**
   - Verified non-root user implementation
   - Checked for minimal base images
   - Reviewed health check implementations

### Files Scanned:
```
/apps/services/*/Dockerfile
/apps/services/*/Dockerfile.*
/apps/services/*/docker-compose*.yml
/apps/services/*/docker-compose*.yaml
```

---

## Conclusion

**Overall Security Posture:** GOOD ✅

The container configuration demonstrates **excellent security practices** for Dockerfiles:
- No secrets baked into images
- Proper user isolation
- Minimal attack surface
- Clean dependency management

**Action Required:** Address the 3 docker-compose files with hardcoded credentials before using them in any production-like environment.

**Next Steps:**
1. ✅ Review this report with security team
2. ⚠️ Fix hardcoded credentials in docker-compose files
3. ✅ Implement secret management solution
4. ✅ Add automated security scanning to CI/CD
5. ✅ Document secret management procedures

---

## Appendix: Scanned File Inventory

### Dockerfiles (54 files):
```
/apps/services/advisory-service/Dockerfile
/apps/services/agent-registry/Dockerfile
/apps/services/agro-advisor/Dockerfile
/apps/services/agro-rules/Dockerfile
/apps/services/ai-advisor/Dockerfile
/apps/services/ai-agents-core/Dockerfile
/apps/services/alert-service/Dockerfile
/apps/services/astronomical-calendar/Dockerfile
/apps/services/billing-core/Dockerfile
/apps/services/chat-service/Dockerfile
/apps/services/code-review-service/Dockerfile
/apps/services/community-chat/Dockerfile
/apps/services/crop-growth-model/Dockerfile
/apps/services/crop-health/Dockerfile
/apps/services/crop-health-ai/Dockerfile
/apps/services/crop-intelligence-service/Dockerfile
/apps/services/demo-data/Dockerfile
/apps/services/disaster-assessment/Dockerfile
/apps/services/equipment-service/Dockerfile
/apps/services/fertilizer-advisor/Dockerfile
/apps/services/field-chat/Dockerfile
/apps/services/field-core/Dockerfile
/apps/services/field-core/Dockerfile.python
/apps/services/field-intelligence/Dockerfile
/apps/services/field-management-service/Dockerfile
/apps/services/field-management-service/Dockerfile.python
/apps/services/field-ops/Dockerfile
/apps/services/field-service/Dockerfile
/apps/services/globalgap-compliance/Dockerfile
/apps/services/indicators-service/Dockerfile
/apps/services/inventory-service/Dockerfile
/apps/services/iot-gateway/Dockerfile
/apps/services/iot-service/Dockerfile
/apps/services/irrigation-smart/Dockerfile
/apps/services/lai-estimation/Dockerfile
/apps/services/marketplace-service/Dockerfile
/apps/services/mcp-server/Dockerfile
/apps/services/ndvi-engine/Dockerfile
/apps/services/ndvi-processor/Dockerfile
/apps/services/notification-service/Dockerfile
/apps/services/provider-config/Dockerfile
/apps/services/research-core/Dockerfile
/apps/services/satellite-service/Dockerfile
/apps/services/task-service/Dockerfile
/apps/services/user-service/Dockerfile
/apps/services/vegetation-analysis-service/Dockerfile
/apps/services/virtual-sensors/Dockerfile
/apps/services/weather-advanced/Dockerfile
/apps/services/weather-core/Dockerfile
/apps/services/weather-service/Dockerfile
/apps/services/ws-gateway/Dockerfile
/apps/services/yield-engine/Dockerfile
/apps/services/yield-prediction/Dockerfile
/apps/services/yield-prediction-service/Dockerfile
```

### Docker Compose Files (3 files):
```
/apps/services/field-core/docker-compose.profitability.yml
/apps/services/field-management-service/docker-compose.profitability.yml
/apps/services/notification-service/docker-compose.dev.yml
```

---

**Report Generated By:** Container Security Scan Tool
**Scan Date:** 2026-01-06
**Report Version:** 1.0
**Classification:** INTERNAL USE ONLY
