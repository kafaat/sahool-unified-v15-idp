# PostgreSQL High Availability Configuration Guide

## SAHOOL Platform - Production-Ready Database Setup

**Last Updated:** 2026-01-06
**PostgreSQL Version:** 16 with PostGIS 3.4
**Configuration Type:** Streaming Replication with Hot Standby

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration Files](#configuration-files)
4. [Prerequisites](#prerequisites)
5. [Deployment Guide](#deployment-guide)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tuning](#performance-tuning)
9. [Security Considerations](#security-considerations)
10. [Backup & Recovery](#backup--recovery)

---

## 🎯 Overview

This PostgreSQL High Availability setup provides:

- **Streaming Replication**: Real-time data synchronization from primary to replica
- **Hot Standby**: Replica accepts read-only queries for load distribution
- **Automatic Failover Ready**: Replica can be promoted to primary
- **Point-in-Time Recovery (PITR)**: WAL archiving for data recovery
- **Production-Optimized**: Performance tuning for 39+ microservices
- **Security Hardened**: TLS encryption, SCRAM-SHA-256 authentication
- **Connection Pooling**: PgBouncer configured for 250 database connections

### Key Improvements from Audit

Based on the PostgreSQL audit (2026-01-06), this configuration addresses:

| Issue | Status | Solution |
|-------|--------|----------|
| No replication/HA | ✅ Fixed | Streaming replication with hot standby |
| TLS not enforced | ✅ Fixed | TLS 1.3 required for all connections |
| Insufficient connections | ✅ Fixed | Increased to 300 max_connections |
| No performance tuning | ✅ Fixed | Optimized for 8GB RAM, SSD storage |
| No automated backups | ✅ Fixed | WAL archiving configured |
| Missing monitoring | ✅ Fixed | pg_stat_statements enabled |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SAHOOL Platform (39+ Services)                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   PgBouncer     │  (Connection Pooler)
            │   Port: 6432    │  - Max DB Connections: 250
            │                 │  - Max Client Conn: 800
            └────────┬────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│  PostgreSQL      │      │  PostgreSQL      │
│  PRIMARY         │ ───> │  REPLICA         │
│  Port: 5432      │      │  Port: 5433      │
│                  │      │                  │
│  - Read/Write    │      │  - Read Only     │
│  - WAL Sender    │      │  - WAL Receiver  │
│  - 8GB RAM       │      │  - 4GB RAM       │
└──────────────────┘      └──────────────────┘
        │                         │
        ▼                         ▼
   WAL Archive              Standby Logs
```

### Data Flow

1. **Write Operations**: Applications → PgBouncer → Primary DB
2. **Read Operations**: Applications → PgBouncer → Primary or Replica
3. **Replication**: Primary → Streaming Replication → Replica
4. **Archiving**: Primary → WAL Archive (for PITR)

---

## 📁 Configuration Files

### Directory Structure

```
config/postgres/
├── postgresql.conf              # Primary production configuration
├── postgresql-replica.conf      # Replica-specific overrides
├── pg_hba.conf                 # Host-based authentication (TLS enforced)
├── postgresql-tls.conf         # TLS/SSL settings (legacy)
├── scripts/
│   ├── 01-setup-replication.sh # Primary: Create replication user/slot
│   └── setup-replica.sh        # Replica: Initialize from primary
└── POSTGRESQL_HA_SETUP.md      # This file
```

### Configuration Highlights

#### postgresql.conf (Primary)

```conf
# Connection & Performance
max_connections = 300
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 20MB

# Replication
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
hot_standby = on

# Security
ssl = on
ssl_min_protocol_version = 'TLSv1.3'
password_encryption = scram-sha-256

# Monitoring
shared_preload_libraries = 'pg_stat_statements,auto_explain'
```

#### pg_hba.conf (Security)

```conf
# SSL required for all remote connections
hostssl replication     replicator      172.16.0.0/12   scram-sha-256
hostssl all             sahool          172.16.0.0/12   scram-sha-256
host    all             all             all             reject  # Deny non-SSL
```

---

## ✅ Prerequisites

### 1. Environment Variables

Create/update `.env` file with:

```bash
# Database credentials
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=sahool

# Replication credentials
POSTGRES_REPLICATION_USER=replicator
POSTGRES_REPLICATION_PASSWORD=<strong_replication_password>

# Volume paths (optional)
POSTGRES_DATA_PATH=./data/postgres
POSTGRES_REPLICA_DATA_PATH=./data/postgres-replica
POSTGRES_WAL_PATH=./data/postgres-wal
POSTGRES_LOGS_PATH=./logs/postgres
POSTGRES_REPLICA_LOGS_PATH=./logs/postgres-replica
```

### 2. Create Data Directories

```bash
# Create directories for volumes
mkdir -p data/postgres data/postgres-replica data/postgres-wal
mkdir -p logs/postgres logs/postgres-replica

# Set permissions (if needed)
chmod 700 data/postgres data/postgres-replica
```

### 3. TLS Certificates

Generate or copy TLS certificates to `config/certs/postgres/`:

```bash
# Generate self-signed certificates (development)
cd config/certs/postgres
openssl req -new -x509 -days 365 -nodes -text \
  -out server.crt \
  -keyout server.key \
  -subj "/CN=postgres"

# Set permissions
chmod 600 server.key
chmod 644 server.crt

# Copy CA certificate (or use server.crt as CA)
cp server.crt ca.crt
```

**Production**: Use certificates from your CA or Let's Encrypt.

---

## 🚀 Deployment Guide

### Option 1: Standard Deployment (Single Instance)

For development or non-HA environments:

```bash
# Use base docker-compose.yml
docker-compose up -d postgres pgbouncer
```

### Option 2: High Availability Deployment (Recommended for Production)

For production with replication:

```bash
# 1. Start primary and replica
docker-compose -f docker-compose.yml -f docker-compose.ha.yml up -d postgres postgres-replica

# 2. Wait for initialization (check logs)
docker logs -f sahool-postgres-primary

# 3. Verify replication status
docker exec -it sahool-postgres-primary psql -U sahool -c "SELECT * FROM pg_stat_replication;"

# 4. Start PgBouncer and other services
docker-compose -f docker-compose.yml -f docker-compose.ha.yml up -d
```

### Step-by-Step First-Time Setup

#### Step 1: Initialize Primary Database

```bash
# Start only the primary database
docker-compose -f docker-compose.yml -f docker-compose.ha.yml up -d postgres

# Wait for initialization
docker logs -f sahool-postgres-primary

# Verify primary is running
docker exec -it sahool-postgres-primary pg_isready -U sahool
```

#### Step 2: Create Replication User (Automated)

The initialization script automatically creates:
- Replication user with REPLICATION privilege
- Physical replication slot named `replica_slot`
- Performance monitoring extensions

Verify:

```bash
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT rolname, rolreplication FROM pg_roles WHERE rolname = 'replicator';
"

docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT slot_name, slot_type, active FROM pg_replication_slots;
"
```

#### Step 3: Start Replica

```bash
# Start replica (will auto-initialize from primary)
docker-compose -f docker-compose.yml -f docker-compose.ha.yml up -d postgres-replica

# Monitor replica initialization
docker logs -f sahool-postgres-replica

# Wait for "database system is ready to accept read-only connections"
```

#### Step 4: Verify Replication

```bash
# Check replication status on primary
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT application_name, client_addr, state, sync_state,
       pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS send_lag,
       pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replay_lag
FROM pg_stat_replication;
"

# Expected output:
# application_name | client_addr | state     | sync_state | send_lag | replay_lag
# postgres-replica | 172.x.x.x   | streaming | async      | 0        | 0

# Check replica is in recovery mode
docker exec -it sahool-postgres-replica psql -U sahool -c "
SELECT pg_is_in_recovery();
"
# Expected: t (true)
```

#### Step 5: Start Remaining Services

```bash
# Start all services
docker-compose -f docker-compose.yml -f docker-compose.ha.yml up -d

# Verify all services are running
docker-compose ps
```

---

## 📊 Monitoring & Maintenance

### Health Checks

#### Check Primary Status

```bash
# Connection test
docker exec -it sahool-postgres-primary pg_isready -U sahool

# Database info
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT version();
SELECT pg_size_pretty(pg_database_size('sahool'));
"

# Active connections
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT count(*) as connections,
       max_conn.setting::int as max_connections,
       round((count(*) / max_conn.setting::numeric) * 100, 2) as pct_used
FROM pg_stat_activity, pg_settings max_conn
WHERE max_conn.name = 'max_connections';
"
```

#### Check Replication Status

```bash
# Replication lag
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT application_name,
       state,
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS lag_human
FROM pg_stat_replication;
"

# WAL archiving status
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT archived_count, failed_count, last_archived_time
FROM pg_stat_archiver;
"
```

#### PgBouncer Status

```bash
# Connect to PgBouncer admin console
docker exec -it sahool-pgbouncer psql -h localhost -p 6432 -U pgbouncer_admin pgbouncer

# Show pool status
SHOW POOLS;

# Show client connections
SHOW CLIENTS;

# Show server connections
SHOW SERVERS;

# Show statistics
SHOW STATS;
```

### Performance Monitoring

#### Slow Query Analysis

```bash
# Top 10 slowest queries
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT query,
       calls,
       round(total_exec_time::numeric, 2) as total_time_ms,
       round(mean_exec_time::numeric, 2) as avg_time_ms,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
"
```

#### Cache Hit Ratio

```bash
# Should be > 99%
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT sum(blks_hit)::float / (sum(blks_hit) + sum(blks_read)) * 100 AS cache_hit_ratio
FROM pg_stat_database;
"
```

#### Index Usage

```bash
# Find unused indexes
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 10;
"
```

### Regular Maintenance

#### Vacuum Statistics

```bash
# Check vacuum stats
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT schemaname, tablename,
       last_vacuum, last_autovacuum,
       n_dead_tup, n_live_tup,
       round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
"
```

#### Manual Vacuum (if needed)

```bash
# Vacuum specific table
docker exec -it sahool-postgres-primary psql -U sahool -c "
VACUUM VERBOSE ANALYZE table_name;
"

# Full vacuum (requires downtime)
docker exec -it sahool-postgres-primary psql -U sahool -c "
VACUUM FULL;
"
```

---

## 🔧 Troubleshooting

### Replica Not Connecting

**Symptoms**: Replica container starts but doesn't show in `pg_stat_replication`

**Solutions**:

```bash
# 1. Check replica logs
docker logs sahool-postgres-replica

# 2. Verify replication user exists on primary
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT rolname FROM pg_roles WHERE rolname = 'replicator';
"

# 3. Check pg_hba.conf allows replication connections
docker exec -it sahool-postgres-primary cat /etc/postgresql/pg_hba.conf | grep replication

# 4. Test connection from replica to primary
docker exec -it sahool-postgres-replica pg_isready -h postgres-primary -U replicator

# 5. Verify replication slot exists
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT * FROM pg_replication_slots;
"
```

### High Replication Lag

**Symptoms**: `replay_lag` > 10MB or increasing

**Solutions**:

```bash
# 1. Check primary load
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
"

# 2. Check network between primary and replica
docker exec -it sahool-postgres-replica ping postgres-primary

# 3. Check replica resource usage
docker stats sahool-postgres-replica

# 4. Increase replica resources in docker-compose.ha.yml
# memory: 4G -> 8G
# cpus: '2.0' -> '4.0'
```

### Connection Pool Exhaustion

**Symptoms**: "connection pool exhausted" errors

**Solutions**:

```bash
# 1. Check current connections
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
"

# 2. Check PgBouncer pool status
docker exec -it sahool-pgbouncer psql -h localhost -p 6432 -U pgbouncer_admin pgbouncer -c "SHOW POOLS;"

# 3. Increase connection limits (already done in this config)
# - max_connections: 300 (postgresql.conf)
# - max_db_connections: 250 (pgbouncer.ini)

# 4. Kill idle connections (if needed)
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND state_change < now() - interval '30 minutes';
"
```

### TLS/SSL Connection Issues

**Symptoms**: "SSL connection required" errors

**Solutions**:

```bash
# 1. Verify certificates exist
docker exec -it sahool-postgres-primary ls -la /var/lib/postgresql/certs/

# 2. Check SSL is enabled
docker exec -it sahool-postgres-primary psql -U sahool -c "SHOW ssl;"

# 3. Test SSL connection
docker exec -it sahool-postgres-primary psql "sslmode=require host=localhost user=sahool dbname=sahool"

# 4. For development, temporarily disable SSL enforcement
# Edit pg_hba.conf: change "hostssl" to "host"
# Edit pgbouncer.ini: change "require" to "prefer"
```

---

## ⚡ Performance Tuning

### Resource Allocation Guidelines

| Component | Development | Production | High-Load |
|-----------|-------------|------------|-----------|
| Primary CPU | 2 cores | 4 cores | 8+ cores |
| Primary RAM | 2GB | 8GB | 16GB+ |
| Replica CPU | 1 core | 2 cores | 4+ cores |
| Replica RAM | 1GB | 4GB | 8GB+ |
| Storage | 20GB | 500GB | 1TB+ |

### Memory Settings (postgresql.conf)

```conf
# For 8GB RAM system
shared_buffers = 2GB              # 25% of RAM
effective_cache_size = 6GB        # 75% of RAM
maintenance_work_mem = 512MB      # For maintenance ops
work_mem = 20MB                   # Per operation

# For 16GB RAM system
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 32MB
```

### Connection Tuning

```conf
# Adjust based on workload
max_connections = 300             # Total connections
max_db_connections = 250          # PgBouncer connections
default_pool_size = 30            # Per database/user
```

### Query Optimization

```sql
-- Enable query timing
\timing

-- Analyze query plan
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

-- Update statistics
ANALYZE table_name;

-- Reindex if needed
REINDEX TABLE table_name;
```

---

## 🔒 Security Considerations

### Production Checklist

- ✅ TLS 1.3 enforced for all connections
- ✅ SCRAM-SHA-256 password encryption
- ✅ Strong passwords for all users
- ✅ Network isolation (Docker networks)
- ✅ Port binding to localhost (127.0.0.1)
- ✅ No-new-privileges security option
- ✅ Read-only mounts for configs
- ⚠️ Certificate validation (self-signed for dev)
- ⚠️ Row-level security (implement per requirements)
- ⚠️ Audit logging (pgaudit recommended)

### Security Hardening

```sql
-- Enable row-level security
ALTER TABLE sensitive_table ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY tenant_isolation ON fields
FOR ALL TO PUBLIC
USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Audit user activity
SELECT * FROM pg_stat_activity WHERE usename != 'postgres';
```

### Firewall Rules (if applicable)

```bash
# Allow only specific IPs to PostgreSQL port
iptables -A INPUT -p tcp --dport 5432 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 5432 -j DROP
```

---

## 💾 Backup & Recovery

### WAL Archiving (Already Configured)

WAL files are automatically archived to `/var/lib/postgresql/wal_archive/`

```bash
# Check archive status
docker exec -it sahool-postgres-primary psql -U sahool -c "
SELECT * FROM pg_stat_archiver;
"

# List archived WAL files
docker exec -it sahool-postgres-primary ls -lh /var/lib/postgresql/wal_archive/
```

### Manual Backup

#### Using pg_dump

```bash
# Backup entire database
docker exec -it sahool-postgres-primary pg_dump -U sahool sahool > backup_$(date +%Y%m%d).sql

# Backup with compression
docker exec -it sahool-postgres-primary pg_dump -U sahool -Fc sahool > backup_$(date +%Y%m%d).dump

# Backup specific schema
docker exec -it sahool-postgres-primary pg_dump -U sahool -n public sahool > backup_public.sql
```

#### Using pg_basebackup

```bash
# Physical backup (entire cluster)
docker exec -it sahool-postgres-primary pg_basebackup -U sahool -D /backups/base_$(date +%Y%m%d) -Ft -z -P
```

### Restore

#### From pg_dump

```bash
# Restore SQL dump
docker exec -i sahool-postgres-primary psql -U sahool sahool < backup_20260106.sql

# Restore custom format
docker exec -i sahool-postgres-primary pg_restore -U sahool -d sahool backup_20260106.dump
```

#### Point-in-Time Recovery (PITR)

```bash
# 1. Stop replica
docker stop sahool-postgres-replica

# 2. Create recovery.signal file
docker exec -it sahool-postgres-replica touch /var/lib/postgresql/data/recovery.signal

# 3. Configure recovery target
docker exec -it sahool-postgres-replica bash -c "cat >> /var/lib/postgresql/data/postgresql.auto.conf <<EOF
recovery_target_time = '2026-01-06 14:30:00'
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
EOF"

# 4. Start recovery
docker start sahool-postgres-replica
```

### Automated Backup Script

```bash
#!/bin/bash
# backup-postgres.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
docker exec sahool-postgres-primary pg_dump -U sahool -Fc sahool > "$BACKUP_DIR/sahool_$DATE.dump"

# Compress WAL archive
tar -czf "$BACKUP_DIR/wal_archive_$DATE.tar.gz" -C /home/user/sahool-unified-v15-idp/data postgres-wal/

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR" -name "*.dump" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/sahool_$DATE.dump"
```

### Backup Schedule (Cron)

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup-postgres.sh

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /path/to/backup-postgres-full.sh
```

---

## 🚨 Failover Procedure

### Manual Failover (Promote Replica to Primary)

#### Step 1: Assess Primary Status

```bash
# Check if primary is truly down
docker exec -it sahool-postgres-primary pg_isready -U sahool

# If primary is recoverable, prefer to fix it
```

#### Step 2: Promote Replica

```bash
# Promote replica to primary
docker exec -it sahool-postgres-replica pg_ctl promote

# Or use SQL
docker exec -it sahool-postgres-replica psql -U sahool -c "SELECT pg_promote();"

# Wait for promotion
docker logs -f sahool-postgres-replica
# Look for: "database system is ready to accept connections"
```

#### Step 3: Update Application Connections

```bash
# Option 1: Update PgBouncer configuration
# Edit pgbouncer.ini to point to new primary:
# sahool = host=postgres-replica port=5432 dbname=sahool

# Option 2: Update DNS/service discovery
# Point 'postgres' hostname to replica container

# Option 3: Restart services with new DATABASE_URL
# DATABASE_URL=postgresql://sahool:password@postgres-replica:5432/sahool
```

#### Step 4: Verify New Primary

```bash
# Check it's no longer in recovery
docker exec -it sahool-postgres-replica psql -U sahool -c "SELECT pg_is_in_recovery();"
# Expected: f (false)

# Check write capability
docker exec -it sahool-postgres-replica psql -U sahool -c "CREATE TABLE failover_test (id INT);"
docker exec -it sahool-postgres-replica psql -U sahool -c "DROP TABLE failover_test;"
```

#### Step 5: Rebuild Old Primary as New Replica

```bash
# Stop old primary
docker stop sahool-postgres-primary

# Clear data directory
docker run --rm -v postgres_data:/data alpine rm -rf /data/*

# Reconfigure as replica and restart
# (Follow replica setup steps)
```

---

## 📚 Additional Resources

### Documentation

- [PostgreSQL 16 Official Documentation](https://www.postgresql.org/docs/16/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [PgBouncer Documentation](https://www.pgbouncer.org/config.html)
- [PostgreSQL Replication Tutorial](https://www.postgresql.org/docs/16/warm-standby.html)

### Monitoring Tools

- **pgAdmin**: Web-based PostgreSQL administration
- **pgBadger**: PostgreSQL log analyzer
- **pg_activity**: Top-like activity monitor
- **Patroni**: HA solution with automatic failover
- **pg_auto_failover**: Automatic failover solution

### Performance Tools

- **pg_stat_statements**: Query performance tracking (enabled)
- **pgbench**: Benchmarking tool
- **explain.depesz.com**: Visual EXPLAIN analyzer

---

## 📞 Support

For issues or questions:

1. Check logs: `docker logs sahool-postgres-primary`
2. Review this documentation
3. Consult PostgreSQL audit report: `/tests/database/POSTGRESQL_AUDIT.md`
4. Contact platform engineering team

---

## 📝 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-06 | 1.0 | Initial HA configuration based on audit findings |

---

**Status**: ✅ Production Ready (with TLS certificates)

**Next Steps**:
1. Generate/install production TLS certificates
2. Test failover procedure in staging environment
3. Set up automated backup schedule
4. Implement monitoring dashboards
5. Configure alerting for replication lag

