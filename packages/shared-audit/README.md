# @sahool/shared-audit

Enhanced audit trail system for the SAHOOL platform with field-level change tracking, automatic diff generation, hash chain integrity, and intelligent alert triggers.

## Features

- **Field-Level Change Tracking**: Automatically tracks which fields changed and their before/after values
- **Automatic Diff Generation**: Uses deep-diff to generate comprehensive change diffs
- **Hash Chain Integrity**: Cryptographic hash chain prevents tampering with audit logs
- **Category & Severity Tagging**: Organize events by category (security, data, config, etc.) and severity
- **Alert Triggers**: Automatically detect critical patterns and trigger alerts
- **NestJS Integration**: Decorators and middleware for seamless integration
- **Type-Safe**: Full TypeScript support with comprehensive types

## Installation

```bash
npm install @sahool/shared-audit
```

## Quick Start

### 1. Configure the Audit Logger

```typescript
import { AuditLogger } from "@sahool/shared-audit";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

const auditLogger = new AuditLogger({
  prisma,
  enableHashChain: true,
  enableAlerts: true,
  alertConfig: {
    handlers: [consoleAlertHandler],
  },
});
```

### 2. Add Middleware to Your NestJS App

```typescript
import { Module, NestModule, MiddlewareConsumer } from "@nestjs/common";
import { AuditMiddleware, AuditLogger } from "@sahool/shared-audit";

@Module({
  providers: [AuditLogger],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(AuditMiddleware).forRoutes("*");
  }
}
```

### 3. Use Decorators in Controllers

```typescript
import {
  AuditCreate,
  AuditUpdate,
  AuditDelete,
  Audit,
} from "@sahool/shared-audit";

@Controller("products")
export class ProductsController {
  @Post()
  @AuditCreate("product")
  async createProduct(
    @Body() dto: CreateProductDto,
    @Audit() audit: AuditContext,
  ) {
    // Your code here
    return this.productsService.create(dto);
  }

  @Put(":id")
  @AuditUpdate("product", { trackChanges: true })
  async updateProduct(@Param("id") id: string, @Body() dto: UpdateProductDto) {
    // Your code here
    return this.productsService.update(id, dto);
  }

  @Delete(":id")
  @AuditDelete("product")
  async deleteProduct(@Param("id") id: string) {
    // Your code here
    return this.productsService.delete(id);
  }
}
```

### 4. Add Global Interceptor

```typescript
import { APP_INTERCEPTOR } from "@nestjs/core";
import { AuditInterceptor } from "@sahool/shared-audit";

@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: AuditInterceptor,
    },
  ],
})
export class AppModule {}
```

## Manual Logging

You can also log audit events manually:

```typescript
import {
  AuditLogger,
  AuditCategory,
  AuditSeverity,
} from "@sahool/shared-audit";

// Simple log
await auditLogger.log({
  tenantId: "tenant-123",
  actorId: "user-456",
  actorType: ActorType.USER,
  action: "product.create",
  category: AuditCategory.DATA,
  severity: AuditSeverity.INFO,
  resourceType: "product",
  resourceId: "product-789",
  correlationId: "request-abc",
  success: true,
});

// Log with change tracking
await auditLogger.logWithChanges(
  {
    tenantId: "tenant-123",
    actorId: "user-456",
    actorType: ActorType.USER,
    action: "product.update",
    category: AuditCategory.DATA,
    severity: AuditSeverity.INFO,
    resourceType: "product",
    resourceId: "product-789",
    correlationId: "request-abc",
    success: true,
  },
  { name: "Old Product", price: 100 }, // Old value
  { name: "New Product", price: 150 }, // New value
  {
    trackChanges: true,
    generateDiff: true,
    excludeFields: ["updatedAt"],
    redactFields: ["internalNotes"],
  },
);
```

## Field-Level Decorators

Mark sensitive fields in your DTOs:

```typescript
import {
  AuditField,
  SensitiveField,
  ExcludeFromAudit,
} from "@sahool/shared-audit";

class UpdateProductDto {
  @AuditField()
  name: string;

  @SensitiveField() // Will be redacted in logs
  price: number;

  @ExcludeFromAudit() // Won't appear in audit logs
  internalNotes: string;
}
```

## Alert Handlers

Configure custom alert handlers:

```typescript
import {
  AuditLogger,
  AlertHandler,
  createWebhookAlertHandler,
} from "@sahool/shared-audit";

// Custom handler
const customHandler: AlertHandler = {
  name: "custom",
  async handle(alert) {
    console.log("Custom alert:", alert);
    // Send to your monitoring system
  },
};

// Webhook handler
const webhookHandler = createWebhookAlertHandler(
  "https://your-webhook-url.com",
);

const auditLogger = new AuditLogger({
  prisma,
  enableAlerts: true,
  alertConfig: {
    handlers: [customHandler, webhookHandler],
  },
});
```

## Query Audit Logs

```typescript
const logs = await auditLogger.query({
  tenantId: "tenant-123",
  actorId: "user-456",
  category: AuditCategory.SECURITY,
  startDate: new Date("2024-01-01"),
  endDate: new Date("2024-12-31"),
  limit: 100,
});
```

## Get Statistics

```typescript
const stats = await auditLogger.getStats("tenant-123", new Date());
console.log(stats);
// {
//   totalEvents: 1234,
//   eventsByCategory: { security: 100, data: 500, ... },
//   eventsBySeverity: { critical: 5, warning: 50, ... },
//   uniqueActors: 25,
//   ...
// }
```

## Validate Hash Chain

```typescript
const validation = await auditLogger.validateHashChain("tenant-123");
if (!validation.valid) {
  console.error("Hash chain validation failed:", validation.errors);
}
```

## Database Schema

Create the audit log table in your database:

```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id VARCHAR(255) NOT NULL,
  actor_id VARCHAR(255),
  actor_type VARCHAR(50) NOT NULL,
  action VARCHAR(255) NOT NULL,
  category VARCHAR(50) NOT NULL,
  severity VARCHAR(50) NOT NULL,
  resource_type VARCHAR(255) NOT NULL,
  resource_id VARCHAR(255) NOT NULL,
  correlation_id VARCHAR(255) NOT NULL,
  session_id VARCHAR(255),
  ip_address VARCHAR(50),
  user_agent TEXT,
  changes JSONB,
  diff JSONB,
  metadata JSONB,
  success BOOLEAN NOT NULL DEFAULT true,
  error_code VARCHAR(100),
  error_message TEXT,
  prev_hash VARCHAR(64),
  entry_hash VARCHAR(64),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant_created ON audit_logs(tenant_id, created_at);
CREATE INDEX idx_audit_actor ON audit_logs(actor_id, created_at);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_correlation ON audit_logs(correlation_id);
CREATE INDEX idx_audit_category ON audit_logs(category, created_at);
```

## License

MIT
