"""
Feedback Collector for Agent Training
جامع التغذية الراجعة لتدريب الوكلاء

Collects and stores user feedback on agent responses
for reinforcement learning and supervised fine-tuning.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

import structlog

logger = structlog.get_logger()


class FeedbackType(StrEnum):
    """Type of feedback provided."""

    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    RATING = "rating"  # 1-5 scale
    CORRECTION = "correction"  # User provides correct answer
    OUTCOME = "outcome"  # Did the advice work?


# Import canonical OutcomeStatus from shared.ai.feedback
from shared.ai.feedback import OutcomeStatus  # noqa: E402, F811


@dataclass
class AgentFeedback:
    """Feedback on an agent's response."""

    feedback_id: str = field(default_factory=lambda: str(uuid4())[:8])
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Context
    session_id: str = ""
    agent_name: str = ""
    user_input: str = ""
    agent_response: str = ""

    # Feedback
    feedback_type: FeedbackType = FeedbackType.THUMBS_UP
    rating: int | None = None  # 1-5
    is_positive: bool = True
    correction: str | None = None

    # Outcome tracking
    outcome: OutcomeStatus = OutcomeStatus.UNKNOWN
    outcome_notes: str | None = None
    outcome_recorded_at: datetime | None = None

    # Metadata
    user_id: str | None = None
    tenant_id: str | None = None
    field_id: str | None = None
    crop_type: str | None = None
    intent_type: str | None = None

    def to_training_example(self) -> dict[str, Any]:
        """Convert to training example format."""
        return {
            "input": self.user_input,
            "output": self.agent_response,
            "correction": self.correction,
            "is_positive": self.is_positive,
            "rating": self.rating,
            "outcome": self.outcome.value if self.outcome else None,
            "metadata": {
                "agent": self.agent_name,
                "intent": self.intent_type,
                "crop": self.crop_type,
            },
        }


