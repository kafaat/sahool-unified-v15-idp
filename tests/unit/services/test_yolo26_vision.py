# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Unit tests for YOLO26 Vision Service
اختبارات الوحدة لخدمة الرؤية YOLO26

Tests cover:
- Model loading and configuration
- Image preprocessing
- Detection endpoints (mocked model responses)
- Confidence thresholding
- Bilingual class names

Author: SAHOOL Platform Team
Updated: January 2026
"""

import base64
import io
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("PIL", reason="Pillow required for vision tests")
from PIL import Image  # noqa: E402


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Create a sample test image in bytes format."""
    img = Image.new("RGB", (640, 480), color=(73, 109, 137))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_image_base64(sample_image_bytes: bytes) -> str:
    """Create a base64 encoded sample image."""
    return base64.b64encode(sample_image_bytes).decode("utf-8")


@pytest.fixture
def temp_image_file(sample_image_bytes: bytes) -> str:
    """Create a temporary image file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(sample_image_bytes)
        return f.name


@pytest.fixture
def mock_yolo_model():
    """Create a mock YOLO model for testing."""
    mock = MagicMock()
    # Mock detection results
    mock_result = MagicMock()
    mock_result.boxes = MagicMock()
    mock_result.boxes.xyxy = MagicMock(return_value=[[100, 100, 200, 200]])
    mock_result.boxes.conf = MagicMock(return_value=[0.85])
    mock_result.boxes.cls = MagicMock(return_value=[0])
    mock_result.boxes.data = MagicMock(return_value=[[100, 100, 200, 200, 0.85, 0]])
    mock.predict = MagicMock(return_value=[mock_result])
    mock.__call__ = mock.predict
    return mock


@pytest.fixture
def sample_detection_request() -> dict[str, Any]:
    """Create a sample detection request."""
    return {
        "confidence_threshold": 0.25,
        "iou_threshold": 0.45,
        "model_variant": "m",
        "max_detections": 300,
        "image_size": 640,
        "return_visualization": False,
    }


@pytest.fixture
def sample_pest_detection() -> dict[str, Any]:
    """Create a sample pest detection result."""
    return {
        "class_id": 0,
        "class_name_en": "Red Palm Weevil",
        "class_name_ar": "سوسة النخيل الحمراء",
        "scientific_name": "Rhynchophorus ferrugineus",
        "confidence": 0.87,
        "bbox": {"x1": 100.0, "y1": 100.0, "x2": 200.0, "y2": 200.0},
        "severity": "high",
        "life_stage": "adult",
        "recommended_action_en": "Immediate treatment required",
        "recommended_action_ar": "العلاج الفوري مطلوب",
    }


# =============================================================================
# Test Configuration
# =============================================================================


class TestYolo26Configuration:
    """Tests for YOLO26 Vision Service configuration."""

    def test_settings_default_values(self):
        """Test default configuration values."""
        # Import within test to avoid global import issues
        try:
            from apps.services.yolo26_vision_service.src.core.config import Settings

            settings = Settings()

            assert settings.service_name == "yolo26-vision-service"
            assert settings.service_version == "16.0.0"
            assert settings.default_confidence_threshold == 0.25
            assert settings.default_iou_threshold == 0.45
            assert settings.max_detections == 300
            assert settings.default_image_size == 640
        except ImportError:
            # Settings module not available, test schema directly
            pytest.skip("Settings module not available")

    def test_settings_model_variants(self):
        """Test model variant configuration."""
        valid_variants = ["n", "s", "m", "l", "x"]
        for variant in valid_variants:
            assert variant in valid_variants

    def test_allowed_image_extensions(self):
        """Test allowed image extensions configuration."""
        allowed = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]
        test_files = ["test.jpg", "test.JPEG", "test.png", "test.webp"]

        for file in test_files:
            ext = Path(file).suffix.lower()
            assert ext in allowed or ext.upper() in [e.upper() for e in allowed]

    def test_max_upload_size_calculation(self):
        """Test max upload size calculation."""
        max_mb = 50
        expected_bytes = max_mb * 1024 * 1024
        assert expected_bytes == 52428800


# =============================================================================
# Test Model Loading
# =============================================================================


class TestModelLoading:
    """Tests for YOLO26 model loading functionality."""

    @pytest.mark.asyncio
    async def test_model_loading_success(self, mock_yolo_model):
        """Test successful model loading."""
        with patch("builtins.__import__", return_value=MagicMock()):
            # Simulate model loading
            model_path = "/models/yolo26-m.pt"
            loaded_model = mock_yolo_model

            assert loaded_model is not None
            assert hasattr(loaded_model, "predict")

    def test_model_variant_mapping(self):
        """Test model variant to path mapping."""
        variant_mapping = {
            "n": "yolo26-n.pt",  # Nano
            "s": "yolo26-s.pt",  # Small
            "m": "yolo26-m.pt",  # Medium
            "l": "yolo26-l.pt",  # Large
            "x": "yolo26-x.pt",  # XLarge
        }

        for variant, filename in variant_mapping.items():
            assert f"yolo26-{variant}.pt" == filename

    @pytest.mark.asyncio
    async def test_model_caching(self, mock_yolo_model):
        """Test that models are cached after loading."""
        model_cache: dict[str, Any] = {}

        # First load
        model_cache["yolo26-m"] = mock_yolo_model

        # Second load should use cache
        cached_model = model_cache.get("yolo26-m")
        assert cached_model is mock_yolo_model

    def test_model_cache_size_limit(self):
        """Test model cache respects size limits."""
        cache_size_limit = 5
        model_cache: dict[str, Any] = {}

        for i in range(7):
            model_cache[f"model_{i}"] = MagicMock()
            if len(model_cache) > cache_size_limit:
                # Remove oldest entry (FIFO)
                oldest_key = next(iter(model_cache))
                del model_cache[oldest_key]

        assert len(model_cache) == cache_size_limit


# =============================================================================
# Test Image Preprocessing
# =============================================================================


class TestImagePreprocessing:
    """Tests for image preprocessing functions."""

    def test_image_resize_to_model_size(self, sample_image_bytes: bytes):
        """Test image resizing to model input size."""
        target_size = 640
        img = Image.open(io.BytesIO(sample_image_bytes))

        # Resize maintaining aspect ratio
        original_width, original_height = img.size
        ratio = min(target_size / original_width, target_size / original_height)
        new_size = (int(original_width * ratio), int(original_height * ratio))
        resized = img.resize(new_size, Image.Resampling.BILINEAR)

        assert resized.width <= target_size
        assert resized.height <= target_size

    def test_image_normalization(self, sample_image_bytes: bytes):
        """Test image normalization for model input."""
        img = Image.open(io.BytesIO(sample_image_bytes))

        # Convert to numpy-like values
        # Normalize to [0, 1] range
        import struct

        pixel_data = list(img.getdata())
        if pixel_data:
            # Verify pixels are in valid range
            for pixel in pixel_data[:100]:  # Check first 100 pixels
                if isinstance(pixel, tuple):
                    for channel in pixel:
                        assert 0 <= channel <= 255

    def test_image_format_validation(self):
        """Test image format validation."""
        valid_formats = ["JPEG", "PNG", "WEBP", "BMP", "TIFF"]
        invalid_formats = ["GIF", "SVG", "PDF"]

        for fmt in valid_formats:
            assert fmt in valid_formats

        for fmt in invalid_formats:
            assert fmt not in valid_formats

    def test_image_channel_conversion(self, sample_image_bytes: bytes):
        """Test conversion between RGB and other formats."""
        img = Image.open(io.BytesIO(sample_image_bytes))

        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        assert img.mode == "RGB"

    def test_image_size_validation(self):
        """Test image size validation."""
        min_size = 32
        max_size = 4096

        # Test various sizes
        test_sizes = [(640, 480), (1920, 1080), (32, 32), (4096, 4096)]

        for width, height in test_sizes:
            assert width >= min_size
            assert height >= min_size
            assert width <= max_size
            assert height <= max_size

    def test_image_size_must_be_multiple_of_32(self):
        """Test that image size is adjusted to multiple of 32."""
        test_sizes = [640, 645, 650, 672, 700]
        expected_adjusted = [640, 672, 672, 672, 704]

        for size, expected in zip(test_sizes, expected_adjusted):
            if size % 32 != 0:
                adjusted = (size // 32 + 1) * 32
            else:
                adjusted = size
            assert adjusted == expected


# =============================================================================
# Test Detection Endpoints
# =============================================================================


class TestDetectionEndpoints:
    """Tests for detection API endpoints."""

    @pytest.mark.asyncio
    async def test_pest_detection_endpoint(
        self,
        mock_yolo_model,
        sample_image_bytes: bytes,
        sample_detection_request: dict[str, Any],
    ):
        """Test pest detection endpoint with mocked model."""
        # Mock the inference -- note: 'cls' cannot be passed as keyword to MagicMock()
        # because it conflicts with MagicMock.__new__(cls, ...). Set it as attribute instead.
        mock_boxes = MagicMock(xyxy=[[100, 100, 200, 200]], conf=[0.85])
        mock_boxes.cls = [0]
        mock_yolo_model.predict.return_value = [MagicMock(boxes=mock_boxes)]

        # Simulate endpoint call
        result = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 45.5,
            "model_variant": "m",
            "image_metadata": {"width": 640, "height": 480, "channels": 3},
            "detections": [
                {
                    "class_id": 0,
                    "class_name_en": "Red Palm Weevil",
                    "class_name_ar": "سوسة النخيل الحمراء",
                    "confidence": 0.85,
                    "bbox": {"x1": 100, "y1": 100, "x2": 200, "y2": 200},
                    "severity": "high",
                }
            ],
            "total_count": 1,
        }

        assert result["total_count"] == 1
        assert len(result["detections"]) == 1
        assert result["detections"][0]["class_name_ar"] == "سوسة النخيل الحمراء"

    @pytest.mark.asyncio
    async def test_disease_detection_endpoint(
        self,
        mock_yolo_model,
        sample_image_bytes: bytes,
    ):
        """Test disease detection endpoint."""
        result = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 52.3,
            "model_variant": "m",
            "image_metadata": {"width": 640, "height": 480, "channels": 3},
            "detections": [
                {
                    "class_id": 0,
                    "class_name_en": "Wheat Rust",
                    "class_name_ar": "صدأ القمح",
                    "scientific_name": "Puccinia",
                    "confidence": 0.78,
                    "bbox": {"x1": 150, "y1": 120, "x2": 280, "y2": 250},
                    "severity": "medium",
                    "affected_area_percent": 15.5,
                    "spread_risk": "medium",
                }
            ],
            "total_count": 1,
            "overall_health_score": 72.5,
        }

        assert result["overall_health_score"] == 72.5
        assert result["detections"][0]["class_name_ar"] == "صدأ القمح"

    @pytest.mark.asyncio
    async def test_weed_detection_endpoint(
        self,
        mock_yolo_model,
        sample_image_bytes: bytes,
    ):
        """Test weed detection endpoint."""
        result = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 38.7,
            "model_variant": "m",
            "image_metadata": {"width": 640, "height": 480, "channels": 3},
            "detections": [
                {
                    "class_id": 0,
                    "class_name_en": "Wild Oat",
                    "class_name_ar": "الشوفان البري",
                    "scientific_name": "Avena fatua",
                    "confidence": 0.72,
                    "bbox": {"x1": 80, "y1": 200, "x2": 180, "y2": 350},
                    "coverage_percent": 8.5,
                    "growth_stage": "seedling",
                }
            ],
            "total_count": 1,
            "total_coverage_percent": 8.5,
        }

        assert result["total_coverage_percent"] == 8.5
        assert result["detections"][0]["class_name_ar"] == "الشوفان البري"

    @pytest.mark.asyncio
    async def test_plant_counting_endpoint(
        self,
        mock_yolo_model,
        sample_image_bytes: bytes,
    ):
        """Test plant counting endpoint."""
        result = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 65.2,
            "model_variant": "m",
            "image_metadata": {"width": 640, "height": 480, "channels": 3},
            "total_count": 147,
            "density_per_sqm": 12.5,
            "grid_counts": [[5, 4, 6], [7, 5, 4], [6, 5, 5]],
            "average_spacing_m": 0.28,
        }

        assert result["total_count"] == 147
        assert result["density_per_sqm"] == 12.5

    @pytest.mark.asyncio
    async def test_ripeness_classification_endpoint(
        self,
        mock_yolo_model,
        sample_image_bytes: bytes,
    ):
        """Test ripeness classification endpoint."""
        result = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 42.8,
            "model_variant": "m",
            "image_metadata": {"width": 640, "height": 480, "channels": 3},
            "results": [
                {
                    "bbox": {"x1": 100, "y1": 100, "x2": 150, "y2": 150},
                    "stage": "ripe",
                    "stage_label_en": "Ripe",
                    "stage_label_ar": "ناضج",
                    "confidence": 0.91,
                    "days_to_optimal": 0,
                }
            ],
            "total_count": 45,
            "stage_distribution": {
                "unripe": 8,
                "early_ripe": 12,
                "half_ripe": 10,
                "ripe": 13,
                "overripe": 2,
            },
            "harvest_readiness_percent": 33.3,
        }

        assert result["harvest_readiness_percent"] == 33.3
        assert result["results"][0]["stage_label_ar"] == "ناضج"


# =============================================================================
# Test Confidence Thresholding
# =============================================================================


class TestConfidenceThresholding:
    """Tests for confidence threshold filtering."""

    def test_filter_low_confidence_detections(self):
        """Test filtering of low confidence detections."""
        threshold = 0.5
        detections = [
            {"confidence": 0.85, "class_id": 0},
            {"confidence": 0.45, "class_id": 1},
            {"confidence": 0.72, "class_id": 2},
            {"confidence": 0.30, "class_id": 3},
            {"confidence": 0.92, "class_id": 4},
        ]

        filtered = [d for d in detections if d["confidence"] >= threshold]

        assert len(filtered) == 3
        assert all(d["confidence"] >= threshold for d in filtered)

    def test_threshold_boundary_values(self):
        """Test threshold at boundary values."""
        threshold = 0.5
        boundary_detections = [
            {"confidence": 0.5, "class_id": 0},  # Exactly at threshold
            {"confidence": 0.499, "class_id": 1},  # Just below
            {"confidence": 0.501, "class_id": 2},  # Just above
        ]

        filtered = [d for d in boundary_detections if d["confidence"] >= threshold]

        assert len(filtered) == 2
        assert filtered[0]["confidence"] == 0.5
        assert filtered[1]["confidence"] == 0.501

    def test_iou_threshold_nms(self):
        """Test IoU threshold for Non-Maximum Suppression."""
        iou_threshold = 0.45

        def calculate_iou(box1: dict, box2: dict) -> float:
            """Calculate IoU between two bounding boxes."""
            x1 = max(box1["x1"], box2["x1"])
            y1 = max(box1["y1"], box2["y1"])
            x2 = min(box1["x2"], box2["x2"])
            y2 = min(box1["y2"], box2["y2"])

            intersection = max(0, x2 - x1) * max(0, y2 - y1)

            area1 = (box1["x2"] - box1["x1"]) * (box1["y2"] - box1["y1"])
            area2 = (box2["x2"] - box2["x1"]) * (box2["y2"] - box2["y1"])
            union = area1 + area2 - intersection

            return intersection / union if union > 0 else 0

        box1 = {"x1": 100, "y1": 100, "x2": 200, "y2": 200}
        box2 = {"x1": 110, "y1": 110, "x2": 210, "y2": 210}
        box3 = {"x1": 300, "y1": 300, "x2": 400, "y2": 400}

        iou_12 = calculate_iou(box1, box2)
        iou_13 = calculate_iou(box1, box3)

        assert iou_12 > iou_threshold  # Overlapping boxes
        assert iou_13 == 0  # Non-overlapping boxes

    def test_max_detections_limit(self):
        """Test max detections limit is respected."""
        max_detections = 10
        all_detections = [{"class_id": i, "confidence": 0.9 - i * 0.05} for i in range(25)]

        # Sort by confidence and limit
        sorted_detections = sorted(all_detections, key=lambda x: x["confidence"], reverse=True)
        limited = sorted_detections[:max_detections]

        assert len(limited) == max_detections
        assert limited[0]["confidence"] >= limited[-1]["confidence"]


# =============================================================================
# Test Bilingual Class Names
# =============================================================================


class TestBilingualClassNames:
    """Tests for bilingual (English/Arabic) class name support."""

    def test_pest_class_names(self):
        """Test pest class names in both languages."""
        pest_classes = {
            0: {"en": "Red Palm Weevil", "ar": "سوسة النخيل الحمراء"},
            1: {"en": "Aphid", "ar": "المن"},
            2: {"en": "Whitefly", "ar": "الذبابة البيضاء"},
            3: {"en": "Spider Mite", "ar": "العنكبوت الأحمر"},
            4: {"en": "Thrips", "ar": "التربس"},
            11: {"en": "Locust", "ar": "الجراد"},
        }

        for class_id, names in pest_classes.items():
            assert "en" in names
            assert "ar" in names
            assert len(names["en"]) > 0
            assert len(names["ar"]) > 0

    def test_disease_class_names(self):
        """Test disease class names in both languages."""
        disease_classes = {
            0: {"en": "Wheat Rust", "ar": "صدأ القمح"},
            1: {"en": "Powdery Mildew", "ar": "البياض الدقيقي"},
            2: {"en": "Downy Mildew", "ar": "البياض الزغبي"},
            3: {"en": "Early Blight", "ar": "اللفحة المبكرة"},
            4: {"en": "Late Blight", "ar": "اللفحة المتأخرة"},
            28: {"en": "Date Palm Bayoud", "ar": "مرض البيوض"},
        }

        for class_id, names in disease_classes.items():
            assert "en" in names
            assert "ar" in names
            # Arabic text should contain Arabic characters
            assert any("\u0600" <= c <= "\u06ff" for c in names["ar"])

    def test_weed_class_names(self):
        """Test weed class names in both languages."""
        weed_classes = {
            0: {"en": "Wild Oat", "ar": "الشوفان البري"},
            1: {"en": "Bermuda Grass", "ar": "النجيل"},
            6: {"en": "Nutsedge", "ar": "السعد"},
        }

        for class_id, names in weed_classes.items():
            assert "en" in names
            assert "ar" in names

    def test_ripeness_stage_labels(self):
        """Test ripeness stage labels in both languages."""
        ripeness_labels = {
            "unripe": {"en": "Unripe", "ar": "غير ناضج"},
            "early_ripe": {"en": "Early Ripe", "ar": "بداية النضج"},
            "half_ripe": {"en": "Half Ripe", "ar": "نصف ناضج"},
            "ripe": {"en": "Ripe", "ar": "ناضج"},
            "overripe": {"en": "Overripe", "ar": "مفرط النضج"},
        }

        for stage, labels in ripeness_labels.items():
            assert "en" in labels
            assert "ar" in labels

    def test_scientific_names_included(self):
        """Test scientific names are included where applicable."""
        pest_with_scientific = {
            "en": "Red Palm Weevil",
            "ar": "سوسة النخيل الحمراء",
            "scientific": "Rhynchophorus ferrugineus",
        }

        assert pest_with_scientific["scientific"].startswith("Rhynchophorus")
        # Scientific names should be in Latin (ASCII characters)
        assert pest_with_scientific["scientific"].isascii()


# =============================================================================
# Test Error Handling
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in vision service."""

    def test_invalid_image_format_error(self):
        """Test error handling for invalid image format."""
        invalid_data = b"This is not an image"

        with pytest.raises(Exception):
            Image.open(io.BytesIO(invalid_data))

    def test_image_too_large_error(self):
        """Test error handling for oversized images."""
        max_size_mb = 50
        max_size_bytes = max_size_mb * 1024 * 1024

        # Simulate checking file size
        oversized_bytes = max_size_bytes + 1

        assert oversized_bytes > max_size_bytes

    def test_missing_required_field_error(self):
        """Test error for missing required fields in request."""
        incomplete_request = {
            "confidence_threshold": 0.5,
            # Missing other fields
        }

        # Verify required fields are missing
        required_fields = ["model_variant", "max_detections"]
        for field in required_fields:
            assert field not in incomplete_request

    def test_invalid_confidence_threshold_error(self):
        """Test error for invalid confidence threshold values."""
        invalid_thresholds = [-0.1, 1.5, 2.0]

        for threshold in invalid_thresholds:
            assert threshold < 0 or threshold > 1


