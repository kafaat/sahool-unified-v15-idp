# Redis High Availability Infrastructure

# البنية التحتية للتوافر العالي لـ Redis

## نظرة عامة | Overview

هذا المجلد يحتوي على جميع ملفات التكوين والسكريبتات اللازمة لإعداد وإدارة **Redis Sentinel** للتوافر العالي.

This directory contains all configuration files and scripts needed to setup and manage **Redis Sentinel** for high availability.

---

## محتويات المجلد | Directory Contents

```
infra/redis-ha/
├── config/
│   └── sentinel.conf          # تكوين Sentinel
├── .env.example               # مثال متغيرات البيئة
├── docker-compose.override.example.yml  # مثال تخصيص Docker Compose
├── health-check.sh            # سكريبت فحص الصحة
├── test-failover.sh           # سكريبت اختبار Failover
├── Makefile                   # أوامر الإدارة
├── QUICKSTART.md              # دليل البدء السريع
├── prometheus-redis-exporter.yml  # تكوين Prometheus
└── README.md                  # هذا الملف
```

---

## البدء السريع | Quick Start

```bash
# 1. إعداد البيئة
make setup

# 2. تحديث كلمة المرور في .env
nano .env

# 3. بدء النظام
make start

# 4. فحص الصحة
make health
```

للمزيد من التفاصيل، راجع [QUICKSTART.md](./QUICKSTART.md)

---

## الملفات الرئيسية | Main Files

### docker-compose.redis-ha.yml

ملف Docker Compose الرئيسي الذي يحتوي على:

- Redis Master (1)
- Redis Replicas (2)
- Redis Sentinels (3)
- Redis Exporter (للمراقبة)

**الموقع:** `/docker-compose.redis-ha.yml` (في جذر المشروع)

### health-check.sh

سكريبت شامل لفحص صحة النظام:

- فحص Master
- فحص Replicas
- فحص Sentinels
- عرض معلومات Replication

```bash
./health-check.sh
```

### test-failover.sh

سكريبت اختبار تلقائي لعملية Failover:

- إيقاف Master
- مراقبة Failover
- التحقق من البيانات
- إعادة تشغيل Master

```bash
./test-failover.sh
```

### Makefile

أوامر سهلة لإدارة النظام:

```bash
make help        # عرض جميع الأوامر
make start       # بدء النظام
make stop        # إيقاف النظام
make restart     # إعادة التشغيل
make status      # عرض الحالة
make logs        # عرض السجلات
make health      # فحص الصحة
make test-failover  # اختبار Failover
make backup      # نسخ احتياطي
make info        # معلومات النظام
```

---

## الهندسة المعمارية | Architecture

```
Application Layer
     │
     ├─── Python App ──────┐
     ├─── Node.js App ─────┼──► Sentinel Client Library
     └─── Other Apps ──────┘         │
                                     ▼
                          ┌──────────────────────┐
                          │   Sentinel Cluster   │
                          │  (3 instances)       │
                          │   Quorum = 2         │
                          └──────────┬───────────┘
                                     │
                          ┌──────────┴──────────┐
                          │  Automatic Failover │
                          └──────────┬──────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
        ┌──────────┐          ┌──────────┐          ┌──────────┐
        │  Master  │──sync───▶│Replica 1 │          │Replica 2 │
        │ Port 6379│          │Port 6380 │◀──sync───│Port 6381 │
        └──────────┘          └──────────┘          └──────────┘
             │
             └──► Redis Exporter (Port 9121) ──► Prometheus
```

---

## المنافذ | Ports

| الخدمة          | المنفذ | الوصف             |
| --------------- | ------ | ----------------- |
| Redis Master    | 6379   | Master الرئيسي    |
| Redis Replica 1 | 6380   | نسخة احتياطية 1   |
| Redis Replica 2 | 6381   | نسخة احتياطية 2   |
| Sentinel 1      | 26379  | مراقب 1           |
| Sentinel 2      | 26380  | مراقب 2           |
| Sentinel 3      | 26381  | مراقب 3           |
| Redis Exporter  | 9121   | مقاييس Prometheus |

