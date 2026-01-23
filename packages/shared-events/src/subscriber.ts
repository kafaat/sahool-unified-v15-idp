/**
 * SAHOOL Event Bus - Event Subscriber
 * مشترك الأحداث - مساعدات للاشتراك في الأحداث من NATS
 *
 * Helper functions for subscribing to events from NATS with type safety.
 *
 * @packageDocumentation
 */

import { StringCodec, Subscription } from "nats";
import { NatsClient } from "./nats-client";
import type { SahoolEvent } from "./events";
import type { EventSubject } from "./subjects";
import {
  SAHOOL_FIELD_ALL,
  SAHOOL_FARM_ALL,
  SAHOOL_WEATHER_ALL,
  SAHOOL_SATELLITE_ALL,
  SAHOOL_HEALTH_ALL,
  SAHOOL_INVENTORY_ALL,
  SAHOOL_BILLING_ALL,
  SAHOOL_TASK_ALL,
  SAHOOL_ALERT_ALL,
  SAHOOL_IOT_ALL,
  SAHOOL_IOT_SENSOR_ALL,
  SAHOOL_IOT_DEVICE_ALL,
  SAHOOL_NOTIFICATION_ALL,
  SAHOOL_USER_ALL,
  SAHOOL_ORDER_ALL,
  SAHOOL_AGENT_ALL,
  SAHOOL_RECOMMENDATION_ALL,
  SAHOOL_SYSTEM_ALL,
  getTenantWildcard,
} from "./subjects";

const codec = StringCodec();

// ============================================================================
// Types - الأنواع
// ============================================================================

/**
 * Event handler function type.
 * نوع دالة معالج الأحداث
 */
export type EventHandler<T extends SahoolEvent = SahoolEvent> = (
  event: T,
  subject: string
) => Promise<void> | void;

/**
 * Options for subscribing to events.
 * خيارات الاشتراك في الأحداث
 */
export interface SubscribeOptions {
  /**
   * Queue group name for load balancing across multiple instances.
   * اسم مجموعة الانتظار لتوزيع الحمل
   */
  queue?: string;

  /**
   * Whether to log received events (default: true in development).
   * تسجيل الأحداث المستلمة
   */
  debug?: boolean;

  /**
   * Error handler for subscription errors.
   * معالج أخطاء الاشتراك
   */
  onError?: (error: Error) => void;

  /**
   * Tenant ID for tenant-scoped subscriptions.
   * معرف المستأجر للاشتراكات المحددة النطاق
   */
  tenantId?: string;
}

// ============================================================================
// Core Subscription Functions - دوال الاشتراك الأساسية
// ============================================================================

/**
 * Subscribe to a specific event subject.
 * الاشتراك في موضوع حدث محدد
 *
 * @param subject - NATS subject or wildcard pattern
 * @param handler - Event handler function
 * @param options - Subscription options
 * @returns NATS subscription
 */
export async function subscribe<T extends SahoolEvent = SahoolEvent>(
  subject: EventSubject | string,
  handler: EventHandler<T>,
  options: SubscribeOptions = {}
): Promise<Subscription> {
  const client = NatsClient.getInstance({
    servers: process.env.NATS_URL || "nats://localhost:4222",
  });

  const connection = client.getConnection();
  if (!connection || connection.isClosed()) {
    throw new Error("NATS connection is not available. Please connect first.");
  }

  // Build subject with optional tenant scoping
  let actualSubject = subject;
  if (options.tenantId) {
    const parts = subject.split(".");
    if (parts[0] === "sahool" && parts.length >= 2) {
      const domain = parts[1];
      const rest = parts.slice(2).join(".") || "*";
      actualSubject = `sahool.tenant.${options.tenantId}.${domain}.${rest}`;
    }
  }

  const subscription = options.queue
    ? connection.subscribe(actualSubject, { queue: options.queue })
    : connection.subscribe(actualSubject);

  if (options.debug !== false && process.env.NODE_ENV !== "production") {
    console.log(
      `[EventSubscriber] Subscribed to: ${actualSubject}${
        options.queue ? ` (queue: ${options.queue})` : ""
      }`
    );
  }

  // Process messages asynchronously
  (async () => {
    for await (const msg of subscription) {
      try {
        const data = codec.decode(msg.data);
        const event = JSON.parse(data) as T;

        if (options.debug !== false && process.env.NODE_ENV !== "production") {
          console.log(
            `[EventSubscriber] Received event on ${msg.subject}:`,
            event.eventType
          );
        }

        await handler(event, msg.subject);
      } catch (error) {
        console.error(
          `[EventSubscriber] Error processing message on ${msg.subject}:`,
          error
        );
        if (options.onError) {
          options.onError(error as Error);
        }
      }
    }
  })().catch((err) => {
    console.error(`[EventSubscriber] Subscription error on ${actualSubject}:`, err);
    if (options.onError) {
      options.onError(err);
    }
  });

  return subscription;
}