class FeedbackCollector:
    """
    Collects and manages feedback for agent training.
    يجمع ويدير التغذية الراجعة لتدريب الوكلاء
    """

    def __init__(self, max_feedback_items: int = 10000):
        self._feedback: dict[str, AgentFeedback] = {}
        self._max_items = max_feedback_items
        self._by_agent: dict[str, list[str]] = {}  # agent_name -> feedback_ids
        self._by_session: dict[str, list[str]] = {}  # session_id -> feedback_ids

    async def record_feedback(
        self,
        session_id: str,
        agent_name: str,
        user_input: str,
        agent_response: str,
        feedback_type: FeedbackType,
        rating: int | None = None,
        correction: str | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        **metadata: Any,
    ) -> AgentFeedback:
        """
        Record feedback on an agent's response.
        تسجيل تغذية راجعة على استجابة الوكيل
        """
        is_positive = self._determine_positive(feedback_type, rating)

        feedback = AgentFeedback(
            session_id=session_id,
            agent_name=agent_name,
            user_input=user_input,
            agent_response=agent_response,
            feedback_type=feedback_type,
            rating=rating,
            is_positive=is_positive,
            correction=correction,
            user_id=user_id,
            tenant_id=tenant_id,
            **metadata,
        )

        self._store_feedback(feedback)

        logger.info(
            "Feedback recorded",
            feedback_id=feedback.feedback_id,
            agent=agent_name,
            type=feedback_type.value,
            positive=is_positive,
        )

        return feedback

    async def record_outcome(
        self,
        feedback_id: str,
        outcome: OutcomeStatus,
        notes: str | None = None,
    ) -> AgentFeedback | None:
        """
        Record the outcome after following agent advice.
        تسجيل النتيجة بعد اتباع نصيحة الوكيل
        """
        feedback = self._feedback.get(feedback_id)
        if not feedback:
            return None

        feedback.outcome = outcome
        feedback.outcome_notes = notes
        feedback.outcome_recorded_at = datetime.now(UTC)

        # Update positivity based on outcome
        if outcome == OutcomeStatus.SUCCESS:
            feedback.is_positive = True
        elif outcome == OutcomeStatus.FAILURE:
            feedback.is_positive = False

        logger.info(
            "Outcome recorded",
            feedback_id=feedback_id,
            outcome=outcome.value,
        )

        return feedback

    def _determine_positive(
        self,
        feedback_type: FeedbackType,
        rating: int | None,
    ) -> bool:
        """Determine if feedback is positive."""
        if feedback_type == FeedbackType.THUMBS_UP:
            return True
        elif feedback_type == FeedbackType.THUMBS_DOWN:
            return False
        elif feedback_type == FeedbackType.RATING and rating:
            return rating >= 4
        elif feedback_type == FeedbackType.CORRECTION:
            return False  # Corrections imply the response was wrong
        return True

    def _store_feedback(self, feedback: AgentFeedback) -> None:
        """Store feedback with index management."""
        # Evict old feedback if at capacity
        if len(self._feedback) >= self._max_items:
            oldest_id = min(
                self._feedback.keys(),
                key=lambda k: self._feedback[k].timestamp,
            )
            self._remove_feedback(oldest_id)

        # Store feedback
        self._feedback[feedback.feedback_id] = feedback

        # Index by agent
        if feedback.agent_name not in self._by_agent:
            self._by_agent[feedback.agent_name] = []
        self._by_agent[feedback.agent_name].append(feedback.feedback_id)

        # Index by session
        if feedback.session_id not in self._by_session:
            self._by_session[feedback.session_id] = []
        self._by_session[feedback.session_id].append(feedback.feedback_id)

    def _remove_feedback(self, feedback_id: str) -> None:
        """Remove feedback and clean up indices."""
        feedback = self._feedback.pop(feedback_id, None)
        if feedback:
            if feedback.agent_name in self._by_agent:
                self._by_agent[feedback.agent_name] = [
                    fid for fid in self._by_agent[feedback.agent_name] if fid != feedback_id
                ]
            if feedback.session_id in self._by_session:
                self._by_session[feedback.session_id] = [
                    fid for fid in self._by_session[feedback.session_id] if fid != feedback_id
                ]

    async def get_feedback_for_agent(
        self,
        agent_name: str,
        positive_only: bool = False,
        negative_only: bool = False,
        with_corrections: bool = False,
        with_outcomes: bool = False,
        limit: int = 100,
    ) -> list[AgentFeedback]:
        """
        Get feedback for a specific agent.
        الحصول على التغذية الراجعة لوكيل محدد
        """
        feedback_ids = self._by_agent.get(agent_name, [])
        feedbacks = [self._feedback[fid] for fid in feedback_ids if fid in self._feedback]

        # Apply filters
        if positive_only:
            feedbacks = [f for f in feedbacks if f.is_positive]
        if negative_only:
            feedbacks = [f for f in feedbacks if not f.is_positive]
        if with_corrections:
            feedbacks = [f for f in feedbacks if f.correction]
        if with_outcomes:
            feedbacks = [f for f in feedbacks if f.outcome != OutcomeStatus.UNKNOWN]

        # Sort by timestamp, newest first
        feedbacks.sort(key=lambda f: f.timestamp, reverse=True)

        return feedbacks[:limit]

    async def get_training_data(
        self,
        agent_name: str | None = None,
        min_rating: int | None = None,
        outcome_filter: OutcomeStatus | None = None,
    ) -> list[dict[str, Any]]:
        """
        Export feedback as training data.
        تصدير التغذية الراجعة كبيانات تدريب
        """
        feedbacks = list(self._feedback.values())

        # Apply filters
        if agent_name:
            feedbacks = [f for f in feedbacks if f.agent_name == agent_name]
        if min_rating:
            feedbacks = [f for f in feedbacks if f.rating and f.rating >= min_rating]
        if outcome_filter:
            feedbacks = [f for f in feedbacks if f.outcome == outcome_filter]

        return [f.to_training_example() for f in feedbacks]

    async def get_statistics(self, agent_name: str | None = None) -> dict[str, Any]:
        """
        Get feedback statistics.
        الحصول على إحصائيات التغذية الراجعة
        """
        if agent_name:
            feedbacks = await self.get_feedback_for_agent(agent_name, limit=10000)
        else:
            feedbacks = list(self._feedback.values())

        if not feedbacks:
            return {
                "total": 0,
                "positive_rate": 0,
                "average_rating": 0,
                "with_outcomes": 0,
                "success_rate": 0,
            }

        total = len(feedbacks)
        positive = sum(1 for f in feedbacks if f.is_positive)
        ratings = [f.rating for f in feedbacks if f.rating]
        with_outcomes = [f for f in feedbacks if f.outcome != OutcomeStatus.UNKNOWN]
        successes = sum(1 for f in with_outcomes if f.outcome == OutcomeStatus.SUCCESS)

        return {
            "total": total,
            "positive_count": positive,
            "negative_count": total - positive,
            "positive_rate": round(positive / total * 100, 1) if total else 0,
            "average_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "ratings_count": len(ratings),
            "corrections_count": sum(1 for f in feedbacks if f.correction),
            "with_outcomes": len(with_outcomes),
            "success_rate": round(successes / len(with_outcomes) * 100, 1) if with_outcomes else 0,
            "by_type": {ft.value: sum(1 for f in feedbacks if f.feedback_type == ft) for ft in FeedbackType},
        }
