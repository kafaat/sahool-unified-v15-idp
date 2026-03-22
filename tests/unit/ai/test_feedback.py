"""
Tests for Feedback Collection Module
اختبارات وحدة جمع التغذية الراجعة
"""

import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.feedback import (
    FeedbackCollector,
    FeedbackItem,
    FeedbackSentiment,
    FeedbackStorage,
    FeedbackSummary,
    FeedbackType,
    OutcomeStatus,
    RecommendationType,
    collect_outcome,
    collect_rating,
    get_feedback_collector,
    get_feedback_summary,
)


class TestFeedbackType:
    """Tests for FeedbackType enum"""

    def test_feedback_type_values(self):
        """Test FeedbackType enum values"""
        assert FeedbackType.RATING.value == "rating"
        assert FeedbackType.THUMBS.value == "thumbs"
        assert FeedbackType.CORRECTION.value == "correction"
        assert FeedbackType.COMMENT.value == "comment"
        assert FeedbackType.OUTCOME.value == "outcome"


class TestFeedbackSentiment:
    """Tests for FeedbackSentiment enum"""

    def test_sentiment_values(self):
        """Test FeedbackSentiment enum values"""
        assert FeedbackSentiment.POSITIVE.value == "positive"
        assert FeedbackSentiment.NEGATIVE.value == "negative"
        assert FeedbackSentiment.NEUTRAL.value == "neutral"
        assert FeedbackSentiment.MIXED.value == "mixed"


class TestRecommendationType:
    """Tests for RecommendationType enum"""

    def test_recommendation_type_values(self):
        """Test RecommendationType enum values"""
        assert RecommendationType.IRRIGATION.value == "irrigation"
        assert RecommendationType.FERTILIZER.value == "fertilizer"
        assert RecommendationType.PEST_CONTROL.value == "pest_control"
        assert RecommendationType.HARVEST.value == "harvest"


class TestOutcomeStatus:
    """Tests for OutcomeStatus enum"""

    def test_outcome_status_values(self):
        """Test OutcomeStatus enum values"""
        assert OutcomeStatus.SUCCESS.value == "success"
        assert OutcomeStatus.PARTIAL_SUCCESS.value == "partial_success"
        assert OutcomeStatus.FAILURE.value == "failure"
        assert OutcomeStatus.NOT_APPLICABLE.value == "not_applicable"


class TestFeedbackItem:
    """Tests for FeedbackItem"""

    def test_create_feedback_item(self):
        """Test creating a feedback item"""
        item = FeedbackItem(
            recommendation_id="rec_001",
            recommendation_type=RecommendationType.IRRIGATION,
            user_id="user_001",
            tenant_id="farm_001",
            feedback_type=FeedbackType.RATING,
            rating=4,
        )
        assert item.recommendation_id == "rec_001"
        assert item.rating == 4
        assert item.id is not None

    def test_feedback_item_with_comment(self):
        """Test feedback item with bilingual comments"""
        item = FeedbackItem(
            recommendation_id="rec_001",
            feedback_type=FeedbackType.COMMENT,
            comment="Great advice!",
            comment_ar="نصيحة رائعة!",
            tenant_id="farm_001",
        )
        assert item.comment == "Great advice!"
        assert item.comment_ar == "نصيحة رائعة!"

    def test_feedback_item_with_outcome(self):
        """Test feedback item with outcome"""
        item = FeedbackItem(
            recommendation_id="rec_001",
            feedback_type=FeedbackType.OUTCOME,
            outcome=OutcomeStatus.SUCCESS,
            yield_impact=15.0,
            cost_impact=500.0,
            tenant_id="farm_001",
        )
        assert item.outcome == OutcomeStatus.SUCCESS
        assert item.yield_impact == 15.0
        assert item.cost_impact == 500.0

    def test_feedback_item_to_dict(self):
        """Test converting feedback item to dictionary"""
        item = FeedbackItem(
            recommendation_id="rec_001",
            recommendation_type=RecommendationType.FERTILIZER,
            user_id="user_001",
            tenant_id="farm_001",
            feedback_type=FeedbackType.RATING,
            rating=5,
            sentiment=FeedbackSentiment.POSITIVE,
        )
        d = item.to_dict()
        assert d["recommendation_id"] == "rec_001"
        assert d["recommendation_type"] == "fertilizer"
        assert d["rating"] == 5
        assert d["sentiment"] == "positive"

    def test_feedback_item_from_dict(self):
        """Test creating feedback item from dictionary"""
        data = {
            "id": "test_id",
            "recommendation_id": "rec_001",
            "recommendation_type": "irrigation",
            "user_id": "user_001",
            "tenant_id": "farm_001",
            "feedback_type": "rating",
            "rating": 4,
            "sentiment": "positive",
            "sentiment_score": 0.5,
            "created_at": "2026-01-20T10:00:00",
            "updated_at": "2026-01-20T10:00:00",
        }
        item = FeedbackItem.from_dict(data)
        assert item.id == "test_id"
        assert item.rating == 4
        assert item.recommendation_type == RecommendationType.IRRIGATION


