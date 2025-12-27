# دليل تشغيل Migrations - Field Service

## 📋 الملفات التي تم إنشاؤها

### 1. Database Models & Configuration
- ✅ `src/db_models.py` - Tortoise ORM models للجداول
- ✅ `src/database.py` - TORTOISE_ORM configuration

### 2. Migration Files
- ✅ `src/migrations/__init__.py`
- ✅ `src/migrations/models/__init__.py`
- ✅ `src/migrations/models/0_20251227000000_init.py` - Initial migration

### 3. Configuration Files
- ✅ `aerich.ini` - Aerich configuration (النسخة القصيرة)
- ✅ `pyproject.toml` - Project configuration مع aerich section

## 🚀 طريقة التشغيل

### خطوة 1: التأكد من تشغيل PostgreSQL

```bash
docker-compose up -d postgres
```

### خطوة 2: الدخول إلى container الخدمة

```bash
docker-compose exec field-service sh
# أو إذا لم يكن يعمل:
docker run -it --network sahool-unified-v15-idp_default \
  -v $(pwd)/apps/services/field-service:/app \
  -w /app \
  -e DATABASE_URL="postgres://sahool:sahool@postgres:5432/sahool" \
  python:3.11-slim sh
```

### خطوة 3: تثبيت المكتبات (إذا لزم الأمر)

```bash
pip install -r requirements.txt
```

### خطوة 4: تشغيل Migrations

```bash
# تهيئة Aerich وإنشاء الجداول
aerich init-db

# أو إذا كان قد تم تهيئته مسبقاً:
aerich upgrade
```

## 🔍 التحقق من الجداول

بعد تشغيل migrations، تحقق من إنشاء الجداول:

```bash
# الاتصال بـ PostgreSQL
docker-compose exec postgres psql -U sahool -d sahool

# عرض جميع الجداول
\dt

# عرض بنية جدول معين
\d fields
\d crop_seasons
\d zones
\d ndvi_records

# الخروج
\q
```

## 📊 الجداول المتوقعة

يجب أن ترى الجداول التالية:

1. **fields** - الحقول الزراعية
2. **crop_seasons** - مواسم المحاصيل
3. **zones** - المناطق الفرعية
4. **ndvi_records** - قياسات NDVI
5. **aerich** - جدول تتبع migrations

## 🧪 اختبار Migrations

### اختبار إنشاء بيانات

```python
# في Python shell أو script
from tortoise import Tortoise
from uuid import uuid4
from src.database import TORTOISE_ORM
from src.db_models import Field, CropSeason, Zone, NDVIRecord

# Initialize
await Tortoise.init(config=TORTOISE_ORM)
await Tortoise.generate_schemas()

# Create test field
field = await Field.create(
    id=uuid4(),
    tenant_id="test-tenant",
    user_id="test-user",
    name="حقل تجريبي",
    location={"region": "الجوف", "district": "سكاكا", "village": "القرية الشمالية"},
    area_hectares=10.5,
    soil_type="loam",
    irrigation_source="well"
)

print(f"Created field: {field.name} ({field.id})")

# Query
fields = await Field.filter(tenant_id="test-tenant").all()
print(f"Found {len(fields)} fields")

# Cleanup
await Tortoise.close_connections()
```

## 🔄 إنشاء Migration جديد

بعد تعديل models في `db_models.py`:

```bash
# إنشاء migration تلقائياً
aerich migrate --name "add_new_field_to_table"

# تطبيق Migration
aerich upgrade

# التراجع عن آخر migration (إذا لزم)
aerich downgrade
```

## 🐛 حل المشاكل الشائعة

### مشكلة: `ModuleNotFoundError: No module named 'src'`

**الحل:**
```bash
# تأكد من أنك في المجلد الصحيح
cd /app  # أو apps/services/field-service

# أضف المسار الحالي إلى PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### مشكلة: `Connection refused` عند الاتصال بـ PostgreSQL

**الحل:**
```bash
# تأكد من أن PostgreSQL يعمل
docker-compose ps postgres

# تحقق من اتصال الشبكة
docker-compose exec field-service ping postgres

# تحقق من DATABASE_URL
echo $DATABASE_URL
```

### مشكلة: `aerich.exceptions.NotSupportError`

**الحل:**
```bash
# امسح ملفات aerich القديمة
rm -rf .aerich
rm -f aerich.txt

# أعد التهيئة
aerich init-db
```

## 📝 ملاحظات مهمة

1. **Aerich vs Alembic**: هذا المشروع يستخدم Aerich (لـ Tortoise ORM) وليس Alembic (لـ SQLAlchemy)

2. **Initial Migration**: الملف `0_20251227000000_init.py` يحتوي على SQL مباشر لإنشاء جميع الجداول

3. **JSONB Fields**: الحقول التالية تستخدم JSONB:
   - `fields.location`
   - `fields.boundary`
   - `fields.metadata`
   - `zones.boundary`
   - `ndvi_records.metadata`

4. **Indexes**: تم إنشاء indexes على:
   - `tenant_id`, `user_id`, `field_id`
   - تركيبات مثل `(tenant_id, status)`, `(field_id, date)`

5. **Unique Constraints**:
   - `fields`: لا يمكن تكرار `(tenant_id, name)`
   - `ndvi_records`: لا يمكن تكرار `(field_id, date, source)`

## 🔗 الخطوات التالية

بعد تشغيل migrations بنجاح:

1. **تحديث `main.py`**: قم بتحديث الكود ليستخدم Tortoise ORM بدلاً من in-memory storage

2. **تحديث API endpoints**: استبدل `_fields`, `_seasons`, الخ بـ Tortoise queries

3. **تحديث Tests**: حدّث الـ tests لتستخدم database بدلاً من in-memory

4. **إضافة في Docker**: أضف `aerich upgrade` في startup command

مثال في `docker-compose.yml`:
```yaml
field-service:
  command: sh -c "aerich upgrade && uvicorn src.main:app --host 0.0.0.0 --port 3000"
```

## 📞 دعم

إذا واجهت مشاكل، راجع:
- [Tortoise ORM Documentation](https://tortoise.github.io/)
- [Aerich Documentation](https://github.com/tortoise/aerich)
