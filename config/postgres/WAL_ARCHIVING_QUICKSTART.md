# PostgreSQL WAL Archiving Quick Start Guide

## Overview

Quick setup guide for enabling PostgreSQL WAL archiving to S3/MinIO for disaster recovery.

## Prerequisites

- Docker and Docker Compose installed
- MinIO or AWS S3 configured
- 15 minutes setup time

## Quick Setup (5 Steps)

### Step 1: Update Environment Variables

Edit `.env` file and configure:

```bash
# S3/MinIO credentials (if not already configured)
MINIO_ROOT_USER=your_minio_user
MINIO_ROOT_PASSWORD=your_secure_password

# WAL-G configuration
WALG_S3_PREFIX=s3://sahool-wal-archive/pg-primary
AWS_ENDPOINT=http://minio:9000  # Or your AWS S3 endpoint
AWS_ACCESS_KEY_ID=${MINIO_ROOT_USER}
AWS_SECRET_ACCESS_KEY=${MINIO_ROOT_PASSWORD}
AWS_REGION=us-east-1
```

### Step 2: Deploy PostgreSQL with WAL-G

```bash
# Option A: Using docker-compose overlay (recommended)
docker-compose -f docker-compose.yml -f docker-compose.walg.yml up -d postgres

# Option B: Build and deploy custom image
cd config/postgres
docker build -f Dockerfile.walg -t sahool/postgres-walg:16-3.4 .
cd ../..
# Then update docker-compose.yml to use sahool/postgres-walg:16-3.4
docker-compose up -d postgres
```

### Step 3: Initialize WAL-G

```bash
# Run initialization script
./config/postgres/scripts/init-walg.sh

# This will:
# - Validate configuration
# - Create S3 bucket
# - Test connectivity
```

### Step 4: Create Initial Backup

```bash
# Create first base backup
docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data

# Wait for completion (check logs)
docker-compose exec postgres tail -f /var/log/postgresql/wal-archive.log
```

### Step 5: Verify Setup

```bash
# List backups
docker-compose exec postgres wal-g backup-list

# Check WAL archiving status
docker-compose exec postgres psql -U sahool -c "SELECT * FROM pg_stat_archiver;"

# Check logs
docker-compose exec postgres tail -20 /var/log/postgresql/wal-archive.log
```

## Verification Checklist

- [ ] WAL-G installed in PostgreSQL container
- [ ] S3 bucket created and accessible
- [ ] First base backup completed successfully
- [ ] WAL archiving active (check pg_stat_archiver)
- [ ] Archive logs show successful WAL pushes

## Next Steps

1. **Schedule automated backups** - Set up cron job for daily backups
2. **Configure monitoring** - Set up alerts for failed archives
3. **Test recovery** - Perform test restore in isolated environment
4. **Document procedures** - Update runbooks with recovery steps

## Daily Operations

### Create Backup

```bash
# Full backup
docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data
```

### List Backups

```bash
docker-compose exec postgres wal-g backup-list
```

### Delete Old Backups

```bash
# Keep last 7 backups
docker-compose exec postgres wal-g delete retain 7
```

### Monitor WAL Archiving

```bash
# Check archiver status
docker-compose exec postgres psql -U sahool -c "
SELECT
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count
FROM pg_stat_archiver;
"

# View archive logs
docker-compose exec postgres tail -f /var/log/postgresql/wal-archive.log
```

## Troubleshooting

### WAL Archiving Not Working

```bash
# Check archive command
docker-compose exec postgres psql -U sahool -c "SHOW archive_command;"

# Check S3 connectivity
docker-compose exec postgres wal-g backup-list

# Check logs for errors
docker-compose exec postgres tail -50 /var/log/postgresql/wal-archive.log
```

### Backup Failed

```bash
# Check available disk space
docker-compose exec postgres df -h

# Check S3 bucket permissions
docker-compose exec postgres aws s3 ls s3://sahool-wal-archive/ --endpoint-url http://minio:9000

# Verify environment variables
docker-compose exec postgres env | grep -E "WALG|AWS"
```

## Recovery Example

Quick recovery to latest state:

```bash
# 1. Stop PostgreSQL
docker-compose stop postgres

# 2. Clear data directory
docker run --rm -v sahool-unified-v15-idp_postgres_data:/data alpine rm -rf /data/*

# 3. Restore backup
docker-compose run --rm postgres wal-g backup-fetch /var/lib/postgresql/data LATEST

# 4. Create recovery signal
docker-compose run --rm postgres touch /var/lib/postgresql/data/recovery.signal

# 5. Configure recovery
docker-compose run --rm postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = '/usr/local/bin/wal-restore.sh %f %p'
recovery_target_timeline = 'latest'
EOF"

# 6. Start PostgreSQL
docker-compose up -d postgres

# 7. Monitor recovery
docker-compose logs -f postgres
```

For complete recovery procedures, see [PITR_RECOVERY.md](./PITR_RECOVERY.md)

## Resources

- [Complete PITR Guide](./PITR_RECOVERY.md)
- [WAL-G Documentation](https://github.com/wal-g/wal-g)
- [PostgreSQL Archiving](https://www.postgresql.org/docs/16/continuous-archiving.html)

## Support

For issues or questions:

- Check logs: `docker-compose logs postgres`
- Review documentation: `config/postgres/PITR_RECOVERY.md`
- Contact: devops@sahool.com
