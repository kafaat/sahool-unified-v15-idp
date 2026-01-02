#!/usr/bin/env python3
"""
SAHOOL Database Migration - Example Usage
مثال على استخدام هجرة قاعدة بيانات SAHOOL

This script demonstrates how to use the migration utilities.
يوضح هذا النص البرمجي كيفية استخدام أدوات الهجرة.
"""

import os
import sys
from pathlib import Path

# إضافة المسار إلى sys.path
# Add path to sys.path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from apps.kernel.common.database import MigrationManager


def print_section(title: str, title_ar: str = ""):
    """طباعة عنوان القسم / Print section title"""
    print("\n" + "="*80)
    print(f"  {title}")
    if title_ar:
        print(f"  {title_ar}")
    print("="*80 + "\n")


def example_migration_status():
    """
    مثال: التحقق من حالة الهجرة
    Example: Check migration status
    """
    print_section("Migration Status Example", "مثال: حالة الهجرة")

    # الحصول على عنوان URL من البيئة
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://sahool:password@localhost/sahool')

    # إنشاء مدير الهجرة
    # Create migration manager
    manager = MigrationManager(database_url)

    # الحصول على حالة الهجرة
    # Get migration status
    status = manager.get_migration_status()

    print(f"Current Revision: {status['current_revision']}")
    print(f"الإصدار الحالي: {status['current_revision']}")
    print(f"\nTotal Available Migrations: {status['total_available']}")
    print(f"إجمالي الهجرات المتاحة: {status['total_available']}")
    print(f"\nTotal Applied Migrations: {status['total_applied']}")
    print(f"إجمالي الهجرات المطبقة: {status['total_applied']}")
    print(f"\nPending Migrations: {status['pending_migrations']}")
    print(f"الهجرات المعلقة: {status['pending_migrations']}")

    # عرض الهجرات المتاحة
    # Show available migrations
    if status['available_migrations']:
        print("\nAvailable Migrations / الهجرات المتاحة:")
        for migration in status['available_migrations']:
            print(f"  - {migration['revision']}: {migration['description']}")

    # عرض الهجرات المطبقة
    # Show applied migrations
    if status['applied_migrations']:
        print("\nApplied Migrations / الهجرات المطبقة:")
        for migration in status['applied_migrations']:
            print(f"  - {migration['revision']}: {migration['description']}")
            print(f"    Applied at: {migration['applied_at']}")


