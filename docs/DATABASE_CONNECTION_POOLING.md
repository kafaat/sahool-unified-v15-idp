# Database Connection Pool Configuration

## Overview

SAHOOL platform runs 39+ microservices that all need database connections. Without proper connection pooling, this can quickly exhaust PostgreSQL's connection limit and cause service failures.

This document explains the two-layer connection pooling strategy implemented in SAHOOL.

## Problem

**Before optimization:**
- Each service had a pool size of only 10 connections
- With 39+ services, potential maximum connections: 390+
- PostgreSQL default max_connections: 100
- Result: Connection exhaustion and service failures

**After optimization:**
- Application-level pooling: 50 connections per service (configurable)
- PgBouncer connection pooling: Manages actual PostgreSQL connections
- PostgreSQL sees only 100 connections max
- All services work reliably

## Two-Layer Pooling Strategy

### Layer 1: Application Connection Pool (TypeORM)

Each Node.js service using TypeORM maintains its own connection pool:

```typescript
// apps/services/*/src/data-source.ts
extra: {
    max: parseInt(process.env.DB_POOL_SIZE || "50"),    // Maximum pool size
    min: 5,                                              // Minimum connections kept alive
    idleTimeoutMillis: 300000,                           // 5 minutes idle timeout
    connectionTimeoutMillis: 10000,                      // 10 seconds connection timeout
    statement_timeout: 120000,                           // 2 minutes query timeout
    keepAlive: true,                                     // TCP keep-alive
    keepAliveInitialDelayMillis: 10000,                 // Keep-alive delay
}
```

### Layer 2: PgBouncer Connection Pool

PgBouncer sits between services and PostgreSQL, multiplexing connections:

```yaml
# docker-compose.yml
pgbouncer:
  environment:
    POOL_MODE: transaction                  # Best for web services
    MAX_DB_CONNECTIONS: 100                 # Total PostgreSQL connections
    DEFAULT_POOL_SIZE: 20                   # Connections per database/user
    MIN_POOL_SIZE: 5                        # Warm connections
    MAX_CLIENT_CONN: 500                    # Client connections to PgBouncer
```

## Recommended Settings

### Development (without PgBouncer)

```bash
# .env
DB_POOL_SIZE=50
DB_HOST=postgres
DB_PORT=5432
```

Services connect directly to PostgreSQL with larger pools.

### Production (with PgBouncer)

```bash
# .env
DB_POOL_SIZE=20
DB_HOST=pgbouncer
DB_PORT=6432
```

Services connect to PgBouncer with smaller pools since PgBouncer handles multiplexing.

## Pool Sizing Formula

### Without PgBouncer

```
pool_size_per_service = max_db_connections / number_of_services
```

For SAHOOL (39 services, 100 max connections):
```
pool_size = 100 / 39 ≈ 2-3 connections per service (TOO SMALL!)
```

Solution: Increase to 50 per service, accept that not all services will max out simultaneously.

### With PgBouncer

```
application_pool = 10-20 (smaller, since PgBouncer manages real connections)
pgbouncer_pool = 100 (total PostgreSQL connections)
max_clients = 500 (total application connections to PgBouncer)
```

This allows all services to have adequate pools while PostgreSQL sees only 100 connections.

## Connection Pool Health Monitoring

### TypeORM Health Check

Both `field-core` and `field-management-service` now export a `getPoolHealth()` function:

```typescript
import { getPoolHealth } from './data-source';

const health = await getPoolHealth();
console.log(health);
// {
//   healthy: true,
//   totalConnections: 15,
//   idleConnections: 10,
//   waitingConnections: 0
// }
```

### PgBouncer Monitoring

Connect to PgBouncer admin console:

```bash
# Connect to PgBouncer admin
psql -h localhost -p 6432 -U pgbouncer_admin pgbouncer

# Show pool statistics
SHOW POOLS;

# Show connection statistics
SHOW STATS;

# Show server connections
SHOW SERVERS;

# Show client connections
SHOW CLIENTS;
```

Key metrics to monitor:
- `cl_active`: Active client connections
- `cl_waiting`: Clients waiting for connections
- `sv_active`: Active server connections to PostgreSQL
- `sv_idle`: Idle server connections
- `maxwait`: Maximum wait time for connection

### PostgreSQL Monitoring

Check actual PostgreSQL connections:

```sql
-- Count total connections
SELECT count(*) FROM pg_stat_activity;

-- Connections by application
SELECT application_name, count(*)
FROM pg_stat_activity
GROUP BY application_name;

-- Idle connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'idle';

-- Check max_connections setting
SHOW max_connections;
```

## Timeout Configuration

### Application Timeouts

```typescript
// Connection pool timeouts
connectionTimeoutMillis: 10000,     // Wait 10s for connection from pool
idleTimeoutMillis: 300000,           // Close idle connections after 5 minutes
statement_timeout: 120000,           // Kill queries after 2 minutes
```

### PgBouncer Timeouts

```ini
# pgbouncer.ini
query_timeout = 120                  # Kill query after 120 seconds
query_wait_timeout = 30              # Wait 30s for connection from pool
server_idle_timeout = 600            # Close idle server conn after 10 min
client_idle_timeout = 0              # Don't timeout client connections
```

### PostgreSQL Timeouts

```sql
-- Set in postgresql.conf or database level
ALTER DATABASE sahool SET statement_timeout = '120s';
ALTER DATABASE sahool SET idle_in_transaction_session_timeout = '300s';
```

