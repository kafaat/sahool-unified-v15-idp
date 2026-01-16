# PostgreSQL Point-in-Time Recovery (PITR) with WAL-G

## Overview

This document provides comprehensive instructions for setting up and performing Point-in-Time Recovery (PITR) for PostgreSQL using WAL-G with S3/MinIO storage.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Creating Backups](#creating-backups)
- [Point-in-Time Recovery](#point-in-time-recovery)
- [Disaster Recovery Procedures](#disaster-recovery-procedures)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Architecture

### Components

1. **PostgreSQL 16 with PostGIS** - Primary database server
2. **WAL-G** - Continuous archiving tool for PostgreSQL
3. **MinIO/S3** - S3-compatible object storage for WAL archives and base backups
4. **Archive Scripts** - Custom scripts for WAL archiving and restoration

### Data Flow

```
PostgreSQL --> WAL Files --> wal-archive.sh --> WAL-G --> S3/MinIO
                                             |
                                             v
                                    Local WAL Archive (Fast Recovery)
```

### Recovery Flow

```
S3/MinIO --> WAL-G --> wal-restore.sh --> PostgreSQL Recovery Mode
    |
    v
Local WAL Archive (if available)
```

## Prerequisites

### Required Services

- PostgreSQL 16 with PostGIS (running in Docker)
- MinIO or AWS S3 (for object storage)
- Docker and Docker Compose

### Required Tools

- `wal-g` - Installed in PostgreSQL container
- `aws` CLI - Installed in PostgreSQL container (fallback method)
- `bash` - For running scripts

### Required Credentials

Configure in `.env` file:

```bash
# MinIO/S3 Credentials
MINIO_ROOT_USER=sahool_minio_admin
MINIO_ROOT_PASSWORD=<secure-password>

# WAL-G Configuration
WALG_S3_PREFIX=s3://sahool-wal-archive/pg-primary
AWS_ENDPOINT=http://minio:9000
AWS_ACCESS_KEY_ID=${MINIO_ROOT_USER}
AWS_SECRET_ACCESS_KEY=${MINIO_ROOT_PASSWORD}
AWS_REGION=us-east-1
```

## Initial Setup

### Step 1: Deploy PostgreSQL with WAL-G Support

```bash
# Using the WAL-G overlay
docker-compose -f docker-compose.yml -f docker-compose.walg.yml up -d postgres
```

Or build custom image:

```bash
cd config/postgres
docker build -f Dockerfile.walg -t sahool/postgres-walg:16-3.4 .
```

### Step 2: Initialize WAL-G and Create S3 Bucket

```bash
# Run initialization script
./config/postgres/scripts/init-walg.sh
```

This script will:

- Validate WAL-G configuration
- Create S3 bucket if it doesn't exist
- Enable bucket versioning
- Set up lifecycle policies for old WAL files
- Test WAL-G connection to S3

### Step 3: Verify PostgreSQL Configuration

Check that WAL archiving is enabled:

```bash
docker-compose exec postgres psql -U sahool -c "SHOW archive_mode;"
docker-compose exec postgres psql -U sahool -c "SHOW archive_command;"
docker-compose exec postgres psql -U sahool -c "SHOW wal_level;"
```

Expected output:

```
archive_mode | on
archive_command | /usr/local/bin/wal-archive.sh %p %f
wal_level | replica
```

### Step 4: Create Initial Base Backup

```bash
# Create first base backup
docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data

# Wait for backup to complete (may take several minutes)
# Monitor progress:
docker-compose exec postgres tail -f /var/log/postgresql/wal-archive.log
```

### Step 5: Verify Backup

```bash
# List all backups
docker-compose exec postgres wal-g backup-list

# Example output:
# name                          modified             wal_segment_backup_start
# base_000000010000000000000002 2024-01-08T10:30:00Z 000000010000000000000002
```

## Creating Backups

### Full Base Backup

Full backups capture the entire database state at a specific point in time.

```bash
# Create full backup
docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data

# Verify backup completed
docker-compose exec postgres wal-g backup-list
```

**Recommended Schedule:** Daily at off-peak hours (e.g., 2 AM)

### Delta Backup (Incremental)

Delta backups only store changes since the last backup, saving storage space.

```bash
# Create delta backup (automatically incremental)
docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data

# WAL-G automatically uses delta if WALG_DELTA_MAX_STEPS > 0
```

**Recommended Schedule:** Every 6 hours

### Continuous WAL Archiving

WAL archiving happens automatically via `archive_command`. Monitor it with:

```bash
# Check WAL archiving status
docker-compose exec postgres psql -U sahool -c "SELECT * FROM pg_stat_archiver;"

# Check archive logs
docker-compose exec postgres tail -f /var/log/postgresql/wal-archive.log
```

### Backup Retention Management

Remove old backups to save storage:

```bash
# Delete backups older than the last 7 base backups
docker-compose exec postgres wal-g delete retain 7

# OR: Delete backups older than 30 days
docker-compose exec postgres wal-g delete before FIND_FULL "2024-01-01T00:00:00Z"

# Delete all backups except the latest
docker-compose exec postgres wal-g delete everything FORCE --confirm
```

## Point-in-Time Recovery

### Recovery Scenarios

1. **Latest State Recovery** - Restore to the most recent transaction
2. **Specific Time Recovery** - Restore to exact timestamp
3. **Specific Transaction Recovery** - Restore to transaction ID
4. **Named Restore Point Recovery** - Restore to labeled point

### Preparation Steps

1. **Stop all applications** accessing the database
2. **Stop PostgreSQL** service
3. **Backup current data** (if possible)
4. **Clear data directory**

```bash
# Stop PostgreSQL
docker-compose stop postgres

# Backup current data directory (if accessible)
docker run --rm -v sahool-unified-v15-idp_postgres_data:/source -v $(pwd)/emergency-backup:/backup alpine tar czf /backup/postgres-emergency-$(date +%Y%m%d-%H%M%S).tar.gz -C /source .

# Clear data directory
docker run --rm -v sahool-unified-v15-idp_postgres_data:/data alpine sh -c "rm -rf /data/*"
```

### Recovery to Latest State

Restore to the most recent committed transaction:

```bash
# 1. Restore base backup
docker-compose run --rm postgres wal-g backup-fetch /var/lib/postgresql/data LATEST

# 2. Create recovery signal file
docker-compose run --rm postgres touch /var/lib/postgresql/data/recovery.signal

# 3. Configure recovery settings
docker-compose run --rm postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = '/usr/local/bin/wal-restore.sh %f %p'
recovery_target_timeline = 'latest'
EOF"

# 4. Start PostgreSQL (recovery will begin automatically)
docker-compose up -d postgres

# 5. Monitor recovery progress
docker-compose logs -f postgres
docker-compose exec postgres tail -f /var/log/postgresql/wal-restore.log

# 6. Check recovery status
docker-compose exec postgres psql -U sahool -c "SELECT pg_is_in_recovery();"

# When recovery completes (pg_is_in_recovery returns false), verify data
```

### Recovery to Specific Timestamp

Restore database to exact point in time:

```bash
# 1. Restore base backup
docker-compose run --rm postgres wal-g backup-fetch /var/lib/postgresql/data LATEST

# 2. Create recovery configuration
TARGET_TIME="2024-01-08 14:30:00+00"

docker-compose run --rm postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = '/usr/local/bin/wal-restore.sh %f %p'
recovery_target_time = '${TARGET_TIME}'
recovery_target_action = 'promote'
EOF"

# 3. Create recovery signal
docker-compose run --rm postgres touch /var/lib/postgresql/data/recovery.signal

# 4. Start PostgreSQL
docker-compose up -d postgres

# 5. Monitor recovery
docker-compose logs -f postgres
```

### Recovery to Specific Transaction ID

Restore to exact transaction:

```bash
# 1. Restore base backup
docker-compose run --rm postgres wal-g backup-fetch /var/lib/postgresql/data LATEST

# 2. Configure recovery to transaction ID
TARGET_XID="1234567"

docker-compose run --rm postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = '/usr/local/bin/wal-restore.sh %f %p'
recovery_target_xid = '${TARGET_XID}'
recovery_target_action = 'promote'
EOF"

# 3. Create recovery signal
docker-compose run --rm postgres touch /var/lib/postgresql/data/recovery.signal

# 4. Start PostgreSQL
docker-compose up -d postgres
```

### Recovery to Named Restore Point

First, create named restore points in normal operation:

```sql
-- Create a named restore point
SELECT pg_create_restore_point('before_major_update');
```

Then restore to that point:

```bash
# 1. Restore base backup
docker-compose run --rm postgres wal-g backup-fetch /var/lib/postgresql/data LATEST

# 2. Configure recovery
docker-compose run --rm postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = '/usr/local/bin/wal-restore.sh %f %p'
recovery_target_name = 'before_major_update'
recovery_target_action = 'promote'
EOF"

# 3. Create recovery signal and start
docker-compose run --rm postgres touch /var/lib/postgresql/data/recovery.signal
docker-compose up -d postgres
```

## Disaster Recovery Procedures

### Complete Site Failure

When primary site is completely unavailable:

#### 1. Prepare New Environment

```bash
# Clone repository to new server
git clone https://github.com/your-org/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp

# Copy .env configuration (from secure backup location)
cp /secure-backup/.env .env

# Verify S3/MinIO access
./config/postgres/scripts/init-walg.sh
```

#### 2. List Available Backups

```bash
# List all available backups from S3
docker-compose run --rm -e WALG_S3_PREFIX=s3://sahool-wal-archive/pg-primary \
  postgres wal-g backup-list
```

#### 3. Restore Database

```bash
# Clear any existing data
docker volume rm sahool-unified-v15-idp_postgres_data || true

# Create fresh volume
docker volume create sahool-unified-v15-idp_postgres_data

# Restore backup
docker-compose run --rm postgres wal-g backup-fetch /var/lib/postgresql/data LATEST

# Configure for recovery
docker-compose run --rm postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = '/usr/local/bin/wal-restore.sh %f %p'
recovery_target_timeline = 'latest'
EOF"

docker-compose run --rm postgres touch /var/lib/postgresql/data/recovery.signal

# Start services
docker-compose -f docker-compose.yml -f docker-compose.walg.yml up -d
```

#### 4. Verify Recovery

```bash
# Wait for recovery to complete
docker-compose logs -f postgres | grep -i "recovery"

# Check database is accessible
docker-compose exec postgres psql -U sahool -c "\l"

# Verify data integrity
docker-compose exec postgres psql -U sahool -d sahool -c "SELECT COUNT(*) FROM users;"

# Check replication status (if applicable)
docker-compose exec postgres psql -U sahool -c "SELECT * FROM pg_stat_replication;"
```

### Database Corruption Recovery

If database is corrupted but WAL archives are intact:

```bash
# 1. Stop PostgreSQL
docker-compose stop postgres

# 2. Rename corrupted data directory
docker run --rm -v sahool-unified-v15-idp_postgres_data:/data alpine mv /data /data.corrupted

# 3. Restore from backup
docker-compose run --rm postgres wal-g backup-fetch /var/lib/postgresql/data LATEST

# 4. Configure recovery
docker-compose run --rm postgres touch /var/lib/postgresql/data/recovery.signal
docker-compose run --rm postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = '/usr/local/bin/wal-restore.sh %f %p'
recovery_target_timeline = 'latest'
EOF"

# 5. Start recovery
docker-compose up -d postgres
```

## Monitoring and Maintenance

### Health Checks

#### WAL Archiving Status

```bash
# Check archiver process status
docker-compose exec postgres psql -U sahool -c "
SELECT
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count,
    last_failed_wal,
    last_failed_time
FROM pg_stat_archiver;
"
```

#### Backup Status

```bash
# List recent backups
docker-compose exec postgres wal-g backup-list

# Check backup integrity
docker-compose exec postgres wal-g backup-show LATEST
```

#### Storage Usage

```bash
# Check S3 bucket size
docker-compose exec postgres aws s3 ls s3://sahool-wal-archive/ --recursive \
  --endpoint-url http://minio:9000 --summarize --human-readable
```

### Automated Monitoring Script

Create monitoring script `/usr/local/bin/monitor-walg.sh`:

```bash
#!/bin/bash
# WAL-G Health Monitoring Script

# Check last archive time
LAST_ARCHIVE=$(docker-compose exec -T postgres psql -U sahool -t -c \
  "SELECT EXTRACT(EPOCH FROM (NOW() - last_archived_time)) FROM pg_stat_archiver;")

# Alert if no archive in last 2 hours
if (( $(echo "$LAST_ARCHIVE > 7200" | bc -l) )); then
    echo "ALERT: No WAL archived in last 2 hours!" | \
      mail -s "WAL Archive Alert" admin@sahool.com
fi

# Check backup age
BACKUP_AGE=$(docker-compose exec -T postgres wal-g backup-list | \
  tail -1 | awk '{print $2}')

# Alert if no backup in last 24 hours
BACKUP_SECONDS=$(( $(date +%s) - $(date -d "$BACKUP_AGE" +%s) ))
if [ $BACKUP_SECONDS -gt 86400 ]; then
    echo "ALERT: No backup in last 24 hours!" | \
      mail -s "Backup Alert" admin@sahool.com
fi
```

Schedule with cron:

```bash
# Add to crontab
*/30 * * * * /usr/local/bin/monitor-walg.sh
```

### Maintenance Tasks

#### Weekly Tasks

```bash
# 1. Verify backup integrity
docker-compose exec postgres wal-g backup-list

# 2. Check WAL archive storage
docker-compose exec postgres aws s3 ls s3://sahool-wal-archive/ \
  --endpoint-url http://minio:9000 --recursive --summarize

# 3. Review PostgreSQL logs
docker-compose exec postgres tail -100 /var/log/postgresql/wal-archive.log
```

#### Monthly Tasks

```bash
# 1. Perform test restore (in isolated environment)
./scripts/test-restore.sh

# 2. Clean up old backups
docker-compose exec postgres wal-g delete retain 30

# 3. Verify S3 bucket versioning
docker-compose exec postgres aws s3api get-bucket-versioning \
  --bucket sahool-wal-archive --endpoint-url http://minio:9000
```

#### Quarterly Tasks

```bash
# 1. Full disaster recovery drill
./scripts/dr-drill.sh

# 2. Review and update recovery procedures
vim config/postgres/PITR_RECOVERY.md

# 3. Test recovery to specific point in time
./scripts/test-pitr.sh "2024-01-01 00:00:00"
```

## Troubleshooting

### Common Issues

#### Issue: WAL Archiving Fails

**Symptoms:**

```
ERROR: could not archive WAL file
failed_count increasing in pg_stat_archiver
```

**Diagnosis:**

```bash
# Check archive logs
docker-compose exec postgres tail -50 /var/log/postgresql/wal-archive.log

# Test S3 connectivity
docker-compose exec postgres wal-g backup-list

# Check S3 credentials
docker-compose exec postgres env | grep AWS
```

**Solutions:**

1. Verify S3 credentials in `.env`
2. Check S3 endpoint is accessible
3. Ensure S3 bucket exists and has write permissions
4. Check disk space on PostgreSQL container

#### Issue: WAL Restore Fails During Recovery

**Symptoms:**

```
FATAL: could not restore WAL segment
WARNING: wal-restore.sh returned exit code 1
```

**Diagnosis:**

```bash
# Check restore logs
docker-compose logs postgres | grep -i restore

# Test WAL restoration manually
docker-compose exec postgres /usr/local/bin/wal-restore.sh 000000010000000000000010 /tmp/test.wal
```

**Solutions:**

1. Verify WAL files exist in S3
2. Check network connectivity to S3
3. Ensure correct WALG_S3_PREFIX
4. Try restoring specific WAL file manually

#### Issue: Backup Takes Too Long

**Symptoms:**

- Backup duration > 1 hour
- High CPU/memory usage during backup

**Solutions:**

```bash
# 1. Enable delta backups
# In .env:
WALG_DELTA_MAX_STEPS=6

# 2. Increase concurrency
WALG_UPLOAD_CONCURRENCY=8
WALG_UPLOAD_DISK_CONCURRENCY=4

# 3. Use faster compression
WALG_COMPRESSION_METHOD=lz4  # Faster than brotli

# 4. Check database size
docker-compose exec postgres psql -U sahool -c "
SELECT pg_size_pretty(pg_database_size('sahool'));
"
```

#### Issue: Out of Disk Space

**Symptoms:**

```
ERROR: could not extend file: No space left on device
```

**Solutions:**

```bash
# 1. Check disk usage
docker-compose exec postgres df -h

# 2. Clean up old WAL files
docker-compose exec postgres rm -f /var/lib/postgresql/wal_archive/*

# 3. Clean up old logs
docker-compose exec postgres find /var/log/postgresql -type f -mtime +7 -delete

# 4. Adjust WAL retention
# In postgresql.conf:
# min_wal_size = 1GB
# max_wal_size = 4GB
```

### Getting Help

For additional support:

1. Check PostgreSQL logs: `docker-compose logs postgres`
2. Check WAL-G logs: `docker-compose exec postgres tail -f /var/log/postgresql/wal-archive.log`
3. Review WAL-G documentation: https://github.com/wal-g/wal-g
4. Contact SAHOOL DevOps team: devops@sahool.com

## References

- [WAL-G Documentation](https://github.com/wal-g/wal-g/blob/master/README.md)
- [PostgreSQL PITR Documentation](https://www.postgresql.org/docs/16/continuous-archiving.html)
- [MinIO Documentation](https://docs.min.io/)
- [SAHOOL Backup Strategy](../../scripts/backup/README.md)

## Appendix

### Environment Variables Reference

| Variable                    | Description            | Default                              |
| --------------------------- | ---------------------- | ------------------------------------ |
| `WALG_S3_PREFIX`            | S3 path for backups    | `s3://sahool-wal-archive/pg-primary` |
| `AWS_ENDPOINT`              | S3 endpoint URL        | `http://minio:9000`                  |
| `AWS_ACCESS_KEY_ID`         | S3 access key          | `${MINIO_ROOT_USER}`                 |
| `AWS_SECRET_ACCESS_KEY`     | S3 secret key          | `${MINIO_ROOT_PASSWORD}`             |
| `AWS_REGION`                | S3 region              | `us-east-1`                          |
| `WALG_COMPRESSION_METHOD`   | Compression algorithm  | `brotli`                             |
| `WALG_DELTA_MAX_STEPS`      | Delta backup depth     | `6`                                  |
| `WALG_UPLOAD_CONCURRENCY`   | Upload threads         | `4`                                  |
| `WALG_DOWNLOAD_CONCURRENCY` | Download threads       | `4`                                  |
| `WALG_RETAIN_BACKUPS`       | Backup retention count | `7`                                  |

### Backup Size Estimates

Typical backup sizes for SAHOOL database:

| Database Size | Full Backup | Delta Backup | WAL per Day |
| ------------- | ----------- | ------------ | ----------- |
| 10 GB         | 3 GB        | 500 MB       | 2 GB        |
| 50 GB         | 15 GB       | 2 GB         | 10 GB       |
| 100 GB        | 30 GB       | 5 GB         | 20 GB       |

### Recovery Time Objectives

| Scenario                       | RTO (Recovery Time Objective) |
| ------------------------------ | ----------------------------- |
| Latest state recovery          | 15-30 minutes                 |
| Point-in-time recovery (< 24h) | 30-60 minutes                 |
| Point-in-time recovery (> 24h) | 1-4 hours                     |
| Complete site recovery         | 2-6 hours                     |
