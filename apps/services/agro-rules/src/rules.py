"""
Agro Rules - SAHOOL
Event-driven rules for automatic task generation
"""

from dataclasses import dataclass


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

    def to_tuple(self) -> tuple[str, str, str]:
        """Return (title_ar, description_ar, priority) tuple"""
        return (self.title_ar, self.description_ar, self.priority)


# ============== NDVI Rules ==============


def rule_from_ndvi(ndvi_mean: float, trend_7d: float) -> TaskRule | None:
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


def rule_from_weather(alert_type: str, severity: str) -> TaskRule | None:
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
    if alert_type == "strong_wind" and severity in ("critical", "high"):
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


# ============== NDVI Trend Rules ==============


def rule_from_ndvi_trend(
    trend_direction: str,
    anomaly_count: int,
    period_days: int,
    current_ndvi: float | None = None,
) -> TaskRule | None:
    """Generate a task from a multi-week NDVI trend summary.

    ``satellite.ndvi.trend`` events carry the direction of the linear fit
    ("increasing" / "stable" / "declining" / "volatile") across a window
    (typically 30-90 days), plus the count of detected anomalies. That's
    a slower signal than ``ndvi.computed`` — only a *sustained* decline
    or a *volatile* series should trigger an agronomic review.
    """

    # Sustained decline across the window — dominant stress signal
    if trend_direction == "declining":
        return TaskRule(
            title_ar="مراجعة اتجاه هبوط NDVI",
            title_en="Declining NDVI Trend Review",
            description_ar=(
                f"اتجاه هبوط مستمر في مؤشر الغطاء النباتي خلال {period_days} يوم "
                f"({anomaly_count} شذوذ). مراجعة الري والتسميد وصحة المحصول."
            ),
            description_en=(
                f"Sustained declining NDVI trend over {period_days} days "
                f"({anomaly_count} anomalies). Review irrigation, fertilization, "
                f"and crop health."
            ),
            task_type="inspection",
            priority="high",
            urgency_hours=24,
        )

    # Erratic series with multiple anomalies — likely pest / disease / water
    if trend_direction == "volatile" and anomaly_count >= 2:
        return TaskRule(
            title_ar="تذبذب غير طبيعي في NDVI",
            title_en="Volatile NDVI Pattern",
            description_ar=(
                f"تذبذب ملحوظ في مؤشر الغطاء النباتي ({anomaly_count} شذوذ خلال "
                f"{period_days} يوم). فحص الآفات والأمراض وانتظام الري."
            ),
            description_en=(
                f"Erratic NDVI pattern with {anomaly_count} anomalies over "
                f"{period_days} days. Inspect for pests, diseases, and irrigation uniformity."
            ),
            task_type="inspection",
            priority="medium",
            urgency_hours=48,
        )

    # Increasing / stable — no action
    return None


# ============== Phenology Rules ==============


_PHENOLOGY_STAGE_ACTIONS: dict[str, tuple[str, str, str, str, str, int]] = {
    # stage -> (title_ar, title_en, description_ar, description_en, priority, hours)
    "flowering": (
        "دعم مرحلة الإزهار",
        "Support Flowering Stage",
        "الحقل دخل مرحلة الإزهار. راجع كفاية الماء، ضع السماد البوتاسي، وتابع النحل/التلقيح.",
        "Field entered flowering. Check water sufficiency, apply potassium fertilizer, and monitor pollination.",
        "high",
        24,
    ),
    "fruiting": (
        "دعم مرحلة عقد الثمار",
        "Support Fruiting Stage",
        "الحقل في مرحلة عقد الثمار. زيادة الري، رش الكالسيوم، ومراقبة الآفات.",
        "Field is in fruiting stage. Increase irrigation, apply calcium spray, and scout for pests.",
        "high",
        24,
    ),
    "grain_filling": (
        "دعم مرحلة امتلاء الحبة",
        "Support Grain-Filling Stage",
        "الحقل في امتلاء الحبة. حافظ على انتظام الري وراقب أمراض الأوراق.",
        "Field is in grain filling. Maintain steady irrigation and monitor leaf diseases.",
        "high",
        24,
    ),
    "maturity": (
        "تحضير الحصاد",
        "Prepare Harvest",
        "المحصول اقترب من النضج. خطط لوجستيات الحصاد وتحقق من التخزين والمعدات.",
        "Crop nearing maturity. Plan harvest logistics and verify storage and equipment readiness.",
        "medium",
        72,
    ),
    "harvest_ready": (
        "جاهز للحصاد",
        "Ready for Harvest",
        "المحصول جاهز للحصاد. جدولة العمالة والمعدات خلال 48 ساعة لتفادي خسائر ما بعد النضج.",
        "Crop is ready for harvest. Schedule labor and equipment within 48h to avoid post-maturity losses.",
        "urgent",
        48,
    ),
    "senescence": (
        "نهاية الموسم",
        "End of Season",
        "المحصول في مرحلة الشيخوخة. ابدأ الحصاد أو التحضير لتجهيز التربة للموسم التالي.",
        "Crop is senescing. Begin harvest or soil preparation for the next season.",
        "medium",
        72,
    ),
}


