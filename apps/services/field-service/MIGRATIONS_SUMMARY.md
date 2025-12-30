# ملخص Migrations - Field Service

تم إنشاء جميع الملفات المطلوبة لـ database migrations باستخدام Tortoise ORM و Aerich.

## 📁 الملفات التي تم إنشاؤها

### 1. Database Configuration & Models

| الملف | الوصف | المسار الكامل |
|------|-------|---------------|
| `database.py` | TORTOISE_ORM configuration | `/home/user/sahool-unified-v15-idp/apps/services/field-service/src/database.py` |
| `db_models.py` | Tortoise ORM models (4 models) | `/home/user/sahool-unified-v15-idp/apps/services/field-service/src/db_models.py` |

### 2. Migration Files

| الملف | الوصف | المسار الكامل |
|------|-------|---------------|
| `migrations/__init__.py` | Package initializer | `/home/user/sahool-unified-v15-idp/apps/services/field-service/src/migrations/__init__.py` |
| `migrations/models/__init__.py` | Models package initializer | `/home/user/sahool-unified-v15-idp/apps/services/field-service/src/migrations/models/__init__.py` |
| `0_20251227000000_init.py` | Initial migration (150 lines) | `/home/user/sahool-unified-v15-idp/apps/services/field-service/src/migrations/models/0_20251227000000_init.py` |

### 3. Configuration Files

| الملف | الوصف | المسار الكامل |
|------|-------|---------------|
| `aerich.ini` | Aerich configuration (INI format) | `/home/user/sahool-unified-v15-idp/apps/services/field-service/aerich.ini` |
| `pyproject.toml` | Project & Aerich configuration | `/home/user/sahool-unified-v15-idp/apps/services/field-service/pyproject.toml` |

### 4. Documentation

| الملف | الوصف | المسار الكامل |
|------|-------|---------------|
| `migrations/README.md` | Migration usage guide | `/home/user/sahool-unified-v15-idp/apps/services/field-service/src/migrations/README.md` |
| `MIGRATION_GUIDE.md` | Complete migration guide | `/home/user/sahool-unified-v15-idp/apps/services/field-service/MIGRATION_GUIDE.md` |

## 🗄️ Database Models

تم إنشاء 4 نماذج في `db_models.py`:

### 1. Field (حقل زراعي)
```python
class Field(Model):
    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    user_id = fields.CharField(max_length=64, index=True)
    name = fields.CharField(max_length=200)
    name_en = fields.CharField(max_length=200, null=True)
    status = fields.CharField(max_length=20, default="active")
    location = fields.JSONField()  # FieldLocation
    boundary = fields.JSONField(null=True)  # GeoPolygon
    area_hectares = fields.FloatField()
    soil_type = fields.CharField(max_length=30, default="unknown")
    irrigation_source = fields.CharField(max_length=30, default="none")
    current_crop = fields.CharField(max_length=100, null=True)
    metadata = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
```

**Constraints:**
- Unique: `(tenant_id, name)`
- Indexes: `tenant_id`, `user_id`, `(tenant_id, user_id)`, `(tenant_id, status)`, `(user_id, status)`

### 2. CropSeason (موسم محصول)
```python
class CropSeason(Model):
    id = fields.UUIDField(pk=True)
    field_id = fields.UUIDField(index=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    crop_type = fields.CharField(max_length=100)
    variety = fields.CharField(max_length=100, null=True)
    planting_date = fields.DateField()
    expected_harvest = fields.DateField(null=True)
    harvest_date = fields.DateField(null=True)
    status = fields.CharField(max_length=20, default="planning")
    expected_yield_kg = fields.FloatField(null=True)
    actual_yield_kg = fields.FloatField(null=True)
    quality_grade = fields.CharField(max_length=50, null=True)
    seed_source = fields.CharField(max_length=200, null=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
```

**Indexes:** `field_id`, `tenant_id`, `(field_id, status)`, `(tenant_id, crop_type)`, `planting_date`

### 3. Zone (منطقة فرعية)
```python
class Zone(Model):
    id = fields.UUIDField(pk=True)
    field_id = fields.UUIDField(index=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    name = fields.CharField(max_length=100)
    name_ar = fields.CharField(max_length=100, null=True)
    boundary = fields.JSONField()  # GeoPolygon
    area_hectares = fields.FloatField()
    purpose = fields.CharField(max_length=50)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
```

**Indexes:** `field_id`, `tenant_id`

