/**
 * SAHOOL Event Bus - Type Definitions
 * تعريفات أنواع ناقل الأحداث في سهول
 *
 * Central registry for all cross-service events with type-safe definitions.
 * Uses discriminated unions for compile-time event type checking.
 *
 * @packageDocumentation
 */

import type { z } from "zod";
import type {
  // Common types
  EventMetadata,
  Severity,
  Priority,
  Currency,

  // Payload types
  FieldCreatedPayload,
  FieldUpdatedPayload,
  FieldDeletedPayload,
  FarmCreatedPayload,
  WeatherForecastPayload,
  WeatherAlertPayload,
  SatelliteDataReadyPayload,
  SatelliteAnomalyPayload,
  DiseaseDetectedPayload,
  CropStressPayload,
  LowStockPayload,
  InventoryMovementPayload,
  BatchExpiredPayload,
  SubscriptionCreatedPayload,
  PaymentCompletedPayload,
  PaymentFailedPayload,
  TaskCreatedPayload,
  TaskCompletedPayload,
  AlertCreatedPayload,
  SensorReadingPayload,
  DeviceConnectedPayload,
  DeviceDisconnectedPayload,
  NotificationSendPayload,
  UserCreatedPayload,
  UserUpdatedPayload,
  OrderPlacedPayload,
  OrderCompletedPayload,
  OrderCancelledPayload,
  AgentExecutionStartedPayload,
  AgentExecutionCompletedPayload,
  AgentExecutionFailedPayload,
  RecommendationCreatedPayload,
} from "./schemas";

import { EventSubjects } from "./subjects";

// Re-export types from schemas
export type {
  EventMetadata,
  Severity,
  Priority,
  Currency,
  FieldCreatedPayload,
  FieldUpdatedPayload,
  FieldDeletedPayload,
  FarmCreatedPayload,
  WeatherForecastPayload,
  WeatherAlertPayload,
  SatelliteDataReadyPayload,
  SatelliteAnomalyPayload,
  DiseaseDetectedPayload,
  CropStressPayload,
  LowStockPayload,
  InventoryMovementPayload,
  BatchExpiredPayload,
  SubscriptionCreatedPayload,
  PaymentCompletedPayload,
  PaymentFailedPayload,
  TaskCreatedPayload,
  TaskCompletedPayload,
  AlertCreatedPayload,
  SensorReadingPayload,
  DeviceConnectedPayload,
  DeviceDisconnectedPayload,
  NotificationSendPayload,
  UserCreatedPayload,
  UserUpdatedPayload,
  OrderPlacedPayload,
  OrderCompletedPayload,
  OrderCancelledPayload,
  AgentExecutionStartedPayload,
  AgentExecutionCompletedPayload,
  AgentExecutionFailedPayload,
  RecommendationCreatedPayload,
};

// Re-export subjects
export { EventSubjects };
export type { EventSubject } from "./subjects";

// ============================================================================
// Base Event Interface - واجهة الحدث الأساسية
// ============================================================================

/**
 * Base event structure that all events must conform to.
 * الهيكل الأساسي للحدث الذي يجب أن تتوافق معه جميع الأحداث
 */
export interface BaseEvent<
  TType extends string = string,
  TPayload = unknown
> {
  /** Unique event identifier | معرف الحدث الفريد */
  eventId: string;
  /** Event type (matches NATS subject) | نوع الحدث */
  eventType: TType;
  /** Event timestamp | طابع وقت الحدث */
  timestamp: Date | string;
  /** Schema version | إصدار المخطط */
  version: string;
  /** Event payload | حمولة الحدث */
  payload: TPayload;
  /** Optional metadata | البيانات الوصفية الاختيارية */
  metadata?: EventMetadata;
}

// ============================================================================
// Field Events - أحداث الحقول
// ============================================================================

/** Field created event | حدث إنشاء حقل */
export interface FieldCreatedEvent extends BaseEvent<
  typeof EventSubjects.FIELD_CREATED,
  FieldCreatedPayload
> {}

/** Field updated event | حدث تحديث حقل */
export interface FieldUpdatedEvent extends BaseEvent<
  typeof EventSubjects.FIELD_UPDATED,
  FieldUpdatedPayload
> {}

/** Field deleted event | حدث حذف حقل */
export interface FieldDeletedEvent extends BaseEvent<
  typeof EventSubjects.FIELD_DELETED,
  FieldDeletedPayload
> {}

/** Union of all field events | اتحاد جميع أحداث الحقول */
export type FieldEvent =
  | FieldCreatedEvent
  | FieldUpdatedEvent
  | FieldDeletedEvent;

