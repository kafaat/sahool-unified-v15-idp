"""
Geofencing Alerts - تنبيهات السياج الجغرافي
Alert generation helpers for different scenarios
"""

from __future__ import annotations

import uuid
<<<<<<< HEAD
from datetime import datetime, timezone
=======
from datetime import datetime, UTC
>>>>>>> origin/main
from typing import Any

from .models import (
    Geofence,
)


def generate_exit_alert(
    equipment_id: str,
    equipment_name: str,
    equipment_name_ar: str,
    tenant_id: str,
    geofence: Geofence,
    position: tuple[float, float],
    distance_to_boundary_m: float,
    speed_kmh: float | None = None,
) -> dict[str, Any]:
    """
    Generate exit alert for NATS publishing
    إنشاء تنبيه خروج للنشر عبر NATS
    """
    lat, lng = position
<<<<<<< HEAD
    timestamp = datetime.now(timezone.utc)
=======
    timestamp = datetime.now(UTC)
>>>>>>> origin/main

    severity = "critical" if geofence.geofence_type.value == "farm_boundary" else "high"

    return {
        "alert_type": "geofence_exit",
        "alert_type_ar": "خروج من السياج الجغرافي",
        "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
        "priority": severity,
        "timestamp": timestamp.isoformat(),

        # Equipment info
        "equipment_id": equipment_id,
        "equipment_name": equipment_name,
        "equipment_name_ar": equipment_name_ar,
        "tenant_id": tenant_id,

        # Geofence info
        "geofence_id": geofence.id,
        "geofence_name": geofence.name,
        "geofence_name_ar": geofence.name_ar,
        "geofence_type": geofence.geofence_type.value,

        # Position
        "position": {"lat": lat, "lng": lng},
        "distance_to_boundary_m": distance_to_boundary_m,
        "speed_kmh": speed_kmh,

        # Messages
        "title_en": f"🚨 Equipment Left Zone: {geofence.name}",
        "title_ar": f"🚨 المعدة غادرت المنطقة: {geofence.name_ar}",
        "message_en": f"⚠️ ALERT: {equipment_name} has left the allowed zone '{geofence.name}'.\n"
                      f"📍 Current location: ({lat:.6f}, {lng:.6f})\n"
                      f"📏 Distance from boundary: {distance_to_boundary_m:.0f}m\n"
                      f"🕐 Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        "message_ar": f"⚠️ تنبيه: {equipment_name_ar} غادرت المنطقة المسموح بها '{geofence.name_ar}'.\n"
                      f"📍 الموقع الحالي: ({lat:.6f}, {lng:.6f})\n"
                      f"📏 المسافة من الحدود: {distance_to_boundary_m:.0f}م\n"
                      f"🕐 الوقت: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",

        # Actions
        "action_required": True,
        "recommended_actions_en": [
            "Check equipment location on map",
            "Contact equipment operator",
            "Verify if movement is authorized",
        ],
        "recommended_actions_ar": [
            "تحقق من موقع المعدة على الخريطة",
            "تواصل مع مشغّل المعدة",
            "تأكد من أن الحركة مصرح بها",
        ],

        # Channels
        "channels": geofence.alert_channels,
    }


def generate_entry_alert(
    equipment_id: str,
    equipment_name: str,
    equipment_name_ar: str,
    tenant_id: str,
    geofence: Geofence,
    position: tuple[float, float],
) -> dict[str, Any]:
    """
    Generate entry alert for NATS publishing
    إنشاء تنبيه دخول للنشر عبر NATS
    """
    lat, lng = position
<<<<<<< HEAD
    timestamp = datetime.now(timezone.utc)
=======
    timestamp = datetime.now(UTC)
>>>>>>> origin/main

    severity = "high" if geofence.geofence_type.value == "restricted" else "medium"
    if geofence.geofence_type.value == "sensitive":
        severity = "critical"

    return {
        "alert_type": "geofence_entry",
        "alert_type_ar": "دخول للسياج الجغرافي",
        "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
        "priority": severity,
        "timestamp": timestamp.isoformat(),

        # Equipment info
        "equipment_id": equipment_id,
        "equipment_name": equipment_name,
        "equipment_name_ar": equipment_name_ar,
        "tenant_id": tenant_id,

        # Geofence info
        "geofence_id": geofence.id,
        "geofence_name": geofence.name,
        "geofence_name_ar": geofence.name_ar,
        "geofence_type": geofence.geofence_type.value,

        # Position
        "position": {"lat": lat, "lng": lng},

        # Messages
        "title_en": f"⚠️ Equipment Entered Zone: {geofence.name}",
        "title_ar": f"⚠️ المعدة دخلت المنطقة: {geofence.name_ar}",
        "message_en": f"{equipment_name} has entered the '{geofence.name}' zone.",
        "message_ar": f"{equipment_name_ar} دخلت منطقة '{geofence.name_ar}'.",

        # Channels
        "channels": geofence.alert_channels,
    }


