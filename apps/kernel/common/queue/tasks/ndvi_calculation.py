"""
SAHOOL NDVI Calculation Handler
معالج حساب NDVI

Handles background NDVI (Normalized Difference Vegetation Index) calculations.
يعالج حسابات NDVI (مؤشر الغطاء النباتي المعياري) في الخلفية.

NDVI Formula: (NIR - RED) / (NIR + RED)
- Values range from -1 to +1
- Higher values indicate healthier vegetation
- Typical ranges:
  - Water bodies: < 0
  - Bare soil: 0.0 - 0.1
  - Sparse vegetation: 0.1 - 0.2
  - Moderate vegetation: 0.2 - 0.4
  - Dense vegetation: 0.4 - 0.6
  - Very dense vegetation: > 0.6

Author: SAHOOL Platform Team
License: MIT
"""

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# Constants and Thresholds - الثوابت والعتبات
# =============================================================================

# NDVI classification thresholds - عتبات تصنيف NDVI
NDVI_THRESHOLDS = {
    "water": -0.1,  # ماء
    "bare_soil": 0.1,  # تربة عارية
    "sparse_vegetation": 0.2,  # غطاء نباتي متفرق
    "moderate_vegetation": 0.4,  # غطاء نباتي معتدل
    "dense_vegetation": 0.6,  # غطاء نباتي كثيف
    "very_dense": 0.8,  # غطاء نباتي كثيف جداً
}

# Health score thresholds - عتبات درجة الصحة
HEALTH_THRESHOLDS = {
    "critical": 0.15,  # حرج
    "poor": 0.25,  # ضعيف
    "fair": 0.35,  # متوسط
    "good": 0.50,  # جيد
    "excellent": 0.65,  # ممتاز
}


# =============================================================================
# Data Classes - فئات البيانات
# =============================================================================


@dataclass
class NDVIStatistics:
    """إحصائيات NDVI - NDVI Statistics"""

    mean: float
    median: float
    min: float
    max: float
    std_dev: float
    coverage_percent: float  # نسبة التغطية النباتية
    valid_pixels: int  # عدد البكسلات الصالحة
    total_pixels: int  # إجمالي البكسلات

    def to_dict(self) -> dict[str, Any]:
        """تحويل إلى قاموس - Convert to dictionary"""
        return {
            "mean": round(self.mean, 4),
            "median": round(self.median, 4),
            "min": round(self.min, 4),
            "max": round(self.max, 4),
            "std_dev": round(self.std_dev, 4),
            "coverage_percent": round(self.coverage_percent, 2),
            "valid_pixels": self.valid_pixels,
            "total_pixels": self.total_pixels,
        }


@dataclass
class ZoneClassification:
    """تصنيف المناطق - Zone Classification"""

    healthy_percent: float  # صحي
    stressed_percent: float  # مجهد
    critical_percent: float  # حرج
    bare_soil_percent: float  # تربة عارية
    water_percent: float  # ماء

    def to_dict(self) -> dict[str, float]:
        """تحويل إلى قاموس - Convert to dictionary"""
        return {
            "healthy": round(self.healthy_percent, 2),
            "stressed": round(self.stressed_percent, 2),
            "critical": round(self.critical_percent, 2),
            "bare_soil": round(self.bare_soil_percent, 2),
            "water": round(self.water_percent, 2),
        }


@dataclass
class NDVIAlert:
    """تنبيه NDVI - NDVI Alert"""

    alert_type: str
    severity: str  # low, medium, high, critical
    location: dict[str, float] | None
    area_percent: float
    message_ar: str
    message_en: str

    def to_dict(self) -> dict[str, Any]:
        """تحويل إلى قاموس - Convert to dictionary"""
        return {
            "type": self.alert_type,
            "severity": self.severity,
            "location": self.location,
            "area_percent": round(self.area_percent, 2),
            "message": self.message_en,
            "message_ar": self.message_ar,
        }


