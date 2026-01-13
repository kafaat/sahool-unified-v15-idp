# NATS Event Bus Activation Summary

## Overview

Successfully activated the NATS Event Bus across SAHOOL services by creating a shared events package and integrating it into the marketplace service with real-world event publishing and logging.

## 1. Created @sahool/shared-events Package

**Location**: `/home/user/sahool-unified-v15-idp/packages/shared-events/`

### Package Structure

```
packages/shared-events/
├── package.json
├── tsconfig.json
├── README.md
└── src/
    ├── index.ts           # Main exports
    ├── events.ts          # Event type definitions
    ├── nats-client.ts     # Singleton NATS connection with reconnect logic
    ├── publisher.ts       # Event publishing helpers
    └── subscriber.ts      # Event subscription helpers
```

### Key Features

- **Singleton Pattern**: NatsClient ensures a single connection per service
- **Auto-Reconnection**: Automatic reconnection with configurable retry logic
- **Type Safety**: Full TypeScript support with strongly-typed events
- **Easy API**: Simple helper functions for common operations
- **Debug Logging**: Optional logging for development

## 2. Event Type Definitions

### Implemented Event Types

#### Field Events

- `field.created` - New field created
- `field.updated` - Field information updated
- `field.deleted` - Field deleted

#### Order Events

- `order.placed` - New order placed
- `order.completed` - Order completed
- `order.cancelled` - Order cancelled

#### Sensor & IoT Events

- `sensor.reading` - Sensor data reading
- `device.connected` - Device connected
- `device.disconnected` - Device disconnected

#### User Events

- `user.created` - New user registered
- `user.updated` - User information updated

#### Inventory Events

- `inventory.low_stock` - Stock level below threshold
- `inventory.movement` - Inventory movement recorded

#### Notification Events

- `notification.send` - Notification to be sent

## 3. NATS Client Features

### Connection Management

- Singleton pattern with lazy initialization
- Automatic reconnection on disconnect
- Connection status monitoring
- Graceful shutdown with drain

### Configuration

```typescript
{
  servers: string | string[],     // NATS server URLs
  name: string,                   // Service name
  maxReconnectAttempts: number,   // -1 for infinite
  reconnectTimeWait: number,      // ms between attempts
  timeout: number,                // connection timeout
  debug: boolean                  // enable debug logging
}
```

### Event Lifecycle Monitoring

- Disconnect detection
- Reconnect notification
- Connection updates
- Error handling

## 4. Marketplace Service Integration

**Location**: `/home/user/sahool-unified-v15-idp/apps/services/marketplace-service/`

### Changes Made

1. **Added Dependencies** (`package.json`)
   - `@sahool/shared-events` - Local package reference
   - `nats` - NATS client library
   - `uuid` - Event ID generation

2. **Created Events Module** (`src/events/`)
   - `events.module.ts` - Module with lifecycle hooks
   - `events.service.ts` - Service for NATS connection and event publishing

3. **Updated App Module** (`src/app.module.ts`)
   - Added `EventsModule` to imports
   - Automatic NATS connection on startup
   - Graceful disconnect on shutdown

4. **Updated Market Service** (`src/market/market.service.ts`)
   - Injected `EventsService`
   - Publishes `order.placed` event when order is created
   - Publishes `inventory.low_stock` event when stock falls below threshold (10 units)

### Event Publishing Examples

#### Order Placed Event

```typescript
// Triggered when createOrder() is called
await this.eventsService.publishOrderPlaced({
  orderId: order.id,
  userId: order.buyerId,
  items: orderItems.map((item) => ({
    productId: item.productId,
    quantity: item.quantity,
    price: item.unitPrice,
  })),
  totalAmount: order.totalAmount,
  currency: "YER",
});
```

#### Inventory Low Stock Event

```typescript
// Triggered when stock falls below threshold
await this.eventsService.publishInventoryLowStock({
  productId: product.id,
  productName: product.nameAr || product.name,
  currentStock: product.stock,
  threshold: LOW_STOCK_THRESHOLD,
  unit: product.unit,
});
```

## 5. Event Logging Subscriber

The marketplace service automatically subscribes to all events in development mode for logging:

```typescript
// In EventsService.connect()
if (process.env.NODE_ENV !== "production") {
  await this.setupEventLogging();
}
```

This provides real-time visibility into all events flowing through the system during development.

## 6. Usage Examples

### Publishing Events (from any service)

