# SAHOOL Database Backup System

# نظام النسخ الاحتياطي لقاعدة بيانات SAHOOL

## Overview | نظرة عامة

This is a comprehensive, production-ready database backup solution for the SAHOOL platform. It supports full and incremental backups, schema-specific backups, compression, retention policies, and integration with PgBouncer.

هذا حل شامل وجاهز للإنتاج للنسخ الاحتياطي لقاعدة البيانات لمنصة SAHOOL. يدعم النسخ الاحتياطي الكامل والتدريجي، والنسخ الاحتياطي الخاص بالمخططات، والضغط، وسياسات الاحتفاظ، والتكامل مع PgBouncer.

## Features | المميزات

✅ **Multiple Backup Types** - Daily, weekly, monthly, and manual backups
✅ **Backup Modes** - Full and incremental backup support
✅ **Schema-Specific** - Backup specific schemas (geo, users, etc.)
✅ **Compression** - Gzip compression to save space
✅ **Retention Policy** - Automatically keep 7 daily, 4 weekly, 12 monthly backups
✅ **Pre/Post Hooks** - Custom scripts before and after backups
✅ **PgBouncer Support** - Works with PgBouncer connection pooling
✅ **Verification** - Automatic backup integrity verification
✅ **Logging** - Comprehensive operation logging
✅ **Error Handling** - Robust error handling and notifications

## Installation | التثبيت

### 1. Prerequisites | المتطلبات الأساسية

```bash
# Ensure you have the required tools
# تأكد من وجود الأدوات المطلوبة
docker --version
pg_dump --version
gzip --version
```

### 2. Directory Structure | هيكل المجلدات

```bash
# Create backup directories
# إنشاء مجلدات النسخ الاحتياطي
sudo mkdir -p /backups/postgres/{daily,weekly,monthly,manual}
sudo mkdir -p /backups/logs
sudo mkdir -p /backups/.state
sudo mkdir -p /backups/reports

# Set permissions
# ضبط الصلاحيات
sudo chown -R $(whoami):$(whoami) /backups
chmod -R 755 /backups
```

### 3. Configuration | التكوين

The script automatically loads configuration from:

- `/home/user/sahool-unified-v15-idp/.env`
- `/home/user/sahool-unified-v15-idp/config/base.env`

يقوم السكريبت تلقائياً بتحميل التكوين من:

Key environment variables:

```bash
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=sahool
POSTGRES_PASSWORD=your_password
POSTGRES_DB=sahool
POSTGRES_CONTAINER=sahool-postgres
BACKUP_DIR=/backups
```

## Usage | الاستخدام

### Basic Usage | الاستخدام الأساسي

```bash
# Full daily backup (default)
# نسخ احتياطي يومي كامل (افتراضي)
./scripts/backup_database.sh

# Weekly full backup
# نسخ احتياطي أسبوعي كامل
./scripts/backup_database.sh -t weekly -m full

# Monthly full backup
# نسخ احتياطي شهري كامل
./scripts/backup_database.sh -t monthly -m full
```

### Advanced Usage | الاستخدام المتقدم

```bash
# Incremental backup
# نسخ احتياطي تدريجي
./scripts/backup_database.sh -t daily -m incremental

# Backup specific schema only
# نسخ احتياطي لمخطط محدد فقط
./scripts/backup_database.sh -s geo -t manual

# Backup via PgBouncer
# نسخ احتياطي عبر PgBouncer
./scripts/backup_database.sh --pgbouncer -t daily

# Backup without compression
# نسخ احتياطي بدون ضغط
./scripts/backup_database.sh --no-compress -t manual

# Verify existing backup
# التحقق من نسخة احتياطية موجودة
./scripts/backup_database.sh --verify-only /backups/postgres/daily/20260106_120000/full_20260106_120000.dump.gz
```

### Command Line Options | خيارات سطر الأوامر

| Option                | Description                                 | مثال                        |
| --------------------- | ------------------------------------------- | --------------------------- |
| `-t, --type TYPE`     | Backup type: daily, weekly, monthly, manual | `-t weekly`                 |
| `-m, --mode MODE`     | Backup mode: full, incremental              | `-m incremental`            |
| `-s, --schema SCHEMA` | Specific schema to backup                   | `-s geo`                    |
| `-d, --database DB`   | Database name                               | `-d sahool`                 |
| `--pgbouncer`         | Use PgBouncer connection                    | `--pgbouncer`               |
| `--no-compress`       | Skip compression                            | `--no-compress`             |
| `--verify-only FILE`  | Only verify backup file                     | `--verify-only backup.dump` |
| `-h, --help`          | Show help message                           | `-h`                        |

