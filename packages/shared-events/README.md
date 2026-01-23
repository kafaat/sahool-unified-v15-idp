# @sahool/shared-events

Unified NATS event bus for SAHOOL microservices with type-safe event definitions, Zod validation, and bilingual documentation.

ناقل الأحداث الموحد لخدمات سهول المصغرة مع تعريفات الأحداث الآمنة والتحقق من الصحة

## Features

- **Type-Safe Events**: Discriminated unions for compile-time type checking
- **Zod Validation**: Runtime payload validation with comprehensive schemas
- **Consistent Naming**: Subject naming aligned with Python services (`sahool.{domain}.{action}`)
- **Multi-Tenant Support**: Tenant-scoped subjects for data isolation
- **Bilingual Documentation**: Arabic and English JSDoc comments
- **Comprehensive Coverage**: 15+ event domains (field, weather, satellite, health, billing, etc.)

## Installation

```bash
npm install @sahool/shared-events
# or
pnpm add @sahool/shared-events
```

## Quick Start

### Initialize NATS Connection

```typescript
import { initializeNatsClient } from "@sahool/shared-events";

// Initialize at application startup
await initializeNatsClient({
  servers: process.env.NATS_URL || "nats://localhost:4222",
  name: "my-service",
  debug: true,
});
```

### Publishing Events

```typescript
import {
  publishFieldCreated,
  publishWeatherAlert,
  publishSensorReading,
} from "@sahool/shared-events";

// Publish a field created event with validation
await publishFieldCreated({
  fieldId: "550e8400-e29b-41d4-a716-446655440000",
  farmId: "550e8400-e29b-41d4-a716-446655440001",
  tenantId: "550e8400-e29b-41d4-a716-446655440002",
  name: "North Field",
  nameAr: "الحقل الشمالي",
  area: 10.5,
  areaUnit: "hectares",
  location: {
    type: "Polygon",
    coordinates: [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
  },
});

// Publish with tenant scoping
await publishWeatherAlert(
  {
    alertId: "550e8400-e29b-41d4-a716-446655440003",
    tenantId: "550e8400-e29b-41d4-a716-446655440002",
    alertType: "frost",
    severity: "high",
    title: "Frost Warning",
    titleAr: "تحذير من الصقيع",
    message: "Expected frost tonight",
    messageAr: "متوقع صقيع الليلة",
    startTime: new Date(),
  },
  { tenantId: "org_123" }
);

// Publish sensor reading
await publishSensorReading({
  deviceId: "sensor-001",
  sensorType: "soil_moisture",
  value: 45.2,
  unit: "%",
  readingTime: new Date(),
  fieldId: "550e8400-e29b-41d4-a716-446655440000",
});
```

### Subscribing to Events

```typescript
import {
  subscribeToFieldEvents,
  subscribeToWeatherEvents,
  subscribeToTenantEvents,
  createLoggingHandler,
  isFieldEvent,
} from "@sahool/shared-events";

// Subscribe to all field events
const fieldSub = await subscribeToFieldEvents(async (event, subject) => {
  if (isFieldEvent(event)) {
    console.log("Field event:", event.payload);
  }
});

// Subscribe to weather events with queue group (load balancing)
const weatherSub = await subscribeToWeatherEvents(
  async (event) => {
    console.log("Weather event:", event.payload);
  },
  { queue: "weather-processors" }
);

// Subscribe to all events for a specific tenant
const tenantSub = await subscribeToTenantEvents(
  "org_123",
  createLoggingHandler("[Tenant Events]")
);
```

### Payload Validation

```typescript
import {
  validatePayload,
  safeValidatePayload,
  FieldCreatedPayloadSchema,
} from "@sahool/shared-events";

// Strict validation (throws on error)
try {
  const validated = validatePayload("FieldCreated", rawPayload);
} catch (error) {
  console.error("Validation failed:", error);
}

// Safe validation (returns result object)
const result = safeValidatePayload("FieldCreated", rawPayload);
if (result.success) {
  console.log("Valid payload:", result.data);
} else {
  console.log("Validation errors:", result.error.issues);
}

// Direct schema usage
const payload = FieldCreatedPayloadSchema.parse(rawData);
```

