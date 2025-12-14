# SAHOOL v15.3.2 Operations Runbook

## Service Management

### Starting Services

```bash
# All services
docker compose up -d

# Specific service
docker compose up -d field_ops

# With logs
docker compose up field_ops
```

### Stopping Services

```bash
# Stop all
docker compose down

# Stop without removing volumes
docker compose stop

# Stop specific service
docker compose stop field_ops
```

### Restarting Services

```bash
# Graceful restart
docker compose restart field_ops

# Force recreate
docker compose up -d --force-recreate field_ops
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f field_ops

# Last 100 lines
docker compose logs --tail=100 field_ops

# Since timestamp
docker compose logs --since 2024-01-15T10:00:00 field_ops
```

## Health Monitoring

### Health Check Endpoints

| Service | Health URL | Ready URL |
|---------|-----------|-----------|
| field_ops | :8080/healthz | :8080/readyz |
| ndvi_engine | :8097/healthz | :8097/readyz |
| weather_core | :8098/healthz | :8098/readyz |
| field_chat | :8099/healthz | :8099/readyz |
| iot_gateway | :8094/healthz | :8094/readyz |
| agro_advisor | :8095/healthz | :8095/readyz |
| ws_gateway | :8090/healthz | :8090/readyz |

### Health Check Script

```bash
./tools/release/smoke_test.sh
```

### Manual Health Checks

```bash
# Quick check all services
for port in 8080 8097 8098 8099 8094 8095 8090; do
  echo -n "Port $port: "
  curl -sf http://localhost:$port/healthz && echo "OK" || echo "FAIL"
done
```

## Database Operations

### Connection

```bash
# Interactive psql
docker exec -it sahool-postgres psql -U sahool -d sahool

# Run single query
docker exec sahool-postgres psql -U sahool -d sahool -c "SELECT count(*) FROM tasks"
```

### Migrations

```bash
# Run all migrations
./tools/env/migrate.sh

# Check migration status
docker exec sahool-postgres psql -U sahool -d sahool -c "SELECT * FROM _migrations ORDER BY applied_at"
```

### Backup

```bash
# Full backup
docker exec sahool-postgres pg_dump -U sahool sahool > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker exec sahool-postgres pg_dump -U sahool sahool | gzip > backup_$(date +%Y%m%d).sql.gz

# Specific tables
docker exec sahool-postgres pg_dump -U sahool -t tasks -t fields sahool > tasks_fields.sql
```

### Restore

```bash
# Full restore (WARNING: destructive)
docker exec -i sahool-postgres psql -U sahool sahool < backup.sql

# Restore to new database
docker exec sahool-postgres createdb -U sahool sahool_restored
docker exec -i sahool-postgres psql -U sahool sahool_restored < backup.sql
```

## NATS Operations

### Monitoring

```bash
# Server info
curl http://localhost:8222/varz

# Connections
curl http://localhost:8222/connz

# Subscriptions
curl http://localhost:8222/subsz
```

### JetStream

```bash
# List streams (requires nats CLI)
nats stream ls

# Stream info
nats stream info SAHOOL_EVENTS

# Consumer info
nats consumer ls SAHOOL_EVENTS
```

### Purging Messages

```bash
# Purge stream (WARNING: data loss)
nats stream purge SAHOOL_EVENTS --force
```

## Redis Operations

### Connection

```bash
# Interactive redis-cli
docker exec -it sahool-redis redis-cli

# Single command
docker exec sahool-redis redis-cli INFO
```

### Memory Check

```bash
docker exec sahool-redis redis-cli INFO memory
```

### Cache Flush

```bash
# Flush all (WARNING: clears all cache)
docker exec sahool-redis redis-cli FLUSHALL

# Flush specific pattern
docker exec sahool-redis redis-cli KEYS "session:*" | xargs docker exec sahool-redis redis-cli DEL
```

## Common Issues

### Service Won't Start

**Symptoms**: Container exits immediately

**Diagnosis**:
```bash
docker compose logs field_ops --tail=50
docker inspect sahool-field-ops --format='{{.State.ExitCode}}'
```

**Common Causes**:
1. Database not ready - wait for postgres healthcheck
2. Missing environment variables
3. Port already in use

### Database Connection Errors

**Symptoms**: "connection refused" or timeout

**Diagnosis**:
```bash
# Check postgres is running
docker compose ps postgres

# Test connectivity
docker exec sahool-field-ops nc -zv postgres 5432
```

**Solutions**:
1. Restart postgres: `docker compose restart postgres`
2. Check network: `docker network inspect sahool-network`

### High Memory Usage

**Symptoms**: OOM kills, slow responses

**Diagnosis**:
```bash
docker stats
docker compose top
```

**Solutions**:
1. Increase container limits in docker-compose.yml
2. Add more replicas for load distribution
3. Check for memory leaks in logs

### NATS Connection Issues

**Symptoms**: Events not flowing

**Diagnosis**:
```bash
curl http://localhost:8222/connz
docker compose logs nats --tail=50
```

**Solutions**:
1. Restart NATS: `docker compose restart nats`
2. Check JetStream is enabled
3. Verify network connectivity

## Performance Tuning

### PostgreSQL

```bash
# Connection pool size (in service env)
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

### NATS

```yaml
# In docker-compose.yml
nats:
  command:
    - "--jetstream"
    - "--max_memory_store=1G"
    - "--max_file_store=10G"
```

### Redis

```bash
# Max memory
docker exec sahool-redis redis-cli CONFIG SET maxmemory 512mb
docker exec sahool-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Scheduled Tasks

### Recommended Cron Jobs

```cron
# Backup database daily at 2 AM
0 2 * * * /path/to/backup.sh

# Rotate logs weekly
0 0 * * 0 docker compose logs --no-color > /logs/sahool_$(date +\%Y\%W).log

# Health check every 5 minutes
*/5 * * * * /path/to/health_check.sh

# Clean old audit logs monthly
0 3 1 * * /path/to/cleanup_audit.sh
```

## Disaster Recovery

### Complete System Recovery

1. **Stop all services**
   ```bash
   docker compose down
   ```

2. **Restore database**
   ```bash
   docker compose up -d postgres
   sleep 10
   docker exec -i sahool-postgres psql -U sahool sahool < backup.sql
   ```

3. **Restore NATS streams** (if backed up)
   ```bash
   docker compose up -d nats
   nats stream restore /backups/nats/
   ```

4. **Start all services**
   ```bash
   docker compose up -d
   ```

5. **Verify**
   ```bash
   ./tools/release/smoke_test.sh
   ```

### Rollback Deployment

```bash
# Tag current state
docker compose down
docker tag sahool/field-ops:15.3.2 sahool/field-ops:rollback-$(date +%Y%m%d)

# Restore previous version
docker compose pull  # Get previous version
docker compose up -d
```

## Contacts

- **On-Call**: See PagerDuty rotation
- **Database Issues**: DBA team
- **Security Incidents**: security@sahool.io
- **Platform Issues**: platform-team@sahool.io
