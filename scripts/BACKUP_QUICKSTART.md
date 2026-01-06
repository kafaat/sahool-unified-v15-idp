# Database Backup Quick Start Guide
# دليل البدء السريع للنسخ الاحتياطي

## 🚀 Quick Setup (5 Minutes) | الإعداد السريع

### Step 1: Verify Installation | التحقق من التثبيت

```bash
cd /home/user/sahool-unified-v15-idp

# Check script is executable
ls -l scripts/backup_database.sh

# Verify directories exist
ls -ld /backups/
```

### Step 2: Run Your First Backup | تشغيل أول نسخة احتياطية

```bash
# Test with a simple daily backup
./scripts/backup_database.sh -t manual -m full

# Check the results
ls -lh /backups/postgres/manual/
```

### Step 3: Set Up Automated Backups | إعداد النسخ الآلي

```bash
# Edit crontab
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /home/user/sahool-unified-v15-idp/scripts/backup_database.sh -t daily -m full >> /backups/logs/cron.log 2>&1

# Save and exit
```

## 📋 Common Commands | الأوامر الشائعة

### Daily Operations | العمليات اليومية

```bash
# Full backup
./scripts/backup_database.sh -t daily -m full

# Incremental backup
./scripts/backup_database.sh -t daily -m incremental

# Check backup status
tail -f /backups/logs/backup_daily_$(date +%Y%m%d).log

# List all backups
ls -lh /backups/postgres/*/
```

### Weekly/Monthly Backups | النسخ الأسبوعي/الشهري

```bash
# Weekly backup
./scripts/backup_database.sh -t weekly -m full

# Monthly backup
./scripts/backup_database.sh -t monthly -m full
```

### Schema-Specific Backups | نسخ المخططات المحددة

```bash
# Backup geo schema
./scripts/backup_database.sh -s geo -t manual

# Backup users schema
./scripts/backup_database.sh -s users -t manual

# Backup with PgBouncer
./scripts/backup_database.sh --pgbouncer -t daily
```

## 🔄 Quick Restore | الاستعادة السريعة

### Restore Latest Backup | استعادة آخر نسخة

```bash
# Find latest backup
LATEST_BACKUP=$(find /backups/postgres/daily -name "*.dump.gz" -type f | sort -r | head -1)
echo "Latest backup: $LATEST_BACKUP"

# Decompress
gunzip -c "$LATEST_BACKUP" > /tmp/restore.dump

# Restore (CAUTION: This will overwrite existing data!)
docker exec -i sahool-postgres pg_restore \
    -U sahool \
    -d sahool \
    -c \
    --if-exists \
    --no-owner \
    --no-privileges \
    < /tmp/restore.dump

# Cleanup
rm /tmp/restore.dump
```

### Restore Specific Schema | استعادة مخطط محدد

```bash
# Find schema backup
SCHEMA_BACKUP=$(find /backups/postgres -name "*schema_geo*.sql*" | sort -r | head -1)

# Decompress and restore
gunzip -c "$SCHEMA_BACKUP" | docker exec -i sahool-postgres psql -U sahool -d sahool
```

## 📊 Monitoring | المراقبة

### Check Disk Space | فحص المساحة

```bash
# Check backup directory size
du -sh /backups/

# Check available space
df -h /backups

# Breakdown by backup type
du -sh /backups/postgres/*
```

### View Logs | عرض السجلات

```bash
# Today's backup log
tail -f /backups/logs/backup_daily_$(date +%Y%m%d).log

# All logs from today
tail -f /backups/logs/*.log

# Search for errors
grep -i error /backups/logs/*.log
```

### Backup Status | حالة النسخ الاحتياطي

```bash
# Count backups
echo "Daily: $(find /backups/postgres/daily -type d -maxdepth 1 | wc -l)"
echo "Weekly: $(find /backups/postgres/weekly -type d -maxdepth 1 | wc -l)"
echo "Monthly: $(find /backups/postgres/monthly -type d -maxdepth 1 | wc -l)"

# Latest backup info
find /backups/postgres -name "metadata.json" -type f | xargs -I {} sh -c 'echo "---"; cat {}'
```

## ⚙️ Customization | التخصيص

### Modify Retention Policy | تعديل سياسة الاحتفاظ

Edit `/home/user/sahool-unified-v15-idp/scripts/backup_database.sh`:

