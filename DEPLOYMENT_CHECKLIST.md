# SAHOOL Platform v16.0.0 - Deployment Checklist

**Platform**: SAHOOL Unified Platform
**Version**: v16.0.0
**Services**: 50+ microservices
**Infrastructure**: PostgreSQL, Redis, NATS, MQTT, Qdrant, Kong, etcd
**Last Updated**: January 6, 2026

---

## Table of Contents

1. [Pre-Deployment Steps](#pre-deployment-steps)
2. [Database Migrations](#database-migrations)
3. [Infrastructure Startup Order](#infrastructure-startup-order)
4. [Service Startup Order](#service-startup-order)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Health Checks & Monitoring](#health-checks--monitoring)
7. [Rollback Procedures](#rollback-procedures)
8. [Emergency Response](#emergency-response)

---

## Pre-Deployment Steps

### 1. Pre-Deployment Environment Verification

- [ ] **Verify Git State**
  - [ ] All changes committed: `git status` (should be clean)
  - [ ] Pull latest from main: `git pull origin main`
  - [ ] Verify current branch is for deployment: `git branch`
  - [ ] Tag the release: `git tag -a v16.0.0 -m "Production deployment"`
  - [ ] Push tags: `git push origin --tags`

- [ ] **Verify Deployment Environment**
  - [ ] Confirm target environment (development/staging/production)
  - [ ] Verify environment is accessible and responsive
  - [ ] Check system resources available:
    - [ ] Disk space: min 50GB free
    - [ ] CPU cores: min 8 cores recommended
    - [ ] RAM: min 16GB available
  - [ ] Verify Docker daemon is running: `docker ps`
  - [ ] Verify Docker Compose version: `docker-compose --version` (min v1.29)

- [ ] **Network & Connectivity**
  - [ ] Verify DNS resolution is working
  - [ ] Check firewall rules for required ports:
    - [ ] PostgreSQL: 5432
    - [ ] PgBouncer: 6432
    - [ ] Redis: 6379
    - [ ] NATS: 4222, 8222
    - [ ] MQTT: 1883, 9001
    - [ ] Kong: 8000, 8001, 8443, 8444
    - [ ] Qdrant: 6333, 6334
    - [ ] Services: 8100-8150 range
  - [ ] Verify external API connectivity (weather, satellite data providers)
  - [ ] Confirm TLS certificates are valid (if applicable)

### 2. Credentials & Secrets Management

- [ ] **Environment Configuration**
  - [ ] Copy and customize `.env` file: `cp .env.example .env`
  - [ ] Verify all required variables are set (no defaults):
    - [ ] `POSTGRES_PASSWORD` - Generate with: `openssl rand -base64 32`
    - [ ] `POSTGRES_USER` - Set to `sahool`
    - [ ] `POSTGRES_DB` - Set to `sahool`
    - [ ] `REDIS_PASSWORD` - Generate with: `openssl rand -base64 32`
    - [ ] `NATS_USER` - Set user account
    - [ ] `NATS_PASSWORD` - Generate with: `openssl rand -base64 32`
    - [ ] `NATS_ADMIN_PASSWORD` - Generate with: `openssl rand -base64 32`
    - [ ] `JWT_SECRET_KEY` - Generate with: `openssl rand -base64 48`
    - [ ] `MQTT_USER` - Set to `sahool_iot`
    - [ ] `MQTT_PASSWORD` - Generate with: `openssl rand -base64 32`
    - [ ] `QDRANT_API_KEY` - Generate with: `openssl rand -base64 32`

- [ ] **Credentials Validation**
  - [ ] Run secret validation: `./scripts/security/check-secrets.sh`
  - [ ] Verify no credentials in git history
  - [ ] Rotate credentials if they're older than 90 days
  - [ ] Back up `.env` file in secure location
  - [ ] Verify `.env` file is not tracked in git

- [ ] **TLS/SSL Certificates (if applicable)**
  - [ ] Generate certificates: `./scripts/security/generate-certs.sh`
  - [ ] Verify certificate validity dates
  - [ ] Copy certificates to `/infrastructure/gateway/kong/certs/`
  - [ ] Set permissions: `chmod 600 *.key`
  - [ ] Verify Kong TLS configuration in `docker-compose.yml`

### 3. Backup & Recovery Preparation

- [ ] **Create Pre-Deployment Backup**
  - [ ] If upgrading existing deployment:
    - [ ] Full database backup: `./scripts/backup_database.sh -t manual -m full`
    - [ ] Backup verification: Verify backup file size > 10MB
    - [ ] Store backup in 2 locations (local + cloud/external)
    - [ ] Test backup restoration (dry run): `pg_restore --list backup_file.dump | head -20`
    - [ ] Record backup location and timestamp

- [ ] **Document Pre-Deployment State**
  - [ ] Export current service configurations
  - [ ] Record active connections count: `docker-compose ps | wc -l`
  - [ ] Document current resource usage: `docker stats --no-stream`
  - [ ] Capture database schema version
  - [ ] Note any active deployments or migrations in progress

- [ ] **Communication Plan**
  - [ ] Notify stakeholders of deployment window
  - [ ] Schedule maintenance window (if needed)
  - [ ] Post maintenance notification in team channels
  - [ ] Prepare rollback communication template

### 4. Code & Configuration Review

- [ ] **Code Quality Checks**
  - [ ] Run linter: `npm run lint`
  - [ ] Run tests: `npm run test`
  - [ ] Run security scan: `npm run security`
  - [ ] Verify TypeScript compilation: `npm run build`
  - [ ] Check API documentation is current

- [ ] **Configuration Validation**
  - [ ] Validate docker-compose syntax: `docker-compose config > /dev/null`
  - [ ] Verify all service images are specified with versions (no `latest`)
  - [ ] Check Kong configuration: `./scripts/validate-kong-config.sh`
  - [ ] Validate NATS configuration in `config/nats/nats.conf`
  - [ ] Verify Redis security config: `./scripts/validate-redis-security.sh`
  - [ ] Check environment variable usage in services

- [ ] **Dependency & Image Verification**
  - [ ] Pull all container images: `docker-compose pull`
  - [ ] Verify image checksums match
  - [ ] Scan images for vulnerabilities
  - [ ] Check image disk space requirements
  - [ ] Verify all images are from trusted registries

---

## Database Migrations

### 1. Pre-Migration Checks

- [ ] **Database Accessibility**
  - [ ] PostgreSQL service is running: `docker-compose up -d postgres`
  - [ ] Wait for PostgreSQL to be healthy (30s startup period)
  - [ ] Test connection: `docker exec sahool-postgres pg_isready -U sahool`
  - [ ] Verify database exists: `docker exec sahool-postgres psql -U sahool -l | grep sahool`
  - [ ] Check database size: `docker exec sahool-postgres psql -U sahool -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) FROM pg_database WHERE datname = 'sahool';"`

- [ ] **PgBouncer Verification** (for production)
  - [ ] PgBouncer is running: `docker-compose ps pgbouncer`
  - [ ] PgBouncer health check: `docker exec sahool-pgbouncer pg_isready -h localhost -p 6432`
  - [ ] Test pooled connection: `docker exec sahool-pgbouncer psql -h localhost -p 6432 -U sahool -c "SELECT 1;"`
  - [ ] Check connection pool stats: `docker exec sahool-pgbouncer psql -h localhost -p 6432 -U pgbouncer_admin -c "SHOW STATS;"`

- [ ] **Migration Lock Status**
  - [ ] Check for existing migration locks: `docker exec sahool-postgres psql -U sahool -c "SELECT * FROM pg_locks WHERE locktype='advisory';"`
  - [ ] Kill any hung migration processes if needed
  - [ ] Document any concurrent operations that should complete first

### 2. Execute Migrations

- [ ] **Run Database Migrations**
  - [ ] Navigate to project root: `cd /home/user/sahool-unified-v15-idp`
  - [ ] List pending migrations: `docker-compose exec postgres psql -U sahool -c "\dt information_schema.tables" | grep -i migration`
  - [ ] **Alert Service Migration** (if applicable)
    - [ ] Apply migration: `docker-compose exec postgres psql -U sahool sahool < database/migrations/011_migrate_passwords_to_argon2.sql`
    - [ ] Verify migration: `docker exec sahool-postgres psql -U sahool -c "SELECT COUNT(*) as password_migration_tracking FROM information_schema.columns WHERE table_name='users' AND column_name='password_needs_migration';"`
    - [ ] Check migration stats: `docker exec sahool-postgres psql -U sahool -c "SELECT * FROM password_migration_stats;"`

  - [ ] **Execute Pending Migrations** (for services using Alembic)
    - For each affected service (if applicable):
      ```bash
      docker-compose up -d <service-name>
      docker-compose exec <service-name> alembic upgrade head
      docker-compose logs <service-name> | grep -i migration
      ```

  - [ ] **Seed Database** (initial deployment only)
    - [ ] If fresh deployment, load seed data:
      ```bash
      docker-compose exec postgres psql -U sahool sahool < database/seeds/01_users.sql
      docker-compose exec postgres psql -U sahool sahool < database/seeds/02_farms.sql
      docker-compose exec postgres psql -U sahool sahool < database/seeds/03_fields.sql
      # ... continue for other seeds
      ```

### 3. Migration Verification

- [ ] **Validate Migration Success**
  - [ ] Check for migration errors in logs: `docker-compose logs postgres | grep -i error`
  - [ ] Verify schema changes applied:
    ```bash
    docker exec sahool-postgres psql -U sahool -c "
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;"
    ```
  - [ ] Record table counts: `docker exec sahool-postgres psql -U sahool -c "SELECT tablename, pg_size_pretty(pg_total_relation_size('\"'||tablename||'\"')) FROM pg_tables WHERE schemaname='public';"`
  - [ ] Check for constraint violations: `docker exec sahool-postgres psql -U sahool -c "SELECT * FROM pg_constraint;"`
  - [ ] Verify indexes are created: `docker exec sahool-postgres psql -U sahool -c "SELECT * FROM pg_indexes WHERE schemaname='public';"`

- [ ] **Data Integrity Checks**
  - [ ] Run validation script: `./scripts/data_integrity_checker.py`
  - [ ] Check for orphaned records
  - [ ] Verify referential integrity (all foreign keys valid)
  - [ ] Validate password algorithm migrations (if applicable):
    ```bash
    docker exec sahool-postgres psql -U sahool -c "
    SELECT password_algorithm, COUNT(*) as count
    FROM users
    WHERE password_hash IS NOT NULL
    GROUP BY password_algorithm;"
    ```

- [ ] **Performance Checks**
  - [ ] Query a large table to verify performance: `docker exec sahool-postgres psql -U sahool -c "EXPLAIN ANALYZE SELECT * FROM users LIMIT 1000;"`
  - [ ] Check slow query log (if enabled)
  - [ ] Verify index statistics are up to date: `docker exec sahool-postgres psql -U sahool -c "ANALYZE;"`

---

## Infrastructure Startup Order

> **Critical**: Services must start in dependency order. Do NOT start all services simultaneously.

### Phase 1: Core Infrastructure (Sequential Start - 60-120s)

Start these services one at a time, waiting for health checks:

1. [ ] **PostgreSQL** (Port 5432)
   ```bash
   docker-compose up -d postgres
   sleep 30  # Wait for startup
   docker-compose exec postgres pg_isready -U sahool
   # Verify: "accepting connections"
   ```

2. [ ] **Redis** (Port 6379)
   ```bash
   docker-compose up -d redis
   sleep 15
   docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" ping
   # Verify: "PONG"
   ```

3. [ ] **PgBouncer** (Port 6432) - for production only
   ```bash
   docker-compose up -d pgbouncer
   sleep 15
   docker-compose exec pgbouncer pg_isready -h localhost -p 6432 -U sahool
   # Verify: "accepting connections"
   ```

4. [ ] **NATS JetStream** (Ports 4222, 8222)
   ```bash
   docker-compose up -d nats
   sleep 15
   curl http://localhost:8222/healthz
   # Verify: HTTP 200 response
   ```

5. [ ] **MQTT Broker** (Ports 1883, 9001)
   ```bash
   docker-compose up -d mqtt
   sleep 10
   docker-compose exec mqtt pidof mosquitto
   # Verify: Process ID returned
   ```

6. [ ] **Qdrant Vector DB** (Ports 6333, 6334)
   ```bash
   docker-compose up -d qdrant
   sleep 20
   curl -s http://localhost:6333/health | jq .
   # Verify: "status":"ok"
   ```

7. [ ] **etcd** (Ports 2379, 2380)
   ```bash
   docker-compose up -d etcd
   sleep 15
   docker-compose exec etcd etcdctl endpoint health
   # Verify: "healthy: true"
   ```

8. [ ] **Minio** (Ports 9000, 9001)
   ```bash
   docker-compose up -d minio
   sleep 15
   curl -s http://localhost:9000/minio/health/live
   # Verify: HTTP 200
   ```

9. [ ] **Milvus** (Ports 19530, 9091)
   ```bash
   docker-compose up -d milvus
   sleep 30
   docker-compose logs milvus | grep -i "healthy"
   # Verify: Health status OK
   ```

10. [ ] **Ollama** (Port 11434)
    ```bash
    docker-compose up -d ollama
    sleep 20
    curl -s http://localhost:11434/api/tags
    # Verify: JSON response with model list
    ```

11. [ ] **Ollama Model Loader** (initialization service)
    ```bash
    docker-compose up -d ollama-model-loader
    sleep 60
    docker-compose logs ollama-model-loader | tail -5
    # Verify: Model loading complete
    ```

### Phase 2: API Gateway & Routing (30-45s)

12. [ ] **Kong API Gateway** (Ports 8000, 8001, 8443, 8444)
    ```bash
    docker-compose up -d kong
    sleep 20
    curl -s http://localhost:8001/
    # Verify: Kong Admin API response (JSON object)
    docker-compose exec kong kong health
    # Verify: Health status
    ```

13. [ ] **Provider Config Service** (bootstrap Kong routes)
    ```bash
    docker-compose up -d provider-config
    sleep 15
    docker-compose logs provider-config | grep -i "route\|plugin\|configured"
    # Verify: Configuration applied successfully
    ```

### Phase 3: Core Platform Services (Parallel Start, 30-60s)

Start these services in parallel (Docker handles dependencies):

```bash
docker-compose up -d \
  field-management-service \
  marketplace-service \
  research-core \
  field-ops \
  weather-service \
  advisory-service \
  weather-core
```

Then verify each:
- [ ] field-management-service (8100): `curl http://localhost:8100/healthz`
- [ ] marketplace-service (8101): `curl http://localhost:8101/healthz`
- [ ] research-core (8102): `curl http://localhost:8102/healthz`
- [ ] field-ops (8103): `curl http://localhost:8103/healthz`
- [ ] weather-service (8104): `curl http://localhost:8104/healthz`
- [ ] advisory-service (8105): `curl http://localhost:8105/healthz`
- [ ] weather-core (8106): `curl http://localhost:8106/healthz`

### Phase 4: Intelligence & Analysis Services (Parallel Start, 45-90s)

```bash
docker-compose up -d \
  yield-prediction \
  lai-estimation \
  crop-growth-model \
  vegetation-analysis-service \
  crop-intelligence-service \
  ndvi-engine \
  disaster-assessment \
  indicators-service
```

Health verification for each service (port numbers 8107-8114)

### Phase 5: Communication & IoT Services (Parallel Start, 30-60s)

```bash
docker-compose up -d \
  chat-service \
  iot-service \
  community-chat \
  notification-service \
  ws-gateway \
  iot-gateway \
  field-chat
```

### Phase 6: Business & Support Services (Parallel Start, 30-60s)

```bash
docker-compose up -d \
  billing-core \
  equipment-service \
  field-intelligence \
  task-service \
  inventory-service \
  virtual-sensors \
  irrigation-smart
```

### Phase 7: AI & Advisory Services (Parallel Start, 30-60s)

```bash
docker-compose up -d \
  ai-advisor \
  agro-advisor \
  alert-service \
  crop-health \
  crop-health-ai \
  astronomical-calendar \
  yield-prediction-service
```

### Phase 8: Monitoring & Code Quality (Sequential Start, 15-30s)

```bash
docker-compose up -d code-review-service
sleep 10
docker-compose up -d agent-registry
sleep 10
docker-compose up -d field-service
```

### Phase 9: Demo & Testing Services (Optional, 15-30s)

```bash
docker-compose up -d demo-data
sleep 10
# Verify demo data population
curl http://localhost:8150/api/demo/status
```

---

## Post-Deployment Verification

### 1. Infrastructure Health Checks

- [ ] **All Services Running**
  ```bash
  docker-compose ps
  # Verify: All services show "Up" status, 0 errors
  ```

- [ ] **Container Health Status**
  ```bash
  docker-compose ps --services | while read service; do
    echo "Checking $service..."
    docker-compose exec $service /bin/sh -c 'true' 2>/dev/null && echo "✓" || echo "✗"
  done
  ```

- [ ] **Database Connectivity**
  - [ ] Direct connection: `docker-compose exec postgres pg_isready -U sahool`
  - [ ] Pooled connection: `docker-compose exec pgbouncer pg_isready -h localhost -p 6432`
  - [ ] Test query: `docker exec sahool-postgres psql -U sahool -c "SELECT version();"`

- [ ] **Message Queue Status**
  - [ ] NATS: `curl http://localhost:8222/healthz`
  - [ ] MQTT: `docker-compose exec mqtt mosquitto_sub -h mqtt -t '$SYS/#' -c 1`
  - [ ] Test publish: `docker-compose exec mqtt mosquitto_pub -h mqtt -t 'test' -m 'test_message'`

- [ ] **Cache Status**
  - [ ] Redis: `docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" INFO server | head -10`
  - [ ] Memory usage: `docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" INFO memory`
  - [ ] Connected clients: `docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" CLIENT LIST | wc -l`

### 2. API Gateway Validation

- [ ] **Kong Status**
  ```bash
  curl http://localhost:8001/status
  # Verify: database=connected, server=online
  ```

- [ ] **Routes Configured**
  ```bash
  curl http://localhost:8001/routes | jq '.data | length'
  # Verify: >10 routes configured
  ```

- [ ] **Plugins Active**
  ```bash
  curl http://localhost:8001/plugins | jq '.data | length'
  # Verify: rate-limiting, jwt, cors plugins active
  ```

### 3. Service Health Endpoint Verification

Test core services (sampling approach):

```bash
SERVICES=(
  "http://localhost:8100/healthz"  # field-management
  "http://localhost:8101/healthz"  # marketplace
  "http://localhost:8102/healthz"  # research-core
  "http://localhost:8103/healthz"  # field-ops
  "http://localhost:8104/healthz"  # weather
)

for service in "${SERVICES[@]}"; do
  echo "Testing $service"
  curl -f "$service" && echo "✓" || echo "✗"
done
```

- [ ] Record healthy service count: `__________ / 50+ services`
- [ ] Identify any unhealthy services for troubleshooting

### 4. Database Verification

- [ ] **Schema Integrity**
  - [ ] Check table count: `docker exec sahool-postgres psql -U sahool -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"`
  - [ ] Verify critical tables exist:
    ```bash
    docker exec sahool-postgres psql -U sahool -c "
    SELECT tablename FROM pg_tables
    WHERE schemaname='public' AND tablename IN
    ('users', 'farms', 'fields', 'crops', 'alerts', 'weather_data');
    "
    ```

- [ ] **Data Validation**
  - [ ] User count: `docker exec sahool-postgres psql -U sahool -c "SELECT COUNT(*) FROM users;"`
  - [ ] Farm count: `docker exec sahool-postgres psql -U sahool -c "SELECT COUNT(*) FROM farms;"`
  - [ ] Field count: `docker exec sahool-postgres psql -U sahool -c "SELECT COUNT(*) FROM fields;"`

### 5. Performance Baseline

- [ ] **Connection Pool Status**
  - [ ] PgBouncer: `docker exec sahool-pgbouncer psql -h localhost -p 6432 -U pgbouncer_admin -c "SHOW POOLS;"`
  - [ ] Current connections: Check should show < MAX_CLIENT_CONN (500)
  - [ ] Active size: Check that DEFAULT_POOL_SIZE (20) is reasonable

- [ ] **Resource Utilization**
  ```bash
  docker stats --no-stream | tail -20
  # Record CPU and memory for each service
  ```

- [ ] **Query Performance** (baseline)
  - [ ] Sample slow query from application logs
  - [ ] EXPLAIN ANALYZE: `docker exec sahool-postgres psql -U sahool -c "EXPLAIN ANALYZE SELECT * FROM users LIMIT 100;"`

---

## Health Checks & Monitoring

### 1. Readiness Probe Verification

These services must respond with HTTP 200 to `/readyz` endpoint:

- [ ] **Core Services**
  - [ ] field-management-service: `curl http://localhost:8100/readyz`
  - [ ] marketplace-service: `curl http://localhost:8101/readyz`
  - [ ] alert-service: `curl http://localhost:8113/readyz`

- [ ] **Verify all readiness probes pass**
  ```bash
  ./scripts/test-api-connectivity.sh
  # Should show all endpoints responding
  ```

### 2. Liveness Probe Verification

- [ ] **Docker health checks active**
  ```bash
  docker-compose ps | grep -E "healthy|unhealthy"
  # All should show "healthy"
  ```

### 3. Continuous Health Monitoring

- [ ] **Set up monitoring script** (if using K8s monitoring)
  - [ ] Deploy Prometheus for metrics collection
  - [ ] Configure Grafana dashboards
  - [ ] Set up alert rules: `/monitoring/alerts/rollout-alerts.yaml`

- [ ] **Application Monitoring**
  - [ ] Check telemetry collection: `curl http://localhost:4317/api/traces` (Jaeger/OTEL)
  - [ ] Verify logs are being collected
  - [ ] Confirm metrics are exported

### 4. Log Aggregation Verification

- [ ] **Check Service Logs**
  ```bash
  docker-compose logs --tail=100 | grep -i "error\|warn"
  # Should be minimal warnings, no errors
  ```

- [ ] **Database Logs**
  ```bash
  docker-compose logs postgres | grep -i "error"
  # Should be none for a healthy deployment
  ```

---

## Rollback Procedures

### Emergency Rollback (< 5 minutes to decision)

Use this if critical issues detected within first 5 minutes:

#### Option 1: Container Rollback (Fastest)

```bash
# Step 1: Identify problematic service
docker-compose logs <service-name> | tail -50

# Step 2: Revert to previous image version
# Edit docker-compose.yml to use previous image tag
# Example: change 'field-management-service:v16.0.0' to 'field-management-service:v15.9.0'

# Step 3: Restart service
docker-compose pull <service-name>
docker-compose up -d <service-name>

# Step 4: Verify recovery
curl http://localhost:8100/healthz
```

#### Option 2: Database Rollback (for schema issues)

```bash
# Step 1: Stop all services
docker-compose stop

# Step 2: Restore from backup
docker exec sahool-postgres pg_restore -U sahool -d sahool -c backup_file.dump

# Step 3: Restart
docker-compose up -d postgres
docker-compose up -d --no-deps <affected-services>
```

#### Option 3: Full Rollback

```bash
# Step 1: Stop all services
docker-compose down

# Step 2: Restore database
docker-compose up -d postgres
docker exec sahool-postgres pg_restore -U sahool -d sahool -c backup_file_before_deployment.dump

# Step 3: Restore previous code
git revert HEAD --no-edit
git push origin main

# Step 4: Deploy previous version
docker-compose pull
docker-compose up -d

# Step 5: Verify all services healthy
./scripts/test-api-connectivity.sh
```

### Rollback Verification Checklist

After rollback, verify:

- [ ] All services responding to health checks
- [ ] Database restored to correct state
- [ ] No data loss in critical tables
- [ ] Previous API contracts working
- [ ] WebSocket connections working (chat, notifications)
- [ ] File uploads/downloads functional
- [ ] External integrations (weather API, satellite data) working

### Post-Rollback Communication

- [ ] Notify stakeholders of rollback
- [ ] Document root cause analysis
- [ ] Create incident report
- [ ] Schedule post-mortem
- [ ] Update deployment procedures based on findings

---

## Emergency Response

### Critical Issues During Deployment

#### Issue: PostgreSQL Won't Start

```bash
# Check logs
docker-compose logs postgres

# If corrupted: reset and restore from backup
docker volume rm sahool_postgres_data
docker-compose up -d postgres
docker exec sahool-postgres pg_restore -U sahool -d sahool backup_file.dump
```

#### Issue: High Connection Failures

```bash
# Check PgBouncer pool
docker exec sahool-pgbouncer psql -h localhost -p 6432 -U pgbouncer_admin -c "SHOW CLIENTS;"

# Restart PgBouncer if stuck
docker-compose restart pgbouncer
sleep 10
docker-compose exec pgbouncer pg_isready
```

#### Issue: Memory Exhaustion

```bash
# Check resource usage
docker stats

# Identify memory hog
docker-compose exec <service> /bin/sh -c 'ps aux | sort -nrk 3,3 | head -10'

# Restart affected service
docker-compose restart <service>
```

#### Issue: NATS/MQTT Not Accepting Messages

```bash
# Check NATS status
curl http://localhost:8222/connz
curl http://localhost:8222/jsz

# Reset NATS (WARNING: loses in-memory state)
docker-compose down nats
docker volume rm sahool_nats_data  # Only if necessary
docker-compose up -d nats
```

### Rollback Decision Tree

```
Issue Detected?
│
├─ YES
│   ├─ Database corruption?
│   │  └─ RESTORE_BACKUP → Restart services
│   │
│   ├─ Service(s) crashing?
│   │  └─ Revert image version → Restart service
│   │
│   ├─ API/Contract incompatibility?
│   │  └─ Revert code: git revert HEAD → Full restart
│   │
│   ├─ Memory/Resource exhaustion?
│   │  └─ Scale down → Investigate → Revert if needed
│   │
│   └─ Configuration error?
│      └─ Fix config → Restart affected services
│
└─ NO
   └─ Continue monitoring
```

---

## Monitoring Checklist (First 24 Hours)

- [ ] **Hourly Checks**
  - [ ] All services still showing healthy status
  - [ ] No critical errors in logs
  - [ ] Response times normal (no degradation)
  - [ ] Database query performance acceptable
  - [ ] Memory/CPU usage stable

- [ ] **Every 4 Hours**
  - [ ] Run full health suite: `./scripts/test-api-connectivity.sh`
  - [ ] Check database integrity: `./scripts/data_integrity_checker.py`
  - [ ] Verify backup completed successfully
  - [ ] Review slow query log

- [ ] **At 24 Hours**
  - [ ] Run performance tests: `./tests/load/docker-compose-sim.yml`
  - [ ] Verify all background jobs executed
  - [ ] Check external API integrations
  - [ ] Confirm no data anomalies

---

## Sign-Off & Documentation

### Deployment Sign-Off

- [ ] Deployment completed successfully
- [ ] All checklist items completed
- [ ] Post-deployment monitoring verified
- [ ] Rollback procedures tested and ready
- [ ] Stakeholders notified of completion
- [ ] Incident log updated

### Documentation Updates

- [ ] Update deployment notes with any issues encountered
- [ ] Record actual timing for each phase
- [ ] Document any environment-specific configurations
- [ ] Update runbooks based on this deployment
- [ ] Archive backup location and credentials securely

---

**Deployment Status**: _______________
**Date Deployed**: ________________
**Deployed By**: ________________
**Approved By**: ________________
**Rollback Executed**: Yes / No
**Issues Encountered**: ______________
**Notes**: ______________________________________________

---

## Quick Reference Commands

```bash
# Start full deployment (careful - sequential is recommended)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f <service-name>

# Stop everything
docker-compose stop

# Stop and remove
docker-compose down

# Remove all data (DESTRUCTIVE)
docker-compose down -v

# Backup database
./scripts/backup_database.sh -t manual -m full

# Database restore
pg_restore -U sahool -d sahool -v -c backup_file.dump

# Rollback script
./scripts/rollback.sh -e production -a --dry-run

# Health check
./scripts/test-api-connectivity.sh

# Validate deployment
./scripts/validate-build.sh

# Check Redis security
./scripts/validate-redis-security.sh

# Database health check
./scripts/db_health_check.sh

# NATS info
curl http://localhost:8222/connz | jq

# Kong status
curl http://localhost:8001/status

# Service count
docker-compose ps --services | wc -l
```

---

**Last Updated**: January 6, 2026
**Version**: 1.0
**Maintained By**: SAHOOL Platform Team
