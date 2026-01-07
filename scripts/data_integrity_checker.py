#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════
SAHOOL IDP - Data Integrity Checker
فاحص سلامة البيانات
═══════════════════════════════════════════════════════════════════════════════════════

Proactively detects data integrity issues:
- Orphaned records (missing foreign key references)
- Stale GPS data
- Duplicate records
- Schema constraint violations

Usage:
    # Run full integrity check
    python data_integrity_checker.py --full

    # Check specific tables
    python data_integrity_checker.py --tables fields,tasks,sensor_readings

    # Auto-fix orphaned records
    python data_integrity_checker.py --auto-fix --dry-run

═══════════════════════════════════════════════════════════════════════════════════════
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

try:
    import asyncpg
except ImportError:
    print("Error: asyncpg is required. Install with: pip install asyncpg")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("data-integrity")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sahool:sahool@localhost:5432/sahool")

# Convert to asyncpg format
if DATABASE_URL.startswith("postgresql://"):
    ASYNCPG_URL = DATABASE_URL
elif DATABASE_URL.startswith("postgresql+asyncpg://"):
    ASYNCPG_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
else:
    ASYNCPG_URL = DATABASE_URL

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class IntegrityIssue:
    table: str
    issue_type: str
    severity: str  # critical, high, medium, low
    count: int
    sample_ids: list[str] = field(default_factory=list)
    description: str = ""
    description_ar: str = ""
    fix_available: bool = False
    fix_query: str = ""