```typescript
import {
  initializeNatsClient,
  publishFieldCreated,
  publishOrderPlaced,
  publishSensorReading,
} from '@sahool/shared-events';

// Initialize connection
await initializeNatsClient({
  servers: process.env.NATS_URL,
  name: 'my-service',
});

// Publish events
await publishFieldCreated({
  fieldId: 'field-123',
  userId: 'user-456',
  name: 'North Field',
  area: 1000,
  location: { type: 'Polygon', coordinates: [...] },
  cropType: 'wheat',
});

await publishOrderPlaced({
  orderId: 'order-789',
  userId: 'user-456',
  items: [{ productId: 'p1', quantity: 2, price: 50 }],
  totalAmount: 100,
  currency: 'YER',
});
```

### Subscribing to Events

```typescript
import {
  subscribe,
  subscribeToOrderEvents,
  EventSubjects,
} from "@sahool/shared-events";

// Subscribe to specific event
await subscribe(EventSubjects.ORDER_PLACED, async (event) => {
  console.log("Order placed:", event.payload);
  // Process order...
});

// Subscribe to all order events
await subscribeToOrderEvents(async (event) => {
  console.log("Order event:", event.eventType);
});

// Subscribe with queue group for load balancing
await subscribe(
  EventSubjects.SENSOR_READING,
  async (event) => {
    // Process sensor data
  },
  { queue: "sensor-processors" },
);
```

## 7. Environment Configuration

The NATS Event Bus uses the following environment variables:

```bash
# NATS server URL (already configured in docker-compose.yml)
NATS_URL=nats://nats:4222

# Service name (for connection identification)
SERVICE_NAME=marketplace-service

# Environment mode (affects debug logging)
NODE_ENV=development
```

## 8. Benefits of This Implementation

1. **Decoupling**: Services communicate through events, not direct calls
2. **Scalability**: Queue groups allow horizontal scaling
3. **Reliability**: Automatic reconnection ensures resilience
4. **Type Safety**: TypeScript prevents runtime errors
5. **Observability**: Built-in logging for development
6. **Maintainability**: Centralized event definitions
7. **Testability**: Easy to mock event publishing/subscription

## 9. Next Steps

To integrate the event bus into other services:

1. **Add dependency** to service's `package.json`:

   ```json
   "@sahool/shared-events": "file:../../../packages/shared-events"
   ```

2. **Initialize NATS** in service startup:

   ```typescript
   import { initializeNatsClient } from "@sahool/shared-events";
   await initializeNatsClient();
   ```

3. **Publish events** when appropriate:

   ```typescript
   import { publishFieldCreated } from '@sahool/shared-events';
   await publishFieldCreated({ ... });
   ```

4. **Subscribe to events** you care about:
   ```typescript
   import { subscribeToFieldEvents } from '@sahool/shared-events';
   await subscribeToFieldEvents(async (event) => { ... });
   ```

## 10. Testing the Implementation

### Start the Infrastructure

```bash
# Start NATS and other infrastructure
docker-compose up -d nats postgres redis
```

### Build and Start Marketplace Service

```bash
# Build shared-events package (already done)
cd packages/shared-events
npm install
npm run build

# Install marketplace-service dependencies and start
cd ../../apps/services/marketplace-service
npm install
npm run start:dev
```

### Watch the Logs

When an order is created, you should see:

- NATS connection established
- Event logging subscriber active
- `order.placed` event published
- `inventory.low_stock` event published (if stock is low)

## 11. Files Created/Modified

### New Files

- `/packages/shared-events/package.json`
- `/packages/shared-events/tsconfig.json`
- `/packages/shared-events/README.md`
- `/packages/shared-events/src/index.ts`
- `/packages/shared-events/src/events.ts`
- `/packages/shared-events/src/nats-client.ts`
- `/packages/shared-events/src/publisher.ts`
- `/packages/shared-events/src/subscriber.ts`
- `/apps/services/marketplace-service/src/events/events.module.ts`
- `/apps/services/marketplace-service/src/events/events.service.ts`

### Modified Files

- `/apps/services/marketplace-service/package.json`
- `/apps/services/marketplace-service/src/app.module.ts`
- `/apps/services/marketplace-service/src/market/market.service.ts`

## Summary

The NATS Event Bus is now fully activated with:

- ✅ Shared events package with TypeScript types
- ✅ Singleton NATS client with reconnection logic
- ✅ Publisher helper functions for all event types
- ✅ Subscriber helper functions with pattern support
- ✅ Integration in marketplace-service
- ✅ Real event publishing on order creation
- ✅ Inventory low stock monitoring
- ✅ Development logging subscriber
- ✅ Comprehensive documentation

The system is ready for cross-service event-driven communication!
