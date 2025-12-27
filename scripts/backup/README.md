# SAHOOL Platform Backup & Disaster Recovery
# نظام النسخ الاحتياطي والتعافي من الكوارث لمنصة سهول

**Version:** 1.0.0
**Last Updated:** 2024-12-26

---

## Overview - نظرة عامة

Complete backup and disaster recovery solution for the SAHOOL agricultural platform, featuring automated backups, S3/MinIO integration, and comprehensive restoration procedures.

حل شامل للنسخ الاحتياطي والتعافي من الكوارث لمنصة سهول الزراعية، يتميز بالنسخ الاحتياطي الآلي، والتكامل مع S3/MinIO، وإجراءات الاستعادة الشاملة.

## Features - الميزات

✅ **Automated Backups** - نسخ احتياطي آلي
- Daily, weekly, and monthly schedules
- Intelligent retention policies
- Cron-based scheduling

✅ **Comprehensive Coverage** - تغطية شاملة
- PostgreSQL/PostGIS databases
- Redis cache data
- NATS JetStream messages
- Uploaded files (satellite imagery, photos)
- Configuration files

✅ **Cloud Storage** - التخزين السحابي
- S3/MinIO integration
- Automatic upload to cloud
- Multi-location redundancy

✅ **Verification** - التحقق
- Automated backup testing
- Integrity validation
- Test restore to temporary database

✅ **Notifications** - الإشعارات
- Email alerts
- Slack integration
- Success/failure reporting

✅ **Disaster Recovery** - التعافي من الكوارث
- Step-by-step procedures
- RTO/RPO targets
- Emergency contacts

---

## Quick Start - البدء السريع

### 1. Setup Environment - إعداد البيئة

```bash
# Navigate to backup directory
cd /path/to/sahool-unified-v15-idp/scripts/backup

# Copy environment template
cp .env.backup.example .env.backup

# Edit configuration
nano .env.backup
```

### 2. Make Scripts Executable - جعل السكريبتات قابلة للتنفيذ

```bash
chmod +x backup.sh restore.sh backup-cron.sh verify-backup.sh
```

### 3. Run Manual Backup - تشغيل نسخة احتياطية يدوية

```bash
./backup.sh daily
```

### 4. Setup Automated Backups - إعداد النسخ الاحتياطي الآلي

#### Option A: Using Docker Compose (Recommended)

```bash
# Start backup infrastructure
docker compose -f docker-compose.backup.yml up -d

# View logs
docker logs -f sahool-backup-scheduler

# Access MinIO console
open http://localhost:9001
```

#### Option B: Using System Crontab

```bash
# Edit crontab
crontab -e

# Add these lines:
0 2 * * * /path/to/scripts/backup/backup-cron.sh daily
0 3 * * 0 /path/to/scripts/backup/backup-cron.sh weekly
0 4 1 * * /path/to/scripts/backup/backup-cron.sh monthly
```

---

## Scripts Reference - مرجع السكريبتات

### 1. backup.sh - Main Backup Script

**Purpose:** Create complete backups of all platform components

**Usage:**
```bash
./backup.sh [daily|weekly|monthly]
```

**Features:**
- PostgreSQL custom format dump with compression
- Redis RDB and AOF snapshots
- NATS JetStream data directory backup
- Uploaded files archival
- Configuration files backup
- Consolidated tar.gz archive
- S3/MinIO upload (optional)
- Email/Slack notifications

**Output:**
```
/backups/
  └── 20241226_020000/
      ├── postgres/sahool_20241226_020000.sql.gz
      ├── redis/dump_20241226_020000.rdb.gz
      ├── nats/jetstream_20241226_020000.tar.gz
      ├── uploads/files_20241226_020000.tar.gz
      ├── config/config_20241226_020000.tar.gz
      └── backup_metadata.json

  sahool_backup_daily_20241226_020000.tar.gz
```

### 2. restore.sh - Restore Script

**Purpose:** Restore from backup with integrity verification

**Usage:**
```bash
# Interactive mode
./restore.sh

# Direct restore
./restore.sh /path/to/backup.tar.gz
```

**Features:**
- Interactive backup selection
- Backup integrity verification
- Service stop/start management
- PostgreSQL database restoration
- Redis data restoration
- NATS JetStream restoration
- Uploaded files restoration
- Configuration restoration
- Automatic verification

**Safety:**
- Confirms before overwriting data
- Creates backup of current configuration
- Verifies restoration success
- Provides rollback instructions

### 3. backup-cron.sh - Cron Job Wrapper

**Purpose:** Wrapper script for scheduled backups with logging and monitoring

**Usage:**
```bash
./backup-cron.sh [daily|weekly|monthly]
```

**Features:**
- Lock file to prevent concurrent runs
- Pre-backup system checks
- Resource availability verification
- Comprehensive logging
- Log rotation and cleanup
- Failure notifications
- Email/Slack alerts