## Event Domains

| Domain | Subject Pattern | Description |
|--------|-----------------|-------------|
| Field | `sahool.field.*` | Field CRUD operations |
| Farm | `sahool.farm.*` | Farm management |
| Weather | `sahool.weather.*` | Forecasts and alerts |
| Satellite | `sahool.satellite.*` | Imagery and NDVI |
| Health | `sahool.health.*` | Disease, pest, stress detection |
| Inventory | `sahool.inventory.*` | Stock management |
| Billing | `sahool.billing.*` | Subscriptions and payments |
| Task | `sahool.task.*` | Task management |
| Alert | `sahool.alert.*` | System alerts |
| IoT | `sahool.iot.*` | Sensors and devices |
| Notification | `sahool.notification.*` | Push notifications |
| User | `sahool.user.*` | User management |
| Order | `sahool.order.*` | Marketplace orders |
| Agent | `sahool.agent.*` | AI agent execution |
| Recommendation | `sahool.recommendation.*` | Advisory recommendations |
| System | `sahool.system.*` | System health and metrics |

## Subject Naming Convention

All subjects follow the pattern: `sahool.{domain}.{action}` or `sahool.{domain}.{entity}.{action}`

Examples:
- `sahool.field.created` - Field created
- `sahool.weather.alert` - Weather alert
- `sahool.billing.payment.completed` - Payment completed
- `sahool.health.disease.detected` - Disease detected

### Tenant-Scoped Subjects

For multi-tenant isolation: `sahool.tenant.{tenant_id}.{domain}.{action}`

```typescript
import { getTenantSubject, getTenantWildcard } from "@sahool/shared-events";

// Get tenant-scoped subject
const subject = getTenantSubject("org_123", "field", "created");
// => "sahool.tenant.org_123.field.created"

// Get wildcard for all tenant events
const wildcard = getTenantWildcard("org_123");
// => "sahool.tenant.org_123.>"

// Subscribe to tenant domain
const domainWildcard = getTenantWildcard("org_123", "field");
// => "sahool.tenant.org_123.field.*"
```

## Event Structure

All events follow this structure:

```typescript
interface SahoolEvent<TPayload> {
  eventId: string;        // UUID
  eventType: string;      // NATS subject
  timestamp: Date;        // Event timestamp
  version: string;        // Schema version (default: "1.0")
  payload: TPayload;      // Event-specific payload
  metadata?: {
    correlationId?: string;   // Request correlation
    causationId?: string;     // Causing event ID
    userId?: string;          // Acting user
    traceId?: string;         // OpenTelemetry trace
    spanId?: string;          // OpenTelemetry span
    source?: string;          // Source service
  };
}
```

## Type Guards

Use type guards for runtime type checking:

```typescript
import {
  isFieldEvent,
  isWeatherEvent,
  isBillingEvent,
  getEventDomain,
  getEventAction,
} from "@sahool/shared-events";

function handleEvent(event: SahoolEvent) {
  if (isFieldEvent(event)) {
    // TypeScript knows event is FieldEvent
    console.log("Field:", event.payload.fieldId);
  } else if (isWeatherEvent(event)) {
    // TypeScript knows event is WeatherEvent
    console.log("Weather:", event.payload.alertType);
  }

  // Extract domain and action
  const domain = getEventDomain(event.eventType); // "field"
  const action = getEventAction(event.eventType); // "created"
}
```

## Available Schemas

### Common Schemas

