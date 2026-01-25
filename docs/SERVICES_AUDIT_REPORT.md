# SAHOOL Services Audit Report

**Date**: 2026-01-25
**Version**: 16.0.0
**Auditor**: Claude AI Assistant

---

## Executive Summary

This report presents a comprehensive audit of all 61 services in the SAHOOL platform. The audit identified critical issues that need immediate attention, along with recommendations for improvement.

### Key Statistics

| Category | Count | Percentage |
|----------|-------|------------|
| **Total Services** | 61 | 100% |
| **Python Services** | 42 | 69% |
| **Node.js Services** | 12 | 20% |
| **Hybrid Services** | 2 | 3% |
| **Stub Services** | 5 | 8% |

### Critical Issues Found

| Issue Type | Count | Severity |
|------------|-------|----------|
| Missing Prisma Schema | 5 | CRITICAL |
| ORM Conflicts | 1 | CRITICAL |
| Port Conflicts | 4 | HIGH |
| Database Driver Conflicts | 5 | HIGH |
| Incomplete Dockerfile | 1 | MEDIUM |

---

## Node.js Services Audit

### Services Using Prisma Correctly

| Service | Status | Notes |
|---------|--------|-------|
| chat-service | OK | Full Prisma setup |
| iot-service | OK | Full Prisma setup |
| marketplace-service | OK | Full Prisma setup |
| research-core | OK | Full Prisma setup |
| user-service | OK | Full Prisma setup |

### Services Missing Prisma Schema (CRITICAL)

These services have Prisma dependencies but **NO schema.prisma file**:

| Service | Issue | Impact |
|---------|-------|--------|
| crop-growth-model | Missing prisma/schema.prisma | Build will fail |
| disaster-assessment | Missing prisma/schema.prisma | Build will fail |
| lai-estimation | Missing prisma/schema.prisma | Build will fail |
| yield-prediction-service | Missing prisma/schema.prisma | Build will fail |
| yield-prediction | Missing prisma/schema.prisma | Build will fail |

**Recommended Actions:**
1. Create `prisma/schema.prisma` for each service
2. Run `npx prisma generate`
3. Update Dockerfile to include Prisma build steps

### ORM Conflict (RESOLVED)

| Service | Issue | Status |
|---------|-------|--------|
| field-management-service | Had both Prisma and TypeORM | **FIXED** - Removed Prisma |

### Stateless Services (No ORM Needed)

| Service | Purpose |
|---------|---------|
| code-review-agent | AI code review (uses Claude SDK) |
| community-chat | In-memory chat (Socket.io) |

### Incomplete Dockerfile

| Service | Issue |
|---------|-------|
| weather-service | Has Prisma schema but Dockerfile missing `prisma generate` |

---

## Python Services Audit

### Port Conflicts (CRITICAL)

Multiple services are configured to use the same ports:

| Port | Service 1 | Service 2 | Action Required |
|------|-----------|-----------|-----------------|
| 8090 | code-fix-agent | vegetation-analysis-service | Reassign ports |
| 8121 | agent-registry | skills-service | Reassign ports |
| 8130 | ai-agents-service | ussd-gateway | Reassign ports |
| 8131 | crm-service | logistics-service | Reassign ports |

### Database Driver Conflicts (HIGH)

Services with incompatible async/sync database drivers:

| Service | Conflict | Resolution |
|---------|----------|------------|
| alert-service | asyncpg + psycopg2-binary | Keep asyncpg (async), remove psycopg2 |
| audit-service | asyncpg + psycopg2 + SQLAlchemy + Tortoise | Choose ONE approach |
| billing-core | asyncpg + psycopg2-binary | Keep asyncpg (async), remove psycopg2 |
| field-intelligence | asyncpg + psycopg2-binary | Keep asyncpg (async), remove psycopg2 |
| inventory-service | asyncpg + psycopg2-binary | Keep asyncpg (async), remove psycopg2 |

**Recommendation:** Use Tortoise ORM + asyncpg for all async Python services (SAHOOL standard).

### Version Inconsistency

| Service | Issue |
|---------|-------|
| advisory-service | App version 15.3.3, health endpoint 16.0.0 |

### Services Configured Correctly