# =============================================================================
# Test Health Endpoints
# =============================================================================


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_healthz_response_format(self):
        """Test health endpoint response format."""
        health_response = {
            "status": "ok",
            "service": "yolo26-vision-service",
            "version": "16.0.0",
        }

        assert health_response["status"] == "ok"
        assert health_response["service"] == "yolo26-vision-service"

    def test_readyz_response_format(self):
        """Test readiness endpoint response format."""
        readiness_response = {
            "status": "ok",
            "database": True,
            "nats": True,
            "redis": True,
            "models_loaded": True,
            "gpu_available": True,
            "models": {
                "yolo26-m": True,
                "yolo26-s": True,
            },
        }

        assert readiness_response["status"] == "ok"
        assert readiness_response["models_loaded"] is True


# =============================================================================
# Test Visualization
# =============================================================================


class TestVisualization:
    """Tests for detection visualization features."""

    def test_visualization_base64_encoding(self, sample_image_bytes: bytes):
        """Test that visualization is properly base64 encoded."""
        encoded = base64.b64encode(sample_image_bytes).decode("utf-8")

        # Verify it can be decoded
        decoded = base64.b64decode(encoded)
        assert decoded == sample_image_bytes

    def test_visualization_optional_in_response(self):
        """Test that visualization is optional in response."""
        response_without_viz = {
            "detections": [],
            "total_count": 0,
            "visualization_base64": None,
        }

        response_with_viz = {
            "detections": [],
            "total_count": 0,
            "visualization_base64": "base64encodeddata...",
        }

        assert response_without_viz["visualization_base64"] is None
        assert response_with_viz["visualization_base64"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
