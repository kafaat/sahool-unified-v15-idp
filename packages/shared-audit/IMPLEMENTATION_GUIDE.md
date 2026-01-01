# Enhanced Audit Trail System - Implementation Guide

## Overview

The enhanced audit trail system provides comprehensive audit logging with:

- **Field-Level Change Tracking**: Track exactly which fields changed with before/after values
- **Automatic Diff Generation**: Deep-diff integration for detailed change analysis
- **Hash Chain Integrity**: Cryptographic verification to prevent tampering
- **Category & Severity Tagging**: Organize by category (security, data, config, etc.)
- **Alert Triggers**: Automatic detection of critical patterns
- **NestJS Integration**: Seamless integration with decorators and middleware

## Architecture

```
packages/shared-audit/
├── src/
│   ├── index.ts                    # Main exports
│   ├── audit-types.ts              # TypeScript types
│   ├── audit-logger.ts             # Core logging service
│   ├── audit-middleware.ts         # Express/NestJS middleware
│   ├── audit-alerts.ts             # Alert detection & triggers
│   └── decorators/
│       ├── auditable.decorator.ts  # @Auditable decorator
│       ├── audit-field.decorator.ts # @AuditField decorator
│       ├── audit.interceptor.ts    # Automatic logging interceptor
│       └── index.ts
├── package.json
├── tsconfig.json
└── README.md
```

## Database Schema

The audit system uses a PostgreSQL table with the following structure:

```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
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
  changes JSONB,           -- Field-level changes
  diff JSONB,              -- Automatic diff
  metadata JSONB,
  success BOOLEAN NOT NULL,
  error_code VARCHAR(100),
  error_message TEXT,
  prev_hash VARCHAR(64),   -- Hash chain
  entry_hash VARCHAR(64),  -- Hash chain
  created_at TIMESTAMPTZ NOT NULL
);
```

## Integration Steps

### 1. Install Dependencies

Add to your service's `package.json`:

```json
{
  "dependencies": {
    "@sahool/shared-audit": "file:../../../packages/shared-audit"
  }
}
```

### 2. Create Audit Module

Create `src/audit/audit.module.ts`:

```typescript
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import {
  AuditLogger,
  AuditMiddleware,
  AuditInterceptor,
  consoleAlertHandler,
} from '@sahool/shared-audit';
import { PrismaService } from '../prisma/prisma.service';

@Module({
  providers: [
    {
      provide: AuditLogger,
      useFactory: (prisma: PrismaService) => {
        return new AuditLogger({
          prisma,
          enableHashChain: true,
          enableAlerts: true,
          alertConfig: {
            handlers: [consoleAlertHandler],
          },
        });
      },
      inject: [PrismaService],
    },
    {
      provide: APP_INTERCEPTOR,
      useClass: AuditInterceptor,
    },
  ],
  exports: [AuditLogger],
})
export class AuditModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(AuditMiddleware).forRoutes('*');
  }
}
```

### 3. Import Audit Module

Update `app.module.ts`:

```typescript
import { AuditModule } from './audit/audit.module';

@Module({
  imports: [
    AuditModule,
    // ... other modules
  ],
})
export class AppModule {}
```

### 4. Run Database Migration

Apply the migration SQL:

```bash
psql -d your_database -f prisma/migrations/20260101_add_audit_logs/migration.sql
```

## Usage Examples

### Example 1: Automatic Audit with Decorators

```typescript
import { Controller, Post, Put, Delete, Body, Param } from '@nestjs/common';
import { AuditCreate, AuditUpdate, AuditDelete } from '@sahool/shared-audit';

@Controller('products')
export class ProductsController {
  @Post()
  @AuditCreate('product', { trackChanges: true })
  async createProduct(@Body() dto: CreateProductDto) {
    // Audit log created automatically
    return this.service.create(dto);
  }

  @Put(':id')
  @AuditUpdate('product', {
    trackChanges: true,
    generateDiff: true,
    redactFields: ['costPrice']
  })
  async updateProduct(@Param('id') id: string, @Body() dto: UpdateProductDto) {
    // Field-level changes tracked automatically
    return this.service.update(id, dto);
  }

  @Delete(':id')
  @AuditDelete('product')
  async deleteProduct(@Param('id') id: string) {
    // Deletion logged with WARNING severity
    return this.service.delete(id);
  }
}
```