- `UUIDSchema` - UUID validation
- `ISODateSchema` - ISO date string
- `GeoJSONPolygonSchema` - GeoJSON polygon
- `SeveritySchema` - low | medium | high | critical
- `PrioritySchema` - low | medium | high | urgent
- `CurrencySchema` - SAR | YER | USD | EUR | AED

### Event Payload Schemas

All schemas include Arabic field name support where applicable:

| Schema | Required Fields | Optional Fields |
|--------|-----------------|-----------------|
| `FieldCreatedPayloadSchema` | fieldId, farmId, tenantId, name, area, location | nameAr, cropType, soilType |
| `WeatherAlertPayloadSchema` | alertId, tenantId, alertType, severity, title, message, startTime | titleAr, messageAr, fieldIds |
| `SensorReadingPayloadSchema` | deviceId, sensorType, value, unit, readingTime | fieldId, tenantId, quality |
| `PaymentCompletedPayloadSchema` | paymentId, tenantId, amount, paymentMethod, transactionId | subscriptionId, taxAmount |

See `/src/schemas/index.ts` for complete schema definitions.

## Advanced Usage

### Custom Event Publishing

```typescript
import { publishEvent, publishValidatedEvent } from "@sahool/shared-events";

// Publish without validation
await publishEvent("sahool.custom.event", {
  customField: "value",
}, {
  version: "2.0",
  metadata: {
    source: "my-service",
    correlationId: "req-123",
  },
});

// Publish with explicit validation disabled
await publishValidatedEvent(
  "sahool.field.created",
  "FieldCreated",
  payload,
  { validate: false }
);
```

### Pattern Subscriptions

```typescript
import { subscribePattern } from "@sahool/shared-events";

// Subscribe to all creation events
await subscribePattern("sahool.*.created", async (event) => {
  console.log("Something was created:", event);
});

// Subscribe to all SAHOOL events
await subscribePattern("sahool.>", async (event) => {
  console.log("Event received:", event);
});
```

### Filtering and Validating Handlers

```typescript
import {
  createFilteringHandler,
  createValidatingHandler,
} from "@sahool/shared-events";

// Only process high-severity alerts
const filteredHandler = createFilteringHandler(
  (event) => event.payload.severity === "high",
  async (event) => {
    console.log("High severity alert:", event);
  }
);

// Validate before processing
const validatedHandler = createValidatingHandler(
  (event) => {
    if (!event.payload.fieldId) {
      throw new Error("fieldId is required");
    }
  },
  async (event) => {
    console.log("Valid event:", event);
  },
  (error, event) => {
    console.error("Validation failed:", error, event);
  }
);
```

## API Reference

### NATS Client

```typescript
// Initialize client
initializeNatsClient(config: NatsClientConfig): Promise<void>

// Get connection
getNatsConnection(): NatsConnection | null

// Singleton instance
NatsClient.getInstance(config): NatsClient
```

### Publishers

```typescript
// Generic publish
publishEvent<T>(subject, payload, options?): Promise<void>
publishValidatedEvent<T>(subject, schemaName, payload, options?): Promise<void>

// Domain-specific publishers
publishFieldCreated(payload, options?): Promise<void>
publishFieldUpdated(payload, options?): Promise<void>
publishFieldDeleted(payload, options?): Promise<void>
publishWeatherForecast(payload, options?): Promise<void>
publishWeatherAlert(payload, options?): Promise<void>
publishSatelliteDataReady(payload, options?): Promise<void>
publishSatelliteAnomaly(payload, options?): Promise<void>
publishDiseaseDetected(payload, options?): Promise<void>
publishCropStress(payload, options?): Promise<void>
publishInventoryLowStock(payload, options?): Promise<void>
publishInventoryMovement(payload, options?): Promise<void>
publishTaskCreated(payload, options?): Promise<void>
publishTaskCompleted(payload, options?): Promise<void>
publishAlertCreated(payload, options?): Promise<void>
publishSensorReading(payload, options?): Promise<void>
publishDeviceConnected(payload, options?): Promise<void>
publishDeviceDisconnected(payload, options?): Promise<void>
publishNotificationSend(payload, options?): Promise<void>
publishUserCreated(payload, options?): Promise<void>
publishUserUpdated(payload, options?): Promise<void>
publishOrderPlaced(payload, options?): Promise<void>
publishOrderCompleted(payload, options?): Promise<void>
publishOrderCancelled(payload, options?): Promise<void>
publishSubscriptionCreated(payload, options?): Promise<void>
publishPaymentCompleted(payload, options?): Promise<void>
publishAgentExecutionStarted(payload, options?): Promise<void>
publishAgentExecutionCompleted(payload, options?): Promise<void>
publishAgentExecutionFailed(payload, options?): Promise<void>
publishRecommendationCreated(payload, options?): Promise<void>
```