def example_run_migrations():
    """
    مثال: تشغيل الهجرات
    Example: Run migrations
    """
    print_section("Run Migrations Example", "مثال: تشغيل الهجرات")

    database_url = os.getenv('DATABASE_URL', 'postgresql://sahool:password@localhost/sahool')
    manager = MigrationManager(database_url)

    print("Running migrations to latest version...")
    print("تشغيل الهجرات إلى أحدث إصدار...")

    try:
        result = manager.run_migrations()

        if result['success']:
            print(f"\n✓ Success! / ✓ نجاح!")
            print(f"Target Version: {result['target_version']}")
            print(f"Execution Time: {result['execution_time_ms']}ms")
            print(f"وقت التنفيذ: {result['execution_time_ms']}ms")
        else:
            print(f"\n✗ Failed! / ✗ فشل!")
            print(f"Error: {result.get('error')}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print(f"✗ خطأ: {str(e)}")


def example_rollback():
    """
    مثال: التراجع عن الهجرات
    Example: Rollback migrations
    """
    print_section("Rollback Example", "مثال: التراجع")

    database_url = os.getenv('DATABASE_URL', 'postgresql://sahool:password@localhost/sahool')
    manager = MigrationManager(database_url)

    steps = 1
    print(f"Rolling back {steps} migration(s)...")
    print(f"التراجع عن {steps} هجرة...")

    try:
        result = manager.rollback(steps=steps)

        if result['success']:
            print(f"\n✓ Rollback successful! / ✓ التراجع ناجح!")
            print(f"Steps: {result['steps']}")
            print(f"Execution Time: {result['execution_time_ms']}ms")
        else:
            print(f"\n✗ Rollback failed! / ✗ فشل التراجع!")
            print(f"Error: {result.get('error')}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print(f"✗ خطأ: {str(e)}")


def example_validate_checksums():
    """
    مثال: التحقق من checksums
    Example: Validate checksums
    """
    print_section("Checksum Validation Example", "مثال: التحقق من Checksum")

    database_url = os.getenv('DATABASE_URL', 'postgresql://sahool:password@localhost/sahool')
    manager = MigrationManager(database_url)

    print("Validating migration checksums...")
    print("التحقق من checksums الهجرة...")

    try:
        result = manager.validate_checksums()

        if result['has_conflicts']:
            print("\n⚠️  Warning: Migration file conflicts detected!")
            print("⚠️  تحذير: تم اكتشاف تعارضات في ملفات الهجرة!")
            print("\nConflicts / التعارضات:")
            for conflict in result['conflicts']:
                print(f"  - Revision: {conflict['revision']}")
                print(f"    Stored:  {conflict['stored_checksum'][:16]}...")
                print(f"    Current: {conflict['current_checksum'][:16]}...")
        else:
            print("\n✓ All checksums valid! / ✓ جميع checksums صالحة!")
            print("No conflicts detected / لم يتم اكتشاف أي تعارضات")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print(f"✗ خطأ: {str(e)}")


def example_seed_data():
    """
    مثال: تعبئة البيانات
    Example: Seed data
    """
    print_section("Seed Data Example", "مثال: تعبئة البيانات")

    database_url = os.getenv('DATABASE_URL', 'postgresql://sahool:password@localhost/sahool')
    manager = MigrationManager(database_url)

    print("Seeding development data...")
    print("تعبئة بيانات التطوير...")

    try:
        result = manager.seed_data(environment="development")

        if result['success']:
            print("\n✓ Seeding successful! / ✓ التعبئة ناجحة!")
            print(f"\nCreated / تم إنشاء:")
            print(f"  - Tenants: {result['tenants']}")
            print(f"    المستأجرون: {result['tenants']}")
            print(f"  - Users: {result['users']}")
            print(f"    المستخدمون: {result['users']}")
            print(f"  - Farms: {result['farms']}")
            print(f"    المزارع: {result['farms']}")
            print(f"  - Fields: {result['fields']}")
            print(f"    الحقول: {result['fields']}")
            print(f"  - Crops: {result['crops']}")
            print(f"    المحاصيل: {result['crops']}")
            print(f"  - Sensors: {result['sensors']}")
            print(f"    أجهزة الاستشعار: {result['sensors']}")
            print(f"\nExecution Time: {result['execution_time_ms']}ms")
            print(f"وقت التنفيذ: {result['execution_time_ms']}ms")
        else:
            print(f"\n✗ Seeding failed! / ✗ فشلت التعبئة!")
            print(f"Error: {result.get('error')}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print(f"✗ خطأ: {str(e)}")


def example_create_migration():
    """
    مثال: إنشاء هجرة جديدة
    Example: Create new migration
    """
    print_section("Create Migration Example", "مثال: إنشاء هجرة")

    database_url = os.getenv('DATABASE_URL', 'postgresql://sahool:password@localhost/sahool')
    manager = MigrationManager(database_url)

    migration_name = "add_weather_data"
    description = "Add weather data tracking tables"

    print(f"Creating new migration: {migration_name}")
    print(f"إنشاء هجرة جديدة: {migration_name}")

    try:
        result = manager.create_migration(
            name=migration_name,
            description=description,
            autogenerate=False
        )

        print(f"\n✓ {result}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print(f"✗ خطأ: {str(e)}")


def main():
    """
    الدالة الرئيسية
    Main function
    """
    print("\n" + "="*80)
    print("  SAHOOL Database Migration - Example Usage")
    print("  مثال على استخدام هجرة قاعدة بيانات SAHOOL")
    print("="*80)

    # التحقق من وجود متغير البيئة
    # Check for environment variable
    if not os.getenv('DATABASE_URL'):
        print("\n⚠️  Warning: DATABASE_URL not set, using default")
        print("⚠️  تحذير: DATABASE_URL غير محدد، استخدام الافتراضي")
        print("Default: postgresql://sahool:password@localhost/sahool\n")

    # تشغيل الأمثلة
    # Run examples
    examples = [
        ("1", "Migration Status", "حالة الهجرة", example_migration_status),
        ("2", "Run Migrations", "تشغيل الهجرات", example_run_migrations),
        ("3", "Rollback", "التراجع", example_rollback),
        ("4", "Validate Checksums", "التحقق من Checksums", example_validate_checksums),
        ("5", "Seed Data", "تعبئة البيانات", example_seed_data),
        ("6", "Create Migration", "إنشاء هجرة", example_create_migration),
    ]

    print("\nAvailable Examples / الأمثلة المتاحة:\n")
    for num, title, title_ar, _ in examples:
        print(f"  {num}. {title} / {title_ar}")

    print("\n  0. Run All Examples / تشغيل جميع الأمثلة")
    print("  q. Quit / خروج")

    while True:
        choice = input("\nSelect example (number or 'q' to quit): ").strip()

        if choice.lower() == 'q':
            print("\nGoodbye! / وداعاً!")
            break

        if choice == '0':
            # تشغيل جميع الأمثلة
            # Run all examples
            for _, _, _, example_func in examples:
                try:
                    example_func()
                except Exception as e:
                    print(f"\nError running example: {str(e)}")
                    print(f"خطأ في تشغيل المثال: {str(e)}")
            break

        # تشغيل مثال محدد
        # Run specific example
        for num, _, _, example_func in examples:
            if choice == num:
                try:
                    example_func()
                except Exception as e:
                    print(f"\nError running example: {str(e)}")
                    print(f"خطأ في تشغيل المثال: {str(e)}")
                break
        else:
            print("Invalid choice / اختيار غير صالح")


if __name__ == '__main__':
    main()
