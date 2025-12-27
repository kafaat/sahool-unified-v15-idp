# Field Service Migrations

## دليل استخدام Aerich للـ Migrations

### المتطلبات الأولية

تأكد من تثبيت المكتبات المطلوبة:
```bash
pip install tortoise-orm aerich asyncpg
```

### هيكل المجلدات

```
field-service/
├── src/
│   ├── db_models.py          # Tortoise ORM models
│   ├── database.py           # TORTOISE_ORM configuration
│   └── migrations/
│       ├── __init__.py
│       └── models/
│           ├── __init__.py
│           └── 0_20251227000000_init.py  # Initial migration
├── aerich.ini                # Aerich configuration
└── pyproject.toml            # Project configuration with aerich section
```

### إعداد قاعدة البيانات

#### 1. متغيرات البيئة

تأكد من تعيين `DATABASE_URL`:
```bash
export DATABASE_URL="postgres://sahool:sahool@postgres:5432/sahool"
```

#### 2. تهيئة Aerich (مرة واحدة فقط)

```bash
cd apps/services/field-service
aerich init-db
```

هذا الأمر سينشئ:
- الجداول في قاعدة البيانات
- ملف `aerich.txt` لتتبع حالة migrations

### تشغيل Migrations

#### تطبيق جميع Migrations

```bash
aerich upgrade
```

#### التحقق من حالة Migrations

```bash
aerich heads
```

#### إنشاء migration جديد (بعد تعديل models)

```bash
aerich migrate --name "description_of_change"
```

#### التراجع عن migration

```bash
aerich downgrade
```

### الجداول المنشأة

#### 1. fields
حقول زراعية مع معلومات الموقع والحدود الجغرافية

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | معرف الحقل |
| tenant_id | VARCHAR(64) | معرف المستأجر |
| user_id | VARCHAR(64) | معرف المزارع |
| name | VARCHAR(200) | اسم الحقل |
| location | JSONB | موقع الحقل |
| boundary | JSONB | حدود الحقل (GeoJSON) |
| area_hectares | FLOAT | المساحة بالهكتار |
| soil_type | VARCHAR(30) | نوع التربة |
| irrigation_source | VARCHAR(30) | مصدر الري |

#### 2. crop_seasons
مواسم المحاصيل المزروعة

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | معرف الموسم |
| field_id | UUID | معرف الحقل |
| crop_type | VARCHAR(100) | نوع المحصول |
| planting_date | DATE | تاريخ الزراعة |
| harvest_date | DATE | تاريخ الحصاد |
| status | VARCHAR(20) | حالة الموسم |
| actual_yield_kg | FLOAT | الإنتاج الفعلي |

#### 3. zones
مناطق فرعية داخل الحقول

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | معرف المنطقة |
| field_id | UUID | معرف الحقل |
| name | VARCHAR(100) | اسم المنطقة |
| boundary | JSONB | حدود المنطقة |
| purpose | VARCHAR(50) | غرض التقسيم |

#### 4. ndvi_records
سجلات قياسات NDVI

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | معرف السجل |
| field_id | UUID | معرف الحقل |
| date | DATE | تاريخ القياس |
| mean | FLOAT | متوسط NDVI |
| min | FLOAT | أدنى NDVI |
| max | FLOAT | أقصى NDVI |
| source | VARCHAR(50) | مصدر البيانات |

### استخدام Models في الكود

```python
from tortoise import Tortoise
from src.database import TORTOISE_ORM
from src.db_models import Field, CropSeason, Zone, NDVIRecord

# Initialize Tortoise
await Tortoise.init(config=TORTOISE_ORM)

# Create a field
field = await Field.create(
    id=uuid4(),
    tenant_id="tenant-123",
    user_id="user-456",
    name="حقل الزيتون الشمالي",
    location={"region": "الجوف", "district": "سكاكا"},
    area_hectares=5.5,
    soil_type="loam",
    irrigation_source="well"
)

# Query fields
fields = await Field.filter(tenant_id="tenant-123", status="active")

# Update field
await Field.filter(id=field_id).update(status="inactive")

# Delete field
await Field.filter(id=field_id).delete()
```

### ملاحظات مهمة

1. **JSONB Fields**: الحقول `location`, `boundary`, `metadata` تستخدم JSONB لتخزين بيانات معقدة
2. **Indexes**: تم إنشاء indexes على الحقول الأكثر استخداماً في الاستعلامات
3. **Unique Constraints**:
   - `fields`: (tenant_id, name) - لا يمكن تكرار اسم حقل لنفس المستأجر
   - `ndvi_records`: (field_id, date, source) - لا يمكن تكرار قياس NDVI لنفس اليوم والمصدر
4. **Timestamps**: جميع الجداول تحتوي على `created_at` و`updated_at` (ما عدا ndvi_records)

### إعادة إنشاء قاعدة البيانات (للتطوير فقط)

```bash
# حذف قاعدة البيانات وإعادة إنشائها
aerich init-db
```

⚠️ **تحذير**: هذا سيحذف جميع البيانات!

### التكامل مع Docker

في `docker-compose.yml`:
```yaml
services:
  field-service:
    command: >
      sh -c "
        aerich upgrade &&
        uvicorn src.main:app --host 0.0.0.0 --port 3000
      "
```