### Subscribers

```typescript
// Generic subscribe
subscribe<T>(subject, handler, options?): Promise<Subscription>
subscribePattern<T>(pattern, handler, options?): Promise<Subscription>
subscribeAll(handler, options?): Promise<Subscription>

// Domain-specific subscribers
subscribeToFieldEvents(handler, options?): Promise<Subscription>
subscribeToFarmEvents(handler, options?): Promise<Subscription>
subscribeToWeatherEvents(handler, options?): Promise<Subscription>
subscribeToSatelliteEvents(handler, options?): Promise<Subscription>
subscribeToHealthEvents(handler, options?): Promise<Subscription>
subscribeToInventoryEvents(handler, options?): Promise<Subscription>
subscribeToBillingEvents(handler, options?): Promise<Subscription>
subscribeToTaskEvents(handler, options?): Promise<Subscription>
subscribeToAlertEvents(handler, options?): Promise<Subscription>
subscribeToIoTEvents(handler, options?): Promise<Subscription>
subscribeToSensorEvents(handler, options?): Promise<Subscription>
subscribeToDeviceEvents(handler, options?): Promise<Subscription>
subscribeToNotificationEvents(handler, options?): Promise<Subscription>
subscribeToUserEvents(handler, options?): Promise<Subscription>
subscribeToOrderEvents(handler, options?): Promise<Subscription>
subscribeToAgentEvents(handler, options?): Promise<Subscription>
subscribeToRecommendationEvents(handler, options?): Promise<Subscription>
subscribeToSystemEvents(handler, options?): Promise<Subscription>

// Tenant-scoped
subscribeToTenantEvents(tenantId, handler, options?): Promise<Subscription>
subscribeToTenantDomain(tenantId, domain, handler, options?): Promise<Subscription>
```

### Utilities

```typescript
// Logging handler
createLoggingHandler(prefix?): EventHandler

// Filtering handler
createFilteringHandler(predicate, handler): EventHandler

// Validating handler
createValidatingHandler(validator, handler, onError?): EventHandler
```

## Environment Variables

- `NATS_URL` - NATS server URL (default: `nats://localhost:4222`)
- `NODE_ENV` - Environment mode (affects debug logging)

## Migration from v1

### Breaking Changes

1. **Subject naming**: Subjects now include `sahool.` prefix
   - Before: `field.created`
   - After: `sahool.field.created`

2. **Payload validation**: Payloads are now validated by default
   - Disable with `{ validate: false }`

3. **Required fields**: More fields are now required for type safety
   - `tenantId` required on most events
   - `farmId` required on field events

### Migration Steps

```typescript
// Before (v1)
import { publishFieldCreated } from "@sahool/shared-events";
await publishFieldCreated({ fieldId, name, area, location });

// After (v2)
import { publishFieldCreated } from "@sahool/shared-events";
await publishFieldCreated({
  fieldId,
  farmId,     // Now required
  tenantId,   // Now required
  name,
  area,
  areaUnit: "hectares",  // Now explicit
  location,   // GeoJSON format required
});
```

## License

Proprietary - KAFAAT