**Logs:**
```
/logs/backup/
  ├── backup_daily_20241226_020000.log
  ├── backup_weekly_20241225_030000.log
  └── backup_monthly_20241201_040000.log
```

### 4. verify-backup.sh - Backup Verification

**Purpose:** Test backup integrity and restoration capabilities

**Usage:**
```bash
# Verify latest backup
./verify-backup.sh

# Verify specific backup
./verify-backup.sh /path/to/backup.tar.gz
```

**Features:**
- Archive integrity check
- Test restore to temporary database
- Data validation
- Table counting and verification
- PostGIS extension check
- Redis file validation
- NATS archive verification
- Detailed verification report

**Report Output:**
```
/logs/backup-reports/
  └── verification_20241226_060000.txt
```

---

## Configuration - التكوين

### Environment Variables - متغيرات البيئة

Create `.env.backup` file or use existing `.env`:

```bash
# Database credentials
POSTGRES_USER=sahool
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=sahool
REDIS_PASSWORD=your_redis_password

# Backup configuration
BACKUP_DIR=/backups
BACKUP_RETENTION_DAYS=30

# S3/MinIO (optional)
S3_BACKUP_ENABLED=true
S3_ENDPOINT=http://minio:9000
S3_BUCKET=sahool-backups
S3_ACCESS_KEY=sahool_backup
S3_SECRET_KEY=your_minio_password

# Notifications (optional)
EMAIL_NOTIFICATIONS_ENABLED=true
BACKUP_EMAIL_TO=admin@sahool.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

SLACK_NOTIFICATIONS_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Retention Policy - سياسة الاحتفاظ

Default retention periods (configurable in `backup.sh`):

| Backup Type | Retention |
|-------------|-----------|
| Daily | 7 days |
| Weekly | 28 days (4 weeks) |
| Monthly | 365 days (12 months) |

---

## Backup Schedule - جدول النسخ الاحتياطي

### Default Schedule - الجدول الافتراضي

| Type | Time | Day | Retention |
|------|------|-----|-----------|
| Daily | 02:00 AM | Every day | 7 days |
| Weekly | 03:00 AM | Sunday | 28 days |
| Monthly | 04:00 AM | 1st of month | 365 days |

### Additional Tasks - مهام إضافية

| Task | Time | Day | Purpose |
|------|------|-----|---------|
| Verification | 06:00 AM | Sunday | Test latest backup |
| Log Cleanup | 01:00 AM | Monday | Remove old logs |
| Log Compression | 05:00 AM | Sunday | Compress old logs |

---

## Storage Requirements - متطلبات التخزين

### Estimated Backup Sizes - أحجام النسخ الاحتياطي المقدرة

| Component | Size (Typical) | Size (Large) |
|-----------|----------------|--------------|
| PostgreSQL | 500 MB | 5 GB |
| Redis | 50 MB | 500 MB |
| NATS | 100 MB | 1 GB |
| Uploads | 1 GB | 50 GB |
| Config | 10 MB | 50 MB |
| **Total** | **~2 GB** | **~57 GB** |

### Disk Space Planning - تخطيط مساحة القرص

```
Daily backups (7 days): 2 GB × 7 = 14 GB
Weekly backups (4 weeks): 2 GB × 4 = 8 GB
Monthly backups (12 months): 2 GB × 12 = 24 GB
Total minimum required: ~50 GB
Recommended: 100 GB
```

---

## MinIO/S3 Setup - إعداد MinIO/S3

### Local MinIO (Included) - MinIO محلي

```bash
# Start MinIO with backup infrastructure
docker compose -f docker-compose.backup.yml up -d minio

# Access MinIO Console
open http://localhost:9001

# Default credentials
Username: sahool_backup
Password: [Set in .env.backup]
```

### AWS S3 Configuration - تكوين AWS S3

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
AWS Access Key ID: [YOUR_KEY]
AWS Secret Access Key: [YOUR_SECRET]
Default region name: us-east-1

# Update .env.backup
S3_ENDPOINT=https://s3.amazonaws.com
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
```

---

## Monitoring & Logs - المراقبة والسجلات

### View Backup Logs - عرض سجلات النسخ الاحتياطي

```bash
# Latest daily backup log
tail -f /logs/backup/backup_daily_*.log

# View all backup logs
ls -lh /logs/backup/

# Search for errors
grep -i error /logs/backup/*.log
```

### Check Backup Status - فحص حالة النسخ الاحتياطي

```bash
# List all backups
ls -lh /backups/sahool_backup_*.tar.gz

# Check latest backup
ls -lth /backups/sahool_backup_*.tar.gz | head -1

# Verify backup count
find /backups -name "sahool_backup_*.tar.gz" | wc -l
```

### Monitor Cron Jobs - مراقبة مهام Cron

```bash
# View cron schedule
docker exec sahool-backup-scheduler crontab -l

# Check cron logs
docker logs -f sahool-backup-scheduler

# View cron health
tail -f /var/log/cron/health.log
```

---

## Disaster Recovery - التعافي من الكوارث

