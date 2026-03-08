"""
SAHOOL Disease Detection Handler
معالج كشف الأمراض

Handles background disease detection using AI models.
يعالج كشف الأمراض في الخلفية باستخدام نماذج الذكاء الاصطناعي.

Author: SAHOOL Platform Team
License: MIT
"""

import io
import logging
import os
from datetime import UTC, datetime, timezone
from typing import Any

import httpx
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Disease Database - قاعدة بيانات الأمراض
# ═══════════════════════════════════════════════════════════════════════════════

DISEASE_DATABASE: dict[str, dict[str, Any]] = {
    "brown_leaf_spot": {
        "name_ar": "بقع الأوراق البنية",
        "name_en": "Brown Leaf Spot",
        "severity": "medium",
        "description_ar": "مرض فطري يسبب بقع بنية على الأوراق",
        "description_en": "Fungal disease causing brown spots on leaves",
        "color_indicators": {"hue_range": (10, 30), "saturation_min": 50},
        "treatments": [
            {
                "action": "رش مبيد فطري",
                "action_en": "Apply fungicide",
                "product": "Tebuconazole 250 EC",
                "dosage": "1 لتر/فدان",
                "timing": "خلال 48 ساعة",
                "priority": "high",
                "estimated_cost_sar": 450.0,
            }
        ],
    },
    "yellow_rust": {
        "name_ar": "الصدأ الأصفر",
        "name_en": "Yellow Rust",
        "severity": "high",
        "description_ar": "مرض فطري يظهر كبثور صفراء برتقالية على الأوراق",
        "description_en": "Fungal disease appearing as yellow-orange pustules on leaves",
        "color_indicators": {"hue_range": (20, 45), "saturation_min": 60},
        "treatments": [
            {
                "action": "رش مبيد فطري ترايازول",
                "action_en": "Apply triazole fungicide",
                "product": "Propiconazole 25% EC",
                "dosage": "0.5 لتر/هكتار",
                "timing": "فوراً",
                "priority": "high",
                "estimated_cost_sar": 380.0,
            }
        ],
    },
    "powdery_mildew": {
        "name_ar": "البياض الدقيقي",
        "name_en": "Powdery Mildew",
        "severity": "medium",
        "description_ar": "مرض فطري يظهر كطبقة بيضاء دقيقية على الأوراق",
        "description_en": "Fungal disease appearing as white powdery coating on leaves",
        "color_indicators": {"brightness_min": 200, "saturation_max": 30},
        "treatments": [
            {
                "action": "رش مبيد كبريتي",
                "action_en": "Apply sulfur-based fungicide",
                "product": "Sulfur 80% WP",
                "dosage": "2-3 كجم/هكتار",
                "timing": "خلال 7 أيام",
                "priority": "medium",
                "estimated_cost_sar": 200.0,
            }
        ],
    },
    "late_blight": {
        "name_ar": "اللفحة المتأخرة",
        "name_en": "Late Blight",
        "severity": "critical",
        "description_ar": "مرض فطري مدمر يسبب آفات داكنة وموت سريع للنبات",
        "description_en": "Devastating fungal disease causing dark lesions and rapid plant death",
        "color_indicators": {"hue_range": (0, 15), "brightness_max": 80},
        "treatments": [
            {
                "action": "رش مبيد نحاسي",
                "action_en": "Apply copper-based fungicide",
                "product": "Copper Hydroxide",
                "dosage": "2-3 كجم/هكتار",
                "timing": "فوراً",
                "priority": "critical",
                "estimated_cost_sar": 520.0,
            }
        ],
    },
    "nitrogen_deficiency": {
        "name_ar": "نقص النيتروجين",
        "name_en": "Nitrogen Deficiency",
        "severity": "medium",
        "description_ar": "اصفرار الأوراق القديمة بسبب نقص النيتروجين",
        "description_en": "Yellowing of older leaves due to nitrogen deficiency",
        "color_indicators": {"hue_range": (50, 70), "saturation_min": 40},
        "treatments": [
            {
                "action": "تسميد بالنيتروجين",
                "action_en": "Apply nitrogen fertilizer",
                "product": "Urea 46%",
                "dosage": "50-100 كجم/هكتار",
                "timing": "خلال أسبوع",
                "priority": "medium",
                "estimated_cost_sar": 280.0,
            }
        ],
    },
    "water_stress": {
        "name_ar": "إجهاد مائي",
        "name_en": "Water Stress",
        "severity": "high",
        "description_ar": "ذبول النبات بسبب نقص المياه",
        "description_en": "Plant wilting due to water shortage",
        "color_indicators": {"brightness_range": (60, 120), "saturation_min": 20},
        "treatments": [
            {
                "action": "ري فوري",
                "action_en": "Immediate irrigation",
                "product": "N/A",
                "dosage": "حسب احتياجات المحصول",
                "timing": "فوراً",
                "priority": "high",
                "estimated_cost_sar": 0.0,
            }
        ],
    },
    "healthy": {
        "name_ar": "نبات سليم",
        "name_en": "Healthy Plant",
        "severity": "none",
        "description_ar": "لم يتم اكتشاف أي مرض",
        "description_en": "No disease detected",
        "color_indicators": {"hue_range": (35, 85), "saturation_min": 40},
        "treatments": [],
    },
}

