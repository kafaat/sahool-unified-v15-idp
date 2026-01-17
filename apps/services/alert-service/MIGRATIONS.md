# Alert Service Database Migrations Guide

# دليل ترحيل قاعدة البيانات لخدمة التنبيهات

## نظرة عامة | Overview

تم إعداد خدمة التنبيهات للعمل مع قاعدة بيانات PostgreSQL باستخدام:

- **SQLAlchemy**: ORM للتعامل مع قاعدة البيانات
- **Alembic**: إدارة إصدارات قاعدة البيانات (migrations)

The Alert Service has been set up to work with PostgreSQL using:

- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database version control and migrations

## الملفات المُنشأة | Files Created

```
alert-service/
├── alembic.ini                      # إعدادات Alembic
├── requirements.txt                 # تحديث بإضافة SQLAlchemy و Alembic
├── src/
│   ├── db_models.py                # نماذج قاعدة البيانات (جديد)
│   ├── database.py                 # إعدادات قاعدة البيانات (جديد)
│   ├── repository.py               # طبقة الوصول للبيانات (جديد)
│   └── migrations/
│       ├── __init__.py
│       ├── env.py                  # بيئة Alembic
│       ├── script.py.mako          # قالب الـ migrations
│       ├── README.md               # توثيق الـ migrations
│       └── versions/
│           ├── __init__.py
│           └── s16_0001_alerts_initial.py  # Migration الأولي
```

## الجداول | Database Tables

### جدول `alerts` - التنبيهات

يخزن التنبيهات الزراعية والإنذارات للحقول.

**الحقول الرئيسية:**

- `id` (UUID): المعرف الفريد
- `tenant_id` (UUID): معرف المستأجر (multi-tenancy)
- `field_id` (String): معرف الحقل
- `type` (String): نوع التنبيه (weather, pest, disease, irrigation, etc.)
- `severity` (String): مستوى الخطورة (critical, high, medium, low, info)
- `status` (String): الحالة (active, acknowledged, dismissed, resolved, expired)
- `title`, `title_en`: العنوان بالعربية والإنجليزية
- `message`, `message_en`: الرسالة بالعربية والإنجليزية
- `recommendations`, `recommendations_en`: التوصيات (JSONB)
- `metadata`: بيانات إضافية (JSONB)
- `created_at`, `expires_at`, `acknowledged_at`, `dismissed_at`, `resolved_at`: التواريخ

**الفهارس:**

- `ix_alerts_field_status`: للبحث بالحقل والحالة
- `ix_alerts_tenant_created`: للبحث بالمستأجر
- `ix_alerts_type_severity`: للتصفية بالنوع والخطورة
- `ix_alerts_active`: للتنبيهات النشطة
- `ix_alerts_source`: لتتبع المصدر

### جدول `alert_rules` - قواعد التنبيه

يخزن قواعد التنبيه الآلي.

**الحقول الرئيسية:**

- `id` (UUID): المعرف الفريد
- `tenant_id` (UUID): معرف المستأجر
- `field_id` (String): معرف الحقل
- `name`, `name_en`: اسم القاعدة
- `enabled` (Boolean): حالة التفعيل
- `condition` (JSONB): شروط القاعدة
- `alert_config` (JSONB): إعدادات التنبيه
- `cooldown_hours` (Integer): فترة الانتظار قبل التكرار
- `last_triggered_at`: آخر وقت تم تفعيل القاعدة فيه

**الفهارس:**

- `ix_alert_rules_field`: للبحث بالحقل
- `ix_alert_rules_tenant`: للبحث بالمستأجر
- `ix_alert_rules_enabled`: للقواعد المفعلة

## التثبيت | Installation

### 1. تثبيت المتطلبات

```bash
cd apps/services/alert-service
pip install -r requirements.txt
```

المكتبات الجديدة:

- `sqlalchemy==2.0.23`
- `alembic==1.13.1`
- `psycopg2-binary==2.9.9`

### 2. إعداد قاعدة البيانات

```bash
# إنشاء قاعدة بيانات PostgreSQL
createdb sahool_alerts

# أو باستخدام psql
psql -U postgres -c "CREATE DATABASE sahool_alerts;"
```

### 3. ضبط متغير البيئة

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sahool_alerts"
```

أو في ملف `.env`:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sahool_alerts
```

## تشغيل الـ Migrations | Running Migrations

### ترقية قاعدة البيانات (Upgrade)

```bash
cd apps/services/alert-service

# تطبيق جميع الـ migrations
alembic upgrade head

# أو تطبيق migration محددة
alembic upgrade s16_0001
```

### التراجع (Downgrade)

```bash
# التراجع خطوة واحدة
alembic downgrade -1

# التراجع إلى migration محددة
alembic downgrade s16_0001

# التراجع لبداية (حذف كل شيء)
alembic downgrade base
```