def rule_from_phenology(
    current_stage: str,
    confidence: float,
    stage_ar: str | None = None,
    stage_en: str | None = None,
    action_template: dict | None = None,
) -> TaskRule | None:
    """Generate a task from a phenology-stage detection event.

    Preference order:
      1. Use the ``action_template`` shipped in the event (the vegetation
         service already ran the crop-aware stage-to-action mapping).
      2. Fall back to the stage->action table above for the common stages
         when no template is attached.
      3. Return None for early stages (germination, vegetative) where the
         stage transition itself is not actionable — normal NDVI rules
         already cover those.
    """
    if confidence < 0.5:
        return None

    if action_template:
        urgency = action_template.get("urgency", "medium")
        hours_map = {"critical": 6, "urgent": 12, "high": 24, "medium": 48, "low": 72}
        return TaskRule(
            title_ar=action_template.get("title_ar") or f"إجراء مرحلة: {stage_ar or current_stage}",
            title_en=action_template.get("title_en") or f"Stage action: {stage_en or current_stage}",
            description_ar=action_template.get("description_ar") or "متابعة مرحلة النمو.",
            description_en=action_template.get("description_en") or "Follow up on the growth stage.",
            task_type=action_template.get("action_type", "phenology"),
            priority=urgency if urgency in ("low", "medium", "high", "urgent") else "medium",
            urgency_hours=hours_map.get(urgency, 48),
        )

    mapping = _PHENOLOGY_STAGE_ACTIONS.get(current_stage.lower())
    if not mapping:
        return None

    title_ar, title_en, desc_ar, desc_en, priority, hours = mapping
    return TaskRule(
        title_ar=title_ar,
        title_en=title_en,
        description_ar=desc_ar,
        description_en=desc_en,
        task_type="phenology",
        priority=priority,
        urgency_hours=hours,
    )


# ============== Combined Rules ==============


def rule_from_ndvi_weather(
    ndvi_mean: float,
    ndvi_trend: float,
    temp_c: float,
    humidity_pct: float,
) -> TaskRule | None:
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
) -> TaskRule | None:
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
            description_ar=f"زيادة الري بنسبة {int((adjustment_factor - 1) * 100)}% بسبب الظروف الجوية.",
            description_en=f"Increase irrigation by {int((adjustment_factor - 1) * 100)}% due to weather conditions.",
            task_type="irrigation",
            priority="high",
            urgency_hours=6,
        )

    if adjustment_factor <= 0.6:
        return TaskRule(
            title_ar="تقليل ري - رطوبة كافية",
            title_en="Reduce Irrigation - Sufficient Moisture",
            description_ar=f"تقليل الري بنسبة {int((1 - adjustment_factor) * 100)}% بسبب الأمطار أو الرطوبة.",
            description_en=f"Reduce irrigation by {int((1 - adjustment_factor) * 100)}% due to rain or humidity.",
            task_type="irrigation",
            priority="medium",
            urgency_hours=12,
        )

    return None
