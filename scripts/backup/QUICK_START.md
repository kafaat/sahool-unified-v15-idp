# SAHOOL Backup System - Quick Start Guide
# دليل البدء السريع لنظام النسخ الاحتياطي لسهول

**Version:** 1.0.0
**Setup Time:** ~10 minutes

---

## 📋 What You Get - ما ستحصل عليه

✅ Automated daily, weekly, and monthly backups
✅ PostgreSQL, Redis, NATS, and file backups
✅ S3/MinIO cloud storage integration
✅ Email and Slack notifications
✅ Backup verification and testing
✅ Complete disaster recovery procedures
✅ Web-based backup monitoring

---

## 🚀 Quick Setup (3 Steps) - الإعداد السريع

### Step 1: Configure Environment - تكوين البيئة

```bash
# Navigate to backup directory
cd scripts/backup

# Copy environment template
cp .env.backup.example .env.backup

# Edit configuration (required: passwords)
nano .env.backup
```

**Minimum required settings:**
```bash
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
MINIO_ROOT_PASSWORD=your_minio_password
```

### Step 2: Start Backup Infrastructure - تشغيل البنية التحتية

```bash
# Option A: Using make (recommended)
make backup-infra-up

# Option B: Using docker compose
docker compose -f scripts/backup/docker-compose.backup.yml up -d
```

**Access Points:**
- MinIO Console: http://localhost:9001
- Backup Monitor: http://localhost:8082

### Step 3: Test Backup - اختبار النسخ الاحتياطي

```bash
# Create your first backup
make backup

# Or using script directly
./scripts/backup/backup.sh daily

# Verify backup
make backup-verify
```

✅ **Done! Your backups are now automated.**

---

## 📁 Files Created - الملفات المنشأة

```
scripts/backup/
├── backup.sh                    # Main backup script
├── restore.sh                   # Restore from backup
├── backup-cron.sh              # Cron job wrapper
├── verify-backup.sh            # Backup verification
├── docker-compose.backup.yml   # Backup infrastructure
├── Dockerfile.backup           # Backup scheduler image
├── crontab                     # Cron schedule
├── disaster-recovery.md        # DR procedures
├── README.md                   # Full documentation
├── QUICK_START.md              # This file
└── .env.backup.example         # Configuration template
```

---

## ⏰ Backup Schedule - جدول النسخ الاحتياطي

| Type | Time | Retention | Status |
|------|------|-----------|--------|
| **Daily** | 02:00 AM | 7 days | ✅ Automated |
| **Weekly** | Sunday 03:00 AM | 28 days | ✅ Automated |
| **Monthly** | 1st 04:00 AM | 365 days | ✅ Automated |

**Verification:** Every Sunday at 06:00 AM (automated)

---

## 🎯 Common Tasks - المهام الشائعة

### Create Manual Backup - نسخة احتياطية يدوية

```bash
make backup
# or
./scripts/backup/backup.sh daily
```

### List All Backups - عرض جميع النسخ

```bash
make backup-list
# or
ls -lh backups/sahool_backup_*.tar.gz
```

### Restore from Backup - الاستعادة من نسخة احتياطية

```bash
make backup-restore
# Follow interactive prompts
```

### Verify Backup Integrity - التحقق من سلامة النسخة

```bash
make backup-verify
# or
./scripts/backup/verify-backup.sh
```

### View Backup Logs - عرض السجلات

```bash
make backup-logs
# or
tail -f logs/backup/backup_*.log
```

---

## 🔧 Troubleshooting - استكشاف الأخطاء

### Issue: "Backup fails - disk space"

**Solution:**
```bash
# Check disk space
df -h /backups

# Clean old backups manually
find /backups -name "*.tar.gz" -mtime +30 -delete
```

### Issue: "Container not running"

**Solution:**
```bash
# Check container status
docker ps | grep sahool

# Restart infrastructure services
docker compose up -d postgres redis nats
```

### Issue: "S3 upload fails"

**Solution:**
```bash
# Check MinIO is running
docker logs sahool-backup-minio

# Test MinIO connection
curl http://localhost:9000/minio/health/live

# Verify credentials in .env.backup
```

---

## 📊 Monitoring - المراقبة

### Check Backup Status - فحص حالة النسخ الاحتياطي

