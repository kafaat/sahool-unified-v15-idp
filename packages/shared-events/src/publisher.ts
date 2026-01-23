/**
 * SAHOOL Event Bus - Event Publisher
 * ناشر الأحداث - مساعدات لنشر الأحداث إلى NATS
 *
 * Provides type-safe event publishing with optional payload validation.
 *
 * @packageDocumentation
 */

import { StringCodec } from "nats";
import { v4 as uuidv4 } from "uuid";
import { NatsClient } from "./nats-client";
import { EventSubjects, type EventSubject } from "./subjects";
import type { SahoolEvent, EventMetadata } from "./events";
import {
  EventSchemas,
  safeValidatePayload,
  type FieldCreatedPayload,
  type FieldUpdatedPayload,
  type FieldDeletedPayload,
  type WeatherForecastPayload,
  type WeatherAlertPayload,
  type SatelliteDataReadyPayload,
  type SatelliteAnomalyPayload,
  type DiseaseDetectedPayload,
  type CropStressPayload,
  type LowStockPayload,
  type InventoryMovementPayload,
  type TaskCreatedPayload,
  type TaskCompletedPayload,
  type AlertCreatedPayload,
  type SensorReadingPayload,
  type DeviceConnectedPayload,
  type DeviceDisconnectedPayload,
  type NotificationSendPayload,
  type UserCreatedPayload,
  type UserUpdatedPayload,
  type OrderPlacedPayload,
  type OrderCompletedPayload,
  type OrderCancelledPayload,
  type SubscriptionCreatedPayload,
  type PaymentCompletedPayload,
  type AgentExecutionStartedPayload,
  type AgentExecutionCompletedPayload,
  type AgentExecutionFailedPayload,
  type RecommendationCreatedPayload,
} from "./schemas";

const codec = StringCodec();

// ============================================================================
// Publish Options - خيارات النشر
// ============================================================================

/**
 * Options for publishing events.
 * خيارات نشر الأحداث
 */
export interface PublishOptions {
  /**
   * Override the default event ID generation
   * تجاوز توليد معرف الحدث الافتراضي
   */
  eventId?: string;

  /**
   * Event version (defaults to '1.0')
   * إصدار الحدث
   */
  version?: string;

  /**
   * Additional metadata to attach to the event
   * البيانات الوصفية الإضافية
   */
  metadata?: EventMetadata;

  /**
   * Timeout for publish operation in milliseconds (default: 5000)
   * مهلة عملية النشر
   */
  timeout?: number;

  /**
   * Whether to log the publish operation (default: true in development)
   * تسجيل عملية النشر
   */
  debug?: boolean;

  /**
   * Whether to validate the payload before publishing (default: true)
   * التحقق من صحة الحمولة قبل النشر
   */
  validate?: boolean;

  /**
   * Tenant ID for tenant-scoped subjects
   * معرف المستأجر
   */
  tenantId?: string;
}

// ============================================================================
// Base Publish Function - دالة النشر الأساسية
// ============================================================================

/**
 * Publish any event to NATS with optional validation.
 * نشر أي حدث إلى NATS مع التحقق الاختياري
 *
 * @param subject - NATS subject to publish to
 * @param payload - Event payload
 * @param options - Publishing options
 * @throws Error if validation fails or connection unavailable
 */
export async function publishEvent<T = unknown>(
  subject: EventSubject | string,
  payload: T,
  options: PublishOptions = {}
): Promise<void> {
  const client = NatsClient.getInstance({
    servers: process.env.NATS_URL || "nats://localhost:4222",
  });

  const connection = client.getConnection();
  if (!connection || connection.isClosed()) {
    throw new Error("NATS connection is not available. Please connect first.");
  }

  // Build the full subject (with optional tenant scoping)
  let fullSubject = subject;
  if (options.tenantId) {
    // Extract domain and action from subject
    const parts = subject.split(".");
    if (parts[0] === "sahool" && parts.length >= 3) {
      const domain = parts[1];
      const action = parts.slice(2).join(".");
      fullSubject = `sahool.tenant.${options.tenantId}.${domain}.${action}`;
    }
  }

  const event: SahoolEvent = {
    eventId: options.eventId || uuidv4(),
    eventType: subject,
    timestamp: new Date(),
    version: options.version || "1.0",
    payload,
    metadata: options.metadata,
  } as SahoolEvent;

  const data = codec.encode(JSON.stringify(event));

  if (options.debug !== false && process.env.NODE_ENV !== "production") {
    console.log(`[EventPublisher] Publishing event: ${fullSubject}`, event);
  }

  connection.publish(fullSubject, data);

  // Optionally wait for the publish to complete with timeout
  if (options.timeout) {
    await connection.flush();
  }
}

/**
 * Publish an event with validation against its schema.
 * نشر حدث مع التحقق من صحته
 *
 * @param subject - NATS subject
 * @param schemaName - Schema name for validation
 * @param payload - Event payload
 * @param options - Publishing options
 */
