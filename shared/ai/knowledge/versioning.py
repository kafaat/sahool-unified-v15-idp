# =============================================================================
# Document Versioning (GAP-14)
# =============================================================================
#
# Manages version history for knowledge documents with full snapshot tracking,
# diff computation, and rollback capabilities.
#
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from shared.ai.knowledge._logging import get_logger

from .models import BaseKnowledgeDocument

logger = get_logger(__name__)


@dataclass
class DocumentVersion:
    """A single version snapshot of a document.
    لقطة إصدار واحدة لوثيقة"""

    version: str  # semver like "1.0.0"
    timestamp: datetime
    author: str = ""
    change_summary: str = ""
    change_summary_ar: str = ""
    data: dict[str, Any] = field(default_factory=dict)  # Full document snapshot


@dataclass
class VersionDiff:
    """Differences between two versions.
    الفروقات بين إصدارين"""

    old_version: str
    new_version: str
    added_fields: list[str] = field(default_factory=list)
    removed_fields: list[str] = field(default_factory=list)
    modified_fields: list[str] = field(default_factory=list)
    content_changed: bool = False
    content_ar_changed: bool = False


class DocumentVersionManager:
    """Manages version history for knowledge documents.
    يدير سجل الإصدارات لوثائق المعرفة"""

    def __init__(self) -> None:
        # dict[document_id, list[DocumentVersion]]
        self._history: dict[str, list[DocumentVersion]] = {}

    def track(
        self,
        document: BaseKnowledgeDocument,
        author: str = "",
        change_summary: str = "",
        change_summary_ar: str = "",
    ) -> str:
        """Record current state as a new version. Returns new version string.
        تسجيل الحالة الحالية كإصدار جديد. يُرجع رقم الإصدار الجديد"""
        doc_id = document.id
        snapshot = document.model_dump()

        versions = self._history.get(doc_id, [])

        if versions:
            latest = versions[-1]
            new_version = self._increment_version(latest.version)
        else:
            new_version = document.version or "1.0.0"

        entry = DocumentVersion(
            version=new_version,
            timestamp=datetime.utcnow(),
            author=author,
            change_summary=change_summary,
            change_summary_ar=change_summary_ar,
            data=snapshot,
        )

        if doc_id not in self._history:
            self._history[doc_id] = []
        self._history[doc_id].append(entry)

        logger.info(
            "document_version_tracked",
            document_id=doc_id,
            version=new_version,
            author=author,
            change_summary=change_summary,
        )

        return new_version

    def get_history(self, document_id: str) -> list[DocumentVersion]:
        """Get all versions for a document.
        الحصول على جميع الإصدارات لوثيقة"""
        return list(self._history.get(document_id, []))

    def get_version(self, document_id: str, version: str) -> DocumentVersion | None:
        """Get a specific version.
        الحصول على إصدار محدد"""
        versions = self._history.get(document_id, [])
        for v in versions:
            if v.version == version:
                return v
        return None

    def get_latest(self, document_id: str) -> DocumentVersion | None:
        """Get the latest version.
        الحصول على أحدث إصدار"""
        versions = self._history.get(document_id, [])
        if not versions:
            return None
        return versions[-1]

    def diff(self, document_id: str, version_a: str, version_b: str) -> VersionDiff | None:
        """Compare two versions of a document.
        مقارنة إصدارين من وثيقة"""
        va = self.get_version(document_id, version_a)
        vb = self.get_version(document_id, version_b)
        if va is None or vb is None:
            logger.warning(
                "version_diff_failed",
                document_id=document_id,
                version_a=version_a,
                version_b=version_b,
                reason="one or both versions not found",
            )
            return None
        return self._compute_diff(va.data, vb.data, version_a, version_b)

    def rollback(self, document_id: str, target_version: str) -> dict[str, Any] | None:
        """Get document data at a specific version for restoration.
        الحصول على بيانات الوثيقة عند إصدار محدد للاستعادة"""
        version = self.get_version(document_id, target_version)
        if version is None:
            logger.warning(
                "rollback_version_not_found",
                document_id=document_id,
                target_version=target_version,
            )
            return None

        logger.info(
            "document_rollback_retrieved",
            document_id=document_id,
            target_version=target_version,
        )
        return dict(version.data)

    def _increment_version(self, current: str) -> str:
        """Increment patch version: 1.0.0 -> 1.0.1
        زيادة رقم الإصدار الفرعي"""
        parts = current.split(".")
        if len(parts) != 3:
            # If the version string is malformed, default to appending .1
            return current + ".1"
        try:
            parts[2] = str(int(parts[2]) + 1)
        except ValueError:
            parts[2] = "1"
        return ".".join(parts)

    def _compute_diff(
        self,
        old_data: dict[str, Any],
        new_data: dict[str, Any],
        old_version: str = "",
        new_version: str = "",
    ) -> VersionDiff:
        """Compute field-level diff between two snapshots.
        حساب الفروقات على مستوى الحقول بين لقطتين"""
        old_keys = set(old_data.keys())
        new_keys = set(new_data.keys())

        added = sorted(new_keys - old_keys)
        removed = sorted(old_keys - new_keys)

        modified: list[str] = []
        for key in sorted(old_keys & new_keys):
            if old_data[key] != new_data[key]:
                modified.append(key)

        content_changed = "content" in modified
        content_ar_changed = "content_ar" in modified

        return VersionDiff(
            old_version=old_version,
            new_version=new_version,
            added_fields=added,
            removed_fields=removed,
            modified_fields=modified,
            content_changed=content_changed,
            content_ar_changed=content_ar_changed,
        )
