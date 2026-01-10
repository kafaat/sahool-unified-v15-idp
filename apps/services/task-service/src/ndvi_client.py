"""
NDVI Client for Task Service
عميل NDVI لخدمة المهام

This module provides integration with the NDVI calculation module
to fetch field health data for task suggestions and alerts.

Author: SAHOOL Platform Team
License: MIT
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration - التكوين
# =============================================================================

# NDVI Engine service URL (internal Kubernetes service)
NDVI_SERVICE_URL = "http://ndvi-engine:8107"

# Health thresholds for task suggestions
HEALTH_THRESHOLDS = {
    "critical": 3.0,  # Health score < 3 = critical
    "poor": 5.0,  # Health score < 5 = poor
    "moderate": 7.0,  # Health score < 7 = moderate
    "good": 8.5,  # Health score < 8.5 = good
    "excellent": 10.0,  # Health score >= 8.5 = excellent
}


# =============================================================================
# Enums - التعدادات
# =============================================================================


class HealthStatus(str, Enum):
    """Field health status based on NDVI analysis"""

    CRITICAL = "critical"
    POOR = "poor"
    MODERATE = "moderate"
    GOOD = "good"
    EXCELLENT = "excellent"


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# Data Classes - فئات البيانات
# =============================================================================


@dataclass
class FieldHealthData:
    """
    بيانات صحة الحقل من تحليل NDVI
    Field health data from NDVI analysis
    """

    field_id: str
    health_score: float  # 0-10
    health_status: HealthStatus
    ndvi_mean: float
    ndvi_min: float
    ndvi_max: float
    ndvi_std_dev: float
    vegetation_coverage: float  # percentage
    zones: dict[str, float]  # healthy, stressed, critical, bare_soil, water
    alerts: list[dict[str, Any]]
    needs_attention: bool
    suggested_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "field_id": self.field_id,
            "health_score": self.health_score,
            "health_status": self.health_status.value,
            "ndvi_mean": round(self.ndvi_mean, 4),
            "ndvi_min": round(self.ndvi_min, 4),
            "ndvi_max": round(self.ndvi_max, 4),
            "ndvi_std_dev": round(self.ndvi_std_dev, 4),
            "vegetation_coverage": round(self.vegetation_coverage, 2),
            "zones": self.zones,
            "alerts": self.alerts,
            "needs_attention": self.needs_attention,
            "suggested_actions": self.suggested_actions,
        }


# =============================================================================
# NDVI Client - عميل NDVI
# =============================================================================


class NDVIClient:
    """
    عميل للتواصل مع خدمة NDVI
    Client for communicating with NDVI service
    """

    def __init__(self, base_url: str = NDVI_SERVICE_URL, timeout: float = 30.0):
        """
        Initialize NDVI client

        Args:
            base_url: Base URL of NDVI service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def close(self):
        """Close HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def get_field_health(
        self,
        field_id: str,
        image_url: str | None = None,
        red_band_data: list | None = None,
        nir_band_data: list | None = None,
    ) -> FieldHealthData:
        """
        الحصول على بيانات صحة الحقل
        Get field health data

        Args:
            field_id: Field identifier
            image_url: Optional satellite image URL
            red_band_data: Optional RED band data array
            nir_band_data: Optional NIR band data array

        Returns:
            Field health data with analysis results
        """
        logger.info(f"Fetching health data for field: {field_id}")

        try:
            # Try to call the NDVI service
            client = await self._get_client()

            payload = {
                "field_id": field_id,
                "image_url": image_url or f"s3://sahool-satellite/{field_id}/latest.tif",
            }

            if red_band_data is not None and nir_band_data is not None:
                payload["red_band_data"] = red_band_data
                payload["nir_band_data"] = nir_band_data

            response = await client.post("/api/v1/ndvi/calculate", json=payload)
            response.raise_for_status()
            data = response.json()

            return self._parse_ndvi_response(field_id, data)

        except httpx.HTTPError as e:
            logger.warning(f"NDVI service unavailable, using local calculation: {e}")
            # Fall back to local calculation
            return await self._calculate_locally(
                field_id, image_url, red_band_data, nir_band_data
            )

        except Exception as e:
            logger.error(f"Error fetching field health: {e}")
            # Return default/simulated data
            return self._get_simulated_health(field_id)

    async def _calculate_locally(
        self,
        field_id: str,
        image_url: str | None,
        red_band_data: list | None,
        nir_band_data: list | None,
    ) -> FieldHealthData:
        """
        حساب محلي باستخدام وحدة NDVI
        Local calculation using NDVI module
        
        NOTE: Heavy CPU-bound calculations run in executor to avoid blocking event loop
        """
        import asyncio
        try:
            # Import the NDVI calculation module
            from apps.kernel.common.queue.tasks.ndvi_calculation import (
                handle_ndvi_calculation,
            )

            payload = {
                "field_id": field_id,
                "image_url": image_url or f"s3://sahool-satellite/{field_id}/latest.tif",
            }

            if red_band_data is not None and nir_band_data is not None:
                payload["red_band_data"] = red_band_data
                payload["nir_band_data"] = nir_band_data

            # Run CPU-intensive NDVI calculation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, handle_ndvi_calculation, payload)
            return self._parse_ndvi_response(field_id, result)

        except ImportError:
            logger.warning("NDVI calculation module not available")
            return self._get_simulated_health(field_id)
        except Exception as e:
            logger.error(f"Local NDVI calculation failed: {e}")
            return self._get_simulated_health(field_id)

    def _parse_ndvi_response(
        self, field_id: str, data: dict[str, Any]
    ) -> FieldHealthData:
        """
        تحليل استجابة NDVI
        Parse NDVI response data
        """
        stats = data.get("statistics", {})
        zones = data.get("zones", {})
        alerts = data.get("alerts", [])
        health_score = data.get("health_score", 5.0)

        # Determine health status
        health_status = self._get_health_status(health_score)

        # Determine if field needs attention
        needs_attention = (
            health_score < HEALTH_THRESHOLDS["moderate"]
            or zones.get("critical", 0) > 10
            or zones.get("stressed", 0) > 25
            or len(alerts) > 0
        )

        # Generate suggested actions based on analysis
        suggested_actions = self._generate_suggested_actions(
            health_score, zones, alerts
        )

        return FieldHealthData(
            field_id=field_id,
            health_score=health_score,
            health_status=health_status,
            ndvi_mean=stats.get("mean", 0.0),
            ndvi_min=stats.get("min", 0.0),
            ndvi_max=stats.get("max", 0.0),
            ndvi_std_dev=stats.get("std_dev", 0.0),
            vegetation_coverage=stats.get("coverage_percent", 0.0),
            zones=zones,
            alerts=alerts,
            needs_attention=needs_attention,
            suggested_actions=suggested_actions,
        )

    def _get_health_status(self, health_score: float) -> HealthStatus:
        """Get health status from score"""
        if health_score < HEALTH_THRESHOLDS["critical"]:
            return HealthStatus.CRITICAL
        elif health_score < HEALTH_THRESHOLDS["poor"]:
            return HealthStatus.POOR
        elif health_score < HEALTH_THRESHOLDS["moderate"]:
            return HealthStatus.MODERATE
        elif health_score < HEALTH_THRESHOLDS["good"]:
            return HealthStatus.GOOD
        else:
            return HealthStatus.EXCELLENT

    def _generate_suggested_actions(
        self,
        health_score: float,
        zones: dict[str, float],
        alerts: list[dict[str, Any]],
    ) -> list[str]:
        """
        إنشاء إجراءات مقترحة
        Generate suggested actions based on analysis
        """
        actions = []

        # Based on health score
        if health_score < HEALTH_THRESHOLDS["critical"]:
            actions.append("Immediate field inspection required")
            actions.append("Check irrigation system")
            actions.append("Soil analysis recommended")
        elif health_score < HEALTH_THRESHOLDS["poor"]:
            actions.append("Schedule field inspection within 24 hours")
            actions.append("Review irrigation schedule")
        elif health_score < HEALTH_THRESHOLDS["moderate"]:
            actions.append("Monitor vegetation trends")
            actions.append("Consider preventive measures")

        # Based on zones
        critical_percent = zones.get("critical", 0)
        stressed_percent = zones.get("stressed", 0)
        bare_soil_percent = zones.get("bare_soil", 0)

        if critical_percent > 20:
            actions.append(f"Investigate critical areas ({critical_percent:.1f}% of field)")

        if stressed_percent > 30:
            actions.append(f"Address stressed vegetation ({stressed_percent:.1f}% of field)")

        if bare_soil_percent > 15:
            actions.append(f"Check bare soil areas ({bare_soil_percent:.1f}% of field)")

        # Based on alerts
        for alert in alerts:
            alert_type = alert.get("type", "")
            if alert_type == "low_vegetation":
                if "Consider nutrient application" not in actions:
                    actions.append("Consider nutrient application")
            elif alert_type == "non_uniform_growth":
                if "Investigate growth pattern variations" not in actions:
                    actions.append("Investigate growth pattern variations")

        return actions[:5]  # Limit to 5 actions

    def _get_simulated_health(self, field_id: str) -> FieldHealthData:
        """
        إنشاء بيانات صحة محاكاة
        Generate simulated health data for testing/fallback
        """
        import random

        # Create consistent random based on field_id
        random.seed(hash(field_id) % (2**32))

        health_score = round(random.uniform(4.0, 9.0), 1)
        health_status = self._get_health_status(health_score)

        zones = {
            "healthy": round(random.uniform(50, 85), 2),
            "stressed": round(random.uniform(5, 25), 2),
            "critical": round(random.uniform(0, 15), 2),
            "bare_soil": round(random.uniform(0, 10), 2),
            "water": round(random.uniform(0, 5), 2),
        }

        # Normalize to 100%
        total = sum(zones.values())
        zones = {k: round(v / total * 100, 2) for k, v in zones.items()}

        ndvi_mean = round(random.uniform(0.3, 0.7), 4)

        alerts = []
        if health_score < 6:
            alerts.append({
                "type": "low_vegetation",
                "severity": "medium",
                "message": "Below average vegetation health detected",
                "message_ar": "تم اكتشاف صحة نباتية أقل من المتوسط",
            })

        needs_attention = health_score < HEALTH_THRESHOLDS["moderate"]
        suggested_actions = self._generate_suggested_actions(
            health_score, zones, alerts
        )

        return FieldHealthData(
            field_id=field_id,
            health_score=health_score,
            health_status=health_status,
            ndvi_mean=ndvi_mean,
            ndvi_min=round(ndvi_mean - 0.2, 4),
            ndvi_max=round(ndvi_mean + 0.2, 4),
            ndvi_std_dev=round(random.uniform(0.05, 0.15), 4),
            vegetation_coverage=zones["healthy"] + zones["stressed"],
            zones=zones,
            alerts=alerts,
            needs_attention=needs_attention,
            suggested_actions=suggested_actions,
        )


# =============================================================================
# Helper Functions - دوال مساعدة
# =============================================================================


def get_task_priority_from_health(health_data: FieldHealthData) -> str:
    """
    تحديد أولوية المهمة بناءً على صحة الحقل
    Determine task priority based on field health

    Returns:
        Priority level: "urgent", "high", "medium", or "low"
    """
    if health_data.health_status == HealthStatus.CRITICAL:
        return "urgent"
    elif health_data.health_status == HealthStatus.POOR:
        return "high"
    elif health_data.health_status == HealthStatus.MODERATE:
        return "medium"
    else:
        return "low"


def get_task_suggestions_from_health(
    health_data: FieldHealthData,
) -> list[dict[str, Any]]:
    """
    إنشاء اقتراحات المهام بناءً على صحة الحقل
    Generate task suggestions based on field health

    Returns:
        List of task suggestion dictionaries
    """
    suggestions = []
    priority = get_task_priority_from_health(health_data)

    # Critical or poor health - immediate inspection
    if health_data.health_status in [HealthStatus.CRITICAL, HealthStatus.POOR]:
        suggestions.append({
            "task_type": "scouting",
            "priority": priority,
            "title": "Urgent Field Inspection Required",
            "title_ar": "فحص عاجل للحقل مطلوب",
            "description": (
                f"Field health score is {health_data.health_score}/10. "
                f"Immediate inspection needed to identify issues. "
                f"Critical areas: {health_data.zones.get('critical', 0):.1f}%"
            ),
            "description_ar": (
                f"درجة صحة الحقل {health_data.health_score}/10. "
                f"مطلوب فحص فوري لتحديد المشاكل. "
                f"المناطق الحرجة: {health_data.zones.get('critical', 0):.1f}%"
            ),
            "reason": f"Health score: {health_data.health_score}/10",
            "reason_ar": f"درجة الصحة: {health_data.health_score}/10",
            "confidence": 0.9 if health_data.health_status == HealthStatus.CRITICAL else 0.8,
            "suggested_due_days": 1 if health_data.health_status == HealthStatus.CRITICAL else 2,
        })

    # High stressed areas - irrigation check
    if health_data.zones.get("stressed", 0) > 20:
        suggestions.append({
            "task_type": "irrigation",
            "priority": "high" if health_data.zones["stressed"] > 35 else "medium",
            "title": "Review Irrigation Schedule",
            "title_ar": "مراجعة جدول الري",
            "description": (
                f"Stressed vegetation detected in {health_data.zones['stressed']:.1f}% of field. "
                "Consider adjusting irrigation frequency or duration."
            ),
            "description_ar": (
                f"تم اكتشاف نباتات مجهدة في {health_data.zones['stressed']:.1f}% من الحقل. "
                "فكر في تعديل تكرار الري أو مدته."
            ),
            "reason": f"Stressed areas: {health_data.zones['stressed']:.1f}%",
            "reason_ar": f"المناطق المجهدة: {health_data.zones['stressed']:.1f}%",
            "confidence": 0.75,
            "suggested_due_days": 2,
        })

    # Low vegetation coverage - soil sampling
    if health_data.vegetation_coverage < 60:
        suggestions.append({
            "task_type": "sampling",
            "priority": "medium",
            "title": "Soil Nutrient Analysis",
            "title_ar": "تحليل مغذيات التربة",
            "description": (
                f"Low vegetation coverage ({health_data.vegetation_coverage:.1f}%). "
                "Recommend soil sampling to check nutrient levels."
            ),
            "description_ar": (
                f"تغطية نباتية منخفضة ({health_data.vegetation_coverage:.1f}%). "
                "يوصى بأخذ عينات التربة للتحقق من مستويات المغذيات."
            ),
            "reason": f"Coverage: {health_data.vegetation_coverage:.1f}%",
            "reason_ar": f"التغطية: {health_data.vegetation_coverage:.1f}%",
            "confidence": 0.7,
            "suggested_due_days": 5,
        })

    # High variance - investigate pattern
    if health_data.ndvi_std_dev > 0.15:
        suggestions.append({
            "task_type": "scouting",
            "priority": "medium",
            "title": "Investigate Growth Variation",
            "title_ar": "فحص تباين النمو",
            "description": (
                f"High variation in vegetation (std: {health_data.ndvi_std_dev:.3f}). "
                "Field shows non-uniform growth patterns."
            ),
            "description_ar": (
                f"تباين عالي في الغطاء النباتي (الانحراف: {health_data.ndvi_std_dev:.3f}). "
                "الحقل يُظهر أنماط نمو غير متجانسة."
            ),
            "reason": f"NDVI std_dev: {health_data.ndvi_std_dev:.3f}",
            "reason_ar": f"انحراف NDVI: {health_data.ndvi_std_dev:.3f}",
            "confidence": 0.65,
            "suggested_due_days": 4,
        })

    return suggestions


# =============================================================================
# Singleton Instance - نسخة واحدة
# =============================================================================

# Global NDVI client instance
_ndvi_client: NDVIClient | None = None


def get_ndvi_client() -> NDVIClient:
    """Get or create NDVI client instance"""
    global _ndvi_client
    if _ndvi_client is None:
        _ndvi_client = NDVIClient()
    return _ndvi_client


async def close_ndvi_client():
    """Close NDVI client on shutdown"""
    global _ndvi_client
    if _ndvi_client is not None:
        await _ndvi_client.close()
        _ndvi_client = None
