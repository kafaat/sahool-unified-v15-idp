# PostgreSQL WAL Archiving to S3/MinIO - Configuration Summary

## Overview

This directory contains the complete configuration for PostgreSQL WAL (Write-Ahead Log) archiving to S3-compatible storage (MinIO or AWS S3) using WAL-G for disaster recovery and point-in-time recovery (PITR).

## What Has Been Configured

### 1. PostgreSQL Configuration

**File:** `/config/postgres/postgresql.conf` (lines 78-116)

- Enabled WAL archiving with `archive_mode = on`
- Configured `archive_command` to use WAL-G via custom script
- Set `archive_timeout = 1h` for maximum 1-hour data loss
- Added comprehensive documentation and configuration comments

### 2. WAL-G Scripts

#### Archive Script

**File:** `/config/postgres/scripts/wal-archive.sh`

Multi-tiered archiving strategy:

1. Primary: WAL-G to S3/MinIO
2. Fallback: AWS CLI to S3/MinIO
3. Emergency: Local filesystem only

Features:

- Comprehensive logging
- Error handling with fallback methods
- Local cache for quick recovery

#### Restore Script

**File:** `/config/postgres/scripts/wal-restore.sh`

Multi-source restore strategy:

1. Local archive (fastest)
2. WAL-G from S3/MinIO
3. AWS CLI from S3/MinIO

Features:

- Automatic caching to local archive
- Multiple S3 path attempts
- Comprehensive logging

#### Initialization Script

**File:** `/config/postgres/scripts/init-walg.sh`

Automated setup script that:

- Validates configuration
- Creates S3 bucket if needed
- Enables bucket versioning
- Sets lifecycle policies
- Tests WAL-G connectivity

#### Test Script

**File:** `/config/postgres/scripts/test-walg-setup.sh`

Comprehensive test suite that validates:

- PostgreSQL status
- WAL-G installation
- Configuration correctness
- S3/MinIO connectivity
- WAL archiving functionality

#### Maintenance Script

**File:** `/config/postgres/scripts/walg-maintenance.sh`

Maintenance operations:

- Create backups
- Clean up old backups
- Verify backup integrity
- Show detailed status

### 3. Docker Configuration

#### Custom Docker Image

**File:** `/config/postgres/Dockerfile.walg`

Custom PostgreSQL image with:

- PostgreSQL 16 + PostGIS 3.4
- WAL-G v2.0.1
- AWS CLI v2
- Pre-configured scripts

#### Docker Compose Override

**File:** `/docker-compose.walg.yml`

Overlay configuration that adds:

- WAL-G environment variables
- S3/MinIO connection settings
- Additional volumes for WAL archive
- Custom PostgreSQL configuration

Usage:

```bash
docker-compose -f docker-compose.yml -f docker-compose.walg.yml up -d
```

### 4. Kubernetes Configuration

**File:** `/config/postgres/k8s-walg-example.yaml`

Complete Kubernetes manifests including:

- StatefulSet for PostgreSQL with WAL-G
- Secrets for S3 credentials
- ConfigMaps for configuration
- PersistentVolumeClaims for data and WAL archive
- CronJobs for automated backups
- NetworkPolicy for security

### 5. Environment Configuration

**File:** `/.env.example` (lines 774-842)

Added comprehensive WAL-G configuration:

- `WALG_S3_PREFIX` - S3 bucket path
- `WALG_COMPRESSION_METHOD` - Compression algorithm
- `WALG_DELTA_MAX_STEPS` - Delta backup depth
- `WALG_UPLOAD_CONCURRENCY` - Upload performance
- `WALG_DOWNLOAD_CONCURRENCY` - Download performance
- `WALG_RETAIN_BACKUPS` - Retention policy
- Logging configuration

### 6. Documentation

#### Complete PITR Guide

**File:** `/config/postgres/PITR_RECOVERY.md`

Comprehensive 500+ line guide covering:

- Architecture and components
- Initial setup procedures
- Creating and managing backups
- Point-in-time recovery procedures
- Disaster recovery workflows
- Monitoring and maintenance
- Troubleshooting common issues

