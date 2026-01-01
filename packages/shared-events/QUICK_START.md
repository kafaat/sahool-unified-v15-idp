# SAHOOL Event Bus - Quick Start Guide

## Installation

Add the shared-events package to your service:

```bash
# In your service's package.json
{
  "dependencies": {
    "@sahool/shared-events": "file:../../../packages/shared-events",
    "nats": "^2.28.2",
    "uuid": "^10.0.0"
  }
}
```

Then install:

```bash
npm install
```

## Basic Usage

### 1. Initialize NATS Connection

**In your main application file (e.g., `main.ts` or `index.ts`):**

```typescript
import { initializeNatsClient } from '@sahool/shared-events';

async function bootstrap() {
  // Initialize NATS before starting your service
  await initializeNatsClient({
    servers: process.env.NATS_URL || 'nats://localhost:4222',
    name: 'your-service-name',
    debug: process.env.NODE_ENV !== 'production',
  });

  // ... rest of your app initialization
}

bootstrap();
```

### 2. Publishing Events

**Example: Publishing a field created event**

```typescript
import { publishFieldCreated } from '@sahool/shared-events';

async function createField(data: any) {
  // Create the field in your database
  const field = await db.field.create(data);

  // Publish the event
  await publishFieldCreated({
    fieldId: field.id,
    userId: data.userId,
    name: field.name,
    area: field.area,
    location: field.location,
    cropType: field.cropType,
  });

  return field;
}
```

**Example: Publishing an order placed event**

```typescript
import { publishOrderPlaced } from '@sahool/shared-events';

async function createOrder(orderData: any) {
  const order = await db.order.create(orderData);

  await publishOrderPlaced({
    orderId: order.id,
    userId: order.buyerId,
    items: order.items.map((item) => ({
      productId: item.productId,
      quantity: item.quantity,
      price: item.price,
    })),
    totalAmount: order.totalAmount,
    currency: 'YER',
  });

  return order;
}
```

### 3. Subscribing to Events

**Example: Subscribe to a specific event**

```typescript
import { subscribe, EventSubjects } from '@sahool/shared-events';

// Subscribe to field created events
await subscribe(EventSubjects.FIELD_CREATED, async (event) => {
  console.log('Field created:', event.payload.fieldId);

  // Do something with the event
  await updateAnalytics(event.payload);
});
```

**Example: Subscribe to all events of a type**

```typescript
import { subscribeToOrderEvents } from '@sahool/shared-events';

// Subscribe to all order events (placed, completed, cancelled)
await subscribeToOrderEvents(async (event) => {
  console.log('Order event:', event.eventType);

  switch (event.eventType) {
    case 'order.placed':
      await handleOrderPlaced(event.payload);
      break;
    case 'order.completed':
      await handleOrderCompleted(event.payload);
      break;
    case 'order.cancelled':
      await handleOrderCancelled(event.payload);
      break;
  }
});
```

**Example: Subscribe with queue group (for load balancing)**

```typescript
import { subscribe, EventSubjects } from '@sahool/shared-events';

// Multiple instances will share the work
await subscribe(
  EventSubjects.SENSOR_READING,
  async (event) => {
    await processSensorReading(event.payload);
  },
  {
    queue: 'sensor-processors' // All instances in this queue share the load
  }
);
```

**Example: Subscribe to pattern**

```typescript
import { subscribePattern } from '@sahool/shared-events';

// Subscribe to all field events
await subscribePattern('field.*', async (event) => {
  console.log('Field event:', event.eventType);
});

// Subscribe to all creation events
await subscribePattern('*.created', async (event) => {
  console.log('Something was created:', event.eventType);
});

// Subscribe to ALL events
await subscribePattern('>', async (event) => {
  console.log('Event:', event.eventType);
});
```

## Available Events

### Field Events
```typescript
publishFieldCreated(payload)
publishFieldUpdated(payload)
publishFieldDeleted(payload)
```

### Order Events
```typescript
publishOrderPlaced(payload)
publishOrderCompleted(payload)
publishOrderCancelled(payload)
```

