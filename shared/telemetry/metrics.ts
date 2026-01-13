/**
 * Prometheus Metrics for SAHOOL Platform (TypeScript/NestJS)
 * ===========================================================
 *
 * This module provides comprehensive metrics instrumentation for all
 * TypeScript-based services (NestJS) in the SAHOOL agricultural platform.
 *
 * Features:
 * - Prometheus client integration
 * - Request count, latency, error rate metrics
 * - Custom business metrics (fields, notifications, chat messages)
 * - Automatic metric labeling
 * - Metrics endpoint (/metrics)
 *
 * Usage:
 *     import { initMetrics, trackRequest, trackBusinessMetric } from './shared/telemetry/metrics';
 *
 *     // Initialize at application startup
 *     initMetrics({ serviceName: 'chat-service' });
 *
 *     // Track HTTP requests
 *     trackRequest('GET', '/messages', 200, 0.123);
 *
 *     // Track business metrics
 *     trackBusinessMetric('messages_sent', 1, { channel: 'field-chat' });
 *
 * Author: SAHOOL Platform Team
 * Date: 2025-12-26
 */

import * as promClient from "prom-client";
import { INestApplication } from "@nestjs/common";

let register: promClient.Registry;
let metricsInitialized = false;

// Standard HTTP metrics
let httpRequestsTotal: promClient.Counter<string>;
let httpRequestDuration: promClient.Histogram<string>;
let httpErrorsTotal: promClient.Counter<string>;

// Business metrics storage
const businessCounters: Map<string, promClient.Counter<string>> = new Map();
const businessHistograms: Map<string, promClient.Histogram<string>> = new Map();
const businessGauges: Map<string, promClient.Gauge<string>> = new Map();

export interface MetricsConfig {
  serviceName?: string;
  serviceVersion?: string;
  environment?: string;
  defaultLabels?: Record<string, string>;
  collectDefaultMetrics?: boolean;
}

/**
 * Initialize Prometheus metrics
 */
export function initMetrics(config: MetricsConfig = {}): promClient.Registry {
  if (metricsInitialized) {
    console.warn("Metrics already initialized");
    return register;
  }

  // Auto-detect service name from environment
  const serviceName =
    config.serviceName ||
    process.env.OTEL_SERVICE_NAME ||
    process.env.SERVICE_NAME ||
    "sahool-service";

  const serviceVersion =
    config.serviceVersion || process.env.SERVICE_VERSION || "1.0.0";
  const environment =
    config.environment || process.env.ENVIRONMENT || "development";

  // Create new registry
  register = new promClient.Registry();

  // Set default labels
  const defaultLabels = {
    service: serviceName,
    version: serviceVersion,
    environment,
    ...config.defaultLabels,
  };
  register.setDefaultLabels(defaultLabels);

  // Collect default Node.js metrics
  if (config.collectDefaultMetrics ?? true) {
    promClient.collectDefaultMetrics({ register });
  }

  // Initialize standard HTTP metrics
  httpRequestsTotal = new promClient.Counter({
    name: "http_requests_total",
    help: "Total number of HTTP requests",
    labelNames: ["method", "endpoint", "status_code"],
    registers: [register],
  });

  httpRequestDuration = new promClient.Histogram({
    name: "http_request_duration_seconds",
    help: "HTTP request duration in seconds",
    labelNames: ["method", "endpoint", "status_code"],
    buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
    registers: [register],
  });

  httpErrorsTotal = new promClient.Counter({
    name: "http_errors_total",
    help: "Total number of HTTP errors",
    labelNames: ["method", "endpoint", "status_code", "error_type"],
    registers: [register],
  });

  metricsInitialized = true;

  console.log(
    `Prometheus metrics initialized: service=${serviceName}, env=${environment}`,
  );

  return register;
}

/**
 * Get the metrics registry
 */
export function getRegistry(): promClient.Registry {
  if (!register) {
    throw new Error("Metrics not initialized. Call initMetrics() first.");
  }
  return register;
}

/**
 * Get metrics endpoint handler
 */
export async function getMetrics(): Promise<string> {
  return register.metrics();
}

/**
 * Track HTTP request metrics
 */
