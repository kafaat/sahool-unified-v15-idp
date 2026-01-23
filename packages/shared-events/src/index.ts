/**
 * SAHOOL Shared Events Package
 * حزمة الأحداث المشتركة في سهول
 *
 * Unified event bus for microservices communication via NATS.
 * Provides type-safe event definitions, validation, and publishing.
 *
 * @packageDocumentation
 */

// ============================================================================
// Re-export NATS Client
// ============================================================================

export {
  NatsClient,
  type NatsClientConfig,
  initializeNatsClient,
  getNatsConnection,
} from "./nats-client";

// ============================================================================
// Re-export Subjects
// ============================================================================

export {
  // Subject constants
  EventSubjects,
  type EventSubject,

  // Individual subject constants
  SAHOOL_FIELD_CREATED,
  SAHOOL_FIELD_UPDATED,
  SAHOOL_FIELD_DELETED,
  SAHOOL_FIELD_ALL,
  SAHOOL_FARM_CREATED,
  SAHOOL_FARM_UPDATED,
  SAHOOL_FARM_DELETED,
  SAHOOL_FARM_ALL,
  SAHOOL_WEATHER_FORECAST,
  SAHOOL_WEATHER_ALERT,
  SAHOOL_WEATHER_ALL,
  SAHOOL_SATELLITE_DATA_READY,
  SAHOOL_SATELLITE_ANOMALY,
  SAHOOL_SATELLITE_ALL,
  SAHOOL_HEALTH_DISEASE_DETECTED,
  SAHOOL_HEALTH_STRESS_DETECTED,
  SAHOOL_HEALTH_ALL,
  SAHOOL_INVENTORY_LOW_STOCK,
  SAHOOL_INVENTORY_MOVEMENT,
  SAHOOL_INVENTORY_ALL,
  SAHOOL_BILLING_SUBSCRIPTION_CREATED,
  SAHOOL_BILLING_PAYMENT_COMPLETED,
  SAHOOL_BILLING_ALL,
  SAHOOL_TASK_CREATED,
  SAHOOL_TASK_COMPLETED,
  SAHOOL_TASK_ALL,
  SAHOOL_ALERT_CREATED,
  SAHOOL_ALERT_ALL,
  SAHOOL_IOT_SENSOR_READING,
  SAHOOL_IOT_ALL,
  SAHOOL_NOTIFICATION_SEND,
  SAHOOL_NOTIFICATION_ALL,
  SAHOOL_USER_CREATED,
  SAHOOL_USER_UPDATED,
  SAHOOL_USER_ALL,
  SAHOOL_ORDER_PLACED,
  SAHOOL_ORDER_ALL,
  SAHOOL_AGENT_EXECUTION_STARTED,
  SAHOOL_AGENT_ALL,
  SAHOOL_RECOMMENDATION_CREATED,
  SAHOOL_RECOMMENDATION_ALL,
  SAHOOL_SYSTEM_HEALTH,
  SAHOOL_SYSTEM_ALL,

  // Utility functions
  getSubjectForEvent,
  getWildcardSubject,
  isValidSubject,
  getTenantSubject,
  getTenantWildcard,
  extractDomain,
} from "./subjects";

// ============================================================================
// Re-export Event Types
// ============================================================================

export {
  // Base types
  type BaseEvent,
  type SahoolEvent,

  // Payload types
  type EventMetadata,
  type Severity,
  type Priority,
  type Currency,
  type FieldCreatedPayload,
  type FieldUpdatedPayload,
  type FieldDeletedPayload,
  type FarmCreatedPayload,
  type WeatherForecastPayload,
  type WeatherAlertPayload,
  type SatelliteDataReadyPayload,
  type SatelliteAnomalyPayload,
  type DiseaseDetectedPayload,
  type CropStressPayload,
  type LowStockPayload,
  type InventoryMovementPayload,
  type BatchExpiredPayload,
  type SubscriptionCreatedPayload,
  type PaymentCompletedPayload,
  type PaymentFailedPayload,
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
  type AgentExecutionStartedPayload,
  type AgentExecutionCompletedPayload,
  type AgentExecutionFailedPayload,
  type RecommendationCreatedPayload,

  // Event types
  type FieldEvent,
  type FieldCreatedEvent,
  type FieldUpdatedEvent,
  type FieldDeletedEvent,
  type FarmEvent,
  type FarmCreatedEvent,
  type WeatherEvent,
  type WeatherForecastEvent,
  type WeatherAlertEvent,
  type SatelliteEvent,
  type SatelliteDataReadyEvent,
  type SatelliteAnomalyEvent,
  type HealthEvent,
  type DiseaseDetectedEvent,
  type CropStressEvent,
  type InventoryEvent,
  type InventoryLowStockEvent,
  type InventoryMovementEvent,
  type BillingEvent,
  type SubscriptionCreatedEvent,
  type PaymentCompletedEvent,
  type TaskEvent,
  type TaskCreatedEvent,
  type TaskCompletedEvent,
  type AlertEvent,
  type AlertCreatedEvent,
  type SensorEvent,
  type SensorReadingEvent,
  type DeviceConnectedEvent,
  type DeviceDisconnectedEvent,
  type NotificationEvent,
  type NotificationSendEvent,
  type UserEvent,
  type UserCreatedEvent,
  type UserUpdatedEvent,
  type OrderEvent,
  type OrderPlacedEvent,
  type OrderCompletedEvent,
  type OrderCancelledEvent,
  type AgentEvent,
  type AgentExecutionStartedEvent,
  type AgentExecutionCompletedEvent,
  type AgentExecutionFailedEvent,
  type RecommendationEvent,
  type RecommendationCreatedEvent,

  // Type guards
  isFieldEvent,
  isFarmEvent,
  isWeatherEvent,
  isSatelliteEvent,
  isHealthEvent,
  isInventoryEvent,
  isBillingEvent,
  isTaskEvent,
  isAlertEvent,
  isSensorEvent,
  isNotificationEvent,
  isUserEvent,
  isOrderEvent,
  isAgentEvent,
  isRecommendationEvent,

  // Utility functions
  getEventDomain,
  getEventAction,
} from "./events";