## Automated Backups | النسخ الاحتياطي الآلي

### Cron Setup | إعداد Cron

Create a cron job for automated backups:

```bash
# Edit crontab
# تحرير crontab
crontab -e

# Add the following lines
# أضف الأسطر التالية

# Daily full backup at 2:00 AM
# نسخ احتياطي يومي كامل الساعة 2:00 صباحاً
0 2 * * * /home/user/sahool-unified-v15-idp/scripts/backup_database.sh -t daily -m full >> /backups/logs/cron.log 2>&1

# Daily incremental backup at 6:00 AM, 12:00 PM, 6:00 PM
# نسخ احتياطي تدريجي يومي الساعة 6:00 صباحاً، 12:00 ظهراً، 6:00 مساءً
0 6,12,18 * * * /home/user/sahool-unified-v15-idp/scripts/backup_database.sh -t daily -m incremental >> /backups/logs/cron.log 2>&1

# Weekly backup every Sunday at 3:00 AM
# نسخ احتياطي أسبوعي كل يوم أحد الساعة 3:00 صباحاً
0 3 * * 0 /home/user/sahool-unified-v15-idp/scripts/backup_database.sh -t weekly -m full >> /backups/logs/cron.log 2>&1

# Monthly backup on the 1st of each month at 4:00 AM
# نسخ احتياطي شهري في اليوم الأول من كل شهر الساعة 4:00 صباحاً
0 4 1 * * /home/user/sahool-unified-v15-idp/scripts/backup_database.sh -t monthly -m full >> /backups/logs/cron.log 2>&1
```

### Systemd Timer (Alternative) | مؤقت Systemd (بديل)

Create a systemd service and timer:

```bash
# Create service file
# إنشاء ملف الخدمة
sudo nano /etc/systemd/system/sahool-backup.service

[Unit]
Description=SAHOOL Database Backup Service
After=docker.service

[Service]
Type=oneshot
User=root
ExecStart=/home/user/sahool-unified-v15-idp/scripts/backup_database.sh -t daily -m full
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Create timer file
# إنشاء ملف المؤقت
sudo nano /etc/systemd/system/sahool-backup.timer

[Unit]
Description=SAHOOL Database Backup Timer
Requires=sahool-backup.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Enable and start timer
# تفعيل وبدء المؤقت
sudo systemctl daemon-reload
sudo systemctl enable sahool-backup.timer
sudo systemctl start sahool-backup.timer
sudo systemctl status sahool-backup.timer
```

## Backup Hooks | خطافات النسخ الاحتياطي

### Pre-Backup Hook | خطاف ما قبل النسخ الاحتياطي

The pre-backup hook (`scripts/hooks/pre-backup.sh`) runs before the backup starts. Use it to:

- Check disk space
- Run VACUUM ANALYZE
- Pause background jobs
- Send notifications

يعمل خطاف ما قبل النسخ الاحتياطي قبل بدء النسخ. استخدمه لـ:

Example:

```bash
#!/bin/bash
# Check disk space
df -h /backups | tail -1

# Run VACUUM ANALYZE
docker exec sahool-postgres psql -U sahool -d sahool -c "VACUUM ANALYZE;"

# Create checkpoint
docker exec sahool-postgres psql -U sahool -d sahool -c "CHECKPOINT;"
```

### Post-Backup Hook | خطاف ما بعد النسخ الاحتياطي

The post-backup hook (`scripts/hooks/post-backup.sh`) runs after the backup completes. Use it to:

- Send notifications (email, Slack, SMS)
- Sync to remote storage (S3, NFS)
- Generate reports
- Resume background jobs

يعمل خطاف ما بعد النسخ الاحتياطي بعد اكتمال النسخ. استخدمه لـ:

Example:

```bash
#!/bin/bash
STATUS=$4  # success or failure

# Send email notification
if [ "$STATUS" = "success" ]; then
    echo "Backup completed successfully" | mail -s "SAHOOL Backup Success" admin@example.com
fi

# Sync to S3
aws s3 sync /backups/postgres s3://my-backups/postgres/
```

## Restoration | الاستعادة

### Restore Full Backup | استعادة النسخة الكاملة