```bash
# Find this section and modify as needed
declare -A RETENTION_COUNT=(
    ["daily"]=7      # Keep last 7 daily backups
    ["weekly"]=4     # Keep last 4 weekly backups
    ["monthly"]=12   # Keep last 12 monthly backups
    ["manual"]=10    # Keep last 10 manual backups
)
```

### Add Custom Hooks | إضافة خطافات مخصصة

Edit pre-backup hook:
```bash
nano /home/user/sahool-unified-v15-idp/scripts/hooks/pre-backup.sh
```

Edit post-backup hook:
```bash
nano /home/user/sahool-unified-v15-idp/scripts/hooks/post-backup.sh
```

## 🆘 Troubleshooting | استكشاف الأخطاء

### Problem: Backup fails with "disk full"

```bash
# Check space
df -h /backups

# Clean old backups manually
rm -rf /backups/postgres/daily/$(ls -t /backups/postgres/daily | tail -1)

# Or adjust retention
# Edit the script to keep fewer backups
```

### Problem: Cannot connect to database

```bash
# Check container status
docker ps | grep postgres

# Test connection
docker exec sahool-postgres psql -U sahool -d sahool -c "SELECT 1;"

# Check environment variables
source /home/user/sahool-unified-v15-idp/config/base.env
env | grep POSTGRES
```

### Problem: Backup verification fails

```bash
# Verify manually
gunzip -t /path/to/backup.dump.gz

# List backup contents
gunzip -c /path/to/backup.dump.gz | pg_restore -l | head -20

# Use verify-only mode
./scripts/backup_database.sh --verify-only /path/to/backup.dump.gz
```

## 📁 File Structure | هيكل الملفات

```
/home/user/sahool-unified-v15-idp/
├── scripts/
│   ├── backup_database.sh          # Main backup script (البرنامج الرئيسي)
│   ├── backup_database.cron        # Cron examples (أمثلة Cron)
│   ├── BACKUP_README.md            # Full documentation (الوثائق الكاملة)
│   ├── BACKUP_QUICKSTART.md        # This file (هذا الملف)
│   └── hooks/
│       ├── pre-backup.sh           # Pre-backup hook (خطاف ما قبل)
│       └── post-backup.sh          # Post-backup hook (خطاف ما بعد)
│
/backups/
├── postgres/
│   ├── daily/                      # Daily backups (النسخ اليومي)
│   ├── weekly/                     # Weekly backups (النسخ الأسبوعي)
│   ├── monthly/                    # Monthly backups (النسخ الشهري)
│   └── manual/                     # Manual backups (النسخ اليدوي)
├── logs/                           # Backup logs (السجلات)
├── .state/                         # State tracking (تتبع الحالة)
└── reports/                        # Backup reports (التقارير)
```

## 🎯 Best Practices | أفضل الممارسات

1. **Test Restores Regularly** - Test at least monthly
   اختبر الاستعادة بانتظام - اختبر على الأقل شهرياً

2. **Monitor Disk Space** - Keep at least 50% free
   راقب مساحة القرص - احتفظ بـ 50% على الأقل

3. **Verify Backups** - Run verification weekly
   تحقق من النسخ - قم بالتحقق أسبوعياً

4. **Offsite Copies** - Store copies in different locations
   نسخ خارج الموقع - احفظ نسخاً في مواقع مختلفة

5. **Document Procedures** - Keep restore procedures updated
   وثق الإجراءات - حافظ على تحديث إجراءات الاستعادة

## 📞 Need Help? | تحتاج مساعدة؟

- Check full documentation: `BACKUP_README.md`
- View logs: `/backups/logs/`
- Run with help: `./scripts/backup_database.sh --help`
- Contact: SAHOOL Platform Team

---

**Quick Reference Commands:**

```bash
# Run backup
./scripts/backup_database.sh -t daily -m full

# Check status
tail -f /backups/logs/backup_daily_$(date +%Y%m%d).log

# List backups
find /backups/postgres -name "*.dump.gz"

# Verify backup
./scripts/backup_database.sh --verify-only /path/to/backup.dump.gz

# Restore
gunzip -c backup.dump.gz | docker exec -i sahool-postgres pg_restore -U sahool -d sahool
```

Happy Backing Up! 🎉
