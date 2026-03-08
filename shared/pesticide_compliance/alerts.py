"""
Pesticide Compliance Alerts - تنبيهات امتثال المبيدات
Generate alerts for compliance violations
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .models import (
    ComplianceStatus,
    MixCompatibility,
    PHIViolation,
    REIViolation,
    TankMixCompatibility,
)


def generate_phi_alert(violation: PHIViolation) -> dict[str, Any]:
    """
    Generate PHI violation alert - إنشاء تنبيه انتهاك فترة ما قبل الحصاد

    Returns alert dict suitable for NATS publishing
    """
    priority = "critical" if violation.status == ComplianceStatus.CRITICAL else "high"

    return {
        "alert_type": "phi_violation",
        "alert_type_ar": "انتهاك فترة ما قبل الحصاد",
        "priority": priority,
        "timestamp": datetime.now(UTC).isoformat(),
        # Violation details
        "field_id": violation.field_id,
        "pesticide_id": violation.pesticide_id,
        "pesticide_name": violation.pesticide_name,
        "pesticide_name_ar": violation.pesticide_name_ar,
        # Dates
        "application_date": violation.application_date.isoformat(),
        "earliest_harvest_date": violation.earliest_harvest_date.isoformat(),
        "planned_harvest_date": violation.planned_harvest_date.isoformat(),
        "days_remaining": violation.days_remaining,
        "phi_days": violation.phi_days,
        # Messages
        "title_en": "⚠️ Pre-Harvest Interval Violation",
        "title_ar": "⚠️ انتهاك فترة ما قبل الحصاد",
        "message_en": violation.message_en,
        "message_ar": violation.message_ar,
        # Recommendations
        "recommendations_en": violation.recommendations_en,
        "recommendations_ar": violation.recommendations_ar,
        # Action required
        "action_required": True,
        "action_en": f"Delay harvest until {violation.earliest_harvest_date.strftime('%Y-%m-%d')}",
        "action_ar": f"أجّل الحصاد حتى {violation.earliest_harvest_date.strftime('%Y-%m-%d')}",
        # Compliance
        "compliance_status": violation.status.value,
        "food_safety_risk": True,
    }


def generate_rei_alert(violation: REIViolation) -> dict[str, Any]:
    """
    Generate REI violation alert - إنشاء تنبيه انتهاك فترة إعادة الدخول

    Returns alert dict suitable for NATS publishing
    """
    priority = "critical" if violation.status == ComplianceStatus.VIOLATION else "high"

    alert = {
        "alert_type": "rei_violation",
        "alert_type_ar": "انتهاك فترة إعادة الدخول",
        "priority": priority,
        "timestamp": datetime.now(UTC).isoformat(),
        # Violation details
        "field_id": violation.field_id,
        "pesticide_id": violation.pesticide_id,
        "pesticide_name": violation.pesticide_name,
        "pesticide_name_ar": violation.pesticide_name_ar,
        # Times
        "application_date": violation.application_date.isoformat(),
        "safe_entry_time": violation.safe_entry_time.isoformat(),
        "rei_hours": violation.rei_hours,
        # Messages
        "title_en": "⚠️ Re-Entry Interval Violation - Worker Safety Risk",
        "title_ar": "⚠️ انتهاك فترة إعادة الدخول - خطر على سلامة العمال",
        "message_en": violation.message_en,
        "message_ar": violation.message_ar,
        # Action required
        "action_required": True,
        "action_en": f"Restrict field access until {violation.safe_entry_time.strftime('%Y-%m-%d %H:%M')}",
        "action_ar": f"قيّد الوصول للحقل حتى {violation.safe_entry_time.strftime('%Y-%m-%d %H:%M')}",
        # Compliance
        "compliance_status": violation.status.value,
        "worker_safety_risk": True,
    }

    # Add PPE requirements for early entry if available
    if violation.early_entry_ppe:
        alert["early_entry_allowed"] = True
        alert["early_entry_ppe"] = {
            "level": violation.early_entry_ppe.level.value,
            "gloves": violation.early_entry_ppe.gloves,
            "gloves_ar": violation.early_entry_ppe.gloves_ar,
            "respirator": violation.early_entry_ppe.respirator,
            "respirator_ar": violation.early_entry_ppe.respirator_ar,
            "eye_protection": violation.early_entry_ppe.eye_protection,
            "eye_protection_ar": violation.early_entry_ppe.eye_protection_ar,
            "clothing": violation.early_entry_ppe.clothing,
            "clothing_ar": violation.early_entry_ppe.clothing_ar,
            "footwear": violation.early_entry_ppe.footwear,
            "footwear_ar": violation.early_entry_ppe.footwear_ar,
        }
        alert["early_entry_note_en"] = "Early entry permitted ONLY with full PPE as specified"
        alert["early_entry_note_ar"] = "الدخول المبكر مسموح فقط مع معدات الحماية الكاملة المحددة"
    else:
        alert["early_entry_allowed"] = False

    return alert


def generate_tank_mix_alert(compatibility: TankMixCompatibility) -> dict[str, Any]:
    """
    Generate tank mix compatibility alert - إنشاء تنبيه توافق الخلط

    Returns alert dict suitable for NATS publishing
    """
    if compatibility.compatibility == MixCompatibility.INCOMPATIBLE:
        priority = "critical"
        title_en = "❌ INCOMPATIBLE Tank Mix - DO NOT APPLY"
        title_ar = "❌ خلط غير متوافق - لا تطبق"
    elif compatibility.compatibility == MixCompatibility.CAUTION:
        priority = "high"
        title_en = "⚠️ Tank Mix Requires Caution"
        title_ar = "⚠️ خلط يتطلب حذراً"
    else:
        priority = "low"
        title_en = "✅ Tank Mix Compatible"
        title_ar = "✅ خلط متوافق"

    alert = {
        "alert_type": "tank_mix_compatibility",
        "alert_type_ar": "توافق خلط المبيدات",
        "priority": priority,
        "timestamp": datetime.now(UTC).isoformat(),
        # Products
        "product_a_id": compatibility.product_a_id,
        "product_a_name": compatibility.product_a_name,
        "product_b_id": compatibility.product_b_id,
        "product_b_name": compatibility.product_b_name,
        # Compatibility
        "compatibility": compatibility.compatibility.value,
        # Messages
        "title_en": title_en,
        "title_ar": title_ar,
        "message_en": compatibility.message_en,
        "message_ar": compatibility.message_ar,
        # Warnings
        "warnings_en": compatibility.warnings_en,
        "warnings_ar": compatibility.warnings_ar,
        # Mixing order (if compatible)
        "mixing_order": compatibility.mixing_order,
    }

    if compatibility.compatibility == MixCompatibility.INCOMPATIBLE:
        alert["action_required"] = True
        alert["action_en"] = "Apply products separately with at least 24 hour interval"
        alert["action_ar"] = "طبق المنتجات بشكل منفصل مع فاصل 24 ساعة على الأقل"
        alert["chemical_reaction_risk"] = True

    return alert


def generate_spray_drift_alert(
    field_id: str,
    wind_speed_kmh: float,
    wind_direction: str,
    risk_level: str,
    can_spray: bool,
    recommended_buffer_m: int,
    recommendations_en: list[str],
    recommendations_ar: list[str],
) -> dict[str, Any]:
    """
    Generate spray drift risk alert - إنشاء تنبيه خطر انجراف الرش
    """
    if risk_level == "extreme":
        priority = "critical"
        title_en = "🌬️ EXTREME Spray Drift Risk - DO NOT SPRAY"
        title_ar = "🌬️ خطر انجراف شديد جداً - لا ترش"
    elif risk_level == "high":
        priority = "high"
        title_en = "🌬️ HIGH Spray Drift Risk - Spraying Not Recommended"
        title_ar = "🌬️ خطر انجراف مرتفع - لا يُنصح بالرش"
    elif risk_level == "medium":
        priority = "medium"
        title_en = "🌬️ MODERATE Spray Drift Risk - Proceed with Caution"
        title_ar = "🌬️ خطر انجراف متوسط - تابع بحذر"
    else:
        priority = "low"
        title_en = "✅ Low Spray Drift Risk - Good Spraying Conditions"
        title_ar = "✅ خطر انجراف منخفض - ظروف رش جيدة"

    return {
        "alert_type": "spray_drift_risk",
        "alert_type_ar": "خطر انجراف الرش",
        "priority": priority,
        "timestamp": datetime.now(UTC).isoformat(),
        # Field
        "field_id": field_id,
        # Weather conditions
        "wind_speed_kmh": wind_speed_kmh,
        "wind_direction": wind_direction,
        "risk_level": risk_level,
        # Decision
        "can_spray": can_spray,
        "recommended_buffer_m": recommended_buffer_m,
        # Messages
        "title_en": title_en,
        "title_ar": title_ar,
        "message_en": f"Wind: {wind_speed_kmh} km/h from {wind_direction}. Buffer zone: {recommended_buffer_m}m",
        "message_ar": f"الرياح: {wind_speed_kmh} كم/س من {wind_direction}. المنطقة العازلة: {recommended_buffer_m}م",
        # Recommendations
        "recommendations_en": recommendations_en,
        "recommendations_ar": recommendations_ar,
        # Action
        "action_required": not can_spray,
        "action_en": "Wait for better conditions" if not can_spray else "Proceed with caution",
        "action_ar": "انتظر ظروفاً أفضل" if not can_spray else "تابع بحذر",
    }


def generate_compliance_summary_alert(
    field_id: str,
    overall_status: ComplianceStatus,
    phi_count: int,
    rei_count: int,
    tank_mix_count: int,
    drift_risk: str | None,
    summary_en: str,
    summary_ar: str,
) -> dict[str, Any]:
    """
    Generate overall compliance summary alert - تنبيه ملخص الامتثال الشامل
    """
    if overall_status == ComplianceStatus.CRITICAL:
        priority = "critical"
        title_en = "🚨 CRITICAL Compliance Violations"
        title_ar = "🚨 مخالفات امتثال حرجة"
    elif overall_status == ComplianceStatus.VIOLATION:
        priority = "high"
        title_en = "⚠️ Compliance Violations Found"
        title_ar = "⚠️ تم العثور على مخالفات امتثال"
    elif overall_status == ComplianceStatus.WARNING:
        priority = "medium"
        title_en = "⚠️ Compliance Warnings"
        title_ar = "⚠️ تحذيرات امتثال"
    else:
        priority = "low"
        title_en = "✅ All Compliance Checks Passed"
        title_ar = "✅ جميع فحوصات الامتثال ناجحة"

    return {
        "alert_type": "compliance_summary",
        "alert_type_ar": "ملخص الامتثال",
        "priority": priority,
        "timestamp": datetime.now(UTC).isoformat(),
        # Field
        "field_id": field_id,
        # Status
        "overall_status": overall_status.value,
        # Violation counts
        "phi_violations": phi_count,
        "rei_violations": rei_count,
        "tank_mix_issues": tank_mix_count,
        "drift_risk": drift_risk,
        # Messages
        "title_en": title_en,
        "title_ar": title_ar,
        "message_en": summary_en,
        "message_ar": summary_ar,
        # Flags
        "action_required": overall_status in [ComplianceStatus.CRITICAL, ComplianceStatus.VIOLATION],
        "food_safety_risk": phi_count > 0,
        "worker_safety_risk": rei_count > 0,
    }
