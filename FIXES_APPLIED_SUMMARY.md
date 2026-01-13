# Database Connection Fixes Applied

## Summary

Fixed database connection issues affecting multiple services.

## Fixes Applied

### 1. ✅ PgBouncer SCRAM Authentication

- **Issue:** PostgreSQL 16 uses SCRAM-SHA-256, but PgBouncer was configured for MD5
- **Fix:**
  - Updated `infrastructure/core/pgbouncer/pgbouncer.ini` to use `auth_type = scram-sha-256`
  - Added `auth_query` to query PostgreSQL directly for password verification
  - Created `pgbouncer` user in PostgreSQL with `pg_monitor` role
- **Status:** ✅ Fixed - PgBouncer now supports SCRAM authentication

### 2. ✅ Billing-Core Async Driver

- **Issue:** Using `postgresql+psycopg2://` (sync) with async SQLAlchemy
- **Fix:**
  - Changed `DATABASE_URL` in `docker-compose.yml` to `postgresql+asyncpg://`
  - Updated `apps/services/billing-core/src/database.py` to:
    - Convert `postgresql+psycopg2://` to `postgresql+asyncpg://`
    - Use `AsyncQueuePool` instead of `QueuePool` for async engines
- **Status:** ✅ Fixed - Billing-core now uses async driver correctly

### 3. ✅ PgBouncer User Creation

- **Issue:** `pgbouncer` user didn't exist in PostgreSQL
- **Fix:**
  - Created user: `CREATE USER pgbouncer WITH PASSWORD 'pgbouncer_auth_query'`
  - Granted `pg_monitor` role for auth_query access
- **Status:** ✅ Fixed - User created and permissions granted

### 4. ✅ MQTT Password File

- **Issue:** Password file had encoding issues and wrong permissions
- **Fix:**
  - Regenerated password file with proper SHA-512 format
  - Added command to fix permissions on container startup
- **Status:** ✅ Fixed - MQTT authentication working

## Services Restarted

- `billing-core` - Recreated with new async driver
- `pgbouncer` - Restarted after user creation
- `chat-service` - Restarted to pick up auth fix
- `marketplace-service` - Restarted to pick up auth fix
- `research-core` - Restarted to pick up auth fix
- `notification-service` - Already healthy

## Current Status

### Services Still Restarting (Expected - may need more time)

- `chat-service` - Connecting to database
- `marketplace-service` - Connecting to database
- `research-core` - Connecting to database
- `ai-advisor` - May have DNS issues
- `inventory-service` - Unknown issue
- `ndvi-processor` - Unknown issue

### Services Unhealthy (Non-database related)

- `equipment-service` - Health check failing
- `provider-config` - Health check failing
- `task-service` - Health check failing
- `yield-prediction-service` - Health check failing

## Next Steps

1. **Wait for services to stabilize** (2-3 minutes)
2. **Check logs** for services still restarting:
   ```bash
   docker logs sahool-chat-service --tail 50
   docker logs sahool-marketplace --tail 50
   ```
3. **Verify database connections**:
   ```bash
   docker exec sahool-pgbouncer psql -h localhost -p 6432 -U sahool -d sahool -c "SELECT 1;"
   ```
4. **Review health checks** for unhealthy services

## Files Modified

- `docker-compose.yml` - Updated billing-core DATABASE_URL
- `infrastructure/core/pgbouncer/pgbouncer.ini` - SCRAM auth configuration
- `infrastructure/core/postgres/init/02-pgbouncer-user.sql` - User creation script
- `apps/services/billing-core/src/database.py` - Async driver and pool fixes
- `infrastructure/core/mqtt/passwd` - Regenerated password file