### Sensor Events
```typescript
publishSensorReading(payload)
publishDeviceConnected(payload)
publishDeviceDisconnected(payload)
```

### User Events
```typescript
publishUserCreated(payload)
publishUserUpdated(payload)
```

### Inventory Events
```typescript
publishInventoryLowStock(payload)
publishInventoryMovement(payload)
```

### Notification Events
```typescript
publishNotificationSend(payload)
```

## NestJS Integration Example

**Create an events module:**

```typescript
// events/events.module.ts
import { Module, OnModuleInit } from '@nestjs/common';
import { EventsService } from './events.service';

@Module({
  providers: [EventsService],
  exports: [EventsService],
})
export class EventsModule implements OnModuleInit {
  constructor(private eventsService: EventsService) {}

  async onModuleInit() {
    await this.eventsService.connect();
  }
}
```

**Create an events service:**

```typescript
// events/events.service.ts
import { Injectable, Logger } from '@nestjs/common';
import {
  initializeNatsClient,
  publishOrderPlaced,
  subscribeAll,
  createLoggingHandler,
} from '@sahool/shared-events';

@Injectable()
export class EventsService {
  private readonly logger = new Logger(EventsService.name);

  async connect() {
    await initializeNatsClient({
      servers: process.env.NATS_URL,
      name: 'my-service',
    });

    // Subscribe to events for logging in development
    if (process.env.NODE_ENV !== 'production') {
      await subscribeAll(createLoggingHandler('[MyService]'));
    }

    this.logger.log('Connected to NATS event bus');
  }

  async publishOrder(orderData: any) {
    await publishOrderPlaced(orderData);
  }
}
```

**Use in your app module:**

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { EventsModule } from './events/events.module';

@Module({
  imports: [EventsModule],
  // ...
})
export class AppModule {}
```

## Error Handling

Events are published asynchronously and won't block your application if NATS is unavailable:

```typescript
import { publishOrderPlaced } from '@sahool/shared-events';

async function createOrder(data: any) {
  const order = await db.order.create(data);

  // Event publishing won't throw if NATS is down
  // Errors are logged but don't affect the order creation
  try {
    await publishOrderPlaced({
      orderId: order.id,
      userId: order.buyerId,
      items: order.items,
      totalAmount: order.totalAmount,
      currency: 'YER',
    });
  } catch (error) {
    console.error('Failed to publish order event:', error);
    // Order is still created, event can be re-published later
  }

  return order;
}
```

## Debug Logging

Enable debug logging in development:

```typescript
await initializeNatsClient({
  servers: process.env.NATS_URL,
  name: 'my-service',
  debug: true, // Will log all connection events and published messages
});
```

Or use the logging handler:

```typescript
import { subscribeAll, createLoggingHandler } from '@sahool/shared-events';

// Subscribe to all events and log them
await subscribeAll(createLoggingHandler('[MyService]'));
```

## Best Practices

1. **Initialize once**: Call `initializeNatsClient()` once at application startup
2. **Don't block**: Event publishing is async but shouldn't block critical operations
3. **Use queue groups**: For scalability, use queue groups when multiple instances process the same events
4. **Handle errors**: Always wrap event publishing in try-catch
5. **Log in development**: Use the logging subscriber to see all events during development
6. **Type safety**: Use TypeScript types provided by the package
7. **Event versioning**: Use the version field in publish options if you change event structure

## Troubleshooting

**NATS connection failed:**
- Check that NATS is running: `docker-compose ps nats`
- Verify NATS_URL environment variable
- Check network connectivity

**Events not received:**
- Verify subscription is active before events are published
- Check subject/pattern matches the event type
- Ensure NATS connection is established

**Multiple event deliveries:**
- Use queue groups to ensure single delivery across instances
- Check for duplicate subscriptions

## Environment Variables

```bash
# Required
NATS_URL=nats://nats:4222

# Optional
SERVICE_NAME=my-service
NODE_ENV=development
```

## More Information

- Full API documentation: See [README.md](./README.md)
- Event type definitions: See [src/events.ts](./src/events.ts)
- Example integration: See `/apps/services/marketplace-service/`
