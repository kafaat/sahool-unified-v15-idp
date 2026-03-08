"""
Anomaly Detector Module - كاشف الشذوذ
Based on: Qin et al. (2026) - Unusual event detection in agricultural monitoring

This module detects anomalies in agricultural fields from tower camera frames,
including pest/disease outbreaks, water stress, unauthorized activity, etc.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Optional

import numpy as np
from pydantic import BaseModel, Field

from ..core.change_detection import ChangeDetectionResult, ChangeDetector
from ..models.anomaly import (
    ANOMALY_TYPE_AR,
    SEVERITY_AR,
    SEVERITY_RESPONSE_TIME,
    AnomalyAlert,
    AnomalyDetection,
    AnomalyLocation,
    AnomalySeverity,
    AnomalyType,
)

logger = logging.getLogger(__name__)


class AnomalyCandidate(BaseModel):
    """Candidate anomaly before confirmation"""

    anomaly_type: AnomalyType
    confidence: float
    location_x: int
    location_y: int
    width: int
    height: int
    description: str
    evidence_score: float


class AnomalyDetector:
    """
    Detect anomalies in agricultural fields from camera frames.

    Uses multiple detection methods:
    1. Change detection for sudden changes
    2. Color/texture analysis for stress detection
    3. Motion detection for unauthorized activity
    4. Pattern matching for known anomaly signatures
    """

    # Thresholds for different anomaly types
    WATER_STRESS_NDVI_THRESHOLD = 0.3
    SEVERE_CHANGE_THRESHOLD = 0.4
    MOTION_THRESHOLD = 0.25

    # Color ranges for stress detection (in HSV)
    STRESS_COLOR_RANGES = {
        "yellowing": ((20, 100, 100), (40, 255, 255)),  # Yellow
        "browning": ((10, 100, 50), (20, 255, 200)),  # Brown
        "wilting": ((35, 50, 50), (85, 255, 200)),  # Faded green
    }

    def __init__(
        self,
        change_detector: ChangeDetector | None = None,
        enable_motion_detection: bool = True,
        enable_stress_detection: bool = True,
    ):
        """
        Initialize anomaly detector.

        Args:
            change_detector: Change detector instance
            enable_motion_detection: Enable motion-based anomaly detection
            enable_stress_detection: Enable crop stress detection
        """
        self.change_detector = change_detector or ChangeDetector(trigger_threshold=0.15)
        self.enable_motion = enable_motion_detection
        self.enable_stress = enable_stress_detection

        # Background model for motion detection
        self.background_model: np.ndarray | None = None
        self.background_alpha = 0.1  # Learning rate

        logger.info("AnomalyDetector initialized")

    async def detect(
        self,
        frame: np.ndarray,
        previous_frame: np.ndarray | None,
        frame_id: str,
        field_id: str,
        camera_id: str,
        tenant_id: str,
        geo_projector=None,
    ) -> list[AnomalyDetection]:
        """
        Detect anomalies in a frame.

        Args:
            frame: Current frame
            previous_frame: Previous frame for change detection
            frame_id: Frame identifier
            field_id: Field identifier
            camera_id: Camera identifier
            tenant_id: Tenant identifier
            geo_projector: Optional geo-projector for coordinates

        Returns:
            List of detected anomalies
        """
        anomalies = []
        candidates = []

        # 1. Change-based detection
        if previous_frame is not None:
            change_candidates = await self._detect_change_anomalies(frame, previous_frame)
            candidates.extend(change_candidates)

        # 2. Stress detection (color/texture analysis)
        if self.enable_stress:
            stress_candidates = self._detect_stress_anomalies(frame)
            candidates.extend(stress_candidates)

        # 3. Motion detection (for unauthorized activity)
        if self.enable_motion:
            motion_candidates = self._detect_motion_anomalies(frame)
            candidates.extend(motion_candidates)

        # Update background model
        self._update_background(frame)

        # Convert candidates to anomaly detections
        for candidate in candidates:
            if candidate.confidence < 0.5:
                continue

            # Compute geo-location if projector available
            location = self._compute_location(candidate, frame.shape, geo_projector)

            # Determine severity based on type and confidence
            severity = self._determine_severity(candidate)

            anomaly = AnomalyDetection(
                anomaly_id=f"anomaly_{uuid.uuid4().hex[:12]}",
                field_id=field_id,
                camera_id=camera_id,
                anomaly_type=candidate.anomaly_type,
                anomaly_type_ar=ANOMALY_TYPE_AR.get(candidate.anomaly_type, "غير معروف"),
                severity=severity,
                severity_ar=SEVERITY_AR.get(severity, "غير معروف"),
                confidence=candidate.confidence,
                description=candidate.description,
                description_ar=self._translate_description(candidate.description),
                location=location,
                source_frame_id=frame_id,
                detection_method="cv_multi_method",
                tenant_id=tenant_id,
            )
            anomalies.append(anomaly)

        logger.info(f"Detected {len(anomalies)} anomalies in {field_id}")
        return anomalies

    async def _detect_change_anomalies(
        self,
        frame: np.ndarray,
        previous_frame: np.ndarray,
    ) -> list[AnomalyCandidate]:
        """Detect anomalies based on frame changes."""
        candidates = []

        # Run change detection
        change_result = await self.change_detector.compute_change(previous_frame, frame)

        # Check for severe sudden change
        if change_result.change_score >= self.SEVERE_CHANGE_THRESHOLD:
            candidates.append(
                AnomalyCandidate(
                    anomaly_type=AnomalyType.UNKNOWN,
                    confidence=min(change_result.change_score * 1.5, 0.95),
                    location_x=0,
                    location_y=0,
                    width=frame.shape[1],
                    height=frame.shape[0],
                    description=f"Severe sudden change detected (score: {change_result.change_score:.2f})",
                    evidence_score=change_result.change_score,
                )
            )

        # Check individual regions for localized anomalies
        for region in change_result.change_regions:
            if region["change_score"] >= self.SEVERE_CHANGE_THRESHOLD:
                candidates.append(
                    AnomalyCandidate(
                        anomaly_type=AnomalyType.UNKNOWN,
                        confidence=min(region["change_score"] * 1.2, 0.9),
                        location_x=region["x"],
                        location_y=region["y"],
                        width=region["width"],
                        height=region["height"],
                        description=f"Localized change in region ({region['x']}, {region['y']})",
                        evidence_score=region["change_score"],
                    )
                )

        return candidates

    def _detect_stress_anomalies(
        self,
        frame: np.ndarray,
    ) -> list[AnomalyCandidate]:
        """Detect crop stress from color/texture analysis."""
        candidates = []
        h, w = frame.shape[:2]

        # Convert to HSV if RGB
        if len(frame.shape) == 3 and frame.shape[2] >= 3:
            # Simple RGB to HSV conversion
            hsv = self._rgb_to_hsv(frame)

            # Check for stress colors
            for stress_type, (lower, upper) in self.STRESS_COLOR_RANGES.items():
                mask = self._color_mask(hsv, lower, upper)
                stress_ratio = np.sum(mask) / (h * w)

                if stress_ratio > 0.1:  # More than 10% of image
                    # Find largest connected region
                    region = self._find_largest_region(mask)
                    if region is not None:
                        x, y, rw, rh = region
                        candidates.append(
                            AnomalyCandidate(
                                anomaly_type=self._stress_type_to_anomaly(stress_type),
                                confidence=min(stress_ratio * 5, 0.9),
                                location_x=x,
                                location_y=y,
                                width=rw,
                                height=rh,
                                description=f"Crop {stress_type} detected ({stress_ratio * 100:.1f}% of field)",
                                evidence_score=stress_ratio,
                            )
                        )

        return candidates

    def _detect_motion_anomalies(
        self,
        frame: np.ndarray,
    ) -> list[AnomalyCandidate]:
        """Detect motion-based anomalies (unauthorized activity)."""
        candidates = []

        if self.background_model is None:
            return candidates

        # Convert to grayscale
        if len(frame.shape) == 3:
            gray = np.dot(frame[..., :3], [0.299, 0.587, 0.114])
        else:
            gray = frame.astype(float)

        # Background subtraction
        diff = np.abs(gray - self.background_model)
        motion_mask = diff > 30  # Threshold

        motion_ratio = np.sum(motion_mask) / motion_mask.size

        if motion_ratio > self.MOTION_THRESHOLD:
            # Significant motion detected
            region = self._find_largest_region(motion_mask.astype(np.uint8))
            if region is not None:
                x, y, rw, rh = region
                candidates.append(
                    AnomalyCandidate(
                        anomaly_type=AnomalyType.UNAUTHORIZED_ACTIVITY,
                        confidence=min(motion_ratio * 3, 0.85),
                        location_x=x,
                        location_y=y,
                        width=rw,
                        height=rh,
                        description=f"Significant motion detected ({motion_ratio * 100:.1f}% of frame)",
                        evidence_score=motion_ratio,
                    )
                )

        return candidates

    def _update_background(self, frame: np.ndarray):
        """Update background model for motion detection."""
        if len(frame.shape) == 3:
            gray = np.dot(frame[..., :3], [0.299, 0.587, 0.114])
        else:
            gray = frame.astype(float)

        if self.background_model is None:
            self.background_model = gray.copy()
        else:
            # Exponential moving average
            self.background_model = (1 - self.background_alpha) * self.background_model + self.background_alpha * gray

    def _rgb_to_hsv(self, rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to HSV color space."""
        # Normalize to [0, 1]
        rgb_norm = rgb.astype(float) / 255.0

        r, g, b = rgb_norm[..., 0], rgb_norm[..., 1], rgb_norm[..., 2]

        max_c = np.maximum(np.maximum(r, g), b)
        min_c = np.minimum(np.minimum(r, g), b)
        delta = max_c - min_c

        # Hue
        h = np.zeros_like(max_c)
        mask_r = (max_c == r) & (delta > 0)
        mask_g = (max_c == g) & (delta > 0)
        mask_b = (max_c == b) & (delta > 0)

        h[mask_r] = 60 * (((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6)
        h[mask_g] = 60 * (((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2)
        h[mask_b] = 60 * (((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4)

        # Saturation
        s = np.where(max_c > 0, delta / max_c, 0)

        # Value
        v = max_c

        # Scale to [0, 255]
        hsv = np.stack([h / 2, s * 255, v * 255], axis=-1)
        return hsv.astype(np.uint8)

    def _color_mask(
        self,
        hsv: np.ndarray,
        lower: tuple,
        upper: tuple,
    ) -> np.ndarray:
        """Create mask for colors in range."""
        h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

        mask = (h >= lower[0]) & (h <= upper[0]) & (s >= lower[1]) & (s <= upper[1]) & (v >= lower[2]) & (v <= upper[2])

        return mask.astype(np.uint8)

    def _find_largest_region(
        self,
        mask: np.ndarray,
    ) -> tuple[int, int, int, int] | None:
        """Find bounding box of largest connected region in mask."""
        if np.sum(mask) == 0:
            return None

        # Find non-zero coordinates
        coords = np.argwhere(mask > 0)
        if len(coords) == 0:
            return None

        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)

        return (int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min))

    def _stress_type_to_anomaly(self, stress_type: str) -> AnomalyType:
        """Map stress type to anomaly type."""
        mapping = {
            "yellowing": AnomalyType.NUTRIENT_DEFICIENCY,
            "browning": AnomalyType.WATER_STRESS,
            "wilting": AnomalyType.WATER_STRESS,
        }
        return mapping.get(stress_type, AnomalyType.UNKNOWN)

    def _compute_location(
        self,
        candidate: AnomalyCandidate,
        frame_shape: tuple,
        geo_projector,
    ) -> AnomalyLocation:
        """Compute geographic location for anomaly."""
        h, w = frame_shape[:2]

        # Compute center of anomaly region
        center_x = candidate.location_x + candidate.width / 2
        center_y = candidate.location_y + candidate.height / 2

        # Default coordinates
        lat, lon = 0.0, 0.0

        if geo_projector is not None:
            try:
                lon, lat = geo_projector.pixel_to_geo(center_x, center_y)
            except Exception as e:
                logger.warning(f"Failed to compute geo coordinates: {e}")

        # Compute affected area percentage
        anomaly_pixels = candidate.width * candidate.height
        total_pixels = h * w
        affected_percent = (anomaly_pixels / total_pixels) * 100

        return AnomalyLocation(
            lat=lat,
            lon=lon,
            affected_area_percent=affected_percent,
        )

    def _determine_severity(self, candidate: AnomalyCandidate) -> AnomalySeverity:
        """Determine severity based on anomaly type and confidence."""
        # Critical anomalies
        critical_types = {
            AnomalyType.FIRE_DETECTED,
            AnomalyType.UNAUTHORIZED_ACTIVITY,
            AnomalyType.THEFT,
        }

        high_types = {
            AnomalyType.PEST_INFESTATION,
            AnomalyType.DISEASE_OUTBREAK,
            AnomalyType.FLOOD_DAMAGE,
            AnomalyType.IRRIGATION_FAILURE,
        }

        if candidate.anomaly_type in critical_types:
            return AnomalySeverity.CRITICAL
        elif candidate.anomaly_type in high_types:
            if candidate.confidence >= 0.8:
                return AnomalySeverity.HIGH
            return AnomalySeverity.MEDIUM
        elif candidate.confidence >= 0.85:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def _translate_description(self, description: str) -> str:
        """Translate description to Arabic (simplified)."""
        # Basic translation mapping
        translations = {
            "Severe sudden change detected": "تم اكتشاف تغيير مفاجئ شديد",
            "Localized change in region": "تغيير موضعي في المنطقة",
            "Crop yellowing detected": "تم اكتشاف اصفرار المحصول",
            "Crop browning detected": "تم اكتشاف اسمرار المحصول",
            "Crop wilting detected": "تم اكتشاف ذبول المحصول",
            "Significant motion detected": "تم اكتشاف حركة ملحوظة",
        }

        for eng, ar in translations.items():
            if eng in description:
                # Replace and keep any numbers/details
                return description.replace(eng, ar)

        return f"شذوذ مكتشف: {description}"

    def create_alert(
        self,
        anomaly: AnomalyDetection,
    ) -> AnomalyAlert:
        """Create alert from anomaly detection."""
        # Determine notification channels based on severity
        if anomaly.severity == AnomalySeverity.CRITICAL:
            channels = ["push", "sms", "whatsapp"]
            roles = ["field_manager", "owner", "agronomist"]
        elif anomaly.severity == AnomalySeverity.HIGH:
            channels = ["push", "sms"]
            roles = ["field_manager", "agronomist"]
        else:
            channels = ["push"]
            roles = ["field_manager"]

        # Calculate priority score (1-100)
        severity_scores = {
            AnomalySeverity.CRITICAL: 90,
            AnomalySeverity.HIGH: 70,
            AnomalySeverity.MEDIUM: 50,
            AnomalySeverity.LOW: 30,
        }
        base_score = severity_scores.get(anomaly.severity, 50)
        priority_score = min(100, int(base_score + anomaly.confidence * 10))

        # Generate recommended actions
        actions, actions_ar = self._generate_actions(anomaly)

        return AnomalyAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:12]}",
            anomaly_id=anomaly.anomaly_id,
            field_id=anomaly.field_id,
            title=f"{anomaly.severity.value.upper()}: {anomaly.anomaly_type.value.replace('_', ' ').title()}",
            title_ar=f"{anomaly.severity_ar}: {anomaly.anomaly_type_ar}",
            message=anomaly.description,
            message_ar=anomaly.description_ar,
            severity=anomaly.severity,
            priority_score=priority_score,
            recommended_actions=actions,
            recommended_actions_ar=actions_ar,
            notify_roles=roles,
            notification_channels=channels,
            tenant_id=anomaly.tenant_id,
        )

    def _generate_actions(
        self,
        anomaly: AnomalyDetection,
    ) -> tuple[list[str], list[str]]:
        """Generate recommended actions for anomaly."""
        actions_map = {
            AnomalyType.WATER_STRESS: (
                [
                    "Check irrigation system",
                    "Increase watering frequency",
                    "Inspect soil moisture sensors",
                ],
                ["فحص نظام الري", "زيادة تكرار الري", "فحص مستشعرات رطوبة التربة"],
            ),
            AnomalyType.NUTRIENT_DEFICIENCY: (
                ["Conduct soil test", "Apply appropriate fertilizer", "Consult agronomist"],
                ["إجراء اختبار التربة", "تطبيق السماد المناسب", "استشارة المهندس الزراعي"],
            ),
            AnomalyType.PEST_INFESTATION: (
                [
                    "Identify pest species",
                    "Consider biological control",
                    "Apply targeted treatment",
                ],
                ["تحديد نوع الآفة", "النظر في المكافحة البيولوجية", "تطبيق علاج مستهدف"],
            ),
            AnomalyType.UNAUTHORIZED_ACTIVITY: (
                ["Review camera footage", "Contact security", "File incident report"],
                ["مراجعة تسجيلات الكاميرا", "الاتصال بالأمن", "تقديم تقرير الحادث"],
            ),
            AnomalyType.FIRE_DETECTED: (
                [
                    "Call emergency services immediately",
                    "Evacuate personnel",
                    "Activate fire suppression",
                ],
                ["الاتصال بخدمات الطوارئ فوراً", "إخلاء الموظفين", "تفعيل نظام إطفاء الحريق"],
            ),
        }

        default = (
            ["Investigate the anomaly", "Document findings", "Take corrective action"],
            ["التحقيق في الشذوذ", "توثيق النتائج", "اتخاذ إجراء تصحيحي"],
        )

        return actions_map.get(anomaly.anomaly_type, default)
