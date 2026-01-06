# Provider Configuration Service - PostgreSQL Migration Guide

## Overview

The provider-config service has been migrated from in-memory storage to PostgreSQL with Redis caching. This ensures provider configurations persist across restarts and provides version history for audit and rollback capabilities.

## Changes Made

### 1. Database Schema

Created two new tables in PostgreSQL:

- **`provider_configs`**: Stores provider configurations for each tenant
  - Supports all provider types: map, weather, satellite, payment, SMS, notification
  - Includes API keys, priorities, enable/disable flags
  - Unique constraint per tenant/provider type/provider name
  - Automatic version tracking

- **`config_versions`**: Version history for all configuration changes
  - Tracks every create, update, delete, enable, disable operation
  - Enables audit trail and rollback capabilities
  - Automatic triggers maintain history

### 2. Service Architecture

**Before (In-Memory)**:
```python
tenant_configs: dict[str, TenantProviderConfig] = {}
provider_status_cache: dict[str, ProviderStatusResponse] = {}
```

**After (Database + Cache)**:
```python
# PostgreSQL for persistence
database: Database
# Redis for performance caching (5-minute TTL)
cache_manager: CacheManager
# Service layer for business logic
config_service: ProviderConfigService
```

### 3. New Features

#### a. Persistent Storage
- Configurations survive service restarts
- Multi-tenant isolation
- Atomic operations with transactions

#### b. Caching Layer
- Redis caching with 5-minute TTL
- Automatic cache invalidation on updates
- Graceful fallback if Redis unavailable

#### c. Version History
- Complete audit trail of all changes
- Rollback to any previous version
- Track who made changes and when

### 4. New API Endpoints

#### Version History
```bash
# Get configuration history
GET /config/{tenant_id}/history?provider_type=map&limit=100

# Rollback to specific version
POST /config/{tenant_id}/rollback
{
  "config_id": "uuid",
  "version": 3
}
```

## Database Setup

### 1. Initialize Schema

The schema is automatically created on service startup, but you can also initialize it manually:

```bash
# Connect to PostgreSQL
psql -U sahool -d sahool -h localhost -p 5432

# Run the initialization script
\i apps/services/provider-config/src/db_init.sql
```

### 2. Verify Tables

```sql
-- Check tables exist
\dt provider_configs
\dt config_versions

-- Check indexes
\di provider_configs*
\di config_versions*

-- View table structure
\d provider_configs
\d config_versions
```

## Migration Steps

### 1. Update Environment Variables

Add to `.env`:
```bash
# Database connection (already exists)
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool

# Redis connection (already exists)
REDIS_URL=redis://:password@redis:6379/0
```

### 2. Rebuild Service

```bash
# Rebuild provider-config service
docker-compose build provider-config

# Restart with new configuration
docker-compose up -d provider-config

# Check logs
docker-compose logs -f provider-config
```

Expected startup logs:
```
✓ Database initialized successfully
✓ Cache initialized successfully
✓ Provider Config Service initialized
```

### 3. Migrate Existing Data (if any)

If you have existing in-memory configurations to migrate:

```python
# Example migration script (run once)
import requests

# Old in-memory data
old_configs = {
    "tenant_001": {
        "map_providers": [
            {"provider_name": "openstreetmap", "priority": "primary", "enabled": True}
        ]
    }
}

# Migrate to database
for tenant_id, config in old_configs.items():
    response = requests.post(
        f"http://localhost:8104/config/{tenant_id}",
        json=config
    )
    print(f"Migrated {tenant_id}: {response.json()}")
```

## Testing

### 1. Test Configuration Persistence

```bash
# Create a configuration
curl -X POST http://localhost:8104/config/test-tenant \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "test-tenant",
    "map_providers": [{
      "provider_name": "openstreetmap",
      "api_key": null,
      "priority": "primary",
      "enabled": true
    }]
  }'

# Restart service
docker-compose restart provider-config

# Verify configuration persists
curl http://localhost:8104/config/test-tenant
```

### 2. Test Caching

```bash
# First request (database query)
time curl http://localhost:8104/config/test-tenant

# Second request (cached - should be faster)
time curl http://localhost:8104/config/test-tenant

# Check Redis cache
docker exec -it sahool-redis redis-cli
> KEYS provider_config:*
> GET provider_config:test-tenant:all
```

### 3. Test Version History

```bash
# Create initial config
curl -X POST http://localhost:8104/config/test-tenant \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "test-tenant", "map_providers": [{"provider_name": "openstreetmap", "priority": "primary", "enabled": true}]}'

# Update config
curl -X POST http://localhost:8104/config/test-tenant \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "test-tenant", "map_providers": [{"provider_name": "openstreetmap", "priority": "secondary", "enabled": false}]}'

# View history
curl http://localhost:8104/config/test-tenant/history

# Response:
{
  "tenant_id": "test-tenant",
  "history": [
    {
      "version": 2,
      "change_type": "disabled",
      "changed_at": "2024-02-15T10:30:00Z"
    },
    {
      "version": 1,
      "change_type": "created",
      "changed_at": "2024-02-15T10:25:00Z"
    }
  ]
}
```

## Performance

