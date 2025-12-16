"""
💬 SAHOOL Personalized Notification Service v15.3
خدمة الإشعارات المخصصة - تنبيهات ذكية لكل مزارع

Features:
- Personalized alerts based on farmer's crops and location
- Weather warnings (frost, heat waves, storms)
- Pest outbreak alerts in nearby areas
- Irrigation reminders
- Market price notifications
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sahool-notifications")

app = FastAPI(
    title="SAHOOL Notification Service | خدمة الإشعارات",
    version="15.3.0",
    description="Personalized agricultural notifications for Yemeni farmers",
)


# =============================================================================
# Enums & Models
# =============================================================================


class NotificationType(str, Enum):
    WEATHER_ALERT = "weather_alert"
    PEST_OUTBREAK = "pest_outbreak"
    IRRIGATION_REMINDER = "irrigation_reminder"
    CROP_HEALTH = "crop_health"
    MARKET_PRICE = "market_price"
    SYSTEM = "system"
    TASK_REMINDER = "task_reminder"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(str, Enum):
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"


class Governorate(str, Enum):
    SANAA = "sanaa"
    ADEN = "aden"
    TAIZ = "taiz"
    HODEIDAH = "hodeidah"
    IBB = "ibb"
    DHAMAR = "dhamar"
    HADRAMAUT = "hadramaut"
    MARIB = "marib"
    HAJJAH = "hajjah"
    SAADA = "saada"
    LAHJ = "lahj"
    ABYAN = "abyan"


class CropType(str, Enum):
    TOMATO = "tomato"
    WHEAT = "wheat"
    COFFEE = "coffee"
    QAT = "qat"
    BANANA = "banana"
    DATE_PALM = "date_palm"
    MANGO = "mango"
    GRAPES = "grapes"
    CORN = "corn"
    POTATO = "potato"


# Arabic translations
NOTIFICATION_TYPE_AR = {
    NotificationType.WEATHER_ALERT: "تنبيه طقس",
    NotificationType.PEST_OUTBREAK: "انتشار آفات",
    NotificationType.IRRIGATION_REMINDER: "تذكير ري",
    NotificationType.CROP_HEALTH: "صحة المحصول",
    NotificationType.MARKET_PRICE: "أسعار السوق",
    NotificationType.SYSTEM: "نظام",
    NotificationType.TASK_REMINDER: "تذكير مهمة",
}

PRIORITY_AR = {
    NotificationPriority.LOW: "منخفضة",
    NotificationPriority.MEDIUM: "متوسطة",
    NotificationPriority.HIGH: "عالية",
    NotificationPriority.CRITICAL: "حرجة",
}

GOVERNORATE_AR = {
    Governorate.SANAA: "صنعاء",
    Governorate.ADEN: "عدن",
    Governorate.TAIZ: "تعز",
    Governorate.HODEIDAH: "الحديدة",
    Governorate.IBB: "إب",
    Governorate.DHAMAR: "ذمار",
    Governorate.HADRAMAUT: "حضرموت",
    Governorate.MARIB: "مأرب",
    Governorate.HAJJAH: "حجة",
    Governorate.SAADA: "صعدة",
    Governorate.LAHJ: "لحج",
    Governorate.ABYAN: "أبين",
}

CROP_AR = {
    CropType.TOMATO: "طماطم",
    CropType.WHEAT: "قمح",
    CropType.COFFEE: "بن",
    CropType.QAT: "قات",
    CropType.BANANA: "موز",
    CropType.DATE_PALM: "نخيل",
    CropType.MANGO: "مانجو",
    CropType.GRAPES: "عنب",
    CropType.CORN: "ذرة",
    CropType.POTATO: "بطاطس",
}


# =============================================================================
# Request/Response Models
# =============================================================================


class FarmerProfile(BaseModel):
    """ملف المزارع للإشعارات المخصصة"""
    farmer_id: str
    name: str
    name_ar: str
    governorate: Governorate
    district: Optional[str] = None
    crops: List[CropType]
    field_ids: List[str] = []
    phone: Optional[str] = None
    fcm_token: Optional[str] = None  # Firebase Cloud Messaging
    notification_channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    language: str = "ar"


class NotificationPreferences(BaseModel):
    """تفضيلات الإشعارات"""
    farmer_id: str
    weather_alerts: bool = True
    pest_alerts: bool = True
    irrigation_reminders: bool = True
    crop_health_alerts: bool = True
    market_prices: bool = True
    quiet_hours_start: Optional[str] = "22:00"  # HH:MM
    quiet_hours_end: Optional[str] = "06:00"
    min_priority: NotificationPriority = NotificationPriority.LOW


class Notification(BaseModel):
    """إشعار"""
    id: str
    type: NotificationType
    type_ar: str
    priority: NotificationPriority
    priority_ar: str
    title: str
    title_ar: str
    body: str
    body_ar: str
    data: Dict[str, Any] = {}
    target_farmers: List[str] = []  # Empty = broadcast
    target_governorates: List[Governorate] = []
    target_crops: List[CropType] = []
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_read: bool = False
    action_url: Optional[str] = None


class CreateNotificationRequest(BaseModel):
    """طلب إنشاء إشعار"""
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    title_ar: str
    body: str
    body_ar: str
    data: Dict[str, Any] = {}
    target_farmers: List[str] = []
    target_governorates: List[Governorate] = []
    target_crops: List[CropType] = []
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    expires_in_hours: Optional[int] = 24


class WeatherAlertRequest(BaseModel):
    """طلب تنبيه طقس"""
    governorates: List[Governorate]
    alert_type: str  # frost, heat_wave, storm, flood, drought
    severity: NotificationPriority
    expected_date: date
    details: Dict[str, Any] = {}


class PestAlertRequest(BaseModel):
    """طلب تنبيه آفات"""
    governorate: Governorate
    pest_name: str
    pest_name_ar: str
    affected_crops: List[CropType]
    severity: NotificationPriority
    recommendations: List[str] = []
    recommendations_ar: List[str] = []


class IrrigationReminderRequest(BaseModel):
    """طلب تذكير ري"""
    farmer_id: str
    field_id: str
    field_name: str
    crop: CropType
    water_needed_mm: float
    urgency: NotificationPriority


# =============================================================================
# In-Memory Storage (Replace with Database in Production)
# =============================================================================


# Simulated farmer profiles
FARMER_PROFILES: Dict[str, FarmerProfile] = {
    "farmer-1": FarmerProfile(
        farmer_id="farmer-1",
        name="Ahmed Ali",
        name_ar="أحمد علي",
        governorate=Governorate.SANAA,
        crops=[CropType.TOMATO, CropType.COFFEE],
        field_ids=["field-1", "field-2"],
        phone="+967771234567",
    ),
    "farmer-2": FarmerProfile(
        farmer_id="farmer-2",
        name="Mohammed Hassan",
        name_ar="محمد حسن",
        governorate=Governorate.IBB,
        crops=[CropType.BANANA, CropType.MANGO],
        field_ids=["field-3"],
        phone="+967772345678",
    ),
}

NOTIFICATIONS: Dict[str, Notification] = {}
FARMER_NOTIFICATIONS: Dict[str, List[str]] = {}  # farmer_id -> [notification_ids]


# =============================================================================
# Notification Logic
# =============================================================================


def create_notification(
    type: NotificationType,
    priority: NotificationPriority,
    title: str,
    title_ar: str,
    body: str,
    body_ar: str,
    data: Dict[str, Any] = {},
    target_farmers: List[str] = [],
    target_governorates: List[Governorate] = [],
    target_crops: List[CropType] = [],
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP],
    expires_in_hours: Optional[int] = 24,
) -> Notification:
    """إنشاء إشعار جديد"""
    notification_id = str(uuid.uuid4())

    notification = Notification(
        id=notification_id,
        type=type,
        type_ar=NOTIFICATION_TYPE_AR[type],
        priority=priority,
        priority_ar=PRIORITY_AR[priority],
        title=title,
        title_ar=title_ar,
        body=body,
        body_ar=body_ar,
        data=data,
        target_farmers=target_farmers,
        target_governorates=target_governorates,
        target_crops=target_crops,
        channels=channels,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        if expires_in_hours
        else None,
    )

    NOTIFICATIONS[notification_id] = notification

    # Determine target farmers
    recipients = determine_recipients(notification)

    for farmer_id in recipients:
        if farmer_id not in FARMER_NOTIFICATIONS:
            FARMER_NOTIFICATIONS[farmer_id] = []
        FARMER_NOTIFICATIONS[farmer_id].append(notification_id)

    logger.info(
        f"📬 Notification created: {notification_id} for {len(recipients)} farmers"
    )

    return notification


def determine_recipients(notification: Notification) -> List[str]:
    """تحديد المستلمين بناءً على معايير الإشعار"""
    if notification.target_farmers:
        return notification.target_farmers

    recipients = set()

    for farmer_id, profile in FARMER_PROFILES.items():
        # Filter by governorate
        if notification.target_governorates:
            if profile.governorate not in notification.target_governorates:
                continue

        # Filter by crops
        if notification.target_crops:
            if not any(crop in profile.crops for crop in notification.target_crops):
                continue

        recipients.add(farmer_id)

    return list(recipients)


def get_weather_alert_message(alert_type: str, governorate: Governorate) -> tuple:
    """الحصول على رسالة تنبيه الطقس"""
    gov_ar = GOVERNORATE_AR[governorate]

    messages = {
        "frost": (
            f"Frost Warning in {governorate.value}",
            f"⚠️ تحذير من الصقيع في {gov_ar}",
            f"Expected frost tonight. Protect your crops by covering them or using heating methods.",
            f"يُتوقع صقيع الليلة. قم بحماية محاصيلك بتغطيتها أو استخدام طرق التدفئة. درجات الحرارة قد تنخفض إلى ما دون الصفر.",
        ),
        "heat_wave": (
            f"Heat Wave Alert in {governorate.value}",
            f"🌡️ تنبيه موجة حر في {gov_ar}",
            f"Extreme heat expected. Increase irrigation and provide shade for sensitive crops.",
            f"متوقع حرارة شديدة. زِد من الري ووفر الظل للمحاصيل الحساسة. تجنب العمل في الحقل خلال ساعات الذروة.",
        ),
        "storm": (
            f"Storm Warning in {governorate.value}",
            f"🌧️ تحذير من عاصفة في {gov_ar}",
            f"Heavy rain and strong winds expected. Secure equipment and protect vulnerable crops.",
            f"متوقع أمطار غزيرة ورياح قوية. أمّن المعدات واحمِ المحاصيل المعرضة للخطر.",
        ),
        "flood": (
            f"Flood Risk in {governorate.value}",
            f"🌊 خطر فيضان في {gov_ar}",
            f"Flood risk due to heavy rainfall. Move equipment to higher ground and check drainage.",
            f"خطر فيضان بسبب الأمطار الغزيرة. انقل المعدات لمناطق مرتفعة وتحقق من الصرف.",
        ),
        "drought": (
            f"Drought Alert in {governorate.value}",
            f"☀️ تنبيه جفاف في {gov_ar}",
            f"Extended dry period expected. Conserve water and prioritize essential irrigation.",
            f"متوقع فترة جفاف ممتدة. حافظ على المياه وأعطِ الأولوية للري الضروري.",
        ),
    }

    return messages.get(
        alert_type,
        (
            f"Weather Alert in {governorate.value}",
            f"⚠️ تنبيه طقس في {gov_ar}",
            "Check weather conditions and take necessary precautions.",
            "تحقق من حالة الطقس واتخذ الاحتياطات اللازمة.",
        ),
    )


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/healthz")
def health_check():
    return {
        "status": "ok",
        "service": "notification-service",
        "version": "15.3.0",
        "active_notifications": len(NOTIFICATIONS),
        "registered_farmers": len(FARMER_PROFILES),
    }


@app.post("/v1/notifications", response_model=Notification)
def create_custom_notification(request: CreateNotificationRequest):
    """إنشاء إشعار مخصص"""
    return create_notification(
        type=request.type,
        priority=request.priority,
        title=request.title,
        title_ar=request.title_ar,
        body=request.body,
        body_ar=request.body_ar,
        data=request.data,
        target_farmers=request.target_farmers,
        target_governorates=request.target_governorates,
        target_crops=request.target_crops,
        channels=request.channels,
        expires_in_hours=request.expires_in_hours,
    )


@app.post("/v1/alerts/weather", response_model=Notification)
def create_weather_alert(request: WeatherAlertRequest, background_tasks: BackgroundTasks):
    """إنشاء تنبيه طقس لمحافظات محددة"""

    # Get message for first governorate (can be customized per governorate)
    title, title_ar, body, body_ar = get_weather_alert_message(
        request.alert_type, request.governorates[0]
    )

    notification = create_notification(
        type=NotificationType.WEATHER_ALERT,
        priority=request.severity,
        title=title,
        title_ar=title_ar,
        body=body,
        body_ar=body_ar,
        data={
            "alert_type": request.alert_type,
            "expected_date": request.expected_date.isoformat(),
            **request.details,
        },
        target_governorates=request.governorates,
        channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP],
        expires_in_hours=48,
    )

    logger.info(
        f"🌤️ Weather alert created for {len(request.governorates)} governorates"
    )
    return notification


@app.post("/v1/alerts/pest", response_model=Notification)
def create_pest_alert(request: PestAlertRequest):
    """إنشاء تنبيه انتشار آفات"""
    gov_ar = GOVERNORATE_AR[request.governorate]
    crops_ar = ", ".join([CROP_AR[c] for c in request.affected_crops])

    notification = create_notification(
        type=NotificationType.PEST_OUTBREAK,
        priority=request.severity,
        title=f"Pest Outbreak: {request.pest_name}",
        title_ar=f"🐛 انتشار آفة: {request.pest_name_ar}",
        body=f"Pest outbreak reported in {request.governorate.value}. Affected crops: {', '.join([c.value for c in request.affected_crops])}",
        body_ar=f"تم رصد انتشار {request.pest_name_ar} في {gov_ar}. المحاصيل المتأثرة: {crops_ar}. تحقق من حقولك واتخذ الإجراءات الوقائية.",
        data={
            "pest_name": request.pest_name,
            "pest_name_ar": request.pest_name_ar,
            "affected_crops": [c.value for c in request.affected_crops],
            "recommendations": request.recommendations,
            "recommendations_ar": request.recommendations_ar,
        },
        target_governorates=[request.governorate],
        target_crops=request.affected_crops,
        channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP],
        expires_in_hours=72,
    )

    logger.info(f"🐛 Pest alert created for {request.governorate.value}")
    return notification


@app.post("/v1/reminders/irrigation", response_model=Notification)
def create_irrigation_reminder(request: IrrigationReminderRequest):
    """إنشاء تذكير ري مخصص"""
    crop_ar = CROP_AR.get(request.crop, request.crop.value)

    notification = create_notification(
        type=NotificationType.IRRIGATION_REMINDER,
        priority=request.urgency,
        title=f"Irrigation Reminder: {request.field_name}",
        title_ar=f"💧 تذكير ري: {request.field_name}",
        body=f"Your {request.crop.value} field needs {request.water_needed_mm}mm of water.",
        body_ar=f"حقل {crop_ar} يحتاج {request.water_needed_mm} ملم من المياه. يُنصح بالري في الصباح الباكر لتقليل التبخر.",
        data={
            "field_id": request.field_id,
            "field_name": request.field_name,
            "crop": request.crop.value,
            "water_needed_mm": request.water_needed_mm,
        },
        target_farmers=[request.farmer_id],
        channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP],
        expires_in_hours=12,
    )

    return notification


@app.get("/v1/notifications/farmer/{farmer_id}")
def get_farmer_notifications(
    farmer_id: str,
    unread_only: bool = Query(default=False),
    type: Optional[NotificationType] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
):
    """الحصول على إشعارات مزارع معين"""
    notification_ids = FARMER_NOTIFICATIONS.get(farmer_id, [])

    notifications = []
    for nid in notification_ids:
        if nid in NOTIFICATIONS:
            n = NOTIFICATIONS[nid]

            # Filter expired
            if n.expires_at and n.expires_at < datetime.utcnow():
                continue

            # Filter by read status
            if unread_only and n.is_read:
                continue

            # Filter by type
            if type and n.type != type:
                continue

            notifications.append(n)

    # Sort by created_at descending
    notifications.sort(key=lambda x: x.created_at, reverse=True)

    return {
        "farmer_id": farmer_id,
        "total": len(notifications),
        "unread_count": sum(1 for n in notifications if not n.is_read),
        "notifications": notifications[:limit],
    }


@app.patch("/v1/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, farmer_id: str):
    """تحديد إشعار كمقروء"""
    if notification_id not in NOTIFICATIONS:
        raise HTTPException(status_code=404, detail="Notification not found")

    # In real implementation, track read status per farmer
    # For now, we just return success
    return {"success": True, "notification_id": notification_id, "is_read": True}


@app.get("/v1/notifications/broadcast")
def get_broadcast_notifications(
    governorate: Optional[Governorate] = None,
    crop: Optional[CropType] = None,
    limit: int = Query(default=20, ge=1, le=50),
):
    """الحصول على الإشعارات العامة (البث)"""
    notifications = []

    for n in NOTIFICATIONS.values():
        # Skip expired
        if n.expires_at and n.expires_at < datetime.utcnow():
            continue

        # Skip targeted notifications
        if n.target_farmers:
            continue

        # Filter by governorate
        if governorate and n.target_governorates:
            if governorate not in n.target_governorates:
                continue

        # Filter by crop
        if crop and n.target_crops:
            if crop not in n.target_crops:
                continue

        notifications.append(n)

    notifications.sort(key=lambda x: x.created_at, reverse=True)

    return {
        "total": len(notifications),
        "notifications": notifications[:limit],
    }


@app.post("/v1/farmers/register")
def register_farmer(profile: FarmerProfile):
    """تسجيل مزارع للإشعارات"""
    FARMER_PROFILES[profile.farmer_id] = profile
    FARMER_NOTIFICATIONS[profile.farmer_id] = []

    logger.info(f"👨‍🌾 Farmer registered: {profile.farmer_id} ({profile.name_ar})")

    return {
        "success": True,
        "farmer_id": profile.farmer_id,
        "message": "تم تسجيل المزارع بنجاح",
        "message_en": "Farmer registered successfully",
    }


@app.put("/v1/farmers/{farmer_id}/preferences")
def update_preferences(farmer_id: str, preferences: NotificationPreferences):
    """تحديث تفضيلات الإشعارات"""
    if farmer_id not in FARMER_PROFILES:
        raise HTTPException(status_code=404, detail="Farmer not found")

    # Store preferences (in real implementation, save to database)
    return {
        "success": True,
        "farmer_id": farmer_id,
        "preferences": preferences.dict(),
        "message": "تم تحديث التفضيلات",
    }


@app.get("/v1/stats")
def get_notification_stats():
    """إحصائيات الإشعارات"""
    type_counts = {}
    for n in NOTIFICATIONS.values():
        type_counts[n.type.value] = type_counts.get(n.type.value, 0) + 1

    return {
        "total_notifications": len(NOTIFICATIONS),
        "registered_farmers": len(FARMER_PROFILES),
        "by_type": type_counts,
        "active_weather_alerts": sum(
            1
            for n in NOTIFICATIONS.values()
            if n.type == NotificationType.WEATHER_ALERT
            and (not n.expires_at or n.expires_at > datetime.utcnow())
        ),
        "active_pest_alerts": sum(
            1
            for n in NOTIFICATIONS.values()
            if n.type == NotificationType.PEST_OUTBREAK
            and (not n.expires_at or n.expires_at > datetime.utcnow())
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8109)
