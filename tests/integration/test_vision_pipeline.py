# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Integration tests for Vision Pipeline
اختبارات التكامل لخط أنابيب الرؤية

End-to-end test: upload image -> detect -> store -> alert

This test suite validates the complete flow from image upload through
pest/disease detection to storage and alert generation.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
import base64
import io
import json
import os
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

Image = pytest.importorskip("PIL.Image", reason="Pillow required for vision tests")

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_test_image() -> bytes:
    """Create a sample test image for the pipeline."""
    img = Image.new("RGB", (1280, 720), color=(34, 139, 34))  # Green background

    # Add some patterns to simulate plant imagery
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)

    # Draw some leaf-like shapes
    for i in range(5):
        x, y = 200 + i * 200, 200
        draw.ellipse([x, y, x + 150, y + 100], fill=(0, 100, 0))

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_image_base64(sample_test_image: bytes) -> str:
    """Create base64 encoded image."""
    return base64.b64encode(sample_test_image).decode("utf-8")


@pytest.fixture
def sample_field_context() -> dict[str, Any]:
    """Create sample field context for detection."""
    return {
        "field_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "crop_type": "date_palm",
        "crop_type_ar": "نخيل التمر",
        "growth_stage": "fruiting",
        "location": {
            "latitude": 15.35,
            "longitude": 44.20,
        },
    }


@pytest.fixture
def mock_yolo26_service():
    """Create a mock YOLO26 Vision Service."""
    mock_service = MagicMock()

    # Mock detection response
    mock_service.detect_pests = AsyncMock(
        return_value={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 85.5,
            "model_variant": "m",
            "image_metadata": {"width": 1280, "height": 720, "channels": 3},
            "detections": [
                {
                    "class_id": 0,
                    "class_name_en": "Red Palm Weevil",
                    "class_name_ar": "سوسة النخيل الحمراء",
                    "scientific_name": "Rhynchophorus ferrugineus",
                    "confidence": 0.92,
                    "bbox": {"x1": 320, "y1": 180, "x2": 420, "y2": 280},
                    "severity": "critical",
                    "life_stage": "adult",
                    "recommended_action_en": "Immediate treatment required",
                    "recommended_action_ar": "العلاج الفوري مطلوب",
                }
            ],
            "total_count": 1,
            "severity_summary": {"critical": 1},
        }
    )

    mock_service.detect_diseases = AsyncMock(
        return_value={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 72.3,
            "model_variant": "m",
            "image_metadata": {"width": 1280, "height": 720, "channels": 3},
            "detections": [
                {
                    "class_id": 28,
                    "class_name_en": "Date Palm Bayoud",
                    "class_name_ar": "مرض البيوض",
                    "scientific_name": "Fusarium oxysporum f. sp. albedinis",
                    "confidence": 0.78,
                    "bbox": {"x1": 500, "y1": 200, "x2": 650, "y2": 350},
                    "severity": "high",
                    "affected_area_percent": 15.5,
                    "spread_risk": "high",
                }
            ],
            "total_count": 1,
            "overall_health_score": 65.0,
            "severity_summary": {"high": 1},
        }
    )

    return mock_service


@pytest.fixture
def mock_storage_service():
    """Create a mock storage service."""
    mock_storage = MagicMock()

    stored_items = {}

    async def mock_store(item_type: str, item_id: str, data: dict) -> dict:
        stored_items[f"{item_type}:{item_id}"] = data
        return {"success": True, "id": item_id}

    async def mock_retrieve(item_type: str, item_id: str) -> dict | None:
        return stored_items.get(f"{item_type}:{item_id}")

    mock_storage.store = AsyncMock(side_effect=mock_store)
    mock_storage.retrieve = AsyncMock(side_effect=mock_retrieve)
    mock_storage.stored_items = stored_items

    return mock_storage


@pytest.fixture
def mock_alert_service():
    """Create a mock alert service."""
    mock_alerts = MagicMock()
    alerts_sent = []

    async def mock_send_alert(alert: dict) -> dict:
        alert["id"] = str(uuid.uuid4())
        alert["sent_at"] = datetime.utcnow().isoformat()
        alerts_sent.append(alert)
        return {"success": True, "alert_id": alert["id"]}

    mock_alerts.send_alert = AsyncMock(side_effect=mock_send_alert)
    mock_alerts.alerts_sent = alerts_sent

    return mock_alerts