```bash
# 1. Decompress backup (if compressed)
# فك ضغط النسخة (إذا كانت مضغوطة)
gunzip /backups/postgres/daily/20260106_120000/full_20260106_120000.dump.gz

# 2. Stop applications
# إيقاف التطبيقات
docker-compose stop web admin api

# 3. Drop and recreate database (CAUTION!)
# حذف وإعادة إنشاء قاعدة البيانات (تحذير!)
docker exec sahool-postgres psql -U sahool -d postgres -c "DROP DATABASE IF EXISTS sahool;"
docker exec sahool-postgres psql -U sahool -d postgres -c "CREATE DATABASE sahool;"

# 4. Restore backup
# استعادة النسخة
docker exec -i sahool-postgres pg_restore \
    -U sahool \
    -d sahool \
    -v \
    --no-owner \
    --no-privileges \
    < /backups/postgres/daily/20260106_120000/full_20260106_120000.dump

# 5. Restart applications
# إعادة تشغيل التطبيقات
docker-compose start web admin api
```

### Restore Specific Schema | استعادة مخطط محدد

```bash
# Restore only the geo schema
# استعادة مخطط geo فقط
docker exec -i sahool-postgres pg_restore \
    -U sahool \
    -d sahool \
    -n geo \
    -v \
    < /backups/postgres/manual/20260106_150000/schema_geo_20260106_150000.dump
```

### Restore from SQL Backup | الاستعادة من نسخة SQL

```bash
# Decompress
gunzip /backups/postgres/weekly/20260105_030000/sahool_20260105_030000.sql.gz

# Restore
docker exec -i sahool-postgres psql -U sahool -d sahool \
    < /backups/postgres/weekly/20260105_030000/sahool_20260105_030000.sql
```

### Restore Incremental Backup | استعادة النسخة التدريجية

```bash
# 1. First restore the base full backup
# أولاً استعادة النسخة الأساسية الكاملة
docker exec -i sahool-postgres pg_restore \
    -U sahool -d sahool -v \
    < /backups/postgres/daily/20260106_020000/full_20260106_020000.dump

# 2. Then apply incremental changes in order
# ثم تطبيق التغييرات التدريجية بالترتيب
docker exec -i sahool-postgres psql -U sahool -d sahool \
    < /backups/postgres/daily/20260106_060000/incremental_20260106_060000.sql

docker exec -i sahool-postgres psql -U sahool -d sahool \
    < /backups/postgres/daily/20260106_120000/incremental_20260106_120000.sql
```

### Point-in-Time Recovery | الاستعادة إلى نقطة زمنية محددة

For point-in-time recovery, you need to enable WAL archiving in PostgreSQL. This is beyond the scope of basic backups but can be configured.

للاستعادة إلى نقطة زمنية محددة، تحتاج إلى تفعيل أرشفة WAL في PostgreSQL.

## Backup Verification | التحقق من النسخ الاحتياطية

### Verify Backup Integrity | التحقق من سلامة النسخة

```bash
# Verify backup file
# التحقق من ملف النسخة
./scripts/backup_database.sh --verify-only /backups/postgres/daily/20260106_120000/full_20260106_120000.dump.gz

# List backup contents
# عرض محتويات النسخة
gunzip -c backup.dump.gz | pg_restore -l | head -20

# Test restore to temporary database
# اختبار الاستعادة إلى قاعدة بيانات مؤقتة
docker exec sahool-postgres psql -U sahool -c "CREATE DATABASE sahool_test;"
docker exec -i sahool-postgres pg_restore -U sahool -d sahool_test < backup.dump
docker exec sahool-postgres psql -U sahool -c "DROP DATABASE sahool_test;"
```

### Automated Verification | التحقق الآلي

Add to cron for weekly verification:

```bash
# Every Monday at 1:00 AM, verify the latest backup
# كل يوم اثنين الساعة 1:00 صباحاً، تحقق من أحدث نسخة احتياطية
0 1 * * 1 /home/user/sahool-unified-v15-idp/scripts/verify-backup.sh >> /backups/logs/verify.log 2>&1
```

## Monitoring and Alerts | المراقبة والتنبيهات

### Check Backup Status | التحقق من حالة النسخ الاحتياطي

```bash
# View backup logs
# عرض سجلات النسخ الاحتياطي
tail -f /backups/logs/backup_daily_$(date +%Y%m%d).log

# List all backups
# عرض جميع النسخ الاحتياطية
find /backups/postgres -name "*.dump.gz" -o -name "*.sql.gz" | sort

# Check backup sizes
# فحص أحجام النسخ الاحتياطية
du -sh /backups/postgres/*

# Generate backup report
# إنشاء تقرير النسخ الاحتياطي
cat /backups/reports/backup_report_$(date +%Y%m%d).txt
```

