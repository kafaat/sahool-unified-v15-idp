"""
SAHOOL AI Explainability Models
نماذج تفسير توصيات الذكاء الاصطناعي
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class EvidenceItem:
    """قطعة دليل تدعم التوصية."""

    source_id: str
    source_name: str
    snippet: str
    relevance_score: float  # 0..1
    knowledge_type: str


@dataclass(frozen=True)
class ConfidenceBreakdown:
    """تفصيل درجة الثقة."""

    knowledge_score: float  # مدى تطابق المعرفة
    context_score: float    # اكتمال سياق الحقل
    recency_score: float    # حداثة البيانات
    overall: float          # النتيجة الإجمالية


@dataclass(frozen=True)
class Explanation:
    """تفسير كامل لتوصية الذكاء الاصطناعي."""

    summary_ar: str
    summary_en: str
    evidences: list[EvidenceItem]
    confidence_breakdown: ConfidenceBreakdown
    context_factors: list[str]
    limitations: list[str]

    def to_dict(self) -> dict:
        """تحويل إلى قاموس للـ API."""
        return {
            "summary": {"ar": self.summary_ar, "en": self.summary_en},
            "evidences": [
                {
                    "source_id": e.source_id,
                    "source_name": e.source_name,
                    "snippet": e.snippet,
                    "relevance": e.relevance_score,
                    "type": e.knowledge_type,
                }
                for e in self.evidences
            ],
            "confidence": {
                "knowledge": self.confidence_breakdown.knowledge_score,
                "context": self.confidence_breakdown.context_score,
                "recency": self.confidence_breakdown.recency_score,
                "overall": self.confidence_breakdown.overall,
            },
            "factors": self.context_factors,
            "limitations": self.limitations,
        }
