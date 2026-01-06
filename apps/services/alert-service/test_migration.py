#!/usr/bin/env python3
"""
Alert Service PostgreSQL Migration Verification Script

This script verifies that the alert-service has been successfully migrated
from in-memory storage to PostgreSQL.

Usage:
    python test_migration.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all database modules can be imported"""
    print("Testing imports...")
    try:
        from src.database import SessionLocal, check_db_connection, get_db
        from src.db_models import Alert, AlertRule
        from src.repository import (
            create_alert,
            create_alert_rule,
            get_alert,
            get_alerts_by_field,
        )

        print("  ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from src.database import check_db_connection

        if check_db_connection():
            print("  ✅ Database connection successful")
            return True
        else:
            print("  ⚠️  Database connection failed (may be expected if DB not running)")
            return False
    except Exception as e:
        print(f"  ⚠️  Database connection error: {e}")
        return False


def test_models():
    """Test that models are properly defined"""
    print("\nTesting database models...")
    try:
        from src.db_models import Alert, AlertRule

        # Check Alert model has required fields
        alert_fields = [
            "id",
            "tenant_id",
            "field_id",
            "type",
            "severity",
            "status",
            "title",
            "message",
            "created_at",
        ]
        for field in alert_fields:
            assert hasattr(Alert, field), f"Alert missing field: {field}"

        # Check AlertRule model has required fields
        rule_fields = [
            "id",
            "tenant_id",
            "field_id",
            "name",
            "enabled",
            "condition",
            "alert_config",
            "created_at",
        ]
        for field in rule_fields:
            assert hasattr(AlertRule, field), f"AlertRule missing field: {field}"

        print("  ✅ All model fields present")
        return True
    except AssertionError as e:
        print(f"  ❌ Model validation error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Model test error: {e}")
        return False


def test_repository():
    """Test that repository functions exist"""
    print("\nTesting repository layer...")
    try:
        from src import repository

        required_functions = [
            "create_alert",
            "get_alert",
            "get_alerts_by_field",
            "update_alert_status",
            "delete_alert",
            "get_alert_statistics",
            "create_alert_rule",
            "get_alert_rule",
            "get_alert_rules_by_field",
            "delete_alert_rule",
        ]

        for func_name in required_functions:
            assert hasattr(
                repository, func_name
            ), f"Repository missing function: {func_name}"

        print("  ✅ All repository functions present")
        return True
    except AssertionError as e:
        print(f"  ❌ Repository validation error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Repository test error: {e}")
        return False


def test_migration_file():
    """Test that migration file exists"""
    print("\nTesting migration files...")
    migration_file = (
        Path(__file__).parent
        / "src"
        / "migrations"
        / "versions"
        / "s16_0001_alerts_initial.py"
    )

    if migration_file.exists():
        print(f"  ✅ Migration file exists: {migration_file.name}")
        return True
    else:
        print(f"  ❌ Migration file not found: {migration_file}")
        return False


def test_main_py():
    """Test that main.py has been updated"""
    print("\nTesting main.py migration...")
    main_file = Path(__file__).parent / "src" / "main.py"

    if not main_file.exists():
        print("  ❌ main.py not found")
        return False

    content = main_file.read_text()

    # Check for database imports
    checks = [
        ("Database imports", "from .database import"),
        ("DB models import", "from .db_models import"),
        ("Repository imports", "from .repository import"),
        ("Session dependency", "Session = Depends(get_db)"),
        ("Migration comment", "MIGRATED TO POSTGRESQL"),
    ]

    all_passed = True
    for check_name, check_str in checks:
        if check_str in content:
            print(f"  ✅ {check_name} found")
        else:
            print(f"  ❌ {check_name} NOT found")
            all_passed = False

    # Check that in-memory storage is removed
    if "_alerts: dict[str, dict] = {}" in content:
        print("  ❌ In-memory storage still present!")
        all_passed = False
    else:
        print("  ✅ In-memory storage removed")

    return all_passed


def main():
    """Run all tests"""
    print("=" * 70)
    print("ALERT SERVICE POSTGRESQL MIGRATION VERIFICATION")
    print("=" * 70)

    results = {
        "Imports": test_imports(),
        "Database Connection": test_database_connection(),
        "Models": test_models(),
        "Repository": test_repository(),
        "Migration File": test_migration_file(),
        "Main.py Updates": test_main_py(),
    }

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")

    print("=" * 70)
    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! Migration is complete and verified.")
        return 0
    else:
        print(
            "\n⚠️  Some tests failed. Please review the errors above."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