### Integration with Monitoring Systems | التكامل مع أنظمة المراقبة

The hooks support integration with:

- Email notifications
- Slack webhooks
- Prometheus metrics
- Custom monitoring systems

تدعم الخطافات التكامل مع:

## Retention Policy | سياسة الاحتفاظ

The script automatically manages backup retention:

- **Daily**: Keep last 7 backups (احتفظ بآخر 7 نسخ)
- **Weekly**: Keep last 4 backups (احتفظ بآخر 4 نسخ)
- **Monthly**: Keep last 12 backups (احتفظ بآخر 12 نسخة)
- **Manual**: Keep last 10 backups (احتفظ بآخر 10 نسخ)

Old backups are automatically deleted when new backups are created.

يتم حذف النسخ القديمة تلقائياً عند إنشاء نسخ جديدة.

## Troubleshooting | استكشاف الأخطاء

### Common Issues | المشاكل الشائعة

#### Backup fails with "disk full" | النسخ يفشل بسبب "امتلاء القرص"

```bash
# Check disk space
df -h /backups

# Clean up old backups manually
rm -rf /backups/postgres/daily/oldest_backup_folder

# Reduce retention count in script
# قلل عدد الاحتفاظ في السكريبت
```

#### Cannot connect to database | لا يمكن الاتصال بقاعدة البيانات

```bash
# Check if container is running
docker ps | grep postgres

# Check database connection
docker exec sahool-postgres psql -U sahool -d sahool -c "SELECT 1;"

# Check environment variables
env | grep POSTGRES
```

#### Restore fails with permission errors | الاستعادة تفشل بسبب أخطاء الصلاحيات

```bash
# Use --no-owner and --no-privileges flags
pg_restore --no-owner --no-privileges -d sahool backup.dump
```

#### PgBouncer connection issues | مشاكل اتصال PgBouncer

```bash
# PgBouncer doesn't support pg_restore custom format
# Use plain text format instead
# PgBouncer لا يدعم تنسيق pg_restore المخصص
# استخدم تنسيق النص العادي بدلاً من ذلك

./scripts/backup_database.sh --pgbouncer -t daily
# This will automatically use plain text format
```

## Security Best Practices | أفضل ممارسات الأمان

1. **Encrypt Backups**: Consider encrypting sensitive backups (تشفير النسخ الحساسة)

   ```bash
   # Encrypt backup
   openssl enc -aes-256-cbc -salt -in backup.dump -out backup.dump.enc

   # Decrypt backup
   openssl enc -aes-256-cbc -d -in backup.dump.enc -out backup.dump
   ```

2. **Secure Storage**: Store backups in secure, access-controlled locations (تخزين آمن)

3. **Offsite Backups**: Maintain copies in geographically separate locations (نسخ خارج الموقع)

4. **Regular Testing**: Test restore procedures regularly (اختبار منتظم)

5. **Access Control**: Limit access to backup files and scripts (التحكم في الوصول)

## Performance Optimization | تحسين الأداء

### For Large Databases | للقواعد الكبيرة

```bash
# Use parallel backup (requires PostgreSQL 9.3+)
# استخدام النسخ الاحتياطي المتوازي
pg_dump -j 4 -F d -f backup_dir sahool

# Use compression during backup
# استخدام الضغط أثناء النسخ الاحتياطي
pg_dump sahool | gzip > backup.sql.gz

# Backup during low-traffic hours
# النسخ الاحتياطي خلال ساعات الازدحام المنخفض
# Schedule backups at 2-4 AM
```

## Additional Resources | موارد إضافية

- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [pg_dump Manual](https://www.postgresql.org/docs/current/app-pgdump.html)
- [pg_restore Manual](https://www.postgresql.org/docs/current/app-pgrestore.html)
- [Docker PostgreSQL Guide](https://hub.docker.com/_/postgres)

## Support | الدعم

For issues or questions:

- Check logs: `/backups/logs/`
- Review this documentation
- Contact: SAHOOL Platform Team

للمشاكل أو الأسئلة:

- فحص السجلات
- مراجعة هذه الوثائق
- الاتصال: فريق منصة SAHOOL

---

**Last Updated**: 2026-01-06
**Version**: 2.0.0
**Maintainer**: SAHOOL Platform Team
