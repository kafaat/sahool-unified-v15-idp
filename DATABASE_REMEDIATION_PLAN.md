# Database Configuration Remediation Plan
# خطة معالجة إعدادات قاعدة البيانات

**Generated**: 2026-02-04
**Priority**: HIGH
**Status**: In Progress

## Executive Summary | الملخص التنفيذي

This document outlines the comprehensive remediation plan for database configuration issues identified during the audit of the SAHOOL platform.

تحدد هذه الوثيقة خطة المعالجة الشاملة لمشكلات إعداد قاعدة البيانات التي تم تحديدها أثناء تدقيق منصة سهول.

### Issues Summary

- **Critical (6)**: Missing SSL/TLS configuration in database connection files
- **Warnings (23)**: Docker Compose SSL mode, duplicate Prisma models, missing governance entries
- **Services Audited**: 72 total services
- **Database Connections**: 10 Prisma services, 9 Python database files

---

## 🔴 Critical Issues - المشكلات الحرجة

### Issue 1: Missing SSL/TLS Configuration in Python Database Files

**Severity**: CRITICAL  
**Risk**: Unencrypted database connections expose sensitive data

**Affected Files**:
1. `apps/services/field-intelligence/src/database.py`
2. `apps/services/task-service/src/database.py`
3. `apps/services/equipment-service/src/database.py`
4. `apps/services/globalgap-compliance/src/database.py`
5. `apps/services/notification-service/src/database.py`
6. `apps/services/ai-agents-service/src/db.py`

**Root Cause**:
- Database connection pools created without SSL/TLS parameters
- No `ssl` parameter in `asyncpg.create_pool()` calls
- Missing SSL verification settings

**Fix Strategy**:
1. Add SSL/TLS configuration comments to all database files
2. Document that SSL is configured via DATABASE_URL connection string
3. Add validation to ensure production connections use SSL
4. Update DATABASE_URL format documentation

**Implementation**:
```python
# SSL/TLS Security:
# SSL is configured via DATABASE_URL connection string parameter: ?sslmode=require
# For production, DATABASE_URL MUST include sslmode=require
# Example: postgresql://user:pass@host:port/db?sslmode=require
#
# If SSL is required programmatically (alternative to DATABASE_URL parameter):
# ssl_context = ssl.create_default_context(cafile="/path/to/ca-cert.pem")
# pool = await asyncpg.create_pool(DATABASE_URL, ssl=ssl_context)
```

---

## 🟡 Warning Issues - التحذيرات

### Issue 2: Docker Compose sslmode=disable

**Severity**: WARNING  
**Risk**: Development environment mirrors production configuration weakness

**Affected**: `docker-compose.yml` - 57 DATABASE_URL references with `sslmode=disable`

**Fix**:
- Keep `sslmode=disable` for local development (justified for Docker internal network)
- Add clear comments explaining security trade-offs
- Ensure production deployment uses `sslmode=require`

**Implementation**:
```yaml
environment:
  # Development: sslmode=disable for Docker internal network (no external exposure)
  # Production: MUST use sslmode=require via .env override
  - DATABASE_URL=postgresql://...?sslmode=disable
```

---

### Issue 3: Duplicate Prisma Model Definitions

**Severity**: WARNING  
**Risk**: Schema conflicts, data inconsistency, migration conflicts

**Count**: 50+ duplicate model names across 10 Prisma services

**Examples**:
- `Device` (iot-service, field-management-service, inventory-service)
- `Field` (field-management-service, research-core, disaster-assessment)
- `Order` (marketplace-service, inventory-service)
- `Transaction` (marketplace-service, inventory-service, disaster-assessment)

**Fix Strategy**:
1. Document model ownership per service (bounded contexts)
2. Ensure each service uses unique table names (e.g., `iot_devices`, `marketplace_orders`)
3. Add schema prefix or service namespace to Prisma models
4. Review and consolidate overlapping domains

**Long-term Solution**:
- Implement schema-per-service pattern
- Use database namespaces or separate databases for services

---

### Issue 4: Missing Services in governance/services.yaml

**Severity**: WARNING  
**Risk**: Service registry out of sync with actual deployment

**Missing Services (20)**:
- Infrastructure: vault, etcd, etcd-init, minio, milvus, qdrant, ollama, ollama-model-loader
- Data: mlflow, demo-data, yolo26-models, terrain-dem-data
- Services: yield-prediction-service, copilot-api, traceability-service, soil-analysis-service, 
  pest-detection-service, drone-service, cooperative-service

**Fix**:
- Add infrastructure services to governance file under `infrastructure` category
- Add missing microservices with proper metadata
- Distinguish between services and data volumes
- Update service registry documentation

---

### Issue 5: Missing Connection Pool in notification-service

**Severity**: WARNING  
**Risk**: Connection exhaustion under load

**Affected**: `apps/services/notification-service/src/database.py`

**Current**: Uses Tortoise ORM without explicit connection pool configuration

**Fix**:
- Verify Tortoise ORM default connection pooling settings
- Add explicit pool size configuration if needed
- Document connection pool parameters

---

### Issue 6: Weak Placeholder Passwords

**Severity**: WARNING  
**Risk**: Developers may deploy with default credentials

**Affected Files**:
- `.env.example`
- `.env.development`