def generate_speed_alert(
    equipment_id: str,
    equipment_name: str,
    equipment_name_ar: str,
    tenant_id: str,
    geofence: Geofence,
    position: tuple[float, float],
    current_speed_kmh: float,
) -> dict[str, Any]:
    """
    Generate speed limit violation alert
    إنشاء تنبيه تجاوز حد السرعة
    """
    lat, lng = position
<<<<<<< HEAD
    timestamp = datetime.now(timezone.utc)
=======
    timestamp = datetime.now(UTC)
>>>>>>> origin/main
    max_speed = geofence.max_speed_kmh or 0

    return {
        "alert_type": "speed_violation",
        "alert_type_ar": "تجاوز حد السرعة",
        "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
        "priority": "medium",
        "timestamp": timestamp.isoformat(),

        # Equipment info
        "equipment_id": equipment_id,
        "equipment_name": equipment_name,
        "equipment_name_ar": equipment_name_ar,
        "tenant_id": tenant_id,

        # Geofence info
        "geofence_id": geofence.id,
        "geofence_name": geofence.name,
        "geofence_name_ar": geofence.name_ar,

        # Position and speed
        "position": {"lat": lat, "lng": lng},
        "current_speed_kmh": current_speed_kmh,
        "max_speed_kmh": max_speed,
        "excess_speed_kmh": current_speed_kmh - max_speed,

        # Messages
        "title_en": "⚡ Speed Limit Exceeded",
        "title_ar": "⚡ تجاوز حد السرعة",
        "message_en": f"{equipment_name} traveling at {current_speed_kmh:.1f} km/h in '{geofence.name}'. "
                      f"Speed limit: {max_speed} km/h",
        "message_ar": f"{equipment_name_ar} تسير بسرعة {current_speed_kmh:.1f} كم/س في '{geofence.name_ar}'. "
                      f"حد السرعة: {max_speed} كم/س",

        # Channels
        "channels": ["push"],
    }


def generate_theft_alert(
    equipment_id: str,
    equipment_name: str,
    equipment_name_ar: str,
    tenant_id: str,
    position: tuple[float, float],
    speed_kmh: float,
    reasons: list[str],
    last_known_zone: str | None = None,
) -> dict[str, Any]:
    """
    Generate theft alert for NATS publishing
    إنشاء تنبيه سرقة للنشر عبر NATS

    This is a CRITICAL alert that should trigger immediate response
    """
    lat, lng = position
<<<<<<< HEAD
    timestamp = datetime.now(timezone.utc)
=======
    timestamp = datetime.now(UTC)
