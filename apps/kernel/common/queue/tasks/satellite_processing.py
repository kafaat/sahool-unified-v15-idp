"""
SAHOOL Satellite Image Processing Handler
معالج معالجة صور الأقمار الصناعية

Handles background processing of satellite imagery.
يعالج معالجة صور الأقمار الصناعية في الخلفية.

Processing Steps:
1. Download/load image from URL
2. Extract required spectral bands
3. Apply atmospheric and geometric corrections
4. Crop image to field boundaries
5. Calculate vegetation indices (NDVI, EVI, SAVI, etc.)
6. Generate statistics and quality metrics
7. Save processed outputs

Supported Satellites:
- Sentinel-2 (10m resolution): B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12
- Landsat 8/9 (30m resolution): B2, B3, B4, B5, B6, B7
- MODIS (250m resolution): B1, B2

Author: SAHOOL Platform Team
License: MIT
"""

import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timezone
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# ======================================================================
# Constants - الثوابت
# ======================================================================

# Satellite band mappings for NDVI calculation
# تعيينات نطاقات الأقمار الصناعية لحساب NDVI
SATELLITE_BANDS = {
    "Sentinel-2": {"red": "B4", "nir": "B8", "resolution": 10},
    "Landsat-8": {"red": "B4", "nir": "B5", "resolution": 30},
    "Landsat-9": {"red": "B4", "nir": "B5", "resolution": 30},
    "MODIS": {"red": "B1", "nir": "B2", "resolution": 250},
}

# Cloud coverage thresholds - عتبات الغطاء السحابي
MAX_CLOUD_COVERAGE_PERCENT = 30  # Maximum acceptable cloud coverage


# ======================================================================
# Data Classes - فئات البيانات
# ======================================================================


@dataclass
class BandData:
    """بيانات النطاق الطيفي - Spectral Band Data"""

    name: str
    data: np.ndarray
    wavelength_nm: float
    resolution_m: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "wavelength_nm": self.wavelength_nm,
            "resolution_m": self.resolution_m,
            "shape": list(self.data.shape),
            "min": float(np.nanmin(self.data)),
            "max": float(np.nanmax(self.data)),
        }


@dataclass
class VegetationIndices:
    """مؤشرات الغطاء النباتي - Vegetation Indices"""

    ndvi: float  # Normalized Difference Vegetation Index
    ndvi_min: float
    ndvi_max: float
    ndvi_std: float
    evi: float | None = None  # Enhanced Vegetation Index
    savi: float | None = None  # Soil Adjusted Vegetation Index
    ndwi: float | None = None  # Normalized Difference Water Index

    def to_dict(self) -> dict[str, Any]:
        result = {
            "ndvi": round(self.ndvi, 4),
            "ndvi_min": round(self.ndvi_min, 4),
            "ndvi_max": round(self.ndvi_max, 4),
            "ndvi_std": round(self.ndvi_std, 4),
        }
        if self.evi is not None:
            result["evi"] = round(self.evi, 4)
        if self.savi is not None:
            result["savi"] = round(self.savi, 4)
        if self.ndwi is not None:
            result["ndwi"] = round(self.ndwi, 4)
        return result


@dataclass
class ProcessingResult:
    """نتيجة المعالجة - Processing Result"""

    success: bool
    field_id: str
    indices: VegetationIndices | None
    cloud_coverage: float
    valid_pixels_percent: float
    processing_duration_sec: float
    output_url: str | None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "field_id": self.field_id,
            "indices": self.indices.to_dict() if self.indices else None,
            "cloud_coverage": round(self.cloud_coverage, 2),
            "valid_pixels_percent": round(self.valid_pixels_percent, 2),
            "processing_duration_sec": round(self.processing_duration_sec, 3),
            "output_url": self.output_url,
            "error_message": self.error_message,
        }


# ======================================================================
# Processing Functions - دوال المعالجة
# ======================================================================