// ============================================================================
// Farm Events - أحداث المزارع
// ============================================================================

/** Farm created event | حدث إنشاء مزرعة */
export interface FarmCreatedEvent extends BaseEvent<
  typeof EventSubjects.FARM_CREATED,
  FarmCreatedPayload
> {}

/** Farm updated event | حدث تحديث مزرعة */
export interface FarmUpdatedEvent extends BaseEvent<
  typeof EventSubjects.FARM_UPDATED,
  Partial<FarmCreatedPayload> & { farmId: string }
> {}

/** Farm deleted event | حدث حذف مزرعة */
export interface FarmDeletedEvent extends BaseEvent<
  typeof EventSubjects.FARM_DELETED,
  { farmId: string; tenantId: string; deletedAt: Date | string }
> {}

/** Union of all farm events | اتحاد جميع أحداث المزارع */
export type FarmEvent =
  | FarmCreatedEvent
  | FarmUpdatedEvent
  | FarmDeletedEvent;

// ============================================================================
// Weather Events - أحداث الطقس
// ============================================================================

/** Weather forecast event | حدث توقعات الطقس */
export interface WeatherForecastEvent extends BaseEvent<
  typeof EventSubjects.WEATHER_FORECAST,
  WeatherForecastPayload
> {}

/** Weather alert event | حدث تنبيه الطقس */
export interface WeatherAlertEvent extends BaseEvent<
  typeof EventSubjects.WEATHER_ALERT,
  WeatherAlertPayload
> {}

/** Union of all weather events | اتحاد جميع أحداث الطقس */
export type WeatherEvent =
  | WeatherForecastEvent
  | WeatherAlertEvent;

// ============================================================================
// Satellite Events - أحداث الأقمار الصناعية
// ============================================================================

/** Satellite data ready event | حدث جاهزية بيانات الأقمار الصناعية */
export interface SatelliteDataReadyEvent extends BaseEvent<
  typeof EventSubjects.SATELLITE_DATA_READY,
  SatelliteDataReadyPayload
> {}

/** Satellite anomaly event | حدث شذوذ الأقمار الصناعية */
export interface SatelliteAnomalyEvent extends BaseEvent<
  typeof EventSubjects.SATELLITE_ANOMALY,
  SatelliteAnomalyPayload
> {}

/** NDVI computed event | حدث حساب NDVI */
export interface NDVIComputedEvent extends BaseEvent<
  typeof EventSubjects.NDVI_COMPUTED,
  SatelliteDataReadyPayload
> {}

/** Union of all satellite events | اتحاد جميع أحداث الأقمار الصناعية */
export type SatelliteEvent =
  | SatelliteDataReadyEvent
  | SatelliteAnomalyEvent
  | NDVIComputedEvent;

// ============================================================================
// Health Events - أحداث الصحة النباتية
// ============================================================================

/** Disease detected event | حدث اكتشاف مرض */
export interface DiseaseDetectedEvent extends BaseEvent<
  typeof EventSubjects.HEALTH_DISEASE_DETECTED,
  DiseaseDetectedPayload
> {}

/** Pest detected event | حدث اكتشاف آفة */
export interface PestDetectedEvent extends BaseEvent<
  typeof EventSubjects.HEALTH_PEST_DETECTED,
  DiseaseDetectedPayload
> {}

/** Crop stress event | حدث إجهاد المحصول */
export interface CropStressEvent extends BaseEvent<
  typeof EventSubjects.HEALTH_STRESS_DETECTED,
  CropStressPayload
> {}

/** Union of all health events | اتحاد جميع أحداث الصحة */
export type HealthEvent =
  | DiseaseDetectedEvent
  | PestDetectedEvent
  | CropStressEvent;

// ============================================================================
// Inventory Events - أحداث المخزون
// ============================================================================

/** Low stock event | حدث انخفاض المخزون */
export interface InventoryLowStockEvent extends BaseEvent<
  typeof EventSubjects.INVENTORY_LOW_STOCK,
  LowStockPayload
> {}

/** Inventory movement event | حدث حركة المخزون */
export interface InventoryMovementEvent extends BaseEvent<
  typeof EventSubjects.INVENTORY_MOVEMENT,
  InventoryMovementPayload
> {}

/** Batch expired event | حدث انتهاء صلاحية الدفعة */
export interface BatchExpiredEvent extends BaseEvent<
  typeof EventSubjects.INVENTORY_BATCH_EXPIRED,
  BatchExpiredPayload
> {}