For complete disaster recovery procedures, see:
للحصول على إجراءات التعافي الكاملة من الكوارث، راجع:

📄 **[disaster-recovery.md](./disaster-recovery.md)**

### Quick Recovery - التعافي السريع

```bash
# 1. List available backups
./restore.sh

# 2. Select backup to restore
# Follow interactive prompts

# 3. Verify restoration
docker compose ps
docker compose logs

# 4. Test services
curl http://localhost:8000/health
```

### Emergency Contact - الاتصال الطارئ

- **Platform Team:** support@sahool.com
- **Emergency Hotline:** +967-XXX-XXX-XXX
- **Documentation:** [disaster-recovery.md](./disaster-recovery.md)

---

## Testing & Verification - الاختبار والتحقق

### Weekly Verification - التحقق الأسبوعي

```bash
# Automated (runs every Sunday at 6 AM)
# يعمل تلقائياً كل أحد الساعة 6 صباحاً

# Manual verification
./verify-backup.sh

# View verification report
cat /logs/backup-reports/verification_*.txt
```

### Monthly DR Drill - تمرين التعافي الشهري

```bash
# 1. Create test environment
docker compose -f docker-compose.test.yml up -d

# 2. Restore latest backup to test
./restore.sh [latest-backup] --target=test

# 3. Verify functionality
# Run integration tests

# 4. Document results
# Update disaster-recovery.md
```

---

## Troubleshooting - استكشاف الأخطاء

### Common Issues - المشاكل الشائعة

#### 1. Backup Fails - Disk Space

```bash
# Check disk space
df -h /backups

# Clean old backups
find /backups -name "*.tar.gz" -mtime +30 -delete

# Compress existing backups
gzip /backups/*.tar
```

#### 2. PostgreSQL Backup Fails

```bash
# Check PostgreSQL logs
docker logs sahool-postgres

# Test connection
docker exec sahool-postgres pg_isready -U sahool

# Manual backup test
docker exec sahool-postgres pg_dump -U sahool sahool > test.sql
```

#### 3. S3 Upload Fails

```bash
# Check AWS credentials
aws s3 ls s3://your-bucket/

# Test upload manually
aws s3 cp test-file.txt s3://your-bucket/ --endpoint-url=http://minio:9000

# Check network connectivity
curl http://minio:9000/minio/health/live
```

#### 4. Cron Not Running

```bash
# Check cron service
docker exec sahool-backup-scheduler pgrep cron

# View cron logs
docker exec sahool-backup-scheduler tail -f /var/log/cron/cron.log

# Restart scheduler
docker restart sahool-backup-scheduler
```

---

## Security Best Practices - أفضل ممارسات الأمان

### Encryption - التشفير

```bash
# Encrypt backups with GPG
gpg --encrypt --recipient admin@sahool.com backup.tar.gz

# Decrypt when needed
gpg --decrypt backup.tar.gz.gpg > backup.tar.gz
```

### Access Control - التحكم في الوصول

- Restrict backup directory permissions: `chmod 700 /backups`
- Use strong passwords for database and MinIO
- Rotate credentials regularly
- Enable MFA for cloud storage access

### Off-site Backups - النسخ الاحتياطي خارج الموقع

- Configure S3 replication to multiple regions
- Schedule periodic backups to external storage
- Test restoration from off-site backups quarterly

---

## Performance Optimization - تحسين الأداء

### Reduce Backup Time - تقليل وقت النسخ الاحتياطي

```bash
# Use parallel compression
export GZIP=-9
pigz -p 4 large-file.tar

# Exclude unnecessary data
pg_dump --exclude-table=logs --exclude-table=temp_data

# Incremental backups (for large datasets)
# Use pg_basebackup for PostgreSQL PITR
```

### Network Optimization - تحسين الشبكة

```bash
# Use compression for S3 uploads
aws s3 cp --storage-class INTELLIGENT_TIERING

# Limit bandwidth usage
aws s3 cp --bandwidth-limit 10MB/s
```

---

## Updates & Maintenance - التحديثات والصيانة

### Script Updates - تحديثات السكريبتات

```bash
# Pull latest scripts
git pull origin main

# Make executable
chmod +x scripts/backup/*.sh

# Test in dry-run mode
./backup.sh daily --dry-run
```

### Version History - تاريخ الإصدارات

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-12-26 | Initial release |

---

## Support - الدعم

### Documentation - التوثيق

- **Backup Scripts:** This README
- **Disaster Recovery:** [disaster-recovery.md](./disaster-recovery.md)
- **Platform Docs:** ../../docs/

### Getting Help - الحصول على المساعدة

- **Email:** support@sahool.com
- **Slack:** #sahool-ops
- **Issues:** GitHub Issues

### Contributing - المساهمة

Improvements and bug fixes are welcome! Please submit a pull request.

---

## License - الترخيص

Copyright © 2024 SAHOOL Platform Team. All rights reserved.

---

**Last Updated:** 2024-12-26
**Maintained By:** SAHOOL DevOps Team
