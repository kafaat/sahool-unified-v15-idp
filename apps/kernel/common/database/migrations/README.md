# SAHOOL Database Migrations
# هجرة قاعدة البيانات

This directory contains database migration scripts for the SAHOOL platform.
يحتوي هذا الدليل على نصوص هجرة قاعدة البيانات لمنصة SAHOOL.

## Structure / البنية

```
migrations/
├── versions/           # Migration files / ملفات الهجرة
│   ├── 001_initial_schema.py
│   └── 002_add_postgis.py
├── env.py             # Alembic environment / بيئة Alembic
├── script.py.mako     # Migration template / قالب الهجرة
└── README.md          # This file / هذا الملف
```

## Usage / الاستخدام

### Creating a New Migration / إنشاء هجرة جديدة

```python
from apps.kernel.common.database.migrations import MigrationManager

manager = MigrationManager(database_url="postgresql://...")
manager.create_migration(
    name="add_user_table",
    description="Add users table with authentication fields"
)
```

### Running Migrations / تشغيل الهجرات

```python
# Migrate to latest version / الهجرة إلى أحدث إصدار
manager.run_migrations()

# Migrate to specific version / الهجرة إلى إصدار محدد
manager.run_migrations(target_version="002")
```

### Rolling Back / التراجع

```python
# Rollback one step / التراجع خطوة واحدة
manager.rollback(steps=1)

# Rollback multiple steps / التراجع خطوات متعددة
manager.rollback(steps=3)
```

### Checking Status / التحقق من الحالة

```python
status = manager.get_migration_status()
print(f"Current revision: {status['current_revision']}")
print(f"Pending migrations: {status['pending_migrations']}")
```

### Seeding Data / تعبئة البيانات

```python
# Seed development data / تعبئة بيانات التطوير
manager.seed_data(environment="development")
```

## Migration Guidelines / إرشادات الهجرة

### Naming Conventions / اصطلاحات التسمية

- Use descriptive names in English / استخدم أسماء وصفية بالإنجليزية
- Include timestamp prefix / قم بتضمين بادئة الطابع الزمني
- Format: `YYYYMMDD_HHMM_description.py`

### Best Practices / أفضل الممارسات

1. **Always include both upgrade() and downgrade()** / قم دائمًا بتضمين كل من upgrade() و downgrade()
   - Every migration must be reversible / يجب أن تكون كل هجرة قابلة للعكس
   - Test rollback before deploying / اختبر التراجع قبل النشر

2. **Include Arabic comments** / قم بتضمين تعليقات بالعربية
   - Add bilingual documentation / أضف وثائق ثنائية اللغة
   - Explain the purpose and impact / اشرح الغرض والتأثير

3. **Use transactions** / استخدم المعاملات
   - Migrations run in transactions by default / تعمل الهجرات في المعاملات افتراضيًا
   - Ensure atomic operations / تأكد من العمليات الذرية

4. **Test with real data** / اختبر بالبيانات الحقيقية
   - Test on development database first / اختبر على قاعدة بيانات التطوير أولاً
   - Verify data integrity / تحقق من سلامة البيانات

5. **Document dependencies** / وثق التبعيات
   - List required migrations / قم بإدراج الهجرات المطلوبة
   - Note external dependencies / لاحظ التبعيات الخارجية

## PostGIS Support / دعم PostGIS

For spatial data operations, use the PostGISMigrationHelper:
لعمليات البيانات المكانية، استخدم PostGISMigrationHelper:

```python
from apps.kernel.common.database.migrations import PostGISMigrationHelper

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

## Checksum Validation / التحقق من Checksum

The migration system tracks checksums to detect unauthorized changes:
يتتبع نظام الهجرة checksums للكشف عن التغييرات غير المصرح بها:

```python
# Validate checksums / التحقق من checksums
result = manager.validate_checksums()
if result['has_conflicts']:
    print("Warning: Migration files have been modified!")
    for conflict in result['conflicts']:
        print(f"  - {conflict['revision']}")
```

## Environment Variables / متغيرات البيئة

Required environment variables:
متغيرات البيئة المطلوبة:

```bash
DB_HOST=postgres
DB_PORT=5432
DB_NAME=sahool
DB_USER=sahool
DB_PASSWORD=your_secure_password
```

## Troubleshooting / استكشاف الأخطاء

### Migration fails / فشل الهجرة

1. Check database connection / تحقق من اتصال قاعدة البيانات
2. Verify permissions / تحقق من الأذونات
3. Review migration logs / راجع سجلات الهجرة
4. Test in development first / اختبر في التطوير أولاً

### Checksum mismatch / عدم تطابق Checksum

1. Do not modify applied migrations / لا تعدل الهجرات المطبقة
2. Create new migration for changes / أنشئ هجرة جديدة للتغييرات
3. Document reason for override / وثق سبب التجاوز

## Support / الدعم

For issues or questions, contact the SAHOOL development team.
للمشاكل أو الأسئلة، اتصل بفريق تطوير SAHOOL.