### Before (In-Memory)
- **Read**: O(1) - instant
- **Write**: O(1) - instant
- **Persistence**: ❌ Lost on restart
- **Multi-instance**: ❌ No shared state

### After (Database + Cache)
- **Read (cached)**: O(1) - ~5ms (Redis)
- **Read (uncached)**: ~20-50ms (PostgreSQL)
- **Write**: ~30-100ms (PostgreSQL + cache invalidation)
- **Persistence**: ✅ Survives restarts
- **Multi-instance**: ✅ Shared state via database

## Rollback Plan

If issues occur, you can temporarily revert to in-memory storage:

1. **Quick Rollback**: Use previous Docker image
   ```bash
   docker-compose down provider-config
   # Restore previous image
   docker tag sahool-provider-config:backup sahool-provider-config:latest
   docker-compose up -d provider-config
   ```

2. **Keep Database Schema**: The database tables don't affect the service if environment variables are not set. The service will fall back to defaults.

## Monitoring

### 1. Database Metrics

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename IN ('provider_configs', 'config_versions');

-- Check recent changes
SELECT
    tenant_id,
    provider_type,
    change_type,
    changed_at
FROM config_versions
ORDER BY changed_at DESC
LIMIT 20;

-- Check active configurations per tenant
SELECT
    tenant_id,
    provider_type,
    COUNT(*) as provider_count,
    COUNT(*) FILTER (WHERE enabled = true) as enabled_count
FROM provider_configs
GROUP BY tenant_id, provider_type;
```

### 2. Cache Metrics

```bash
# Redis CLI
docker exec -it sahool-redis redis-cli

# Check cache hit rate
INFO stats

# View cached keys
KEYS provider_config:*

# Check cache memory usage
INFO memory
```

### 3. Service Logs

```bash
# Monitor service logs
docker-compose logs -f provider-config | grep -E "(Cache|Database|Config)"

# Expected log patterns:
# ✓ Database initialized successfully
# ✓ Cache initialized successfully
# Cache hit for provider_config:tenant_001:map
# Cache miss for provider_config:tenant_002:weather
# Created config for tenant tenant_001: map/openstreetmap
# Updated config for tenant tenant_001: map/google_maps
```

## Troubleshooting

### Issue: Service fails to start

**Symptoms**: Service exits immediately or shows "Database not initialized"

**Solution**:
1. Check database connection:
   ```bash
   docker-compose exec provider-config env | grep DATABASE_URL
   ```
2. Verify PgBouncer is running:
   ```bash
   docker-compose ps pgbouncer
   docker-compose logs pgbouncer
   ```
3. Test database connectivity:
   ```bash
   docker-compose exec provider-config python -c "
   from models import Database
   db = Database('postgresql://sahool:password@pgbouncer:6432/sahool')
   print('✓ Database connection successful')
   "
   ```

### Issue: Cache errors (non-critical)

**Symptoms**: Warnings about cache failures

**Solution**: Service continues without caching. To fix:
1. Check Redis connection:
   ```bash
   docker-compose ps redis
   docker-compose logs redis
   ```
2. Verify Redis URL:
   ```bash
   docker-compose exec provider-config env | grep REDIS_URL
   ```

### Issue: Duplicate key errors

**Symptoms**: "Configuration already exists" error

**Solution**: This is expected - each tenant can only have one configuration per provider type/name. To update, use the POST endpoint which handles updates automatically.

## Security Considerations

### API Key Storage

⚠️ **Current Implementation**: API keys are stored in plain text in the database.

**Production Recommendations**:

1. **Encrypt API keys** using application-level encryption:
   ```python
   from cryptography.fernet import Fernet

   # In config_service.py
   def encrypt_api_key(self, key: str) -> str:
       return self.cipher.encrypt(key.encode()).decode()

   def decrypt_api_key(self, encrypted_key: str) -> str:
       return self.cipher.decrypt(encrypted_key.encode()).decode()
   ```

2. **Use PostgreSQL encryption**:
   ```sql
   -- Add pgcrypto extension
   CREATE EXTENSION IF NOT EXISTS pgcrypto;

   -- Encrypt on insert
   INSERT INTO provider_configs (api_key)
   VALUES (pgp_sym_encrypt('secret-key', 'encryption-password'));

   -- Decrypt on select
   SELECT pgp_sym_decrypt(api_key::bytea, 'encryption-password') FROM provider_configs;
   ```

3. **Use HashiCorp Vault** or AWS Secrets Manager for key storage

## Benefits Summary

✅ **Persistence**: Configurations survive restarts
✅ **Performance**: Redis caching for fast reads
✅ **Audit Trail**: Complete version history
✅ **Rollback**: Restore any previous version
✅ **Multi-tenant**: Isolated configurations per tenant
✅ **Scalability**: Multiple service instances share state
✅ **Reliability**: Database transactions ensure consistency

## Next Steps

1. ✅ Database schema created
2. ✅ Service code updated
3. ✅ Caching layer implemented
4. ✅ Docker configuration updated
5. ⏳ Test in staging environment
6. ⏳ Migrate production data
7. ⏳ Implement API key encryption
8. ⏳ Set up monitoring alerts
