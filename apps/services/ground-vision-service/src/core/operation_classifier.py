"""
Operation Classifier Module - مصنف العمليات الزراعية
Based on: Qin et al. (2026) - YOLO-based operation detection

This module uses computer vision to detect and classify agricultural operations
from tower camera frames.
"""

import logging
from datetime import UTC, datetime, timezone
from typing import Optional

import numpy as np
from pydantic import BaseModel, Field

from ..models.detection import (
    EQUIPMENT_TYPE_AR,
    OPERATION_TYPE_AR,
    BoundingBox,
    DetectionConfidence,
    EquipmentType,
    FieldOperationDetection,
    OperationType,
)

logger = logging.getLogger(__name__)


class DetectionBox(BaseModel):
    """Raw detection bounding box from model"""

    x_min: int
    y_min: int
    x_max: int
    y_max: int
    class_id: int
    class_name: str
    confidence: float


class ClassificationResult(BaseModel):
    """Result from operation classification"""

    detections: list[FieldOperationDetection] = Field(default_factory=list)
    equipment_detected: list[dict] = Field(default_factory=list)
    processing_time_ms: int = 0
    model_version: str = "unknown"
    frame_id: str


class OperationClassifier:
    """
    Classify agricultural operations from camera frames using YOLO.

    Based on: Qin et al. (2026) - YOLO-based operation detection
    """

    # Mapping from YOLO class IDs to operation/equipment types
    EQUIPMENT_CLASS_MAP = {
        0: EquipmentType.COMBINE_HARVESTER,
        1: EquipmentType.TRACTOR,
        2: EquipmentType.PLOW,
        3: EquipmentType.SPRAYER,
        4: EquipmentType.SEEDER,
        5: EquipmentType.IRRIGATION_PIVOT,
        6: EquipmentType.IRRIGATION_DRIP,
        7: EquipmentType.TRUCK,
        8: EquipmentType.WORKER,
    }

    # Mapping from equipment to typical operation
    EQUIPMENT_TO_OPERATION = {
        EquipmentType.COMBINE_HARVESTER: OperationType.HARVEST,
        EquipmentType.TRACTOR: OperationType.TILLAGE,  # Default, can be multiple
        EquipmentType.PLOW: OperationType.TILLAGE,
        EquipmentType.SPRAYER: OperationType.SPRAYING,
        EquipmentType.SEEDER: OperationType.PLANTING,
        EquipmentType.IRRIGATION_PIVOT: OperationType.IRRIGATION,
        EquipmentType.IRRIGATION_DRIP: OperationType.IRRIGATION,
        EquipmentType.TRUCK: OperationType.TRANSPORT,
        EquipmentType.WORKER: OperationType.UNKNOWN,  # Could be multiple operations
    }

    def __init__(self, model_path: str | None = None, confidence_threshold: float = 0.5, device: str = "cuda"):
        """
        Initialize operation classifier.

        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Minimum confidence for detections
            device: Device to run model on ('cuda' or 'cpu')
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.model = None
        self.model_version = "yolo_agri_ops_v1"

        if model_path:
            self._load_model()

    def _load_model(self):
        """Load YOLO model from checkpoint."""
        try:
            # Using ultralytics YOLO
            from ultralytics import YOLO

            self.model = YOLO(self.model_path)
            self.model.to(self.device)
            logger.info(f"Loaded YOLO model from {self.model_path}")
        except ImportError:
            logger.warning("ultralytics not installed, using mock classifier")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None

    async def classify(
        self,
        frame: np.ndarray,
        frame_id: str,
        field_id: str,
        camera_id: str,
        tenant_id: str,
        geo_projector=None,  # Optional QuaternionGeoProjector
    ) -> ClassificationResult:
        """
        Classify agricultural operations in a frame.

        Args:
            frame: Image frame as numpy array
            frame_id: Unique frame identifier
            field_id: Field being monitored
            camera_id: Camera that captured the frame
            tenant_id: Tenant identifier
            geo_projector: Optional projector for georeferencing

        Returns:
            ClassificationResult with detected operations
        """
        import time

        start_time = time.time()

        # Run detection
        if self.model is not None:
            raw_detections = await self._run_yolo_detection(frame)
        else:
            raw_detections = self._run_mock_detection(frame)

        # Convert to FieldOperationDetection objects
        detections = []
        equipment_detected = []

        for det in raw_detections:
            if det.confidence < self.confidence_threshold:
                continue

            # Determine equipment and operation types
            equipment_type = self._get_equipment_type(det.class_id)
            operation_type = self._get_operation_type(equipment_type)

            # Create bounding box with optional geo-coordinates
            bbox = BoundingBox(
                x_min=det.x_min,
                y_min=det.y_min,
                x_max=det.x_max,
                y_max=det.y_max,
                geo_coords=self._compute_geo_coords(det, geo_projector) if geo_projector else None,
            )

            # Compute center coordinates
            center_lat, center_lon = None, None
            if geo_projector:
                center_x = (det.x_min + det.x_max) / 2
                center_y = (det.y_min + det.y_max) / 2
                center_lon, center_lat = geo_projector.pixel_to_geo(center_x, center_y)

            # Create detection record
            detection = FieldOperationDetection(
                detection_id=f"det_{frame_id}_{len(detections)}",
                field_id=field_id,
                camera_id=camera_id,
                operation_type=operation_type,
                operation_type_ar=OPERATION_TYPE_AR.get(operation_type, "غير معروف"),
                confidence=det.confidence,
                confidence_level=self._get_confidence_level(det.confidence),
                equipment_type=equipment_type,
                equipment_type_ar=EQUIPMENT_TYPE_AR.get(equipment_type, "غير معروف"),
                bounding_box=bbox,
                center_lat=center_lat,
                center_lon=center_lon,
                source_frame_id=frame_id,
                tenant_id=tenant_id,
            )

            detections.append(detection)

            equipment_detected.append(
                {
                    "type": equipment_type.value if equipment_type else "unknown",
                    "type_ar": EQUIPMENT_TYPE_AR.get(equipment_type, "غير معروف"),
                    "confidence": det.confidence,
                    "count": 1,
                }
            )

        processing_time = int((time.time() - start_time) * 1000)

        return ClassificationResult(
            detections=detections,
            equipment_detected=self._aggregate_equipment(equipment_detected),
            processing_time_ms=processing_time,
            model_version=self.model_version,
            frame_id=frame_id,
        )

    async def _run_yolo_detection(self, frame: np.ndarray) -> list[DetectionBox]:
        """Run actual YOLO detection."""
        results = self.model(frame, verbose=False)

        detections = []
        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())

                detections.append(
                    DetectionBox(
                        x_min=int(xyxy[0]),
                        y_min=int(xyxy[1]),
                        x_max=int(xyxy[2]),
                        y_max=int(xyxy[3]),
                        class_id=cls_id,
                        class_name=result.names.get(cls_id, "unknown"),
                        confidence=conf,
                    )
                )

        return detections

    def _run_mock_detection(self, frame: np.ndarray) -> list[DetectionBox]:
        """
        Run mock detection for testing without model.
        Generates synthetic detections based on image properties.
        """
        h, w = frame.shape[:2]

        # Generate random detections for testing
        # In real usage, this would never be called
        detections = []

        # Simulate detection based on image variance
        variance = np.var(frame)
        if variance > 1000:  # Only detect if image has content
            # Simulate a tractor detection
            detections.append(
                DetectionBox(
                    x_min=int(w * 0.3),
                    y_min=int(h * 0.4),
                    x_max=int(w * 0.5),
                    y_max=int(h * 0.6),
                    class_id=1,  # Tractor
                    class_name="tractor",
                    confidence=0.85,
                )
            )

        return detections

    def _get_equipment_type(self, class_id: int) -> EquipmentType | None:
        """Get equipment type from class ID."""
        return self.EQUIPMENT_CLASS_MAP.get(class_id, EquipmentType.UNKNOWN)

    def _get_operation_type(self, equipment_type: EquipmentType | None) -> OperationType:
        """Get most likely operation type for equipment."""
        if equipment_type is None:
            return OperationType.UNKNOWN
        return self.EQUIPMENT_TO_OPERATION.get(equipment_type, OperationType.UNKNOWN)

    def _get_confidence_level(self, confidence: float) -> DetectionConfidence:
        """Convert confidence score to confidence level."""
        if confidence >= 0.85:
            return DetectionConfidence.HIGH
        elif confidence >= 0.60:
            return DetectionConfidence.MEDIUM
        else:
            return DetectionConfidence.LOW

    def _compute_geo_coords(self, detection: DetectionBox, projector) -> list[dict] | None:
        """Compute geo-coordinates for bounding box corners."""
        if projector is None:
            return None

        corners = [
            (detection.x_min, detection.y_min),  # Top-left
            (detection.x_max, detection.y_min),  # Top-right
            (detection.x_max, detection.y_max),  # Bottom-right
            (detection.x_min, detection.y_max),  # Bottom-left
        ]

        geo_coords = []
        for u, v in corners:
            lon, lat = projector.pixel_to_geo(u, v)
            geo_coords.append({"lat": lat, "lon": lon})

        return geo_coords

    def _aggregate_equipment(self, equipment_list: list[dict]) -> list[dict]:
        """Aggregate equipment detections by type."""
        aggregated = {}
        for eq in equipment_list:
            eq_type = eq["type"]
            if eq_type not in aggregated:
                aggregated[eq_type] = {
                    "type": eq_type,
                    "type_ar": eq["type_ar"],
                    "count": 0,
                    "max_confidence": 0,
                }
            aggregated[eq_type]["count"] += 1
            aggregated[eq_type]["max_confidence"] = max(aggregated[eq_type]["max_confidence"], eq["confidence"])

        return list(aggregated.values())


class OperationTracker:
    """
    Track operations over time to detect start/end and duration.
    """

    def __init__(self, min_detections_for_operation: int = 3, max_gap_seconds: int = 600):
        """
        Initialize operation tracker.

        Args:
            min_detections_for_operation: Minimum consecutive detections
            max_gap_seconds: Maximum gap between detections to consider same operation
        """
        self.min_detections = min_detections_for_operation
        self.max_gap_seconds = max_gap_seconds

        # Track ongoing operations
        self.active_operations: dict[str, dict] = {}

    def update(self, detections: list[FieldOperationDetection]) -> list[dict]:
        """
        Update operation tracking with new detections.

        Args:
            detections: New detections from classification

        Returns:
            List of completed operations
        """
        completed = []
        current_time = datetime.now(UTC)

        # Group detections by operation type and field
        detection_groups: dict[str, list[FieldOperationDetection]] = {}
        for det in detections:
            key = f"{det.field_id}_{det.operation_type.value}"
            if key not in detection_groups:
                detection_groups[key] = []
            detection_groups[key].append(det)

        # Update active operations
        for key, group in detection_groups.items():
            if key not in self.active_operations:
                # Start new operation
                self.active_operations[key] = {
                    "field_id": group[0].field_id,
                    "operation_type": group[0].operation_type,
                    "started_at": current_time,
                    "last_seen_at": current_time,
                    "detection_count": len(group),
                    "detections": group,
                }
            else:
                # Update existing operation
                self.active_operations[key]["last_seen_at"] = current_time
                self.active_operations[key]["detection_count"] += len(group)
                self.active_operations[key]["detections"].extend(group)

        # Check for completed operations (gap exceeded)
        for key in list(self.active_operations.keys()):
            op = self.active_operations[key]
            gap = (current_time - op["last_seen_at"]).total_seconds()

            if gap > self.max_gap_seconds:
                # Operation completed
                if op["detection_count"] >= self.min_detections:
                    completed.append(
                        {
                            "field_id": op["field_id"],
                            "operation_type": op["operation_type"].value,
                            "started_at": op["started_at"].isoformat(),
                            "ended_at": op["last_seen_at"].isoformat(),
                            "duration_minutes": int((op["last_seen_at"] - op["started_at"]).total_seconds() / 60),
                            "detection_count": op["detection_count"],
                        }
                    )

                del self.active_operations[key]

        return completed

    def get_active_operations(self) -> list[dict]:
        """Get list of currently active operations."""
        return [
            {
                "field_id": op["field_id"],
                "operation_type": op["operation_type"].value,
                "started_at": op["started_at"].isoformat(),
                "duration_minutes": int((datetime.now(UTC) - op["started_at"]).total_seconds() / 60),
                "detection_count": op["detection_count"],
            }
            for op in self.active_operations.values()
        ]
