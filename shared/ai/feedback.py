"""
Feedback Collection Module
==========================
وحدة جمع التغذية الراجعة

Collects and manages user feedback on AI recommendations for:
- Quality improvement tracking
- Model fine-tuning data collection
- User satisfaction analysis
- Recommendation effectiveness measurement

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable


class FeedbackType(StrEnum):
    """Types of feedback | أنواع التغذية الراجعة"""

    RATING = "rating"  # Numeric rating (1-5)
    THUMBS = "thumbs"  # Thumbs up/down
    CORRECTION = "correction"  # User provides correction
    COMMENT = "comment"  # Free-text comment
    OUTCOME = "outcome"  # Did the advice work?
    COMPARISON = "comparison"  # Compare to alternative


class FeedbackSentiment(StrEnum):
    """Feedback sentiment | المشاعر تجاه التغذية الراجعة"""

    POSITIVE = "positive"  # إيجابي
    NEGATIVE = "negative"  # سلبي
    NEUTRAL = "neutral"  # محايد
    MIXED = "mixed"  # مختلط


class RecommendationType(StrEnum):
    """Types of recommendations | أنواع التوصيات"""

    IRRIGATION = "irrigation"  # الري
    FERTILIZER = "fertilizer"  # التسميد
    PEST_CONTROL = "pest_control"  # مكافحة الآفات
    DISEASE = "disease"  # الأمراض
    HARVEST = "harvest"  # الحصاد
    PLANTING = "planting"  # الزراعة
    GENERAL = "general"  # عام


class OutcomeStatus(StrEnum):
    """
    Outcome of following recommendation | نتيجة اتباع التوصية

    Canonical definition — other modules should import from here.
    التعريف المعتمد — يجب على الوحدات الأخرى الاستيراد من هنا.
    """

    SUCCESS = "success"  # نجاح
    PARTIAL_SUCCESS = "partial_success"  # نجاح جزئي
    PARTIAL = "partial"  # Alias value used by agent feedback loops
    FAILURE = "failure"  # فشل
    NOT_APPLICABLE = "not_applicable"  # غير قابل للتطبيق
    PENDING = "pending"  # قيد الانتظار
    UNKNOWN = "unknown"  # غير معروف
    NOT_APPLIED = "not_applied"  # لم يتم التطبيق


@dataclass
class FeedbackItem:
    """
    A single feedback item
    عنصر تغذية راجعة واحد
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recommendation_id: str = ""
    recommendation_type: RecommendationType = RecommendationType.GENERAL

    # User info (anonymized)
    user_id: str = ""
    tenant_id: str = ""
    field_id: str | None = None
    crop_type: str | None = None

    # Feedback content
    feedback_type: FeedbackType = FeedbackType.RATING
    rating: int | None = None  # 1-5
    thumbs_up: bool | None = None
    comment: str | None = None
    comment_ar: str | None = None
    correction: str | None = None

    # Outcome tracking
    outcome: OutcomeStatus | None = None
    outcome_details: str | None = None
    outcome_details_ar: str | None = None
    yield_impact: float | None = None  # Percentage change in yield
    cost_impact: float | None = None  # Cost impact in local currency

    # Context at time of recommendation
    context: dict[str, Any] = field(default_factory=dict)

    # Sentiment analysis
    sentiment: FeedbackSentiment = FeedbackSentiment.NEUTRAL
    sentiment_score: float = 0.0  # -1.0 to 1.0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str = "mobile_app"  # mobile_app, web, api, sms

    # Tags for categorization
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "recommendation_id": self.recommendation_id,
            "recommendation_type": self.recommendation_type.value,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "thumbs_up": self.thumbs_up,
            "comment": self.comment,
            "comment_ar": self.comment_ar,
            "correction": self.correction,
            "outcome": self.outcome.value if self.outcome else None,
            "outcome_details": self.outcome_details,
            "outcome_details_ar": self.outcome_details_ar,
            "yield_impact": self.yield_impact,
            "cost_impact": self.cost_impact,
            "context": self.context,
            "sentiment": self.sentiment.value,
            "sentiment_score": self.sentiment_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "source": self.source,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeedbackItem:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            recommendation_id=data.get("recommendation_id", ""),
            recommendation_type=RecommendationType(data.get("recommendation_type", "general")),
            user_id=data.get("user_id", ""),
            tenant_id=data.get("tenant_id", ""),
            field_id=data.get("field_id"),
            crop_type=data.get("crop_type"),
            feedback_type=FeedbackType(data.get("feedback_type", "rating")),
            rating=data.get("rating"),
            thumbs_up=data.get("thumbs_up"),
            comment=data.get("comment"),
            comment_ar=data.get("comment_ar"),
            correction=data.get("correction"),
            outcome=OutcomeStatus(data["outcome"]) if data.get("outcome") else None,
            outcome_details=data.get("outcome_details"),
            outcome_details_ar=data.get("outcome_details_ar"),
            yield_impact=data.get("yield_impact"),
            cost_impact=data.get("cost_impact"),
            context=data.get("context", {}),
            sentiment=FeedbackSentiment(data.get("sentiment", "neutral")),
            sentiment_score=data.get("sentiment_score", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
            source=data.get("source", "mobile_app"),
            tags=data.get("tags", []),
        )