### Example 2: Manual Audit Logging

```typescript
import { Injectable } from '@nestjs/common';
import {
  AuditLogger,
  AuditCategory,
  AuditSeverity,
  ActorType
} from '@sahool/shared-audit';

@Injectable()
export class PaymentService {
  constructor(private auditLogger: AuditLogger) {}

  async processPayment(payment: Payment) {
    // Manual audit logging
    await this.auditLogger.log({
      tenantId: payment.tenantId,
      actorId: payment.userId,
      actorType: ActorType.USER,
      action: 'payment.process',
      category: AuditCategory.FINANCIAL,
      severity: AuditSeverity.WARNING,
      resourceType: 'payment',
      resourceId: payment.id,
      correlationId: payment.correlationId,
      metadata: {
        amount: payment.amount,
        currency: payment.currency,
        method: payment.method,
      },
      success: true,
    });

    return processedPayment;
  }
}
```

### Example 3: Change Tracking

```typescript
async updateProduct(id: string, updates: Partial<Product>) {
  // Get current state
  const oldProduct = await this.prisma.product.findUnique({ where: { id } });

  // Apply updates
  const newProduct = await this.prisma.product.update({
    where: { id },
    data: updates,
  });

  // Log with field-level change tracking
  await this.auditLogger.logWithChanges(
    {
      tenantId: 'tenant-123',
      actorId: userId,
      actorType: ActorType.USER,
      action: 'product.update',
      category: AuditCategory.DATA,
      severity: AuditSeverity.INFO,
      resourceType: 'product',
      resourceId: id,
      correlationId: correlationId,
      success: true,
    },
    oldProduct,  // Before
    newProduct,  // After
    {
      trackChanges: true,
      generateDiff: true,
      excludeFields: ['updatedAt'],
      redactFields: ['internalNotes'],
    }
  );

  return newProduct;
}
```

### Example 4: Security Alerts

```typescript
@Controller('admin')
export class AdminController {
  @Post('users/:id/promote')
  @AuditSecurity('user.promote_admin', {
    severity: AuditSeverity.CRITICAL
  })
  async promoteToAdmin(@Param('id') id: string) {
    // This will trigger security alerts
    return this.userService.promoteToAdmin(id);
  }
}
```

### Example 5: Query Audit Logs

```typescript
@Get('audit')
async getAuditTrail(
  @Query('resourceId') resourceId: string,
  @TenantId() tenantId: string
) {
  return this.auditLogger.query({
    tenantId,
    resourceType: 'product',
    resourceId,
    category: AuditCategory.DATA,
    limit: 100,
  });
}
```

### Example 6: Validate Hash Chain

```typescript
@Get('audit/validate')
async validateAudit(@TenantId() tenantId: string) {
  const validation = await this.auditLogger.validateHashChain(tenantId);

  if (!validation.valid) {
    // Alert: Audit trail has been tampered with!
    throw new UnauthorizedException('Audit chain validation failed');
  }

  return validation;
}
```

## Alert Configuration

### Built-in Alert Rules

The system includes default alert rules for:

- Multiple failed login attempts
- Privilege escalation attempts
- Financial transaction failures
- Data deletion events
- Critical errors
- Unauthorized access
- Security configuration changes
- Bulk data exports

### Custom Alert Handlers

```typescript
import { AlertHandler, createWebhookAlertHandler } from '@sahool/shared-audit';

// Email handler
const emailHandler: AlertHandler = {
  name: 'email',
  async handle(alert) {
    await emailService.send({
      to: 'security@example.com',
      subject: `Security Alert: ${alert.rule}`,
      body: alert.message,
    });
  },
};

// Webhook handler
const slackWebhook = createWebhookAlertHandler(
  'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
);

// Configure in AuditModule
new AuditLogger({
  prisma,
  enableAlerts: true,
  alertConfig: {
    handlers: [emailHandler, slackWebhook],
  },
});
```

