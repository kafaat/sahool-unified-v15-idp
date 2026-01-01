"""
📤 SAHOOL Export Tasks
مهام تصدير البيانات

This module provides tasks for exporting EOPatch data to
SAHOOL platform formats and storage systems.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json
import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# SAHOOL Export Task
# =============================================================================


class SahoolExportTask:
    """
    Export EOPatch data to SAHOOL-compatible format

    This task converts EOPatch data to a JSON-serializable format
    that can be consumed by SAHOOL platform services.

    Example:
        task = SahoolExportTask(
            field_id="field_001",
            tenant_id="tenant_123"
        )
        result = task.execute(eopatch)
        # result can be sent to SAHOOL APIs
    """

    def __init__(
        self,
        field_id: str,
        tenant_id: str,
        include_bands: bool = False,
        include_masks: bool = False,
        indices_only: bool = True,
        aggregate_method: str = "mean",  # "mean", "median", "percentile"
        percentile: int = 50,
    ):
        """
        Initialize export task

        Args:
            field_id: SAHOOL field identifier
            tenant_id: SAHOOL tenant identifier
            include_bands: Include raw band statistics
            include_masks: Include mask statistics
            indices_only: Only export vegetation indices
            aggregate_method: Method for spatial aggregation
            percentile: Percentile for "percentile" method
        """
        self.field_id = field_id
        self.tenant_id = tenant_id
        self.include_bands = include_bands
        self.include_masks = include_masks
        self.indices_only = indices_only
        self.aggregate_method = aggregate_method
        self.percentile = percentile

    def execute(self, eopatch) -> Dict[str, Any]:
        """
        Export EOPatch to SAHOOL format

        Args:
            eopatch: EOPatch with calculated indices

        Returns:
            Dictionary in SAHOOL format
        """
        try:
            from eolearn.core import FeatureType

            result = {
                "field_id": self.field_id,
                "tenant_id": self.tenant_id,
                "export_timestamp": datetime.utcnow().isoformat(),
                "data_source": eopatch[FeatureType.META_INFO].get(
                    "data_source", "unknown"
                ),
                "indices": {},
                "metadata": {},
            }

            # Export vegetation indices
            indices = ["NDVI", "EVI", "LAI", "NDWI", "SAVI", "NDMI", "GNDVI", "NDRE"]
            for index_name in indices:
                data = eopatch[FeatureType.DATA].get(index_name)
                if data is not None:
                    stats = self._calculate_statistics(data)
                    result["indices"][index_name.lower()] = stats

            # Export raw bands if requested
            if self.include_bands:
                bands = eopatch[FeatureType.DATA].get("BANDS")
                if bands is not None:
                    result["bands"] = {
                        "shape": list(bands.shape),
                        "dtype": str(bands.dtype),
                        "statistics": self._calculate_band_statistics(bands),
                    }

            # Export mask statistics if requested
            if self.include_masks:
                result["masks"] = {}
                for mask_name in ["CLOUD_MASK", "VALID_DATA", "SCL"]:
                    mask = eopatch[FeatureType.MASK].get(mask_name)
                    if mask is not None:
                        result["masks"][mask_name.lower()] = {
                            "coverage_percent": float(np.mean(mask) * 100),
                        }

            # Add metadata
            result["metadata"]["cloud_coverage"] = eopatch[FeatureType.META_INFO].get(
                "cloud_coverage", None
            )
            result["metadata"]["resolution"] = eopatch[FeatureType.META_INFO].get(
                "resolution", None
            )
            result["metadata"]["time_interval"] = eopatch[FeatureType.META_INFO].get(
                "time_interval", None
            )

            # Add health assessment
            result["health_assessment"] = self._assess_crop_health(result["indices"])

            return result

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

    def _calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate statistics for an index"""
        valid_data = data[np.isfinite(data)]

        if len(valid_data) == 0:
            return {"value": None, "valid_pixels": 0}

        if self.aggregate_method == "mean":
            value = float(np.mean(valid_data))
        elif self.aggregate_method == "median":
            value = float(np.median(valid_data))
        elif self.aggregate_method == "percentile":
            value = float(np.percentile(valid_data, self.percentile))
        else:
            value = float(np.mean(valid_data))

        return {
            "value": round(value, 4),
            "min": round(float(np.min(valid_data)), 4),
            "max": round(float(np.max(valid_data)), 4),
            "std": round(float(np.std(valid_data)), 4),
            "valid_pixels": int(len(valid_data)),
            "total_pixels": int(data.size),
        }

    def _calculate_band_statistics(self, bands: np.ndarray) -> List[Dict[str, float]]:
        """Calculate statistics for each band"""
        band_names = [
            "B02",
            "B03",
            "B04",
            "B05",
            "B06",
            "B07",
            "B08",
            "B8A",
            "B11",
            "B12",
        ]
        stats = []

        for i in range(bands.shape[-1]):
            band_data = bands[..., i]
            valid_data = band_data[np.isfinite(band_data)]

            if len(valid_data) > 0:
                stats.append(
                    {
                        "band": band_names[i] if i < len(band_names) else f"B{i}",
                        "mean": round(float(np.mean(valid_data)), 4),
                        "std": round(float(np.std(valid_data)), 4),
                    }
                )

        return stats

    def _assess_crop_health(self, indices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess crop health based on vegetation indices

        This mirrors the assessment logic in SAHOOL's satellite-service
        but uses real data from eo-learn processing.
        """
        score = 50.0
        anomalies = []
        recommendations_ar = []
        recommendations_en = []

        # Get index values
        ndvi = indices.get("ndvi", {}).get("value")
        ndwi = indices.get("ndwi", {}).get("value")
        evi = indices.get("evi", {}).get("value")
        lai = indices.get("lai", {}).get("value")
        ndmi = indices.get("ndmi", {}).get("value")

        # NDVI assessment
        if ndvi is not None:
            if ndvi >= 0.6:
                score += 20
            elif ndvi >= 0.4:
                score += 10
            elif ndvi >= 0.2:
                score += 0
            else:
                score -= 20
                anomalies.append("low_vegetation_cover")
                recommendations_ar.append(
                    "🌱 الغطاء النباتي منخفض - تحقق من صحة المحصول"
                )
                recommendations_en.append("🌱 Low vegetation cover - check crop health")

        # Water stress (NDWI)
        if ndwi is not None:
            if ndwi < -0.2:
                score -= 15
                anomalies.append("water_stress_detected")
                recommendations_ar.append("💧 إجهاد مائي - زيادة الري فوراً")
                recommendations_en.append("💧 Water stress - increase irrigation")
            elif ndwi > 0.3:
                score += 10

        # Moisture stress (NDMI)
        if ndmi is not None:
            if ndmi < 0:
                score -= 10
                anomalies.append("moisture_deficit")
                recommendations_ar.append("🌡️ نقص الرطوبة - ري تكميلي مطلوب")
                recommendations_en.append(
                    "🌡️ Moisture deficit - supplemental irrigation needed"
                )

        # EVI assessment
        if evi is not None:
            if evi >= 0.4:
                score += 10
            elif evi < 0.2:
                score -= 10
                anomalies.append("poor_canopy_structure")
                recommendations_ar.append("🍃 بنية المظلة ضعيفة - تحقق من التسميد")
                recommendations_en.append(
                    "🍃 Poor canopy structure - check fertilization"
                )

        # LAI assessment
        if lai is not None:
            if lai >= 3:
                score += 10
            elif lai < 1:
                score -= 5
                anomalies.append("sparse_leaf_coverage")
                recommendations_ar.append(
                    "🌿 تغطية الأوراق متناثرة - تسميد نيتروجيني مطلوب"
                )
                recommendations_en.append(
                    "🌿 Sparse leaf coverage - nitrogen fertilization needed"
                )

        # Clamp score
        score = max(0, min(100, score))

        # Determine status
        if score >= 80:
            status = "ممتاز | Excellent"
        elif score >= 60:
            status = "جيد | Good"
        elif score >= 40:
            status = "متوسط | Fair"
        elif score >= 20:
            status = "ضعيف | Poor"
        else:
            status = "حرج | Critical"

        if not anomalies:
            recommendations_ar.append("✅ المحصول في حالة صحية جيدة")
            recommendations_en.append("✅ Crop is healthy - continue current practices")

        return {
            "health_score": round(score, 1),
            "health_status": status,
            "anomalies": anomalies,
            "recommendations_ar": recommendations_ar,
            "recommendations_en": recommendations_en,
        }


# =============================================================================
# EOPatch to SAHOOL Event Task
# =============================================================================


class EOPatchToSahoolTask:
    """
    Convert EOPatch to SAHOOL Event format

    This task creates events compatible with SAHOOL's event-driven
    architecture for publishing to NATS message bus.

    Event types:
    - SatelliteSceneIngested.v1
    - FieldIndicatorsComputed.v1
    - CropHealthAssessed.v1
    """

    def __init__(
        self,
        field_id: str,
        tenant_id: str,
        source_service: str = "satellite-service",
    ):
        """
        Initialize event conversion task

        Args:
            field_id: SAHOOL field identifier
            tenant_id: SAHOOL tenant identifier
            source_service: Name of producing service
        """
        self.field_id = field_id
        self.tenant_id = tenant_id
        self.source_service = source_service

    def create_scene_ingested_event(self, eopatch) -> Dict[str, Any]:
        """
        Create SatelliteSceneIngested.v1 event

        This event is published when new satellite data is fetched.
        """
        import uuid

        try:
            from eolearn.core import FeatureType

            return {
                "event_id": str(uuid.uuid4()),
                "event_type": "SatelliteSceneIngested",
                "event_version": 1,
                "tenant_id": self.tenant_id,
                "timestamp": datetime.utcnow().isoformat(),
                "source": self.source_service,
                "payload": {
                    "scene_id": f"EOPatch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "field_id": self.field_id,
                    "satellite": eopatch[FeatureType.META_INFO].get(
                        "data_source", "SENTINEL2_L2A"
                    ),
                    "acquisition_date": datetime.utcnow().isoformat(),
                    "cloud_cover_percent": eopatch[FeatureType.META_INFO].get(
                        "cloud_coverage", 0
                    ),
                    "resolution_m": eopatch[FeatureType.META_INFO].get(
                        "resolution", 10
                    ),
                    "bands_available": [
                        "B02",
                        "B03",
                        "B04",
                        "B05",
                        "B06",
                        "B07",
                        "B08",
                        "B8A",
                        "B11",
                        "B12",
                    ],
                    "processing_level": "L2A",
                },
            }
        except Exception as e:
            logger.error(f"Failed to create scene event: {e}")
            raise

    def create_indicators_computed_event(
        self, eopatch, indices_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create FieldIndicatorsComputed.v1 event

        This event is published when vegetation indices are calculated.
        """
        import uuid

        return {
            "event_id": str(uuid.uuid4()),
            "event_type": "FieldIndicatorsComputed",
            "event_version": 1,
            "tenant_id": self.tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "source": self.source_service,
            "payload": {
                "field_id": self.field_id,
                "computation_date": datetime.utcnow().isoformat(),
                "source_scene_id": f"EOPatch_{datetime.now().strftime('%Y%m%d')}",
                "indicators": {
                    "ndvi": indices_summary.get("NDVI", {}).get("mean"),
                    "evi": indices_summary.get("EVI", {}).get("mean"),
                    "lai": indices_summary.get("LAI", {}).get("mean"),
                    "ndwi": indices_summary.get("NDWI", {}).get("mean"),
                    "savi": indices_summary.get("SAVI", {}).get("mean"),
                    "ndmi": indices_summary.get("NDMI", {}).get("mean"),
                },
                "valid_pixel_percentage": 95.0,  # Would be calculated from mask
            },
        }

    def create_health_assessed_event(
        self, health_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create CropHealthAssessed.v1 event

        This event is published when crop health is assessed.
        """
        import uuid

        return {
            "event_id": str(uuid.uuid4()),
            "event_type": "CropHealthAssessed",
            "event_version": 1,
            "tenant_id": self.tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "source": self.source_service,
            "payload": {
                "field_id": self.field_id,
                "assessment_date": datetime.utcnow().isoformat(),
                "health_score": health_assessment.get("health_score", 0),
                "health_status": health_assessment.get("health_status", "unknown"),
                "anomalies_detected": health_assessment.get("anomalies", []),
                "assessment_method": "eo-learn-vegetation-indices",
                "confidence_score": 0.85,
            },
        }

    def execute(self, eopatch, indices_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate all SAHOOL events from EOPatch

        Returns list of events ready for publishing to NATS.
        """
        events = []

        # Scene ingested event
        events.append(self.create_scene_ingested_event(eopatch))

        # Indicators computed event
        events.append(self.create_indicators_computed_event(eopatch, indices_summary))

        # Run export to get health assessment
        export_task = SahoolExportTask(field_id=self.field_id, tenant_id=self.tenant_id)
        export_result = export_task.execute(eopatch)

        # Health assessed event
        events.append(
            self.create_health_assessed_event(
                export_result.get("health_assessment", {})
            )
        )

        return events