/** Union of all inventory events | اتحاد جميع أحداث المخزون */
export type InventoryEvent =
  | InventoryLowStockEvent
  | InventoryMovementEvent
  | BatchExpiredEvent;

// ============================================================================
// Billing Events - أحداث الفوترة
// ============================================================================

/** Subscription created event | حدث إنشاء اشتراك */
export interface SubscriptionCreatedEvent extends BaseEvent<
  typeof EventSubjects.BILLING_SUBSCRIPTION_CREATED,
  SubscriptionCreatedPayload
> {}

/** Payment completed event | حدث اكتمال الدفع */
export interface PaymentCompletedEvent extends BaseEvent<
  typeof EventSubjects.BILLING_PAYMENT_COMPLETED,
  PaymentCompletedPayload
> {}

/** Payment failed event | حدث فشل الدفع */
export interface PaymentFailedEvent extends BaseEvent<
  typeof EventSubjects.BILLING_PAYMENT_FAILED,
  PaymentFailedPayload
> {}

/** Union of all billing events | اتحاد جميع أحداث الفوترة */
export type BillingEvent =
  | SubscriptionCreatedEvent
  | PaymentCompletedEvent
  | PaymentFailedEvent;

// ============================================================================
// Task Events - أحداث المهام
// ============================================================================

/** Task created event | حدث إنشاء مهمة */
export interface TaskCreatedEvent extends BaseEvent<
  typeof EventSubjects.TASK_CREATED,
  TaskCreatedPayload
> {}

/** Task completed event | حدث اكتمال مهمة */
export interface TaskCompletedEvent extends BaseEvent<
  typeof EventSubjects.TASK_COMPLETED,
  TaskCompletedPayload
> {}

/** Union of all task events | اتحاد جميع أحداث المهام */
export type TaskEvent =
  | TaskCreatedEvent
  | TaskCompletedEvent;

// ============================================================================
// Alert Events - أحداث التنبيهات
// ============================================================================

/** Alert created event | حدث إنشاء تنبيه */
export interface AlertCreatedEvent extends BaseEvent<
  typeof EventSubjects.ALERT_CREATED,
  AlertCreatedPayload
> {}

/** Alert acknowledged event | حدث تأكيد التنبيه */
export interface AlertAcknowledgedEvent extends BaseEvent<
  typeof EventSubjects.ALERT_ACKNOWLEDGED,
  { alertId: string; acknowledgedBy: string; acknowledgedAt: Date | string }
> {}

/** Alert resolved event | حدث حل التنبيه */
export interface AlertResolvedEvent extends BaseEvent<
  typeof EventSubjects.ALERT_RESOLVED,
  { alertId: string; resolvedBy: string; resolvedAt: Date | string; resolution?: string }
> {}

/** Union of all alert events | اتحاد جميع أحداث التنبيهات */
export type AlertEvent =
  | AlertCreatedEvent
  | AlertAcknowledgedEvent
  | AlertResolvedEvent;

// ============================================================================
// IoT/Sensor Events - أحداث إنترنت الأشياء
// ============================================================================

/** Sensor reading event | حدث قراءة المستشعر */
export interface SensorReadingEvent extends BaseEvent<
  typeof EventSubjects.IOT_SENSOR_READING,
  SensorReadingPayload
> {}

/** Device connected event | حدث اتصال الجهاز */
export interface DeviceConnectedEvent extends BaseEvent<
  typeof EventSubjects.IOT_SENSOR_CONNECTED,
  DeviceConnectedPayload
> {}

/** Device disconnected event | حدث انقطاع الجهاز */
export interface DeviceDisconnectedEvent extends BaseEvent<
  typeof EventSubjects.IOT_SENSOR_DISCONNECTED,
  DeviceDisconnectedPayload
> {}

/** Union of all sensor events | اتحاد جميع أحداث المستشعرات */
export type SensorEvent =
  | SensorReadingEvent
  | DeviceConnectedEvent
  | DeviceDisconnectedEvent;

// ============================================================================
// Notification Events - أحداث الإشعارات
// ============================================================================

/** Notification send event | حدث إرسال إشعار */
export interface NotificationSendEvent extends BaseEvent<
  typeof EventSubjects.NOTIFICATION_SEND,
  NotificationSendPayload
> {}

/** Notification delivered event | حدث توصيل الإشعار */
export interface NotificationDeliveredEvent extends BaseEvent<
  typeof EventSubjects.NOTIFICATION_DELIVERED,
  { notificationId: string; deliveredAt: Date | string }
> {}