### Custom Alert Rules

```typescript
import { AlertRule, AuditSeverity } from '@sahool/shared-audit';

const customRule: AlertRule = {
  name: 'high_value_transaction',
  description: 'Transaction over $10,000',
  conditions: [
    { field: 'action', operator: 'equals', value: 'payment.process' },
    { field: 'category', operator: 'equals', value: AuditCategory.FINANCIAL },
  ],
  severity: AuditSeverity.WARNING,
  batchSimilar: false,
};

auditLogger.addRule(customRule);
```

## Best Practices

### 1. Use Decorators for Common Operations

```typescript
// ✅ Good: Declarative and automatic
@AuditCreate('product')
async createProduct() { ... }

// ❌ Avoid: Manual logging for simple CRUD
async createProduct() {
  const result = ...;
  await this.auditLogger.log(...); // Unnecessary
  return result;
}
```

### 2. Redact Sensitive Data

```typescript
// Always redact sensitive fields
@AuditUpdate('user', {
  redactFields: ['password', 'ssn', 'creditCard']
})
async updateUser() { ... }
```

### 3. Use Appropriate Severity Levels

```typescript
// INFO: Normal operations
@AuditCreate('product', { severity: AuditSeverity.INFO })

// WARNING: Important changes, deletions
@AuditDelete('product', { severity: AuditSeverity.WARNING })

// CRITICAL: Security events, admin actions
@AuditSecurity('user.delete', { severity: AuditSeverity.CRITICAL })
```

### 4. Enable Change Tracking for Important Updates

```typescript
// Track field-level changes for auditable resources
@AuditUpdate('financial_record', {
  trackChanges: true,
  generateDiff: true,
})
```

### 5. Use Correlation IDs

```typescript
// Correlation IDs help trace related operations
@Post()
async placeOrder(@CorrelationId() correlationId: string) {
  // All related operations share the same correlationId
  await this.paymentService.charge({ correlationId });
  await this.inventoryService.reserve({ correlationId });
}
```

## Performance Considerations

1. **Async Logging**: Audit logging is async and won't block requests
2. **Batch Alerts**: Alerts are batched to reduce overhead
3. **Indexed Queries**: Database indexes on common query patterns
4. **Selective Logging**: Use decorators to avoid unnecessary logs

## Compliance

The audit system supports:

- **GDPR**: PII redaction and data export capabilities
- **SOC 2**: Comprehensive security audit trail
- **PCI DSS**: Financial transaction logging
- **HIPAA**: Healthcare data access logging
- **ISO 27001**: Security event monitoring

## Troubleshooting

### Issue: Audit logs not appearing

Check:
1. AuditModule is imported in app.module.ts
2. Database table exists (run migration)
3. PrismaService is configured correctly
4. Middleware is applied to routes

### Issue: Hash chain validation failing

Possible causes:
1. Manual modification of audit_logs table
2. Clock skew between servers
3. Database triggers interfering

### Issue: Performance degradation

Solutions:
1. Reduce logging verbosity for GET requests
2. Enable batch alerts
3. Archive old audit logs
4. Use database partitioning

## Migration from Old System

The existing Python-based audit system (`shared/libs/audit/`) can coexist with the new TypeScript system:

1. Continue using Python audit for Python services
2. Migrate TypeScript services to new system
3. Both systems write to compatible tables
4. Gradually migrate Python services to event-based audit

## Support

For issues or questions:
- Check README.md for basic usage
- Review examples in `apps/services/marketplace-service/src/examples/`
- See integration in marketplace-service for complete example

## Future Enhancements

Planned features:
- [ ] Real-time audit log streaming
- [ ] Advanced analytics dashboard
- [ ] Machine learning for anomaly detection
- [ ] Blockchain integration for immutable audit trail
- [ ] Compliance report generation
- [ ] Multi-region audit log replication
