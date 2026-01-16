# دليل تكوين قاعدة البيانات - SAHOOL Database Configuration Guide

## نظرة عامة | Overview

هذا الدليل يشرح كيفية تكوين اتصالات قاعدة البيانات لجميع خدمات SAHOOL باستخدام PgBouncer للحصول على أفضل أداء.

## البنية التحتية | Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SAHOOL Services (39+)                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │field-core│ │user-svc │ │iot-svc │ │billing │ │marketplace│       │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬───┘ └─────┬─────┘       │
│       │           │           │           │           │              │
│       └───────────┴───────────┴───────────┴───────────┘              │
│                               │                                       │
│                               ▼                                       │
│                    ┌─────────────────────┐                           │
│                    │     PgBouncer       │                           │
│                    │   (Port: 6432)      │                           │
│                    │  Connection Pooler  │                           │
│                    └──────────┬──────────┘                           │
│                               │                                       │
│                               ▼                                       │
│                    ┌─────────────────────┐                           │
│                    │    PostgreSQL 16    │                           │
│                    │   + PostGIS 3.4     │                           │
│                    │    (Port: 5432)     │                           │
│                    └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────┘
```

## تكوين الاتصال | Connection Configuration

### 1. اتصال مباشر (للتطوير فقط)

```
DATABASE_URL=postgresql://sahool:password@postgres:5432/sahool
```

### 2. اتصال عبر PgBouncer (موصى به للإنتاج)

```
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
```

### 3. اتصال Prisma مع PgBouncer

```
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool?pgbouncer=true&connection_limit=5
```

### 4. اتصال SQLAlchemy مع PgBouncer

```python
# For async (recommended)
DATABASE_URL=postgresql+asyncpg://sahool:password@pgbouncer:6432/sahool

# For sync
DATABASE_URL=postgresql+psycopg2://sahool:password@pgbouncer:6432/sahool
```

## إعدادات PgBouncer | PgBouncer Settings

| الإعداد              | القيمة        | الوصف                               |
| -------------------- | ------------- | ----------------------------------- |
| `pool_mode`          | `transaction` | أفضل لتطبيقات الويب                 |
| `max_client_conn`    | `500`         | الحد الأقصى لاتصالات العملاء        |
| `default_pool_size`  | `20`          | حجم المجمع الافتراضي                |
| `max_db_connections` | `100`         | الحد الأقصى لاتصالات قاعدة البيانات |
| `query_timeout`      | `120`         | مهلة الاستعلام بالثواني             |

## تكوين الخدمات | Service Configuration

### خدمات Prisma (TypeScript)

```prisma
// schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}
```

```env
# .env
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool?pgbouncer=true
```

### خدمات SQLAlchemy (Python)

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# تحويل URL للاتصال غير المتزامن
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

## الفهارس المركبة | Composite Indexes

تم إضافة الفهارس التالية لتحسين الأداء:

### جدول الحقول (fields)

```sql
CREATE INDEX idx_fields_tenant_status ON fields(tenant_id, status);
CREATE INDEX idx_fields_tenant_crop ON fields(tenant_id, crop_type);
CREATE INDEX idx_fields_location ON fields USING GIST(centroid);
```

### جدول المهام (tasks)

```sql
CREATE INDEX idx_tasks_field_status ON tasks(field_id, status);
CREATE INDEX idx_tasks_assignee_due ON tasks(assigned_to, due_date);
CREATE INDEX idx_tasks_tenant_status_date ON tasks(tenant_id, status, due_date);
```

### جدول المستشعرات (sensors)

```sql
CREATE INDEX idx_sensor_readings_sensor_time ON sensor_readings(sensor_id, timestamp DESC);
CREATE INDEX idx_devices_tenant_status ON devices(tenant_id, status);
```

## النسخ الاحتياطي | Backup Strategy

### النسخ الاحتياطي اليومي

```bash
# يتم تشغيله تلقائياً عبر cron
0 2 * * * /scripts/backup_database.sh daily
```

### النسخ الاحتياطي الأسبوعي

```bash
0 3 * * 0 /scripts/backup_database.sh weekly
```

### استعادة النسخة الاحتياطية

```bash
./scripts/restore_database.sh /path/to/backup.sql.gz
```

## مراقبة الأداء | Performance Monitoring

### فحص اتصالات PgBouncer

```sql
-- الاتصال بـ PgBouncer admin
psql -h pgbouncer -p 6432 -U pgbouncer_admin pgbouncer

-- عرض الإحصائيات
SHOW STATS;
SHOW POOLS;
SHOW CLIENTS;
SHOW SERVERS;
```

### فحص الاستعلامات البطيئة

```sql
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '30 seconds'
AND state != 'idle';
```

## استكشاف الأخطاء | Troubleshooting

### خطأ: "too many connections"

```bash
# تحقق من اتصالات PgBouncer
docker exec sahool-pgbouncer psql -p 6432 -U pgbouncer_admin pgbouncer -c "SHOW POOLS;"

# أعد تشغيل PgBouncer إذا لزم الأمر
docker restart sahool-pgbouncer
```

### خطأ: "connection timeout"

```bash
# تحقق من صحة PostgreSQL
docker exec sahool-postgres pg_isready -U sahool

# تحقق من الشبكة
docker network inspect sahool-network
```

## أفضل الممارسات | Best Practices

1. **استخدم PgBouncer دائماً في الإنتاج**
2. **لا تتجاوز 5 اتصالات لكل خدمة**
3. **استخدم `transaction` pool mode**
4. **فعّل `pgbouncer=true` في Prisma**
5. **راقب الاتصالات بانتظام**
