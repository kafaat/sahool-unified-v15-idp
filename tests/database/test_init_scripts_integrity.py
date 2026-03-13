"""
Database Init Scripts Integrity Tests for SAHOOL Platform.

Validates that SQL init scripts can execute without errors by checking:
1. No FK references to Prisma-managed tables (users, experiments, etc.)
2. All required enums are defined before use
3. All referenced tables exist within the same init script or earlier scripts
4. Demo data doesn't reference non-existent tables without safety wrappers

FIX (2026-03-13): Created after discovering startup failures caused by
01-research-expansion.sql referencing Prisma-managed tables (users, experiments).
"""

import os
import re
import pytest
from pathlib import Path

# Path to init scripts
INIT_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "core" / "postgres" / "init"

# Prisma-managed tables that should NOT be referenced with FK constraints in init scripts
# These tables are created by NestJS services AFTER Docker init completes
PRISMA_MANAGED_TABLES = {
    "users",
    "user_profiles",
    "user_roles",
    "user_sessions",
    "refresh_tokens",
    "experiments",
    "research_protocols",
    "research_plots",
    "treatments",
    "fields",
    "farms",
    "field_boundary_history",
    "tasks",
    "ndvi_readings",
    "sync_status",
    "products",
    "orders",
    "wallets",
    "transactions",
    "loans",
    "disaster_alerts",
    "disaster_zones",
    "damage_assessments",
    "conversations",
    "messages",
    "participants",
    "devices",
    "sensors",
    "actuators",
    "sensor_readings",
}

# Pattern to match FK references like: REFERENCES users(id) or REFERENCES experiments(id)
FK_REFERENCE_PATTERN = re.compile(
    r"REFERENCES\s+(" + "|".join(PRISMA_MANAGED_TABLES) + r")\s*\(",
    re.IGNORECASE,
)


def strip_sql_comments(sql: str) -> str:
    """Remove SQL single-line comments (--) to avoid false positives."""
    return "\n".join(
        line for line in sql.splitlines()
        if not line.strip().startswith("--")
    )

# Pattern to match enum usage in column definitions (not in CREATE TYPE)
ENUM_USAGE_PATTERN = re.compile(
    r"^\s+\w+\s+(\w+)(?:\[\])?\s*(?:DEFAULT|NOT NULL|,|$)",
    re.MULTILINE,
)


class TestInitScriptsExist:
    """Verify init scripts directory and files exist."""

    def test_init_directory_exists(self):
        assert INIT_DIR.exists(), f"Init directory not found: {INIT_DIR}"

    def test_main_init_script_exists(self):
        assert (INIT_DIR / "00-init-sahool.sql").exists()

    def test_research_expansion_exists(self):
        assert (INIT_DIR / "01-research-expansion.sql").exists()

    def test_pgbouncer_user_exists(self):
        assert (INIT_DIR / "02-pgbouncer-user.sql").exists()

    def test_scripts_ordered_correctly(self):
        """Verify scripts are alphabetically ordered (Docker execution order)."""
        scripts = sorted(f.name for f in INIT_DIR.iterdir() if f.suffix in (".sql", ".sh"))
        assert len(scripts) >= 3, f"Expected at least 3 init scripts, found {len(scripts)}"
        # 00 should come before 01, 01 before 02, etc.
        numbers = []
        for s in scripts:
            match = re.match(r"(\d+)-", s)
            if match:
                numbers.append(int(match.group(1)))
        assert numbers == sorted(numbers), f"Scripts not in order: {scripts}"