## Best Practices

### 1. Always Use PgBouncer in Production

PgBouncer prevents connection exhaustion and improves performance through connection reuse.

### 2. Set Application Names

Each service sets its application name for easier monitoring:

```typescript
application_name: "field-management-service"
```

### 3. Use Transaction Pooling Mode

For stateless web services, use `POOL_MODE=transaction`:
- Fastest connection reuse
- Best for REST APIs
- Cannot use session-level features (prepared statements, temp tables)

Use `POOL_MODE=session` only if you need:
- Prepared statements
- Temporary tables
- Advisory locks

### 4. Monitor Pool Saturation

Watch for these warning signs:
- `cl_waiting > 0` in PgBouncer: Clients waiting for connections
- `maxwait > 1000ms`: Long wait times for connections
- Frequent connection timeouts in application logs

### 5. Right-Size Your Pools

Start conservative and increase based on metrics:

```
Initial application pool = 10-20
Initial PgBouncer pool = 100
Monitor and adjust based on:
  - Connection wait times
  - Query throughput
  - Error rates
```

### 6. Keep Connections Warm

Use `min_pool_size` to maintain warm connections:

```typescript
min: 5  // Keep 5 connections always ready
```

This reduces latency for the first requests after idle periods.

## Troubleshooting

### Problem: "Connection pool timeout"

**Cause:** All connections in use, service waiting for available connection

**Solutions:**
1. Increase pool size: `DB_POOL_SIZE=100`
2. Enable PgBouncer to multiplex connections
3. Optimize slow queries holding connections
4. Reduce `connectionTimeoutMillis` to fail faster

### Problem: "FATAL: too many connections"

**Cause:** PostgreSQL max_connections exceeded

**Solutions:**
1. Enable PgBouncer immediately
2. Reduce application pool sizes
3. Increase PostgreSQL `max_connections` (not recommended for 100+ services)

### Problem: "Connection terminated unexpectedly"

**Cause:** Network issues, PostgreSQL restart, or timeout

**Solutions:**
1. Enable TCP keep-alive: `keepAlive: true`
2. Adjust `idleTimeoutMillis` to be less than PostgreSQL timeout
3. Implement retry logic in application

### Problem: "Connection acquisition timeout"

**Cause:** PgBouncer pool exhausted or PostgreSQL overloaded

**Solutions:**
1. Increase `MAX_DB_CONNECTIONS` in PgBouncer
2. Check PostgreSQL performance (slow queries, locks)
3. Scale PostgreSQL (read replicas, connection pooling at DB level)

## Configuration Files

### Application Configuration

```
/apps/services/field-core/src/data-source.ts
/apps/services/field-management-service/src/data-source.ts
```

### PgBouncer Configuration

```
/infrastructure/core/pgbouncer/pgbouncer.ini
/infrastructure/core/pgbouncer/userlist.txt
/infrastructure/core/pgbouncer/docker-compose.pgbouncer.yml
```

### Docker Compose

```
/docker-compose.yml (includes PgBouncer)
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `postgres` | Database host (use `pgbouncer` in production) |
| `DB_PORT` | `5432` | Database port (use `6432` for PgBouncer) |
| `DB_USER` | `sahool` | Database user |
| `DB_PASSWORD` | Required | Database password |
| `DB_NAME` | `sahool` | Database name |
| `DB_POOL_SIZE` | `50` | Application pool size (use `20` with PgBouncer) |

## Performance Impact

### Before Optimization

- Max pool size: 10 connections per service
- Total potential connections: 390+
- Result: Frequent connection exhaustion
- Service failures during peak load

### After Optimization

- Application pool: 50 connections per service (without PgBouncer)
- Application pool: 20 connections per service (with PgBouncer)
- PgBouncer manages 100 PostgreSQL connections
- Result: Stable operation under load
- No connection exhaustion errors

## Testing Pool Configuration

### Load Test Without PgBouncer

```bash
# Start services without PgBouncer
docker compose up -d postgres redis nats

# Run load test
for i in {1..100}; do
  curl http://localhost:3000/api/fields &
done
wait

# Check connections
docker exec sahool-postgres psql -U sahool -c "SELECT count(*) FROM pg_stat_activity;"
```

### Load Test With PgBouncer

```bash
# Start services with PgBouncer
docker compose up -d postgres pgbouncer redis nats

# Update services to use PgBouncer
export DB_HOST=pgbouncer
export DB_PORT=6432

# Run load test
for i in {1..100}; do
  curl http://localhost:3000/api/fields &
done
wait

# Check PgBouncer stats
docker exec sahool-pgbouncer psql -h localhost -p 6432 -U pgbouncer_admin pgbouncer -c "SHOW POOLS;"

# Check PostgreSQL connections (should be much lower)
docker exec sahool-postgres psql -U sahool -c "SELECT count(*) FROM pg_stat_activity;"
```

## Further Reading

- [PgBouncer Documentation](https://www.pgbouncer.org/usage.html)
- [TypeORM Connection Options](https://typeorm.io/data-source-options)
- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [Node.js pg Pool Documentation](https://node-postgres.com/api/pool)

## Support

For issues or questions about connection pooling:

1. Check PgBouncer logs: `docker logs sahool-pgbouncer`
2. Check PostgreSQL logs: `docker logs sahool-postgres`
3. Review application logs for connection errors
4. Monitor pool statistics using provided health check functions
