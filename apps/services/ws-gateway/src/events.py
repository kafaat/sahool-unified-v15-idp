"""
WebSocket Event Types
أنواع الأحداث في النظام

Defines all event types that can be sent through WebSocket
"""

from enum import Enum
from typing import Dict


class EventType(str, Enum):
    """
    WebSocket event types
    أنواع الأحداث
    """
    # Field Events
    FIELD_UPDATED = "field.updated"
    FIELD_CREATED = "field.created"
    FIELD_DELETED = "field.deleted"

    # Weather Events
    WEATHER_ALERT = "weather.alert"
    WEATHER_UPDATED = "weather.updated"

    # Satellite Events
    SATELLITE_READY = "satellite.ready"
    SATELLITE_PROCESSING = "satellite.processing"
    SATELLITE_FAILED = "satellite.failed"

    # NDVI Events
    NDVI_UPDATED = "ndvi.updated"
    NDVI_ANALYSIS_READY = "ndvi.analysis.ready"

    # Inventory Events
    LOW_STOCK = "inventory.low_stock"
    OUT_OF_STOCK = "inventory.out_of_stock"
    STOCK_UPDATED = "inventory.updated"

    # Crop Health Events
    DISEASE_DETECTED = "crop.disease.detected"
    PEST_DETECTED = "crop.pest.detected"
    HEALTH_ALERT = "crop.health.alert"

    # Spray Events
    SPRAY_WINDOW = "spray.window.optimal"
    SPRAY_WARNING = "spray.window.warning"
    SPRAY_SCHEDULED = "spray.scheduled"

    # Chat Events
    CHAT_MESSAGE = "chat.message"
    CHAT_TYPING = "chat.typing"
    CHAT_READ = "chat.read"

    # Task Events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_OVERDUE = "task.overdue"

    # IoT Events
    IOT_READING = "iot.reading"
    IOT_ALERT = "iot.alert"
    IOT_OFFLINE = "iot.offline"

    # System Events
    SYSTEM_NOTIFICATION = "system.notification"
    SYNC_REQUIRED = "system.sync_required"

    # User Events
    USER_ONLINE = "user.online"
    USER_OFFLINE = "user.offline"


# Event messages in Arabic
EVENT_MESSAGES_AR: Dict[EventType, str] = {
    EventType.FIELD_UPDATED: "تم تحديث بيانات الحقل",
    EventType.FIELD_CREATED: "تم إنشاء حقل جديد",
    EventType.FIELD_DELETED: "تم حذف الحقل",

    EventType.WEATHER_ALERT: "تنبيه طقس مهم",
    EventType.WEATHER_UPDATED: "تم تحديث بيانات الطقس",

    EventType.SATELLITE_READY: "صور الأقمار الصناعية جاهزة",
    EventType.SATELLITE_PROCESSING: "جاري معالجة صور الأقمار الصناعية",
    EventType.SATELLITE_FAILED: "فشلت معالجة صور الأقمار الصناعية",

    EventType.NDVI_UPDATED: "تم تحديث بيانات NDVI",
    EventType.NDVI_ANALYSIS_READY: "تحليل NDVI جاهز",

    EventType.LOW_STOCK: "مخزون منخفض",
    EventType.OUT_OF_STOCK: "نفاد المخزون",
    EventType.STOCK_UPDATED: "تم تحديث المخزون",

    EventType.DISEASE_DETECTED: "تم اكتشاف مرض في المحصول",
    EventType.PEST_DETECTED: "تم اكتشاف آفة في المحصول",
    EventType.HEALTH_ALERT: "تنبيه صحة المحصول",

    EventType.SPRAY_WINDOW: "وقت الرش المثالي",
    EventType.SPRAY_WARNING: "تحذير وقت الرش",
    EventType.SPRAY_SCHEDULED: "تم جدولة الرش",

    EventType.CHAT_MESSAGE: "رسالة جديدة",
    EventType.CHAT_TYPING: "يكتب...",
    EventType.CHAT_READ: "تمت القراءة",

    EventType.TASK_CREATED: "تم إنشاء مهمة جديدة",
    EventType.TASK_UPDATED: "تم تحديث المهمة",
    EventType.TASK_COMPLETED: "تمت المهمة",
    EventType.TASK_OVERDUE: "مهمة متأخرة",

    EventType.IOT_READING: "قراءة من المستشعر",
    EventType.IOT_ALERT: "تنبيه من المستشعر",
    EventType.IOT_OFFLINE: "المستشعر غير متصل",

    EventType.SYSTEM_NOTIFICATION: "إشعار النظام",
    EventType.SYNC_REQUIRED: "مطلوب مزامنة",

    EventType.USER_ONLINE: "المستخدم متصل",
    EventType.USER_OFFLINE: "المستخدم غير متصل",
}