export async function publishValidatedEvent<T extends keyof typeof EventSchemas>(
  subject: EventSubject | string,
  schemaName: T,
  payload: unknown,
  options: PublishOptions = {}
): Promise<void> {
  if (options.validate !== false) {
    const result = safeValidatePayload(schemaName, payload);
    if (!result.success) {
      throw new Error(
        `Payload validation failed for ${schemaName}: ${result.error.message}`
      );
    }
  }

  await publishEvent(subject, payload, options);
}

// ============================================================================
// Field Event Publishers - ناشرات أحداث الحقول
// ============================================================================

/**
 * Publish a field created event.
 * نشر حدث إنشاء حقل
 */
export async function publishFieldCreated(
  payload: FieldCreatedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.FIELD_CREATED,
    "FieldCreated",
    payload,
    options
  );
}

/**
 * Publish a field updated event.
 * نشر حدث تحديث حقل
 */
export async function publishFieldUpdated(
  payload: FieldUpdatedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.FIELD_UPDATED,
    "FieldUpdated",
    payload,
    options
  );
}

/**
 * Publish a field deleted event.
 * نشر حدث حذف حقل
 */
export async function publishFieldDeleted(
  payload: FieldDeletedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.FIELD_DELETED,
    "FieldDeleted",
    payload,
    options
  );
}

// ============================================================================
// Weather Event Publishers - ناشرات أحداث الطقس
// ============================================================================

/**
 * Publish a weather forecast event.
 * نشر حدث توقعات الطقس
 */
export async function publishWeatherForecast(
  payload: WeatherForecastPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.WEATHER_FORECAST,
    "WeatherForecast",
    payload,
    options
  );
}

/**
 * Publish a weather alert event.
 * نشر حدث تنبيه الطقس
 */
export async function publishWeatherAlert(
  payload: WeatherAlertPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.WEATHER_ALERT,
    "WeatherAlert",
    payload,
    options
  );
}

// ============================================================================
// Satellite Event Publishers - ناشرات أحداث الأقمار الصناعية
// ============================================================================

/**
 * Publish a satellite data ready event.
 * نشر حدث جاهزية بيانات الأقمار الصناعية
 */
export async function publishSatelliteDataReady(
  payload: SatelliteDataReadyPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.SATELLITE_DATA_READY,
    "SatelliteDataReady",
    payload,
    options
  );
}

/**
 * Publish a satellite anomaly event.
 * نشر حدث شذوذ الأقمار الصناعية
 */
export async function publishSatelliteAnomaly(
  payload: SatelliteAnomalyPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.SATELLITE_ANOMALY,
    "SatelliteAnomaly",
    payload,
    options
  );
}

// ============================================================================
// Health Event Publishers - ناشرات أحداث الصحة
// ============================================================================

/**
 * Publish a disease detected event.
 * نشر حدث اكتشاف مرض
 */
export async function publishDiseaseDetected(
  payload: DiseaseDetectedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.HEALTH_DISEASE_DETECTED,
    "DiseaseDetected",
    payload,
    options
  );
}

/**
 * Publish a crop stress event.
 * نشر حدث إجهاد المحصول
 */
export async function publishCropStress(
  payload: CropStressPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.HEALTH_STRESS_DETECTED,
    "CropStress",
    payload,
    options
  );
}

// ============================================================================
// Inventory Event Publishers - ناشرات أحداث المخزون
// ============================================================================

/**
 * Publish a low stock event.
 * نشر حدث انخفاض المخزون
 */
export async function publishInventoryLowStock(
  payload: LowStockPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.INVENTORY_LOW_STOCK,
    "LowStock",
    payload,
    options
  );
}

/**
 * Publish an inventory movement event.
 * نشر حدث حركة المخزون
 */
export async function publishInventoryMovement(
  payload: InventoryMovementPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.INVENTORY_MOVEMENT,
    "InventoryMovement",
    payload,
    options
  );
}

// ============================================================================
// Task Event Publishers - ناشرات أحداث المهام
// ============================================================================

/**
 * Publish a task created event.
 * نشر حدث إنشاء مهمة
 */
export async function publishTaskCreated(
  payload: TaskCreatedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.TASK_CREATED,
    "TaskCreated",
    payload,
    options
  );
}

/**
 * Publish a task completed event.
 * نشر حدث اكتمال مهمة
 */
export async function publishTaskCompleted(
  payload: TaskCompletedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.TASK_COMPLETED,
    "TaskCompleted",
    payload,
    options
  );
}

// ============================================================================
// Alert Event Publishers - ناشرات أحداث التنبيهات
// ============================================================================

/**
 * Publish an alert created event.
 * نشر حدث إنشاء تنبيه
 */
export async function publishAlertCreated(
  payload: AlertCreatedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.ALERT_CREATED,
    "AlertCreated",
    payload,
    options
  );
}

