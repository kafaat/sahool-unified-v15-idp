"""
SAHOOL AI Explainer Service
خدمة توليد التفسيرات للتوصيات
"""

from __future__ import annotations

from typing import Any, Protocol

from .models import (
    ConfidenceBreakdown,
    EvidenceItem,
    Explanation,
)


# Protocol for knowledge types
class KnowledgeChunk(Protocol):
    """Protocol for knowledge chunk."""

    id: str
    content: str
    source: str
    knowledge_type: Any


class RetrievedContext(Protocol):
    """Protocol for retrieved context."""

    chunks: list[Any]
    scores: list[float]
    query: str


def compute_confidence_breakdown(
    retrieved: RetrievedContext,
    context_completeness: dict[str, bool],
    data_age_days: int,
) -> ConfidenceBreakdown:
    """
    حساب تفصيل درجة الثقة.

    Args:
        retrieved: السياق المسترجع من قاعدة المعرفة
        context_completeness: العوامل المتوفرة
        data_age_days: عمر البيانات بالأيام

    Returns:
        تفصيل درجة الثقة
    """
    # درجة المعرفة من الاسترجاع
    if retrieved.scores:
        knowledge_score = sum(retrieved.scores) / len(retrieved.scores)
    else:
        knowledge_score = 0.0

    # درجة السياق من الاكتمال
    available = sum(1 for v in context_completeness.values() if v)
    total = len(context_completeness)
    context_score = available / total if total > 0 else 0.0

    # درجة الحداثة (تتناقص خلال 14 يوم)
    recency_score = max(0.0, 1.0 - (data_age_days / 14.0))

    # المتوسط الموزون
    overall = knowledge_score * 0.5 + context_score * 0.3 + recency_score * 0.2

    return ConfidenceBreakdown(
        knowledge_score=round(knowledge_score, 3),
        context_score=round(context_score, 3),
        recency_score=round(recency_score, 3),
        overall=round(overall, 3),
    )


def build_explanation(
    *,
    retrieved: RetrievedContext,
    context_flags: dict[str, bool],
    data_age_days: int = 0,
    max_evidences: int = 3,
) -> Explanation:
    """
    بناء تفسير شامل لتوصية الذكاء الاصطناعي.

    Args:
        retrieved: القطع المعرفية المسترجعة
        context_flags: العوامل السياقية المستخدمة
        data_age_days: عمر بيانات الحقل
        max_evidences: الحد الأقصى للأدلة

    Returns:
        تفسير كامل
    """
    # بناء عناصر الأدلة
    evidences = []
    chunks = retrieved.chunks[:max_evidences] if retrieved.chunks else []
    scores = retrieved.scores[:max_evidences] if retrieved.scores else []

    for i, chunk in enumerate(chunks):
        score = scores[i] if i < len(scores) else 0.0
        content = getattr(chunk, "content", str(chunk))
        evidences.append(
            EvidenceItem(
                source_id=getattr(chunk, "id", f"chunk_{i}"),
                source_name=getattr(chunk, "source", "Unknown"),
                snippet=content[:200] + "..." if len(content) > 200 else content,
                relevance_score=round(score, 3),
                knowledge_type=str(getattr(chunk, "knowledge_type", "general")),
            )
        )

    # حساب الثقة
    confidence = compute_confidence_breakdown(
        retrieved=retrieved,
        context_completeness=context_flags,
        data_age_days=data_age_days,
    )

    # بناء قائمة العوامل السياقية
    context_factors = []
    factor_names = {
        "ndvi": "مؤشر NDVI للنبات",
        "weather": "بيانات الطقس الحالية",
        "soil": "معلومات التربة",
        "crop": "نوع المحصول",
        "irrigation": "سجل الري",
    }
    for key, available in context_flags.items():
        if available:
            context_factors.append(factor_names.get(key, key))

    # بناء القيود
    limitations = []
    if not context_flags.get("ndvi"):
        limitations.append("لا تتوفر بيانات NDVI حديثة")
    if not context_flags.get("weather"):
        limitations.append("لا تتوفر بيانات الطقس")
    if data_age_days > 7:
        limitations.append(f"البيانات عمرها {data_age_days} أيام")
    if len(chunks) < 2:
        limitations.append("مصادر معرفية محدودة")

    # بناء الملخصات
    summary_ar = "تمت التوصية بناءً على "
    if evidences:
        summary_ar += f"{len(evidences)} مصادر معرفية "
    if context_factors:
        summary_ar += f"و{len(context_factors)} عوامل سياقية"

    summary_en = f"Recommendation based on {len(evidences)} knowledge sources"
    if context_factors:
        summary_en += f" and {len(context_factors)} context factors"

    return Explanation(
        summary_ar=summary_ar,
        summary_en=summary_en,
        evidences=evidences,
        confidence_breakdown=confidence,
        context_factors=context_factors,
        limitations=limitations,
    )