# =============================================================================
# NDVI Calculation Functions - دوال حساب NDVI
# =============================================================================


def calculate_ndvi_from_bands(
    red_band: np.ndarray, nir_band: np.ndarray
) -> np.ndarray:
    """
    حساب NDVI من نطاقي الأحمر والأشعة تحت الحمراء القريبة
    Calculate NDVI from RED and NIR bands

    Formula: NDVI = (NIR - RED) / (NIR + RED)

    Args:
        red_band: نطاق الأحمر - RED band array (typically B4 for Sentinel-2)
        nir_band: نطاق الأشعة تحت الحمراء - NIR band array (typically B8 for Sentinel-2)

    Returns:
        مصفوفة قيم NDVI - NDVI values array (-1 to 1)
    """
    # تحويل إلى float32 لتجنب مشاكل القسمة
    # Convert to float32 to avoid division issues
    red = red_band.astype(np.float32)
    nir = nir_band.astype(np.float32)

    # حساب المقام مع تجنب القسمة على صفر
    # Calculate denominator avoiding division by zero
    denominator = nir + red

    # حساب NDVI مع معالجة القسمة على صفر
    # Calculate NDVI with zero-division handling
    # Use np.divide with where to avoid RuntimeWarning
    ndvi = np.zeros_like(denominator)
    np.divide(nir - red, denominator, out=ndvi, where=denominator != 0)

    # قص القيم ضمن النطاق المنطقي [-1, 1]
    # Clip values to valid range
    ndvi = np.clip(ndvi, -1, 1)

    return ndvi


def calculate_statistics(ndvi_array: np.ndarray) -> NDVIStatistics:
    """
    حساب إحصائيات NDVI
    Calculate NDVI statistics

    Args:
        ndvi_array: مصفوفة NDVI - NDVI array

    Returns:
        إحصائيات NDVI - NDVI statistics
    """
    # إزالة القيم غير الصالحة (NaN, Inf)
    # Remove invalid values
    valid_mask = np.isfinite(ndvi_array)
    valid_values = ndvi_array[valid_mask]

    if len(valid_values) == 0:
        return NDVIStatistics(
            mean=0.0,
            median=0.0,
            min=0.0,
            max=0.0,
            std_dev=0.0,
            coverage_percent=0.0,
            valid_pixels=0,
            total_pixels=ndvi_array.size,
        )

    # حساب نسبة التغطية النباتية (NDVI > 0.2)
    # Calculate vegetation coverage percentage
    vegetation_mask = valid_values > NDVI_THRESHOLDS["sparse_vegetation"]
    coverage_percent = (np.sum(vegetation_mask) / len(valid_values)) * 100

    return NDVIStatistics(
        mean=float(np.mean(valid_values)),
        median=float(np.median(valid_values)),
        min=float(np.min(valid_values)),
        max=float(np.max(valid_values)),
        std_dev=float(np.std(valid_values)),
        coverage_percent=coverage_percent,
        valid_pixels=int(np.sum(valid_mask)),
        total_pixels=ndvi_array.size,
    )


