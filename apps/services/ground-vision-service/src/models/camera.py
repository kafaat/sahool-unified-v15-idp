"""
Tower Camera Models - نماذج كاميرات الأبراج
Based on: Qin et al. (2026) - Quaternion-based georeferencing
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class CameraStatus(StrEnum):
    """Camera operational status"""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    CALIBRATING = "calibrating"


class CameraIntrinsics(BaseModel):
    """Camera intrinsic parameters - معاملات الكاميرا الداخلية"""

    focal_length_x: float = Field(..., description="Focal length in x (pixels)")
    focal_length_y: float = Field(..., description="Focal length in y (pixels)")
    principal_point_x: float = Field(..., description="Principal point x (pixels)")
    principal_point_y: float = Field(..., description="Principal point y (pixels)")
    distortion_k1: float = Field(default=0.0, description="Radial distortion k1")
    distortion_k2: float = Field(default=0.0, description="Radial distortion k2")
    distortion_p1: float = Field(default=0.0, description="Tangential distortion p1")
    distortion_p2: float = Field(default=0.0, description="Tangential distortion p2")
    image_width: int = Field(..., description="Image width in pixels")
    image_height: int = Field(..., description="Image height in pixels")

    def to_matrix(self) -> list[list[float]]:
        """Return 3x3 intrinsic matrix K"""
        return [
            [self.focal_length_x, 0, self.principal_point_x],
            [0, self.focal_length_y, self.principal_point_y],
            [0, 0, 1],
        ]


class CameraExtrinsics(BaseModel):
    """
    Camera extrinsic parameters using quaternion representation.
    معاملات الكاميرا الخارجية باستخدام تمثيل الكواترنيون

    Quaternion avoids gimbal lock issues with Euler angles.
    """

    # Position in local ENU (East-North-Up) coordinates
    position_x: float = Field(..., description="X position in meters (East)")
    position_y: float = Field(..., description="Y position in meters (North)")
    position_z: float = Field(..., description="Z position in meters (Up/Altitude)")

    # Orientation as quaternion [w, x, y, z]
    quaternion_w: float = Field(..., description="Quaternion scalar component")
    quaternion_x: float = Field(..., description="Quaternion x component")
    quaternion_y: float = Field(..., description="Quaternion y component")
    quaternion_z: float = Field(..., description="Quaternion z component")

    # Reference point for local coordinates
    reference_lat: float = Field(..., description="Reference latitude (WGS84)")
    reference_lon: float = Field(..., description="Reference longitude (WGS84)")
    reference_alt: float = Field(default=0.0, description="Reference altitude (m)")

    def get_quaternion(self) -> tuple[float, float, float, float]:
        """Return quaternion as tuple (w, x, y, z)"""
        return (
            self.quaternion_w,
            self.quaternion_x,
            self.quaternion_y,
            self.quaternion_z,
        )

    def get_position(self) -> tuple[float, float, float]:
        """Return position as tuple (x, y, z)"""
        return (self.position_x, self.position_y, self.position_z)


class TowerCamera(BaseModel):
    """
    Tower camera registration model - نموذج تسجيل كاميرا البرج
    """

    camera_id: str = Field(..., description="Unique camera identifier")
    tower_id: str = Field(..., description="Tower identifier where camera is mounted")
    name: str = Field(..., description="Camera display name")
    name_ar: str = Field(..., description="Camera display name in Arabic")

    # Location
    latitude: float = Field(..., description="Camera latitude (WGS84)")
    longitude: float = Field(..., description="Camera longitude (WGS84)")
    altitude_m: float = Field(..., description="Camera altitude in meters")

    # Calibration
    intrinsics: CameraIntrinsics
    extrinsics: CameraExtrinsics

    # Field of View coverage (GeoJSON polygon)
    fov_polygon: dict | None = Field(default=None, description="Ground coverage area as GeoJSON Polygon")

    # Capabilities
    zoom_min: float = Field(default=1.0, description="Minimum zoom factor")
    zoom_max: float = Field(default=40.0, description="Maximum zoom factor")
    pan_range_degrees: float = Field(default=360.0, description="Pan range in degrees")
    tilt_min_degrees: float = Field(default=-90.0, description="Minimum tilt angle")
    tilt_max_degrees: float = Field(default=30.0, description="Maximum tilt angle")

    # Status
    status: CameraStatus = Field(default=CameraStatus.OFFLINE)
    last_frame_at: datetime | None = None

    # Multi-tenancy
    tenant_id: str = Field(..., description="Tenant identifier")
    fields_covered: list[str] = Field(default_factory=list, description="List of field IDs in camera coverage")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    calibrated_at: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "camera_id": "cam_tower_001",
                "tower_id": "tower_hadramaut_001",
                "name": "Hadramaut Valley Camera 1",
                "name_ar": "كاميرا وادي حضرموت 1",
                "latitude": 15.9,
                "longitude": 48.8,
                "altitude_m": 50.0,
                "tenant_id": "sahool",
                "fields_covered": ["field_001", "field_002", "field_003"],
            }
        }


class CameraCreateRequest(BaseModel):
    """Request model for creating a new camera"""

    tower_id: str
    name: str
    name_ar: str
    latitude: float
    longitude: float
    altitude_m: float
    intrinsics: CameraIntrinsics
    extrinsics: CameraExtrinsics
    tenant_id: str
    zoom_min: float = 1.0
    zoom_max: float = 40.0


class CameraUpdateRequest(BaseModel):
    """Request model for updating camera configuration"""

    name: str | None = None
    name_ar: str | None = None
    intrinsics: CameraIntrinsics | None = None
    extrinsics: CameraExtrinsics | None = None
    status: CameraStatus | None = None
    fields_covered: list[str] | None = None
