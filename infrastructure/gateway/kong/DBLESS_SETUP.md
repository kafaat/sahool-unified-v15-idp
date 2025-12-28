# Kong DB-less Mode Setup
# إعداد Kong في وضع بدون قاعدة بيانات

## Overview | نظرة عامة

Kong has been configured to run in **DB-less mode** for simplicity and better performance. This means:

- Kong uses declarative configuration files (kong.yml, kong-packages.yml, consumers.yml)
- No database migrations needed for Kong
- Faster startup and lower resource usage
- Configuration is version-controlled and easier to manage

تم تكوين Kong للعمل في **وضع بدون قاعدة بيانات** للبساطة والأداء الأفضل. هذا يعني:

- يستخدم Kong ملفات التكوين التصريحية
- لا حاجة لترحيل قاعدة البيانات لـ Kong
- بدء تشغيل أسرع واستخدام أقل للموارد
- التكوين خاضع لإدارة الإصدارات وأسهل في الإدارة

## Critical Fixes Implemented | الإصلاحات الحرجة المنفذة

### 1. Konga Database Creation | إنشاء قاعدة بيانات Konga

**Problem:** Konga requires its own database, but it wasn't being created.

**Solution:**
- Created `init-konga-db.sh` script to initialize the Konga database
- Script is automatically executed when PostgreSQL container starts
- Mounted in docker-compose.yml at `/docker-entrypoint-initdb.d/init-konga-db.sh`

**Files Changed:**
- `/home/user/sahool-unified-v15-idp/infrastructure/kong/init-konga-db.sh` (NEW)
- `/home/user/sahool-unified-v15-idp/infrastructure/kong/docker-compose.yml` (UPDATED)

### 2. Network Configuration | تكوين الشبكة

**Problem:** `sahool-network` was marked as external, causing failures if the network didn't exist.

**Solution:**
- Changed `sahool-net` from external to local bridge network
- Added comments explaining how to switch back to external mode if needed
- Network is now created automatically by docker-compose

**Files Changed:**
- `/home/user/sahool-unified-v15-idp/infrastructure/kong/docker-compose.yml` (UPDATED)

### 3. Declarative Config Loading | تحميل التكوين التصريحي

**Problem:** Kong was using database mode but declarative config was commented out.

**Solution:**
- Switched Kong to DB-less mode (`KONG_DATABASE=off`)
- Enabled `KONG_DECLARATIVE_CONFIG=/etc/kong/kong.yml`
- Removed `kong-migrations` and `kong-migrations-up` services (not needed in DB-less mode)
- Kept PostgreSQL database for Konga only

**Files Changed:**
- `/home/user/sahool-unified-v15-idp/infrastructure/kong/docker-compose.yml` (UPDATED)

### 4. Additional Improvements | تحسينات إضافية

**Health Checks Added:**
- Konga: HTTP check on port 1337
- Prometheus: HTTP check on `/-/healthy` endpoint
- Grafana: HTTP check on `/api/health` endpoint

**Volume Consolidation:**
- All volumes now defined in a single section at the top
- Removed duplicate volume definitions

## Architecture | البنية

```
┌─────────────────────────────────────────────────────────────┐
│                     Kong API Gateway                         │
│                    (DB-less Mode)                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Declarative Config Files:                           │  │
│  │  • kong.yml (39 microservices)                       │  │
│  │  • kong-packages.yml (package-specific routes)       │  │
│  │  • consumers.yml (JWT consumers)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Konga UI   │    │  Prometheus  │    │   Grafana    │
│ (with DB)    │    │  (Metrics)   │    │ (Dashboard)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │
        │
        ▼
┌──────────────┐
│  PostgreSQL  │
│ (Konga only) │
└──────────────┘
```

## Configuration Updates | تحديثات التكوين

### Kong Service Changes

**Before:**
```yaml
environment:
  KONG_DATABASE: postgres
  KONG_PG_HOST: kong-database
  # KONG_DECLARATIVE_CONFIG: /etc/kong/kong.yml  # Commented out
depends_on:
  kong-database:
    condition: service_healthy
  kong-migrations-up:
    condition: service_completed_successfully
```

**After:**
```yaml
environment:
  KONG_DATABASE: "off"
  KONG_DECLARATIVE_CONFIG: /etc/kong/kong.yml
# No database dependencies
```

### PostgreSQL Service Changes

**Before:**
```yaml
volumes:
  - kong-postgres-data:/var/lib/postgresql/data
```