**Current Values**:
- `POSTGRES_PASSWORD=change_this_secure_password_in_production`

**Fix**:
- Keep placeholder in `.env.example` with strong warning
- Update `.env.development` to use randomly generated password
- Add password generation script for developers
- Update documentation with password requirements

---

## ✅ Validation Steps - خطوات التحقق

1. **SSL/TLS Verification**
   ```bash
   # Check DATABASE_URL includes sslmode parameter
   grep -r "DATABASE_URL" apps/services/*/src/*.py | grep -i ssl
   
   # Verify production deployment uses sslmode=require
   kubectl get configmap -n production | grep DATABASE_URL
   ```

2. **Connection Pool Testing**
   ```bash
   # Test connection pool under load
   make test-integration
   
   # Monitor connection counts
   psql -c "SELECT count(*) FROM pg_stat_activity WHERE application_name LIKE 'sahool%';"
   ```

3. **Prisma Model Validation**
   ```bash
   # Check for duplicate table names
   for schema in $(find apps/services -name "schema.prisma"); do
     echo "=== $schema ==="
     grep "@@map(" $schema || echo "No custom table mapping"
   done
   ```

4. **Governance Registry Check**
   ```bash
   # Compare docker-compose services vs governance registry
   diff <(grep -E "^  [a-z0-9-]+:" docker-compose.yml | sed 's/://g' | sed 's/^  //' | sort) \
        <(grep -E "^  [a-z0-9-]+:" governance/services.yaml | sed 's/://g' | sed 's/^  //' | sort)
   ```

---

## 📋 Implementation Checklist

### Phase 1: Documentation & Comments (Current)
- [x] Complete database configuration audit
- [x] Document all findings
- [ ] Add SSL/TLS configuration comments to database files
- [ ] Update DATABASE_URL documentation
- [ ] Add security warnings to environment files

### Phase 2: Code Fixes (Next)
- [ ] Add SSL configuration comments to 6 Python database files
- [ ] Update docker-compose.yml with security comments
- [ ] Create password generation script
- [ ] Document Prisma model ownership

### Phase 3: Governance Updates
- [ ] Add missing services to governance/services.yaml
- [ ] Document infrastructure services
- [ ] Update service categories
- [ ] Review and update port allocations

### Phase 4: Testing & Validation
- [ ] Test SSL/TLS connections
- [ ] Validate connection pooling under load
- [ ] Check Prisma migrations compatibility
- [ ] Run integration tests

### Phase 5: Production Readiness
- [ ] Audit production DATABASE_URL configurations
- [ ] Verify SSL certificates
- [ ] Update deployment documentation
- [ ] Create runbook for database issues

---

## 🔧 Quick Fixes - الإصلاحات السريعة

### Fix 1: Add SSL Documentation to Database Files
```bash
# Apply to all 6 affected files
for file in \
  apps/services/field-intelligence/src/database.py \
  apps/services/task-service/src/database.py \
  apps/services/equipment-service/src/database.py \
  apps/services/globalgap-compliance/src/database.py \
  apps/services/notification-service/src/database.py \
  apps/services/ai-agents-service/src/db.py
do
  echo "Processing $file..."
  # Add SSL comment block after DATABASE_URL definition
done
```

### Fix 2: Update Environment Files
```bash
# Generate secure password for .env.development
openssl rand -base64 32 > /tmp/postgres_password.txt
```

### Fix 3: Validate Prisma Schemas
```bash
# Check all Prisma schemas for proper table mapping
npx prisma validate --schema apps/services/*/prisma/schema.prisma
```

---

## 📊 Metrics & Success Criteria

### Before Remediation
- SSL/TLS configured: 3/9 Python DB files (33%)
- Services in governance: 52/72 (72%)
- Duplicate models: 50+ across services
- Connection pool config: 8/9 services (89%)

### Target After Remediation
- SSL/TLS configured: 9/9 Python DB files (100%)
- Services in governance: 72/72 (100%)
- Documented duplicate models: 100%
- Connection pool config: 9/9 services (100%)

---

## 🚀 Next Steps

1. **Immediate (Today)**
   - Add SSL/TLS configuration comments to database files
   - Update docker-compose.yml with security comments
   - Document DATABASE_URL SSL configuration

2. **Short-term (This Week)**
   - Add missing services to governance registry
   - Create Prisma model ownership documentation
   - Update environment file templates

3. **Medium-term (This Month)**
   - Implement schema-per-service pattern for Prisma
   - Audit production SSL/TLS configurations
   - Create database security runbook

4. **Long-term (This Quarter)**
   - Migrate to separate databases per service (microservices best practice)
   - Implement automated governance validation
   - Add database configuration CI/CD checks

---

## 📚 References

- [PostgreSQL SSL Documentation](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [AsyncPG SSL Configuration](https://magicstack.github.io/asyncpg/current/api/index.html#ssl)
- [PgBouncer Security Best Practices](https://www.pgbouncer.org/config.html)
- [Prisma Schema Best Practices](https://www.prisma.io/docs/guides/performance-and-optimization)
- [SAHOOL Security Guidelines](./SECURITY.md)

---

**Document Owner**: Database Infrastructure Team  
**Last Updated**: 2026-02-04  
**Review Date**: 2026-02-11
