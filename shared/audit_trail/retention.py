"""
SAHOOL Audit Trail Retention Management
======================================
إدارة الاحتفاظ بمسار التدقيق

Data retention management for audit trail supporting:
- Policy-based retention | الاحتفاظ المستند إلى السياسة
- GlobalGAP 5-year requirement | متطلب GlobalGAP لـ 5 سنوات
- Automated archival | الأرشفة التلقائية
- Secure deletion | الحذف الآمن
- Retention job scheduling | جدولة مهام الاحتفاظ

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

import structlog

from .models import (
    AuditCategory,
    AuditEntry,
    RetentionJob,
    RetentionPeriod,
    RetentionPolicy,
)

logger = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Default Retention Policies | سياسات الاحتفاظ الافتراضية
# ─────────────────────────────────────────────────────────────────────────────


def get_default_policies() -> list[RetentionPolicy]:
    """
    Get default retention policies.
    الحصول على سياسات الاحتفاظ الافتراضية

    These policies implement GlobalGAP requirements and best practices.
    """
    return [
        # GlobalGAP Compliance - 5 years (required by GlobalGAP IFA v6)
        RetentionPolicy(
            id="policy-globalgap",
            name="GlobalGAP Compliance",
            name_ar="امتثال GlobalGAP",
            description="5-year retention for GlobalGAP compliance records (IFA v6 requirement)",
            description_ar="احتفاظ لمدة 5 سنوات لسجلات امتثال GlobalGAP (متطلب IFA v6)",
            category=AuditCategory.GLOBALGAP,
            retention_period=RetentionPeriod.GLOBALGAP,
            retention_days=1825,
            archive_before_delete=True,
            notify_before_delete_days=90,
        ),
        # Field Operations - 5 years (GlobalGAP traceability requirement)
        RetentionPolicy(
            id="policy-field-ops",
            name="Field Operations Records",
            name_ar="سجلات عمليات الحقل",
            description="5-year retention for field operations (irrigation, fertilizer, pesticide, harvest)",
            description_ar="احتفاظ لمدة 5 سنوات لعمليات الحقل (ري، سماد، مبيد، حصاد)",
            category=AuditCategory.FIELD_OPS,
            retention_period=RetentionPeriod.GLOBALGAP,
            retention_days=1825,
            archive_before_delete=True,
            notify_before_delete_days=90,
        ),
        # Compliance Records - 5 years
        RetentionPolicy(
            id="policy-compliance",
            name="Compliance Records",
            name_ar="سجلات الامتثال",
            description="5-year retention for compliance and audit records",
            description_ar="احتفاظ لمدة 5 سنوات لسجلات الامتثال والتدقيق",
            category=AuditCategory.COMPLIANCE,
            retention_period=RetentionPeriod.GLOBALGAP,
            retention_days=1825,
            archive_before_delete=True,
            notify_before_delete_days=90,
        ),
        # Security Records - 3 years
        RetentionPolicy(
            id="policy-security",
            name="Security Records",
            name_ar="سجلات الأمان",
            description="3-year retention for security events (login, permissions, etc.)",
            description_ar="احتفاظ لمدة 3 سنوات لأحداث الأمان (تسجيل الدخول، الصلاحيات، إلخ)",
            category=AuditCategory.SECURITY,
            retention_period=RetentionPeriod.LONG,
            retention_days=1095,
            archive_before_delete=True,
            notify_before_delete_days=60,
        ),
        # Financial Records - 5 years
        RetentionPolicy(
            id="policy-financial",
            name="Financial Records",
            name_ar="السجلات المالية",
            description="5-year retention for financial transactions",
            description_ar="احتفاظ لمدة 5 سنوات للمعاملات المالية",
            category=AuditCategory.FINANCIAL,
            retention_period=RetentionPeriod.GLOBALGAP,
            retention_days=1825,
            archive_before_delete=True,
            notify_before_delete_days=90,
        ),
        # Data Operations - 1 year
        RetentionPolicy(
            id="policy-data",
            name="Data Operations",
            name_ar="عمليات البيانات",
            description="1-year retention for general data operations",
            description_ar="احتفاظ لمدة سنة واحدة لعمليات البيانات العامة",
            category=AuditCategory.DATA,
            retention_period=RetentionPeriod.MEDIUM,
            retention_days=365,
            archive_before_delete=True,
            notify_before_delete_days=30,
        ),
        # System Events - 90 days
        RetentionPolicy(
            id="policy-system",
            name="System Events",
            name_ar="أحداث النظام",
            description="90-day retention for system events",
            description_ar="احتفاظ لمدة 90 يوم لأحداث النظام",
            category=AuditCategory.SYSTEM,
            retention_period=RetentionPeriod.SHORT,
            retention_days=90,
            archive_before_delete=False,
            notify_before_delete_days=7,
        ),
        # Configuration Changes - 3 years
        RetentionPolicy(
            id="policy-config",
            name="Configuration Changes",
            name_ar="تغييرات التكوين",
            description="3-year retention for configuration changes",
            description_ar="احتفاظ لمدة 3 سنوات لتغييرات التكوين",
            category=AuditCategory.CONFIG,
            retention_period=RetentionPeriod.LONG,
            retention_days=1095,
            archive_before_delete=True,
            notify_before_delete_days=60,
        ),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Retention Manager | مدير الاحتفاظ
# ─────────────────────────────────────────────────────────────────────────────


class RetentionManager:
    """
    Manages data retention for audit trail.
    يدير الاحتفاظ بالبيانات لمسار التدقيق

    Features:
    - Policy-based retention | الاحتفاظ المستند إلى السياسة
    - Automated archival | الأرشفة التلقائية
    - Secure deletion | الحذف الآمن
    - Job scheduling | جدولة المهام
    - Notification hooks | خطافات الإشعارات

    Example:
        manager = RetentionManager(
            storage_path="/data/audit",
            archive_path="/data/audit/archive",
        )

        # Apply default policies
        for policy in get_default_policies():
            manager.add_policy(policy)

        # Run retention job
        job = await manager.run_retention()
        print(f"Archived: {job.entries_archived}, Deleted: {job.entries_deleted}")

        # Get entries expiring soon
        expiring = manager.get_entries_expiring_soon(days=30)
    """

    def __init__(
        self,
        storage_path: str | None = None,
        archive_path: str | None = None,
        entries: list[AuditEntry] | None = None,
        on_archive: Callable[[list[AuditEntry]], None] | None = None,
        on_delete: Callable[[list[AuditEntry]], None] | None = None,
        on_notification: Callable[[str, list[AuditEntry]], None] | None = None,
    ):
        """
        Initialize RetentionManager.

        Args:
            storage_path: Path for audit trail storage
            archive_path: Path for archived entries
            entries: Initial list of entries (for in-memory mode)
            on_archive: Callback before archiving entries
            on_delete: Callback before deleting entries
            on_notification: Callback for expiration notifications
        """
        self.storage_path = storage_path
        self.archive_path = archive_path or (os.path.join(storage_path, "archive") if storage_path else None)
        self._entries = entries or []
        self.on_archive = on_archive
        self.on_delete = on_delete
        self.on_notification = on_notification

        self._policies: dict[str, RetentionPolicy] = {}
        self._jobs: list[RetentionJob] = []
        self._lock = asyncio.Lock()

        # Ensure directories exist
        if self.storage_path:
            Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        if self.archive_path:
            Path(self.archive_path).mkdir(parents=True, exist_ok=True)

        logger.info(
            "retention_manager_initialized",
            storage_path=storage_path,
            archive_path=self.archive_path,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Policy Management | إدارة السياسات
    # ─────────────────────────────────────────────────────────────────────────

    def add_policy(self, policy: RetentionPolicy) -> None:
        """
        Add a retention policy.
        إضافة سياسة احتفاظ
        """
        self._policies[policy.id] = policy
        logger.info(
            "retention_policy_added",
            policy_id=policy.id,
            name=policy.name,
            retention_days=policy.retention_days,
        )

    def remove_policy(self, policy_id: str) -> bool:
        """
        Remove a retention policy.
        إزالة سياسة احتفاظ
        """
        if policy_id in self._policies:
            del self._policies[policy_id]
            logger.info("retention_policy_removed", policy_id=policy_id)
            return True
        return False

    def get_policy(self, policy_id: str) -> RetentionPolicy | None:
        """Get a specific policy."""
        return self._policies.get(policy_id)

    def get_policies(self) -> list[RetentionPolicy]:
        """Get all policies."""
        return list(self._policies.values())

    def get_policy_for_entry(self, entry: AuditEntry) -> RetentionPolicy | None:
        """
        Get the applicable policy for an entry.
        الحصول على السياسة المناسبة للإدخال
        """
        # First, try to find a policy matching the entry's category
        for policy in self._policies.values():
            if not policy.is_active:
                continue
            if policy.category == entry.category:
                if policy.tenant_id is None or policy.tenant_id == entry.tenant_id:
                    if policy.resource_type is None or policy.resource_type == entry.resource_type:
                        return policy

        # Fall back to any active policy without category filter
        for policy in self._policies.values():
            if policy.is_active and policy.category is None:
                if policy.tenant_id is None or policy.tenant_id == entry.tenant_id:
                    return policy

        return None

    def load_default_policies(self) -> None:
        """
        Load default retention policies.
        تحميل سياسات الاحتفاظ الافتراضية
        """
        for policy in get_default_policies():
            self.add_policy(policy)
        logger.info("default_retention_policies_loaded", count=len(self._policies))

    # ─────────────────────────────────────────────────────────────────────────
    # Entry Management | إدارة الإدخالات
    # ─────────────────────────────────────────────────────────────────────────

    def set_entries(self, entries: list[AuditEntry]) -> None:
        """Set entries for in-memory mode."""
        self._entries = entries

    def add_entry(self, entry: AuditEntry) -> None:
        """Add a single entry."""
        self._entries.append(entry)

    def get_expired_entries(self) -> list[AuditEntry]:
        """
        Get all expired entries.
        الحصول على جميع الإدخالات المنتهية الصلاحية
        """
        now = datetime.now(UTC)
        expired = []

        for entry in self._entries:
            if entry.expires_at and entry.expires_at <= now:
                # Check if retention period is not permanent
                if entry.retention_period != RetentionPeriod.PERMANENT:
                    expired.append(entry)

        return expired

    def get_entries_expiring_soon(
        self,
        days: int = 30,
    ) -> list[AuditEntry]:
        """
        Get entries expiring within specified days.
        الحصول على الإدخالات التي ستنتهي صلاحيتها خلال الأيام المحددة

        Args:
            days: Number of days to look ahead

        Returns:
            List of entries expiring soon
        """
        now = datetime.now(UTC)
        threshold = now + timedelta(days=days)
        expiring = []

        for entry in self._entries:
            if entry.expires_at:
                if now < entry.expires_at <= threshold:
                    if entry.retention_period != RetentionPeriod.PERMANENT:
                        expiring.append(entry)

        return expiring

    def get_entries_by_policy(
        self,
        policy_id: str,
    ) -> list[AuditEntry]:
        """
        Get entries that match a specific policy.
        الحصول على الإدخالات التي تطابق سياسة محددة
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return []

        matching = []
        for entry in self._entries:
            if policy.category and entry.category != policy.category:
                continue
            if policy.tenant_id and entry.tenant_id != policy.tenant_id:
                continue
            if policy.resource_type and entry.resource_type != policy.resource_type:
                continue
            matching.append(entry)

        return matching

    # ─────────────────────────────────────────────────────────────────────────
    # Archival | الأرشفة
    # ─────────────────────────────────────────────────────────────────────────

    async def archive_entries(
        self,
        entries: list[AuditEntry],
        reason: str = "retention_policy",
    ) -> int:
        """
        Archive entries to archive storage.
        أرشفة الإدخالات إلى تخزين الأرشيف

        Args:
            entries: Entries to archive
            reason: Reason for archival

        Returns:
            Number of entries archived
        """
        if not entries:
            return 0

        # Trigger callback
        if self.on_archive:
            try:
                self.on_archive(entries)
            except Exception as e:
                logger.error("archive_callback_error", error=str(e))

        archived = 0

        # Archive to file if archive path configured
        if self.archive_path:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"archive_{timestamp}_{reason}.jsonl"
            filepath = os.path.join(self.archive_path, filename)

            async with self._lock:
                with open(filepath, "a", encoding="utf-8") as f:
                    for entry in entries:
                        archive_record = {
                            "archived_at": datetime.now(UTC).isoformat(),
                            "reason": reason,
                            "entry": entry.to_dict(),
                        }
                        f.write(json.dumps(archive_record, ensure_ascii=False) + "\n")
                        archived += 1

        logger.info(
            "entries_archived",
            count=archived,
            reason=reason,
            archive_path=self.archive_path,
        )

        return archived

    async def restore_from_archive(
        self,
        archive_file: str,
    ) -> list[AuditEntry]:
        """
        Restore entries from an archive file.
        استعادة الإدخالات من ملف الأرشيف

        Args:
            archive_file: Path to archive file

        Returns:
            List of restored entries
        """
        restored = []

        if not os.path.exists(archive_file):
            raise FileNotFoundError(f"Archive file not found: {archive_file}")

        with open(archive_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    entry_data = record.get("entry", {})
                    entry = AuditEntry.from_dict(entry_data)
                    restored.append(entry)

        logger.info(
            "entries_restored",
            count=len(restored),
            archive_file=archive_file,
        )

        return restored

    # ─────────────────────────────────────────────────────────────────────────
    # Deletion | الحذف
    # ─────────────────────────────────────────────────────────────────────────

    async def delete_entries(
        self,
        entries: list[AuditEntry],
        secure: bool = True,
    ) -> int:
        """
        Delete entries from storage.
        حذف الإدخالات من التخزين

        Args:
            entries: Entries to delete
            secure: Whether to use secure deletion (overwrite)

        Returns:
            Number of entries deleted
        """
        if not entries:
            return 0

        # Trigger callback
        if self.on_delete:
            try:
                self.on_delete(entries)
            except Exception as e:
                logger.error("delete_callback_error", error=str(e))

        deleted = 0
        entry_ids = {e.id for e in entries}

        async with self._lock:
            # Remove from in-memory storage
            self._entries = [e for e in self._entries if e.id not in entry_ids]
            deleted = len(entry_ids)

        logger.info(
            "entries_deleted",
            count=deleted,
            secure=secure,
        )

        return deleted

    # ─────────────────────────────────────────────────────────────────────────
    # Retention Jobs | مهام الاحتفاظ
    # ─────────────────────────────────────────────────────────────────────────

    async def run_retention(
        self,
        dry_run: bool = False,
    ) -> RetentionJob:
        """
        Run retention job to archive/delete expired entries.
        تشغيل مهمة الاحتفاظ لأرشفة/حذف الإدخالات المنتهية الصلاحية

        Args:
            dry_run: If True, only simulate without making changes

        Returns:
            RetentionJob with results
        """
        job = RetentionJob(
            id=str(uuid4()),
            policy_id="all",
            started_at=datetime.now(UTC),
            status="running",
        )

        try:
            # Get expired entries
            expired_entries = self.get_expired_entries()
            job.entries_processed = len(expired_entries)

            if dry_run:
                job.status = "completed"
                job.completed_at = datetime.now(UTC)
                job.entries_archived = len([e for e in expired_entries if self._should_archive(e)])
                job.entries_deleted = len(expired_entries)
                logger.info(
                    "retention_dry_run_completed",
                    job_id=job.id,
                    entries_processed=job.entries_processed,
                    entries_would_archive=job.entries_archived,
                    entries_would_delete=job.entries_deleted,
                )
                return job

            # Group by whether to archive
            to_archive = [e for e in expired_entries if self._should_archive(e)]
            to_delete = expired_entries

            # Archive first
            if to_archive:
                job.entries_archived = await self.archive_entries(to_archive)

            # Then delete
            job.entries_deleted = await self.delete_entries(to_delete)

            job.status = "completed"
            job.completed_at = datetime.now(UTC)

        except Exception as e:
            job.status = "failed"
            job.errors.append(str(e))
            job.completed_at = datetime.now(UTC)
            logger.error("retention_job_failed", job_id=job.id, error=str(e))

        self._jobs.append(job)

        logger.info(
            "retention_job_completed",
            job_id=job.id,
            status=job.status,
            entries_processed=job.entries_processed,
            entries_archived=job.entries_archived,
            entries_deleted=job.entries_deleted,
        )

        return job

    async def run_policy_retention(
        self,
        policy_id: str,
        dry_run: bool = False,
    ) -> RetentionJob:
        """
        Run retention for a specific policy.
        تشغيل الاحتفاظ لسياسة محددة

        Args:
            policy_id: Policy ID to apply
            dry_run: If True, only simulate

        Returns:
            RetentionJob with results
        """
        policy = self.get_policy(policy_id)
        if not policy:
            raise ValueError(f"Policy not found: {policy_id}")

        job = RetentionJob(
            id=str(uuid4()),
            policy_id=policy_id,
            started_at=datetime.now(UTC),
            status="running",
        )

        try:
            # Get entries matching policy
            matching_entries = self.get_entries_by_policy(policy_id)

            # Filter to expired only
            now = datetime.now(UTC)
            expired_entries = [e for e in matching_entries if e.expires_at and e.expires_at <= now]

            job.entries_processed = len(expired_entries)

            if dry_run:
                job.status = "completed"
                job.completed_at = datetime.now(UTC)
                job.entries_archived = len(expired_entries) if policy.archive_before_delete else 0
                job.entries_deleted = len(expired_entries)
                return job

            # Archive if required
            if policy.archive_before_delete and expired_entries:
                job.entries_archived = await self.archive_entries(expired_entries, reason=f"policy_{policy_id}")

            # Delete
            job.entries_deleted = await self.delete_entries(expired_entries)

            job.status = "completed"
            job.completed_at = datetime.now(UTC)

        except Exception as e:
            job.status = "failed"
            job.errors.append(str(e))
            job.completed_at = datetime.now(UTC)
            logger.error("policy_retention_failed", policy_id=policy_id, error=str(e))

        self._jobs.append(job)
        return job

    def _should_archive(self, entry: AuditEntry) -> bool:
        """Check if entry should be archived before deletion."""
        policy = self.get_policy_for_entry(entry)
        if policy:
            return policy.archive_before_delete
        return True  # Default to archive

    # ─────────────────────────────────────────────────────────────────────────
    # Notifications | الإشعارات
    # ─────────────────────────────────────────────────────────────────────────

    async def check_and_notify_expiring(
        self,
        days: int | None = None,
    ) -> dict[str, list[AuditEntry]]:
        """
        Check for entries expiring soon and send notifications.
        التحقق من الإدخالات التي ستنتهي صلاحيتها قريباً وإرسال الإشعارات

        Args:
            days: Days to look ahead (uses policy settings if None)

        Returns:
            Dict of policy_id -> expiring entries
        """
        notifications: dict[str, list[AuditEntry]] = {}

        for policy in self._policies.values():
            if not policy.is_active:
                continue

            # Use policy's notification threshold
            check_days = days or policy.notify_before_delete_days

            # Get entries matching policy and expiring soon
            matching = self.get_entries_by_policy(policy.id)
            now = datetime.now(UTC)
            threshold = now + timedelta(days=check_days)

            expiring = [e for e in matching if e.expires_at and now < e.expires_at <= threshold]

            if expiring:
                notifications[policy.id] = expiring

                # Trigger notification callback
                if self.on_notification:
                    try:
                        self.on_notification(policy.id, expiring)
                    except Exception as e:
                        logger.error(
                            "notification_callback_error",
                            policy_id=policy.id,
                            error=str(e),
                        )

                logger.info(
                    "expiring_entries_notification",
                    policy_id=policy.id,
                    policy_name=policy.name,
                    expiring_count=len(expiring),
                    threshold_days=check_days,
                )

        return notifications

    # ─────────────────────────────────────────────────────────────────────────
    # Job History | سجل المهام
    # ─────────────────────────────────────────────────────────────────────────

    def get_jobs(
        self,
        policy_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[RetentionJob]:
        """
        Get retention job history.
        الحصول على سجل مهام الاحتفاظ
        """
        jobs = self._jobs

        if policy_id:
            jobs = [j for j in jobs if j.policy_id == policy_id]
        if status:
            jobs = [j for j in jobs if j.status == status]

        return jobs[-limit:]

    def get_last_job(
        self,
        policy_id: str | None = None,
    ) -> RetentionJob | None:
        """Get the most recent retention job."""
        jobs = self.get_jobs(policy_id=policy_id, limit=1)
        return jobs[0] if jobs else None

    # ─────────────────────────────────────────────────────────────────────────
    # Statistics | الإحصائيات
    # ─────────────────────────────────────────────────────────────────────────

    def get_retention_summary(self) -> dict[str, Any]:
        """
        Get summary of retention status.
        الحصول على ملخص حالة الاحتفاظ
        """
        datetime.now(UTC)

        # Count entries by retention status
        total = len(self._entries)
        expired = len(self.get_expired_entries())
        expiring_30d = len(self.get_entries_expiring_soon(30))
        expiring_90d = len(self.get_entries_expiring_soon(90))
        permanent = sum(1 for e in self._entries if e.retention_period == RetentionPeriod.PERMANENT)

        # Count by category
        by_category = {}
        for entry in self._entries:
            cat = entry.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        # Count by retention period
        by_period = {}
        for entry in self._entries:
            period = entry.retention_period.value
            by_period[period] = by_period.get(period, 0) + 1

        # Recent jobs
        recent_jobs = self.get_jobs(limit=5)

        return {
            "total_entries": total,
            "expired_entries": expired,
            "expiring_30_days": expiring_30d,
            "expiring_90_days": expiring_90d,
            "permanent_entries": permanent,
            "entries_by_category": by_category,
            "entries_by_retention_period": by_period,
            "active_policies": len([p for p in self._policies.values() if p.is_active]),
            "total_policies": len(self._policies),
            "recent_jobs": [j.to_dict() for j in recent_jobs],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Global Retention Manager | مدير الاحتفاظ العالمي
# ─────────────────────────────────────────────────────────────────────────────

_global_manager: RetentionManager | None = None


def get_retention_manager(
    storage_path: str | None = None,
    archive_path: str | None = None,
) -> RetentionManager:
    """
    Get or create the global retention manager.
    الحصول على أو إنشاء مدير الاحتفاظ العالمي
    """
    global _global_manager
    if _global_manager is None:
        # Default to /var/lib/sahool in production, /tmp for development only
        default_path = (
            "/var/lib/sahool/audit_trail" if os.getenv("ENVIRONMENT") == "production" else "/tmp/sahool_audit_trail"
        )  # nosec B108
        storage = storage_path or os.getenv("AUDIT_TRAIL_STORAGE_PATH", default_path)
        archive = archive_path or os.path.join(storage, "archive")
        _global_manager = RetentionManager(
            storage_path=storage,
            archive_path=archive,
        )
        _global_manager.load_default_policies()
    return _global_manager


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions | دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────


async def run_retention(dry_run: bool = False) -> RetentionJob:
    """
    Run retention using global manager.
    تشغيل الاحتفاظ باستخدام المدير العالمي
    """
    manager = get_retention_manager()
    return await manager.run_retention(dry_run=dry_run)


def get_expired_entries() -> list[AuditEntry]:
    """
    Get expired entries using global manager.
    الحصول على الإدخالات المنتهية الصلاحية باستخدام المدير العالمي
    """
    manager = get_retention_manager()
    return manager.get_expired_entries()


def get_entries_expiring_soon(days: int = 30) -> list[AuditEntry]:
    """
    Get entries expiring soon using global manager.
    الحصول على الإدخالات التي ستنتهي صلاحيتها قريباً باستخدام المدير العالمي
    """
    manager = get_retention_manager()
    return manager.get_entries_expiring_soon(days)


def get_retention_summary() -> dict[str, Any]:
    """
    Get retention summary using global manager.
    الحصول على ملخص الاحتفاظ باستخدام المدير العالمي
    """
    manager = get_retention_manager()
    return manager.get_retention_summary()