class TestFeedbackSummary:
    """Tests for FeedbackSummary"""

    def test_create_summary(self):
        """Test creating a feedback summary"""
        summary = FeedbackSummary(
            total_feedback=100,
            positive_count=70,
            negative_count=20,
            neutral_count=10,
            average_rating=4.2,
        )
        assert summary.total_feedback == 100
        assert summary.average_rating == 4.2

    def test_summary_to_dict(self):
        """Test converting summary to dictionary"""
        summary = FeedbackSummary(
            total_feedback=50,
            average_rating=3.8,
            success_rate=0.75,
        )
        d = summary.to_dict()
        assert d["total_feedback"] == 50
        assert d["average_rating"] == 3.8
        assert d["success_rate"] == 0.75


class TestFeedbackStorage:
    """Tests for FeedbackStorage"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield FeedbackStorage(storage_path=tmpdir)

    @pytest.mark.asyncio
    async def test_save_and_load(self, temp_storage):
        """Test saving and loading feedback"""
        item = FeedbackItem(
            recommendation_id="rec_001",
            tenant_id="farm_001",
            feedback_type=FeedbackType.RATING,
            rating=4,
        )
        await temp_storage.save(item)

        loaded = await temp_storage.load_all("farm_001")
        assert len(loaded) == 1
        assert loaded[0].recommendation_id == "rec_001"

    @pytest.mark.asyncio
    async def test_load_empty(self, temp_storage):
        """Test loading from empty storage"""
        loaded = await temp_storage.load_all("nonexistent")
        assert loaded == []

    @pytest.mark.asyncio
    async def test_load_by_recommendation(self, temp_storage):
        """Test loading by recommendation ID"""
        for i in range(3):
            item = FeedbackItem(
                recommendation_id=f"rec_{i % 2}",
                tenant_id="farm_001",
                feedback_type=FeedbackType.RATING,
                rating=4,
            )
            await temp_storage.save(item)

        loaded = await temp_storage.load_by_recommendation("farm_001", "rec_0")
        assert len(loaded) == 2

    @pytest.mark.asyncio
    async def test_load_by_type(self, temp_storage):
        """Test loading by recommendation type"""
        item1 = FeedbackItem(
            recommendation_id="rec_001",
            recommendation_type=RecommendationType.IRRIGATION,
            tenant_id="farm_001",
            feedback_type=FeedbackType.RATING,
            rating=4,
        )
        item2 = FeedbackItem(
            recommendation_id="rec_002",
            recommendation_type=RecommendationType.FERTILIZER,
            tenant_id="farm_001",
            feedback_type=FeedbackType.RATING,
            rating=5,
        )
        await temp_storage.save(item1)
        await temp_storage.save(item2)

        loaded = await temp_storage.load_by_type("farm_001", RecommendationType.IRRIGATION)
        assert len(loaded) == 1
        assert loaded[0].recommendation_type == RecommendationType.IRRIGATION


class TestFeedbackCollector:
    """Tests for FeedbackCollector"""

    @pytest.fixture
    def collector(self):
        """Create collector with mock storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FeedbackStorage(storage_path=tmpdir)
            yield FeedbackCollector(tenant_id="farm_001", storage=storage)

    @pytest.mark.asyncio
    async def test_collect_rating(self, collector):
        """Test collecting rating feedback"""
        item = await collector.collect_rating(
            recommendation_id="rec_001",
            rating=4,
            recommendation_type=RecommendationType.IRRIGATION,
            user_id="user_001",
        )
        assert item.rating == 4
        assert item.feedback_type == FeedbackType.RATING
        assert item.sentiment == FeedbackSentiment.POSITIVE

    @pytest.mark.asyncio
    async def test_collect_rating_negative(self, collector):
        """Test collecting negative rating"""
        item = await collector.collect_rating(
            recommendation_id="rec_001",
            rating=2,
        )
        assert item.rating == 2
        assert item.sentiment == FeedbackSentiment.NEGATIVE
        assert item.sentiment_score < 0

    @pytest.mark.asyncio
    async def test_collect_rating_neutral(self, collector):
        """Test collecting neutral rating"""
        item = await collector.collect_rating(
            recommendation_id="rec_001",
            rating=3,
        )
        assert item.rating == 3
        assert item.sentiment == FeedbackSentiment.NEUTRAL
        assert item.sentiment_score == 0.0

    @pytest.mark.asyncio
    async def test_collect_rating_invalid(self, collector):
        """Test collecting invalid rating"""
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            await collector.collect_rating(
                recommendation_id="rec_001",
                rating=6,
            )

    @pytest.mark.asyncio
    async def test_collect_thumbs_up(self, collector):
        """Test collecting thumbs up feedback"""
        item = await collector.collect_thumbs(
            recommendation_id="rec_001",
            thumbs_up=True,
        )
        assert item.thumbs_up is True
        assert item.feedback_type == FeedbackType.THUMBS
        assert item.sentiment == FeedbackSentiment.POSITIVE
        assert item.sentiment_score == 1.0

    @pytest.mark.asyncio
    async def test_collect_thumbs_down(self, collector):
        """Test collecting thumbs down feedback"""
        item = await collector.collect_thumbs(
            recommendation_id="rec_001",
            thumbs_up=False,
        )
        assert item.thumbs_up is False
        assert item.sentiment == FeedbackSentiment.NEGATIVE
        assert item.sentiment_score == -1.0

    @pytest.mark.asyncio
    async def test_collect_outcome_success(self, collector):
        """Test collecting successful outcome"""
        item = await collector.collect_outcome(
            recommendation_id="rec_001",
            outcome=OutcomeStatus.SUCCESS,
            yield_impact=20.0,
            cost_impact=1000.0,
        )
        assert item.outcome == OutcomeStatus.SUCCESS
        assert item.yield_impact == 20.0
        assert item.sentiment == FeedbackSentiment.POSITIVE

    @pytest.mark.asyncio
    async def test_collect_outcome_failure(self, collector):
        """Test collecting failed outcome"""
        item = await collector.collect_outcome(
            recommendation_id="rec_001",
            outcome=OutcomeStatus.FAILURE,
            outcome_details="Crop was damaged",
            outcome_details_ar="تضرر المحصول",
        )
        assert item.outcome == OutcomeStatus.FAILURE
        assert item.sentiment == FeedbackSentiment.NEGATIVE
        assert item.outcome_details == "Crop was damaged"

    @pytest.mark.asyncio
    async def test_collect_outcome_partial(self, collector):
        """Test collecting partial success outcome"""
        item = await collector.collect_outcome(
            recommendation_id="rec_001",
            outcome=OutcomeStatus.PARTIAL_SUCCESS,
        )
        assert item.outcome == OutcomeStatus.PARTIAL_SUCCESS
        assert item.sentiment == FeedbackSentiment.MIXED

    @pytest.mark.asyncio
    async def test_collect_correction(self, collector):
        """Test collecting correction feedback"""
        item = await collector.collect_correction(
            recommendation_id="rec_001",
            correction="The correct irrigation amount is 30mm not 25mm",
            comment="Based on my experience",
        )
        assert item.correction is not None
        assert item.feedback_type == FeedbackType.CORRECTION
        assert "needs_review" in item.tags
        assert "training_data" in item.tags

    @pytest.mark.asyncio
    async def test_get_summary(self, collector):
        """Test getting feedback summary"""
        # Add some feedback
        await collector.collect_rating("rec_001", 5)
        await collector.collect_rating("rec_002", 4)
        await collector.collect_rating("rec_003", 2)
        await collector.collect_thumbs("rec_004", True)
        await collector.collect_thumbs("rec_005", False)

        summary = await collector.get_summary()
        assert summary.total_feedback == 5
        assert summary.average_rating == pytest.approx(11 / 3)  # (5+4+2)/3
        assert summary.thumbs_up_count == 1
        assert summary.thumbs_down_count == 1

    @pytest.mark.asyncio
    async def test_get_summary_by_type(self, collector):
        """Test getting summary filtered by type"""
        await collector.collect_rating(
            "rec_001",
            5,
            recommendation_type=RecommendationType.IRRIGATION,
        )
        await collector.collect_rating(
            "rec_002",
            3,
            recommendation_type=RecommendationType.FERTILIZER,
        )

        summary = await collector.get_summary(recommendation_type=RecommendationType.IRRIGATION)
        assert summary.total_feedback == 1
        assert summary.average_rating == 5.0

    @pytest.mark.asyncio
    async def test_get_summary_outcome_stats(self, collector):
        """Test outcome statistics in summary"""
        await collector.collect_outcome("rec_001", OutcomeStatus.SUCCESS)
        await collector.collect_outcome("rec_002", OutcomeStatus.SUCCESS)
        await collector.collect_outcome("rec_003", OutcomeStatus.FAILURE)
        await collector.collect_outcome("rec_004", OutcomeStatus.NOT_APPLICABLE)

        summary = await collector.get_summary()
        # Success rate = 2 successes / 3 applicable outcomes
        assert summary.success_rate == pytest.approx(2 / 3)

    @pytest.mark.asyncio
    async def test_export_for_training(self, collector):
        """Test exporting feedback for training"""
        await collector.collect_rating("rec_001", 5)
        await collector.collect_rating("rec_002", 2)
        await collector.collect_correction(
            "rec_003",
            correction="Better answer",
            context={"original_recommendation": "Original answer"},
        )
        await collector.collect_outcome(
            "rec_004",
            OutcomeStatus.SUCCESS,
            yield_impact=10.0,
        )

        training_data = await collector.export_for_training(min_rating=4)

        # Should include: high rating (1), correction (1), successful outcome (1)
        assert len(training_data) >= 2
        types = [d["type"] for d in training_data]
        assert "positive_example" in types
        assert "correction" in types

    @pytest.mark.asyncio
    async def test_get_feedback_for_recommendation(self, collector):
        """Test getting feedback for specific recommendation"""
        await collector.collect_rating("rec_001", 5)
        await collector.collect_rating("rec_001", 4)
        await collector.collect_rating("rec_002", 3)

        feedback = await collector.get_feedback_for_recommendation("rec_001")
        assert len(feedback) == 2

    @pytest.mark.asyncio
    async def test_callback_on_feedback(self):
        """Test callback when feedback is collected"""
        callback_items = []

        def on_feedback(item):
            callback_items.append(item)

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FeedbackStorage(storage_path=tmpdir)
            collector = FeedbackCollector(
                tenant_id="farm_001",
                storage=storage,
                on_feedback=on_feedback,
            )

            await collector.collect_rating("rec_001", 5)
            await collector.collect_thumbs("rec_002", True)

        assert len(callback_items) == 2


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_get_feedback_collector(self):
        """Test getting feedback collector"""
        collector1 = get_feedback_collector("farm_001")
        collector2 = get_feedback_collector("farm_001")
        # Should return same instance for same tenant
        assert collector1 is collector2

    def test_get_feedback_collector_different_tenants(self):
        """Test getting collectors for different tenants"""
        collector1 = get_feedback_collector("farm_001")
        collector2 = get_feedback_collector("farm_002")
        assert collector1 is not collector2

    @pytest.mark.asyncio
    async def test_collect_rating_function(self):
        """Test collect_rating convenience function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Reset collectors
            from shared.ai import feedback

            feedback._collectors = {}

            # Create collector with temp storage
            storage = FeedbackStorage(storage_path=tmpdir)
            collector = FeedbackCollector("test_farm", storage=storage)
            feedback._collectors["test_farm"] = collector

            item = await collect_rating(
                tenant_id="test_farm",
                recommendation_id="rec_001",
                rating=4,
            )
            assert item.rating == 4

    @pytest.mark.asyncio
    async def test_collect_outcome_function(self):
        """Test collect_outcome convenience function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from shared.ai import feedback

            feedback._collectors = {}

            storage = FeedbackStorage(storage_path=tmpdir)
            collector = FeedbackCollector("test_farm", storage=storage)
            feedback._collectors["test_farm"] = collector

            item = await collect_outcome(
                tenant_id="test_farm",
                recommendation_id="rec_001",
                outcome=OutcomeStatus.SUCCESS,
            )
            assert item.outcome == OutcomeStatus.SUCCESS


