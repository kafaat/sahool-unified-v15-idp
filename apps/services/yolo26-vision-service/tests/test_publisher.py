"""Tests for YOLO26 Vision Service NATS event publisher."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from src.events.publisher import (
        CRITICAL_PESTS,
        VISION_SUBJECTS,
        _confidence_to_severity,
        publish_event,
        publish_pest_detection,
        publish_disease_detection,
        publish_analysis_event,
    )
except ImportError:
    pytest.skip("yolo26-vision-service dependencies not installed", allow_module_level=True)


class TestConfidenceToSeverity:
    """Test confidence-to-severity mapping."""

    def test_critical_severity(self):
        assert _confidence_to_severity(0.90) == "critical"

    def test_high_severity(self):
        assert _confidence_to_severity(0.75) == "high"

    def test_medium_severity(self):
        assert _confidence_to_severity(0.55) == "medium"

    def test_low_severity(self):
        assert _confidence_to_severity(0.30) == "low"


class TestVisionSubjects:
    """Test NATS subject constants."""

    def test_all_subjects_defined(self):
        expected = [
            "pest_detected",
            "disease_detected",
            "weed_detected",
            "plant_count_completed",
            "critical_alert",
            "analysis_started",
            "analysis_completed",
            "analysis_failed",
        ]
        for key in expected:
            assert key in VISION_SUBJECTS
            assert VISION_SUBJECTS[key].startswith("sahool.vision.")

    def test_critical_pests_defined(self):
        assert "red_palm_weevil" in CRITICAL_PESTS
        assert "locust" in CRITICAL_PESTS


class TestPublishEvent:
    """Test the base publish_event function."""

    @pytest.mark.asyncio
    async def test_skips_when_nats_not_connected(self):
        """Should return False when NATS is not connected."""
        request = MagicMock()
        request.app.state = MagicMock(spec=[])  # No nc attribute
        result = await publish_event(request, "sahool.vision.test", {"key": "value"})
        assert result is False

    @pytest.mark.asyncio
    async def test_publishes_when_connected(self):
        """Should publish event when NATS is connected."""
        nc = AsyncMock()
        request = MagicMock()
        request.app.state.nc = nc
        request.app.state.nats_connected = True

        result = await publish_event(request, "sahool.vision.test", {"event_id": "123"})
        assert result is True
        nc.publish.assert_called_once()

        # Verify the published data
        call_args = nc.publish.call_args
        assert call_args[0][0] == "sahool.vision.test"
        published_data = json.loads(call_args[0][1].decode())
        assert published_data["event_id"] == "123"

    @pytest.mark.asyncio
    async def test_handles_publish_failure(self):
        """Should return False on publish failure."""
        nc = AsyncMock()
        nc.publish.side_effect = Exception("NATS error")
        request = MagicMock()
        request.app.state.nc = nc
        request.app.state.nats_connected = True

        result = await publish_event(request, "sahool.vision.test", {"key": "value"})
        assert result is False


class TestPublishPestDetection:
    """Test pest detection event publishing."""

    @pytest.mark.asyncio
    async def test_publishes_pest_events(self):
        """Should publish one event per detection."""
        nc = AsyncMock()
        request = MagicMock()
        request.app.state.nc = nc
        request.app.state.nats_connected = True

        detections = [
            {
                "class_name_en": "Aphid",
                "class_name_ar": "المن",
                "confidence": 0.80,
                "bbox": {"x1": 10, "y1": 20, "x2": 30, "y2": 40},
            }
        ]

        await publish_pest_detection(request, detections, model_variant="m")
        # Should publish pest_detected event (not critical, so no critical_alert)
        assert nc.publish.call_count == 1

    @pytest.mark.asyncio
    async def test_publishes_critical_alert_for_rpw(self):
        """Should publish critical alert for Red Palm Weevil."""
        nc = AsyncMock()
        request = MagicMock()
        request.app.state.nc = nc
        request.app.state.nats_connected = True

        detections = [
            {
                "class_name_en": "Red Palm Weevil",
                "class_name_ar": "سوسة النخيل الحمراء",
                "confidence": 0.92,
                "bbox": {"x1": 10, "y1": 20, "x2": 30, "y2": 40},
            }
        ]

        await publish_pest_detection(request, detections)
        # Should publish pest_detected + critical_alert
        assert nc.publish.call_count == 2

        # Verify critical alert subject
        subjects = [call[0][0] for call in nc.publish.call_args_list]
        assert VISION_SUBJECTS["pest_detected"] in subjects
        assert VISION_SUBJECTS["critical_alert"] in subjects


class TestPublishDiseaseDetection:
    """Test disease detection event publishing."""

    @pytest.mark.asyncio
    async def test_publishes_disease_events(self):
        nc = AsyncMock()
        request = MagicMock()
        request.app.state.nc = nc
        request.app.state.nats_connected = True

        detections = [
            {
                "class_name_en": "Wheat Rust",
                "class_name_ar": "صدأ القمح",
                "confidence": 0.85,
                "bbox": {"x1": 10, "y1": 20, "x2": 100, "y2": 100},
                "affected_area_percentage": 15.0,
            }
        ]

        await publish_disease_detection(request, detections)
        nc.publish.assert_called_once()

        data = json.loads(nc.publish.call_args[0][1].decode())
        assert data["detection_type"] == "disease"
        assert data["class_name_en"] == "Wheat Rust"


class TestPublishAnalysisEvent:
    """Test analysis lifecycle event publishing."""

    @pytest.mark.asyncio
    async def test_publishes_analysis_started(self):
        nc = AsyncMock()
        request = MagicMock()
        request.app.state.nc = nc
        request.app.state.nats_connected = True

        await publish_analysis_event(
            request,
            "analysis_started",
            task="plant_counting",
        )

        nc.publish.assert_called_once()
        subject = nc.publish.call_args[0][0]
        assert subject == VISION_SUBJECTS["analysis_started"]

    @pytest.mark.asyncio
    async def test_ignores_unknown_event_type(self):
        nc = AsyncMock()
        request = MagicMock()
        request.app.state.nc = nc
        request.app.state.nats_connected = True

        await publish_analysis_event(request, "unknown_event")
        nc.publish.assert_not_called()