### 4. NDVIRecord (سجل NDVI)
```python
class NDVIRecord(Model):
    id = fields.UUIDField(pk=True)
    field_id = fields.UUIDField(index=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    date = fields.DateField(index=True)
    mean = fields.FloatField()
    min = fields.FloatField()
    max = fields.FloatField()
    std = fields.FloatField(null=True)
    cloud_cover_pct = fields.FloatField(null=True)
    source = fields.CharField(max_length=50, null=True)
    metadata = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
```

**Constraints:**
- Unique: `(field_id, date, source)`
- Indexes: `field_id`, `tenant_id`, `(field_id, date)`, `(tenant_id, date)`

## 🔧 Configuration Files

### aerich.ini
```ini
[aerich]
tortoise_orm = src.database.TORTOISE_ORM
location = ./src/migrations
src_folder = ./src
```

### pyproject.toml
```toml
[tool.aerich]
tortoise_orm = "src.database.TORTOISE_ORM"
location = "./src/migrations"
src_folder = "./src"

[project]
name = "field-service"
version = "1.0.0"
description = "SAHOOL Field Service - خدمة الحقول الزراعية"
```

## 🚀 كيفية التشغيل

### الطريقة 1: تشغيل مباشر

```bash
cd apps/services/field-service
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/sahool"
aerich init-db
```

### الطريقة 2: داخل Docker

```bash
docker-compose exec field-service sh
aerich upgrade
```

### الطريقة 3: Automated في Docker Compose

أضف في `docker-compose.yml`:
```yaml
field-service:
  command: sh -c "aerich upgrade && uvicorn src.main:app --host 0.0.0.0 --port 3000"
```

## ✅ التحقق من النجاح

بعد تشغيل migrations:

```bash
# اتصل بـ PostgreSQL
docker-compose exec postgres psql -U sahool -d sahool

# عرض الجداول
\dt

# يجب أن ترى:
# - fields
# - crop_seasons
# - zones
# - ndvi_records
# - aerich (جدول تتبع migrations)
```

## 📊 Database Schema

```
fields
├── id (UUID, PK)
├── tenant_id (VARCHAR(64), indexed)
├── user_id (VARCHAR(64), indexed)
├── name (VARCHAR(200))
├── location (JSONB)
├── boundary (JSONB, nullable)
├── area_hectares (FLOAT)
└── ... (12 more columns)

crop_seasons
├── id (UUID, PK)
├── field_id (UUID, indexed)
├── tenant_id (VARCHAR(64), indexed)
├── crop_type (VARCHAR(100))
├── planting_date (DATE)
└── ... (11 more columns)

zones
├── id (UUID, PK)
├── field_id (UUID, indexed)
├── name (VARCHAR(100))
├── boundary (JSONB)
└── ... (7 more columns)

ndvi_records
├── id (UUID, PK)
├── field_id (UUID, indexed)
├── date (DATE)
├── mean, min, max (FLOAT)
└── ... (7 more columns)
```

## 🔍 ميزات Migrations

1. **Idempotent**: يمكن تشغيل `upgrade` أكثر من مرة بأمان (CREATE IF NOT EXISTS)
2. **Reversible**: يمكن التراجع باستخدام `downgrade`
3. **Comments**: جميع الجداول والأعمدة مشروحة بالعربية
4. **Indexes**: indexes محسّنة للـ queries الشائعة
5. **JSONB**: استخدام JSONB لبيانات GeoJSON والـ metadata
6. **Constraints**: unique constraints لمنع البيانات المكررة

## 📝 الخطوات التالية

1. ✅ تشغيل migrations: `aerich init-db` أو `aerich upgrade`
2. 🔄 تحديث `main.py` لاستخدام Tortoise ORM بدلاً من in-memory storage
3. 🧪 تحديث tests لاستخدام database
4. 🐳 إضافة `aerich upgrade` في Docker startup command

## 🆘 دعم

راجع الملفات التالية للمزيد من المعلومات:
- `/src/migrations/README.md` - دليل استخدام Migrations
- `/MIGRATION_GUIDE.md` - دليل شامل مع حلول المشاكل

## ✨ ملخص الإنجاز

- ✅ 2 ملفات Python (database.py, db_models.py)
- ✅ 3 ملفات migrations (__init__.py files + initial migration)
- ✅ 2 ملفات configuration (aerich.ini, pyproject.toml)
- ✅ 2 ملفات documentation (README.md, MIGRATION_GUIDE.md)
- ✅ **المجموع: 9 ملفات جديدة**
- ✅ **4 جداول في قاعدة البيانات**
- ✅ **150 سطر SQL في initial migration**