class TestFeedbackSentimentCalculation:
    """Tests for sentiment calculation"""

    @pytest.fixture
    def collector(self):
        """Create collector"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FeedbackStorage(storage_path=tmpdir)
            yield FeedbackCollector(tenant_id="farm_001", storage=storage)

    @pytest.mark.asyncio
    async def test_rating_5_sentiment(self, collector):
        """Test sentiment for rating 5"""
        item = await collector.collect_rating("rec_001", 5)
        assert item.sentiment == FeedbackSentiment.POSITIVE
        assert item.sentiment_score == 1.0

    @pytest.mark.asyncio
    async def test_rating_4_sentiment(self, collector):
        """Test sentiment for rating 4"""
        item = await collector.collect_rating("rec_001", 4)
        assert item.sentiment == FeedbackSentiment.POSITIVE
        assert item.sentiment_score == 0.5

    @pytest.mark.asyncio
    async def test_rating_3_sentiment(self, collector):
        """Test sentiment for rating 3"""
        item = await collector.collect_rating("rec_001", 3)
        assert item.sentiment == FeedbackSentiment.NEUTRAL
        assert item.sentiment_score == 0.0

    @pytest.mark.asyncio
    async def test_rating_2_sentiment(self, collector):
        """Test sentiment for rating 2"""
        item = await collector.collect_rating("rec_001", 2)
        assert item.sentiment == FeedbackSentiment.NEGATIVE
        assert item.sentiment_score == -0.5

    @pytest.mark.asyncio
    async def test_rating_1_sentiment(self, collector):
        """Test sentiment for rating 1"""
        item = await collector.collect_rating("rec_001", 1)
        assert item.sentiment == FeedbackSentiment.NEGATIVE
        assert item.sentiment_score == -1.0


class TestFeedbackByType:
    """Tests for feedback by recommendation type"""

    @pytest.fixture
    def collector(self):
        """Create collector"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FeedbackStorage(storage_path=tmpdir)
            yield FeedbackCollector(tenant_id="farm_001", storage=storage)

    @pytest.mark.asyncio
    async def test_summary_by_recommendation_type(self, collector):
        """Test summary breakdown by recommendation type"""
        await collector.collect_rating(
            "rec_001",
            5,
            recommendation_type=RecommendationType.IRRIGATION,
        )
        await collector.collect_rating(
            "rec_002",
            4,
            recommendation_type=RecommendationType.IRRIGATION,
        )
        await collector.collect_rating(
            "rec_003",
            3,
            recommendation_type=RecommendationType.FERTILIZER,
        )

        summary = await collector.get_summary()

        assert "irrigation" in summary.by_recommendation_type
        assert "fertilizer" in summary.by_recommendation_type
        assert summary.by_recommendation_type["irrigation"]["count"] == 2
        assert summary.by_recommendation_type["fertilizer"]["count"] == 1
