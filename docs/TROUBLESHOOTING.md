# SAHOOL Troubleshooting Guide

# دليل استكشاف الأخطاء وإصلاحها

This guide covers common issues and their solutions for the SAHOOL platform.

يغطي هذا الدليل المشكلات الشائعة وحلولها لمنصة سهول.

---

## Table of Contents | جدول المحتويات

1. [Quick Diagnostics](#quick-diagnostics--التشخيص-السريع)
2. [Development Environment](#development-environment--بيئة-التطوير)
3. [Docker & Containers](#docker--containers--docker-والحاويات)
4. [Database Issues](#database-issues--مشاكل-قاعدة-البيانات)
5. [Service Issues](#service-issues--مشاكل-الخدمات)
6. [Authentication & Security](#authentication--security--المصادقة-والأمان)
7. [API Gateway (Kong)](#api-gateway-kong--بوابة-api)
8. [Message Queue (NATS)](#message-queue-nats--قائمة-الرسائل)
9. [Mobile App](#mobile-app--تطبيق-الجوال)
10. [Web Dashboard](#web-dashboard--لوحة-المعلومات)
11. [Performance Issues](#performance-issues--مشاكل-الأداء)
12. [CI/CD Pipeline](#cicd-pipeline--خط-التكامل-المستمر)

---

## Quick Diagnostics | التشخيص السريع

### Health Check Commands | أوامر فحص الصحة

```bash
# Check all services status
make status

# View service health
make health

# Check specific service logs
make logs-service SERVICE=field-management-service

# Quick connectivity test
curl http://localhost:8000/healthz  # Kong
curl http://localhost:5432          # PostgreSQL (connection test)
curl http://localhost:6379          # Redis
curl http://localhost:4222          # NATS
```

### System Requirements Check | فحص متطلبات النظام

```bash
# Docker version (requires 24+)
docker --version

# Docker Compose version (requires v2+)
docker compose version

# Available disk space (need at least 10GB free)
df -h

# Available memory (recommend 8GB+)
free -h

# Check port availability
sudo lsof -i :8000  # Kong
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis
```

---

## Development Environment | بيئة التطوير

### Issue: `make dev` fails to start

**Symptoms:**
- Services fail to start
- Port conflicts
- Environment errors

**Solutions:**

1. **Check for port conflicts:**
```bash
# Find processes using required ports
sudo lsof -i :8000 -i :5432 -i :6379 -i :4222

# Kill conflicting processes if needed
sudo kill -9 <PID>
```

2. **Reset the environment:**
```bash
make down-volumes  # Stop and remove volumes
make clean         # Clean build artifacts
make dev           # Restart
```

3. **Check environment file:**
```bash
# Ensure .env exists
cp .env.example .env

# Verify required variables
cat .env | grep -E "^(DATABASE_URL|JWT_SECRET|NATS_URL)"
```

---

### Issue: Python dependencies fail to install

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement
```

**Solutions:**

1. **Use virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

2. **Upgrade pip:**
```bash
pip install --upgrade pip setuptools wheel
```

3. **Check Python version (requires 3.11+):**
```bash
python --version
```

---

### Issue: Node.js packages fail to install

**Symptoms:**
```
npm ERR! ERESOLVE unable to resolve dependency tree
```

**Solutions:**

1. **Clean install:**
```bash
rm -rf node_modules package-lock.json
npm install
```

2. **Use legacy peer deps:**
```bash
npm install --legacy-peer-deps
```

3. **Check Node version (requires 18+):**
```bash
node --version
```

---

## Docker & Containers | Docker والحاويات

### Issue: Container fails to start

**Symptoms:**
- Container exits immediately
- "Error response from daemon"

**Diagnosis:**
```bash
# View container logs
docker logs <container_name>

# View detailed container info
docker inspect <container_name>

# Check container status
docker ps -a
```

**Solutions:**

1. **Memory issues:**
```bash
# Check Docker memory limit
docker system info | grep Memory

# Increase Docker memory (Docker Desktop settings)
# Recommend: 8GB minimum
```

2. **Image build issues:**
```bash
# Rebuild without cache
docker compose build --no-cache <service_name>
```

3. **Volume permission issues:**
```bash
# Fix permissions
sudo chown -R $USER:$USER ./data
```

---

### Issue: "No space left on device"

**Symptoms:**
```
ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device
```

**Solutions:**

1. **Clean Docker resources:**
```bash
# Remove unused images, containers, networks
docker system prune -a

# Remove unused volumes (WARNING: deletes data)
docker volume prune

# Check disk usage
docker system df
```

2. **Clean build caches:**
```bash
# Clear pip cache
pip cache purge

# Clear npm cache
npm cache clean --force
```

---

### Issue: Container networking problems

**Symptoms:**
- Services cannot communicate
- "Connection refused" errors

**Solutions:**

1. **Check network:**
```bash
# List Docker networks
docker network ls

# Inspect network
docker network inspect sahool-network
```

2. **Recreate network:**
```bash
docker compose down
docker network rm sahool-network
docker compose up -d
```

3. **Check service names:**
```bash
# Services should use Docker service names, not localhost
# Example: postgres:5432, not localhost:5432
```

---

## Database Issues | مشاكل قاعدة البيانات

### Issue: Cannot connect to PostgreSQL

**Symptoms:**
```
FATAL: password authentication failed
connection refused
```

**Solutions:**

1. **Check database is running:**
```bash
docker ps | grep postgres
make db-shell  # Try to connect
```

2. **Verify credentials:**
```bash
# Check environment variables
echo $DATABASE_URL
echo $POSTGRES_PASSWORD

# Test connection
psql "$DATABASE_URL"
```

3. **Reset database (development only):**
```bash
make db-reset  # WARNING: Deletes all data
```

---

### Issue: Migration failures

**Symptoms:**
```
Error: Migration failed
relation already exists
```

**Solutions:**

1. **Check migration status:**
```bash
# For Prisma
npx prisma migrate status

# For Alembic (Python)
alembic current
```

2. **Reset migrations (development only):**
```bash
# Prisma
npx prisma migrate reset

# Alembic
alembic downgrade base
alembic upgrade head
```

3. **Fix duplicate migrations:**
```bash
# Check for conflicting migration files
ls -la apps/services/*/prisma/migrations/
```

---

### Issue: PostGIS extension not available

**Symptoms:**
```
ERROR: type "geometry" does not exist
```

**Solutions:**

1. **Enable PostGIS:**
```sql
-- In psql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

2. **Verify extension:**
```sql
SELECT PostGIS_Version();
```

---

### Issue: Slow database queries

**Symptoms:**
- API responses slow
- Timeout errors

**Solutions:**

1. **Check query performance:**
```sql
-- Enable query logging
SET log_min_duration_statement = '100ms';

-- Analyze slow query
EXPLAIN ANALYZE <your_query>;
```

2. **Add missing indexes:**
```sql
-- Check existing indexes
\di

-- Create index for frequently queried columns
CREATE INDEX idx_fields_tenant ON fields(tenant_id);
```

3. **Check connection pool:**
```bash
# View active connections
SELECT count(*) FROM pg_stat_activity;
```

---

## Service Issues | مشاكل الخدمات

### Issue: Service returns 500 Internal Server Error

**Diagnosis:**
```bash
# Check service logs
docker logs <service_container> --tail 100

# Check if dependencies are healthy
curl http://localhost:5432  # Database
curl http://localhost:6379  # Redis
curl http://localhost:4222  # NATS
```

**Common Causes:**

1. **Database connection failure:**
```bash
# Check DATABASE_URL is correct
# Verify database is accessible
```

2. **Missing environment variables:**
```bash
# Check required variables
docker exec <container> env | grep -E "(DATABASE|JWT|NATS)"
```

3. **Import errors:**
```bash
# Check for Python import errors in logs
docker logs <service> 2>&1 | grep "ImportError\|ModuleNotFoundError"
```

---

### Issue: Service health check failing

**Symptoms:**
- `/healthz` returns non-200
- Service marked unhealthy

**Solutions:**

1. **Check health endpoint:**
```bash
curl -v http://localhost:<port>/healthz
curl -v http://localhost:<port>/readyz
```

2. **Check dependent services:**
```bash
# If readiness fails, check dependencies
curl http://localhost:5432  # Database
curl http://localhost:6379  # Redis
```

3. **View detailed health:**
```bash
curl http://localhost:<port>/health | jq
```

---

### Issue: Service not receiving events

**Symptoms:**
- NATS messages not processed
- Events lost

**Solutions:**

1. **Check NATS connection:**
```bash
# Check NATS is running
curl http://localhost:8222/varz

# Check subscriptions
nats sub "sahool.>" --count 5
```

2. **Verify subscription patterns:**
```bash
# Check if service is subscribed
nats sub ls
```

3. **Check consumer status:**
```bash
nats consumer info <stream> <consumer>
```

---

## Authentication & Security | المصادقة والأمان

### Issue: JWT token invalid/expired

**Symptoms:**
```
401 Unauthorized
Token expired
Invalid signature
```

**Solutions:**

1. **Check token expiration:**
```bash
# Decode JWT (paste token)
echo "YOUR_TOKEN" | cut -d'.' -f2 | base64 -d | jq
```

2. **Verify JWT secret:**
```bash
# Ensure same secret across services
echo $JWT_SECRET_KEY
```

3. **Refresh token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

---

### Issue: CORS errors

**Symptoms:**
```
Access-Control-Allow-Origin missing
CORS policy blocked
```

**Solutions:**

1. **Check allowed origins:**
```bash
# Verify CORS configuration
grep -r "CORS\|allow_origins" apps/
```

2. **Add origin to whitelist:**
```python
# In FastAPI service
origins = [
    "http://localhost:3000",
    "https://app.sahool.com",
]
```

3. **Check Kong CORS plugin:**
```bash
curl http://localhost:8001/plugins | jq '.data[] | select(.name=="cors")'
```

---

### Issue: Rate limiting errors

**Symptoms:**
```
429 Too Many Requests
Rate limit exceeded
```

**Solutions:**

1. **Check rate limits:**
```bash
curl -I http://localhost:8000/api/v1/fields
# Look for X-RateLimit-* headers
```

2. **Increase limits (development):**
```yaml
# In Kong configuration
plugins:
  - name: rate-limiting
    config:
      minute: 1000
      hour: 10000
```

---

## API Gateway (Kong) | بوابة API

### Issue: Kong not routing requests

**Symptoms:**
```
502 Bad Gateway
Service unavailable
```

**Solutions:**

1. **Check Kong status:**
```bash
curl http://localhost:8001/status
```

2. **Verify service registration:**
```bash
curl http://localhost:8001/services | jq '.data[].name'
```

3. **Check routes:**
```bash
curl http://localhost:8001/routes | jq '.data[].paths'
```

4. **Test upstream:**
```bash
# Test service directly (bypass Kong)
curl http://localhost:8080/healthz
```

---

### Issue: Kong plugins not working

**Diagnosis:**
```bash
# List active plugins
curl http://localhost:8001/plugins | jq '.data[].name'

# Check plugin status
curl http://localhost:8001/plugins/<plugin_id>
```

**Solutions:**

1. **Reload Kong configuration:**
```bash
docker exec sahool-kong kong reload
```

2. **Check plugin logs:**
```bash
docker logs sahool-kong --tail 100 | grep "plugin"
```

---

## Message Queue (NATS) | قائمة الرسائل

### Issue: NATS connection refused

**Symptoms:**
```
Connection refused to nats://localhost:4222
```

**Solutions:**

1. **Check NATS status:**
```bash
curl http://localhost:8222/varz
docker ps | grep nats
```

2. **Verify NATS URL:**
```bash
# Should be nats://nats:4222 in Docker
echo $NATS_URL
```

---

### Issue: JetStream not enabled

**Symptoms:**
```
JetStream not enabled
```

**Solutions:**

1. **Enable JetStream:**
```bash
# In nats.conf
jetstream {
    store_dir: /data/jetstream
    max_mem: 1G
    max_file: 10G
}
```

2. **Restart NATS:**
```bash
docker restart sahool-nats
```

---

### Issue: Messages not being consumed

**Solutions:**

1. **Check consumer status:**
```bash
nats consumer info SAHOOL_STREAM <consumer_name>
```

2. **Check pending messages:**
```bash
nats stream info SAHOOL_STREAM
```

3. **Restart consumer:**
```bash
docker restart <service_consuming_messages>
```

---

## Mobile App | تطبيق الجوال

### Issue: Flutter build fails

**Symptoms:**
- Dart analysis errors
- Missing dependencies

**Solutions:**

1. **Clean and rebuild:**
```bash
cd apps/mobile/sahool_field_app
flutter clean
flutter pub get
dart run build_runner build --delete-conflicting-outputs
flutter build apk
```

2. **Update dependencies:**
```bash
flutter pub upgrade
```

---

### Issue: Drift database errors

**Symptoms:**
```
Error: Getter not found: 'TasksCompanion'
```

**Solutions:**

1. **Regenerate Drift code:**
```bash
dart run build_runner clean
dart run build_runner build --delete-conflicting-outputs
```

2. **Verify generated files:**
```bash
ls lib/core/storage/*.g.dart
```

---

### Issue: API connection fails from mobile

**Symptoms:**
- Network errors
- Certificate errors

**Solutions:**

1. **Check API URL:**
```dart
// Verify base URL in api_config.dart
const baseUrl = 'https://api.sahool.com';
```

2. **For local development:**
```bash
# Use device IP, not localhost
# Android emulator: 10.0.2.2
# iOS simulator: localhost
```

3. **Certificate issues:**
```dart
// Development only - bypass certificate validation
// DO NOT use in production
```

---

## Web Dashboard | لوحة المعلومات

### Issue: Web build fails

**Symptoms:**
- Module not found errors
- TypeScript errors

**Solutions:**

1. **Build shared packages first:**
```bash
npm run build:packages
```

2. **Clean and rebuild:**
```bash
cd apps/web
rm -rf .next node_modules
npm install
npm run build
```

---

### Issue: WebSocket connection fails

**Symptoms:**
- Real-time updates not working
- WebSocket errors in console

**Solutions:**

1. **Check WebSocket gateway:**
```bash
curl http://localhost:8081/healthz
```

2. **Verify WebSocket URL:**
```javascript
// Should use wss:// in production
const wsUrl = 'wss://api.sahool.com/ws';
```

---

## Performance Issues | مشاكل الأداء

### Issue: Slow API responses

**Diagnosis:**
```bash
# Check response times
curl -w "@curl-format.txt" http://localhost:8000/api/v1/fields
```

**Solutions:**

1. **Enable caching:**
```bash
# Check Redis connection
redis-cli ping
```

2. **Check database indexes:**
```sql
EXPLAIN ANALYZE SELECT * FROM fields WHERE tenant_id = 'xxx';
```

3. **Check connection pooling:**
```bash
# Verify PgBouncer is working
docker logs sahool-pgbouncer
```

---

### Issue: High memory usage

**Diagnosis:**
```bash
docker stats
```

**Solutions:**

1. **Limit container memory:**
```yaml
# In docker-compose.yml
services:
  field-ops:
    mem_limit: 512m
```

2. **Check for memory leaks:**
```bash
# Profile Python service
python -m memory_profiler script.py
```

---

## CI/CD Pipeline | خط التكامل المستمر

For CI/CD specific issues, see [CI_TROUBLESHOOTING.md](./CI_TROUBLESHOOTING.md).

---

## Getting More Help | الحصول على مساعدة إضافية

If these solutions don't resolve your issue:

1. **Check logs thoroughly:**
```bash
make logs | grep -i "error\|exception\|failed"
```

2. **Search documentation:**
```bash
grep -r "your_error_message" docs/
```

3. **Review related documentation:**
- [DEPLOYMENT.md](./DEPLOYMENT.md)
- [OBSERVABILITY.md](./OBSERVABILITY.md)
- [RUNBOOKS.md](./RUNBOOKS.md)
- [CI_TROUBLESHOOTING.md](./CI_TROUBLESHOOTING.md)

---

_Last Updated | آخر تحديث: February 2026_
