# Database Connection Pooling Optimization

# تحسين تجميع الاتصالات بقاعدة البيانات

**Date:** 2026-01-06
**Status:** ✅ Implemented
**Services:** All Prisma-based services (9 services)

## Overview

This document describes the database connection pooling optimizations implemented across the SAHOOL platform to improve database performance, reduce connection overhead, and prevent connection exhaustion.

## Table of Contents

1. [Architecture](#architecture)
2. [Service Categorization](#service-categorization)
3. [Connection Pool Configuration](#connection-pool-configuration)
4. [Monitoring and Metrics](#monitoring-and-metrics)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Architecture

### Two-Tier Connection Pooling

SAHOOL platform uses a two-tier connection pooling strategy:

1. **PgBouncer (External Pool)**: Connection pooler between services and PostgreSQL
   - Session pooling mode
   - Handles connection routing and pooling at the infrastructure level
   - Reduces direct connections to PostgreSQL

2. **Prisma Client (Application Pool)**: Per-service connection limits
   - Configured via `connection_limit` parameter
   - Optimized based on service workload
   - Built-in query engine connection management

```
┌─────────────────┐
│   Services      │
│  (9 services)   │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Prisma  │  ← Application-level pooling (connection_limit)
    │ Client  │
    └────┬────┘
         │
    ┌────▼────────┐
    │  PgBouncer  │  ← Infrastructure-level pooling
    │  (Session)  │
    └────┬────────┘
         │
    ┌────▼──────────┐
    │  PostgreSQL   │
    │   (Primary)   │
    └───────────────┘
```

---

## Service Categorization

Services are categorized by traffic patterns and allocated connection pool sizes accordingly:

### High Traffic Services (10 connections)

- **user-service**: Authentication, user management (frequent queries)
- **chat-service**: Real-time messaging (high read/write)
- **marketplace-service**: Marketplace transactions (high concurrency)

### Medium Traffic Services (8 connections)

- **research-core**: Research data management
- **inventory-service**: Inventory tracking and alerts
- **field-management-service**: Field operations
- **field-core**: Field and farm management

### Low Traffic Services (6 connections)

- **weather-service**: Periodic weather data fetching
- **iot-service**: IoT device data collection

---

## Connection Pool Configuration

### Prisma Schema Configuration

All Prisma schemas have been updated with:

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
  // Direct URL for migrations (bypasses PgBouncer)
  directUrl = env("DATABASE_URL_DIRECT")
}
```

**Why `directUrl`?**

- Prisma migrations require certain PostgreSQL features not supported through PgBouncer
- `directUrl` allows migrations to connect directly to PostgreSQL
- Runtime queries use `url` which goes through PgBouncer

### Environment Variables

#### Per-Service DATABASE_URL

Each service should use the appropriate connection URL based on its tier:

```bash
# High Traffic Services
DATABASE_URL="postgresql://user:pass@pgbouncer:6432/db?sslmode=require&pgbouncer=true&connection_limit=10&pool_timeout=20&connect_timeout=10&statement_timeout=30000"

# Medium Traffic Services
DATABASE_URL="postgresql://user:pass@pgbouncer:6432/db?sslmode=require&pgbouncer=true&connection_limit=8&pool_timeout=20&connect_timeout=10&statement_timeout=30000"

# Low Traffic Services
DATABASE_URL="postgresql://user:pass@pgbouncer:6432/db?sslmode=require&pgbouncer=true&connection_limit=6&pool_timeout=20&connect_timeout=10&statement_timeout=30000"

# For Migrations (all services)
DATABASE_URL_DIRECT="postgresql://user:pass@postgres:5432/db?sslmode=require&connect_timeout=10&keepalives=1&keepalives_idle=30&keepalives_interval=10&keepalives_count=5"
```

#### Connection Pool Parameters

| Parameter           | Value   | Description                                |
| ------------------- | ------- | ------------------------------------------ |
| `connection_limit`  | 6-10    | Max connections per Prisma Client instance |
| `pool_timeout`      | 20s     | Max time to wait for available connection  |
| `connect_timeout`   | 10s     | Max time to establish initial connection   |
| `statement_timeout` | 30000ms | Max query execution time                   |
| `sslmode`           | require | Enforce TLS/SSL connections                |
| `pgbouncer`         | true    | Enable PgBouncer compatibility mode        |

### TCP Keepalive Configuration

TCP keepalive prevents connection drops through firewalls and load balancers:

```bash
# In DATABASE_URL_DIRECT
keepalives=1              # Enable TCP keepalive
keepalives_idle=30        # Start probes after 30s of idle
keepalives_interval=10    # Probe every 10s
keepalives_count=5        # 5 failed probes = dead connection
```

**Benefits:**

- Prevents connection drops in cloud environments
- Early detection of network issues
- Maintains connection health through NAT/firewalls

### Timeout Configuration

| Timeout Type        | Value | Purpose                        |
| ------------------- | ----- | ------------------------------ |
| Connection Timeout  | 10s   | Fail fast on connection issues |
| Pool Timeout        | 20s   | Wait for available connection  |
| Query Timeout       | 30s   | Prevent long-running queries   |
| Idle Timeout        | 600s  | Close unused connections       |
| Connection Lifetime | 3600s | Prevent stale connections      |

---

## Monitoring and Metrics

### Built-in Prisma Metrics

All PrismaService classes now include automatic connection pool metrics collection:

```typescript
/**
 * Get current connection pool metrics
 */
async getPoolMetrics() {
  try {
    const metrics = await this.$metrics.json();
    return {
      activeConnections: // Currently executing queries
      waitingConnections: // Queries waiting for connection
      totalQueries: // Total queries executed
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    this.logger.error('Failed to get pool metrics:', error);
    return null;
  }
}
```

### Automatic Metrics Logging

Each service logs connection pool metrics every 5 minutes:

```
Connection Pool Metrics: {
  pool: {
    active: 3,     // Active connections
    wait: 0,       // Connections waiting
    total: 1547    // Total queries
  },
  timestamp: "2026-01-06T12:00:00.000Z"
}
```

### Prometheus Metrics Export

Prisma metrics are automatically exposed in Prometheus format:

```
# HELP prisma_client_queries_active Number of currently active queries
# TYPE prisma_client_queries_active gauge
prisma_client_queries_active 3

# HELP prisma_client_queries_wait Number of queries waiting for a connection
# TYPE prisma_client_queries_wait gauge
prisma_client_queries_wait 0

# HELP prisma_client_queries_total Total number of queries
# TYPE prisma_client_queries_total counter
prisma_client_queries_total 1547
```

### Grafana Dashboard

Monitor connection pool health through Grafana dashboards:

- Active connections per service
- Connection wait times
- Pool saturation alerts
- Query performance metrics

---

## Best Practices

### 1. Connection Pool Sizing

**Rule of Thumb:**

```
Pool Size = ((Core Count × 2) + Effective Spindle Count)
```

For containerized environments:

- **CPU-bound workloads**: `pool_size = cores × 2`
- **I/O-bound workloads**: `pool_size = cores × 4`

**SAHOOL Platform:**

- High traffic: 10 connections (expected high concurrency)
- Medium traffic: 8 connections (moderate load)
- Low traffic: 6 connections (periodic operations)

### 2. Avoid Connection Leaks

Always use Prisma's built-in lifecycle hooks:

```typescript
async onModuleDestroy() {
  await this.$disconnect();
  this.logger.log('Database disconnected');
}
```

### 3. Query Optimization

Monitor slow queries (>1000ms threshold):

```typescript
this.$on("query", (e: any) => {
  if (e.duration > 1000) {
    this.logger.warn(`Slow query detected (${e.duration}ms): ${e.query}`);
  }
});
```

### 4. Connection Lifecycle

```
1. Connection Request → Pool Check
2. Available? → Use Connection
3. Not Available? → Wait (pool_timeout)
4. Timeout? → Error
5. Query Complete → Return to Pool
6. Idle > idle_timeout → Close Connection
7. Age > connection_lifetime → Replace Connection
```

### 5. PgBouncer Integration

When using PgBouncer:

- ✅ **DO**: Add `pgbouncer=true` parameter
- ✅ **DO**: Use session pooling mode
- ✅ **DO**: Set reasonable `connection_limit`
- ❌ **DON'T**: Use prepared statements across connections
- ❌ **DON'T**: Use `SET` statements (not persisted)

---

## Troubleshooting

### Issue: "Too many connections" Error

**Symptoms:**

```
Error: P1001: Can't reach database server at `pgbouncer:6432`
```

**Solutions:**

1. Check PgBouncer max_client_conn setting
2. Reduce per-service `connection_limit`
3. Verify PostgreSQL `max_connections`
4. Check for connection leaks (monitor metrics)

**Diagnostic:**

```bash
# Check PgBouncer status
docker exec pgbouncer psql -p 6432 -d pgbouncer -c "SHOW POOLS;"

# Check PostgreSQL connections
docker exec postgres psql -U sahool -c "SELECT count(*) FROM pg_stat_activity;"
```

### Issue: Connection Timeouts

**Symptoms:**

```
Error: Timed out trying to acquire a connection from the pool
```

**Solutions:**

1. Increase `pool_timeout` (current: 20s)
2. Optimize slow queries
3. Increase `connection_limit` for service
4. Check database server load

**Diagnostic:**

```typescript
// Check pool metrics
const metrics = await prismaService.getPoolMetrics();
console.log(metrics.waitingConnections); // High number indicates pool exhaustion
```

### Issue: Stale Connections

**Symptoms:**

```
Error: Connection terminated unexpectedly
```

**Solutions:**

1. TCP keepalive is already enabled (✅)
2. Check firewall/NAT timeout settings
3. Verify `connection_lifetime` setting (current: 3600s)
4. Monitor connection health

**Diagnostic:**

```bash
# Check PostgreSQL idle connections
docker exec postgres psql -U sahool -c "
  SELECT state, count(*)
  FROM pg_stat_activity
  WHERE datname = 'sahool'
  GROUP BY state;
"
```

### Issue: High Pool Wait Times

**Symptoms:**

- Queries queuing for connections
- `prisma_client_queries_wait` > 0 consistently

**Solutions:**

1. Increase `connection_limit` for service tier
2. Optimize query performance (add indexes)
3. Implement caching for frequent queries
4. Consider read replicas for read-heavy workloads

---

## Migration Guide

### Running Migrations

Always use `DATABASE_URL_DIRECT` for migrations:

```bash
# Set direct connection for migrations
export DATABASE_URL="${DATABASE_URL_DIRECT}"

# Run Prisma migrations
npx prisma migrate deploy

# Or using Prisma's built-in directUrl
npx prisma migrate deploy
# (automatically uses directUrl from schema)
```

### Rolling Updates

When updating connection pool settings:

1. Update `.env` with new pool parameters
2. Restart services one at a time (rolling restart)
3. Monitor metrics during rollout
4. Verify no connection errors
5. Document changes

---

## Performance Impact

### Before Optimization

- ❌ Unlimited connections per service
- ❌ No connection pooling at application level
- ❌ Direct PostgreSQL connections
- ❌ No connection lifecycle management
- ❌ No pool metrics

### After Optimization

- ✅ Tiered connection limits (6-10 per service)
- ✅ Application-level pooling (Prisma)
- ✅ Infrastructure-level pooling (PgBouncer)
- ✅ TCP keepalive for connection health
- ✅ Comprehensive metrics and monitoring
- ✅ Automatic pool health logging

### Expected Benefits

- **30-50% reduction** in database connections
- **Improved query latency** (reduced connection overhead)
- **Better resource utilization** (connection reuse)
- **Enhanced stability** (connection limits prevent exhaustion)
- **Proactive monitoring** (metrics-driven optimization)

---

## References

- [Prisma Connection Management](https://www.prisma.io/docs/concepts/components/prisma-client/working-with-prismaclient/connection-management)
- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [PgBouncer Documentation](https://www.pgbouncer.org/config.html)
- [TCP Keepalive Guide](https://tldp.org/HOWTO/TCP-Keepalive-HOWTO/)

---

## Changelog

### 2026-01-06 - Initial Implementation

- ✅ Updated all 9 Prisma schemas with `directUrl` support
- ✅ Configured connection pools by service tier (6-10 connections)
- ✅ Added TCP keepalive to `DATABASE_URL_DIRECT`
- ✅ Implemented connection pool metrics in all PrismaService classes
- ✅ Added automatic metrics logging (5-minute intervals)
- ✅ Updated environment variable templates
- ✅ Created comprehensive documentation

---

**Maintained by:** SAHOOL Platform Engineering
**Last Updated:** 2026-01-06