@dataclass
class FeedbackSummary:
    """
    Summary statistics for feedback
    إحصائيات ملخصة للتغذية الراجعة
    """

    # Counts
    total_feedback: int = 0
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0

    # Ratings
    average_rating: float = 0.0
    rating_distribution: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})

    # Thumbs
    thumbs_up_count: int = 0
    thumbs_down_count: int = 0

    # Outcomes
    success_rate: float = 0.0
    outcome_distribution: dict[str, int] = field(default_factory=dict)

    # Impact
    average_yield_impact: float = 0.0
    average_cost_impact: float = 0.0

    # By type
    by_recommendation_type: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Time range
    start_date: datetime | None = None
    end_date: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_feedback": self.total_feedback,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "neutral_count": self.neutral_count,
            "average_rating": self.average_rating,
            "rating_distribution": self.rating_distribution,
            "thumbs_up_count": self.thumbs_up_count,
            "thumbs_down_count": self.thumbs_down_count,
            "success_rate": self.success_rate,
            "outcome_distribution": self.outcome_distribution,
            "average_yield_impact": self.average_yield_impact,
            "average_cost_impact": self.average_cost_impact,
            "by_recommendation_type": self.by_recommendation_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }


class FeedbackStorage:
    """
    Storage backend for feedback
    التخزين الخلفي للتغذية الراجعة
    """

    def __init__(self, storage_path: str | None = None):
        """Initialize storage"""
        import tempfile

        default_path = os.path.join(tempfile.gettempdir(), "sahool_feedback")
        self.storage_path = Path(storage_path or os.getenv("FEEDBACK_STORAGE_PATH", default_path))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def save(self, feedback: FeedbackItem) -> None:
        """Save a feedback item"""
        async with self._lock:
            file_path = self.storage_path / f"{feedback.tenant_id}_feedback.jsonl"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(feedback.to_dict(), ensure_ascii=False) + "\n")

    async def load_all(self, tenant_id: str) -> list[FeedbackItem]:
        """Load all feedback for a tenant"""
        file_path = self.storage_path / f"{tenant_id}_feedback.jsonl"
        if not file_path.exists():
            return []

        items = []
        async with self._lock:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        items.append(FeedbackItem.from_dict(data))
        return items

    async def load_by_recommendation(
        self,
        tenant_id: str,
        recommendation_id: str,
    ) -> list[FeedbackItem]:
        """Load feedback for a specific recommendation"""
        all_feedback = await self.load_all(tenant_id)
        return [f for f in all_feedback if f.recommendation_id == recommendation_id]

    async def load_by_type(
        self,
        tenant_id: str,
        recommendation_type: RecommendationType,
    ) -> list[FeedbackItem]:
        """Load feedback by recommendation type"""
        all_feedback = await self.load_all(tenant_id)
        return [f for f in all_feedback if f.recommendation_type == recommendation_type]

    async def load_recent(
        self,
        tenant_id: str,
        days: int = 30,
    ) -> list[FeedbackItem]:
        """Load recent feedback"""
        from datetime import timedelta

        cutoff = datetime.now(UTC) - timedelta(days=days)
        all_feedback = await self.load_all(tenant_id)
        return [f for f in all_feedback if f.created_at >= cutoff]