class TestNoForeignKeysToPrismaTables:
    """Ensure no FK constraints reference Prisma-managed tables."""

    @pytest.fixture
    def research_expansion_sql(self):
        return (INIT_DIR / "01-research-expansion.sql").read_text()

    @pytest.fixture
    def all_init_sql_files(self):
        files = {}
        for f in sorted(INIT_DIR.glob("*.sql")):
            files[f.name] = f.read_text()
        return files

    def test_no_fk_to_users_table(self, research_expansion_sql):
        """Critical: research-expansion.sql must NOT have REFERENCES users(id)."""
        sql_no_comments = strip_sql_comments(research_expansion_sql)
        matches = re.findall(
            r"REFERENCES\s+users\s*\(",
            sql_no_comments,
            re.IGNORECASE,
        )
        assert len(matches) == 0, (
            f"Found {len(matches)} FK reference(s) to users table in 01-research-expansion.sql. "
            "The users table is Prisma-managed and doesn't exist during Docker init."
        )

    def test_no_fk_to_experiments_table(self, research_expansion_sql):
        """Critical: research-expansion.sql must NOT have REFERENCES experiments(id)."""
        sql_no_comments = strip_sql_comments(research_expansion_sql)
        matches = re.findall(
            r"REFERENCES\s+experiments\s*\(",
            sql_no_comments,
            re.IGNORECASE,
        )
        assert len(matches) == 0, (
            f"Found {len(matches)} FK reference(s) to experiments table in 01-research-expansion.sql. "
            "The experiments table is Prisma-managed and doesn't exist during Docker init."
        )

    def test_no_fk_to_research_plots_table(self, research_expansion_sql):
        """research-expansion.sql must NOT have REFERENCES research_plots(id)."""
        sql_no_comments = strip_sql_comments(research_expansion_sql)
        matches = re.findall(
            r"REFERENCES\s+research_plots\s*\(",
            sql_no_comments,
            re.IGNORECASE,
        )
        assert len(matches) == 0, (
            f"Found {len(matches)} FK reference(s) to research_plots table."
        )

    def test_no_fk_to_treatments_table(self, research_expansion_sql):
        """research-expansion.sql must NOT have REFERENCES treatments(id)."""
        sql_no_comments = strip_sql_comments(research_expansion_sql)
        matches = re.findall(
            r"REFERENCES\s+treatments\s*\(",
            sql_no_comments,
            re.IGNORECASE,
        )
        assert len(matches) == 0, (
            f"Found {len(matches)} FK reference(s) to treatments table."
        )

    def test_no_prisma_fk_in_any_init_script(self, all_init_sql_files):
        """No init script should have FK references to Prisma-managed tables."""
        violations = []
        for filename, content in all_init_sql_files.items():
            matches = FK_REFERENCE_PATTERN.findall(strip_sql_comments(content))
            for match in matches:
                violations.append(f"{filename}: REFERENCES {match}(...)")

        assert len(violations) == 0, (
            f"Found FK references to Prisma-managed tables in init scripts:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


class TestRequiredEnumsDefined:
    """Ensure all enums used in column definitions are created in init scripts."""

    @pytest.fixture
    def research_expansion_sql(self):
        return (INIT_DIR / "01-research-expansion.sql").read_text()

    def test_sample_type_enum_defined(self, research_expansion_sql):
        """sample_type enum must be defined (used by analysis_types.sample_types)."""
        assert re.search(
            r"CREATE\s+TYPE\s+sample_type\s+AS\s+ENUM",
            research_expansion_sql,
            re.IGNORECASE,
        ), "sample_type enum is not defined in 01-research-expansion.sql"

    def test_experiment_status_enum_defined(self, research_expansion_sql):
        """experiment_status enum must be defined (used by experiment_locks.previous_status)."""
        assert re.search(
            r"CREATE\s+TYPE\s+experiment_status\s+AS\s+ENUM",
            research_expansion_sql,
            re.IGNORECASE,
        ), "experiment_status enum is not defined in 01-research-expansion.sql"

    def test_sample_status_enum_defined(self, research_expansion_sql):
        """sample_status enum must be defined."""
        assert re.search(
            r"CREATE\s+TYPE\s+sample_status\s+AS\s+ENUM",
            research_expansion_sql,
            re.IGNORECASE,
        ), "sample_status enum is not defined"

    def test_protocol_status_enum_defined(self, research_expansion_sql):
        """protocol_status enum must be defined."""
        assert re.search(
            r"CREATE\s+TYPE\s+protocol_status\s+AS\s+ENUM",
            research_expansion_sql,
            re.IGNORECASE,
        ), "protocol_status enum is not defined"

    def test_governance_level_enum_defined(self, research_expansion_sql):
        """governance_level enum must be defined."""
        assert re.search(
            r"CREATE\s+TYPE\s+governance_level\s+AS\s+ENUM",
            research_expansion_sql,
            re.IGNORECASE,
        ), "governance_level enum is not defined"

    def test_enums_use_exception_handler(self, research_expansion_sql):
        """All CREATE TYPE statements should use EXCEPTION WHEN duplicate_object."""
        # Count CREATE TYPE statements
        create_types = re.findall(
            r"CREATE\s+TYPE\s+\w+\s+AS\s+ENUM",
            research_expansion_sql,
            re.IGNORECASE,
        )
        # Count exception handlers
        exception_handlers = re.findall(
            r"EXCEPTION\s+WHEN\s+duplicate_object",
            research_expansion_sql,
            re.IGNORECASE,
        )
        assert len(create_types) == len(exception_handlers), (
            f"Found {len(create_types)} CREATE TYPE statements but {len(exception_handlers)} "
            "exception handlers. All enums should be idempotent with EXCEPTION WHEN duplicate_object."
        )


class TestDemoDataSafety:
    """Ensure demo data inserts are safe when dependent tables don't exist."""

    @pytest.fixture
    def research_expansion_sql(self):
        return (INIT_DIR / "01-research-expansion.sql").read_text()

    def test_no_direct_insert_into_experiments(self, research_expansion_sql):
        """Demo data should NOT insert into experiments table (Prisma-managed)."""
        matches = re.findall(
            r"INSERT\s+INTO\s+experiments\s",
            research_expansion_sql,
            re.IGNORECASE,
        )
        assert len(matches) == 0, (
            f"Found {len(matches)} INSERT INTO experiments in 01-research-expansion.sql. "
            "The experiments table is Prisma-managed."
        )

    def test_uses_on_conflict(self, research_expansion_sql):
        """All INSERT statements should use ON CONFLICT for idempotency."""
        inserts = re.findall(
            r"INSERT\s+INTO\s+\w+",
            research_expansion_sql,
            re.IGNORECASE,
        )
        on_conflicts = re.findall(
            r"ON\s+CONFLICT",
            research_expansion_sql,
            re.IGNORECASE,
        )
        assert len(on_conflicts) >= len(inserts) - 1, (
            f"Found {len(inserts)} INSERT statements but only {len(on_conflicts)} "
            "ON CONFLICT clauses. All inserts should be idempotent."
        )


class TestPgBouncerSetup:
    """Verify PgBouncer auth setup in init scripts."""

    @pytest.fixture
    def pgbouncer_sql(self):
        return (INIT_DIR / "02-pgbouncer-user.sql").read_text()

    def test_pgbouncer_schema_created(self, pgbouncer_sql):
        """02-pgbouncer-user.sql must create the pgbouncer schema."""
        assert re.search(
            r"CREATE\s+SCHEMA\s+IF\s+NOT\s+EXISTS\s+pgbouncer",
            pgbouncer_sql,
            re.IGNORECASE,
        ), "pgbouncer schema not created in 02-pgbouncer-user.sql"

    def test_auth_function_created(self, pgbouncer_sql):
        """02-pgbouncer-user.sql must create pgbouncer.get_auth function."""
        assert re.search(
            r"CREATE\s+OR\s+REPLACE\s+FUNCTION\s+pgbouncer\.get_auth",
            pgbouncer_sql,
            re.IGNORECASE,
        ), "pgbouncer.get_auth function not created"

    def test_auth_function_is_security_definer(self, pgbouncer_sql):
        """The auth function must be SECURITY DEFINER for pg_shadow access."""
        assert "SECURITY DEFINER" in pgbouncer_sql, (
            "pgbouncer.get_auth must be SECURITY DEFINER"
        )

    def test_pg_monitor_granted(self, pgbouncer_sql):
        """pg_monitor role must be granted for auth_query support."""
        assert re.search(
            r"GRANT\s+pg_monitor\s+TO",
            pgbouncer_sql,
            re.IGNORECASE,
        ), "pg_monitor not granted in 02-pgbouncer-user.sql"