#### Quick Start Guide

**File:** `/config/postgres/WAL_ARCHIVING_QUICKSTART.md`

Quick 5-step setup guide:

1. Update environment variables
2. Deploy PostgreSQL with WAL-G
3. Initialize WAL-G
4. Create initial backup
5. Verify setup

## Quick Start

### Step 1: Configure Environment

Edit `.env` file:

```bash
# MinIO/S3 Credentials
MINIO_ROOT_USER=your_minio_user
MINIO_ROOT_PASSWORD=your_secure_password

# WAL-G Configuration
WALG_S3_PREFIX=s3://sahool-wal-archive/pg-primary
AWS_ENDPOINT=http://minio:9000
AWS_ACCESS_KEY_ID=${MINIO_ROOT_USER}
AWS_SECRET_ACCESS_KEY=${MINIO_ROOT_PASSWORD}
```

### Step 2: Deploy PostgreSQL with WAL-G

```bash
# Using overlay
docker-compose -f docker-compose.yml -f docker-compose.walg.yml up -d postgres

# OR build custom image
cd config/postgres
docker build -f Dockerfile.walg -t sahool/postgres-walg:16-3.4 .
```

### Step 3: Initialize and Test

```bash
# Initialize WAL-G
./config/postgres/scripts/init-walg.sh

# Test setup
./config/postgres/scripts/test-walg-setup.sh

# Create first backup
docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data

# Verify
docker-compose exec postgres wal-g backup-list
```

## File Structure

```
config/postgres/
├── postgresql.conf                    # PostgreSQL config with WAL archiving
├── Dockerfile.walg                    # Custom Docker image with WAL-G
├── k8s-walg-example.yaml             # Kubernetes configuration
├── README_WAL_ARCHIVING.md           # This file
├── PITR_RECOVERY.md                  # Complete recovery guide
├── WAL_ARCHIVING_QUICKSTART.md       # Quick start guide
└── scripts/
    ├── wal-archive.sh                # WAL archiving script
    ├── wal-restore.sh                # WAL restoration script
    ├── init-walg.sh                  # Initialization script
    ├── test-walg-setup.sh            # Test suite
    └── walg-maintenance.sh           # Maintenance operations

docker-compose.walg.yml               # Docker Compose overlay
.env.example                          # Environment variables (lines 774-842)
```

## Key Features

### Continuous WAL Archiving

- Automatic archiving of WAL files to S3/MinIO
- Local cache for quick recovery
- Multi-tier fallback strategy
- Comprehensive logging

### Base Backups

- Full and incremental (delta) backups
- Automated retention management
- Backup verification
- Performance optimization

### Point-in-Time Recovery

- Restore to latest state
- Restore to specific timestamp
- Restore to transaction ID
- Restore to named restore point

### Disaster Recovery

- Complete site failure recovery
- Database corruption recovery
- Geographic redundancy with S3
- Tested recovery procedures

### Monitoring & Maintenance

- Automated backup scheduling
- Health checks and alerts
- Storage usage monitoring
- Backup verification

## Common Operations

### Create Backup

```bash
docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data
```

### List Backups

```bash
docker-compose exec postgres wal-g backup-list
```

### Clean Up Old Backups

```bash
docker-compose exec postgres wal-g delete retain 7 --confirm
```

### Monitor WAL Archiving

```bash
docker-compose exec postgres psql -U sahool -c "SELECT * FROM pg_stat_archiver;"
```

### Check Logs

```bash
docker-compose exec postgres tail -f /var/log/postgresql/wal-archive.log
```

### Run Maintenance

```bash
./config/postgres/scripts/walg-maintenance.sh status
./config/postgres/scripts/walg-maintenance.sh backup
./config/postgres/scripts/walg-maintenance.sh cleanup
```

## Recovery Example

Quick recovery to latest state:

