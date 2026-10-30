# Alert Service - Quick Start Guide

# دليل البدء السريع لخدمة التنبيهات

## الإعداد السريع | Quick Setup

### 1. تثبيت المتطلبات

```bash
cd apps/services/alert-service
pip install -r requirements.txt
```

### 2. إعداد قاعدة البيانات

```bash
# إنشاء قاعدة بيانات PostgreSQL
createdb sahool_alerts

# ضبط متغير البيئة
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sahool_alerts"
```

### 3. تطبيق Migrations

```bash
# تطبيق جميع الترحيلات
alembic upgrade head

# التحقق من الحالة
alembic current
```

### 4. تشغيل الخدمة

```bash
# تشغيل الخدمة
python -m src.main

# أو باستخدام uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8113 --reload
```

### 5. اختبار الخدمة

```bash
# التحقق من صحة الخدمة
curl http://localhost:8113/health

# عرض الوثائق التفاعلية
open http://localhost:8113/docs
```

## الأوامر الأساسية | Basic Commands

### إدارة Migrations

```bash
# عرض الحالة الحالية
alembic current

# عرض السجل
alembic history

# الترقية
alembic upgrade head

# التراجع خطوة واحدة
alembic downgrade -1

# التراجع الكامل
alembic downgrade base
```

### إنشاء Migration جديدة

```bash
# توليد تلقائي من التغييرات
alembic revision --autogenerate -m "وصف التغيير"

# إنشاء يدوي
alembic revision -m "وصف التغيير"
```

## أمثلة الاستخدام | Usage Examples

### تشغيل الأمثلة

```bash
# تشغيل ملف الأمثلة
python example_usage.py
```

### استخدام في الكود

```python
from src.database import SessionLocal
from src.db_models import Alert
from src import repository
from uuid import uuid4

# إنشاء session
db = SessionLocal()

# إنشاء تنبيه
alert = Alert(
    id=uuid4(), field_id="field_123", type="weather", severity="high", title="تنبيه طقس", message="عاصفة متوقعة"
)
created = repository.create_alert(db, alert)
db.commit()

# جلب تنبيهات
alerts, total = repository.get_alerts_by_field(db, field_id="field_123", status="active")

# إغلاق session
db.close()
```

## بنية المشروع | Project Structure

```
alert-service/
├── alembic.ini                 # إعدادات Alembic
├── requirements.txt            # المتطلبات
├── MIGRATIONS.md              # دليل Migrations المفصل
├── QUICKSTART.md              # هذا الملف
├── example_usage.py           # أمثلة الاستخدام
├── src/
│   ├── main.py               # التطبيق الرئيسي
│   ├── models.py             # Pydantic models (API)
│   ├── db_models.py          # SQLAlchemy models (Database)
│   ├── database.py           # إعدادات قاعدة البيانات
│   ├── repository.py         # طبقة الوصول للبيانات
│   ├── events.py             # NATS events
│   └── migrations/
│       ├── env.py
│       └── versions/
│           └── s16_0001_alerts_initial.py
```

## نقاط النهاية (Endpoints) | API Endpoints

### Health Checks

- `GET /health` - فحص الصحة مع التبعيات
- `GET /healthz` - Kubernetes liveness probe
- `GET /readyz` - Kubernetes readiness probe

### Alerts

- `POST /alerts` - إنشاء تنبيه
- `GET /alerts/{alert_id}` - جلب تنبيه محدد
- `GET /alerts/field/{field_id}` - جلب تنبيهات حقل
- `PATCH /alerts/{alert_id}` - تحديث تنبيه
- `DELETE /alerts/{alert_id}` - حذف تنبيه
- `POST /alerts/{alert_id}/acknowledge` - إقرار بتنبيه
- `POST /alerts/{alert_id}/resolve` - حل تنبيه
- `POST /alerts/{alert_id}/dismiss` - رفض تنبيه

### Alert Rules

- `POST /alerts/rules` - إنشاء قاعدة
- `GET /alerts/rules` - جلب القواعد
- `DELETE /alerts/rules/{rule_id}` - حذف قاعدة

### Statistics

- `GET /alerts/stats` - إحصائيات التنبيهات

## متغيرات البيئة | Environment Variables

```bash
# قاعدة البيانات (مطلوب)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# NATS (اختياري)
NATS_URL=nats://localhost:4222

# المنفذ (اختياري، افتراضي: 8113)
PORT=8113
```

## استكشاف الأخطاء | Troubleshooting

### خطأ في الاتصال بقاعدة البيانات

```bash
# التحقق من PostgreSQL
sudo systemctl status postgresql

# اختبار الاتصال
psql -U postgres -d sahool_alerts -c "SELECT 1;"
```

### Migration تفشل

```bash
# عرض التفاصيل
alembic current -v

# وضع علامة على الحالة الحالية
alembic stamp head
```

### استعادة قاعدة البيانات

```bash
# حذف كل شيء
alembic downgrade base

# إعادة التطبيق
alembic upgrade head
```

## الخطوات التالية | Next Steps

1. ✅ قراءة [MIGRATIONS.md](MIGRATIONS.md) للتفاصيل الكاملة
2. ✅ تشغيل [example_usage.py](example_usage.py) للتعلم
3. ✅ استكشاف [/docs](http://localhost:8113/docs) للوثائق التفاعلية
4. ✅ دمج مع الخدمات الأخرى (NDVI, Weather, IoT)

## الدعم | Support

- 📖 التوثيق: `MIGRATIONS.md`
- 💻 الأمثلة: `example_usage.py`
- 🔍 API Docs: `http://localhost:8113/docs`
- 📝 الكود: `src/`

## الإصدار | Version

- **Service**: Alert Service v16.0.0
- **Migration**: s16_0001 (Initial)
- **Date**: 2025-12-27
