# تشغيل سريع - Field Service Migrations

## 🚀 تشغيل Migrations في خطوة واحدة

```bash
cd apps/services/field-service
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/sahool"
aerich init-db
```

## ✅ التحقق من النجاح

```bash
# اتصل بـ PostgreSQL
docker-compose exec postgres psql -U sahool -d sahool

# عرض الجداول
\dt

# يجب أن ترى:
# fields, crop_seasons, zones, ndvi_records, aerich
```

## 📝 الملفات المهمة

1. **`src/db_models.py`** - 4 نماذج Tortoise ORM
2. **`src/database.py`** - TORTOISE_ORM config
3. **`src/migrations/models/0_20251227000000_init.py`** - Initial migration
4. **`aerich.ini`** و **`pyproject.toml`** - Aerich config

## 📚 المراجع

- `MIGRATIONS_SUMMARY.md` - ملخص شامل
- `MIGRATION_GUIDE.md` - دليل كامل
- `src/migrations/README.md` - دليل الاستخدام

## 🔄 الأوامر الشائعة

```bash
# تطبيق migrations
aerich upgrade

# إنشاء migration جديد
aerich migrate --name "description"

# التراجع
aerich downgrade

# عرض الحالة
aerich heads
```
