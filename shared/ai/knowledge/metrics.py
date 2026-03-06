# =============================================================================
# Knowledge Base Prometheus Metrics (GAP-13)
# مقاييس بروميثيوس لقاعدة المعرفة
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class KnowledgeMetrics:
    """Knowledge base metrics for monitoring.
    مقاييس قاعدة المعرفة للمراقبة"""

    # Counters (incrementing)
    documents_ingested: int = 0
    documents_failed: int = 0
    documents_validated: int = 0
    documents_rejected: int = 0
    documents_expired: int = 0
    queries_total: int = 0
    queries_cache_hits: int = 0

    # By domain/collection breakdown
    by_domain: dict[str, int] = field(default_factory=dict)
    by_collection: dict[str, int] = field(default_factory=dict)

    def record_ingestion(self, success: bool, domain: str = "", collection: str = "") -> None:
        """Record an ingestion event."""
        if success:
            self.documents_ingested += 1
        else:
            self.documents_failed += 1
        if domain:
            self.by_domain[domain] = self.by_domain.get(domain, 0) + 1
        if collection:
            self.by_collection[collection] = self.by_collection.get(collection, 0) + 1

    def record_validation(self, passed: bool) -> None:
        """Record a validation event."""
        self.documents_validated += 1
        if not passed:
            self.documents_rejected += 1

    def record_query(self, cache_hit: bool = False) -> None:
        """Record a query event."""
        self.queries_total += 1
        if cache_hit:
            self.queries_cache_hits += 1

    def record_expiration(self, count: int = 1) -> None:
        """Record document expiration events."""
        self.documents_expired += count

    def to_prometheus_format(self) -> str:
        """Export as Prometheus text format."""
        lines = [
            "# HELP sahool_knowledge_documents_ingested_total Total documents ingested",
            "# TYPE sahool_knowledge_documents_ingested_total counter",
            f"sahool_knowledge_documents_ingested_total {self.documents_ingested}",
            "",
            "# HELP sahool_knowledge_documents_failed_total Total ingestion failures",
            "# TYPE sahool_knowledge_documents_failed_total counter",
            f"sahool_knowledge_documents_failed_total {self.documents_failed}",
            "",
            "# HELP sahool_knowledge_documents_validated_total Total documents validated",
            "# TYPE sahool_knowledge_documents_validated_total counter",
            f"sahool_knowledge_documents_validated_total {self.documents_validated}",
            "",
            "# HELP sahool_knowledge_documents_rejected_total Total documents rejected",
            "# TYPE sahool_knowledge_documents_rejected_total counter",
            f"sahool_knowledge_documents_rejected_total {self.documents_rejected}",
            "",
            "# HELP sahool_knowledge_documents_expired_total Total expired documents",
            "# TYPE sahool_knowledge_documents_expired_total counter",
            f"sahool_knowledge_documents_expired_total {self.documents_expired}",
            "",
            "# HELP sahool_knowledge_queries_total Total knowledge queries",
            "# TYPE sahool_knowledge_queries_total counter",
            f"sahool_knowledge_queries_total {self.queries_total}",
            "",
            "# HELP sahool_knowledge_cache_hits_total Cache hits",
            "# TYPE sahool_knowledge_cache_hits_total counter",
            f"sahool_knowledge_cache_hits_total {self.queries_cache_hits}",
        ]
        # Per-domain metrics
        for domain, count in self.by_domain.items():
            lines.append(f'sahool_knowledge_by_domain{{domain="{domain}"}} {count}')
        return "\n".join(lines) + "\n"

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary."""
        return {
            "documents_ingested": self.documents_ingested,
            "documents_failed": self.documents_failed,
            "documents_validated": self.documents_validated,
            "documents_rejected": self.documents_rejected,
            "documents_expired": self.documents_expired,
            "queries_total": self.queries_total,
            "queries_cache_hits": self.queries_cache_hits,
            "cache_hit_rate": round(self.queries_cache_hits / max(1, self.queries_total), 3),
            "by_domain": dict(self.by_domain),
            "by_collection": dict(self.by_collection),
        }

    def reset(self) -> None:
        """Reset all counters."""
        self.documents_ingested = 0
        self.documents_failed = 0
        self.documents_validated = 0
        self.documents_rejected = 0
        self.documents_expired = 0
        self.queries_total = 0
        self.queries_cache_hits = 0
        self.by_domain.clear()
        self.by_collection.clear()
