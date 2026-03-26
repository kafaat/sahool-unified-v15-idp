/**
 * SAHOOL Shared Events Package
 * Unified event bus for microservices communication via NATS
 *
 * @packageDocumentation
 */

// Export NATS client and utilities
export {
  NatsClient,
  NatsClientConfig,
  initializeNatsClient,
  getNatsConnection,
} from './nats-client';

// Export event type definitions
export {
  // Base types
  BaseEvent,
  SahoolEvent,
  EventSubject,
  EventSubjects,

  // Field events
  FieldEvent,
  FieldCreatedEvent,
  FieldUpdatedEvent,
  FieldDeletedEvent,

  // Order events
  OrderEvent,
  OrderPlacedEvent,
  OrderCompletedEvent,
  OrderCancelledEvent,

  // Sensor events
  SensorEvent,
  SensorReadingEvent,
  DeviceConnectedEvent,
  DeviceDisconnectedEvent,

  // User events
  UserEvent,
  UserCreatedEvent,
  UserUpdatedEvent,

  // Inventory events
  InventoryEvent,
  InventoryLowStockEvent,
  InventoryMovementEvent,

  // Notification events
  NotificationEvent,
  NotificationSendEvent,
} from './events';

// Export publisher functions
export {
  PublishOptions,
  publishEvent,

  // Field publishers
  publishFieldCreated,
  publishFieldUpdated,
  publishFieldDeleted,

  // Order publishers
  publishOrderPlaced,
  publishOrderCompleted,
  publishOrderCancelled,

  // Sensor publishers
  publishSensorReading,
  publishDeviceConnected,
  publishDeviceDisconnected,

  // User publishers
  publishUserCreated,
  publishUserUpdated,

  // Inventory publishers
  publishInventoryLowStock,
  publishInventoryMovement,

  // Notification publishers
  publishNotificationSend,
} from './publisher';

// Export subscriber functions
export {
  EventHandler,
  SubscribeOptions,
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
} from './subscriber';