>>>>>>> origin/main

    # Translate reasons to Arabic
    reason_translations = {
        "Outside farm boundary": "خارج حدود المزرعة",
        "High-speed movement outside operating hours": "حركة عالية السرعة خارج ساعات العمل",
        "Rapid movement outside allowed zones": "حركة سريعة خارج المناطق المسموحة",
        "Movement during restricted hours": "حركة خلال الساعات المقيدة",
        "Unauthorized zone exit": "خروج غير مصرح به من المنطقة",
    }
    reasons_ar = [reason_translations.get(r, r) for r in reasons]

    return {
        "alert_type": "theft_suspected",
        "alert_type_ar": "اشتباه سرقة",
        "alert_id": f"theft_{uuid.uuid4().hex[:8]}",
        "priority": "critical",
        "timestamp": timestamp.isoformat(),

        # Equipment info
        "equipment_id": equipment_id,
        "equipment_name": equipment_name,
        "equipment_name_ar": equipment_name_ar,
        "tenant_id": tenant_id,

        # Position
        "position": {"lat": lat, "lng": lng},
        "speed_kmh": speed_kmh,
        "last_known_zone": last_known_zone,

        # Reasons
        "reasons": reasons,
        "reasons_ar": reasons_ar,

        # Messages
        "title_en": "🚨 THEFT ALERT - Immediate Action Required",
        "title_ar": "🚨 تنبيه سرقة - إجراء فوري مطلوب",
        "message_en": f"🚨 CRITICAL: Suspected theft of {equipment_name}!\n\n"
                      f"📍 Location: ({lat:.6f}, {lng:.6f})\n"
                      f"🚗 Speed: {speed_kmh:.1f} km/h\n"
                      f"⚠️ Suspicious activity:\n"
                      + "\n".join(f"  • {r}" for r in reasons) +
                      f"\n\n🕐 Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                      f"IMMEDIATE ACTIONS REQUIRED:\n"
                      f"1. Track equipment location in real-time\n"
                      f"2. Contact local authorities\n"
                      f"3. Attempt to disable equipment remotely if possible",
        "message_ar": f"🚨 حرج: اشتباه سرقة {equipment_name_ar}!\n\n"
                      f"📍 الموقع: ({lat:.6f}, {lng:.6f})\n"
                      f"🚗 السرعة: {speed_kmh:.1f} كم/س\n"
                      f"⚠️ النشاط المشبوه:\n"
                      + "\n".join(f"  • {r}" for r in reasons_ar) +
                      f"\n\n🕐 الوقت: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                      f"الإجراءات الفورية المطلوبة:\n"
                      f"1. تتبع موقع المعدة في الوقت الفعلي\n"
                      f"2. التواصل مع الجهات الأمنية\n"
                      f"3. محاولة تعطيل المعدة عن بُعد إن أمكن",

        # Recommended actions
        "action_required": True,
        "recommended_actions_en": [
            "Track equipment location immediately",
            "Contact local police/security",
            "Disable equipment remotely if possible",
            "Preserve GPS trail as evidence",
            "Check security cameras if available",
        ],
        "recommended_actions_ar": [
            "تتبع موقع المعدة فوراً",
            "التواصل مع الشرطة/الأمن المحلي",
            "تعطيل المعدة عن بُعد إن أمكن",
            "حفظ مسار GPS كدليل",
            "فحص كاميرات المراقبة إن وجدت",
        ],

        # Emergency contacts template
        "emergency_contacts": {
            "police_sa": "911",
            "police_ye": "199",
        },

        # Use ALL channels for theft alerts
        "channels": ["push", "sms", "whatsapp", "call", "email"],

        # Metadata
        "requires_acknowledgment": True,
        "escalation_timeout_minutes": 5,  # Escalate if not acknowledged within 5 minutes
    }


def generate_daily_summary(
    tenant_id: str,
    date: datetime,
    equipment_count: int,
    total_alerts: int,
    exit_alerts: int,
    entry_alerts: int,
    speed_alerts: int,
    theft_alerts: int,
    equipment_outside_zones: list[dict],
) -> dict[str, Any]:
    """
    Generate daily geofencing summary
    إنشاء ملخص يومي للسياج الجغرافي
    """
    return {
        "report_type": "geofencing_daily_summary",
        "report_type_ar": "ملخص السياج الجغرافي اليومي",
        "tenant_id": tenant_id,
        "date": date.strftime("%Y-%m-%d"),
<<<<<<< HEAD
        "generated_at": datetime.now(timezone.utc).isoformat(),
=======
        "generated_at": datetime.now(UTC).isoformat(),
>>>>>>> origin/main

        # Statistics
        "statistics": {
            "equipment_monitored": equipment_count,
            "total_alerts": total_alerts,
            "alerts_by_type": {
                "exit": exit_alerts,
                "entry": entry_alerts,
                "speed": speed_alerts,
                "theft": theft_alerts,
            },
        },

        # Equipment currently outside allowed zones
        "equipment_outside_zones": equipment_outside_zones,

        # Messages
        "title_en": f"Daily Geofencing Report - {date.strftime('%Y-%m-%d')}",
        "title_ar": f"تقرير السياج الجغرافي اليومي - {date.strftime('%Y-%m-%d')}",
        "summary_en": f"Monitored {equipment_count} equipment. "
                      f"Generated {total_alerts} alerts "
                      f"({exit_alerts} exits, {entry_alerts} entries, "
                      f"{speed_alerts} speed violations, {theft_alerts} theft alerts).",
        "summary_ar": f"تمت مراقبة {equipment_count} معدة. "
                      f"تم إنشاء {total_alerts} تنبيه "
                      f"({exit_alerts} خروج، {entry_alerts} دخول، "
                      f"{speed_alerts} تجاوز سرعة، {theft_alerts} اشتباه سرقة).",
    }
