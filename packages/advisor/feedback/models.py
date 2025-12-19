"""
SAHOOL Feedback Models
Data models for AI feedback
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


class FeedbackType(str, Enum):
    """Type of feedback"""

    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"
    APPLIED = "applied"
    NOT_APPLIED = "not_applied"


class FeedbackRating(int, Enum):
    """Feedback rating scale"""

    VERY_POOR = 1
    POOR = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


@dataclass
class AdvisorFeedback:
    """Feedback on an advisor response"""

    id: str
    response_id: str
    tenant_id: str
    user_id: str
    feedback_type: FeedbackType
    rating: Optional[FeedbackRating]
    comment: Optional[str]
    outcome_notes: Optional[str]
    created_at: datetime

    @classmethod
    def create(
        cls,
        response_id: str,
        tenant_id: str,
        user_id: str,
        feedback_type: FeedbackType,
        rating: Optional[FeedbackRating] = None,
        comment: Optional[str] = None,
        outcome_notes: Optional[str] = None,
    ) -> AdvisorFeedback:
        """Factory method to create feedback"""
        return cls(
            id=str(uuid4()),
            response_id=response_id,
            tenant_id=tenant_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            outcome_notes=outcome_notes,
            created_at=datetime.now(timezone.utc),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "response_id": self.response_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating.value if self.rating else None,
            "comment": self.comment,
            "outcome_notes": self.outcome_notes,
            "created_at": self.created_at.isoformat(),
        }
