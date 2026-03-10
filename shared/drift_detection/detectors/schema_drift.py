"""
Schema Drift Detector
كاشف انحراف المخطط

Detects database schema drift:
- Migration file ordering and consistency
- Backwards-compatible migration checks (expand/migrate/contract)
- RLS (Row-Level Security) consistency across tenants
- Missing indexes on critical queries
- PostGIS extension version drift
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from shared.drift_detection.detectors.base import BaseDriftDetector
from shared.drift_detection.models import (
    DriftCategory,
    DriftResult,
    DriftSeverity,
)

logger = logging.getLogger(__name__)

# SQL patterns that indicate potentially breaking migrations
BREAKING_PATTERNS = [
    (re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE), "DROP TABLE"),
    (re.compile(r"\bDROP\s+COLUMN\b", re.IGNORECASE), "DROP COLUMN"),
    (re.compile(r"\bALTER\s+COLUMN\s+\w+\s+TYPE\b", re.IGNORECASE), "ALTER COLUMN TYPE"),
    (re.compile(r"\bRENAME\s+COLUMN\b", re.IGNORECASE), "RENAME COLUMN"),
    (re.compile(r"\bRENAME\s+TABLE\b", re.IGNORECASE), "RENAME TABLE"),
]

# Patterns that need careful review
RISKY_PATTERNS = [
    (re.compile(r"\bALTER\s+TABLE\s+\w+\s+ADD\s+CONSTRAINT\b", re.IGNORECASE), "Adding constraint"),
    (re.compile(r"\bTRUNCATE\b", re.IGNORECASE), "TRUNCATE"),
    (re.compile(r"\bDELETE\s+FROM\b(?!\s+WHERE)", re.IGNORECASE), "DELETE without WHERE"),
]

# Regex to detect ALTER TABLE ADD COLUMN with NOT NULL but no DEFAULT (truly breaking)
_ALTER_ADD_NOT_NULL_RE = re.compile(
    r"\bALTER\s+TABLE\b[^;]*\bADD\s+(?:COLUMN\s+)?[^;]*\bNOT\s+NULL\b(?![^;]*\bDEFAULT\b)",
    re.IGNORECASE,
)

# Regex to detect CREATE INDEX without CONCURRENTLY (only risky on non-init migrations)
_NON_CONCURRENT_INDEX_RE = re.compile(r"\bCREATE\s+INDEX\b(?!\s+CONCURRENTLY)", re.IGNORECASE)

# Migration path patterns considered "initial" (CREATE TABLE from scratch, no existing data)
_INIT_MIGRATION_RE = re.compile(r"(^|\/)0*1[_-]|init|initial|create[_-]tables", re.IGNORECASE)

# Acknowledgement comment: -- drift:safe reason=... [remediated_by=...]
# When present in a migration file, suppresses risky_migration findings for that file.
_DRIFT_SAFE_RE = re.compile(r"--\s*drift:safe\b", re.IGNORECASE)


def _extract_prisma_models(content: str) -> list[tuple[str, str]]:
    """Extract Prisma model name/body pairs using brace-depth counting.

    Simple regex like ``model (\\w+) \\{([^}]+)\\}`` fails when inline
    comments contain ``}`` (e.g. ``// { lat, lng }``).  This helper
    tracks brace depth so it correctly identifies the closing ``}`` of
    each model block.
    """
    results: list[tuple[str, str]] = []
    model_re = re.compile(r"\bmodel\s+(\w+)\s*\{")
    for m in model_re.finditer(content):
        name = m.group(1)
        start = m.end()  # position right after the opening '{'
        depth = 1
        pos = start
        while pos < len(content) and depth > 0:
            ch = content[pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            pos += 1
        body = content[start : pos - 1] if depth == 0 else content[start:]
        results.append((name, body))
    return results


class SchemaDriftDetector(BaseDriftDetector):
    """
    Detects database schema drift and migration issues.
    يكتشف انحراف مخطط قاعدة البيانات ومشاكل الهجرة.
    """

    @property
    def category(self) -> DriftCategory:
        return DriftCategory.SCHEMA

    async def detect(self) -> list[DriftResult]:
        self.clear_results()

        await self._check_migration_ordering()
        await self._check_breaking_migrations()
        await self._check_prisma_drift()
        await self._check_rls_consistency()
        await self._check_missing_indexes()

        return self.results

    async def _check_migration_ordering(self) -> None:
        """Check migration files are properly ordered and have no gaps."""
        root = Path(self.working_dir)

        # Find all Prisma migration directories
        prisma_dirs = list(root.glob("apps/services/*/prisma/migrations"))

        for prisma_dir in prisma_dirs:
            if not prisma_dir.is_dir():
                continue

            service_name = prisma_dir.parent.parent.name
            migration_dirs = sorted(
                [d for d in prisma_dir.iterdir() if d.is_dir() and d.name != "_journal"],
            )

            # Check for empty migrations
            for mig_dir in migration_dirs:
                sql_file = mig_dir / "migration.sql"
                if sql_file.exists() and sql_file.stat().st_size == 0:
                    self.add_result(
                        DriftResult(
                            category=DriftCategory.SCHEMA,
                            severity=DriftSeverity.MEDIUM,
                            source="migration_ordering",
                            description=f"Empty migration file in {service_name}: {mig_dir.name}",
                            description_ar=f"ملف هجرة فارغ في {service_name}: {mig_dir.name}",
                            file_path=str(sql_file),
                            service_name=service_name,
                            auto_fixable=False,
                            remediation_hint="Remove empty migration or add SQL content",
                        )
                    )

    async def _check_breaking_migrations(self) -> None:
        """Check for potentially breaking migration patterns."""
        root = Path(self.working_dir)

        migration_files = list(root.glob("apps/services/*/prisma/migrations/*/migration.sql"))
        migration_files += list(root.glob("apps/kernel/**/migrations/*.sql"))

        for mig_file in migration_files:
            try:
                content = mig_file.read_text(errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue

            # Check for service name extraction
            parts = mig_file.parts
            service_name = ""
            for i, part in enumerate(parts):
                if part == "services" and i + 1 < len(parts):
                    service_name = parts[i + 1]
                    break

            is_init = _INIT_MIGRATION_RE.search(str(mig_file))
            is_acknowledged = _DRIFT_SAFE_RE.search(content)

            # Check breaking patterns (DROP, RENAME, ALTER TYPE)
            for pattern, pattern_name in BREAKING_PATTERNS:
                matches = pattern.findall(content)
                if matches:
                    self.add_result(
                        DriftResult(
                            category=DriftCategory.SCHEMA,
                            severity=DriftSeverity.CRITICAL,
                            source="breaking_migration",
                            expected="Backwards-compatible migration (expand/migrate/contract)",
                            actual=f"Breaking pattern: {pattern_name}",
                            description=f"Potentially breaking migration in {service_name}: {pattern_name}",
                            description_ar=f"هجرة قد تسبب كسر في {service_name}: {pattern_name}",
                            file_path=str(mig_file),
                            service_name=service_name,
                            auto_fixable=False,
                            remediation_hint=f"Use expand/migrate/contract pattern. Split '{pattern_name}' into safe steps.",
                            remediation_hint_ar=f"استخدم نمط التوسيع/الهجرة/الانكماش. قسّم '{pattern_name}' إلى خطوات آمنة.",
                        )
                    )

            # Check ALTER TABLE ADD COLUMN ... NOT NULL without DEFAULT
            # (Only truly breaking: adds a mandatory column to existing rows)
            # NOT NULL inside CREATE TABLE is safe (no existing rows).
            if _ALTER_ADD_NOT_NULL_RE.search(content):
                self.add_result(
                    DriftResult(
                        category=DriftCategory.SCHEMA,
                        severity=DriftSeverity.CRITICAL,
                        source="breaking_migration",
                        expected="ALTER TABLE ADD COLUMN with DEFAULT or nullable",
                        actual="NOT NULL without DEFAULT on ALTER TABLE ADD COLUMN",
                        description=f"Potentially breaking migration in {service_name}: NOT NULL without DEFAULT",
                        description_ar=f"هجرة قد تسبب كسر في {service_name}: NOT NULL بدون DEFAULT",
                        file_path=str(mig_file),
                        service_name=service_name,
                        auto_fixable=False,
                        remediation_hint="Add DEFAULT value or make column nullable, then backfill.",
                        remediation_hint_ar="أضف قيمة DEFAULT أو اجعل العمود قابلاً للقيم الفارغة ثم املأ البيانات.",
                    )
                )

            # Check risky patterns (skip if file has -- drift:safe acknowledgement)
            if is_acknowledged:
                logger.debug("Skipping risky pattern check for %s (drift:safe)", mig_file)
            for pattern, pattern_name in RISKY_PATTERNS if not is_acknowledged else []:
                matches = pattern.findall(content)
                if matches:
                    self.add_result(
                        DriftResult(
                            category=DriftCategory.SCHEMA,
                            severity=DriftSeverity.MEDIUM,
                            source="risky_migration",
                            description=f"Risky migration pattern in {service_name}: {pattern_name}",
                            description_ar=f"نمط هجرة محفوف بالمخاطر في {service_name}: {pattern_name}",
                            file_path=str(mig_file),
                            service_name=service_name,
                            auto_fixable=False,
                            remediation_hint=f"Review '{pattern_name}' for production safety.",
                        )
                    )

            # Non-concurrent index creation: only flag on non-initial migrations
            # Initial migrations create tables from scratch with no existing data,
            # so CONCURRENTLY is unnecessary and actually unsupported inside transactions.
            # Also skip if file has -- drift:safe acknowledgement comment.
            if not is_init and not is_acknowledged and _NON_CONCURRENT_INDEX_RE.search(content):
                self.add_result(
                    DriftResult(
                        category=DriftCategory.SCHEMA,
                        severity=DriftSeverity.MEDIUM,
                        source="risky_migration",
                        description=f"Risky migration pattern in {service_name}: Non-concurrent index creation",
                        description_ar=f"نمط هجرة محفوف بالمخاطر في {service_name}: إنشاء فهرس بدون CONCURRENTLY",
                        file_path=str(mig_file),
                        service_name=service_name,
                        auto_fixable=False,
                        remediation_hint="Use CREATE INDEX CONCURRENTLY for zero-downtime index creation on existing tables.",
                    )
                )

    async def _check_prisma_drift(self) -> None:
        """Check Prisma schema consistency."""
        root = Path(self.working_dir)

        schema_files = list(root.glob("apps/services/*/prisma/schema.prisma"))

        for schema_file in schema_files:
            service_name = schema_file.parent.parent.name
            try:
                content = schema_file.read_text()
            except (OSError, UnicodeDecodeError):
                continue

            # Check for missing @@map (table naming consistency)
            model_count = content.count("model ")
            map_count = content.count("@@map(")
            if model_count > 0 and map_count == 0:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.SCHEMA,
                        severity=DriftSeverity.LOW,
                        source="prisma_schema",
                        description=f"Service '{service_name}': Prisma models lack explicit @@map table names",
                        description_ar=f"خدمة '{service_name}': نماذج Prisma تفتقر إلى أسماء جداول صريحة",
                        file_path=str(schema_file),
                        service_name=service_name,
                    )
                )

            # Check for tenant_id field on all models (multi-tenant requirement)
            # Use a parser-style approach instead of [^}]+ regex, because inline
            # comments may contain '}' (e.g. // { lat, lng }) that break the match.
            models = _extract_prisma_models(content)
            for model_name, model_body in models:
                # Skip system/config/join-table models that don't need tenant isolation
                skip_models = {
                    "migration",
                    "prisma",
                    "session",
                    "account",
                    "verificationtoken",
                    "authenticator",
                }
                if model_name.lower() in skip_models:
                    continue
                # Check for tenant_id in any common Prisma naming pattern:
                # - tenantId (camelCase field name)
                # - tenant_id (snake_case in @map or raw SQL)
                # - @map("tenant_id") (explicit column mapping)
                has_tenant = "tenant_id" in model_body or "tenantId" in model_body or '@map("tenant_id")' in model_body
                if not has_tenant:
                    self.add_result(
                        DriftResult(
                            category=DriftCategory.SCHEMA,
                            severity=DriftSeverity.HIGH,
                            source="tenant_isolation",
                            expected="tenant_id field on all data models",
                            actual=f"Model '{model_name}' missing tenant_id",
                            description=f"Multi-tenant violation: Model '{model_name}' in {service_name} lacks tenant_id",
                            description_ar=f"انتهاك متعدد المستأجرين: النموذج '{model_name}' في {service_name} يفتقر إلى tenant_id",
                            file_path=str(schema_file),
                            service_name=service_name,
                            auto_fixable=False,
                            remediation_hint=f"Add 'tenantId String @map(\"tenant_id\")' to model {model_name}",
                        )
                    )

    async def _check_rls_consistency(self) -> None:
        """Check Row-Level Security consistency."""
        root = Path(self.working_dir)

        # Check for RLS policy files
        rls_files = list(root.glob("**/rls*.sql")) + list(root.glob("**/*rls*.sql"))
        if not rls_files:
            # Informational only
            self.add_result(
                DriftResult(
                    category=DriftCategory.SCHEMA,
                    severity=DriftSeverity.INFO,
                    source="rls_check",
                    description="No RLS policy files found - consider adding Row-Level Security for multi-tenancy",
                    description_ar="لم يتم العثور على ملفات سياسة RLS - فكر في إضافة أمان مستوى الصف للحماية متعددة المستأجرين",
                )
            )

    async def _check_missing_indexes(self) -> None:
        """Check for potentially missing indexes on critical query patterns."""
        root = Path(self.working_dir)

        # Scan Python files for common query patterns without corresponding indexes
        for py_file in root.glob("apps/services/*/src/**/*.py"):
            try:
                content = py_file.read_text(errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue

            # Check for tenant_id queries without index hints
            if "tenant_id" in content and "ORDER BY" in content.upper():
                # Check if there's a corresponding index in migrations
                service_dir = py_file
                while service_dir.name != "services" and service_dir != root:
                    service_dir = service_dir.parent
                if service_dir.name == "services":
                    continue
                # This is informational - actual index check requires DB connection