All other Python services (36 services) have:
- Valid requirements.txt
- Proper Dockerfile with HEALTHCHECK
- Health endpoints (/healthz, /readyz)
- Consistent FastAPI patterns

---

## Stub Services (Not Yet Implemented)

These services have only README.md files:

| Service | Status |
|---------|--------|
| cooperative-service | Stub |
| drone-service | Stub |
| pest-detection-service | Stub |
| soil-analysis-service | Stub |
| traceability-service | Stub |

---

## Fixes Applied in This Audit

### 1. field-management-service - Prisma Removal

**Commit:** `54651d0`

Changes:
- Removed `@prisma/client` and `prisma` from package.json
- Removed all Prisma scripts (generate, migrate, studio)
- Simplified Dockerfile (removed Prisma commands)
- Removed OpenSSL dependency

### 2. data-source.ts - DATABASE_URL Support

**Commit:** `47f0be4`

Changes:
- Added DATABASE_URL parsing support
- Fixed TypeScript type error
- Changed default DB_HOST from "postgres" to "localhost"
- Supports both connection modes:
  - `DATABASE_URL=postgresql://user:pass@host:5432/dbname`
  - Individual vars: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

---

## Recommendations

### Priority 1: Critical (Immediate Action)

1. **Create Missing Prisma Schemas**
   ```bash
   # For each service missing schema:
   cd apps/services/[service-name]
   npx prisma init
   # Define models in prisma/schema.prisma
   npx prisma generate
   ```

2. **Resolve Port Conflicts**
   - Update `governance/services.yaml` with unique ports
   - Update Dockerfiles and docker-compose.yml

### Priority 2: High

3. **Fix Database Driver Conflicts**
   - Remove psycopg2-binary from async services
   - Standardize on Tortoise ORM + asyncpg

4. **Fix weather-service Dockerfile**
   - Add `prisma generate` commands
   - Copy schema to production stage

### Priority 3: Medium

5. **Version Consistency**
   - Update advisory-service to 16.0.0

6. **Implement Stub Services**
   - Complete drone-service, pest-detection-service, etc.

---

## Port Allocation Reference

### Current Port Map (Services)

| Port Range | Category |
|------------|----------|
| 3000-3030 | Node.js Services |
| 8081-8099 | Core Python Services |
| 8100-8130 | Analytics & AI Services |
| 8131-8160 | Business Services |
| 8160-8200 | Agent Services |

### Recommended Port Reassignments

| Service | Current Port | New Port |
|---------|--------------|----------|
| code-fix-agent | 8090 | 8161 |
| skills-service | 8121 | 8170 |
| ussd-gateway | 8130 | 8180 |
| logistics-service | 8131 | 8181 |

---

## Service Categories

### AI & Intelligence Layer
- agent-registry, ai-advisor, ai-agents-core, ai-agents-service
- code-fix-agent, code-review-agent, code-review-service
- crop-intelligence-service, field-intelligence, knowledge-graph
- skills-service

### Field Operations
- field-management-service (TypeORM)
- field-chat, globalgap-compliance
- irrigation-smart, vegetation-analysis-service

### Analytics & Processing
- indicators-service, ndvi-engine, ndvi-processor
- virtual-sensors, yield-engine, yield-prediction

### Business & Communication
- billing-core, crm-service, notification-service
- marketplace-service, community-chat, chat-service

### Infrastructure
- iot-gateway, iot-service, ws-gateway
- mcp-server, weather-service, astronomical-calendar

---

## Appendix: Service File Paths

### Node.js Services
```
apps/services/chat-service/
apps/services/code-review-agent/
apps/services/community-chat/
apps/services/crop-growth-model/
apps/services/disaster-assessment/
apps/services/field-management-service/
apps/services/iot-service/
apps/services/lai-estimation/
apps/services/marketplace-service/
apps/services/research-core/
apps/services/user-service/
apps/services/weather-service/
apps/services/yield-prediction/
apps/services/yield-prediction-service/
```

### Shared Packages
```
packages/field-shared/          # TypeORM entities for field services
packages/shared-types/          # TypeScript types
packages/shared-utils/          # Utility functions
packages/nestjs-auth/           # NestJS auth module
```

---

*Report generated by Claude AI Assistant*
*Last updated: 2026-01-25*
