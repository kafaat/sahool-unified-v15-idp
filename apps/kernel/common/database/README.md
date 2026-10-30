# SAHOOL Database Management

# إدارة قاعدة بيانات SAHOOL

Comprehensive database migration and seeding utilities for the SAHOOL agricultural platform.
أدوات شاملة لهجرة وتعبئة قاعدة البيانات لمنصة SAHOOL الزراعية.

## Overview / نظرة عامة

This package provides:
توفر هذه الحزمة:

- **Migration Management** / **إدارة الهجرة**: Alembic-based schema version control
- **PostGIS Support** / **دعم PostGIS**: Spatial data capabilities for field mapping
- **Data Seeding** / **تعبئة البيانات**: Sample data for development and testing
- **Checksum Validation** / **التحقق من Checksum**: Ensure migration integrity

## Directory Structure / هيكل الدليل

```
database/
├── migrations.py              # Migration manager / مدير الهجرة
├── migrations/                # Migration scripts / نصوص الهجرة
│   ├── env.py                # Alembic environment / بيئة Alembic
│   ├── script.py.mako        # Migration template / قالب الهجرة
│   ├── README.md             # Migration docs / وثائق الهجرة
│   └── versions/             # Migration versions / إصدارات الهجرة
│       ├── 001_initial_schema.py
│       └── 002_add_postgis.py
├── seeds/                     # Data seeders / أدوات التعبئة
│   ├── __init__.py
│   └── development.py        # Development data / بيانات التطوير
└── README.md                 # This file / هذا الملف
```

## Quick Start / البدء السريع

### 1. Setup / الإعداد

```python
from apps.kernel.common.database import MigrationManager

# Create migration manager / إنشاء مدير الهجرة
manager = MigrationManager(
    database_url="postgresql://user:password@localhost/sahool"
)
```

### 2. Run Migrations / تشغيل الهجرات

```python
# Migrate to latest version / الترقية إلى أحدث إصدار
result = manager.run_migrations()
print(f"Migration completed in {result['execution_time_ms']}ms")

# Check migration status / التحقق من حالة الهجرة
status = manager.get_migration_status()
print(f"Current version: {status['current_revision']}")
print(f"Pending migrations: {status['pending_migrations']}")
```

### 3. Seed Development Data / تعبئة بيانات التطوير

```python
# Seed database with sample data / تعبئة قاعدة البيانات ببيانات نموذجية
result = manager.seed_data(environment="development")

if result['success']:
    print(f"Created {result['fields']} fields in {result['farms']} farms")
    print(f"تم إنشاء {result['fields']} حقل في {result['farms']} مزرعة")
```

## Features / الميزات

### Migration Management / إدارة الهجرة

#### Create New Migration / إنشاء هجرة جديدة

```python
# Manual migration / هجرة يدوية
manager.create_migration(
    name="add_weather_data",
    description="Add weather data tracking tables"
)

# Auto-generate from models / إنشاء تلقائي من النماذج
manager.create_migration(
    name="auto_update",
    autogenerate=True
)
```

#### Rollback Migrations / التراجع عن الهجرات

```python
# Rollback one migration / التراجع عن هجرة واحدة
manager.rollback(steps=1)

# Rollback multiple migrations / التراجع عن هجرات متعددة
manager.rollback(steps=3)
```

#### Validate Checksums / التحقق من Checksums

```python
# Check for unauthorized changes / التحقق من التغييرات غير المصرح بها
validation = manager.validate_checksums()

if validation['has_conflicts']:
    print("⚠️  Warning: Migration files have been modified!")
    print("⚠️  تحذير: تم تعديل ملفات الهجرة!")
    for conflict in validation['conflicts']:
        print(f"  - {conflict['revision']}")
```

### PostGIS Operations / عمليات PostGIS

```python
from apps.kernel.common.database import PostGISMigrationHelper

# In migration upgrade() function / في دالة upgrade() للهجرة
def upgrade():
    conn = op.get_bind()

    # Enable PostGIS / تمكين PostGIS
    PostGISMigrationHelper.enable_postgis_extension(conn)

    # Add spatial column / إضافة عمود مكاني
    PostGISMigrationHelper.add_geography_column(
        conn,
        table="fields",
        column="location",
        geometry_type="POINT"
    )

    # Create spatial index / إنشاء فهرس مكاني
    PostGISMigrationHelper.create_spatial_index(
        conn,
        table="fields",
        column="location"
    )
```