```bash
# 1. Stop PostgreSQL
docker-compose stop postgres

# 2. Clear data directory
docker volume rm sahool-unified-v15-idp_postgres_data

# 3. Restore backup
docker-compose run --rm postgres wal-g backup-fetch /var/lib/postgresql/data LATEST

# 4. Configure recovery
docker-compose run --rm postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = '/usr/local/bin/wal-restore.sh %f %p'
recovery_target_timeline = 'latest'
EOF"

# 5. Create recovery signal
docker-compose run --rm postgres touch /var/lib/postgresql/data/recovery.signal

# 6. Start PostgreSQL
docker-compose up -d postgres

# 7. Monitor recovery
docker-compose logs -f postgres
```

For complete recovery procedures, see [PITR_RECOVERY.md](./PITR_RECOVERY.md)

## Architecture

### Data Flow

```
┌─────────────────┐
│   PostgreSQL    │
│   WAL Writer    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ archive_command │
│  wal-archive.sh │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌──────────┐
│ WAL-G │  │  Local   │
│       │  │  Archive │
└───┬───┘  └──────────┘
    │
    ▼
┌──────────┐
│ S3/MinIO │
│  Bucket  │
└──────────┘
```

### Recovery Flow

```
┌──────────┐
│ S3/MinIO │
│  Bucket  │
└────┬─────┘
     │
     ▼
┌───────┐
│ WAL-G │
└───┬───┘
    │
    ▼
┌─────────────────┐
│ restore_command │
│  wal-restore.sh │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│ Recovery Mode   │
└─────────────────┘
```

## Security Considerations

1. **S3 Credentials** - Store securely in environment variables or HashiCorp Vault
2. **Backup Encryption** - Enable encryption in transit and at rest
3. **Access Control** - Use IAM policies to restrict S3 bucket access
4. **Network Security** - Use TLS for S3 connections
5. **Audit Logging** - Enable S3 bucket logging for compliance

## Performance Tuning

### For Large Databases (>100GB)

```bash
# Increase concurrency
WALG_UPLOAD_CONCURRENCY=8
WALG_DOWNLOAD_CONCURRENCY=8
WALG_DELTA_ORIGIN_CONCURRENCY=4

# Use faster compression
WALG_COMPRESSION_METHOD=lz4

# Enable delta backups
WALG_DELTA_MAX_STEPS=6
```

### For High-Write Workloads

```bash
# Increase WAL retention
# In postgresql.conf:
max_wal_size = 8GB
min_wal_size = 2GB
wal_keep_size = 2GB

# More frequent backups
# Daily full + hourly delta
```

## Troubleshooting

### WAL Archiving Not Working

```bash
# Check configuration
docker-compose exec postgres psql -U sahool -c "SHOW archive_command;"

# Check logs
docker-compose exec postgres tail -50 /var/log/postgresql/wal-archive.log

# Test S3 connection
docker-compose exec postgres wal-g backup-list
```

### Backup Failed

```bash
# Check disk space
docker-compose exec postgres df -h

# Check S3 permissions
docker-compose exec postgres aws s3 ls s3://sahool-wal-archive/ --endpoint-url http://minio:9000

# Review environment variables
docker-compose exec postgres env | grep -E "WALG|AWS"
```

For complete troubleshooting guide, see [PITR_RECOVERY.md](./PITR_RECOVERY.md#troubleshooting)

## Resources

- [Complete PITR Guide](./PITR_RECOVERY.md)
- [Quick Start Guide](./WAL_ARCHIVING_QUICKSTART.md)
- [WAL-G Documentation](https://github.com/wal-g/wal-g)
- [PostgreSQL Continuous Archiving](https://www.postgresql.org/docs/16/continuous-archiving.html)
- [MinIO Documentation](https://docs.min.io/)

## Support

For issues or questions:

- Review documentation in this directory
- Check logs: `docker-compose logs postgres`
- Run diagnostics: `./config/postgres/scripts/test-walg-setup.sh`
- Contact: devops@sahool.com

## Version History

- **v1.0.0** (2026-01-08) - Initial WAL-G archiving configuration
  - PostgreSQL 16 with WAL-G v2.0.1
  - Complete documentation and scripts
  - Docker and Kubernetes support
  - Comprehensive testing and maintenance tools

## License

Copyright (c) 2026 SAHOOL Platform. All rights reserved.
