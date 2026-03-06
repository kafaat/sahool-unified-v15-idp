# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Freshness Monitor
# مراقب حداثة قاعدة المعرفة الزراعية
# ═══════════════════════════════════════════════════════════════════════════════
#
# Monitors knowledge documents for expiration and staleness:
#   - Checks FRESHMetadata.expiration_date for expired documents
#   - Identifies documents nearing expiration (configurable warning window)
#   - Reports freshness statistics per collection/domain
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import structlog

from .models import BaseKnowledgeDocument, KnowledgeDomain

logger = structlog.get_logger(__name__)


@dataclass
class FreshnessAlert:
    """Alert for a document freshness issue | تنبيه حداثة وثيقة"""

    document_id: str
    title: str
    domain: str
    severity: str  # expired, expiring_soon, stale
    expiration_date: date | None = None
    days_until_expiry: int | None = None
    message: str = ""
    message_ar: str = ""


@dataclass
class FreshnessReport:
    """Freshness status report | تقرير حالة الحداثة"""

    total_documents: int = 0
    fresh_count: int = 0
    expiring_soon_count: int = 0
    expired_count: int = 0
    no_expiration_count: int = 0
    alerts: list[FreshnessAlert] = field(default_factory=list)
    by_domain: dict[str, dict[str, int]] = field(default_factory=dict)
    by_collection: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def health_score(self) -> float:
        """Overall freshness health score (0.0-1.0)."""
        if self.total_documents == 0:
            return 1.0
        active = self.fresh_count + self.no_expiration_count
        return active / self.total_documents

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_documents": self.total_documents,
            "fresh": self.fresh_count,
            "expiring_soon": self.expiring_soon_count,
            "expired": self.expired_count,
            "no_expiration": self.no_expiration_count,
            "health_score": round(self.health_score, 3),
            "alerts_count": len(self.alerts),
            "by_domain": self.by_domain,
        }


class KnowledgeFreshnessMonitor:
    """Monitors knowledge base documents for freshness and expiration.
    يراقب وثائق قاعدة المعرفة من حيث الحداثة وانتهاء الصلاحية"""

    def __init__(
        self,
        warning_days: int = 30,
        reference_date: date | None = None,
    ) -> None:
        self._warning_days = warning_days
        self._reference_date = reference_date or date.today()

    def check_documents(
        self,
        documents: list[BaseKnowledgeDocument],
    ) -> FreshnessReport:
        """Check freshness of a list of knowledge documents.
        فحص حداثة قائمة من وثائق المعرفة"""
        report = FreshnessReport(total_documents=len(documents))

        for doc in documents:
            exp_date = doc.fresh.expiration_date
            domain_key = doc.domain.value if isinstance(doc.domain, KnowledgeDomain) else str(doc.domain)
            collection = doc._get_collection()

            # Initialize domain/collection counters
            if domain_key not in report.by_domain:
                report.by_domain[domain_key] = {"fresh": 0, "expiring_soon": 0, "expired": 0, "no_expiration": 0}
            if collection not in report.by_collection:
                report.by_collection[collection] = {"fresh": 0, "expiring_soon": 0, "expired": 0, "no_expiration": 0}

            if exp_date is None:
                report.no_expiration_count += 1
                report.by_domain[domain_key]["no_expiration"] += 1
                report.by_collection[collection]["no_expiration"] += 1
                continue

            days_until = (exp_date - self._reference_date).days

            if days_until < 0:
                # Expired
                report.expired_count += 1
                report.by_domain[domain_key]["expired"] += 1
                report.by_collection[collection]["expired"] += 1
                report.alerts.append(FreshnessAlert(
                    document_id=doc.id,
                    title=doc.title,
                    domain=domain_key,
                    severity="expired",
                    expiration_date=exp_date,
                    days_until_expiry=days_until,
                    message=f"Document expired {abs(days_until)} days ago",
                    message_ar=f"انتهت صلاحية الوثيقة منذ {abs(days_until)} يوم",
                ))

            elif days_until <= self._warning_days:
                # Expiring soon
                report.expiring_soon_count += 1
                report.by_domain[domain_key]["expiring_soon"] += 1
                report.by_collection[collection]["expiring_soon"] += 1
                report.alerts.append(FreshnessAlert(
                    document_id=doc.id,
                    title=doc.title,
                    domain=domain_key,
                    severity="expiring_soon",
                    expiration_date=exp_date,
                    days_until_expiry=days_until,
                    message=f"Document expires in {days_until} days",
                    message_ar=f"تنتهي صلاحية الوثيقة خلال {days_until} يوم",
                ))

            else:
                # Fresh
                report.fresh_count += 1
                report.by_domain[domain_key]["fresh"] += 1
                report.by_collection[collection]["fresh"] += 1

        logger.info(
            "freshness_check_complete",
            total=report.total_documents,
            expired=report.expired_count,
            expiring_soon=report.expiring_soon_count,
            health_score=round(report.health_score, 3),
        )

        return report

    def check_single(self, document: BaseKnowledgeDocument) -> FreshnessAlert | None:
        """Check freshness of a single document. Returns alert if action needed."""
        exp_date = document.fresh.expiration_date
        if exp_date is None:
            return None

        days_until = (exp_date - self._reference_date).days

        if days_until < 0:
            return FreshnessAlert(
                document_id=document.id,
                title=document.title,
                domain=document.domain.value,
                severity="expired",
                expiration_date=exp_date,
                days_until_expiry=days_until,
                message=f"Document expired {abs(days_until)} days ago",
                message_ar=f"انتهت صلاحية الوثيقة منذ {abs(days_until)} يوم",
            )

        if days_until <= self._warning_days:
            return FreshnessAlert(
                document_id=document.id,
                title=document.title,
                domain=document.domain.value,
                severity="expiring_soon",
                expiration_date=exp_date,
                days_until_expiry=days_until,
                message=f"Document expires in {days_until} days",
                message_ar=f"تنتهي صلاحية الوثيقة خلال {days_until} يوم",
            )

        return None
