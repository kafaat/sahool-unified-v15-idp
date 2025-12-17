"""
SAHOOL AI Feedback Models
نماذج التغذية الراجعة لتوصيات الذكاء الاصطناعي
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from dataclasses import dataclass, field


class FeedbackType(str, Enum):
    """نوع التغذية الراجعة."""
    RATING = "rating"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"


class FeedbackSentiment(str, Enum):
    """شعور التغذية الراجعة."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass
class AIFeedback:
    """تغذية راجعة المستخدم على توصيات الذكاء الاصطناعي."""

    tenant_id: UUID
    user_id: UUID
    field_id: UUID
    trace_id: str
    query: str
    feedback_type: FeedbackType
    sentiment: FeedbackSentiment = FeedbackSentiment.NEUTRAL

    id: UUID = field(default_factory=uuid4)
    rating: int | None = None  # 1-5
    comment: str | None = None
    correct_answer: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """تحويل إلى قاموس للـ API."""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "user_id": str(self.user_id),
            "field_id": str(self.field_id),
            "trace_id": self.trace_id,
            "query": self.query,
            "feedback_type": self.feedback_type.value,
            "sentiment": self.sentiment.value,
            "rating": self.rating,
            "comment": self.comment,
            "correct_answer": self.correct_answer,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AIFeedback":
        """إنشاء من قاموس."""
        return cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            tenant_id=UUID(data["tenant_id"]),
            user_id=UUID(data["user_id"]),
            field_id=UUID(data["field_id"]),
            trace_id=data["trace_id"],
            query=data["query"],
            feedback_type=FeedbackType(data["feedback_type"]),
            sentiment=FeedbackSentiment(data.get("sentiment", "neutral")),
            rating=data.get("rating"),
            comment=data.get("comment"),
            correct_answer=data.get("correct_answer"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(timezone.utc),
        )