## Database Schema / مخطط قاعدة البيانات

### Core Tables / الجداول الأساسية

1. **tenants** / **المستأجرون**: Multi-tenant organizations
2. **users** / **المستخدمون**: User accounts with role-based access
3. **farms** / **المزارع**: Agricultural farms
4. **fields** / **الحقول**: Individual fields with spatial data
5. **crops** / **المحاصيل**: Crop seasons and yield tracking
6. **sensors** / **أجهزة الاستشعار**: IoT sensor devices
7. **sensor_readings** / **قراءات الاستشعار**: Time-series sensor data

### Spatial Data / البيانات المكانية

Fields and sensors include PostGIS geometry columns:
تتضمن الحقول وأجهزة الاستشعار أعمدة هندسية من PostGIS:

- **Fields** / **الحقول**:
  - `location`: Center point (POINT)
  - `boundary`: Field polygon (POLYGON)

- **Sensors** / **أجهزة الاستشعار**:
  - `location`: Device location (POINT)

### Yemen-Specific Fields / حقول خاصة باليمن

- `governorate` / `المحافظة`: Administrative division
- `district` / `المديرية`: Sub-division
- `village` / `القرية`: Village name

## Development Data / بيانات التطوير

The development seeder creates sample data representing farms in Yemen:
تنشئ أداة التعبئة التطويرية بيانات نموذجية تمثل مزارع في اليمن:

### Sample Locations / المواقع النموذجية

- **Sana'a** / **صنعاء**: (15.3694°N, 44.1910°E)
- **Taiz** / **تعز**: (13.5795°N, 44.0165°E)
- **Al Hudaydah** / **الحديدة**: (14.7978°N, 42.9545°E)

### Sample Crops / المحاصيل النموذجية

- **Wheat** / **القمح**: Yemen Red variety
- **Coffee** / **البن**: Yemen Mokha variety
- **Qaat** / **القات**: Wadi Hadramaut variety
- **Date Palm** / **نخيل التمر**: Medjool variety
- **Mango** / **المانجو**: Alphonso variety

### Sample Sensors / أجهزة الاستشعار النموذجية

- Soil moisture sensors / مستشعرات رطوبة التربة
- Temperature sensors / مستشعرات درجة الحرارة
- Humidity sensors / مستشعرات الرطوبة
- Weather stations / محطات الطقس

## Environment Variables / متغيرات البيئة

Required environment variables:
متغيرات البيئة المطلوبة:

```bash
# Database connection / اتصال قاعدة البيانات
DB_HOST=postgres
DB_PORT=5432
DB_NAME=sahool
DB_USER=sahool
DB_PASSWORD=your_secure_password

# Or use DATABASE_URL / أو استخدم DATABASE_URL
DATABASE_URL=postgresql://user:password@localhost/sahool
```

## CLI Usage / استخدام سطر الأوامر

### Using Alembic Directly / استخدام Alembic مباشرة

```bash
# Run migrations / تشغيل الهجرات
alembic upgrade head

# Rollback one migration / التراجع عن هجرة واحدة
alembic downgrade -1

# Show current version / عرض الإصدار الحالي
alembic current

# Show migration history / عرض تاريخ الهجرة
alembic history

# Create new migration / إنشاء هجرة جديدة
alembic revision -m "add new table"

# Auto-generate migration / إنشاء هجرة تلقائيًا
alembic revision --autogenerate -m "auto update"
```

### Using Python Script / استخدام نص Python

```python
#!/usr/bin/env python3
"""
SAHOOL Database Migration Script
نص هجرة قاعدة بيانات SAHOOL
"""

import os
from apps.kernel.common.database import MigrationManager

def main():
    # Get database URL from environment / الحصول على عنوان URL من البيئة
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL not set")
        print("خطأ: DATABASE_URL غير محدد")
        return

    # Create manager / إنشاء المدير
    manager = MigrationManager(database_url)

    # Run migrations / تشغيل الهجرات
    print("Running migrations...")
    print("تشغيل الهجرات...")
    result = manager.run_migrations()

    if result['success']:
        print(f"✓ Migrations completed in {result['execution_time_ms']}ms")
        print(f"✓ اكتملت الهجرات في {result['execution_time_ms']}ms")
    else:
        print(f"✗ Migration failed: {result.get('error')}")
        print(f"✗ فشلت الهجرة: {result.get('error')}")

    # Seed development data (if needed) / تعبئة بيانات التطوير (إذا لزم الأمر)
    if os.getenv('SEED_DATA') == 'true':
        print("\\nSeeding development data...")
        print("\\nتعبئة بيانات التطوير...")
        seed_result = manager.seed_data(environment="development")

        if seed_result['success']:
            print(f"✓ Created {seed_result['farms']} farms with {seed_result['fields']} fields")
            print(f"✓ تم إنشاء {seed_result['farms']} مزرعة مع {seed_result['fields']} حقل")

if __name__ == '__main__':
    main()
```