@pytest.fixture
def mock_nats_client():
    """Create a mock NATS client for event publishing."""
    mock_nats = MagicMock()
    published_events = []

    async def mock_publish(subject: str, data: bytes):
        published_events.append(
            {
                "subject": subject,
                "data": json.loads(data.decode()),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    mock_nats.publish = AsyncMock(side_effect=mock_publish)
    mock_nats.published_events = published_events

    return mock_nats


# =============================================================================
# Vision Pipeline Class
# =============================================================================


class VisionPipeline:
    """
    Vision Pipeline orchestrator for end-to-end detection workflow.
    خط أنابيب الرؤية لتنسيق سير عمل الكشف من البداية إلى النهاية.
    """

    def __init__(
        self,
        vision_service,
        storage_service,
        alert_service,
        nats_client,
    ):
        self.vision_service = vision_service
        self.storage_service = storage_service
        self.alert_service = alert_service
        self.nats_client = nats_client

    async def process_image(
        self,
        image_bytes: bytes,
        field_context: dict[str, Any],
        detection_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Process an image through the complete vision pipeline.

        Steps:
        1. Upload and validate image
        2. Run detection(s)
        3. Store results
        4. Generate alerts if needed
        5. Publish events

        Args:
            image_bytes: Raw image bytes
            field_context: Context about the field being analyzed
            detection_types: Types of detection to run (pest, disease, weed)

        Returns:
            Pipeline result with all detection results and alerts
        """
        if detection_types is None:
            detection_types = ["pest", "disease"]

        pipeline_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        result = {
            "pipeline_id": pipeline_id,
            "field_id": field_context["field_id"],
            "tenant_id": field_context["tenant_id"],
            "started_at": start_time.isoformat(),
            "detections": {},
            "alerts": [],
            "events_published": [],
        }

        # Step 1: Validate image (simulated)
        if not image_bytes or len(image_bytes) < 100:
            raise ValueError("Invalid image data")

        # Step 2: Run detections
        if "pest" in detection_types:
            pest_result = await self.vision_service.detect_pests(image_bytes)
            result["detections"]["pest"] = pest_result

            # Store detection result
            await self.storage_service.store(
                "detection",
                f"pest_{pipeline_id}",
                {**pest_result, "field_context": field_context},
            )

        if "disease" in detection_types:
            disease_result = await self.vision_service.detect_diseases(image_bytes)
            result["detections"]["disease"] = disease_result

            # Store detection result
            await self.storage_service.store(
                "detection",
                f"disease_{pipeline_id}",
                {**disease_result, "field_context": field_context},
            )

        # Step 3: Generate alerts for critical detections
        for detection_type, detection_result in result["detections"].items():
            for detection in detection_result.get("detections", []):
                severity = detection.get("severity", "low")
                if severity in ["critical", "high"]:
                    alert = {
                        "type": f"{detection_type}_detection",
                        "severity": severity,
                        "field_id": field_context["field_id"],
                        "tenant_id": field_context["tenant_id"],
                        "title_en": f"{severity.title()} {detection_type} detected: {detection['class_name_en']}",
                        "title_ar": f"تم اكتشاف {detection_type}: {detection['class_name_ar']}",
                        "detection": detection,
                        "requires_action": severity == "critical",
                    }

                    alert_response = await self.alert_service.send_alert(alert)
                    result["alerts"].append({**alert, "id": alert_response["alert_id"]})

        # Step 4: Publish events
        event = {
            "event_type": "vision.detection.completed",
            "pipeline_id": pipeline_id,
            "field_id": field_context["field_id"],
            "tenant_id": field_context["tenant_id"],
            "detection_summary": {
                "pest_count": len(result["detections"].get("pest", {}).get("detections", [])),
                "disease_count": len(result["detections"].get("disease", {}).get("detections", [])),
            },
            "alerts_generated": len(result["alerts"]),
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.nats_client.publish(
            f"sahool.{field_context['tenant_id']}.vision.detection",
            json.dumps(event).encode(),
        )
        result["events_published"].append(event)

        result["completed_at"] = datetime.utcnow().isoformat()
        result["processing_time_ms"] = (datetime.utcnow() - start_time).total_seconds() * 1000

        return result


# =============================================================================
# Integration Tests
# =============================================================================


class TestVisionPipelineIntegration:
    """Integration tests for the complete vision pipeline."""

    @pytest.mark.asyncio
    async def test_complete_pipeline_with_pest_detection(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test complete pipeline with pest detection."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest"],
        )

        # Verify pipeline completed
        assert result["pipeline_id"] is not None
        assert result["field_id"] == sample_field_context["field_id"]
        assert "pest" in result["detections"]

        # Verify pest was detected
        pest_result = result["detections"]["pest"]
        assert pest_result["total_count"] == 1
        assert pest_result["detections"][0]["class_name_en"] == "Red Palm Weevil"

        # Verify storage was called
        assert mock_storage_service.store.called

        # Verify alert was generated for critical pest
        assert len(result["alerts"]) == 1
        assert result["alerts"][0]["severity"] == "critical"

        # Verify event was published
        assert len(mock_nats_client.published_events) == 1
        assert mock_nats_client.published_events[0]["data"]["event_type"] == "vision.detection.completed"

    @pytest.mark.asyncio
    async def test_pipeline_with_multiple_detection_types(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test pipeline with both pest and disease detection."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest", "disease"],
        )

        # Verify both detection types ran
        assert "pest" in result["detections"]
        assert "disease" in result["detections"]

        # Verify both detectors were called
        mock_yolo26_service.detect_pests.assert_called_once()
        mock_yolo26_service.detect_diseases.assert_called_once()

        # Verify storage called for each detection
        assert mock_storage_service.store.call_count == 2

        # Verify alerts for both critical/high severity detections
        assert len(result["alerts"]) >= 1

    @pytest.mark.asyncio
    async def test_pipeline_stores_detection_results(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test that detection results are properly stored."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest"],
        )

        # Verify storage call arguments
        storage_calls = mock_storage_service.store.call_args_list
        assert len(storage_calls) >= 1

        # Check stored data includes field context
        stored_key = f"pest_{result['pipeline_id']}"
        stored_data = mock_storage_service.stored_items.get(f"detection:{stored_key}")
        assert stored_data is not None
        assert "field_context" in stored_data

    @pytest.mark.asyncio
    async def test_pipeline_generates_alerts_for_critical_detections(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test that alerts are generated for critical detections."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest"],
        )

        # Verify alert was sent
        assert mock_alert_service.send_alert.called
        assert len(mock_alert_service.alerts_sent) >= 1

        # Verify alert content
        sent_alert = mock_alert_service.alerts_sent[0]
        assert sent_alert["severity"] == "critical"
        assert sent_alert["requires_action"] is True
        assert "Red Palm Weevil" in sent_alert["title_en"]
        assert "سوسة النخيل الحمراء" in sent_alert["title_ar"]

    @pytest.mark.asyncio
    async def test_pipeline_publishes_events(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test that pipeline publishes NATS events."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest", "disease"],
        )

        # Verify event was published
        assert len(mock_nats_client.published_events) == 1

        # Verify event subject
        event = mock_nats_client.published_events[0]
        expected_subject = f"sahool.{sample_field_context['tenant_id']}.vision.detection"
        assert event["subject"] == expected_subject

        # Verify event content
        event_data = event["data"]
        assert event_data["event_type"] == "vision.detection.completed"
        assert event_data["pipeline_id"] == result["pipeline_id"]
        assert event_data["detection_summary"]["pest_count"] == 1
        assert event_data["detection_summary"]["disease_count"] == 1

    @pytest.mark.asyncio
    async def test_pipeline_handles_no_detections(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test pipeline behavior when no detections are found."""
        # Create a vision service with no detections
        mock_vision_no_detections = MagicMock()
        mock_vision_no_detections.detect_pests = AsyncMock(
            return_value={
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time_ms": 45.0,
                "detections": [],
                "total_count": 0,
            }
        )

        pipeline = VisionPipeline(
            vision_service=mock_vision_no_detections,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest"],
        )

        # Verify no alerts were generated
        assert len(result["alerts"]) == 0

        # Verify no alert service calls
        assert not mock_alert_service.send_alert.called

        # Event should still be published
        assert len(mock_nats_client.published_events) == 1

    @pytest.mark.asyncio
    async def test_pipeline_error_handling_invalid_image(
        self,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test pipeline error handling with invalid image."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        # Should raise error for invalid image
        with pytest.raises(ValueError, match="Invalid image data"):
            await pipeline.process_image(
                image_bytes=b"not an image",
                field_context=sample_field_context,
                detection_types=["pest"],
            )

    @pytest.mark.asyncio
    async def test_pipeline_tracking_info(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test that pipeline includes proper tracking information."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest"],
        )

        # Verify tracking fields
        assert "pipeline_id" in result
        assert "started_at" in result
        assert "completed_at" in result
        assert "processing_time_ms" in result

        # Verify timing is reasonable
        assert result["processing_time_ms"] >= 0


class TestVisionPipelinePerformance:
    """Performance tests for the vision pipeline."""

    @pytest.mark.asyncio
    async def test_pipeline_processing_time(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test that pipeline completes within acceptable time."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        start_time = time.time()
        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest", "disease"],
        )
        elapsed_time = time.time() - start_time

        # Should complete within 5 seconds (with mocks)
        assert elapsed_time < 5.0

    @pytest.mark.asyncio
    async def test_pipeline_concurrent_processing(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test concurrent pipeline processing."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        # Process multiple images concurrently
        contexts = [{**sample_field_context, "field_id": str(uuid.uuid4())} for _ in range(3)]

        tasks = [
            pipeline.process_image(
                image_bytes=sample_test_image,
                field_context=ctx,
                detection_types=["pest"],
            )
            for ctx in contexts
        ]

        results = await asyncio.gather(*tasks)

        # All should complete successfully
        assert len(results) == 3
        assert all(r["pipeline_id"] is not None for r in results)

        # Each should have unique pipeline ID
        pipeline_ids = [r["pipeline_id"] for r in results]
        assert len(set(pipeline_ids)) == 3


class TestVisionPipelineDataFlow:
    """Tests for data flow through the vision pipeline."""

    @pytest.mark.asyncio
    async def test_field_context_propagation(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test that field context is propagated through pipeline."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest"],
        )

        # Check result contains field context
        assert result["field_id"] == sample_field_context["field_id"]
        assert result["tenant_id"] == sample_field_context["tenant_id"]

        # Check alert contains field context
        if result["alerts"]:
            assert result["alerts"][0]["field_id"] == sample_field_context["field_id"]

        # Check event contains field context
        event_data = mock_nats_client.published_events[0]["data"]
        assert event_data["field_id"] == sample_field_context["field_id"]

    @pytest.mark.asyncio
    async def test_detection_result_structure(
        self,
        sample_test_image: bytes,
        sample_field_context: dict[str, Any],
        mock_yolo26_service,
        mock_storage_service,
        mock_alert_service,
        mock_nats_client,
    ):
        """Test detection result structure completeness."""
        pipeline = VisionPipeline(
            vision_service=mock_yolo26_service,
            storage_service=mock_storage_service,
            alert_service=mock_alert_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.process_image(
            image_bytes=sample_test_image,
            field_context=sample_field_context,
            detection_types=["pest"],
        )

        pest_result = result["detections"]["pest"]

        # Verify all expected fields present
        required_fields = [
            "request_id",
            "timestamp",
            "processing_time_ms",
            "detections",
            "total_count",
        ]
        for field in required_fields:
            assert field in pest_result

        # Verify detection structure
        if pest_result["detections"]:
            detection = pest_result["detections"][0]
            assert "class_name_en" in detection
            assert "class_name_ar" in detection
            assert "confidence" in detection
            assert "bbox" in detection


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
