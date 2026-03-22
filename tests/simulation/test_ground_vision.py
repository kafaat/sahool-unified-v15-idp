"""
Ground Vision Service Simulation Tests
اختبارات محاكاة خدمة الرؤية الأرضية

These tests simulate the ground vision pipeline without requiring
actual hardware or models.
"""

import pytest

np = pytest.importorskip("numpy", reason="numpy required for vision tests")
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# ═══════════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_frame():
    """Generate a sample image frame for testing."""
    # Create a simple 640x480 RGB image with some patterns
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Add green field area
    frame[100:400, 100:540] = [34, 139, 34]  # Forest green

    # Add brown path
    frame[200:250, :] = [139, 90, 43]  # Brown

    # Add yellow stress area (simulating crop stress)
    frame[300:350, 200:300] = [255, 255, 0]  # Yellow

    return frame


@pytest.fixture
def sample_camera_intrinsics():
    """Sample camera intrinsic parameters."""
    return {
        "fx": 1000.0,
        "fy": 1000.0,
        "cx": 320.0,
        "cy": 240.0,
        "k1": -0.1,
        "k2": 0.01,
        "k3": 0.0,
        "p1": 0.0,
        "p2": 0.0,
    }


@pytest.fixture
def sample_field_context():
    """Sample field context for timeline analysis."""
    return {
        "field_id": "field_001",
        "location_name": "Test Farm",
        "location_name_ar": "مزرعة اختبارية",
        "lat": 24.7136,
        "lon": 46.6753,
        "area_hectares": 10.5,
        "expected_crop": "wheat",
        "expected_crop_ar": "قمح",
        "expected_planting_date": "2025-11-01",
        "soil_type": "clay_loam",
        "irrigation_type": "pivot",
        "tenant_id": "sahool_test",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Geo-Projection Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestQuaternionGeoProjector:
    """Tests for Quaternion-based georeferencing."""

    def test_projector_initialization(self, sample_camera_intrinsics):
        """Test projector initialization."""
        from apps.services.ground_vision_service.src.core.geo_projection import (
            CameraIntrinsicsMatrix,
            QuaternionGeoProjector,
        )

        intrinsics = CameraIntrinsicsMatrix(**sample_camera_intrinsics)
        camera_position = np.array([0.0, 0.0, 50.0])  # 50m tower
        camera_quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # Looking down

        projector = QuaternionGeoProjector(
            camera_intrinsics=intrinsics,
            camera_position_enu=camera_position,
            camera_quaternion=camera_quaternion,
            origin_lat=24.7136,
            origin_lon=46.6753,
        )

        assert projector is not None
        assert projector.origin_lat == 24.7136
        assert projector.origin_lon == 46.6753

    def test_pixel_to_geo_conversion(self, sample_camera_intrinsics):
        """Test pixel to geographic coordinate conversion."""
        from apps.services.ground_vision_service.src.core.geo_projection import (
            CameraIntrinsicsMatrix,
            QuaternionGeoProjector,
        )

        intrinsics = CameraIntrinsicsMatrix(**sample_camera_intrinsics)
        camera_position = np.array([0.0, 0.0, 50.0])
        # Quaternion for camera looking straight down
        camera_quaternion = np.array([0.707, 0.707, 0.0, 0.0])

        projector = QuaternionGeoProjector(
            camera_intrinsics=intrinsics,
            camera_position_enu=camera_position,
            camera_quaternion=camera_quaternion,
            origin_lat=24.7136,
            origin_lon=46.6753,
        )

        # Test center pixel
        lon, lat = projector.pixel_to_geo(320, 240)

        # Should be close to origin (camera looking straight down)
        assert abs(lat - 24.7136) < 0.01
        assert abs(lon - 46.6753) < 0.01

    def test_footprint_polygon_generation(self, sample_camera_intrinsics):
        """Test ground footprint polygon generation."""
        from apps.services.ground_vision_service.src.core.geo_projection import (
            CameraIntrinsicsMatrix,
            QuaternionGeoProjector,
        )

        intrinsics = CameraIntrinsicsMatrix(**sample_camera_intrinsics)
        camera_position = np.array([0.0, 0.0, 50.0])
        camera_quaternion = np.array([0.707, 0.707, 0.0, 0.0])

        projector = QuaternionGeoProjector(
            camera_intrinsics=intrinsics,
            camera_position_enu=camera_position,
            camera_quaternion=camera_quaternion,
            origin_lat=24.7136,
            origin_lon=46.6753,
        )

        footprint = projector.generate_footprint_polygon(640, 480)

        # Should have 4 corners
        assert len(footprint) == 4

        # Each corner should be (lon, lat) tuple
        for corner in footprint:
            assert len(corner) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# Change Detection Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestChangeDetector:
    """Tests for frame change detection."""

    @pytest.mark.asyncio
    async def test_no_change_detection(self, sample_frame):
        """Test detection when frames are identical."""
        from apps.services.ground_vision_service.src.core.change_detection import (
            ChangeDetector,
            ChangeType,
        )

        detector = ChangeDetector(trigger_threshold=0.15)

        # Same frame = no change
        result = await detector.compute_change(sample_frame, sample_frame.copy())

        assert result.change_score < 0.05
        assert result.change_type == ChangeType.NO_CHANGE
        assert result.should_trigger_analysis is False

    @pytest.mark.asyncio
    async def test_significant_change_detection(self, sample_frame):
        """Test detection when significant change occurs."""
        from apps.services.ground_vision_service.src.core.change_detection import (
            ChangeDetector,
            ChangeType,
        )

        detector = ChangeDetector(trigger_threshold=0.15)

        # Create a modified frame with significant change
        modified_frame = sample_frame.copy()
        modified_frame[150:350, 150:500] = [139, 90, 43]  # Change green to brown

        result = await detector.compute_change(sample_frame, modified_frame)

        assert result.change_score > 0.15
        assert result.change_type in [
            ChangeType.SIGNIFICANT_CHANGE,
            ChangeType.MAJOR_CHANGE,
            ChangeType.MODERATE_CHANGE,
        ]
        assert result.should_trigger_analysis is True

    @pytest.mark.asyncio
    async def test_regional_change_detection(self, sample_frame):
        """Test detection of localized changes."""
        from apps.services.ground_vision_service.src.core.change_detection import (
            ChangeDetector,
        )

        detector = ChangeDetector(trigger_threshold=0.15, region_size=64)

        # Create a modified frame with localized change
        modified_frame = sample_frame.copy()
        modified_frame[200:264, 200:264] = [255, 0, 0]  # Red square

        result = await detector.compute_change(sample_frame, modified_frame)

        # Should detect change in specific region
        assert len(result.change_regions) > 0
        assert result.max_region_change > 0.1


# ═══════════════════════════════════════════════════════════════════════════════
# Operation Classifier Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestOperationClassifier:
    """Tests for agricultural operation classification."""

    @pytest.mark.asyncio
    async def test_classifier_initialization(self):
        """Test classifier initialization without model."""
        from apps.services.ground_vision_service.src.core.operation_classifier import (
            OperationClassifier,
        )

        classifier = OperationClassifier(
            model_path=None,  # No model, uses mock
            confidence_threshold=0.5,
        )

        assert classifier is not None
        assert classifier.model is None  # No YOLO model loaded

    @pytest.mark.asyncio
    async def test_mock_detection(self, sample_frame):
        """Test mock detection without actual model."""
        from apps.services.ground_vision_service.src.core.operation_classifier import (
            OperationClassifier,
        )

        classifier = OperationClassifier(model_path=None)

        result = await classifier.classify(
            frame=sample_frame,
            frame_id="frame_001",
            field_id="field_001",
            camera_id="cam_001",
            tenant_id="sahool_test",
        )

        assert result is not None
        assert result.frame_id == "frame_001"
        assert result.model_version == "yolo_agri_ops_v1"
        assert result.processing_time_ms >= 0

    @pytest.mark.asyncio
    async def test_equipment_aggregation(self):
        """Test equipment detection aggregation."""
        from apps.services.ground_vision_service.src.core.operation_classifier import (
            OperationClassifier,
        )

        classifier = OperationClassifier(model_path=None)

        # Test equipment aggregation
        equipment_list = [
            {"type": "tractor", "type_ar": "جرار", "confidence": 0.8, "count": 1},
            {"type": "tractor", "type_ar": "جرار", "confidence": 0.9, "count": 1},
            {"type": "sprayer", "type_ar": "رشاشة", "confidence": 0.7, "count": 1},
        ]

        aggregated = classifier._aggregate_equipment(equipment_list)

        assert len(aggregated) == 2  # 2 types: tractor and sprayer

        tractor = next(e for e in aggregated if e["type"] == "tractor")
        assert tractor["count"] == 2
        assert tractor["max_confidence"] == 0.9


# ═══════════════════════════════════════════════════════════════════════════════
# Anomaly Detector Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAnomalyDetector:
    """Tests for anomaly detection."""

    @pytest.mark.asyncio
    async def test_detector_initialization(self):
        """Test anomaly detector initialization."""
        from apps.services.ground_vision_service.src.intelligence.anomaly_detector import (
            AnomalyDetector,
        )

        detector = AnomalyDetector(
            enable_motion_detection=True,
            enable_stress_detection=True,
        )

        assert detector is not None
        assert detector.enable_motion is True
        assert detector.enable_stress is True

    @pytest.mark.asyncio
    async def test_stress_detection(self, sample_frame):
        """Test crop stress detection from color analysis."""
        from apps.services.ground_vision_service.src.intelligence.anomaly_detector import (
            AnomalyDetector,
        )

        detector = AnomalyDetector(enable_motion_detection=False)

        # The sample frame has a yellow stress area
        anomalies = await detector.detect(
            frame=sample_frame,
            previous_frame=None,
            frame_id="frame_001",
            field_id="field_001",
            camera_id="cam_001",
            tenant_id="sahool_test",
        )

        # Should detect the yellow stress area
        assert isinstance(anomalies, list)

    @pytest.mark.asyncio
    async def test_change_based_anomaly(self, sample_frame):
        """Test anomaly detection from sudden changes."""
        from apps.services.ground_vision_service.src.intelligence.anomaly_detector import (
            AnomalyDetector,
        )

        detector = AnomalyDetector()

        # Create a severely modified frame
        modified_frame = sample_frame.copy()
        modified_frame[:, :] = [255, 0, 0]  # All red

        anomalies = await detector.detect(
            frame=modified_frame,
            previous_frame=sample_frame,
            frame_id="frame_002",
            field_id="field_001",
            camera_id="cam_001",
            tenant_id="sahool_test",
        )

        # Should detect severe change as anomaly
        assert len(anomalies) > 0

    @pytest.mark.asyncio
    async def test_alert_generation(self, sample_frame):
        """Test alert generation from anomaly."""
        from apps.services.ground_vision_service.src.intelligence.anomaly_detector import (
            AnomalyDetector,
        )
        from apps.services.ground_vision_service.src.models.anomaly import (
            AnomalyDetection,
            AnomalyLocation,
            AnomalySeverity,
            AnomalyType,
        )

        detector = AnomalyDetector()

        # Create a mock anomaly
        anomaly = AnomalyDetection(
            anomaly_id="anomaly_001",
            field_id="field_001",
            camera_id="cam_001",
            anomaly_type=AnomalyType.WATER_STRESS,
            severity=AnomalySeverity.HIGH,
            confidence=0.85,
            description="Water stress detected in northwest section",
            description_ar="تم اكتشاف إجهاد مائي في القسم الشمالي الغربي",
            location=AnomalyLocation(lat=24.7136, lon=46.6753),
            source_frame_id="frame_001",
            tenant_id="sahool_test",
        )

        alert = detector.create_alert(anomaly)

        assert alert is not None
        assert alert.anomaly_id == "anomaly_001"
        assert alert.severity == AnomalySeverity.HIGH
        assert "sms" in alert.notification_channels  # High severity = SMS


# ═══════════════════════════════════════════════════════════════════════════════
# MLLM Reasoner Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCropTimelineReasoner:
    """Tests for MLLM crop timeline analysis."""

    def test_reasoner_initialization(self):
        """Test reasoner initialization."""
        from apps.services.ground_vision_service.src.intelligence.mllm_reasoner import (
            CropTimelineReasoner,
        )

        reasoner = CropTimelineReasoner(
            change_threshold=0.15,
            max_frames_per_analysis=5,
        )

        assert reasoner is not None
        assert reasoner.change_threshold == 0.15
        assert reasoner.max_frames == 5

    @pytest.mark.asyncio
    async def test_should_analyze_decision(self, sample_frame):
        """Test should_analyze decision logic."""
        import io

        from apps.services.ground_vision_service.src.intelligence.mllm_reasoner import (
            CropTimelineReasoner,
        )
        from apps.services.ground_vision_service.src.models.timeline import (
            TimeSeriesFrame,
        )
        from PIL import Image

        reasoner = CropTimelineReasoner(change_threshold=0.15)

        # Convert frame to bytes
        img = Image.fromarray(sample_frame)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        frame_bytes = buffer.getvalue()

        frames = [
            TimeSeriesFrame(
                frame_id="frame_001",
                camera_id="cam_001",
                captured_at=datetime.utcnow() - timedelta(hours=1),
                storage_url="s3://bucket/frame_001.jpg",
            ),
            TimeSeriesFrame(
                frame_id="frame_002",
                camera_id="cam_001",
                captured_at=datetime.utcnow(),
                storage_url="s3://bucket/frame_002.jpg",
            ),
        ]

        # Same frame twice = no significant change
        should_run = await reasoner.should_analyze(frames, [frame_bytes, frame_bytes])

        assert should_run is False


# ═══════════════════════════════════════════════════════════════════════════════
# Event Publisher Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestGroundVisionPublisher:
    """Tests for NATS event publishing."""

    @pytest.mark.asyncio
    async def test_publisher_without_connection(self):
        """Test publisher behavior without NATS connection."""
        from apps.services.ground_vision_service.src.events.publishers import (
            GroundVisionPublisher,
        )

        publisher = GroundVisionPublisher(nc=None)

        # Should not raise, just log warning
        await publisher.publish_frame_captured(
            camera_id="cam_001",
            frame_id="frame_001",
            tenant_id="sahool_test",
        )

    @pytest.mark.asyncio
    async def test_operation_detected_event(self):
        """Test operation detected event publishing."""
        from apps.services.ground_vision_service.src.events.publishers import (
            GroundVisionPublisher,
        )
        from apps.services.ground_vision_service.src.models.detection import (
            BoundingBox,
            DetectionConfidence,
            FieldOperationDetection,
            OperationType,
        )

        mock_nc = AsyncMock()
        publisher = GroundVisionPublisher(nc=mock_nc)

        detection = FieldOperationDetection(
            detection_id="det_001",
            field_id="field_001",
            camera_id="cam_001",
            operation_type=OperationType.HARVEST,
            confidence=0.92,
            confidence_level=DetectionConfidence.HIGH,
            bounding_box=BoundingBox(x_min=100, y_min=100, x_max=300, y_max=300),
            source_frame_id="frame_001",
            tenant_id="sahool_test",
        )

        await publisher.publish_operation_detected(detection)

        # Verify publish was called
        mock_nc.publish.assert_called_once()
        call_args = mock_nc.publish.call_args

        # Check subject pattern
        assert "sahool_test" in call_args[0][0]
        assert "operation_detected" in call_args[0][0]


# ═══════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestGroundVisionPipeline:
    """Integration tests for the complete pipeline."""

    @pytest.mark.asyncio
    async def test_full_frame_processing_pipeline(self, sample_frame, sample_field_context):
        """Test complete frame processing pipeline."""
        from apps.services.ground_vision_service.src.core.change_detection import (
            ChangeDetector,
        )
        from apps.services.ground_vision_service.src.core.operation_classifier import (
            OperationClassifier,
        )
        from apps.services.ground_vision_service.src.intelligence.anomaly_detector import (
            AnomalyDetector,
        )

        # Initialize components
        change_detector = ChangeDetector(trigger_threshold=0.15)
        classifier = OperationClassifier(model_path=None)
        anomaly_detector = AnomalyDetector()

        # Previous frame (for comparison)
        previous_frame = sample_frame.copy()

        # Modified current frame
        current_frame = sample_frame.copy()
        current_frame[200:300, 200:400] = [139, 90, 43]  # Add brown area

        # Step 1: Change detection
        change_result = await change_detector.compute_change(previous_frame, current_frame)

        assert change_result is not None

        # Step 2: Operation classification
        classification = await classifier.classify(
            frame=current_frame,
            frame_id="frame_001",
            field_id="field_001",
            camera_id="cam_001",
            tenant_id="sahool_test",
        )

        assert classification is not None

        # Step 3: Anomaly detection
        anomalies = await anomaly_detector.detect(
            frame=current_frame,
            previous_frame=previous_frame,
            frame_id="frame_001",
            field_id="field_001",
            camera_id="cam_001",
            tenant_id="sahool_test",
        )

        assert isinstance(anomalies, list)


# ═══════════════════════════════════════════════════════════════════════════════
# Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestModels:
    """Tests for data models."""

    def test_camera_model_creation(self):
        """Test TowerCamera model creation."""
        from apps.services.ground_vision_service.src.models.camera import (
            CameraExtrinsics,
            CameraIntrinsics,
            CameraStatus,
            TowerCamera,
        )

        intrinsics = CameraIntrinsics(
            focal_length_mm=35.0,
            sensor_width_mm=23.5,
            sensor_height_mm=15.6,
            image_width_px=4096,
            image_height_px=2160,
        )

        extrinsics = CameraExtrinsics(
            position_lat=24.7136,
            position_lon=46.6753,
            altitude_m=50.0,
            quaternion_w=1.0,
            quaternion_x=0.0,
            quaternion_y=0.0,
            quaternion_z=0.0,
        )

        camera = TowerCamera(
            camera_id="cam_001",
            tower_id="tower_001",
            name="Test Camera",
            name_ar="كاميرا اختبارية",
            intrinsics=intrinsics,
            extrinsics=extrinsics,
            status=CameraStatus.ONLINE,
            tenant_id="sahool_test",
        )

        assert camera.camera_id == "cam_001"
        assert camera.status == CameraStatus.ONLINE

    def test_detection_model_arabic_translation(self):
        """Test automatic Arabic translation in detection model."""
        from apps.services.ground_vision_service.src.models.detection import (
            BoundingBox,
            DetectionConfidence,
            FieldOperationDetection,
            OperationType,
        )

        detection = FieldOperationDetection(
            detection_id="det_001",
            field_id="field_001",
            camera_id="cam_001",
            operation_type=OperationType.HARVEST,
            confidence=0.92,
            confidence_level=DetectionConfidence.HIGH,
            bounding_box=BoundingBox(x_min=100, y_min=100, x_max=300, y_max=300),
            source_frame_id="frame_001",
            tenant_id="sahool_test",
        )

        # Arabic should be auto-filled
        assert detection.operation_type_ar == "حصاد"

    def test_anomaly_severity_response_time(self):
        """Test anomaly severity response time mapping."""
        from apps.services.ground_vision_service.src.models.anomaly import (
            AnomalyDetection,
            AnomalyLocation,
            AnomalySeverity,
            AnomalyType,
        )

        critical_anomaly = AnomalyDetection(
            anomaly_id="anomaly_001",
            field_id="field_001",
            camera_id="cam_001",
            anomaly_type=AnomalyType.FIRE_DETECTED,
            severity=AnomalySeverity.CRITICAL,
            confidence=0.95,
            description="Fire detected",
            description_ar="حريق مكتشف",
            location=AnomalyLocation(lat=24.7136, lon=46.6753),
            source_frame_id="frame_001",
            tenant_id="sahool_test",
        )

        # Critical = 6 hours response
        assert critical_anomaly.response_deadline_hours == 6