## Best Practices / أفضل الممارسات

### 1. Always Test Migrations / اختبر الهجرات دائمًا

```bash
# Test on development database first / اختبر على قاعدة بيانات التطوير أولاً
DATABASE_URL=postgresql://localhost/sahool_dev alembic upgrade head

# Verify rollback works / تحقق من عمل التراجع
alembic downgrade -1
alembic upgrade head
```

### 2. Include Both Upgrade and Downgrade / قم بتضمين الترقية والتراجع

Every migration must have both `upgrade()` and `downgrade()` functions.
يجب أن تحتوي كل هجرة على دالتي `upgrade()` و `downgrade()`.

### 3. Use Transactions / استخدم المعاملات

Migrations run in transactions by default. Ensure atomic operations.
تعمل الهجرات في المعاملات افتراضيًا. تأكد من العمليات الذرية.

### 4. Document Changes / وثق التغييرات

```python
"""Add weather data tracking
إضافة تتبع بيانات الطقس

Creates tables for:
- Weather observations (ملاحظات الطقس)
- Weather forecasts (توقعات الطقس)
- Weather alerts (تنبيهات الطقس)
"""
```

### 5. Validate Data Integrity / التحقق من سلامة البيانات

```python
def upgrade():
    # Add column / إضافة عمود
    op.add_column('fields', sa.Column('elevation', sa.Float()))

    # Migrate existing data / ترحيل البيانات الموجودة
    conn = op.get_bind()
    conn.execute(text("""
        UPDATE fields
        SET elevation = 0
        WHERE elevation IS NULL
    """))

    # Add constraint / إضافة قيد
    op.alter_column('fields', 'elevation', nullable=False)
```

## Troubleshooting / استكشاف الأخطاء

### Migration Fails / فشل الهجرة

1. Check database connection / تحقق من اتصال قاعدة البيانات
2. Verify permissions / تحقق من الأذونات
3. Review migration logs / راجع سجلات الهجرة
4. Check for conflicts / تحقق من التعارضات

### Checksum Mismatch / عدم تطابق Checksum

```python
# Validate checksums / التحقق من checksums
result = manager.validate_checksums()

if result['has_conflicts']:
    # Do not modify applied migrations! / لا تعدل الهجرات المطبقة!
    # Create new migration instead / أنشئ هجرة جديدة بدلاً من ذلك
    print("Create new migration to fix issues")
    print("أنشئ هجرة جديدة لإصلاح المشاكل")
```

### PostGIS Not Available / PostGIS غير متاح

```bash
# Install PostGIS extension / تثبيت امتداد PostGIS
sudo apt-get install postgresql-postgis

# Or on macOS / أو على macOS
brew install postgis
```

## Security Considerations / اعتبارات الأمان

1. **Password Protection** / **حماية كلمة المرور**:
   - Never commit passwords to version control / لا تقم بإرسال كلمات المرور إلى نظام التحكم في الإصدار
   - Use environment variables / استخدم متغيرات البيئة

2. **Access Control** / **التحكم في الوصول**:
   - Limit database user permissions / قيد أذونات مستخدم قاعدة البيانات
   - Use separate users for migrations / استخدم مستخدمين منفصلين للهجرات

3. **Backup Before Migration** / **النسخ الاحتياطي قبل الهجرة**:
   - Always backup production databases / قم دائمًا بعمل نسخة احتياطية من قواعد البيانات الإنتاجية
   - Test migrations on staging first / اختبر الهجرات على التجهيز أولاً

## Support / الدعم

For issues or questions:
للمشاكل أو الأسئلة:

- Check migration logs / راجع سجلات الهجرة
- Review documentation / راجع الوثائق
- Contact SAHOOL development team / اتصل بفريق تطوير SAHOOL

## License / الترخيص

Part of the SAHOOL agricultural platform.
جزء من منصة SAHOOL الزراعية.

---

**Version** / **الإصدار**: 1.0.0
**Last Updated** / **آخر تحديث**: 2026-01-02