# Severity weights for scoring - أوزان الخطورة للتقييم
SEVERITY_WEIGHTS = {
    "none": 0,
    "low": 2,
    "medium": 5,
    "high": 7,
    "critical": 10,
}


# ═══════════════════════════════════════════════════════════════════════════════
# Image Fetching - جلب الصور
# ═══════════════════════════════════════════════════════════════════════════════


async def fetch_image_from_url(url: str, timeout: float = 30.0) -> Image.Image | None:
    """
    جلب صورة من رابط URL
    Fetch image from URL

    Args:
        url: Image URL - رابط الصورة
        timeout: Request timeout in seconds - مهلة الطلب بالثواني

    Returns:
        PIL Image or None if failed - صورة PIL أو None إذا فشل
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Load image from bytes
            image_bytes = io.BytesIO(response.content)
            image = Image.open(image_bytes).convert("RGB")
            return image

    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error fetching image from {url}: {e.response.status_code}")
        return None
    except Exception as e:
        logger.warning(f"Error fetching image from {url}: {e}")
        return None


def load_image_from_path(path: str) -> Image.Image | None:
    """
    تحميل صورة من مسار محلي
    Load image from local path

    Args:
        path: Local file path - مسار الملف المحلي

    Returns:
        PIL Image or None if failed - صورة PIL أو None إذا فشل
    """
    try:
        if os.path.exists(path):
            return Image.open(path).convert("RGB")
        return None
    except Exception as e:
        logger.warning(f"Error loading image from {path}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Image Analysis - تحليل الصور
# ═══════════════════════════════════════════════════════════════════════════════


def analyze_image_colors(image: Image.Image) -> dict[str, Any]:
    """
    تحليل ألوان الصورة للكشف عن مؤشرات المرض
    Analyze image colors to detect disease indicators

    Args:
        image: PIL Image - صورة PIL

    Returns:
        Color analysis results - نتائج تحليل الألوان
    """
    # Convert to numpy array
    img_array = np.array(image)

    # Convert RGB to HSV for better color analysis
    # Simplified HSV conversion
    r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

    # Normalize to 0-1
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    max_val = np.maximum(np.maximum(r_norm, g_norm), b_norm)
    min_val = np.minimum(np.minimum(r_norm, g_norm), b_norm)
    diff = max_val - min_val

    # Calculate Hue (0-360)
    hue = np.zeros_like(max_val)
    mask = diff != 0

    # Red is max
    red_mask = mask & (max_val == r_norm)
    hue[red_mask] = 60 * (((g_norm - b_norm) / diff) % 6)[red_mask]

    # Green is max
    green_mask = mask & (max_val == g_norm)
    hue[green_mask] = 60 * (((b_norm - r_norm) / diff) + 2)[green_mask]

    # Blue is max
    blue_mask = mask & (max_val == b_norm)
    hue[blue_mask] = 60 * (((r_norm - g_norm) / diff) + 4)[blue_mask]

    # Calculate Saturation (0-100)
    saturation = np.where(max_val != 0, (diff / max_val) * 100, 0)

    # Calculate Value/Brightness (0-255)
    brightness = max_val * 255

    # Calculate statistics
    return {
        "mean_hue": float(np.mean(hue)),
        "std_hue": float(np.std(hue)),
        "mean_saturation": float(np.mean(saturation)),
        "mean_brightness": float(np.mean(brightness)),
        "brown_ratio": float(np.mean((hue >= 10) & (hue <= 40) & (saturation > 30))),
        "yellow_ratio": float(np.mean((hue >= 40) & (hue <= 70) & (saturation > 40))),
        "green_ratio": float(np.mean((hue >= 70) & (hue <= 150) & (saturation > 30))),
        "white_ratio": float(np.mean((saturation < 20) & (brightness > 200))),
        "dark_ratio": float(np.mean(brightness < 60)),
    }


def detect_disease_from_colors(
    color_analysis: dict[str, Any],
    crop_type: str,
    confidence_threshold: float = 0.7,
) -> list[dict[str, Any]]:
    """
    كشف الأمراض من تحليل الألوان
    Detect diseases from color analysis

    Args:
        color_analysis: Color analysis results - نتائج تحليل الألوان
        crop_type: Type of crop - نوع المحصول
        confidence_threshold: Minimum confidence threshold - الحد الأدنى للثقة

    Returns:
        List of detected diseases - قائمة الأمراض المكتشفة
    """
    detections = []

    # Brown leaf spot detection
    if color_analysis["brown_ratio"] > 0.15:
        confidence = min(0.95, 0.5 + color_analysis["brown_ratio"])
        if confidence >= confidence_threshold:
            disease = DISEASE_DATABASE["brown_leaf_spot"]
            detections.append(
                {
                    "disease_id": "brown_leaf_spot",
                    "disease_name": disease["name_ar"],
                    "disease_name_en": disease["name_en"],
                    "confidence": round(confidence, 2),
                    "severity": disease["severity"],
                    "description": disease["description_en"],
                    "description_ar": disease["description_ar"],
                    "evidence": {"brown_ratio": round(color_analysis["brown_ratio"], 3)},
                }
            )

    # Yellow rust detection
    if color_analysis["yellow_ratio"] > 0.2 and color_analysis["mean_saturation"] > 50:
        confidence = min(0.92, 0.55 + color_analysis["yellow_ratio"] * 0.8)
        if confidence >= confidence_threshold:
            disease = DISEASE_DATABASE["yellow_rust"]
            detections.append(
                {
                    "disease_id": "yellow_rust",
                    "disease_name": disease["name_ar"],
                    "disease_name_en": disease["name_en"],
                    "confidence": round(confidence, 2),
                    "severity": disease["severity"],
                    "description": disease["description_en"],
                    "description_ar": disease["description_ar"],
                    "evidence": {"yellow_ratio": round(color_analysis["yellow_ratio"], 3)},
                }
            )

    # Powdery mildew detection
    if color_analysis["white_ratio"] > 0.1 and color_analysis["mean_saturation"] < 40:
        confidence = min(0.88, 0.5 + color_analysis["white_ratio"] * 2)
        if confidence >= confidence_threshold:
            disease = DISEASE_DATABASE["powdery_mildew"]
            detections.append(
                {
                    "disease_id": "powdery_mildew",
                    "disease_name": disease["name_ar"],
                    "disease_name_en": disease["name_en"],
                    "confidence": round(confidence, 2),
                    "severity": disease["severity"],
                    "description": disease["description_en"],
                    "description_ar": disease["description_ar"],
                    "evidence": {"white_ratio": round(color_analysis["white_ratio"], 3)},
                }
            )

    # Late blight detection (dark lesions)
    if color_analysis["dark_ratio"] > 0.2 and color_analysis["brown_ratio"] > 0.1:
        confidence = min(0.90, 0.5 + color_analysis["dark_ratio"])
        if confidence >= confidence_threshold:
            disease = DISEASE_DATABASE["late_blight"]
            detections.append(
                {
                    "disease_id": "late_blight",
                    "disease_name": disease["name_ar"],
                    "disease_name_en": disease["name_en"],
                    "confidence": round(confidence, 2),
                    "severity": disease["severity"],
                    "description": disease["description_en"],
                    "description_ar": disease["description_ar"],
                    "evidence": {"dark_ratio": round(color_analysis["dark_ratio"], 3)},
                }
            )

    # Nitrogen deficiency (yellowing with low green)
    if color_analysis["yellow_ratio"] > 0.25 and color_analysis["green_ratio"] < 0.3:
        confidence = min(0.85, 0.5 + color_analysis["yellow_ratio"] * 0.6)
        if confidence >= confidence_threshold:
            disease = DISEASE_DATABASE["nitrogen_deficiency"]
            detections.append(
                {
                    "disease_id": "nitrogen_deficiency",
                    "disease_name": disease["name_ar"],
                    "disease_name_en": disease["name_en"],
                    "confidence": round(confidence, 2),
                    "severity": disease["severity"],
                    "description": disease["description_en"],
                    "description_ar": disease["description_ar"],
                    "evidence": {
                        "yellow_ratio": round(color_analysis["yellow_ratio"], 3),
                        "green_ratio": round(color_analysis["green_ratio"], 3),
                    },
                }
            )

    # Water stress (low saturation, medium brightness)
    if color_analysis["mean_saturation"] < 30 and 60 < color_analysis["mean_brightness"] < 150:
        if color_analysis["green_ratio"] < 0.2:
            confidence = min(0.80, 0.5 + (1 - color_analysis["green_ratio"]) * 0.3)
            if confidence >= confidence_threshold:
                disease = DISEASE_DATABASE["water_stress"]
                detections.append(
                    {
                        "disease_id": "water_stress",
                        "disease_name": disease["name_ar"],
                        "disease_name_en": disease["name_en"],
                        "confidence": round(confidence, 2),
                        "severity": disease["severity"],
                        "description": disease["description_en"],
                        "description_ar": disease["description_ar"],
                        "evidence": {
                            "mean_saturation": round(color_analysis["mean_saturation"], 1),
                            "green_ratio": round(color_analysis["green_ratio"], 3),
                        },
                    }
                )

    # If healthy (high green ratio)
    if color_analysis["green_ratio"] > 0.5 and not detections:
        disease = DISEASE_DATABASE["healthy"]
        detections.append(
            {
                "disease_id": "healthy",
                "disease_name": disease["name_ar"],
                "disease_name_en": disease["name_en"],
                "confidence": min(0.95, 0.6 + color_analysis["green_ratio"] * 0.4),
                "severity": disease["severity"],
                "description": disease["description_en"],
                "description_ar": disease["description_ar"],
                "evidence": {"green_ratio": round(color_analysis["green_ratio"], 3)},
            }
        )

    # Sort by confidence descending
    detections.sort(key=lambda x: x["confidence"], reverse=True)

    return detections


def generate_recommendations(detections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    إنشاء توصيات العلاج من الكشوفات
    Generate treatment recommendations from detections

    Args:
        detections: List of detected diseases - قائمة الأمراض المكتشفة

    Returns:
        List of recommendations - قائمة التوصيات
    """
    recommendations = []
    seen_diseases = set()

    for detection in detections:
        disease_id = detection["disease_id"]
        if disease_id in seen_diseases or disease_id == "healthy":
            continue

        seen_diseases.add(disease_id)
        disease_info = DISEASE_DATABASE.get(disease_id, {})

        for treatment in disease_info.get("treatments", []):
            recommendations.append(
                {
                    "disease": detection["disease_name"],
                    "disease_en": detection["disease_name_en"],
                    **treatment,
                }
            )

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 4))

    return recommendations