def classify_zones(ndvi_array: np.ndarray) -> ZoneClassification:
    """
    تصنيف المناطق حسب قيم NDVI
    Classify zones based on NDVI values

    Args:
        ndvi_array: مصفوفة NDVI - NDVI array

    Returns:
        تصنيف المناطق - Zone classification
    """
    valid_mask = np.isfinite(ndvi_array)
    valid_values = ndvi_array[valid_mask]

    if len(valid_values) == 0:
        return ZoneClassification(
            healthy_percent=0.0,
            stressed_percent=0.0,
            critical_percent=0.0,
            bare_soil_percent=0.0,
            water_percent=0.0,
        )

    total = len(valid_values)

    # تصنيف المناطق
    # Classify zones
    water = np.sum(valid_values < NDVI_THRESHOLDS["water"]) / total * 100
    bare_soil = (
        np.sum(
            (valid_values >= NDVI_THRESHOLDS["water"])
            & (valid_values < NDVI_THRESHOLDS["bare_soil"])
        )
        / total
        * 100
    )
    critical = (
        np.sum(
            (valid_values >= NDVI_THRESHOLDS["bare_soil"])
            & (valid_values < NDVI_THRESHOLDS["sparse_vegetation"])
        )
        / total
        * 100
    )
    stressed = (
        np.sum(
            (valid_values >= NDVI_THRESHOLDS["sparse_vegetation"])
            & (valid_values < NDVI_THRESHOLDS["moderate_vegetation"])
        )
        / total
        * 100
    )
    healthy = (
        np.sum(valid_values >= NDVI_THRESHOLDS["moderate_vegetation"]) / total * 100
    )

    return ZoneClassification(
        healthy_percent=healthy,
        stressed_percent=stressed,
        critical_percent=critical,
        bare_soil_percent=bare_soil,
        water_percent=water,
    )


def calculate_health_score(stats: NDVIStatistics, zones: ZoneClassification) -> float:
    """
    حساب درجة صحة النبات (0-10)
    Calculate plant health score (0-10)

    Args:
        stats: إحصائيات NDVI - NDVI statistics
        zones: تصنيف المناطق - Zone classification

    Returns:
        درجة الصحة - Health score (0-10)
    """
    # حساب الدرجة الأساسية من المتوسط
    # Calculate base score from mean
    # تحويل NDVI (-1 to 1) إلى درجة (0-10)
    # Convert NDVI (-1 to 1) to score (0-10)
    base_score = (stats.mean + 1) * 5  # Maps -1→0, 0→5, 1→10

    # تعديل بناءً على نسبة المناطق الصحية
    # Adjust based on healthy zone percentage
    healthy_bonus = zones.healthy_percent / 100 * 2  # Up to +2

    # خصم للمناطق الحرجة
    # Penalty for critical zones
    critical_penalty = zones.critical_percent / 100 * 3  # Up to -3

    # خصم للتباين العالي (يدل على عدم تجانس)
    # Penalty for high variance (indicates non-uniformity)
    variance_penalty = min(stats.std_dev * 2, 1)  # Up to -1

    # الدرجة النهائية
    # Final score
    score = base_score + healthy_bonus - critical_penalty - variance_penalty
    score = max(0.0, min(10.0, score))

    return round(score, 1)


