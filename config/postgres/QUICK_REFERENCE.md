# PostgreSQL HA - Quick Reference Card

## 🚀 Deployment Commands

### Start HA Cluster
```bash
docker-compose -f docker-compose.yml -f docker-compose.ha.yml up -d postgres postgres-replica
```

### Start All Services
```bash
docker-compose -f docker-compose.yml -f docker-compose.ha.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.yml -f docker-compose.ha.yml down
```

---

## 🔍 Health Checks

### Check Primary
```bash
docker exec -it sahool-postgres-primary pg_isready -U sahool
```

### Check Replica
```bash
docker exec -it sahool-postgres-replica pg_isready -U sahool
```

### Check Replication Status
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "SELECT * FROM pg_stat_replication;"
```

### Check Replication Lag
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT application_name,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS lag
FROM pg_stat_replication;"
```

---

## 📊 Monitoring

### Connection Count
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT count(*) as current, setting::int as max,
       round(100.0 * count(*) / setting::int, 2) as pct
FROM pg_stat_activity, pg_settings WHERE name = 'max_connections';"
```

### PgBouncer Status
```bash
docker exec -it sahool-pgbouncer psql -h localhost -p 6432 -U pgbouncer_admin pgbouncer -c "SHOW POOLS;"
```

### Top Slow Queries
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT substring(query, 1, 60) as query, calls, mean_exec_time
FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

### Cache Hit Ratio
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT round(100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2) AS cache_hit_pct
FROM pg_stat_database;"
```

---

## 🔧 Maintenance

### Manual Vacuum
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "VACUUM ANALYZE;"
```

### Reindex Table
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "REINDEX TABLE table_name;"
```

### Update Statistics
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "ANALYZE;"
```

---

## 💾 Backup

### Manual Backup
```bash
docker exec sahool-postgres-primary pg_dump -U sahool -Fc sahool > backup_$(date +%Y%m%d).dump
```

### Restore
```bash
docker exec -i sahool-postgres-primary pg_restore -U sahool -d sahool < backup.dump
```

---

## 🚨 Emergency Procedures

### Promote Replica to Primary
```bash
docker exec -it sahool-postgres-replica pg_ctl promote
```

### Check if Replica is Now Primary
```bash
docker exec -it sahool-postgres-replica psql -U sahool -c "SELECT pg_is_in_recovery();"
# Expected: f (false = primary)
```

### Restart Primary
```bash
docker restart sahool-postgres-primary
```

### Restart Replica
```bash
docker restart sahool-postgres-replica
```

---

## 📝 View Logs

### Primary Logs
```bash
docker logs sahool-postgres-primary
docker logs -f sahool-postgres-primary  # Follow
```

### Replica Logs
```bash
docker logs sahool-postgres-replica
docker logs -f sahool-postgres-replica  # Follow
```

### PgBouncer Logs
```bash
docker logs sahool-pgbouncer
```

---

## 🔐 Security

### Check SSL Status
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "SHOW ssl;"
```

### View SSL Connections
```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT datname, usename, ssl, version
FROM pg_stat_ssl JOIN pg_stat_activity USING (pid) WHERE ssl = true;"
```

---

## 📋 Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| postgresql.conf | `/config/postgres/` | Primary configuration |
| pg_hba.conf | `/config/postgres/` | Authentication rules |
| postgresql-replica.conf | `/config/postgres/` | Replica overrides |
| pgbouncer.ini | `/infrastructure/core/pgbouncer/` | Connection pooling |
| docker-compose.ha.yml | `/` | HA deployment |

---

## 📞 Key Ports

| Service | Port | Access |
|---------|------|--------|
| PostgreSQL Primary | 5432 | localhost only |
| PostgreSQL Replica | 5433 | localhost only |
| PgBouncer | 6432 | localhost only |

---

## 🎯 Performance Targets

| Metric | Target | Alert If |
|--------|--------|----------|
| Cache Hit Ratio | >99% | <95% |
| Replication Lag | <1MB | >10MB |
| Connection Usage | <80% | >90% |
| Query Time (p95) | <100ms | >500ms |

---

## 📚 Full Documentation

- **Setup Guide:** `config/postgres/POSTGRESQL_HA_SETUP.md`
- **Implementation Summary:** `POSTGRESQL_HA_IMPLEMENTATION_SUMMARY.md`
- **Database Audit:** `tests/database/POSTGRESQL_AUDIT.md`

---

**Quick Help:** For detailed troubleshooting and procedures, refer to the full documentation above.
