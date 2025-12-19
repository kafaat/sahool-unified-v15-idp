"""
SAHOOL AI Feedback Service
خدمة التغذية الراجعة للذكاء الاصطناعي
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import Protocol, Any

from .models import AIFeedback, FeedbackSentiment, FeedbackType


class FeedbackRepository(Protocol):
    """Protocol for feedback storage."""
    def save(self, feedback: AIFeedback) -> AIFeedback: ...
    def get_by_tenant(self, tenant_id: UUID, since: datetime) -> list[AIFeedback]: ...
    def get_stats(self, tenant_id: UUID, since: datetime) -> dict[str, Any]: ...


# In-memory storage for development
_feedback_store: list[AIFeedback] = []


def submit_feedback(
    *,
    tenant_id: UUID,
    user_id: UUID,
    field_id: UUID,
    trace_id: str,
    query: str,
    feedback_type: FeedbackType,
    rating: int | None = None,
    comment: str | None = None,
    correct_answer: str | None = None,
) -> AIFeedback:
    """
    تقديم تغذية راجعة لتوصية الذكاء الاصطناعي.

    Args:
        tenant_id: معرف المستأجر
        user_id: معرف المستخدم
        field_id: معرف الحقل
        trace_id: معرف تتبع التوصية
        query: الاستعلام الأصلي
        feedback_type: نوع التغذية الراجعة
        rating: التقييم 1-5
        comment: تعليق اختياري
        correct_answer: الإجابة الصحيحة (للتصحيحات)

    Returns:
        سجل التغذية الراجعة المنشأ
    """
    # تحديد الشعور من التقييم
    sentiment = FeedbackSentiment.NEUTRAL
    if rating is not None:
        if rating >= 4:
            sentiment = FeedbackSentiment.POSITIVE
        elif rating <= 2:
            sentiment = FeedbackSentiment.NEGATIVE

    feedback = AIFeedback(
        tenant_id=tenant_id,
        user_id=user_id,
        field_id=field_id,
        trace_id=trace_id,
        query=query,
        feedback_type=feedback_type,
        rating=rating,
        sentiment=sentiment,
        comment=comment,
        correct_answer=correct_answer,
    )

    # حفظ في التخزين المؤقت
    _feedback_store.append(feedback)

    return feedback


def get_feedback_stats(
    tenant_id: UUID,
    days: int = 30,
) -> dict:
    """
    الحصول على إحصائيات التغذية الراجعة للمستأجر.

    Args:
        tenant_id: معرف المستأجر
        days: عدد الأيام للتضمين

    Returns:
        قاموس الإحصائيات
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # فلترة بحسب المستأجر والتاريخ
    filtered = [
        f for f in _feedback_store
        if f.tenant_id == tenant_id and f.created_at >= since
    ]

    total = len(filtered)

    # متوسط التقييم
    ratings = [f.rating for f in filtered if f.rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0

    # توزيع الشعور
    positive = sum(1 for f in filtered if f.sentiment == FeedbackSentiment.POSITIVE)
    negative = sum(1 for f in filtered if f.sentiment == FeedbackSentiment.NEGATIVE)

    return {
        "period_days": days,
        "total_feedback": total,
        "average_rating": round(avg_rating, 2),
        "positive_count": positive,
        "negative_count": negative,
        "satisfaction_rate": round(positive / total * 100, 1) if total > 0 else 0,
    }


def clear_feedback_store():
    """مسح التخزين المؤقت (للاختبارات)."""
    _feedback_store.clear()