def simulate_band_download(image_url: str, field_id: str, bands: list[str], satellite_type: str) -> dict[str, BandData]:
    """
    محاكاة تحميل نطاقات الصورة (للتطوير/الاختبار)
    Simulate downloading image bands (for development/testing)

    In production, replace with actual image download from:
    - Sentinel Hub API
    - Google Earth Engine
    - AWS Open Data Registry
    - Local GeoTIFF files

    Args:
        image_url: رابط الصورة - Image URL
        field_id: معرف الحقل - Field ID
        bands: قائمة النطاقات المطلوبة - List of required bands
        satellite_type: نوع القمر الصناعي - Satellite type

    Returns:
        قاموس بيانات النطاقات - Dictionary of band data
    """
    logger.info(f"Downloading bands {bands} from {image_url}")

    # Create consistent random seed based on field_id
    # إنشاء بذرة عشوائية ثابتة بناءً على معرف الحقل
    seed = hash(field_id) % (2**32)
    rng = np.random.default_rng(seed)

    # Simulated image dimensions based on satellite resolution
    # أبعاد الصورة المحاكاة بناءً على دقة القمر الصناعي
    resolution = SATELLITE_BANDS.get(satellite_type, {}).get("resolution", 10)
    # Smaller dimensions for lower resolution satellites
    dim_factor = max(1, 30 // resolution)
    height, width = 100 * dim_factor, 100 * dim_factor

    band_wavelengths = {
        "B2": 490,  # Blue
        "B3": 560,  # Green
        "B4": 665,  # Red
        "B5": 705,  # Red Edge 1
        "B6": 740,  # Red Edge 2
        "B7": 783,  # Red Edge 3
        "B8": 842,  # NIR
        "B8A": 865,  # NIR Narrow
        "B11": 1610,  # SWIR1
        "B12": 2190,  # SWIR2
    }

    band_data = {}
    for band_name in bands:
        # Generate realistic reflectance values (0-1)
        # توليد قيم انعكاسية واقعية (0-1)
        if band_name in ["B8", "B8A", "B5"]:  # NIR bands - higher for vegetation
            base_value = 0.35 + rng.random((height, width)) * 0.3
        elif band_name == "B4":  # Red band - lower for vegetation
            base_value = 0.05 + rng.random((height, width)) * 0.15
        else:
            base_value = 0.1 + rng.random((height, width)) * 0.2

        # Add spatial variation to simulate vegetation patterns
        # إضافة تباين مكاني لمحاكاة أنماط الغطاء النباتي
        x = np.linspace(0, 2 * np.pi, width)
        y = np.linspace(0, 2 * np.pi, height)
        xx, yy = np.meshgrid(x, y)
        spatial_pattern = 0.1 * np.sin(xx) * np.cos(yy)
        base_value += spatial_pattern

        # Clip to valid range
        data = np.clip(base_value, 0, 1).astype(np.float32)

        band_data[band_name] = BandData(
            name=band_name,
            data=data,
            wavelength_nm=band_wavelengths.get(band_name, 0),
            resolution_m=resolution,
        )

    return band_data


def apply_atmospheric_correction(band_data: dict[str, BandData]) -> dict[str, BandData]:
    """
    تطبيق التصحيح الجوي (محاكاة)
    Apply atmospheric correction (simulation)

    In production, use:
    - Sen2Cor for Sentinel-2
    - LaSRC for Landsat
    - MODIS Surface Reflectance products

    Args:
        band_data: بيانات النطاقات الخام - Raw band data

    Returns:
        بيانات النطاقات المصححة - Corrected band data
    """
    logger.info("Applying atmospheric correction")

    corrected_data = {}
    for band_name, band in band_data.items():
        # Simple atmospheric correction simulation
        # تصحيح جوي بسيط محاكى
        # Reduce haze effect (subtract small constant and scale)
        corrected = (band.data - 0.01) * 1.05
        corrected = np.clip(corrected, 0, 1).astype(np.float32)

        corrected_data[band_name] = BandData(
            name=band.name,
            data=corrected,
            wavelength_nm=band.wavelength_nm,
            resolution_m=band.resolution_m,
        )

    return corrected_data


def detect_clouds(band_data: dict[str, BandData]) -> tuple[np.ndarray, float]:
    """
    كشف السحب في الصورة
    Detect clouds in the image

    Uses simple threshold-based detection. In production, use:
    - S2Cloudless for Sentinel-2
    - FMask for Landsat
    - MODIS Cloud Mask products

    Args:
        band_data: بيانات النطاقات - Band data

    Returns:
        (قناع السحب، نسبة التغطية السحابية) - (Cloud mask, cloud coverage percentage)
    """
    logger.info("Detecting clouds")

    # Use blue band for simple cloud detection (clouds are bright in blue)
    # استخدام النطاق الأزرق للكشف البسيط عن السحب
    if "B2" in band_data:
        blue = band_data["B2"].data
    elif "B4" in band_data:  # Fallback to red band
        blue = band_data["B4"].data * 1.2
    else:
        # Return empty mask if no suitable band
        first_band = next(iter(band_data.values()))
        return np.zeros_like(first_band.data, dtype=bool), 0.0

    # Simple threshold: bright pixels are likely clouds
    # عتبة بسيطة: البكسلات الساطعة على الأرجح سحب
    cloud_threshold = 0.35
    cloud_mask = blue > cloud_threshold

    # Calculate cloud coverage percentage
    cloud_coverage = (np.sum(cloud_mask) / cloud_mask.size) * 100

    return cloud_mask, float(cloud_coverage)


def crop_to_field_boundary(band_data: dict[str, BandData], field_geometry: dict | None) -> dict[str, BandData]:
    """
    قص الصورة حسب حدود الحقل
    Crop image to field boundary

    Args:
        band_data: بيانات النطاقات - Band data
        field_geometry: هندسة الحقل (GeoJSON) - Field geometry (GeoJSON)

    Returns:
        بيانات النطاقات المقصوصة - Cropped band data
    """
    logger.info("Cropping image to field boundary")

    # In production, use rasterio.mask.mask() with shapely geometry
    # في الإنتاج، استخدم rasterio.mask.mask() مع هندسة shapely

    # For simulation, just return the original data
    # للمحاكاة، نعيد البيانات الأصلية فقط
    if field_geometry is None:
        return band_data

    # Simulated crop - could extract a central region
    # قص محاكى - يمكن استخراج منطقة مركزية
    return band_data


def calculate_vegetation_indices(band_data: dict[str, BandData]) -> VegetationIndices:
    """
    حساب مؤشرات الغطاء النباتي
    Calculate vegetation indices

    Calculates:
    - NDVI: (NIR - RED) / (NIR + RED)
    - EVI: 2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1)
    - SAVI: ((NIR - RED) / (NIR + RED + L)) * (1 + L), L=0.5

    Args:
        band_data: بيانات النطاقات - Band data

    Returns:
        مؤشرات الغطاء النباتي - Vegetation indices
    """
    logger.info("Calculating vegetation indices")

    # Get RED and NIR bands - الحصول على نطاقي الأحمر والأشعة تحت الحمراء
    red = None
    nir = None

    # Try different band naming conventions
    for red_name in ["B4", "B3"]:
        if red_name in band_data:
            red = band_data[red_name].data
            break

    for nir_name in ["B8", "B8A", "B5", "B2"]:
        if nir_name in band_data:
            nir = band_data[nir_name].data
            break

    if red is None or nir is None:
        raise ValueError("Required bands (RED, NIR) not found in data")

    # Calculate NDVI - حساب NDVI
    denominator = nir + red
    ndvi = np.zeros_like(denominator)
    np.divide(nir - red, denominator, out=ndvi, where=denominator != 0)
    ndvi = np.clip(ndvi, -1, 1)

    # Filter valid pixels (excluding clouds, water, etc.)
    valid_mask = np.isfinite(ndvi) & (ndvi > -0.5)
    valid_ndvi = ndvi[valid_mask]

    if len(valid_ndvi) == 0:
        valid_ndvi = np.array([0.0])

    # Calculate NDVI statistics - حساب إحصائيات NDVI
    ndvi_mean = float(np.mean(valid_ndvi))
    ndvi_min = float(np.min(valid_ndvi))
    ndvi_max = float(np.max(valid_ndvi))
    ndvi_std = float(np.std(valid_ndvi))

    # Calculate EVI if blue band available - حساب EVI إذا توفر النطاق الأزرق
    evi_mean = None
    if "B2" in band_data:
        blue = band_data["B2"].data
        evi_denom = nir + 6 * red - 7.5 * blue + 1
        evi = np.zeros_like(evi_denom)
        np.divide(2.5 * (nir - red), evi_denom, out=evi, where=evi_denom != 0)
        evi = np.clip(evi, -1, 1)
        valid_evi = evi[valid_mask]
        if len(valid_evi) > 0:
            evi_mean = float(np.mean(valid_evi))

    # Calculate SAVI - حساب SAVI
    L = 0.5  # Soil brightness correction factor
    savi_denom = nir + red + L
    savi = np.zeros_like(savi_denom)
    np.divide((nir - red) * (1 + L), savi_denom, out=savi, where=savi_denom != 0)
    savi = np.clip(savi, -1, 1)
    valid_savi = savi[valid_mask]
    savi_mean = float(np.mean(valid_savi)) if len(valid_savi) > 0 else None

    # Calculate NDWI if SWIR band available - حساب NDWI إذا توفر نطاق SWIR
    ndwi_mean = None
    if "B11" in band_data:
        swir = band_data["B11"].data
        ndwi_denom = nir + swir
        ndwi = np.zeros_like(ndwi_denom)
        np.divide(nir - swir, ndwi_denom, out=ndwi, where=ndwi_denom != 0)
        ndwi = np.clip(ndwi, -1, 1)
        valid_ndwi = ndwi[valid_mask]
        if len(valid_ndwi) > 0:
            ndwi_mean = float(np.mean(valid_ndwi))

    return VegetationIndices(
        ndvi=ndvi_mean,
        ndvi_min=ndvi_min,
        ndvi_max=ndvi_max,
        ndvi_std=ndvi_std,
        evi=evi_mean,
        savi=savi_mean,
        ndwi=ndwi_mean,
    )


def save_processed_image(field_id: str, indices: VegetationIndices, output_format: str) -> str:
    """
    حفظ الصورة المعالجة
    Save processed image

    In production, save to:
    - S3/MinIO bucket
    - Local GeoTIFF file
    - Cloud storage

    Args:
        field_id: معرف الحقل - Field ID
        indices: مؤشرات الغطاء النباتي - Vegetation indices
        output_format: تنسيق الإخراج - Output format

    Returns:
        رابط الصورة المحفوظة - Saved image URL
    """
    logger.info(f"Saving processed image in {output_format} format")

    # Generate output URL (simulated)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_url = f"s3://sahool-satellite/{field_id}/{timestamp}_processed.{output_format.lower()}"

    # In production, use rasterio to save GeoTIFF:
    # with rasterio.open(output_path, 'w', **profile) as dst:
    #     dst.write(data, 1)

    return output_url


def process_satellite_image(payload: dict[str, Any]) -> ProcessingResult:
    """
    معالجة صورة القمر الصناعي بالكامل
    Process satellite image completely

    Args:
        payload: حمولة المعالجة - Processing payload

    Returns:
        نتيجة المعالجة - Processing result
    """
    start_time = time.time()
    field_id = payload.get("field_id", "unknown")

    try:
        image_url = payload.get("image_url")
        satellite_type = payload.get("satellite_type", "Sentinel-2")
        bands = payload.get("bands", ["B4", "B8"])
        output_format = payload.get("output_format", "GeoTIFF")
        field_geometry = payload.get("field_geometry")

        # Step 1: Download/load bands - تحميل النطاقات
        logger.info(f"Step 1: Downloading bands for {satellite_type}")
        band_data = simulate_band_download(image_url, field_id, bands, satellite_type)

        # Step 2: Apply atmospheric correction - تطبيق التصحيح الجوي
        logger.info("Step 2: Applying atmospheric correction")
        corrected_data = apply_atmospheric_correction(band_data)

        # Step 3: Detect clouds - كشف السحب
        logger.info("Step 3: Detecting clouds")
        cloud_mask, cloud_coverage = detect_clouds(corrected_data)

        # Check cloud coverage threshold
        if cloud_coverage > MAX_CLOUD_COVERAGE_PERCENT:
            logger.warning(f"High cloud coverage ({cloud_coverage:.1f}%) - results may be unreliable")

        # Step 4: Crop to field boundary - قص حسب حدود الحقل
        logger.info("Step 4: Cropping to field boundary")
        cropped_data = crop_to_field_boundary(corrected_data, field_geometry)

        # Step 5: Calculate vegetation indices - حساب مؤشرات الغطاء النباتي
        logger.info("Step 5: Calculating vegetation indices")
        indices = calculate_vegetation_indices(cropped_data)

        # Step 6: Calculate valid pixels percentage - حساب نسبة البكسلات الصالحة
        first_band = next(iter(cropped_data.values()))
        total_pixels = first_band.data.size
        valid_pixels = np.sum(~cloud_mask)
        valid_pixels_percent = (valid_pixels / total_pixels) * 100

        # Step 7: Save processed image - حفظ الصورة المعالجة
        logger.info("Step 6: Saving processed image")
        output_url = save_processed_image(field_id, indices, output_format)

        processing_duration = time.time() - start_time

        return ProcessingResult(
            success=True,
            field_id=field_id,
            indices=indices,
            cloud_coverage=cloud_coverage,
            valid_pixels_percent=valid_pixels_percent,
            processing_duration_sec=processing_duration,
            output_url=output_url,
        )

    except Exception as e:
        processing_duration = time.time() - start_time
        logger.error(f"Processing failed: {e}", exc_info=True)
        return ProcessingResult(
            success=False,
            field_id=field_id,
            indices=None,
            cloud_coverage=0.0,
            valid_pixels_percent=0.0,
            processing_duration_sec=processing_duration,
            output_url=None,
            error_message=str(e),
        )


def handle_satellite_image_processing(payload: dict[str, Any]) -> dict[str, Any]:
    """
    معالجة صورة القمر الصناعي
    Process satellite image

    This is the main entry point for satellite image processing tasks.
    It processes satellite imagery data, calculates vegetation indices (NDVI, EVI, SAVI),
    applies atmospheric corrections, and stores results.

    Args:
        payload: {
            "image_url": str - رابط الصورة / Image URL
            "field_id": str - معرف الحقل / Field ID
            "satellite_type": str - نوع القمر الصناعي / Satellite type (Sentinel-2, Landsat, etc.)
            "acquisition_date": str - تاريخ الالتقاط / Acquisition date
            "processing_level": str - مستوى المعالجة / Processing level (L1C, L2A, etc.)
            "bands": List[str] - النطاقات المطلوبة / Required bands
            "output_format": str - تنسيق الإخراج / Output format (GeoTIFF, etc.)
            "field_geometry": dict - هندسة الحقل / Field geometry (GeoJSON, optional)
        }

    Returns:
        {
            "processed_image_url": str - رابط الصورة المعالجة / Processed image URL
            "metadata": dict - البيانات الوصفية / Metadata
            "processing_time": float - وقت المعالجة / Processing time
            "status": str - الحالة / Status
            "vegetation_indices": dict - مؤشرات الغطاء النباتي / Vegetation indices
        }
    """
    logger.info(f"Processing satellite image for field: {payload.get('field_id')}")

    try:
        # ==========================================================
        # Step 1: Validate input - التحقق من صحة الإدخال
        # ==========================================================
        image_url = payload.get("image_url")
        field_id = payload.get("field_id")
        satellite_type = payload.get("satellite_type", "Sentinel-2")
        bands = payload.get("bands", ["B4", "B8"])  # Default: Red, NIR

        if not image_url or not field_id:
            raise ValueError("image_url and field_id are required")

        logger.info(f"Starting satellite processing: field={field_id}, satellite={satellite_type}, bands={bands}")

        # ==========================================================
        # Step 2: Execute processing pipeline - تنفيذ خط المعالجة
        # ==========================================================
        # The process_satellite_image function handles:
        # 1. Download/load image from URL - تحميل الصورة من URL
        # 2. Extract required bands - استخراج النطاقات المطلوبة
        # 3. Apply atmospheric correction - تطبيق التصحيح الجوي
        # 4. Detect and mask clouds - كشف السحب وإخفاؤها
        # 5. Crop to field boundaries - قص حسب حدود الحقل
        # 6. Calculate vegetation indices - حساب مؤشرات الغطاء النباتي
        # 7. Save processed image - حفظ الصورة المعالجة

        processing_result = process_satellite_image(payload)

        # ==========================================================
        # Step 3: Prepare response - إعداد الاستجابة
        # ==========================================================
        if not processing_result.success:
            logger.error(f"Satellite processing failed for field {field_id}: {processing_result.error_message}")
            raise RuntimeError(processing_result.error_message)

        # Get satellite resolution - الحصول على دقة القمر الصناعي
        resolution = SATELLITE_BANDS.get(satellite_type, {}).get("resolution", 10)

        result = {
            "processed_image_url": processing_result.output_url,
            "metadata": {
                "satellite_type": satellite_type,
                "bands": bands,
                "resolution": f"{resolution}m",
                "cloud_coverage": processing_result.cloud_coverage,
                "valid_pixels_percent": processing_result.valid_pixels_percent,
                "processing_level": payload.get("processing_level", "L2A"),
                "acquisition_date": payload.get("acquisition_date"),
            },
            "processing_time": processing_result.processing_duration_sec,
            "status": "success",
            "vegetation_indices": (processing_result.indices.to_dict() if processing_result.indices else None),
        }

        logger.info(
            f"Satellite image processed successfully for field: {field_id} "
            f"(NDVI={processing_result.indices.ndvi:.3f}, "
            f"cloud_coverage={processing_result.cloud_coverage:.1f}%, "
            f"processing_time={processing_result.processing_duration_sec:.2f}s)"
        )

        return result

    except Exception as e:
        logger.error(f"Error processing satellite image: {e}", exc_info=True)
        raise