/**
 * Subscribe to multiple subjects using a wildcard pattern.
 * الاشتراك في موضوعات متعددة باستخدام نمط شامل
 *
 * Examples:
 * - 'sahool.field.*' - all field events
 * - 'sahool.*.created' - all creation events
 * - '>' - all events
 *
 * @param pattern - Wildcard pattern
 * @param handler - Event handler
 * @param options - Subscription options
 */
export async function subscribePattern<T extends SahoolEvent = SahoolEvent>(
  pattern: string,
  handler: EventHandler<T>,
  options: SubscribeOptions = {}
): Promise<Subscription> {
  return subscribe(pattern, handler, options);
}

/**
 * Subscribe to all SAHOOL events.
 * الاشتراك في جميع أحداث سهول
 *
 * @param handler - Event handler
 * @param options - Subscription options
 */
export async function subscribeAll(
  handler: EventHandler<SahoolEvent>,
  options: SubscribeOptions = {}
): Promise<Subscription> {
  const pattern = options.tenantId
    ? getTenantWildcard(options.tenantId)
    : "sahool.>";
  return subscribe(pattern, handler, options);
}

// ============================================================================
// Domain-Specific Subscribers - المشتركون الخاصون بالمجال
// ============================================================================

/**
 * Subscribe to all field events.
 * الاشتراك في جميع أحداث الحقول
 */
export async function subscribeToFieldEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_FIELD_ALL, handler, options);
}

/**
 * Subscribe to all farm events.
 * الاشتراك في جميع أحداث المزارع
 */
export async function subscribeToFarmEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_FARM_ALL, handler, options);
}

/**
 * Subscribe to all weather events.
 * الاشتراك في جميع أحداث الطقس
 */
export async function subscribeToWeatherEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_WEATHER_ALL, handler, options);
}

/**
 * Subscribe to all satellite events.
 * الاشتراك في جميع أحداث الأقمار الصناعية
 */
export async function subscribeToSatelliteEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_SATELLITE_ALL, handler, options);
}

/**
 * Subscribe to all health events (disease, pest, stress).
 * الاشتراك في جميع أحداث الصحة
 */
export async function subscribeToHealthEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_HEALTH_ALL, handler, options);
}

/**
 * Subscribe to all inventory events.
 * الاشتراك في جميع أحداث المخزون
 */
export async function subscribeToInventoryEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_INVENTORY_ALL, handler, options);
}

/**
 * Subscribe to all billing events.
 * الاشتراك في جميع أحداث الفوترة
 */
export async function subscribeToBillingEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_BILLING_ALL, handler, options);
}

/**
 * Subscribe to all task events.
 * الاشتراك في جميع أحداث المهام
 */
export async function subscribeToTaskEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_TASK_ALL, handler, options);
}

/**
 * Subscribe to all alert events.
 * الاشتراك في جميع أحداث التنبيهات
 */
export async function subscribeToAlertEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_ALERT_ALL, handler, options);
}

/**
 * Subscribe to all IoT events (sensors and devices).
 * الاشتراك في جميع أحداث إنترنت الأشياء
 */
export async function subscribeToIoTEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_IOT_ALL, handler, options);
}

/**
 * Subscribe to all sensor events.
 * الاشتراك في جميع أحداث المستشعرات
 */
export async function subscribeToSensorEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_IOT_SENSOR_ALL, handler, options);
}

/**
 * Subscribe to all device events.
 * الاشتراك في جميع أحداث الأجهزة
 */
export async function subscribeToDeviceEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_IOT_DEVICE_ALL, handler, options);
}

/**
 * Subscribe to all notification events.
 * الاشتراك في جميع أحداث الإشعارات
 */
export async function subscribeToNotificationEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_NOTIFICATION_ALL, handler, options);
}

/**
 * Subscribe to all user events.
 * الاشتراك في جميع أحداث المستخدمين
 */