def generate_alerts(
    stats: NDVIStatistics, zones: ZoneClassification
) -> list[NDVIAlert]:
    """
    إنشاء تنبيهات بناءً على تحليل NDVI
    Generate alerts based on NDVI analysis

    Args:
        stats: إحصائيات NDVI - NDVI statistics
        zones: تصنيف المناطق - Zone classification

    Returns:
        قائمة التنبيهات - List of alerts
    """
    alerts = []

    # تنبيه المنطقة الحرجة
    # Critical zone alert
    if zones.critical_percent > 10:
        severity = "critical" if zones.critical_percent > 30 else "high"
        alerts.append(
            NDVIAlert(
                alert_type="critical_vegetation",
                severity=severity,
                location=None,
                area_percent=zones.critical_percent,
                message_ar=f"منطقة حرجة تشكل {zones.critical_percent:.1f}% من الحقل تحتاج للفحص الفوري",
                message_en=f"Critical zone covering {zones.critical_percent:.1f}% of field requires immediate inspection",
            )
        )

    # تنبيه المنطقة المجهدة
    # Stressed zone alert
    if zones.stressed_percent > 20:
        severity = "high" if zones.stressed_percent > 40 else "medium"
        alerts.append(
            NDVIAlert(
                alert_type="stressed_vegetation",
                severity=severity,
                location=None,
                area_percent=zones.stressed_percent,
                message_ar=f"منطقة مجهدة تشكل {zones.stressed_percent:.1f}% من الحقل تحتاج للمراقبة",
                message_en=f"Stressed zone covering {zones.stressed_percent:.1f}% of field needs monitoring",
            )
        )

    # تنبيه انخفاض المتوسط
    # Low mean NDVI alert
    if stats.mean < HEALTH_THRESHOLDS["poor"]:
        alerts.append(
            NDVIAlert(
                alert_type="low_vegetation",
                severity="high",
                location=None,
                area_percent=100 - zones.healthy_percent,
                message_ar=f"متوسط NDVI منخفض ({stats.mean:.3f}) يدل على ضعف الغطاء النباتي",
                message_en=f"Low average NDVI ({stats.mean:.3f}) indicates poor vegetation cover",
            )
        )

    # تنبيه التباين العالي
    # High variance alert
    if stats.std_dev > 0.2:
        alerts.append(
            NDVIAlert(
                alert_type="non_uniform_growth",
                severity="medium",
                location=None,
                area_percent=stats.std_dev * 100,
                message_ar="تباين عالي في الغطاء النباتي يدل على نمو غير متجانس",
                message_en="High vegetation variance indicates non-uniform growth pattern",
            )
        )

    # تنبيه التربة العارية
    # Bare soil alert
    if zones.bare_soil_percent > 15:
        alerts.append(
            NDVIAlert(
                alert_type="bare_soil_exposure",
                severity="medium" if zones.bare_soil_percent < 30 else "high",
                location=None,
                area_percent=zones.bare_soil_percent,
                message_ar=f"تربة عارية تشكل {zones.bare_soil_percent:.1f}% من الحقل",
                message_en=f"Bare soil exposure covering {zones.bare_soil_percent:.1f}% of field",
            )
        )

    return alerts


def simulate_band_data(field_id: str, image_url: str) -> tuple[np.ndarray, np.ndarray]:
    """
    محاكاة بيانات النطاقات للتطوير والاختبار
    Simulate band data for development and testing

    In production, this should be replaced with actual image loading from:
    - S3/MinIO storage
    - Sentinel Hub API
    - Local GeoTIFF files

    Args:
        field_id: معرف الحقل - Field ID
        image_url: رابط الصورة - Image URL

    Returns:
        (نطاق الأحمر، نطاق NIR) - (RED band, NIR band)
    """
    # إنشاء بذرة عشوائية ثابتة للحقل للحصول على نتائج متسقة
    # Create consistent seed based on field_id for reproducible results
    seed = hash(field_id) % (2**32)
    rng = np.random.default_rng(seed)

    # حجم الصورة المحاكاة
    # Simulated image size
    height, width = 100, 100

    # محاكاة نمط نباتي واقعي
    # Simulate realistic vegetation pattern
    # إنشاء خريطة أساسية للنباتات
    # Create base vegetation map
    base_vegetation = 0.4 + 0.3 * np.sin(
        np.linspace(0, 2 * np.pi, width)
    ).reshape(1, -1)
    base_vegetation = np.tile(base_vegetation, (height, 1))

    # إضافة تباين مكاني
    # Add spatial variation
    noise = rng.normal(0, 0.1, (height, width))
    vegetation_index = base_vegetation + noise

    # إضافة بعض المناطق المجهدة
    # Add some stressed areas
    stressed_mask = rng.random((height, width)) < 0.1
    vegetation_index[stressed_mask] *= 0.5

    # تحويل إلى قيم نطاق الأحمر و NIR
    # Convert to RED and NIR band values
    # NIR يكون أعلى في المناطق الخضراء، RED يكون أقل
    # NIR is higher in green areas, RED is lower
    nir_band = 0.3 + 0.4 * np.clip(vegetation_index, 0, 1)
    red_band = 0.1 + 0.15 * (1 - np.clip(vegetation_index, 0, 1))

    # إضافة ضوضاء طفيفة
    # Add slight noise
    nir_band += rng.normal(0, 0.02, (height, width))
    red_band += rng.normal(0, 0.01, (height, width))

    # التأكد من القيم الموجبة
    # Ensure positive values
    nir_band = np.clip(nir_band, 0, 1)
    red_band = np.clip(red_band, 0, 1)

    return red_band.astype(np.float32), nir_band.astype(np.float32)


