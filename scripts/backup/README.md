# نظام النسخ الاحتياطي - SAHOOL Platform Backup System

نظام شامل للنسخ الاحتياطي والاستعادة لمنصة سهول.

## 📁 الملفات المتوفرة | Available Files

### نصوص النسخ الاحتياطي | Backup Scripts

- **backup_postgres.sh** - نسخ احتياطي لقاعدة بيانات PostgreSQL
- **backup_redis.sh** - نسخ احتياطي لـ Redis (RDB + AOF)
- **backup_minio.sh** - نسخ احتياطي لـ MinIO/S3
- **backup_all.sh** - نسخ احتياطي شامل لجميع المكونات

### نصوص الاستعادة | Restore Scripts

- **restore_postgres.sh** - استعادة PostgreSQL مع فحوصات أمان

### نصوص إضافية | Additional Scripts

- **backup.sh** - النسخ الاحتياطي القديم (متوافق)
- **restore.sh** - الاستعادة القديمة (متوافق)
- **backup-cron.sh** - جدولة تلقائية
- **verify-backup.sh** - التحقق من صحة النسخ

## 🚀 الاستخدام السريع | Quick Usage

### نسخ احتياطي يدوي

```bash
# PostgreSQL
./backup_postgres.sh daily

# Redis
./backup_redis.sh daily

# MinIO
./backup_minio.sh daily

# الكل معاً
./backup_all.sh manual
```

### الاستعادة

```bash
# استعادة من آخر نسخة
./restore_postgres.sh --latest

# استعادة من ملف محدد
./restore_postgres.sh /path/to/backup.dump

# عرض المساعدة
./restore_postgres.sh --help
```

### البنية التحتية

```bash
# تشغيل خدمات النسخ الاحتياطي
docker compose -f docker-compose.backup.yml up -d

# إيقاف الخدمات
docker compose -f docker-compose.backup.yml down

# عرض السجلات
docker compose -f docker-compose.backup.yml logs -f
```

## ⚙️ المتغيرات المطلوبة | Required Variables

أضف هذه المتغيرات إلى ملف `.env`:

```env
# قواعد البيانات
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_password

# MinIO
MINIO_ROOT_USER=sahool_backup
MINIO_ROOT_PASSWORD=your_secure_password

# التشفير (AES-256) - مطلوب للحماية
BACKUP_ENCRYPTION_ENABLED=true
BACKUP_ENCRYPTION_KEY=change_this_encryption_key_at_least_32_characters_long

# الضغط
BACKUP_COMPRESSION=gzip  # gzip, zstd, none

# اختياري: رفع إلى S3
S3_BACKUP_ENABLED=true
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# اختياري: الإشعارات
SLACK_NOTIFICATIONS_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

## 🔐 التشفير | Encryption

### تفعيل التشفير | Enabling Encryption

النسخ الاحتياطية محمية باستخدام تشفير AES-256-CBC مع PBKDF2:

```bash
# في ملف .env
BACKUP_ENCRYPTION_ENABLED=true
BACKUP_ENCRYPTION_KEY=your_strong_encryption_key_here
```

**⚠️ مهم جداً | Critical:**
- احفظ مفتاح التشفير في مكان آمن
- بدون المفتاح، لن تتمكن من استعادة النسخ الاحتياطية
- استخدم مفتاح بطول 32 حرف على الأقل
- لا تشارك المفتاح في نظام التحكم بالإصدارات

### توليد مفتاح تشفير قوي | Generate Strong Key

```bash
# طريقة 1: استخدام OpenSSL
openssl rand -base64 32

# طريقة 2: استخدام /dev/urandom
head -c 32 /dev/urandom | base64

# طريقة 3: استخدام pwgen
pwgen -s 48 1
```

### استعادة النسخ المشفرة | Restoring Encrypted Backups

النسخ المشفرة تُفك تلقائياً عند الاستعادة:

```bash
# المفتاح من البيئة
export BACKUP_ENCRYPTION_KEY=your_key_here
./restore_postgres.sh backup.dump.gz.enc

# أو سيطلب منك المفتاح تفاعلياً
./restore_postgres.sh backup.dump.gz.enc
# Enter encryption key: [سيطلب منك إدخال المفتاح]
```

### فك التشفير يدوياً | Manual Decryption

```bash
# فك تشفير ملف واحد
openssl enc -aes-256-cbc -d -salt -pbkdf2 \
  -in backup.dump.gz.enc \
  -out backup.dump.gz \
  -k "your_encryption_key"

# ثم فك الضغط
gunzip backup.dump.gz
```

## 📊 جدول النسخ الاحتياطي | Backup Schedule

| النوع | التكرار | الوقت | المكونات |
|-------|---------|-------|----------|
| يومي | كل يوم | 2:00 ص | PostgreSQL, Redis, MinIO (متزايد) |
| أسبوعي | الأحد | 3:00 ص | جميع المكونات + SQL dump |
| شهري | أول يوم | 4:00 ص | نسخة كاملة + أرشفة |

## 🔍 المراقبة | Monitoring

### واجهات الويب

- **MinIO Console**: http://localhost:9001
  - إدارة التخزين
  - مراقبة المساحة

- **Backup Monitor**: http://localhost:8082
  - تصفح النسخ الاحتياطية
  - تحميل الملفات

### السجلات

```bash
# سجلات النسخ الاحتياطي
tail -f ../../backups/logs/*.log

# سجلات Docker
docker compose -f docker-compose.backup.yml logs backup-scheduler
```

## 📖 التوثيق الكامل | Full Documentation

للحصول على التوثيق الشامل، راجع:

📄 **docs/backup-strategy.md**

يتضمن:
- استراتيجيات النسخ الاحتياطي المفصلة
- إجراءات الاستعادة الكاملة
- خطة التعافي من الكوارث
- أفضل الممارسات الأمنية

## 🆘 الدعم | Support

للمساعدة والدعم:
- **البريد الإلكتروني**: devops@sahool.com
- **التوثيق**: https://docs.sahool.com/backup
- **المشاكل**: راجع السجلات في `../../backups/logs/`

---

**آخر تحديث**: 2025-12-27
**الإصدار**: 2.0.0