### عرض الحالة

```bash
# عرض الإصدار الحالي
alembic current

# عرض السجل
alembic history

# عرض التفاصيل
alembic history --verbose
```

## إنشاء Migration جديدة | Creating New Migrations

### إنشاء تلقائي من التغييرات في Models

```bash
# سيقوم Alembic بمقارنة models مع قاعدة البيانات
alembic revision --autogenerate -m "Add new field to alerts"
```

### إنشاء يدوي

```bash
# لإنشاء migration فارغة
alembic revision -m "Custom data migration"
```

ثم قم بتعديل الملف المُنشأ في `src/migrations/versions/`

## الاستخدام في الكود | Usage in Code

### الاتصال بقاعدة البيانات

```python
from src.database import get_db
from sqlalchemy.orm import Session

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    # استخدام db هنا
    alerts = db.query(Alert).all()
    return alerts
```

### استخدام Repository Layer

```python
from src.repository import get_alerts_by_field, create_alert
from src.db_models import Alert
from uuid import uuid4

# إنشاء تنبيه
alert = Alert(
    id=uuid4(),
    field_id="field_123",
    type="weather",
    severity="high",
    title="تنبيه طقس",
    message="عاصفة متوقعة"
)
created = create_alert(db, alert)

# جلب تنبيهات حقل
alerts, total = get_alerts_by_field(
    db,
    field_id="field_123",
    status="active",
    skip=0,
    limit=10
)
```

### التحقق من الاتصال

```python
from src.database import check_db_connection

if check_db_connection():
    print("Database connected!")
else:
    print("Database connection failed!")
```

## أفضل الممارسات | Best Practices

### 1. دائماً اختبر في Development أولاً

```bash
# استخدم قاعدة بيانات منفصلة للتطوير
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sahool_alerts_dev"
alembic upgrade head
```

### 2. لا تعدل Migrations القديمة

إذا احتجت تغيير، أنشئ migration جديدة.

### 3. دائماً قدم upgrade و downgrade

```python
def upgrade() -> None:
    op.add_column('alerts', sa.Column('new_field', sa.String()))

def downgrade() -> None:
    op.drop_column('alerts', 'new_field')
```

### 4. اختبر downgrade

```bash
# تطبيق
alembic upgrade head

# اختبر التراجع
alembic downgrade -1

# أعد التطبيق
alembic upgrade head
```

### 5. استخدم Transactions لـ Data Migrations

```python
from alembic import op

def upgrade():
    connection = op.get_bind()
    connection.execute("UPDATE alerts SET status='active' WHERE status IS NULL")
```

## حل المشاكل | Troubleshooting

### Migration تفشل بخطأ "relation already exists"

```bash
# إذا كانت الجداول موجودة بالفعل، ضع علامة كـ migrated
alembic stamp head
```

### DATABASE_URL غير موجود

تأكد من ضبط متغير البيانات:

```bash
echo $DATABASE_URL
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

### خطأ في الاتصال بـ PostgreSQL

```bash
# تأكد من تشغيل PostgreSQL
sudo systemctl status postgresql

# اختبر الاتصال
psql -U postgres -d sahool_alerts -c "SELECT 1;"
```

### عرض SQL المُنفذ

```bash
# تفعيل logging في alembic.ini
# غير level من WARN إلى INFO
[logger_sqlalchemy]
level = INFO
```

## Docker Support

إذا كنت تستخدم Docker:

```dockerfile
# في Dockerfile
RUN pip install -r requirements.txt

# في docker-compose.yml أو entrypoint.sh
alembic upgrade head
```

## الأمان | Security

### 1. لا تحفظ كلمات المرور في الكود

استخدم متغيرات البيئة فقط.

### 2. استخدم SSL للإنتاج

```python
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
```

### 3. قيّد صلاحيات المستخدم

أنشئ مستخدم خاص بالتطبيق مع صلاحيات محدودة:

```sql
CREATE USER alert_service WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE sahool_alerts TO alert_service;
GRANT USAGE ON SCHEMA public TO alert_service;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO alert_service;
```

## الخلاصة | Summary

تم إعداد خدمة التنبيهات بنجاح مع:

- ✅ نماذج SQLAlchemy (`db_models.py`)
- ✅ إعدادات قاعدة البيانات (`database.py`)
- ✅ طبقة Repository (`repository.py`)
- ✅ Alembic migrations
- ✅ Initial migration للجداول
- ✅ توثيق شامل

للبدء:

```bash
cd apps/services/alert-service
pip install -r requirements.txt
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sahool_alerts"
createdb sahool_alerts
alembic upgrade head
python -m src.main
```

## المراجع | References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI with SQLAlchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
