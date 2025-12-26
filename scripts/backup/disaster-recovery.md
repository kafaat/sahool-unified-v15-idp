# SAHOOL Platform Disaster Recovery Plan
# خطة التعافي من الكوارث لمنصة سهول

**Version:** 1.0.0
**Last Updated:** 2024-12-26
**Owner:** SAHOOL Platform Team

---

## Table of Contents - جدول المحتويات

1. [Overview - نظرة عامة](#overview)
2. [Recovery Objectives - أهداف التعافي](#recovery-objectives)
3. [Backup Strategy - استراتيجية النسخ الاحتياطي](#backup-strategy)
4. [Recovery Procedures - إجراءات التعافي](#recovery-procedures)
5. [Emergency Contacts - جهات الاتصال الطارئة](#emergency-contacts)
6. [Incident Response Checklist - قائمة الاستجابة للحوادث](#incident-response-checklist)
7. [Testing & Validation - الاختبار والتحقق](#testing-validation)

---

## 1. Overview - نظرة عامة

This Disaster Recovery (DR) plan outlines procedures to restore the SAHOOL agricultural platform in case of data loss, system failure, or catastrophic events.

تحدد هذه الخطة للتعافي من الكوارث إجراءات استعادة منصة سهول الزراعية في حالة فقدان البيانات أو فشل النظام أو الأحداث الكارثية.

### Critical Components - المكونات الحرجة

- **PostgreSQL Database** (PostGIS) - قاعدة البيانات المكانية
- **Redis Cache** - ذاكرة التخزين المؤقت
- **NATS JetStream** - نظام الرسائل
- **Qdrant Vector DB** - قاعدة البيانات المتجهة
- **Uploaded Files** - الملفات المرفوعة (صور الأقمار الصناعية، الصور)
- **Configuration Files** - ملفات التكوين

### Disaster Scenarios - سيناريوهات الكوارث

1. **Hardware Failure** - فشل الأجهزة
2. **Data Corruption** - تلف البيانات
3. **Accidental Deletion** - الحذف العرضي
4. **Cyberattack/Ransomware** - الهجوم السيبراني/برامج الفدية
5. **Natural Disaster** - الكوارث الطبيعية
6. **Human Error** - الخطأ البشري

---

## 2. Recovery Objectives - أهداف التعافي

### RTO (Recovery Time Objective) - هدف وقت التعافي

| Component | RTO | Priority |
|-----------|-----|----------|
| Database (PostgreSQL) | 2 hours | Critical |
| Cache (Redis) | 30 minutes | High |
| Message Queue (NATS) | 1 hour | High |
| File Storage | 4 hours | Medium |
| Full System | 6 hours | Critical |

### RPO (Recovery Point Objective) - هدف نقطة التعافي

| Backup Type | Frequency | Retention | RPO |
|-------------|-----------|-----------|-----|
| Daily | 02:00 AM | 7 days | 24 hours |
| Weekly | Sunday 03:00 AM | 4 weeks | 1 week |
| Monthly | 1st day 04:00 AM | 12 months | 1 month |

**Maximum Acceptable Data Loss:** 24 hours
**الحد الأقصى المقبول لفقدان البيانات:** 24 ساعة

---

## 3. Backup Strategy - استراتيجية النسخ الاحتياطي

### Automated Backups - النسخ الاحتياطي الآلي

All backups are automated using cron jobs:

```bash
# Daily backup at 2 AM
0 2 * * * /path/to/scripts/backup/backup-cron.sh daily

# Weekly backup on Sunday at 3 AM
0 3 * * 0 /path/to/scripts/backup/backup-cron.sh weekly

# Monthly backup on 1st at 4 AM
0 4 1 * * /path/to/scripts/backup/backup-cron.sh monthly
```

### Backup Components - مكونات النسخ الاحتياطي

1. **PostgreSQL**
   - Custom format dump with compression
   - Includes schemas, data, and indexes
   - PostGIS spatial data preserved

2. **Redis**
   - RDB snapshot
   - AOF (Append-Only File) if enabled
   - Keys and values preserved

3. **NATS JetStream**
   - Complete data directory
   - Stream configurations
   - Consumer states

4. **File Uploads**
   - Satellite imagery
   - User photos
   - Documents

5. **Configuration**
   - Docker Compose files
   - Infrastructure configs
   - Application settings

### Storage Locations - مواقع التخزين

1. **Primary:** Local disk (`/backups`)
2. **Secondary:** MinIO/S3 (optional)
3. **Off-site:** Cloud storage (recommended for production)

---

## 4. Recovery Procedures - إجراءات التعافي

### 4.1 Full System Recovery - استعادة النظام الكاملة

**Scenario:** Complete system failure requiring full restoration
**السيناريو:** فشل كامل للنظام يتطلب استعادة كاملة

#### Prerequisites - المتطلبات الأساسية

- [ ] Access to backup files
- [ ] Docker and Docker Compose installed
- [ ] `.env` file configured
- [ ] Sufficient disk space (minimum 50GB)
- [ ] Network connectivity

#### Step-by-Step Procedure - الإجراء خطوة بخطوة

```bash
# Step 1: Navigate to project directory
cd /path/to/sahool-unified-v15-idp

# Step 2: Stop all running services
docker compose down

# Step 3: List available backups
./scripts/backup/restore.sh

# Step 4: Select and restore backup (interactive)
./scripts/backup/restore.sh

# OR specify backup file directly
./scripts/backup/restore.sh /path/to/backups/sahool_backup_daily_20241226_020000.tar.gz

# Step 5: Start all services
docker compose up -d

# Step 6: Verify restoration
make health

# Step 7: Check service logs
docker compose logs -f --tail=100
```

#### Verification Steps - خطوات التحقق

```bash
# Verify PostgreSQL
docker exec sahool-postgres psql -U sahool -d sahool -c "SELECT COUNT(*) FROM users;"

# Verify Redis
docker exec sahool-redis redis-cli -a ${REDIS_PASSWORD} PING

# Verify NATS
curl http://localhost:8222/healthz

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8080/healthz
```

### 4.2 Database-Only Recovery - استعادة قاعدة البيانات فقط

**Scenario:** Database corruption or data loss
**السيناريو:** تلف قاعدة البيانات أو فقدان البيانات

```bash
# Step 1: Stop application services (keep infrastructure)
docker compose stop field_ops marketplace_service research_core

# Step 2: Backup current database (if possible)
docker exec sahool-postgres pg_dump -U sahool sahool > /tmp/emergency_backup.sql

# Step 3: Extract database from backup
tar -xzf sahool_backup_daily_20241226.tar.gz

# Step 4: Drop and recreate database
docker exec sahool-postgres psql -U sahool -c "DROP DATABASE sahool;" postgres
docker exec sahool-postgres psql -U sahool -c "CREATE DATABASE sahool;" postgres

# Step 5: Restore from backup
gunzip -c 20241226_020000/postgres/sahool_*.sql.gz | \
  docker exec -i sahool-postgres pg_restore -U sahool -d sahool

# Step 6: Verify restoration
docker exec sahool-postgres psql -U sahool -d sahool -c "\dt"

# Step 7: Restart application services
docker compose start
```

### 4.3 Partial Data Recovery - استعادة جزئية للبيانات

**Scenario:** Accidental deletion of specific records
**السيناريو:** حذف عرضي لسجلات محددة

```bash
# Step 1: Create temporary restore database
docker exec sahool-postgres psql -U sahool -c "CREATE DATABASE sahool_restore;" postgres

# Step 2: Restore backup to temporary database
gunzip -c backup.sql.gz | \
  docker exec -i sahool-postgres pg_restore -U sahool -d sahool_restore

# Step 3: Extract specific data
docker exec sahool-postgres psql -U sahool -d sahool_restore -c \
  "COPY (SELECT * FROM users WHERE deleted_at > '2024-12-25') TO STDOUT CSV HEADER" > recovered_users.csv

# Step 4: Import to production database
docker exec -i sahool-postgres psql -U sahool -d sahool -c \
  "COPY users FROM STDIN CSV HEADER" < recovered_users.csv

# Step 5: Cleanup temporary database
docker exec sahool-postgres psql -U sahool -c "DROP DATABASE sahool_restore;" postgres
```

### 4.4 Point-in-Time Recovery - الاستعادة إلى نقطة زمنية

For PostgreSQL continuous archiving (if configured):

```bash
# Step 1: Stop PostgreSQL
docker compose stop postgres

# Step 2: Move current data directory
docker exec sahool-postgres mv /var/lib/postgresql/data /var/lib/postgresql/data.old

# Step 3: Restore base backup
docker exec sahool-postgres pg_basebackup -U sahool -D /var/lib/postgresql/data

# Step 4: Create recovery.conf
cat > recovery.conf <<EOF
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2024-12-26 10:00:00'
EOF

docker cp recovery.conf sahool-postgres:/var/lib/postgresql/data/

# Step 5: Start PostgreSQL
docker compose start postgres

# Step 6: Monitor recovery
docker logs -f sahool-postgres
```

---

## 5. Emergency Contacts - جهات الاتصال الطارئة

### Primary Team - الفريق الأساسي

| Role | Name | Phone | Email | Availability |
|------|------|-------|-------|--------------|
| Platform Lead | [Name] | +967-XXX-XXX-XXX | lead@sahool.com | 24/7 |
| Database Admin | [Name] | +967-XXX-XXX-XXX | dba@sahool.com | 24/7 |
| DevOps Engineer | [Name] | +967-XXX-XXX-XXX | devops@sahool.com | 24/7 |
| Security Officer | [Name] | +967-XXX-XXX-XXX | security@sahool.com | 24/7 |

### Escalation Path - مسار التصعيد

1. **Level 1:** On-call DevOps Engineer (Response: 15 minutes)
2. **Level 2:** Database Administrator (Response: 30 minutes)
3. **Level 3:** Platform Lead (Response: 1 hour)
4. **Level 4:** CTO/Management (Response: 2 hours)

### External Vendors - الموردين الخارجيين

| Service | Contact | Phone | Email |
|---------|---------|-------|-------|
| Cloud Provider | [Provider] | [Phone] | [Email] |
| Database Consulting | [Consultant] | [Phone] | [Email] |
| Security Firm | [Firm] | [Phone] | [Email] |

---

## 6. Incident Response Checklist - قائمة الاستجابة للحوادث

### Initial Response (0-15 minutes) - الاستجابة الأولية

- [ ] **Identify the incident** - تحديد الحادث
  - Type of failure
  - Affected components
  - Estimated impact

- [ ] **Assess severity** - تقييم الخطورة
  - Critical (full outage)
  - High (major functionality affected)
  - Medium (partial functionality affected)
  - Low (minor impact)

- [ ] **Notify stakeholders** - إخطار أصحاب المصلحة
  - Internal team
  - Management
  - Affected users (if applicable)

- [ ] **Activate DR team** - تفعيل فريق التعافي
  - Assign roles
  - Set up communication channel
  - Establish command center

### Assessment Phase (15-30 minutes) - مرحلة التقييم

- [ ] **Determine root cause** - تحديد السبب الجذري
- [ ] **Identify recovery strategy** - تحديد استراتيجية التعافي
- [ ] **Locate latest valid backup** - تحديد موقع آخر نسخة احتياطية صالحة
- [ ] **Calculate estimated recovery time** - حساب الوقت المتوقع للتعافي
- [ ] **Document incident details** - توثيق تفاصيل الحادث

### Recovery Phase (30 minutes - 6 hours) - مرحلة التعافي

- [ ] **Prepare recovery environment** - تجهيز بيئة التعافي
- [ ] **Verify backup integrity** - التحقق من سلامة النسخ الاحتياطي
- [ ] **Execute recovery procedure** - تنفيذ إجراء التعافي
- [ ] **Monitor recovery progress** - مراقبة تقدم التعافي
- [ ] **Run verification tests** - تشغيل اختبارات التحقق

### Validation Phase (Post-recovery) - مرحلة التحقق

- [ ] **Verify all services operational** - التحقق من تشغيل جميع الخدمات
- [ ] **Test critical functionality** - اختبار الوظائف الحرجة
- [ ] **Validate data integrity** - التحقق من سلامة البيانات
- [ ] **Check system performance** - فحص أداء النظام
- [ ] **Review logs for errors** - مراجعة السجلات للأخطاء

### Post-Incident Phase - مرحلة ما بعد الحادث

- [ ] **Document lessons learned** - توثيق الدروس المستفادة
- [ ] **Update DR plan** - تحديث خطة التعافي
- [ ] **Improve backup procedures** - تحسين إجراءات النسخ الاحتياطي
- [ ] **Schedule post-mortem meeting** - جدولة اجتماع ما بعد الحادث
- [ ] **Implement preventive measures** - تنفيذ الإجراءات الوقائية

---

## 7. Testing & Validation - الاختبار والتحقق

### Backup Verification - التحقق من النسخ الاحتياطي

**Frequency:** Weekly (automated)
**التكرار:** أسبوعياً (آلي)

```bash
# Automated verification
./scripts/backup/verify-backup.sh

# Manual verification
./scripts/backup/verify-backup.sh /path/to/backup.tar.gz
```

### DR Drill Schedule - جدول تمارين التعافي

| Drill Type | Frequency | Participants | Duration |
|------------|-----------|--------------|----------|
| Database Restore | Monthly | DBA, DevOps | 1 hour |
| Partial Recovery | Quarterly | Full DR Team | 2 hours |
| Full System Recovery | Semi-annually | All Teams | 4 hours |
| Disaster Simulation | Annually | Organization-wide | 8 hours |

### Testing Checklist - قائمة الاختبار

#### Monthly Tests - الاختبارات الشهرية

- [ ] Verify backup completion
- [ ] Check backup file sizes
- [ ] Test database restore to test environment
- [ ] Validate backup metadata
- [ ] Review backup logs

#### Quarterly Tests - الاختبارات الفصلية

- [ ] Full system restore to staging environment
- [ ] Performance testing post-restore
- [ ] Data integrity validation
- [ ] Application functionality testing
- [ ] Documentation review

#### Annual Tests - الاختبارات السنوية

- [ ] Complete disaster simulation
- [ ] Test all recovery procedures
- [ ] Validate RTO/RPO metrics
- [ ] Update contact information
- [ ] Review and update DR plan

---

## Recovery Scripts Quick Reference - مرجع سريع للسكريبتات

### Create Backup - إنشاء نسخة احتياطية

```bash
# Manual backup
./scripts/backup/backup.sh [daily|weekly|monthly]

# Example
./scripts/backup/backup.sh daily
```

### Restore from Backup - الاستعادة من نسخة احتياطية

```bash
# Interactive restore
./scripts/backup/restore.sh

# Direct restore
./scripts/backup/restore.sh /path/to/backup.tar.gz
```

### Verify Backup - التحقق من النسخة الاحتياطية

```bash
# Latest backup
./scripts/backup/verify-backup.sh

# Specific backup
./scripts/backup/verify-backup.sh /path/to/backup.tar.gz
```

### Check Backup Status - فحص حالة النسخ الاحتياطي

```bash
# List backups
ls -lh /backups/sahool_backup_*.tar.gz

# Check backup logs
tail -f /logs/backup/backup_*.log

# View backup schedule
docker exec sahool-backup-scheduler crontab -l
```

---

## Appendix A: Common Issues and Solutions

### Issue 1: Backup Fails with Disk Space Error

**Solution:**
```bash
# Check disk space
df -h /backups

# Clean old backups
find /backups -name "*.tar.gz" -mtime +30 -delete

# Adjust retention in backup.sh
DAILY_RETENTION=7  # Reduce if needed
```

### Issue 2: PostgreSQL Restore Fails

**Solution:**
```bash
# Check PostgreSQL logs
docker logs sahool-postgres

# Verify backup file
tar -tzf backup.tar.gz | grep postgres

# Try manual restore
docker exec -i sahool-postgres psql -U sahool -d sahool < backup.sql
```

### Issue 3: Services Won't Start After Restore

**Solution:**
```bash
# Check service dependencies
docker compose ps

# View service logs
docker compose logs [service-name]

# Restart services in order
docker compose up -d postgres redis nats
sleep 10
docker compose up -d
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2024-12-26 | SAHOOL Team | Initial version |

---

**Last Review Date:** 2024-12-26
**Next Review Date:** 2025-06-26
**Document Owner:** Platform Team Lead

---

## Notes - ملاحظات

- This DR plan should be reviewed and updated quarterly
- يجب مراجعة وتحديث هذه الخطة كل ربع سنة

- All team members must be familiar with this plan
- يجب أن يكون جميع أعضاء الفريق على دراية بهذه الخطة

- DR drills are mandatory and must be documented
- تمارين التعافي إلزامية ويجب توثيقها

- Keep contact information current at all times
- حافظ على معلومات الاتصال محدثة في جميع الأوقات