/** Notification failed event | حدث فشل الإشعار */
export interface NotificationFailedEvent extends BaseEvent<
  typeof EventSubjects.NOTIFICATION_FAILED,
  { notificationId: string; failureReason: string; failedAt: Date | string }
> {}

/** Union of all notification events | اتحاد جميع أحداث الإشعارات */
export type NotificationEvent =
  | NotificationSendEvent
  | NotificationDeliveredEvent
  | NotificationFailedEvent;

// ============================================================================
// User Events - أحداث المستخدمين
// ============================================================================

/** User created event | حدث إنشاء مستخدم */
export interface UserCreatedEvent extends BaseEvent<
  typeof EventSubjects.USER_CREATED,
  UserCreatedPayload
> {}

/** User updated event | حدث تحديث مستخدم */
export interface UserUpdatedEvent extends BaseEvent<
  typeof EventSubjects.USER_UPDATED,
  UserUpdatedPayload
> {}

/** User deleted event | حدث حذف مستخدم */
export interface UserDeletedEvent extends BaseEvent<
  typeof EventSubjects.USER_DELETED,
  { userId: string; deletedAt: Date | string }
> {}

/** Union of all user events | اتحاد جميع أحداث المستخدمين */
export type UserEvent =
  | UserCreatedEvent
  | UserUpdatedEvent
  | UserDeletedEvent;

// ============================================================================
// Order Events - أحداث الطلبات
// ============================================================================

/** Order placed event | حدث تقديم طلب */
export interface OrderPlacedEvent extends BaseEvent<
  typeof EventSubjects.ORDER_PLACED,
  OrderPlacedPayload
> {}

/** Order completed event | حدث اكتمال طلب */
export interface OrderCompletedEvent extends BaseEvent<
  typeof EventSubjects.ORDER_COMPLETED,
  OrderCompletedPayload
> {}

/** Order cancelled event | حدث إلغاء طلب */
export interface OrderCancelledEvent extends BaseEvent<
  typeof EventSubjects.ORDER_CANCELLED,
  OrderCancelledPayload
> {}

/** Union of all order events | اتحاد جميع أحداث الطلبات */
export type OrderEvent =
  | OrderPlacedEvent
  | OrderCompletedEvent
  | OrderCancelledEvent;

// ============================================================================
// Agent Events - أحداث الوكلاء
// ============================================================================

/** Agent execution started event | حدث بدء تنفيذ الوكيل */
export interface AgentExecutionStartedEvent extends BaseEvent<
  typeof EventSubjects.AGENT_EXECUTION_STARTED,
  AgentExecutionStartedPayload
> {}

/** Agent execution completed event | حدث اكتمال تنفيذ الوكيل */
export interface AgentExecutionCompletedEvent extends BaseEvent<
  typeof EventSubjects.AGENT_EXECUTION_COMPLETED,
  AgentExecutionCompletedPayload
> {}

/** Agent execution failed event | حدث فشل تنفيذ الوكيل */
export interface AgentExecutionFailedEvent extends BaseEvent<
  typeof EventSubjects.AGENT_EXECUTION_FAILED,
  AgentExecutionFailedPayload
> {}

/** Union of all agent events | اتحاد جميع أحداث الوكلاء */
export type AgentEvent =
  | AgentExecutionStartedEvent
  | AgentExecutionCompletedEvent
  | AgentExecutionFailedEvent;

// ============================================================================
// Recommendation Events - أحداث التوصيات
// ============================================================================

/** Recommendation created event | حدث إنشاء توصية */
export interface RecommendationCreatedEvent extends BaseEvent<
  typeof EventSubjects.RECOMMENDATION_CREATED,
  RecommendationCreatedPayload
> {}

/** Union of all recommendation events | اتحاد جميع أحداث التوصيات */
export type RecommendationEvent = RecommendationCreatedEvent;

// ============================================================================
// Master Union Type - نوع الاتحاد الرئيسي
// ============================================================================

/**
 * Union of all SAHOOL events.
 * اتحاد جميع أحداث سهول
 *
 * This type can be used for generic event handling.
 */
export type SahoolEvent =
  | FieldEvent
  | FarmEvent
  | WeatherEvent
  | SatelliteEvent
  | HealthEvent
  | InventoryEvent
  | BillingEvent
  | TaskEvent
  | AlertEvent
  | SensorEvent
  | NotificationEvent
  | UserEvent
  | OrderEvent
  | AgentEvent
  | RecommendationEvent;

// ============================================================================
// Event Type Guards - حراس أنواع الأحداث
// ============================================================================

/**
 * Check if an event is a field event.
 * التحقق مما إذا كان الحدث حدث حقل
 */