**After:**
```yaml
volumes:
  - kong-postgres-data:/var/lib/postgresql/data
  - ./init-konga-db.sh:/docker-entrypoint-initdb.d/init-konga-db.sh:ro
```

## Usage | الاستخدام

### Starting Services | بدء الخدمات

```bash
cd /home/user/sahool-unified-v15-idp/infrastructure/kong
docker-compose up -d
```

### Updating Configuration | تحديث التكوين

To update Kong configuration:

1. Edit the declarative config files:
   - `kong.yml` - Main services and routes
   - `kong-packages.yml` - Package-specific configurations
   - `consumers.yml` - JWT consumers and credentials

2. Reload Kong configuration:
   ```bash
   docker exec kong-gateway kong reload
   ```

   Or restart Kong:
   ```bash
   docker-compose restart kong
   ```

### Verifying Configuration | التحقق من التكوين

```bash
# Check Kong status
curl http://localhost:8001/status

# Validate declarative config
docker exec kong-gateway kong config parse /etc/kong/kong.yml

# Check services
curl http://localhost:8001/services

# Check routes
curl http://localhost:8001/routes
```

## Service URLs | روابط الخدمات

| Service | URL | Description |
|---------|-----|-------------|
| Kong Proxy | http://localhost:8000 | API Gateway proxy endpoint |
| Kong Admin API | http://localhost:8001 | Admin API for management |
| Konga UI | http://localhost:1337 | Web-based admin interface |
| Prometheus | http://localhost:9090 | Metrics and monitoring |
| Grafana | http://localhost:3002 | Visualization dashboard |
| PostgreSQL | localhost:5433 | Database (Konga only) |

## Important Notes | ملاحظات مهمة

### DB-less Mode Limitations

1. **No Admin API writes**: In DB-less mode, you cannot use the Admin API to create/update entities. All configuration must be done via declarative files.

2. **Configuration reload required**: After editing declarative config files, you must reload Kong for changes to take effect.

3. **Konga compatibility**: Konga is designed for database mode. In DB-less mode:
   - Konga can still be used to VIEW configuration
   - Konga CANNOT be used to MODIFY configuration
   - Use Konga as a read-only dashboard

### Switching Back to Database Mode (If Needed)

If you need to switch back to database mode:

1. Edit `docker-compose.yml`:
   ```yaml
   kong:
     environment:
       KONG_DATABASE: postgres
       KONG_PG_HOST: kong-database
       KONG_PG_PORT: 5432
       KONG_PG_DATABASE: ${KONG_PG_DATABASE:-kong}
       KONG_PG_USER: ${KONG_PG_USER:-kong}
       KONG_PG_PASSWORD: ${KONG_PG_PASSWORD:-kong}
       # Remove or comment out:
       # KONG_DECLARATIVE_CONFIG: /etc/kong/kong.yml
   ```

2. Uncomment the migration services in docker-compose.yml

3. Restart services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. Use `deck sync` to import declarative config into database:
   ```bash
   deck sync -s kong.yml --kong-addr http://localhost:8001
   ```

## Troubleshooting | استكشاف الأخطاء

### Kong fails to start

```bash
# Check logs
docker-compose logs kong

# Validate config file
docker exec kong-gateway kong config parse /etc/kong/kong.yml
```

### Konga database not created

```bash
# Check PostgreSQL logs
docker-compose logs kong-database

# Manually create database
docker exec -it kong-postgres psql -U kong -c "CREATE DATABASE konga;"
```

### Network issues

```bash
# If using external sahool-network, create it first:
docker network create sahool-network

# Then update docker-compose.yml:
# Change sahool-net to external: true
```

## Migration Path | مسار الترحيل

If you have existing Kong database configuration:

1. Export current configuration:
   ```bash
   deck dump --kong-addr http://localhost:8001 --output-file kong-backup.yml
   ```

2. Switch to DB-less mode (follow steps above)

3. Use the exported configuration as your declarative config

4. Test thoroughly before removing database

## Health Checks | فحوصات الصحة

All services now have proper health checks:

- **Kong**: `kong health` command
- **Konga**: HTTP check on port 1337
- **Prometheus**: HTTP check on `/-/healthy`
- **Grafana**: HTTP check on `/api/health`
- **PostgreSQL**: `pg_isready` command
- **Redis**: `redis-cli ping`

## Support | الدعم

For issues or questions:
- Check logs: `docker-compose logs [service-name]`
- Verify config: `docker exec kong-gateway kong config parse /etc/kong/kong.yml`
- Review Kong documentation: https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/