// ============================================================================
// IoT/Sensor Event Publishers - ناشرات أحداث المستشعرات
// ============================================================================

/**
 * Publish a sensor reading event.
 * نشر حدث قراءة مستشعر
 */
export async function publishSensorReading(
  payload: SensorReadingPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.IOT_SENSOR_READING,
    "SensorReading",
    payload,
    options
  );
}

/**
 * Publish a device connected event.
 * نشر حدث اتصال جهاز
 */
export async function publishDeviceConnected(
  payload: DeviceConnectedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.IOT_SENSOR_CONNECTED,
    "DeviceConnected",
    payload,
    options
  );
}

/**
 * Publish a device disconnected event.
 * نشر حدث انقطاع جهاز
 */
export async function publishDeviceDisconnected(
  payload: DeviceDisconnectedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.IOT_SENSOR_DISCONNECTED,
    "DeviceDisconnected",
    payload,
    options
  );
}

// ============================================================================
// Notification Event Publishers - ناشرات أحداث الإشعارات
// ============================================================================

/**
 * Publish a notification send event.
 * نشر حدث إرسال إشعار
 */
export async function publishNotificationSend(
  payload: NotificationSendPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.NOTIFICATION_SEND,
    "NotificationSend",
    payload,
    options
  );
}

// ============================================================================
// User Event Publishers - ناشرات أحداث المستخدمين
// ============================================================================

/**
 * Publish a user created event.
 * نشر حدث إنشاء مستخدم
 */
export async function publishUserCreated(
  payload: UserCreatedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.USER_CREATED,
    "UserCreated",
    payload,
    options
  );
}

/**
 * Publish a user updated event.
 * نشر حدث تحديث مستخدم
 */
export async function publishUserUpdated(
  payload: UserUpdatedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.USER_UPDATED,
    "UserUpdated",
    payload,
    options
  );
}

// ============================================================================
// Order Event Publishers - ناشرات أحداث الطلبات
// ============================================================================

/**
 * Publish an order placed event.
 * نشر حدث تقديم طلب
 */
export async function publishOrderPlaced(
  payload: OrderPlacedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.ORDER_PLACED,
    "OrderPlaced",
    payload,
    options
  );
}

/**
 * Publish an order completed event.
 * نشر حدث اكتمال طلب
 */
export async function publishOrderCompleted(
  payload: OrderCompletedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.ORDER_COMPLETED,
    "OrderCompleted",
    payload,
    options
  );
}

/**
 * Publish an order cancelled event.
 * نشر حدث إلغاء طلب
 */
export async function publishOrderCancelled(
  payload: OrderCancelledPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.ORDER_CANCELLED,
    "OrderCancelled",
    payload,
    options
  );
}

// ============================================================================
// Billing Event Publishers - ناشرات أحداث الفوترة
// ============================================================================

/**
 * Publish a subscription created event.
 * نشر حدث إنشاء اشتراك
 */
export async function publishSubscriptionCreated(
  payload: SubscriptionCreatedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.BILLING_SUBSCRIPTION_CREATED,
    "SubscriptionCreated",
    payload,
    options
  );
}

/**
 * Publish a payment completed event.
 * نشر حدث اكتمال الدفع
 */
export async function publishPaymentCompleted(
  payload: PaymentCompletedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.BILLING_PAYMENT_COMPLETED,
    "PaymentCompleted",
    payload,
    options
  );
}

// ============================================================================
// Agent Event Publishers - ناشرات أحداث الوكلاء
// ============================================================================

/**
 * Publish an agent execution started event.
 * نشر حدث بدء تنفيذ الوكيل
 */
export async function publishAgentExecutionStarted(
  payload: AgentExecutionStartedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.AGENT_EXECUTION_STARTED,
    "AgentExecutionStarted",
    payload,
    options
  );
}

/**
 * Publish an agent execution completed event.
 * نشر حدث اكتمال تنفيذ الوكيل
 */
export async function publishAgentExecutionCompleted(
  payload: AgentExecutionCompletedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.AGENT_EXECUTION_COMPLETED,
    "AgentExecutionCompleted",
    payload,
    options
  );
}

/**
 * Publish an agent execution failed event.
 * نشر حدث فشل تنفيذ الوكيل
 */
export async function publishAgentExecutionFailed(
  payload: AgentExecutionFailedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.AGENT_EXECUTION_FAILED,
    "AgentExecutionFailed",
    payload,
    options
  );
}

// ============================================================================
// Recommendation Event Publishers - ناشرات أحداث التوصيات
// ============================================================================

/**
 * Publish a recommendation created event.
 * نشر حدث إنشاء توصية
 */
export async function publishRecommendationCreated(
  payload: RecommendationCreatedPayload,
  options?: PublishOptions
): Promise<void> {
  await publishValidatedEvent(
    EventSubjects.RECOMMENDATION_CREATED,
    "RecommendationCreated",
    payload,
    options
  );
}