export function trackRequest(
  method: string,
  endpoint: string,
  statusCode: number,
  duration: number,
  labels?: Record<string, string>,
): void {
  if (!metricsInitialized) return;

  const metricLabels = {
    method,
    endpoint,
    status_code: statusCode.toString(),
    ...labels,
  };

  // Count request
  httpRequestsTotal.inc(metricLabels);

  // Record duration
  httpRequestDuration.observe(metricLabels, duration);

  // Count errors (4xx, 5xx)
  if (statusCode >= 400) {
    const errorType = statusCode < 500 ? "client_error" : "server_error";
    httpErrorsTotal.inc({
      ...metricLabels,
      error_type: errorType,
    });
  }
}

/**
 * Create a custom counter metric
 */
export function createCounter(
  name: string,
  help: string,
  labelNames: string[] = [],
): promClient.Counter<string> {
  if (!register) {
    throw new Error("Metrics not initialized");
  }

  const counter = new promClient.Counter({
    name,
    help,
    labelNames,
    registers: [register],
  });

  return counter;
}

/**
 * Create a custom histogram metric
 */
export function createHistogram(
  name: string,
  help: string,
  labelNames: string[] = [],
  buckets?: number[],
): promClient.Histogram<string> {
  if (!register) {
    throw new Error("Metrics not initialized");
  }

  const histogram = new promClient.Histogram({
    name,
    help,
    labelNames,
    buckets: buckets || [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
    registers: [register],
  });

  return histogram;
}

/**
 * Create a custom gauge metric
 */
export function createGauge(
  name: string,
  help: string,
  labelNames: string[] = [],
): promClient.Gauge<string> {
  if (!register) {
    throw new Error("Metrics not initialized");
  }

  const gauge = new promClient.Gauge({
    name,
    help,
    labelNames,
    registers: [register],
  });

  return gauge;
}

/**
 * Track custom business metrics
 */
export function trackBusinessMetric(
  metricName: string,
  value: number = 1,
  metricType: "counter" | "histogram" | "gauge" = "counter",
  labels?: Record<string, string>,
  help?: string,
): void {
  if (!metricsInitialized) return;

  const labelNames = labels ? Object.keys(labels) : [];

  if (metricType === "counter") {
    let counter = businessCounters.get(metricName);
    if (!counter) {
      counter = createCounter(
        metricName,
        help || `Business metric: ${metricName}`,
        labelNames,
      );
      businessCounters.set(metricName, counter);
    }
    counter.inc(labels || {}, value);
  } else if (metricType === "histogram") {
    let histogram = businessHistograms.get(metricName);
    if (!histogram) {
      histogram = createHistogram(
        metricName,
        help || `Business metric: ${metricName}`,
        labelNames,
      );
      businessHistograms.set(metricName, histogram);
    }
    histogram.observe(labels || {}, value);
  } else if (metricType === "gauge") {
    let gauge = businessGauges.get(metricName);
    if (!gauge) {
      gauge = createGauge(
        metricName,
        help || `Business metric: ${metricName}`,
        labelNames,
      );
      businessGauges.set(metricName, gauge);
    }
    gauge.set(labels || {}, value);
  }
}

/**
 * Middleware to track request duration
 */
export function trackRequestDuration(
  method: string,
  endpoint: string,
  labels?: Record<string, string>,
) {
  const startTime = Date.now();

  return (statusCode: number = 200) => {
    const duration = (Date.now() - startTime) / 1000;
    trackRequest(method, endpoint, statusCode, duration, labels);
  };
}

/**
 * Standard business metrics for SAHOOL platform
 */
export class SahoolMetrics {
  /**
   * Track chat message sent
   */
  static trackMessageSent(
    channel: string,
    messageType: string,
    userId: string,
  ): void {
    trackBusinessMetric(
      "sahool_messages_sent_total",
      1,
      "counter",
      { channel, message_type: messageType, user_id: userId },
      "Total number of chat messages sent",
    );
  }

  /**
   * Track notification sent
   */
  static trackNotificationSent(
    notificationType: string,
    channel: string,
    status: string,
  ): void {
    trackBusinessMetric(
      "sahool_notifications_sent_total",
      1,
      "counter",
      { notification_type: notificationType, channel, status },
      "Total number of notifications sent",
    );
  }

  /**
   * Track notification delivery latency
   */
  static trackNotificationLatency(
    notificationType: string,
    duration: number,
  ): void {
    trackBusinessMetric(
      "sahool_notification_duration_seconds",
      duration,
      "histogram",
      { notification_type: notificationType },
      "Notification delivery duration in seconds",
    );
  }

  /**
   * Track WebSocket connections
   */
  static trackWebSocketConnection(event: "connect" | "disconnect"): void {
    const gauge = businessGauges.get("sahool_websocket_connections");
    if (gauge) {
      if (event === "connect") {
        gauge.inc();
      } else {
        gauge.dec();
      }
    } else {
      const newGauge = createGauge(
        "sahool_websocket_connections",
        "Current number of WebSocket connections",
      );
      businessGauges.set("sahool_websocket_connections", newGauge);
      newGauge.set(event === "connect" ? 1 : 0);
    }
  }

  /**
   * Track billing transaction
   */
  static trackBillingTransaction(
    transactionType: string,
    amount: number,
    status: string,
  ): void {
    trackBusinessMetric(
      "sahool_billing_transactions_total",
      1,
      "counter",
      { transaction_type: transactionType, status },
      "Total number of billing transactions",
    );

    trackBusinessMetric(
      "sahool_billing_revenue",
      amount,
      "histogram",
      { transaction_type: transactionType },
      "Billing transaction revenue",
    );
  }

  /**
   * Track marketplace listing
   */
  static trackMarketplaceListing(
    listingType: string,
    action: "create" | "update" | "delete",
  ): void {
    trackBusinessMetric(
      "sahool_marketplace_listings_total",
      1,
      "counter",
      { listing_type: listingType, action },
      "Total number of marketplace listings",
    );
  }

  /**
   * Track inventory operation
   */
  static trackInventoryOperation(
    operationType: string,
    itemType: string,
    quantity: number,
  ): void {
    trackBusinessMetric(
      "sahool_inventory_operations_total",
      1,
      "counter",
      { operation_type: operationType, item_type: itemType },
      "Total number of inventory operations",
    );

    trackBusinessMetric(
      "sahool_inventory_quantity",
      quantity,
      "gauge",
      { item_type: itemType },
      "Current inventory quantity",
    );
  }

  /**
   * Track equipment usage
   */
  static trackEquipmentUsage(equipmentType: string, usageHours: number): void {
    trackBusinessMetric(
      "sahool_equipment_usage_hours",
      usageHours,
      "histogram",
      { equipment_type: equipmentType },
      "Equipment usage in hours",
    );
  }

  /**
   * Track task completion
   */
  static trackTaskCompletion(
    taskType: string,
    status: string,
    duration: number,
  ): void {
    trackBusinessMetric(
      "sahool_tasks_completed_total",
      1,
      "counter",
      { task_type: taskType, status },
      "Total number of tasks completed",
    );

    trackBusinessMetric(
      "sahool_task_duration_seconds",
      duration,
      "histogram",
      { task_type: taskType },
      "Task completion duration in seconds",
    );
  }

  /**
   * Track chat session duration
   */
  static trackChatSession(duration: number, participants: number): void {
    trackBusinessMetric(
      "sahool_chat_session_duration_seconds",
      duration,
      "histogram",
      {},
      "Chat session duration in seconds",
    );

    trackBusinessMetric(
      "sahool_chat_participants",
      participants,
      "histogram",
      {},
      "Number of chat participants",
    );
  }
}

/**
 * NestJS Interceptor for automatic request tracking
 */
export class MetricsInterceptor {
  async intercept(context: any, next: any): Promise<any> {
    const request = context.switchToHttp().getRequest();
    const response = context.switchToHttp().getResponse();

    const startTime = Date.now();
    const method = request.method;
    const endpoint = request.route?.path || request.url;

    try {
      const result = await next.handle().toPromise();
      const duration = (Date.now() - startTime) / 1000;
      trackRequest(method, endpoint, response.statusCode || 200, duration);
      return result;
    } catch (error) {
      const duration = (Date.now() - startTime) / 1000;
      trackRequest(method, endpoint, 500, duration);
      throw error;
    }
  }
}

export default {
  initMetrics,
  getRegistry,
  getMetrics,
  trackRequest,
  trackRequestDuration,
  createCounter,
  createHistogram,
  createGauge,
  trackBusinessMetric,
  SahoolMetrics,
  MetricsInterceptor,
};