def handle_ndvi_calculation(payload: dict[str, Any]) -> dict[str, Any]:
    """
    حساب مؤشر NDVI
    Calculate NDVI index

    Args:
        payload: {
            "image_url": str - رابط الصورة / Image URL
            "field_id": str - معرف الحقل / Field ID
            "red_band": str - النطاق الأحمر / Red band (default: B4)
            "nir_band": str - النطاق تحت الأحمر القريب / NIR band (default: B8)
            "calculation_date": str - تاريخ الحساب / Calculation date
            "generate_map": bool - إنشاء خريطة / Generate map
            "statistics": bool - حساب الإحصائيات / Calculate statistics
            "red_band_data": np.ndarray - بيانات النطاق الأحمر (اختياري) / RED band data (optional)
            "nir_band_data": np.ndarray - بيانات نطاق NIR (اختياري) / NIR band data (optional)
        }

    Returns:
        {
            "ndvi_map_url": str - رابط خريطة NDVI / NDVI map URL
            "ndvi_array": np.ndarray - مصفوفة NDVI (إذا طُلب) / NDVI array (if requested)
            "statistics": dict - الإحصائيات / Statistics
            "health_score": float - درجة صحة النبات / Plant health score
            "alerts": List[dict] - التنبيهات / Alerts
            "zones": dict - تصنيف المناطق / Zone classification
        }
    """
    logger.info(f"Calculating NDVI for field: {payload.get('field_id')}")

    try:
        # استخراج البيانات من الحمولة
        # Extract data from payload
        image_url = payload.get("image_url")
        field_id = payload.get("field_id")
        red_band_name = payload.get("red_band", "B4")
        nir_band_name = payload.get("nir_band", "B8")
        payload.get("generate_map", True)
        include_array = payload.get("include_array", False)

        if not image_url or not field_id:
            raise ValueError("image_url and field_id are required")

        logger.info(
            f"Processing NDVI for field {field_id} using bands {red_band_name}/{nir_band_name}"
        )

        # =================================================================
        # Step 1: Load or simulate band data - تحميل أو محاكاة بيانات النطاقات
        # =================================================================

        # Check if band data is provided directly in payload
        # التحقق مما إذا كانت بيانات النطاقات موجودة مباشرة في الحمولة
        red_band_data = payload.get("red_band_data")
        nir_band_data = payload.get("nir_band_data")

        if red_band_data is not None and nir_band_data is not None:
            # Use provided band data - استخدام البيانات المقدمة
            logger.info("Using provided band data")
            red_band = np.array(red_band_data, dtype=np.float32)
            nir_band = np.array(nir_band_data, dtype=np.float32)
        else:
            # Simulate band data for development/testing
            # محاكاة بيانات النطاقات للتطوير/الاختبار
            # In production, replace with actual image loading from:
            # - S3/MinIO storage using boto3
            # - Sentinel Hub API using sentinelhub-py
            # - Local GeoTIFF files using rasterio
            logger.info("Simulating band data (replace with actual loader in production)")
            red_band, nir_band = simulate_band_data(field_id, image_url)

        # =================================================================
        # Step 2: Calculate NDVI - حساب NDVI
        # =================================================================

        logger.info("Calculating NDVI from bands")
        ndvi_array = calculate_ndvi_from_bands(red_band, nir_band)

        # =================================================================
        # Step 3: Calculate statistics - حساب الإحصائيات
        # =================================================================

        logger.info("Calculating NDVI statistics")
        stats = calculate_statistics(ndvi_array)

        # =================================================================
        # Step 4: Classify zones - تصنيف المناطق
        # =================================================================

        logger.info("Classifying vegetation zones")
        zones = classify_zones(ndvi_array)

        # =================================================================
        # Step 5: Calculate health score - حساب درجة الصحة
        # =================================================================

        logger.info("Calculating health score")
        health_score = calculate_health_score(stats, zones)

        # =================================================================
        # Step 6: Generate alerts - إنشاء التنبيهات
        # =================================================================

        logger.info("Generating alerts")
        alerts = generate_alerts(stats, zones)

        # =================================================================
        # Step 7: Prepare result - إعداد النتيجة
        # =================================================================

        # In production, this would save the NDVI map to S3
        # في الإنتاج، سيتم حفظ خريطة NDVI في S3
        ndvi_map_url = f"s3://sahool-ndvi/{field_id}/ndvi_map.png"

        result: dict[str, Any] = {
            "field_id": field_id,
            "ndvi_map_url": ndvi_map_url,
            "statistics": stats.to_dict(),
            "health_score": health_score,
            "alerts": [alert.to_dict() for alert in alerts],
            "zones": zones.to_dict(),
            "metadata": {
                "red_band": red_band_name,
                "nir_band": nir_band_name,
                "image_dimensions": {
                    "height": ndvi_array.shape[0],
                    "width": ndvi_array.shape[1],
                },
                "calculation_method": "standard_ndvi",
            },
        }

        # Include raw NDVI array if requested (for further processing)
        # تضمين مصفوفة NDVI الخام إذا طُلب (للمعالجة الإضافية)
        if include_array:
            result["ndvi_array"] = ndvi_array.tolist()

        logger.info(
            f"NDVI calculation completed for field: {field_id} "
            f"(score={health_score}, mean={stats.mean:.3f}, alerts={len(alerts)})"
        )

        return result

    except Exception as e:
        logger.error(f"Error calculating NDVI: {e}", exc_info=True)
        raise


