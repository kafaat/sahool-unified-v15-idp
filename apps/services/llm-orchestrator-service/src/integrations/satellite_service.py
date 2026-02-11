# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Satellite Service Integration
تكامل خدمة الأقمار الصناعية

Wraps the shared Sentinel NDVI module for use in the orchestrator.
"""

import os
import sys
from datetime import UTC, datetime
from typing import Any

import structlog

# Add shared module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

logger = structlog.get_logger()


class SatelliteService:
    """
    Satellite imagery service for NDVI analysis.
    خدمة صور الأقمار الصناعية لتحليل NDVI
    """

    def __init__(self):
        self._analyzer = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the satellite analyzer."""
        if self._initialized:
            return True

        try:
            from shared.satellite import SentinelNDVIAnalyzer

            self._analyzer = SentinelNDVIAnalyzer()
            await self._analyzer.initialize()
            self._initialized = True
            logger.info("Satellite service initialized")
            return True

        except ImportError as e:
            logger.warning("shared.satellite not available", error=str(e))
            return False
        except Exception as e:
            logger.error("Failed to initialize satellite service", error=str(e))
            return False

    async def get_field_ndvi(
        self,
        field_id: str,
        coordinates: list[tuple[float, float]],
        area_hectares: float = 1.0,
        date: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Get NDVI for a field.
        الحصول على NDVI لحقل
        """
        if not self._initialized or not self._analyzer:
            return self._mock_ndvi(field_id, date)

        try:
            from shared.satellite import FieldBoundary

            boundary = FieldBoundary(
                field_id=field_id,
                coordinates=coordinates,
                area_hectares=area_hectares,
            )

            result = await self._analyzer.get_ndvi(boundary, date)

            if not result:
                return self._mock_ndvi(field_id, date)

            return {
                "field_id": result.field_id,
                "timestamp": result.timestamp.isoformat(),
                "ndvi": {
                    "mean": result.mean_value,
                    "min": result.min_value,
                    "max": result.max_value,
                    "std": result.std_value,
                },
                "health_status": result.health_status,
                "health_status_ar": result.health_status_ar,
                "cloud_coverage_percent": result.cloud_coverage,
                "data_source": result.data_source,
            }

        except Exception as e:
            logger.error("Failed to get NDVI", error=str(e))
            return self._mock_ndvi(field_id, date)

    async def analyze_crop_health(
        self,
        field_id: str,
        coordinates: list[tuple[float, float]],
        area_hectares: float = 1.0,
    ) -> dict[str, Any]:
        """
        Comprehensive crop health analysis.
        تحليل شامل لصحة المحصول
        """
        if not self._initialized or not self._analyzer:
            return self._mock_health_analysis(field_id)

        try:
            from shared.satellite import FieldBoundary

            boundary = FieldBoundary(
                field_id=field_id,
                coordinates=coordinates,
                area_hectares=area_hectares,
            )

            return await self._analyzer.analyze_crop_health(boundary)

        except Exception as e:
            logger.error("Failed to analyze crop health", error=str(e))
            return self._mock_health_analysis(field_id)

    def _mock_ndvi(self, field_id: str, date: datetime | None = None) -> dict[str, Any]:
        """Generate mock NDVI data."""
        import random

        date = date or datetime.now(UTC)
        mean_ndvi = random.uniform(0.4, 0.75)

        health_status = "healthy"
        health_status_ar = "صحي"
        if mean_ndvi < 0.6:
            health_status = "moderate"
            health_status_ar = "معتدل"
        if mean_ndvi < 0.4:
            health_status = "stressed"
            health_status_ar = "مجهد"

        return {
            "field_id": field_id,
            "timestamp": date.isoformat(),
            "ndvi": {
                "mean": round(mean_ndvi, 3),
                "min": round(mean_ndvi - 0.15, 3),
                "max": round(mean_ndvi + 0.1, 3),
                "std": 0.08,
            },
            "health_status": health_status,
            "health_status_ar": health_status_ar,
            "cloud_coverage_percent": random.uniform(0, 20),
            "data_source": "mock",
        }

    def _mock_health_analysis(self, field_id: str) -> dict[str, Any]:
        """Generate mock health analysis."""
        import random

        ndvi_mean = random.uniform(0.45, 0.7)

        recommendations = []
        recommendations_ar = []

        if ndvi_mean < 0.5:
            recommendations.append("Consider additional fertilization")
            recommendations_ar.append("فكر في تسميد إضافي")
        if ndvi_mean < 0.4:
            recommendations.append("Check irrigation system")
            recommendations_ar.append("تحقق من نظام الري")

        return {
            "field_id": field_id,
            "analysis_date": datetime.now(UTC).isoformat(),
            "ndvi": {
                "current": round(ndvi_mean, 3),
                "min": round(ndvi_mean - 0.15, 3),
                "max": round(ndvi_mean + 0.1, 3),
            },
            "health_status": "moderate" if ndvi_mean < 0.6 else "healthy",
            "health_status_ar": "معتدل" if ndvi_mean < 0.6 else "صحي",
            "trend": "stable",
            "trend_ar": "مستقر",
            "data_source": "mock",
            "recommendations": recommendations,
            "recommendations_ar": recommendations_ar,
        }