# Event messages in English
EVENT_MESSAGES_EN: Dict[EventType, str] = {
    EventType.FIELD_UPDATED: "Field data updated",
    EventType.FIELD_CREATED: "New field created",
    EventType.FIELD_DELETED: "Field deleted",

    EventType.WEATHER_ALERT: "Important weather alert",
    EventType.WEATHER_UPDATED: "Weather data updated",

    EventType.SATELLITE_READY: "Satellite imagery ready",
    EventType.SATELLITE_PROCESSING: "Processing satellite imagery",
    EventType.SATELLITE_FAILED: "Satellite processing failed",

    EventType.NDVI_UPDATED: "NDVI data updated",
    EventType.NDVI_ANALYSIS_READY: "NDVI analysis ready",

    EventType.LOW_STOCK: "Low stock alert",
    EventType.OUT_OF_STOCK: "Out of stock",
    EventType.STOCK_UPDATED: "Stock updated",

    EventType.DISEASE_DETECTED: "Crop disease detected",
    EventType.PEST_DETECTED: "Crop pest detected",
    EventType.HEALTH_ALERT: "Crop health alert",

    EventType.SPRAY_WINDOW: "Optimal spray window",
    EventType.SPRAY_WARNING: "Spray window warning",
    EventType.SPRAY_SCHEDULED: "Spray scheduled",

    EventType.CHAT_MESSAGE: "New message",
    EventType.CHAT_TYPING: "Typing...",
    EventType.CHAT_READ: "Read",

    EventType.TASK_CREATED: "New task created",
    EventType.TASK_UPDATED: "Task updated",
    EventType.TASK_COMPLETED: "Task completed",
    EventType.TASK_OVERDUE: "Task overdue",

    EventType.IOT_READING: "Sensor reading",
    EventType.IOT_ALERT: "Sensor alert",
    EventType.IOT_OFFLINE: "Sensor offline",

    EventType.SYSTEM_NOTIFICATION: "System notification",
    EventType.SYNC_REQUIRED: "Sync required",

    EventType.USER_ONLINE: "User online",
    EventType.USER_OFFLINE: "User offline",
}


def get_event_message(event_type: EventType, language: str = "ar") -> str:
    """
    Get localized message for event type
    الحصول على رسالة محلية لنوع الحدث
    """
    if language == "ar":
        return EVENT_MESSAGES_AR.get(event_type, event_type.value)
    return EVENT_MESSAGES_EN.get(event_type, event_type.value)


# Priority levels for events
class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Map event types to priorities
EVENT_PRIORITIES: Dict[EventType, EventPriority] = {
    EventType.WEATHER_ALERT: EventPriority.HIGH,
    EventType.DISEASE_DETECTED: EventPriority.HIGH,
    EventType.PEST_DETECTED: EventPriority.HIGH,
    EventType.OUT_OF_STOCK: EventPriority.HIGH,
    EventType.IOT_ALERT: EventPriority.HIGH,
    EventType.TASK_OVERDUE: EventPriority.MEDIUM,
    EventType.LOW_STOCK: EventPriority.MEDIUM,
    EventType.SPRAY_WARNING: EventPriority.MEDIUM,
    EventType.SATELLITE_READY: EventPriority.LOW,
    EventType.CHAT_MESSAGE: EventPriority.LOW,
}


def get_event_priority(event_type: EventType) -> EventPriority:
    """Get priority for event type"""
    return EVENT_PRIORITIES.get(event_type, EventPriority.LOW)