# =============================================================================
# Utility Functions for External Integration - دوال مساعدة للتكامل الخارجي
# =============================================================================


def calculate_ndvi_simple(
    red_band: np.ndarray | list, nir_band: np.ndarray | list
) -> dict[str, Any]:
    """
    واجهة مبسطة لحساب NDVI
    Simplified interface for NDVI calculation

    Args:
        red_band: بيانات النطاق الأحمر - RED band data
        nir_band: بيانات نطاق NIR - NIR band data

    Returns:
        قاموس بالنتائج - Results dictionary
    """
    red = np.array(red_band, dtype=np.float32)
    nir = np.array(nir_band, dtype=np.float32)

    ndvi = calculate_ndvi_from_bands(red, nir)
    stats = calculate_statistics(ndvi)
    zones = classify_zones(ndvi)
    health_score = calculate_health_score(stats, zones)
    alerts = generate_alerts(stats, zones)

    return {
        "ndvi_array": ndvi,
        "statistics": stats.to_dict(),
        "zones": zones.to_dict(),
        "health_score": health_score,
        "alerts": [a.to_dict() for a in alerts],
    }


def get_vegetation_class(ndvi_value: float) -> str:
    """
    الحصول على فئة الغطاء النباتي لقيمة NDVI
    Get vegetation class for an NDVI value

    Args:
        ndvi_value: قيمة NDVI - NDVI value

    Returns:
        فئة الغطاء النباتي - Vegetation class name
    """
    if ndvi_value < NDVI_THRESHOLDS["water"]:
        return "water"
    elif ndvi_value < NDVI_THRESHOLDS["bare_soil"]:
        return "bare_soil"
    elif ndvi_value < NDVI_THRESHOLDS["sparse_vegetation"]:
        return "sparse_vegetation"
    elif ndvi_value < NDVI_THRESHOLDS["moderate_vegetation"]:
        return "moderate_vegetation"
    elif ndvi_value < NDVI_THRESHOLDS["dense_vegetation"]:
        return "dense_vegetation"
    else:
        return "very_dense_vegetation"