export async function subscribeToUserEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_USER_ALL, handler, options);
}

/**
 * Subscribe to all order events.
 * الاشتراك في جميع أحداث الطلبات
 */
export async function subscribeToOrderEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_ORDER_ALL, handler, options);
}

/**
 * Subscribe to all agent events.
 * الاشتراك في جميع أحداث الوكلاء
 */
export async function subscribeToAgentEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_AGENT_ALL, handler, options);
}

/**
 * Subscribe to all recommendation events.
 * الاشتراك في جميع أحداث التوصيات
 */
export async function subscribeToRecommendationEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_RECOMMENDATION_ALL, handler, options);
}

/**
 * Subscribe to all system events.
 * الاشتراك في جميع أحداث النظام
 */
export async function subscribeToSystemEvents(
  handler: EventHandler,
  options?: SubscribeOptions
): Promise<Subscription> {
  return subscribePattern(SAHOOL_SYSTEM_ALL, handler, options);
}

// ============================================================================
// Tenant-Scoped Subscriptions - الاشتراكات المحددة النطاق للمستأجرين
// ============================================================================

/**
 * Subscribe to all events for a specific tenant.
 * الاشتراك في جميع أحداث مستأجر محدد
 *
 * @param tenantId - Tenant identifier
 * @param handler - Event handler
 * @param options - Subscription options
 */
export async function subscribeToTenantEvents(
  tenantId: string,
  handler: EventHandler,
  options?: Omit<SubscribeOptions, "tenantId">
): Promise<Subscription> {
  const pattern = getTenantWildcard(tenantId);
  return subscribe(pattern, handler, { ...options, tenantId: undefined });
}

/**
 * Subscribe to a specific domain for a tenant.
 * الاشتراك في مجال محدد لمستأجر
 *
 * @param tenantId - Tenant identifier
 * @param domain - Event domain (e.g., "field", "weather")
 * @param handler - Event handler
 * @param options - Subscription options
 */
export async function subscribeToTenantDomain(
  tenantId: string,
  domain: string,
  handler: EventHandler,
  options?: Omit<SubscribeOptions, "tenantId">
): Promise<Subscription> {
  const pattern = getTenantWildcard(tenantId, domain);
  return subscribe(pattern, handler, { ...options, tenantId: undefined });
}

// ============================================================================
// Utility Functions - دوال المساعدة
// ============================================================================

/**
 * Unsubscribe from a subscription.
 * إلغاء الاشتراك
 *
 * @param subscription - NATS subscription to drain
 */
export async function unsubscribe(subscription: Subscription): Promise<void> {
  await subscription.drain();
}

/**
 * Create a logging handler for debugging.
 * إنشاء معالج تسجيل للتصحيح
 *
 * @param prefix - Log prefix
 */
export function createLoggingHandler(prefix = "[Event]"): EventHandler {
  return (event: SahoolEvent, subject: string) => {
    console.log(`${prefix} [${subject}]`, {
      eventId: event.eventId,
      eventType: event.eventType,
      timestamp: event.timestamp,
      payload: event.payload,
      metadata: event.metadata,
    });
  };
}

/**
 * Create a filtering handler that only processes events matching a predicate.
 * إنشاء معالج تصفية يعالج فقط الأحداث المطابقة
 *
 * @param predicate - Filter function
 * @param handler - Event handler
 */
export function createFilteringHandler<T extends SahoolEvent>(
  predicate: (event: T) => boolean,
  handler: EventHandler<T>
): EventHandler<T> {
  return async (event: T, subject: string) => {
    if (predicate(event)) {
      await handler(event, subject);
    }
  };
}

/**
 * Create a handler that validates events before processing.
 * إنشاء معالج يتحقق من صحة الأحداث قبل المعالجة
 *
 * @param validator - Validation function (throws on invalid)
 * @param handler - Event handler
 * @param onValidationError - Error handler for validation failures
 */
export function createValidatingHandler<T extends SahoolEvent>(
  validator: (event: T) => void,
  handler: EventHandler<T>,
  onValidationError?: (error: Error, event: T) => void
): EventHandler<T> {
  return async (event: T, subject: string) => {
    try {
      validator(event);
      await handler(event, subject);
    } catch (error) {
      if (onValidationError) {
        onValidationError(error as Error, event);
      } else {
        console.error(`[EventSubscriber] Validation error:`, error);
      }
    }
  };
}
