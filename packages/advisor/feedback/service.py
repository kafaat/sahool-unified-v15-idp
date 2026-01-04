"""
SAHOOL Feedback Service
Service for managing AI feedback
"""

from __future__ import annotations

from .models import AdvisorFeedback, FeedbackRating, FeedbackType


class FeedbackService:
    """Service for feedback operations"""

    def __init__(self):
        # In-memory store (replace with repository)
        self._feedback: dict[str, AdvisorFeedback] = {}
        self._response_feedback: dict[str, list[str]] = (
            {}
        )  # response_id -> feedback_ids

    def submit_feedback(
        self,
        response_id: str,
        tenant_id: str,
        user_id: str,
        feedback_type: FeedbackType,
        rating: FeedbackRating | None = None,
        comment: str | None = None,
        outcome_notes: str | None = None,
    ) -> AdvisorFeedback:
        """Submit feedback for an advisor response"""
        feedback = AdvisorFeedback.create(
            response_id=response_id,
            tenant_id=tenant_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            outcome_notes=outcome_notes,
        )

        self._feedback[feedback.id] = feedback

        if response_id not in self._response_feedback:
            self._response_feedback[response_id] = []
        self._response_feedback[response_id].append(feedback.id)

        return feedback

    def get_feedback(self, feedback_id: str) -> AdvisorFeedback | None:
        """Get feedback by ID"""
        return self._feedback.get(feedback_id)

    def get_response_feedback(
        self,
        response_id: str,
    ) -> list[AdvisorFeedback]:
        """Get all feedback for a response"""
        feedback_ids = self._response_feedback.get(response_id, [])
        return [self._feedback[fid] for fid in feedback_ids if fid in self._feedback]

    def get_tenant_feedback(
        self,
        tenant_id: str,
        feedback_type: FeedbackType | None = None,
    ) -> list[AdvisorFeedback]:
        """Get all feedback for a tenant"""
        feedback_list = [f for f in self._feedback.values() if f.tenant_id == tenant_id]

        if feedback_type:
            feedback_list = [
                f for f in feedback_list if f.feedback_type == feedback_type
            ]

        return feedback_list

    def get_feedback_stats(self, tenant_id: str) -> dict:
        """Get feedback statistics for a tenant"""
        feedback_list = self.get_tenant_feedback(tenant_id)

        if not feedback_list:
            return {
                "total_feedback": 0,
                "average_rating": None,
                "helpful_rate": None,
                "applied_rate": None,
            }

        ratings = [f.rating.value for f in feedback_list if f.rating]
        helpful_count = sum(
            1 for f in feedback_list if f.feedback_type == FeedbackType.HELPFUL
        )
        applied_count = sum(
            1 for f in feedback_list if f.feedback_type == FeedbackType.APPLIED
        )

        return {
            "total_feedback": len(feedback_list),
            "average_rating": sum(ratings) / len(ratings) if ratings else None,
            "helpful_rate": (
                helpful_count / len(feedback_list) if feedback_list else None
            ),
            "applied_rate": (
                applied_count / len(feedback_list) if feedback_list else None
            ),
        }