// ============================================================================
// Re-export Schemas (for validation)
// ============================================================================

export {
  // Schema objects
  EventSchemas,
  BaseEventSchema,
  EventMetadataSchema,

  // Common schemas
  UUIDSchema,
  ISODateSchema,
  GeoJSONPolygonSchema,
  SeveritySchema,
  PrioritySchema,
  CurrencySchema,
  NotificationChannelSchema,

  // Field schemas
  FieldCreatedPayloadSchema,
  FieldUpdatedPayloadSchema,
  FieldDeletedPayloadSchema,

  // Weather schemas
  WeatherAlertTypeSchema,
  WeatherForecastPayloadSchema,
  WeatherAlertPayloadSchema,

  // Satellite schemas
  SatelliteAnomalyTypeSchema,
  SatelliteDataReadyPayloadSchema,
  SatelliteAnomalyPayloadSchema,

  // Health schemas
  StressTypeSchema,
  DiseaseDetectedPayloadSchema,
  CropStressPayloadSchema,

  // Inventory schemas
  MovementTypeSchema,
  LowStockPayloadSchema,
  InventoryMovementPayloadSchema,
  BatchExpiredPayloadSchema,

  // Billing schemas
  PlanTierSchema,
  BillingCycleSchema,
  PaymentMethodSchema,
  SubscriptionCreatedPayloadSchema,
  PaymentCompletedPayloadSchema,
  PaymentFailedPayloadSchema,

  // Task schemas
  TaskCreatedPayloadSchema,
  TaskCompletedPayloadSchema,

  // Alert schemas
  AlertTypeSchema,
  AlertCreatedPayloadSchema,

  // IoT schemas
  SensorTypeSchema,
  DisconnectReasonSchema,
  SensorReadingPayloadSchema,
  DeviceConnectedPayloadSchema,
  DeviceDisconnectedPayloadSchema,

  // Notification schemas
  RecipientTypeSchema,
  NotificationSendPayloadSchema,

  // User schemas
  UserCreatedPayloadSchema,
  UserUpdatedPayloadSchema,

  // Order schemas
  OrderItemSchema,
  ShippingAddressSchema,
  OrderPlacedPayloadSchema,
  OrderCompletedPayloadSchema,
  OrderCancelledPayloadSchema,

  // Agent schemas
  AgentTypeSchema,
  ExecutionModeSchema,
  AgentExecutionStartedPayloadSchema,
  AgentExecutionCompletedPayloadSchema,
  AgentExecutionFailedPayloadSchema,

  // Recommendation schemas
  RecommendationTypeSchema,
  RecommendationCreatedPayloadSchema,

  // Validation utilities
  validatePayload,
  safeValidatePayload,
  createPayload,
} from "./schemas";

// ============================================================================
// Re-export Publishers
// ============================================================================

export {
  type PublishOptions,
  publishEvent,
  publishValidatedEvent,

  // Field publishers
  publishFieldCreated,
  publishFieldUpdated,
  publishFieldDeleted,

  // Weather publishers
  publishWeatherForecast,
  publishWeatherAlert,

  // Satellite publishers
  publishSatelliteDataReady,
  publishSatelliteAnomaly,

  // Health publishers
  publishDiseaseDetected,
  publishCropStress,

  // Inventory publishers
  publishInventoryLowStock,
  publishInventoryMovement,

  // Task publishers
  publishTaskCreated,
  publishTaskCompleted,

  // Alert publishers
  publishAlertCreated,

  // IoT publishers
  publishSensorReading,
  publishDeviceConnected,
  publishDeviceDisconnected,

  // Notification publishers
  publishNotificationSend,

  // User publishers
  publishUserCreated,
  publishUserUpdated,

  // Order publishers
  publishOrderPlaced,
  publishOrderCompleted,
  publishOrderCancelled,

  // Billing publishers
  publishSubscriptionCreated,
  publishPaymentCompleted,

  // Agent publishers
  publishAgentExecutionStarted,
  publishAgentExecutionCompleted,
  publishAgentExecutionFailed,

  // Recommendation publishers
  publishRecommendationCreated,
} from "./publisher";

// ============================================================================
// Re-export Subscribers
// ============================================================================

export {
  type EventHandler,
  type SubscribeOptions,
  subscribe,
  subscribePattern,
  subscribeAll,
  unsubscribe,

  // Convenience subscribers
  subscribeToFieldEvents,
  subscribeToOrderEvents,
  subscribeToSensorEvents,
  subscribeToDeviceEvents,
  subscribeToUserEvents,
  subscribeToInventoryEvents,
  subscribeToNotificationEvents,

  // Utilities
  createLoggingHandler,
} from "./subscriber";
