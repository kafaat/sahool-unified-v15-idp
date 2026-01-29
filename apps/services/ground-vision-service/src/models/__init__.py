# Ground Vision Service Models
# نماذج بيانات خدمة الرؤية الأرضية

from .camera import (
    TowerCamera,
    CameraIntrinsics,
    CameraExtrinsics,
    CameraStatus,
    CameraCreateRequest,
    CameraUpdateRequest,
)
from .detection import (
    FieldOperationDetection,
    OperationType,
    DetectionConfidence,
)
from .timeline import (
    CropTimelineEntry,
    GrowthStage,
    CropTimelineAnalysis,
    TimeSeriesFrame,
)
from .anomaly import (
    AnomalyDetection,
    AnomalyType,
    AnomalySeverity,
)

__all__ = [
    # Camera
    "TowerCamera",
    "CameraIntrinsics",
    "CameraExtrinsics",
    "CameraStatus",
    "CameraCreateRequest",
    "CameraUpdateRequest",
    # Detection
    "FieldOperationDetection",
    "OperationType",
    "DetectionConfidence",
    # Timeline
    "CropTimelineEntry",
    "GrowthStage",
    "CropTimelineAnalysis",
    "TimeSeriesFrame",
    # Anomaly
    "AnomalyDetection",
    "AnomalyType",
    "AnomalySeverity",
]