```bash
# View scheduler logs
docker logs -f sahool-backup-scheduler

# Check cron jobs
docker exec sahool-backup-scheduler crontab -l

# View health status
docker ps --filter name=sahool-backup
```

### Access MinIO Console - الوصول إلى MinIO

```bash
# URL: http://localhost:9001
# Username: sahool_backup (or your configured value)
# Password: [from .env.backup MINIO_ROOT_PASSWORD]
```

### Access Backup Monitor - الوصول إلى مراقب النسخ

```bash
# URL: http://localhost:8082
# Browse backups and logs
```

---

## 🔒 Security Best Practices - أفضل ممارسات الأمان

1. **Strong Passwords** - كلمات مرور قوية
   ```bash
   # Use at least 16 characters
   POSTGRES_PASSWORD=$(openssl rand -base64 24)
   ```

2. **Enable S3 for Off-site Backups** - تفعيل S3 للنسخ خارج الموقع
   ```bash
   S3_BACKUP_ENABLED=true
   S3_ENDPOINT=https://s3.amazonaws.com
   ```

3. **Enable Notifications** - تفعيل الإشعارات
   ```bash
   EMAIL_NOTIFICATIONS_ENABLED=true
   SLACK_NOTIFICATIONS_ENABLED=true
   ```

4. **Test Regularly** - اختبر بانتظام
   ```bash
   # Monthly DR drill
   make backup-verify
   ./scripts/backup/restore.sh [test-backup]
   ```

---

## 📚 Full Documentation - التوثيق الكامل

- **Complete Guide:** [README.md](./README.md)
- **Disaster Recovery:** [disaster-recovery.md](./disaster-recovery.md)
- **Script Reference:** See README.md

---

## 🆘 Emergency Recovery - التعافي الطارئ

### System Down? Follow These Steps - النظام معطل؟ اتبع هذه الخطوات

1. **List backups:**
   ```bash
   ls -lh backups/sahool_backup_*.tar.gz
   ```

2. **Restore latest backup:**
   ```bash
   ./scripts/backup/restore.sh
   # Select latest backup
   ```

3. **Start services:**
   ```bash
   docker compose up -d
   ```

4. **Verify:**
   ```bash
   make health
   curl http://localhost:8000/health
   ```

### Emergency Contacts - جهات الاتصال الطارئة

- **Email:** support@sahool.com
- **Phone:** +967-XXX-XXX-XXX
- **Documentation:** [disaster-recovery.md](./disaster-recovery.md)

---

## ✅ Post-Setup Checklist - قائمة ما بعد الإعداد

- [ ] Environment configured (`.env.backup`)
- [ ] Backup infrastructure running
- [ ] First backup completed
- [ ] Backup verified successfully
- [ ] MinIO accessible
- [ ] Notifications tested (if enabled)
- [ ] Team trained on restore procedure
- [ ] Disaster recovery plan reviewed

---

## 🎓 Next Steps - الخطوات التالية

1. **Schedule DR Drill**
   - Test full restore monthly
   - Document lessons learned

2. **Configure Cloud Storage**
   - Set up AWS S3 or DigitalOcean Spaces
   - Enable off-site backups

3. **Enable Notifications**
   - Configure email alerts
   - Set up Slack integration

4. **Review Retention Policies**
   - Adjust based on requirements
   - Consider compliance needs

---

## 💡 Pro Tips - نصائح احترافية

1. **Backup Before Updates**
   ```bash
   make backup && make upgrade
   ```

2. **Test Restore Regularly**
   ```bash
   # Monthly verification
   make backup-verify
   ```

3. **Monitor Disk Space**
   ```bash
   # Add to monitoring dashboard
   df -h /backups
   ```

4. **Document Changes**
   - Update disaster-recovery.md
   - Keep team informed

---

## 📞 Support - الدعم

- **Documentation:** [README.md](./README.md)
- **Disaster Recovery:** [disaster-recovery.md](./disaster-recovery.md)
- **Email:** support@sahool.com
- **GitHub Issues:** [Report Issue]

---

## 🎉 Success! - نجاح!

Your SAHOOL platform now has:
- ✅ Automated backups
- ✅ Disaster recovery capability
- ✅ Cloud storage integration
- ✅ Monitoring and alerts
- ✅ Verified restoration process

**Backups run automatically. Review logs weekly.**

---

**Last Updated:** 2024-12-26
**Version:** 1.0.0
**Author:** SAHOOL Platform Team