---

## التكوين | Configuration

### متغيرات البيئة الأساسية

```bash
# كلمة مرور Redis (مطلوبة)
REDIS_PASSWORD=your_secure_password

# اسم المجموعة
REDIS_MASTER_NAME=sahool-master

# Quorum (الحد الأدنى من Sentinels للموافقة على Failover)
REDIS_SENTINEL_QUORUM=2

# مهلة اعتبار Master معطلاً (ميلي ثانية)
REDIS_SENTINEL_DOWN_AFTER=5000

# مهلة Failover (ميلي ثانية)
REDIS_SENTINEL_FAILOVER_TIMEOUT=10000
```

### تخصيص التكوين

لتخصيص التكوين، انسخ ملف المثال:

```bash
cp docker-compose.override.example.yml docker-compose.override.yml
```

ثم عدّل حسب احتياجاتك.

---

## المراقبة | Monitoring

### Prometheus

أضف التكوين التالي إلى `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "redis"
    static_configs:
      - targets: ["localhost:9121"]
```

راجع [prometheus-redis-exporter.yml](./prometheus-redis-exporter.yml) للتكوين الكامل.

### Grafana

استورد لوحة Redis Dashboard:

- Dashboard ID: 11835 (Redis Dashboard for Prometheus)
- Dashboard ID: 763 (Redis Sentinel)

### السجلات | Logs

```bash
# جميع الخدمات
make logs

# Master فقط
make logs-master

# Sentinels فقط
make logs-sentinel
```

---

## الصيانة | Maintenance

### النسخ الاحتياطي | Backup

```bash
# نسخ احتياطي يدوي
make backup

# جدولة نسخ احتياطي تلقائي (Cron)
0 2 * * * cd /path/to/infra/redis-ha && make backup
```

### الاستعادة | Restore

```bash
make restore
# ثم اختر ملف النسخة الاحتياطية
```

### التحديث | Update

```bash
# سحب أحدث صورة
docker-compose -f ../../docker-compose.redis-ha.yml pull

# إعادة التشغيل
make restart
```

---

## الأمان | Security

### أفضل الممارسات

1. **كلمة مرور قوية**: استخدم كلمة مرور قوية ومعقدة

   ```bash
   REDIS_PASSWORD=$(openssl rand -base64 32)
   ```

2. **تقييد الوصول**: استخدم localhost فقط في الإنتاج

   ```yaml
   ports:
     - "127.0.0.1:6379:6379" # ✓ آمن
   ```

3. **تشفير الاتصال**: فعّل TLS في الإنتاج (يتطلب تكوين إضافي)

4. **Firewall**: قيّد الوصول للمنافذ

5. **النسخ الاحتياطي**: احفظ النسخ الاحتياطية في مكان آمن

---

## استكشاف الأخطاء | Troubleshooting

### المشكلة: Sentinel لا يكتشف Master

```bash
# التحقق من الشبكة
docker network inspect sahool-redis-ha-network

# فحص تكوين Sentinel
docker exec sahool-redis-sentinel-1 cat /tmp/sentinel.conf
```

### المشكلة: Replication لا يعمل

```bash
# فحص حالة Replication
make info

# فحص سجلات Replica
docker logs sahool-redis-replica-1
```

### المشكلة: ذاكرة ممتلئة

```bash
# زيادة maxmemory في docker-compose.yml
# أو تنظيف البيانات القديمة
redis-cli -a $REDIS_PASSWORD FLUSHDB
```

---

## الموارد | Resources

- [Redis Sentinel Documentation](https://redis.io/docs/management/sentinel/)
- [Shared Cache Module](../../shared/cache/README.md)
- [Python Examples](../../shared/cache/examples.py)
- [TypeScript Examples](../../shared/cache/examples.ts)

---

## الدعم | Support

للمساعدة أو الإبلاغ عن مشكلة:

- 📧 Email: support@sahool.platform
- 📝 GitHub Issues
- 📖 Documentation: docs.sahool.platform

---

**تم إنشاؤه بواسطة فريق منصة صحول | Created by Sahool Platform Team**