def calculate_severity_score(detections: list[dict[str, Any]]) -> float:
    """
    حساب درجة الخطورة الإجمالية
    Calculate overall severity score

    Args:
        detections: List of detected diseases - قائمة الأمراض المكتشفة

    Returns:
        Severity score (0-10) - درجة الخطورة
    """
    if not detections:
        return 0.0

    # Calculate weighted severity score
    total_score = 0.0
    total_weight = 0.0

    for detection in detections:
        severity = detection.get("severity", "none")
        confidence = detection.get("confidence", 0.5)
        weight = SEVERITY_WEIGHTS.get(severity, 0)

        total_score += weight * confidence
        total_weight += confidence

    if total_weight == 0:
        return 0.0

    # Normalize to 0-10 scale
    return min(10.0, round(total_score / total_weight, 1))


def handle_disease_detection(payload: dict[str, Any]) -> dict[str, Any]:
    """
    كشف أمراض المحاصيل
    Detect crop diseases

    Args:
        payload: {
            "image_urls": List[str] - روابط الصور / Image URLs
            "field_id": str - معرف الحقل / Field ID
            "crop_type": str - نوع المحصول / Crop type
            "model_version": str - إصدار النموذج / Model version
            "confidence_threshold": float - حد الثقة / Confidence threshold (0-1)
            "detection_types": List[str] - أنواع الكشف / Detection types
        }

    Returns:
        {
            "detections": List[dict] - الكشوفات / Detections
            "summary": dict - الملخص / Summary
            "recommendations": List[dict] - التوصيات / Recommendations
            "severity_score": float - درجة الخطورة / Severity score
        }
    """
    logger.info(f"Detecting diseases for field: {payload.get('field_id')}")

    try:
        # استخراج البيانات من الحمولة
        # Extract data from payload
        image_urls = payload.get("image_urls", [])
        field_id = payload.get("field_id")
        crop_type = payload.get("crop_type", "unknown")
        confidence_threshold = payload.get("confidence_threshold", 0.7)
        model_version = payload.get("model_version", "v1.0.0")

        if not image_urls or not field_id:
            raise ValueError("image_urls and field_id are required")

        # ═══════════════════════════════════════════════════════════════════════
        # 1. تحميل ومعالجة الصور
        # 1. Load and process images
        # ═══════════════════════════════════════════════════════════════════════

        all_detections: list[dict[str, Any]] = []
        processed_images = 0
        failed_images = 0

        for idx, image_url in enumerate(image_urls):
            logger.debug(f"Processing image {idx + 1}/{len(image_urls)}: {image_url}")

            # Try to load image (from URL or local path)
            image = None
            if image_url.startswith(("http://", "https://")):
                # Fetch from URL using synchronous wrapper
                # Note: In production, use asyncio.run() or async context
                import asyncio

                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                image = loop.run_until_complete(fetch_image_from_url(image_url))
            else:
                # Load from local path
                image = load_image_from_path(image_url)

            if image is None:
                logger.warning(f"Failed to load image: {image_url}")
                failed_images += 1
                continue

            # ═══════════════════════════════════════════════════════════════════
            # 2. معالجة الصور مسبقاً وتحليل الألوان
            # 2. Preprocess images and analyze colors
            # ═══════════════════════════════════════════════════════════════════

            # Resize for consistent analysis
            image = image.resize((224, 224), Image.Resampling.LANCZOS)

            # Analyze image colors
            color_analysis = analyze_image_colors(image)

            # ═══════════════════════════════════════════════════════════════════
            # 3. تشغيل الاستنتاج وكشف الأمراض
            # 3. Run inference and detect diseases
            # ═══════════════════════════════════════════════════════════════════

            detections = detect_disease_from_colors(
                color_analysis=color_analysis,
                crop_type=crop_type,
                confidence_threshold=confidence_threshold,
            )

            # Add image metadata to each detection
            detection_timestamp = datetime.now(UTC).isoformat()
            for detection in detections:
                detection["image_url"] = image_url
                detection["image_index"] = idx
                detection["detected_at"] = detection_timestamp
                detection["color_analysis"] = {
                    "green_ratio": color_analysis["green_ratio"],
                    "brown_ratio": color_analysis["brown_ratio"],
                    "yellow_ratio": color_analysis["yellow_ratio"],
                }

            all_detections.extend(detections)
            processed_images += 1

        # ═══════════════════════════════════════════════════════════════════════
        # 4. تصفية النتائج وإزالة التكرار
        # 4. Filter results and deduplicate
        # ═══════════════════════════════════════════════════════════════════════

        # Filter by confidence threshold
        filtered_detections = [d for d in all_detections if d.get("confidence", 0) >= confidence_threshold]

        # Aggregate detections by disease type (keep highest confidence per disease)
        aggregated: dict[str, dict[str, Any]] = {}
        for detection in filtered_detections:
            disease_id = detection.get("disease_id", "unknown")
            if disease_id not in aggregated or detection.get("confidence", 0) > aggregated[disease_id].get(
                "confidence", 0
            ):
                aggregated[disease_id] = detection

        final_detections = list(aggregated.values())

        # Sort by confidence descending
        final_detections.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        # ═══════════════════════════════════════════════════════════════════════
        # 5. إنشاء التوصيات
        # 5. Generate recommendations
        # ═══════════════════════════════════════════════════════════════════════

        recommendations = generate_recommendations(final_detections)

        # ═══════════════════════════════════════════════════════════════════════
        # 6. حساب الملخص ودرجة الخطورة
        # 6. Calculate summary and severity score
        # ═══════════════════════════════════════════════════════════════════════

        severity_score = calculate_severity_score(final_detections)

        # Calculate severity distribution
        severity_distribution = {"none": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
        for detection in final_detections:
            severity = detection.get("severity", "none")
            if severity in severity_distribution:
                severity_distribution[severity] += 1

        # Determine risk level based on severity score
        if severity_score >= 8:
            risk_level = "critical"
        elif severity_score >= 6:
            risk_level = "high"
        elif severity_score >= 4:
            risk_level = "medium"
        elif severity_score >= 2:
            risk_level = "low"
        else:
            risk_level = "none"

        # Find most common disease
        disease_counts: dict[str, int] = {}
        for detection in all_detections:
            disease_id = detection.get("disease_id", "unknown")
            if disease_id != "healthy":
                disease_counts[disease_id] = disease_counts.get(disease_id, 0) + 1

        most_common_disease = None
        if disease_counts:
            most_common_id = max(disease_counts, key=disease_counts.get)  # type: ignore[arg-type]
            most_common_info = DISEASE_DATABASE.get(most_common_id, {})
            most_common_disease = most_common_info.get("name_ar", most_common_id)

        # Calculate next inspection date based on risk level
        from datetime import timedelta

        inspection_days = {"critical": 1, "high": 3, "medium": 7, "low": 14, "none": 30}
        next_inspection = datetime.now(UTC) + timedelta(days=inspection_days.get(risk_level, 14))

        # ═══════════════════════════════════════════════════════════════════════
        # 7. بناء النتيجة النهائية
        # 7. Build final result
        # ═══════════════════════════════════════════════════════════════════════

        result = {
            "detections": final_detections,
            "summary": {
                "total_detections": len(final_detections),
                "processed_images": processed_images,
                "failed_images": failed_images,
                "severity_distribution": severity_distribution,
                "most_common_disease": most_common_disease,
                "field_id": field_id,
                "crop_type": crop_type,
                "model_version": model_version,
            },
            "recommendations": recommendations,
            "severity_score": severity_score,
            "risk_level": risk_level,
            "next_inspection_date": next_inspection.isoformat(),
            "analysis_timestamp": datetime.now(UTC).isoformat(),
        }

        logger.info(
            f"Disease detection completed for field: {field_id} "
            f"(detections={len(final_detections)}, severity={severity_score}, risk={risk_level})"
        )
        return result

    except Exception as e:
        logger.error(f"Error detecting diseases: {e}", exc_info=True)
        raise