@dataclass
class IntegrityReport:
    timestamp: str
    database: str
    total_issues: int
    critical_issues: int
    issues: list[dict] = field(default_factory=list)
    tables_checked: list[str] = field(default_factory=list)
    duration_ms: float = 0.0

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    def print_summary(self):
        print("\n" + "=" * 70)
        print("  🔍 DATA INTEGRITY CHECK RESULTS")
        print("  نتائج فحص سلامة البيانات")
        print("=" * 70)
        print(f"  Timestamp:    {self.timestamp}")
        print(f"  Duration:     {self.duration_ms:.2f}ms")
        print(f"  Tables:       {len(self.tables_checked)}")
        print("")

        if self.total_issues == 0:
            print("  ✅ No integrity issues found!")
            print("  ✅ لم يتم العثور على مشاكل!")
        else:
            print(f"  ⚠️ Total Issues:    {self.total_issues}")
            print(f"  🔴 Critical:        {self.critical_issues}")
            print("")
            print("  Issues by Table:")
            print("  " + "-" * 66)

            for issue in self.issues:
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢",
                }.get(issue["severity"], "⚪")

                print(
                    f"  {severity_icon} {issue['table']}: {issue['issue_type']} ({issue['count']} records)"
                )
                if issue.get("description"):
                    print(f"      {issue['description']}")

        print("=" * 70 + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRITY CHECKS
# ═══════════════════════════════════════════════════════════════════════════════


class DataIntegrityChecker:
    """Main class for checking data integrity."""

    def __init__(self, database_url: str = ASYNCPG_URL):
        self.database_url = database_url
        self.conn: asyncpg.Connection | None = None
        self.issues: list[IntegrityIssue] = []

    async def connect(self):
        """Establish database connection."""
        try:
            self.conn = await asyncpg.connect(self.database_url)
            logger.info("✅ Connected to database")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    async def disconnect(self):
        """Close database connection."""
        if self.conn:
            await self.conn.close()

    async def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        result = await self.conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = $1
            )
        """,
            table_name,
        )
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # ORPHANED RECORDS CHECKS
    # ─────────────────────────────────────────────────────────────────────────

    async def check_orphaned_fields(self) -> IntegrityIssue | None:
        """Check for fields without valid user owners."""
        if not await self.check_table_exists("fields"):
            return None

        result = await self.conn.fetch("""
            SELECT f.id::text
            FROM fields f
            LEFT JOIN users u ON f.user_id = u.id
            WHERE u.id IS NULL AND f.user_id IS NOT NULL
            LIMIT 10
        """)

        if result:
            return IntegrityIssue(
                table="fields",
                issue_type="orphaned_user_reference",
                severity="high",
                count=len(result),
                sample_ids=[r["id"] for r in result],
                description="Fields referencing non-existent users",
                description_ar="حقول تشير إلى مستخدمين غير موجودين",
                fix_available=True,
                fix_query="DELETE FROM fields WHERE user_id NOT IN (SELECT id FROM users)",
            )
        return None

    async def check_orphaned_sensor_readings(self) -> IntegrityIssue | None:
        """Check for sensor readings without valid fields."""
        if not await self.check_table_exists("sensor_readings"):
            return None

        result = await self.conn.fetch("""
            SELECT sr.id::text
            FROM sensor_readings sr
            LEFT JOIN fields f ON sr.field_id = f.id
            WHERE f.id IS NULL AND sr.field_id IS NOT NULL
            LIMIT 10
        """)

        if result:
            return IntegrityIssue(
                table="sensor_readings",
                issue_type="orphaned_field_reference",
                severity="medium",
                count=len(result),
                sample_ids=[r["id"] for r in result],
                description="Sensor readings referencing non-existent fields",
                description_ar="قراءات حساسات تشير إلى حقول غير موجودة",
                fix_available=True,
                fix_query="DELETE FROM sensor_readings WHERE field_id NOT IN (SELECT id FROM fields)",
            )
        return None

    async def check_orphaned_tasks(self) -> IntegrityIssue | None:
        """Check for tasks with invalid references."""
        if not await self.check_table_exists("tasks"):
            return None

        result = await self.conn.fetch("""
            SELECT t.id::text
            FROM tasks t
            LEFT JOIN fields f ON t.field_id = f.id
            WHERE f.id IS NULL AND t.field_id IS NOT NULL
            LIMIT 10
        """)

        if result:
            return IntegrityIssue(
                table="tasks",
                issue_type="orphaned_field_reference",
                severity="medium",
                count=len(result),
                sample_ids=[r["id"] for r in result],
                description="Tasks referencing non-existent fields",
                description_ar="مهام تشير إلى حقول غير موجودة",
                fix_available=True,
                fix_query="DELETE FROM tasks WHERE field_id NOT IN (SELECT id FROM fields)",
            )
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # STALE DATA CHECKS
    # ─────────────────────────────────────────────────────────────────────────

    async def check_stale_gps_data(self, days_threshold: int = 30) -> IntegrityIssue | None:
        """Check for stale GPS data."""
        if not await self.check_table_exists("fields"):
            return None

        # Check if location columns exist
        has_location = await self.conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'fields' AND column_name = 'latitude'
            )
        """)

        if not has_location:
            return None

        result = await self.conn.fetch(f"""
            SELECT id::text
            FROM fields
            WHERE latitude IS NOT NULL
              AND updated_at < NOW() - INTERVAL '{days_threshold} days'
            LIMIT 10
        """)

        if result:
            return IntegrityIssue(
                table="fields",
                issue_type="stale_gps_data",
                severity="low",
                count=len(result),
                sample_ids=[r["id"] for r in result],
                description=f"GPS data not updated in {days_threshold}+ days",
                description_ar=f"بيانات GPS لم تُحدث منذ {days_threshold}+ يوم",
                fix_available=False,
            )
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # DUPLICATE CHECKS
    # ─────────────────────────────────────────────────────────────────────────

    async def check_duplicate_users(self) -> IntegrityIssue | None:
        """Check for duplicate user emails."""
        if not await self.check_table_exists("users"):
            return None

        result = await self.conn.fetch("""
            SELECT email, COUNT(*) as cnt
            FROM users
            GROUP BY email
            HAVING COUNT(*) > 1
            LIMIT 10
        """)

        if result:
            return IntegrityIssue(
                table="users",
                issue_type="duplicate_emails",
                severity="critical",
                count=sum(r["cnt"] for r in result),
                sample_ids=[r["email"] for r in result],
                description="Duplicate user email addresses found",
                description_ar="تم العثور على عناوين بريد إلكتروني مكررة",
                fix_available=False,  # Requires manual intervention
            )
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # CONSTRAINT CHECKS
    # ─────────────────────────────────────────────────────────────────────────

    async def check_missing_fk_constraints(self) -> IntegrityIssue | None:
        """Check for tables missing foreign key constraints."""
        # Check if fields table has FK to users
        fk_exists = await self.conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE table_name = 'fields'
                  AND constraint_type = 'FOREIGN KEY'
                  AND constraint_name LIKE '%user%'
            )
        """)

        if not fk_exists and await self.check_table_exists("fields"):
            return IntegrityIssue(
                table="fields",
                issue_type="missing_fk_constraint",
                severity="high",
                count=1,
                description="Missing foreign key constraint on user_id",
                description_ar="قيد المفتاح الأجنبي مفقود على user_id",
                fix_available=True,
                fix_query="ALTER TABLE fields ADD CONSTRAINT fk_fields_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE",
            )
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # MAIN CHECK RUNNER
    # ─────────────────────────────────────────────────────────────────────────

    async def run_all_checks(self) -> IntegrityReport:
        """Run all integrity checks."""
        start_time = datetime.now()

        await self.connect()

        try:
            checks = [
                self.check_orphaned_fields(),
                self.check_orphaned_sensor_readings(),
                self.check_orphaned_tasks(),
                self.check_stale_gps_data(),
                self.check_duplicate_users(),
                self.check_missing_fk_constraints(),
            ]

            results = await asyncio.gather(*checks, return_exceptions=True)

            issues = []
            for result in results:
                if isinstance(result, IntegrityIssue):
                    issues.append(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Check failed: {result}")

            duration = (datetime.now() - start_time).total_seconds() * 1000

            report = IntegrityReport(
                timestamp=datetime.now(UTC).isoformat(),
                database=self.database_url.split("@")[-1]
                if "@" in self.database_url
                else "localhost",
                total_issues=len(issues),
                critical_issues=sum(1 for i in issues if i.severity == "critical"),
                issues=[asdict(i) for i in issues],
                tables_checked=["fields", "users", "sensor_readings", "tasks"],
                duration_ms=duration,
            )

            return report

        finally:
            await self.disconnect()

    async def auto_fix(self, dry_run: bool = True) -> list[dict]:
        """Automatically fix detected issues."""
        fixes_applied = []

        await self.connect()

        try:
            # Run checks first
            report = await self.run_all_checks()

            for issue in report.issues:
                if issue.get("fix_available") and issue.get("fix_query"):
                    if dry_run:
                        logger.info(f"[DRY RUN] Would execute: {issue['fix_query'][:100]}...")
                        fixes_applied.append(
                            {
                                "table": issue["table"],
                                "issue": issue["issue_type"],
                                "status": "would_fix",
                                "query": issue["fix_query"],
                            }
                        )
                    else:
                        try:
                            await self.conn.execute(issue["fix_query"])
                            logger.info(f"✅ Fixed: {issue['issue_type']} on {issue['table']}")
                            fixes_applied.append(
                                {
                                    "table": issue["table"],
                                    "issue": issue["issue_type"],
                                    "status": "fixed",
                                }
                            )
                        except Exception as e:
                            logger.error(f"❌ Failed to fix {issue['issue_type']}: {e}")
                            fixes_applied.append(
                                {
                                    "table": issue["table"],
                                    "issue": issue["issue_type"],
                                    "status": "failed",
                                    "error": str(e),
                                }
                            )

            return fixes_applied

        finally:
            await self.disconnect()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════


async def main():
    parser = argparse.ArgumentParser(
        description="SAHOOL Data Integrity Checker - فاحص سلامة البيانات"
    )

    parser.add_argument("--full", "-f", action="store_true", help="Run full integrity check")
    parser.add_argument("--tables", "-t", type=str, help="Comma-separated list of tables to check")
    parser.add_argument("--auto-fix", action="store_true", help="Automatically fix detected issues")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed without making changes"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--database", "-d", type=str, help="Database URL (overrides DATABASE_URL env)"
    )

    args = parser.parse_args()

    database_url = args.database or ASYNCPG_URL
    checker = DataIntegrityChecker(database_url)

    try:
        if args.auto_fix:
            fixes = await checker.auto_fix(dry_run=args.dry_run)
            if args.json:
                print(json.dumps(fixes, indent=2))
            else:
                print("\n" + "=" * 70)
                print("  🔧 AUTO-FIX RESULTS")
                print("=" * 70)
                for fix in fixes:
                    status_icon = (
                        "✅"
                        if fix["status"] == "fixed"
                        else "⏳"
                        if fix["status"] == "would_fix"
                        else "❌"
                    )
                    print(f"  {status_icon} {fix['table']}: {fix['issue']} - {fix['status']}")
                print("=" * 70 + "\n")
        else:
            report = await checker.run_all_checks()
            if args.json:
                print(report.to_json())
            else:
                report.print_summary()

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
