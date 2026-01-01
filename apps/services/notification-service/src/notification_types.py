"""
SAHOOL Notification Types & Templates
أنواع وقوالب الإشعارات

Comprehensive notification system for Yemen farmers with bilingual support (Arabic/English).
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class NotificationType(str, Enum):
    """نوع الإشعار - Notification Type"""

    WEATHER_ALERT = "weather_alert"  # تنبيه طقس
    LOW_STOCK = "low_stock"  # نقص مخزون
    DISEASE_DETECTED = "disease_detected"  # مرض مكتشف
    SPRAY_WINDOW = "spray_window"  # وقت الرش
    HARVEST_REMINDER = "harvest_reminder"  # تذكير حصاد
    PAYMENT_DUE = "payment_due"  # دفعة مستحقة
    FIELD_UPDATE = "field_update"  # تحديث حقل
    SATELLITE_READY = "satellite_ready"  # صور أقمار جاهزة
    PEST_OUTBREAK = "pest_outbreak"  # انتشار آفات
    IRRIGATION_REMINDER = "irrigation_reminder"  # تذكير ري
    MARKET_PRICE = "market_price"  # أسعار السوق
    CROP_HEALTH = "crop_health"  # صحة المحصول
    TASK_REMINDER = "task_reminder"  # تذكير مهمة
    SYSTEM = "system"  # نظام


class NotificationPriority(str, Enum):
    """أولوية الإشعار"""

    LOW = "low"  # منخفضة
    MEDIUM = "medium"  # متوسطة
    HIGH = "high"  # عالية
    CRITICAL = "critical"  # حرجة


class NotificationPayload(BaseModel):
    """
    حمولة الإشعار - Notification Payload
    Base model for all notifications
    """

    notification_type: NotificationType = Field(..., description="نوع الإشعار")
    priority: NotificationPriority = Field(
        default=NotificationPriority.MEDIUM, description="الأولوية"
    )
    title: str = Field(..., description="العنوان (English)")
    title_ar: str = Field(..., description="العنوان (العربية)")
    body: str = Field(..., description="النص (English)")
    body_ar: str = Field(..., description="النص (العربية)")

    # Optional fields
    image_url: Optional[str] = Field(None, description="رابط الصورة")
    action_url: Optional[str] = Field(None, description="رابط الإجراء")
    field_id: Optional[str] = Field(None, description="معرف الحقل")
    crop_type: Optional[str] = Field(None, description="نوع المحصول")
    farmer_id: Optional[str] = Field(None, description="معرف المزارع")

    # Extra data
    data: Dict[str, Any] = Field(default_factory=dict, description="بيانات إضافية")

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="وقت الإنشاء"
    )
    expires_at: Optional[datetime] = Field(None, description="وقت الانتهاء")

    class Config:
        json_schema_extra = {
            "example": {
                "notification_type": "weather_alert",
                "priority": "high",
                "title": "Frost Warning",
                "title_ar": "تحذير من الصقيع",
                "body": "Frost expected tonight in Sana'a",
                "body_ar": "صقيع متوقع الليلة في صنعاء",
                "data": {"governorate": "sanaa", "min_temp": -2},
            }
        }


# =============================================================================
# Notification Templates for Each Type
# =============================================================================


class NotificationTemplate:
    """
    قوالب الإشعارات - Notification Templates
    Provides templates for different notification types in Arabic and English
    """

    # Weather Alert Templates
    WEATHER_FROST = {
        "en": {
            "title": "⚠️ Frost Warning",
            "body": "Frost expected tonight in {governorate}. Protect your crops by covering them or using heating methods. Temperature may drop below 0°C.",
        },
        "ar": {
            "title": "⚠️ تحذير من الصقيع",
            "body": "صقيع متوقع الليلة في {governorate}. احمِ محاصيلك بتغطيتها أو استخدام طرق التدفئة. قد تنخفض الحرارة لما دون الصفر.",
        },
    }

    WEATHER_HEAT_WAVE = {
        "en": {
            "title": "🌡️ Heat Wave Alert",
            "body": "Extreme heat expected in {governorate}. Increase irrigation and provide shade for sensitive crops. Avoid field work during peak hours.",
        },
        "ar": {
            "title": "🌡️ تنبيه موجة حر",
            "body": "حرارة شديدة متوقعة في {governorate}. زِد من الري ووفر الظل للمحاصيل الحساسة. تجنب العمل في الحقل خلال ساعات الذروة.",
        },
    }

    WEATHER_STORM = {
        "en": {
            "title": "🌧️ Storm Warning",
            "body": "Heavy rain and strong winds expected in {governorate}. Secure equipment and protect vulnerable crops.",
        },
        "ar": {
            "title": "🌧️ تحذير من عاصفة",
            "body": "أمطار غزيرة ورياح قوية متوقعة في {governorate}. أمّن المعدات واحمِ المحاصيل المعرضة للخطر.",
        },
    }

    WEATHER_FLOOD = {
        "en": {
            "title": "🌊 Flood Risk",
            "body": "Flood risk in {governorate} due to heavy rainfall. Move equipment to higher ground and check drainage systems.",
        },
        "ar": {
            "title": "🌊 خطر فيضان",
            "body": "خطر فيضان في {governorate} بسبب الأمطار الغزيرة. انقل المعدات لمناطق مرتفعة وتحقق من أنظمة الصرف.",
        },
    }

    WEATHER_DROUGHT = {
        "en": {
            "title": "☀️ Drought Alert",
            "body": "Extended dry period expected in {governorate}. Conserve water and prioritize essential irrigation.",
        },
        "ar": {
            "title": "☀️ تنبيه جفاف",
            "body": "فترة جفاف ممتدة متوقعة في {governorate}. حافظ على المياه وأعطِ الأولوية للري الضروري.",
        },
    }

    # Low Stock Templates
    LOW_STOCK = {
        "en": {
            "title": "📦 Low Stock Alert",
            "body": "{item_name} is running low (only {quantity} {unit} left). Consider restocking soon.",
        },
        "ar": {
            "title": "📦 تنبيه نقص مخزون",
            "body": "{item_name} على وشك النفاد (متبقي {quantity} {unit} فقط). فكر في إعادة التخزين قريباً.",
        },
    }

    # Disease Detection Templates
    DISEASE_DETECTED = {
        "en": {
            "title": "🦠 Disease Detected",
            "body": "{disease_name} detected in {field_name}. Take immediate action to prevent spread. Confidence: {confidence}%",
        },
        "ar": {
            "title": "🦠 مرض مكتشف",
            "body": "تم اكتشاف {disease_name} في {field_name}. اتخذ إجراءات فورية لمنع الانتشار. درجة الثقة: {confidence}%",
        },
    }

    # Spray Window Templates
    SPRAY_WINDOW = {
        "en": {
            "title": "💨 Optimal Spray Time",
            "body": "Perfect conditions for spraying {field_name}. Wind speed: {wind_speed} km/h, Temperature: {temp}°C. Window closes in {hours} hours.",
        },
        "ar": {
            "title": "💨 وقت الرش المثالي",
            "body": "ظروف مثالية لرش {field_name}. سرعة الرياح: {wind_speed} كم/س، الحرارة: {temp}°م. ينتهي الوقت خلال {hours} ساعات.",
        },
    }

    # Harvest Reminder Templates
    HARVEST_REMINDER = {
        "en": {
            "title": "🌾 Harvest Reminder",
            "body": "{crop_name} in {field_name} is ready for harvest. Estimated yield: {yield_kg} kg. Best to harvest within {days} days.",
        },
        "ar": {
            "title": "🌾 تذكير حصاد",
            "body": "{crop_name} في {field_name} جاهز للحصاد. الإنتاج المتوقع: {yield_kg} كغ. من الأفضل الحصاد خلال {days} أيام.",
        },
    }

    # Payment Due Templates
    PAYMENT_DUE = {
        "en": {
            "title": "💰 Payment Due",
            "body": "Payment of {amount} YER for {item} is due on {due_date}. Please make payment to avoid late fees.",
        },
        "ar": {
            "title": "💰 دفعة مستحقة",
            "body": "دفعة بقيمة {amount} ريال لـ {item} مستحقة في {due_date}. يرجى السداد لتجنب رسوم التأخير.",
        },
    }

    # Field Update Templates
    FIELD_UPDATE = {
        "en": {
            "title": "🌱 Field Update",
            "body": "{field_name}: {update_message}",
        },
        "ar": {
            "title": "🌱 تحديث حقل",
            "body": "{field_name}: {update_message}",
        },
    }

    # Satellite Ready Templates
    SATELLITE_READY = {
        "en": {
            "title": "🛰️ Satellite Images Ready",
            "body": "New satellite images for {field_name} are now available. NDVI: {ndvi_value}. Tap to view analysis.",
        },
        "ar": {
            "title": "🛰️ صور الأقمار جاهزة",
            "body": "صور أقمار جديدة لـ {field_name} متوفرة الآن. NDVI: {ndvi_value}. اضغط لعرض التحليل.",
        },
    }

    # Pest Outbreak Templates
    PEST_OUTBREAK = {
        "en": {
            "title": "🐛 Pest Outbreak Alert",
            "body": "{pest_name} outbreak reported in {governorate}. Affected crops: {crops}. Check your fields and take preventive measures.",
        },
        "ar": {
            "title": "🐛 تنبيه انتشار آفات",
            "body": "انتشار {pest_name} في {governorate}. المحاصيل المتأثرة: {crops}. تفقد حقولك واتخذ الإجراءات الوقائية.",
        },
    }

    # Irrigation Reminder Templates
    IRRIGATION_REMINDER = {
        "en": {
            "title": "💧 Irrigation Reminder",
            "body": "{field_name} needs watering. Water needed: {water_mm} mm. Best time: Early morning to reduce evaporation.",
        },
        "ar": {
            "title": "💧 تذكير ري",
            "body": "{field_name} يحتاج للري. كمية الماء: {water_mm} ملم. أفضل وقت: الصباح الباكر لتقليل التبخر.",
        },
    }

    # Market Price Templates
    MARKET_PRICE = {
        "en": {
            "title": "📈 Market Price Update",
            "body": "{crop_name} price: {price} YER/kg (↑ {change}%). Good time to sell in {market_name}.",
        },
        "ar": {
            "title": "📈 تحديث أسعار السوق",
            "body": "سعر {crop_name}: {price} ريال/كغ (↑ {change}%). وقت جيد للبيع في {market_name}.",
        },
    }

    # Crop Health Templates
    CROP_HEALTH = {
        "en": {
            "title": "🌿 Crop Health Alert",
            "body": "{field_name}: Crop health is {status}. NDVI dropped by {drop}%. Check for stress factors.",
        },
        "ar": {
            "title": "🌿 تنبيه صحة المحصول",
            "body": "{field_name}: صحة المحصول {status}. انخفض NDVI بنسبة {drop}%. تحقق من عوامل الإجهاد.",
        },
    }

    # Task Reminder Templates
    TASK_REMINDER = {
        "en": {
            "title": "✅ Task Reminder",
            "body": "Task '{task_name}' is due {due_time}. Priority: {priority}",
        },
        "ar": {
            "title": "✅ تذكير مهمة",
            "body": "المهمة '{task_name}' مستحقة {due_time}. الأولوية: {priority}",
        },
    }

    # System Templates
    SYSTEM = {
        "en": {
            "title": "ℹ️ System Notification",
            "body": "{message}",
        },
        "ar": {
            "title": "ℹ️ إشعار نظام",
            "body": "{message}",
        },
    }

    @staticmethod
    def format_template(
        notification_type: NotificationType, language: str = "ar", **kwargs
    ) -> Dict[str, str]:
        """
        تنسيق قالب الإشعار

        Args:
            notification_type: نوع الإشعار
            language: اللغة (ar أو en)
            **kwargs: متغيرات القالب

        Returns:
            Dict with formatted title and body
        """
        # Map notification types to templates
        template_map = {
            NotificationType.WEATHER_ALERT: NotificationTemplate.WEATHER_STORM,  # Default, override with subtype
            NotificationType.LOW_STOCK: NotificationTemplate.LOW_STOCK,
            NotificationType.DISEASE_DETECTED: NotificationTemplate.DISEASE_DETECTED,
            NotificationType.SPRAY_WINDOW: NotificationTemplate.SPRAY_WINDOW,
            NotificationType.HARVEST_REMINDER: NotificationTemplate.HARVEST_REMINDER,
            NotificationType.PAYMENT_DUE: NotificationTemplate.PAYMENT_DUE,
            NotificationType.FIELD_UPDATE: NotificationTemplate.FIELD_UPDATE,
            NotificationType.SATELLITE_READY: NotificationTemplate.SATELLITE_READY,
            NotificationType.PEST_OUTBREAK: NotificationTemplate.PEST_OUTBREAK,
            NotificationType.IRRIGATION_REMINDER: NotificationTemplate.IRRIGATION_REMINDER,
            NotificationType.MARKET_PRICE: NotificationTemplate.MARKET_PRICE,
            NotificationType.CROP_HEALTH: NotificationTemplate.CROP_HEALTH,
            NotificationType.TASK_REMINDER: NotificationTemplate.TASK_REMINDER,
            NotificationType.SYSTEM: NotificationTemplate.SYSTEM,
        }

        # Get weather subtype if provided
        if (
            notification_type == NotificationType.WEATHER_ALERT
            and "weather_type" in kwargs
        ):
            weather_type = kwargs["weather_type"]
            weather_templates = {
                "frost": NotificationTemplate.WEATHER_FROST,
                "heat_wave": NotificationTemplate.WEATHER_HEAT_WAVE,
                "storm": NotificationTemplate.WEATHER_STORM,
                "flood": NotificationTemplate.WEATHER_FLOOD,
                "drought": NotificationTemplate.WEATHER_DROUGHT,
            }
            template = weather_templates.get(
                weather_type, NotificationTemplate.WEATHER_STORM
            )
        else:
            template = template_map.get(notification_type, NotificationTemplate.SYSTEM)

        # Get language template
        lang_template = template.get(language, template.get("ar"))

        # Format with kwargs
        try:
            title = lang_template["title"].format(**kwargs)
            body = lang_template["body"].format(**kwargs)
        except KeyError as e:
            # Missing template variable
            title = lang_template["title"]
            body = lang_template["body"]

        return {"title": title, "body": body}


# =============================================================================
# Helper Functions
# =============================================================================


def create_weather_notification(
    weather_type: str, governorate: str, **extra_data
) -> NotificationPayload:
    """
    إنشاء إشعار طقس

    Args:
        weather_type: نوع التنبيه (frost, heat_wave, storm, flood, drought)
        governorate: المحافظة
        **extra_data: بيانات إضافية

    Returns:
        NotificationPayload
    """
    en_template = NotificationTemplate.format_template(
        NotificationType.WEATHER_ALERT,
        language="en",
        weather_type=weather_type,
        governorate=governorate,
        **extra_data,
    )

    ar_template = NotificationTemplate.format_template(
        NotificationType.WEATHER_ALERT,
        language="ar",
        weather_type=weather_type,
        governorate=governorate,
        **extra_data,
    )

    return NotificationPayload(
        notification_type=NotificationType.WEATHER_ALERT,
        priority=(
            NotificationPriority.HIGH
            if weather_type in ["frost", "storm", "flood"]
            else NotificationPriority.MEDIUM
        ),
        title=en_template["title"],
        title_ar=ar_template["title"],
        body=en_template["body"],
        body_ar=ar_template["body"],
        data={"weather_type": weather_type, "governorate": governorate, **extra_data},
    )


def create_harvest_notification(
    crop_name: str,
    crop_name_ar: str,
    field_name: str,
    field_id: str,
    yield_kg: float,
    days_until: int,
) -> NotificationPayload:
    """
    إنشاء إشعار حصاد

    Args:
        crop_name: اسم المحصول (English)
        crop_name_ar: اسم المحصول (العربية)
        field_name: اسم الحقل
        field_id: معرف الحقل
        yield_kg: الإنتاج المتوقع بالكيلو
        days_until: عدد الأيام المتبقية

    Returns:
        NotificationPayload
    """
    en_template = NotificationTemplate.format_template(
        NotificationType.HARVEST_REMINDER,
        language="en",
        crop_name=crop_name,
        field_name=field_name,
        yield_kg=yield_kg,
        days=days_until,
    )

    ar_template = NotificationTemplate.format_template(
        NotificationType.HARVEST_REMINDER,
        language="ar",
        crop_name=crop_name_ar,
        field_name=field_name,
        yield_kg=yield_kg,
        days=days_until,
    )

    return NotificationPayload(
        notification_type=NotificationType.HARVEST_REMINDER,
        priority=(
            NotificationPriority.HIGH
            if days_until <= 2
            else NotificationPriority.MEDIUM
        ),
        title=en_template["title"],
        title_ar=ar_template["title"],
        body=en_template["body"],
        body_ar=ar_template["body"],
        field_id=field_id,
        crop_type=crop_name,
        data={
            "crop_name": crop_name,
            "crop_name_ar": crop_name_ar,
            "field_name": field_name,
            "yield_kg": yield_kg,
            "days_until": days_until,
        },
    )


def create_satellite_notification(
    field_name: str,
    field_id: str,
    ndvi_value: float,
    change_percentage: float,
) -> NotificationPayload:
    """
    إنشاء إشعار صور أقمار

    Args:
        field_name: اسم الحقل
        field_id: معرف الحقل
        ndvi_value: قيمة NDVI
        change_percentage: نسبة التغيير

    Returns:
        NotificationPayload
    """
    en_template = NotificationTemplate.format_template(
        NotificationType.SATELLITE_READY,
        language="en",
        field_name=field_name,
        ndvi_value=f"{ndvi_value:.2f}",
    )

    ar_template = NotificationTemplate.format_template(
        NotificationType.SATELLITE_READY,
        language="ar",
        field_name=field_name,
        ndvi_value=f"{ndvi_value:.2f}",
    )

    priority = (
        NotificationPriority.HIGH
        if change_percentage < -10
        else NotificationPriority.MEDIUM
    )

    return NotificationPayload(
        notification_type=NotificationType.SATELLITE_READY,
        priority=priority,
        title=en_template["title"],
        title_ar=ar_template["title"],
        body=en_template["body"],
        body_ar=ar_template["body"],
        field_id=field_id,
        action_url=f"/fields/{field_id}/satellite",
        data={
            "field_name": field_name,
            "ndvi_value": ndvi_value,
            "change_percentage": change_percentage,
        },
    )
