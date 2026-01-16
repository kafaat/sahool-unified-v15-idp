# Container Status Analysis Report

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Executive Summary

### Overall Status

- **Total Containers:** 50+
- **Running & Healthy:** ~40 containers
- **Unhealthy:** 5 containers
- **Restarting:** 6 containers
- **Critical Issues:** 3

---

## Container Status Breakdown

### ✅ Healthy & Running (40+ containers)

- Infrastructure: postgres, redis, nats, kong, pgbouncer, qdrant, mqtt, ollama, etcd, milvus, minio
- Core Services: advisory-service, agro-advisor, alert-service, field-management-service, weather-service, iot-service, etc.
- Most services are operational

### ⚠️ Unhealthy Containers (5)

1. **sahool-billing-core**
   - **Status:** Unhealthy
   - **Error:** `The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.`
   - **Issue:** Using sync driver (psycopg2) with async SQLAlchemy
   - **Fix Required:** Switch to asyncpg or use sync SQLAlchemy

2. **sahool-equipment-service**
   - **Status:** Unhealthy
   - **Issue:** Health check failing
   - **Action:** Check service logs for specific error

3. **sahool-provider-config**
   - **Status:** Unhealthy
   - **Issue:** Health check failing
   - **Action:** Check service logs for specific error

4. **sahool-task-service**
   - **Status:** Unhealthy
   - **Issue:** Health check failing
   - **Action:** Check service logs for specific error

5. **sahool-yield-prediction-service**
   - **Status:** Unhealthy
   - **Issue:** Health check failing
   - **Action:** Check service logs for specific error

### 🔄 Restarting Containers (6)

1. **sahool-ai-advisor**
   - **Status:** Restarting (1 second ago)
   - **Likely Cause:** DNS resolution failure (Kong can't find service)
   - **Action:** Verify service is defined in docker-compose.yml

2. **sahool-chat-service**
   - **Status:** Restarting (11 seconds ago)
   - **Error:** PrismaClientInitializationError - Can't reach database
   - **Issue:** Database connection through pgbouncer failing
   - **Action:** Verify pgbouncer authentication is working

3. **sahool-inventory-service**
   - **Status:** Restarting (5 seconds ago)
   - **Action:** Check logs for specific error

4. **sahool-marketplace**
   - **Status:** Restarting (18 seconds ago)
   - **Error:** `errorCode: undefined` (Prisma connection issue)
   - **Issue:** Database connection problem
   - **Action:** Verify database connectivity

5. **sahool-ndvi-processor**
   - **Status:** Restarting (16 seconds ago)
   - **Action:** Check logs for specific error

6. **sahool-research-core**
   - **Status:** Restarting (16 seconds ago)
   - **Error:** `errorCode: undefined` (Prisma connection issue)
   - **Issue:** Database connection problem
   - **Action:** Verify database connectivity

---

## Critical Issues

### 1. Kong DNS Resolution Failures

**Services Affected:**

- ai-advisor
- research-core
- marketplace-service
- crop-intelligence-service
- field-management-service
- billing-core
- weather-service

**Error Pattern:**

```
querying dns for <service> failed: dns server error: 3 name error
```

**Root Cause:** Services are not running or not properly registered in Docker network

**Impact:** Kong cannot route requests to these services

**Fix:**

- Ensure all services are running
- Verify services are on the same Docker network (`sahool-network`)
- Check service names match Kong configuration

### 2. Database Connection Issues

#### PgBouncer Authentication

- **Service:** notification-service
- **Error:** `password authentication failed for user "pgbouncer"`
- **Status:** Fixed in previous session (SCRAM auth configured)
- **Action:** Restart notification-service to pick up new auth config

#### Prisma Connection Errors

- **Services:** chat-service, marketplace, research-core
- **Error:** `PrismaClientInitializationError: Can't reach database server at pgbouncer:6432`
- **Status:** Should be fixed with SCRAM auth changes
- **Action:** Restart affected services

### 3. Async Driver Mismatch

- **Service:** billing-core
- **Error:** `The asyncio extension requires an async driver. The loaded 'psycopg2' is not async.`
- **Fix:** Change database URL to use `asyncpg` or switch to sync SQLAlchemy

---

## Recommendations

### Immediate Actions

1. **Restart Unhealthy Services:**

   ```bash
   docker compose restart billing-core equipment-service provider-config task-service yield-prediction-service
   ```

2. **Fix Billing Core Async Driver:**
   - Update `DATABASE_URL` to use `postgresql+asyncpg://` instead of `postgresql+psycopg2://`
   - Or switch billing-core to use sync SQLAlchemy

3. **Verify PgBouncer Auth:**

   ```bash
   docker compose restart notification-service chat-service marketplace research-core
   ```

4. **Check DNS Resolution:**
   ```bash
   docker compose ps | grep -E "(ai-advisor|research-core|marketplace)"
   ```
   If services are not running, start them:
   ```bash
   docker compose up -d ai-advisor research-core marketplace-service
   ```

### Long-term Actions

1. **Service Discovery:** Ensure all services are properly registered
2. **Health Checks:** Review and fix failing health checks
3. **Database Connections:** Standardize on async or sync drivers across services
4. **Monitoring:** Set up alerts for restarting/unhealthy containers

---

## Service Health Summary

| Service        | Status | Health     | Notes                           |
| -------------- | ------ | ---------- | ------------------------------- |
| Infrastructure | ✅     | Healthy    | All core infra services running |
| Most Services  | ✅     | Healthy    | 40+ services operational        |
| billing-core   | ⚠️     | Unhealthy  | Async driver issue              |
| chat-service   | 🔄     | Restarting | Database connection             |
| ai-advisor     | 🔄     | Restarting | DNS resolution                  |
| marketplace    | 🔄     | Restarting | Database connection             |
| research-core  | 🔄     | Restarting | Database connection             |

---

## Next Steps

1. Review detailed logs for each unhealthy/restarting service
2. Apply fixes for identified issues
3. Restart affected services
4. Monitor for stability
5. Update health check configurations if needed