class FeedbackCollector:
    """
    Collector for user feedback on AI recommendations
    جامع تغذية راجعة المستخدم على توصيات الذكاء الاصطناعي

    Features:
    - Multiple feedback types (rating, thumbs, comment, outcome)
    - Sentiment analysis
    - Outcome tracking
    - Training data export
    - Summary statistics

    Usage:
        collector = FeedbackCollector(tenant_id="farm_001")

        # Collect rating feedback
        await collector.collect_rating(
            recommendation_id="rec_001",
            rating=4,
            comment="The irrigation advice worked well"
        )

        # Collect outcome feedback
        await collector.collect_outcome(
            recommendation_id="rec_001",
            outcome=OutcomeStatus.SUCCESS,
            yield_impact=15.0  # 15% increase
        )

        # Get summary
        summary = await collector.get_summary()
    """

    def __init__(
        self,
        tenant_id: str,
        storage: FeedbackStorage | None = None,
        on_feedback: Callable[[FeedbackItem], None] | None = None,
    ):
        """
        Initialize the feedback collector

        Args:
            tenant_id: Tenant identifier
            storage: Storage backend (default: file-based)
            on_feedback: Callback when feedback is collected
        """
        self.tenant_id = tenant_id
        self.storage = storage or FeedbackStorage()
        self.on_feedback = on_feedback

        # In-memory cache for quick access
        self._cache: list[FeedbackItem] = []
        self._cache_loaded = False

    async def collect_rating(
        self,
        recommendation_id: str,
        rating: int,
        recommendation_type: RecommendationType = RecommendationType.GENERAL,
        user_id: str = "",
        comment: str | None = None,
        comment_ar: str | None = None,
        field_id: str | None = None,
        crop_type: str | None = None,
        context: dict[str, Any] | None = None,
        source: str = "mobile_app",
    ) -> FeedbackItem:
        """
        Collect rating feedback (1-5 stars)
        جمع تغذية راجعة بالتقييم (1-5 نجوم)

        Args:
            recommendation_id: ID of the recommendation
            rating: Rating from 1 to 5
            recommendation_type: Type of recommendation
            user_id: User identifier
            comment: Optional comment (English)
            comment_ar: Optional comment (Arabic)
            field_id: Field identifier
            crop_type: Crop type
            context: Additional context
            source: Feedback source

        Returns:
            FeedbackItem created
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        # Determine sentiment from rating
        if rating >= 4:
            sentiment = FeedbackSentiment.POSITIVE
            sentiment_score = (rating - 3) / 2  # 0.5 or 1.0
        elif rating <= 2:
            sentiment = FeedbackSentiment.NEGATIVE
            sentiment_score = (rating - 3) / 2  # -1.0 or -0.5
        else:
            sentiment = FeedbackSentiment.NEUTRAL
            sentiment_score = 0.0

        feedback = FeedbackItem(
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            user_id=user_id,
            tenant_id=self.tenant_id,
            field_id=field_id,
            crop_type=crop_type,
            feedback_type=FeedbackType.RATING,
            rating=rating,
            comment=comment,
            comment_ar=comment_ar,
            context=context or {},
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            source=source,
        )

        await self._save_feedback(feedback)
        return feedback

    async def collect_thumbs(
        self,
        recommendation_id: str,
        thumbs_up: bool,
        recommendation_type: RecommendationType = RecommendationType.GENERAL,
        user_id: str = "",
        comment: str | None = None,
        comment_ar: str | None = None,
        context: dict[str, Any] | None = None,
        source: str = "mobile_app",
    ) -> FeedbackItem:
        """
        Collect thumbs up/down feedback
        جمع تغذية راجعة بالإعجاب/عدم الإعجاب
        """
        feedback = FeedbackItem(
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            user_id=user_id,
            tenant_id=self.tenant_id,
            feedback_type=FeedbackType.THUMBS,
            thumbs_up=thumbs_up,
            comment=comment,
            comment_ar=comment_ar,
            context=context or {},
            sentiment=FeedbackSentiment.POSITIVE if thumbs_up else FeedbackSentiment.NEGATIVE,
            sentiment_score=1.0 if thumbs_up else -1.0,
            source=source,
        )

        await self._save_feedback(feedback)
        return feedback

    async def collect_outcome(
        self,
        recommendation_id: str,
        outcome: OutcomeStatus,
        recommendation_type: RecommendationType = RecommendationType.GENERAL,
        user_id: str = "",
        outcome_details: str | None = None,
        outcome_details_ar: str | None = None,
        yield_impact: float | None = None,
        cost_impact: float | None = None,
        context: dict[str, Any] | None = None,
        source: str = "mobile_app",
    ) -> FeedbackItem:
        """
        Collect outcome feedback (did the advice work?)
        جمع تغذية راجعة عن النتيجة (هل نجحت النصيحة؟)
        """
        # Determine sentiment from outcome
        sentiment_map = {
            OutcomeStatus.SUCCESS: (FeedbackSentiment.POSITIVE, 1.0),
            OutcomeStatus.PARTIAL_SUCCESS: (FeedbackSentiment.MIXED, 0.5),
            OutcomeStatus.FAILURE: (FeedbackSentiment.NEGATIVE, -1.0),
            OutcomeStatus.NOT_APPLICABLE: (FeedbackSentiment.NEUTRAL, 0.0),
            OutcomeStatus.PENDING: (FeedbackSentiment.NEUTRAL, 0.0),
        }
        sentiment, sentiment_score = sentiment_map.get(outcome, (FeedbackSentiment.NEUTRAL, 0.0))

        feedback = FeedbackItem(
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            user_id=user_id,
            tenant_id=self.tenant_id,
            feedback_type=FeedbackType.OUTCOME,
            outcome=outcome,
            outcome_details=outcome_details,
            outcome_details_ar=outcome_details_ar,
            yield_impact=yield_impact,
            cost_impact=cost_impact,
            context=context or {},
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            source=source,
        )

        await self._save_feedback(feedback)
        return feedback

    async def collect_correction(
        self,
        recommendation_id: str,
        correction: str,
        recommendation_type: RecommendationType = RecommendationType.GENERAL,
        user_id: str = "",
        comment: str | None = None,
        comment_ar: str | None = None,
        context: dict[str, Any] | None = None,
        source: str = "mobile_app",
    ) -> FeedbackItem:
        """
        Collect correction feedback (user provides the correct answer)
        جمع تغذية راجعة تصحيحية (المستخدم يقدم الإجابة الصحيحة)
        """
        feedback = FeedbackItem(
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            user_id=user_id,
            tenant_id=self.tenant_id,
            feedback_type=FeedbackType.CORRECTION,
            correction=correction,
            comment=comment,
            comment_ar=comment_ar,
            context=context or {},
            sentiment=FeedbackSentiment.NEGATIVE,  # Correction implies dissatisfaction
            sentiment_score=-0.5,
            source=source,
            tags=["needs_review", "training_data"],
        )

        await self._save_feedback(feedback)
        return feedback

    async def _save_feedback(self, feedback: FeedbackItem) -> None:
        """Save feedback item"""
        await self.storage.save(feedback)
        self._cache.append(feedback)

        # Trigger callback if set
        if self.on_feedback:
            self.on_feedback(feedback)

    async def get_summary(
        self,
        days: int | None = None,
        recommendation_type: RecommendationType | None = None,
    ) -> FeedbackSummary:
        """
        Get feedback summary statistics
        الحصول على إحصائيات ملخص التغذية الراجعة

        Args:
            days: Number of days to include (None = all time)
            recommendation_type: Filter by type (None = all types)

        Returns:
            FeedbackSummary with statistics
        """
        # Load feedback
        if days:
            feedback_list = await self.storage.load_recent(self.tenant_id, days)
        else:
            feedback_list = await self.storage.load_all(self.tenant_id)

        # Filter by type if specified
        if recommendation_type:
            feedback_list = [f for f in feedback_list if f.recommendation_type == recommendation_type]

        if not feedback_list:
            return FeedbackSummary()

        # Calculate statistics
        summary = FeedbackSummary(
            total_feedback=len(feedback_list),
            start_date=min(f.created_at for f in feedback_list),
            end_date=max(f.created_at for f in feedback_list),
        )

        # Sentiment counts
        for f in feedback_list:
            if f.sentiment == FeedbackSentiment.POSITIVE:
                summary.positive_count += 1
            elif f.sentiment == FeedbackSentiment.NEGATIVE:
                summary.negative_count += 1
            else:
                summary.neutral_count += 1

        # Rating statistics
        ratings = [f.rating for f in feedback_list if f.rating is not None]
        if ratings:
            summary.average_rating = sum(ratings) / len(ratings)
            for r in ratings:
                summary.rating_distribution[r] = summary.rating_distribution.get(r, 0) + 1

        # Thumbs statistics
        thumbs = [f.thumbs_up for f in feedback_list if f.thumbs_up is not None]
        summary.thumbs_up_count = sum(1 for t in thumbs if t)
        summary.thumbs_down_count = sum(1 for t in thumbs if not t)

        # Outcome statistics
        outcomes = [f.outcome for f in feedback_list if f.outcome is not None]
        if outcomes:
            for o in outcomes:
                summary.outcome_distribution[o.value] = summary.outcome_distribution.get(o.value, 0) + 1
            success_count = sum(1 for o in outcomes if o == OutcomeStatus.SUCCESS)
            applicable = sum(1 for o in outcomes if o != OutcomeStatus.NOT_APPLICABLE)
            summary.success_rate = success_count / applicable if applicable > 0 else 0.0

        # Impact statistics
        yield_impacts = [f.yield_impact for f in feedback_list if f.yield_impact is not None]
        if yield_impacts:
            summary.average_yield_impact = sum(yield_impacts) / len(yield_impacts)

        cost_impacts = [f.cost_impact for f in feedback_list if f.cost_impact is not None]
        if cost_impacts:
            summary.average_cost_impact = sum(cost_impacts) / len(cost_impacts)

        # By recommendation type
        by_type: dict[str, dict[str, Any]] = {}
        for f in feedback_list:
            type_key = f.recommendation_type.value
            if type_key not in by_type:
                by_type[type_key] = {
                    "count": 0,
                    "average_rating": 0.0,
                    "ratings": [],
                    "positive": 0,
                    "negative": 0,
                }
            by_type[type_key]["count"] += 1
            if f.rating:
                by_type[type_key]["ratings"].append(f.rating)
            if f.sentiment == FeedbackSentiment.POSITIVE:
                by_type[type_key]["positive"] += 1
            elif f.sentiment == FeedbackSentiment.NEGATIVE:
                by_type[type_key]["negative"] += 1

        # Calculate average ratings per type
        for type_key, stats in by_type.items():
            if stats["ratings"]:
                stats["average_rating"] = sum(stats["ratings"]) / len(stats["ratings"])
            del stats["ratings"]  # Remove raw ratings

        summary.by_recommendation_type = by_type

        return summary

    async def export_for_training(
        self,
        min_rating: int = 4,
        include_corrections: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Export feedback for model training
        تصدير التغذية الراجعة لتدريب النموذج

        Args:
            min_rating: Minimum rating to include (for positive examples)
            include_corrections: Include correction feedback

        Returns:
            List of training examples
        """
        feedback_list = await self.storage.load_all(self.tenant_id)
        training_data = []

        for f in feedback_list:
            # Include high-rated recommendations as positive examples
            if f.rating and f.rating >= min_rating:
                training_data.append(
                    {
                        "type": "positive_example",
                        "recommendation_id": f.recommendation_id,
                        "recommendation_type": f.recommendation_type.value,
                        "context": f.context,
                        "rating": f.rating,
                        "outcome": f.outcome.value if f.outcome else None,
                    }
                )

            # Include corrections for negative examples and improvements
            if include_corrections and f.correction:
                training_data.append(
                    {
                        "type": "correction",
                        "recommendation_id": f.recommendation_id,
                        "recommendation_type": f.recommendation_type.value,
                        "context": f.context,
                        "original_response": f.context.get("original_recommendation"),
                        "corrected_response": f.correction,
                        "comment": f.comment or f.comment_ar,
                    }
                )

            # Include successful outcomes
            if f.outcome == OutcomeStatus.SUCCESS and f.yield_impact and f.yield_impact > 0:
                training_data.append(
                    {
                        "type": "successful_outcome",
                        "recommendation_id": f.recommendation_id,
                        "recommendation_type": f.recommendation_type.value,
                        "context": f.context,
                        "yield_impact": f.yield_impact,
                        "cost_impact": f.cost_impact,
                    }
                )

        return training_data

    async def get_feedback_for_recommendation(
        self,
        recommendation_id: str,
    ) -> list[FeedbackItem]:
        """Get all feedback for a specific recommendation"""
        return await self.storage.load_by_recommendation(
            self.tenant_id,
            recommendation_id,
        )

    async def get_recent_feedback(self, days: int = 30) -> list[FeedbackItem]:
        """Get recent feedback items"""
        return await self.storage.load_recent(self.tenant_id, days)


# Convenience functions
_collectors: dict[str, FeedbackCollector] = {}


def get_feedback_collector(tenant_id: str) -> FeedbackCollector:
    """Get or create a feedback collector for a tenant"""
    if tenant_id not in _collectors:
        _collectors[tenant_id] = FeedbackCollector(tenant_id)
    return _collectors[tenant_id]


async def collect_rating(
    tenant_id: str,
    recommendation_id: str,
    rating: int,
    **kwargs,
) -> FeedbackItem:
    """Collect rating feedback using the default collector"""
    collector = get_feedback_collector(tenant_id)
    return await collector.collect_rating(recommendation_id, rating, **kwargs)


async def collect_outcome(
    tenant_id: str,
    recommendation_id: str,
    outcome: OutcomeStatus,
    **kwargs,
) -> FeedbackItem:
    """Collect outcome feedback using the default collector"""
    collector = get_feedback_collector(tenant_id)
    return await collector.collect_outcome(recommendation_id, outcome, **kwargs)


async def get_feedback_summary(
    tenant_id: str,
    days: int | None = None,
) -> FeedbackSummary:
    """Get feedback summary for a tenant"""
    collector = get_feedback_collector(tenant_id)
    return await collector.get_summary(days=days)
