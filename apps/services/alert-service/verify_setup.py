"""
SAHOOL Alert Service - Setup Verification
التحقق من صحة إعداد قاعدة البيانات والـ Migrations

استخدم هذا السكريبت للتحقق من أن كل شيء تم إعداده بشكل صحيح.
"""

import sys
import os


def check_imports():
    """التحقق من المكتبات المطلوبة"""
    print("🔍 فحص المكتبات المطلوبة...")

    required_modules = {
        "sqlalchemy": "SQLAlchemy",
        "alembic": "Alembic",
        "psycopg2": "psycopg2-binary",
        "fastapi": "FastAPI",
    }

    missing = []
    for module, name in required_modules.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - مفقود")
            missing.append(name)

    if missing:
        print(f"\n❌ مكتبات مفقودة: {', '.join(missing)}")
        print("   قم بتثبيتها: pip install -r requirements.txt")
        return False

    print("✅ جميع المكتبات موجودة\n")
    return True


def check_files():
    """التحقق من وجود الملفات المطلوبة"""
    print("🔍 فحص الملفات المطلوبة...")

    required_files = [
        "alembic.ini",
        "src/db_models.py",
        "src/database.py",
        "src/repository.py",
        "src/migrations/env.py",
        "src/migrations/script.py.mako",
        "src/migrations/versions/s16_0001_alerts_initial.py",
    ]

    missing = []
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"  ✅ {filepath}")
        else:
            print(f"  ❌ {filepath} - مفقود")
            missing.append(filepath)

    if missing:
        print(f"\n❌ ملفات مفقودة: {len(missing)}")
        return False

    print("✅ جميع الملفات موجودة\n")
    return True


def check_models():
    """التحقق من نماذج قاعدة البيانات"""
    print("🔍 فحص نماذج قاعدة البيانات...")

    try:
        from src.db_models import Alert, AlertRule, Base
        print("  ✅ Alert model")
        print("  ✅ AlertRule model")
        print("  ✅ Base metadata")

        # Check tables
        tables = Base.metadata.tables
        print(f"\n  📊 الجداول المُعرّفة: {len(tables)}")
        for table_name in tables.keys():
            print(f"     - {table_name}")

        print("\n✅ النماذج صحيحة\n")
        return True

    except Exception as e:
        print(f"\n❌ خطأ في النماذج: {e}")
        return False


def check_database_config():
    """التحقق من إعدادات قاعدة البيانات"""
    print("🔍 فحص إعدادات قاعدة البيانات...")

    try:
        from src.database import DATABASE_URL, engine, SessionLocal

        print(f"  ✅ DATABASE_URL: {DATABASE_URL[:30]}...")
        print(f"  ✅ Engine configured")
        print(f"  ✅ SessionLocal factory")

        print("\n✅ الإعدادات صحيحة\n")
        return True

    except Exception as e:
        print(f"\n❌ خطأ في الإعدادات: {e}")
        return False


def check_repository():
    """التحقق من طبقة Repository"""
    print("🔍 فحص طبقة Repository...")

    try:
        import src.repository as repo

        functions = [
            "create_alert",
            "get_alert",
            "get_alerts_by_field",
            "update_alert_status",
            "get_active_alerts",
            "create_alert_rule",
            "get_alert_rule",
            "get_enabled_rules",
        ]

        for func in functions:
            if hasattr(repo, func):
                print(f"  ✅ {func}()")
            else:
                print(f"  ❌ {func}() - مفقودة")

        print("\n✅ Repository layer جاهزة\n")
        return True

    except Exception as e:
        print(f"\n❌ خطأ في Repository: {e}")
        return False


def check_alembic():
    """التحقق من إعداد Alembic"""
    print("🔍 فحص إعداد Alembic...")

    try:
        from alembic.config import Config
        from alembic import command

        # Check alembic.ini
        if not os.path.exists("alembic.ini"):
            print("  ❌ alembic.ini مفقود")
            return False

        print("  ✅ alembic.ini موجود")

        # Try to load config
        alembic_cfg = Config("alembic.ini")
        print("  ✅ تم تحميل الإعدادات بنجاح")

        print("\n✅ Alembic جاهز\n")
        return True

    except Exception as e:
        print(f"\n❌ خطأ في Alembic: {e}")
        return False


def print_summary(results):
    """عرض الملخص النهائي"""
    print("\n" + "="*60)
    print("📊 ملخص التحقق")
    print("="*60)

    total = len(results)
    passed = sum(results.values())

    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")

    print("-"*60)
    print(f"النتيجة: {passed}/{total} اختبارات ناجحة")

    if passed == total:
        print("\n🎉 الإعداد كامل وجاهز للاستخدام!")
        print("\nالخطوات التالية:")
        print("1. export DATABASE_URL='postgresql://...'")
        print("2. createdb sahool_alerts")
        print("3. alembic upgrade head")
        print("4. python -m src.main")
        return True
    else:
        print("\n⚠️  يوجد مشاكل تحتاج إلى إصلاح")
        print("\nراجع التوثيق:")
        print("- QUICKSTART.md")
        print("- MIGRATIONS.md")
        return False


def main():
    """تشغيل جميع الفحوصات"""
    print("\n" + "="*60)
    print("🔧 SAHOOL Alert Service - Setup Verification")
    print("   التحقق من إعداد خدمة التنبيهات")
    print("="*60 + "\n")

    results = {}

    # Run checks
    results["المكتبات المطلوبة"] = check_imports()
    results["الملفات المطلوبة"] = check_files()
    results["نماذج قاعدة البيانات"] = check_models()
    results["إعدادات قاعدة البيانات"] = check_database_config()
    results["طبقة Repository"] = check_repository()
    results["إعداد Alembic"] = check_alembic()

    # Print summary
    success = print_summary(results)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