export function isFieldEvent(event: SahoolEvent): event is FieldEvent {
  return event.eventType.startsWith("sahool.field.");
}

/**
 * Check if an event is a farm event.
 * التحقق مما إذا كان الحدث حدث مزرعة
 */
export function isFarmEvent(event: SahoolEvent): event is FarmEvent {
  return event.eventType.startsWith("sahool.farm.");
}

/**
 * Check if an event is a weather event.
 * التحقق مما إذا كان الحدث حدث طقس
 */
export function isWeatherEvent(event: SahoolEvent): event is WeatherEvent {
  return event.eventType.startsWith("sahool.weather.");
}

/**
 * Check if an event is a satellite event.
 * التحقق مما إذا كان الحدث حدث قمر صناعي
 */
export function isSatelliteEvent(event: SahoolEvent): event is SatelliteEvent {
  return event.eventType.startsWith("sahool.satellite.");
}

/**
 * Check if an event is a health event.
 * التحقق مما إذا كان الحدث حدث صحة
 */
export function isHealthEvent(event: SahoolEvent): event is HealthEvent {
  return event.eventType.startsWith("sahool.health.");
}

/**
 * Check if an event is an inventory event.
 * التحقق مما إذا كان الحدث حدث مخزون
 */
export function isInventoryEvent(event: SahoolEvent): event is InventoryEvent {
  return event.eventType.startsWith("sahool.inventory.");
}

/**
 * Check if an event is a billing event.
 * التحقق مما إذا كان الحدث حدث فوترة
 */
export function isBillingEvent(event: SahoolEvent): event is BillingEvent {
  return event.eventType.startsWith("sahool.billing.");
}

/**
 * Check if an event is a task event.
 * التحقق مما إذا كان الحدث حدث مهمة
 */
export function isTaskEvent(event: SahoolEvent): event is TaskEvent {
  return event.eventType.startsWith("sahool.task.");
}

/**
 * Check if an event is an alert event.
 * التحقق مما إذا كان الحدث حدث تنبيه
 */
export function isAlertEvent(event: SahoolEvent): event is AlertEvent {
  return event.eventType.startsWith("sahool.alert.");
}

/**
 * Check if an event is a sensor/IoT event.
 * التحقق مما إذا كان الحدث حدث مستشعر
 */
export function isSensorEvent(event: SahoolEvent): event is SensorEvent {
  return event.eventType.startsWith("sahool.iot.");
}

/**
 * Check if an event is a notification event.
 * التحقق مما إذا كان الحدث حدث إشعار
 */
export function isNotificationEvent(event: SahoolEvent): event is NotificationEvent {
  return event.eventType.startsWith("sahool.notification.");
}

/**
 * Check if an event is a user event.
 * التحقق مما إذا كان الحدث حدث مستخدم
 */
export function isUserEvent(event: SahoolEvent): event is UserEvent {
  return event.eventType.startsWith("sahool.user.");
}

/**
 * Check if an event is an order event.
 * التحقق مما إذا كان الحدث حدث طلب
 */
export function isOrderEvent(event: SahoolEvent): event is OrderEvent {
  return event.eventType.startsWith("sahool.order.");
}

/**
 * Check if an event is an agent event.
 * التحقق مما إذا كان الحدث حدث وكيل
 */
export function isAgentEvent(event: SahoolEvent): event is AgentEvent {
  return event.eventType.startsWith("sahool.agent.");
}

/**
 * Check if an event is a recommendation event.
 * التحقق مما إذا كان الحدث حدث توصية
 */
export function isRecommendationEvent(event: SahoolEvent): event is RecommendationEvent {
  return event.eventType.startsWith("sahool.recommendation.");
}

// ============================================================================
// Event Domain Extraction - استخراج مجال الحدث
// ============================================================================

/**
 * Extract the domain from an event type.
 * استخراج المجال من نوع الحدث
 *
 * @param eventType - Event type string (e.g., "sahool.field.created")
 * @returns Domain name (e.g., "field")
 */
export function getEventDomain(eventType: string): string | null {
  const parts = eventType.split(".");
  if (parts.length >= 2 && parts[0] === "sahool") {
    return parts[1];
  }
  return null;
}

/**
 * Extract the action from an event type.
 * استخراج الإجراء من نوع الحدث
 *
 * @param eventType - Event type string (e.g., "sahool.field.created")
 * @returns Action name (e.g., "created")
 */
export function getEventAction(eventType: string): string | null {
  const parts = eventType.split(".");
  if (parts.length >= 3) {
    return parts.slice(2).join(".");
  }
  return null;
}
