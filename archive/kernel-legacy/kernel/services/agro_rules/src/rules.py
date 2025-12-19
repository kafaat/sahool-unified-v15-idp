"""
Agro Rules - SAHOOL
Event-driven rules for automatic task generation
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class TaskRule:
    """Task generation rule result"""

    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    task_type: str
    priority: str
    urgency_hours: int

    def to_tuple(self) -> Tuple[str, str, str]:
        """Return (title_ar, description_ar, priority) tuple"""
        return (self.title_ar, self.description_ar, self.priority)


# ============== NDVI Rules ==============


def rule_from_ndvi(ndvi_mean: float, trend_7d: float) -> Optional[TaskRule]:
    """
    Generate task from NDVI data

    Args:
        ndvi_mean: Current NDVI value (0-1)
        trend_7d: 7-day NDVI trend (negative = decline)

    Returns:
        TaskRule if action needed, None otherwise
    """
    # Severe NDVI drop
    if trend_7d <= -0.15:
        return TaskRule(
            title_ar="فحص طارئ - هبوط حاد في NDVI",
            title_en="Emergency Inspection - Sharp NDVI Drop",
            description_ar=f"انخفاض حاد في مؤشر الغطاء النباتي ({trend_7d:.2f}) خلال أسبوع. فحص فوري للآفات والأمراض والري.",
            description_en=f"Sharp vegetation index drop ({trend_7d:.2f}) in one week. Immediate inspection for pests, diseases, and irrigation.",
            task_type="inspection",
            priority="urgent",
            urgency_hours=6,
        )

    # Moderate NDVI drop
    if trend_7d <= -0.10:
        return TaskRule(
            title_ar="فحص هبوط NDVI",
            title_en="NDVI Drop Inspection",
            description_ar=f"هبوط ملحوظ في مؤشر الغطاء النباتي ({trend_7d:.2f}) خلال أسبوع. راجع الري والآفات.",
            description_en=f"Notable vegetation index drop ({trend_7d:.2f}) in one week. Check irrigation and pests.",
            task_type="inspection",
            priority="high",
            urgency_hours=24,
        )

    # Very low NDVI
    if ndvi_mean < 0.2:
        return TaskRule(
            title_ar="تحذير NDVI منخفض جداً",
            title_en="Very Low NDVI Warning",
            description_ar=f"مؤشر الغطاء النباتي ({ndvi_mean:.2f}) منخفض جداً. فحص صحة المحصول.",
            description_en=f"Vegetation index ({ndvi_mean:.2f}) is very low. Check crop health.",
            task_type="inspection",
            priority="high",
            urgency_hours=24,
        )

    # Low NDVI
    if ndvi_mean < 0.35:
        return TaskRule(
            title_ar="متابعة NDVI منخفض",
            title_en="Low NDVI Follow-up",
            description_ar=f"مؤشر الغطاء النباتي ({ndvi_mean:.2f}) أقل من المتوسط. مراجعة التسميد والري.",
            description_en=f"Vegetation index ({ndvi_mean:.2f}) below average. Review fertilization and irrigation.",
            task_type="inspection",
            priority="medium",
            urgency_hours=48,
        )

    # Positive trend - good news, no task needed
    if trend_7d >= 0.05 and ndvi_mean >= 0.5:
        return None  # Healthy crop, no action needed

    return None


# ============== Weather Rules ==============


def rule_from_weather(alert_type: str, severity: str) -> Optional[TaskRule]:
    """
    Generate task from weather alert

    Args:
        alert_type: Type of weather alert
        severity: Alert severity (low, medium, high, critical)

    Returns:
        TaskRule if action needed, None otherwise
    """
    if severity == "none" or severity == "low":
        return None

    # Heat stress
    if alert_type == "heat_stress":
        if severity == "critical":
            return TaskRule(
                title_ar="طوارئ موجة حر",
                title_en="Heat Wave Emergency",
                description_ar="موجة حر شديدة! تفعيل الري الطارئ والتظليل فوراً.",
                description_en="Severe heat wave! Activate emergency irrigation and shading immediately.",
                task_type="emergency",
                priority="urgent",
                urgency_hours=2,
            )
        elif severity == "high":
            return TaskRule(
                title_ar="تنبيه موجة حر",
                title_en="Heat Stress Alert",
                description_ar="تأكيد جاهزية الري وتقليل إجهاد المحصول خلال 24 ساعة.",
                description_en="Ensure irrigation readiness and reduce crop stress within 24 hours.",
                task_type="irrigation",
                priority="urgent",
                urgency_hours=6,
            )
        else:  # medium
            return TaskRule(
                title_ar="متابعة حرارة مرتفعة",
                title_en="High Temperature Follow-up",
                description_ar="مراقبة المحصول للإجهاد الحراري وزيادة الري إن لزم.",
                description_en="Monitor crops for heat stress and increase irrigation if needed.",
                task_type="monitoring",
                priority="high",
                urgency_hours=12,
            )

    # Frost
    if alert_type == "frost":
        if severity in ("critical", "high"):
            return TaskRule(
                title_ar="طوارئ صقيع",
                title_en="Frost Emergency",
                description_ar="خطر صقيع! تغطية المحاصيل الحساسة والري الوقائي.",
                description_en="Frost risk! Cover sensitive crops and apply protective irrigation.",
                task_type="emergency",
                priority="urgent",
                urgency_hours=2,
            )
        else:
            return TaskRule(
                title_ar="تحذير برودة",
                title_en="Cold Warning",
                description_ar="تحضير وسائل الحماية من الصقيع.",
                description_en="Prepare frost protection measures.",
                task_type="preparation",
                priority="high",
                urgency_hours=6,
            )

    # Heavy rain
    if alert_type == "heavy_rain":
        if severity in ("critical", "high"):
            return TaskRule(
                title_ar="تحذير أمطار غزيرة",
                title_en="Heavy Rain Warning",
                description_ar="أمطار غزيرة متوقعة. تحسين الصرف وحماية المحاصيل.",
                description_en="Heavy rain expected. Improve drainage and protect crops.",
                task_type="preparation",
                priority="high",
                urgency_hours=6,
            )
        else:
            return TaskRule(
                title_ar="متابعة أمطار",
                title_en="Rain Follow-up",
                description_ar="فحص الصرف بعد الأمطار.",
                description_en="Check drainage after rain.",
                task_type="inspection",
                priority="medium",
                urgency_hours=24,
            )

    # Strong wind
    if alert_type == "strong_wind":
        if severity in ("critical", "high"):
            return TaskRule(
                title_ar="تحذير رياح قوية",
                title_en="Strong Wind Warning",
                description_ar="رياح قوية متوقعة. تأمين المعدات ودعم النباتات.",
                description_en="Strong winds expected. Secure equipment and support plants.",
                task_type="preparation",
                priority="high",
                urgency_hours=4,
            )

    # Disease risk
    if alert_type == "disease_risk":
        if severity in ("critical", "high"):
            return TaskRule(
                title_ar="تحذير خطر أمراض",
                title_en="Disease Risk Warning",
                description_ar="ظروف مناسبة للأمراض الفطرية. فحص وقائي ورش إن لزم.",
                description_en="Conditions favorable for fungal diseases. Preventive inspection and spray if needed.",
                task_type="inspection",
                priority="high",
                urgency_hours=12,
            )
        else:
            return TaskRule(
                title_ar="مراقبة خطر أمراض",
                title_en="Disease Risk Monitoring",
                description_ar="مراقبة النباتات لأعراض الأمراض.",
                description_en="Monitor plants for disease symptoms.",
                task_type="monitoring",
                priority="medium",
                urgency_hours=24,
            )

    return None


# ============== Combined Rules ==============


def rule_from_ndvi_weather(
    ndvi_mean: float,
    ndvi_trend: float,
    temp_c: float,
    humidity_pct: float,
) -> Optional[TaskRule]:
    """
    Combined NDVI + Weather rule

    Detects compound stress situations
    """
    # Heat + NDVI decline = severe stress
    if temp_c >= 35 and ndvi_trend <= -0.08:
        return TaskRule(
            title_ar="إجهاد مركب - حرارة + هبوط NDVI",
            title_en="Compound Stress - Heat + NDVI Drop",
            description_ar="إجهاد حراري مع انخفاض الغطاء النباتي. ري طارئ وفحص فوري.",
            description_en="Heat stress combined with vegetation decline. Emergency irrigation and immediate inspection.",
            task_type="emergency",
            priority="urgent",
            urgency_hours=4,
        )

    # High humidity + Low NDVI = disease + weakness
    if humidity_pct >= 80 and ndvi_mean < 0.4:
        return TaskRule(
            title_ar="خطر مرض + ضعف نبات",
            title_en="Disease Risk + Weak Plants",
            description_ar="رطوبة عالية مع ضعف النباتات. رش وقائي وتحسين تهوية.",
            description_en="High humidity with weak plants. Preventive spray and improve ventilation.",
            task_type="spray",
            priority="high",
            urgency_hours=12,
        )

    return None


# ============== Irrigation Adjustment Rules ==============


def rule_from_irrigation_adjustment(
    adjustment_factor: float,
    field_id: str,
) -> Optional[TaskRule]:
    """
    Generate task from irrigation adjustment

    Args:
        adjustment_factor: Multiplier for irrigation (1.0 = normal)
        field_id: Field identifier

    Returns:
        TaskRule if significant adjustment needed
    """
    if adjustment_factor >= 1.3:
        return TaskRule(
            title_ar="زيادة ري - ظروف جفاف",
            title_en="Increase Irrigation - Dry Conditions",
            description_ar=f"زيادة الري بنسبة {int((adjustment_factor-1)*100)}% بسبب الظروف الجوية.",
            description_en=f"Increase irrigation by {int((adjustment_factor-1)*100)}% due to weather conditions.",
            task_type="irrigation",
            priority="high",
            urgency_hours=6,
        )

    if adjustment_factor <= 0.6:
        return TaskRule(
            title_ar="تقليل ري - رطوبة كافية",
            title_en="Reduce Irrigation - Sufficient Moisture",
            description_ar=f"تقليل الري بنسبة {int((1-adjustment_factor)*100)}% بسبب الأمطار أو الرطوبة.",
            description_en=f"Reduce irrigation by {int((1-adjustment_factor)*100)}% due to rain or humidity.",
            task_type="irrigation",
            priority="medium",
            urgency_hours=12,
        )

    return None
