# @sahool/shared-events

Shared NATS event bus for SAHOOL microservices. This package provides a unified event publishing and subscription system for cross-service communication.

## Features

- **Singleton NATS Connection**: Automatic connection management with reconnection logic
- **Type-Safe Events**: Full TypeScript support with strongly-typed event definitions
- **Easy Publishing**: Simple helper functions for publishing events
- **Flexible Subscriptions**: Subscribe to individual events or patterns
- **Queue Groups**: Built-in support for load balancing across service instances
- **Debug Logging**: Optional logging for development and debugging

## Installation

```bash
npm install @sahool/shared-events
```

## Quick Start

### Initialize NATS Connection

```typescript
import { initializeNatsClient } from '@sahool/shared-events';

// Initialize at application startup
await initializeNatsClient({
  servers: process.env.NATS_URL || 'nats://localhost:4222',
  name: 'my-service',
  debug: true,
});
```

### Publishing Events

```typescript
import { publishFieldCreated, publishOrderPlaced } from '@sahool/shared-events';

// Publish a field creation event
await publishFieldCreated({
  fieldId: 'field-123',
  userId: 'user-456',
  name: 'North Field',
  area: 1000,
  location: {
    type: 'Polygon',
    coordinates: [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
  },
  cropType: 'wheat',
});

// Publish an order event
await publishOrderPlaced({
  orderId: 'order-789',
  userId: 'user-456',
  items: [
    { productId: 'product-1', quantity: 2, price: 50.0 },
  ],
  totalAmount: 100.0,
  currency: 'USD',
});
```

### Subscribing to Events

```typescript
import { subscribe, subscribeToFieldEvents, EventSubjects } from '@sahool/shared-events';

// Subscribe to a specific event
await subscribe(EventSubjects.FIELD_CREATED, async (event) => {
  console.log('Field created:', event.payload);
});

// Subscribe to all field events using pattern
await subscribeToFieldEvents(async (event) => {
  console.log('Field event:', event.eventType, event.payload);
});

// Subscribe with queue group for load balancing
await subscribe(
  EventSubjects.ORDER_PLACED,
  async (event) => {
    // Process order
  },
  { queue: 'order-processors' }
);
```

### Using Logging Handler

```typescript
import { subscribeAll, createLoggingHandler } from '@sahool/shared-events';

// Log all events for debugging
await subscribeAll(createLoggingHandler('[EventBus]'));
```

## Event Types

### Field Events
- `field.created` - New field created
- `field.updated` - Field information updated
- `field.deleted` - Field deleted

### Order Events
- `order.placed` - New order placed
- `order.completed` - Order completed
- `order.cancelled` - Order cancelled

### Sensor Events
- `sensor.reading` - Sensor data reading
- `device.connected` - Device connected
- `device.disconnected` - Device disconnected

### User Events
- `user.created` - New user registered
- `user.updated` - User information updated

### Inventory Events
- `inventory.low_stock` - Stock level below threshold
- `inventory.movement` - Inventory movement recorded

### Notification Events
- `notification.send` - Notification to be sent

## Advanced Usage

### Custom Event Publishing

```typescript
import { publishEvent } from '@sahool/shared-events';

await publishEvent('custom.event', {
  customField: 'value',
}, {
  version: '2.0',
  metadata: {
    source: 'my-service',
  },
});
```

### Pattern Subscriptions

```typescript
import { subscribePattern } from '@sahool/shared-events';

// Subscribe to all creation events
await subscribePattern('*.created', async (event) => {
  console.log('Something was created:', event);
});

// Subscribe to all events
await subscribePattern('>', async (event) => {
  console.log('Event received:', event);
});
```

## Environment Variables

- `NATS_URL` - NATS server URL (default: `nats://localhost:4222`)
- `NODE_ENV` - Environment mode (affects debug logging)

## License

MIT
