# Soft Delete Implementation Guide

This guide provides step-by-step instructions for implementing soft delete across SAHOOL services.

## Table of Contents

1. [Overview](#overview)
2. [For Prisma Services](#for-prisma-services)
3. [For SQLAlchemy Services](#for-sqlalchemy-services)
4. [Migration Strategy](#migration-strategy)
5. [Testing](#testing)
6. [Common Pitfalls](#common-pitfalls)

## Overview

The soft delete pattern marks records as deleted without physically removing them from the database. This provides:

- **Data Recovery**: Easily restore accidentally deleted records
- **Audit Trail**: Track who deleted what and when
- **Compliance**: Meet regulatory requirements for data retention
- **Analytics**: Analyze deletion patterns and reasons

## For Prisma Services

### Services Using Prisma

- field-core
- marketplace-service (✅ **Complete Example**)
- research-core
- chat-service
- field-management-service
- iot-service
- user-service
- weather-service

### Step 1: Update Prisma Schema

Add soft delete fields to models that should support soft delete:

```prisma
model YourModel {
  id          String   @id @default(uuid())
  // ... other fields ...

  // Soft Delete Fields
  deletedAt   DateTime? @map("deleted_at")
  deletedBy   String?   @map("deleted_by")

  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")

  @@index([deletedAt]) // Important for query performance
  @@map("your_table")
}
```

**Important Considerations:**

- Add to main entity models (e.g., Product, Order, User)
- Consider if junction/relation tables need it
- Skip audit/log tables (they should be permanent)

### Step 2: Generate Migration

```bash
cd apps/services/your-service
npx prisma migrate dev --name add_soft_delete_fields
```

Or create manual migration (see example in `/home/user/sahool-unified-v15-idp/apps/services/marketplace-service/prisma/migrations/20260101000000_add_soft_delete_fields/migration.sql`)

### Step 3: Install Shared Package

```bash
npm install @sahool/shared-db
# or add to package.json
```

### Step 4: Update Prisma Service

Modify your Prisma service to apply the middleware:

```typescript
// src/prisma/prisma.service.ts
import { Injectable, OnModuleInit, OnModuleDestroy } from "@nestjs/common";
import { PrismaClient } from "@prisma/client";
import { createSoftDeleteMiddleware } from "@sahool/shared-db";

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  constructor() {
    super({
      log: ["query", "info", "warn", "error"],
    });

    // Apply soft delete middleware
    this.$use(
      createSoftDeleteMiddleware({
        excludedModels: [
          // Add models that should NOT use soft delete
          "AuditLog",
          "EventLog",
          // etc...
        ],
        enableLogging: process.env.NODE_ENV === "development",
      }),
    );
  }

  async onModuleInit() {
    await this.$connect();
    console.log("✅ Database connected with soft delete middleware");
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
```

### Step 5: Update Service Layer

Use soft delete helpers in your services:

```typescript
import { Injectable } from "@nestjs/common";
import { PrismaService } from "./prisma/prisma.service";
import { softDelete, restore, findWithDeleted } from "@sahool/shared-db";

@Injectable()
export class ProductService {
  constructor(private prisma: PrismaService) {}

  async deleteProduct(id: string, userId: string) {
    return softDelete(this.prisma.product, { id }, { deletedBy: userId });
  }

  async restoreProduct(id: string) {
    return restore(this.prisma.product, { id });
  }

  async findAllProducts(includeDeleted = false) {
    if (includeDeleted) {
      return findWithDeleted(this.prisma.product);
    }
    return this.prisma.product.findMany(); // Auto-filters deleted
  }
}
```

### Step 6: Update Controllers

```typescript
@Delete(':id')
async deleteProduct(
  @Param('id') id: string,
  @CurrentUser() user: User,
) {
  return this.productService.deleteProduct(id, user.id);
}

@Post(':id/restore')
async restoreProduct(@Param('id') id: string) {
  return this.productService.restoreProduct(id);
}
```

## For SQLAlchemy Services

### Services Using SQLAlchemy

- billing-core (✅ **Example Available**)
- inventory-service
- notification-service

### Step 1: Update Models

Add `SoftDeleteMixin` to your models:

```python
# src/models.py
from packages.shared_db.src.soft_delete_sqlalchemy import SoftDeleteMixin
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class YourModel(Base, SoftDeleteMixin):
    __tablename__ = "your_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # ... other fields ...

    # deleted_at and deleted_by are inherited from SoftDeleteMixin
```

**Note:** The mixin automatically adds:

- `deleted_at: Column[DateTime]`
- `deleted_by: Column[String]`

### Step 2: Create Alembic Migration

```python
# migrations/versions/xxx_add_soft_delete_fields.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add soft delete columns
    op.add_column('your_table',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column('your_table',
        sa.Column('deleted_by', sa.String(255), nullable=True)
    )

    # Add index for performance
    op.create_index(
        'idx_your_table_deleted_at',
        'your_table',
        ['deleted_at']
    )

    # Add comments
    op.execute("""
        COMMENT ON COLUMN your_table.deleted_at IS 'Soft delete timestamp';
        COMMENT ON COLUMN your_table.deleted_by IS 'User who deleted record';
    """)

def downgrade():
    op.drop_index('idx_your_table_deleted_at', table_name='your_table')
    op.drop_column('your_table', 'deleted_by')
    op.drop_column('your_table', 'deleted_at')
```

### Step 3: Update Service Layer

```python
# src/services/your_service.py
from sqlalchemy.orm import Session
from packages.shared_db.src.soft_delete_sqlalchemy import (
    soft_delete_record,
    restore_record,
    get_active_records,
)
from src.models import YourModel

class YourService:
    def __init__(self, session: Session):
        self.session = session

    def delete_record(self, record_id: str, user_id: str):
        """Soft delete a record"""
        record = soft_delete_record(
            self.session,
            YourModel,
            record_id,
            deleted_by=user_id
        )
        self.session.commit()
        return record

    def restore_record(self, record_id: str):
        """Restore a soft-deleted record"""
        record = restore_record(self.session, YourModel, record_id)
        self.session.commit()
        return record

    def get_all_active(self):
        """Get all active (non-deleted) records"""
        return get_active_records(self.session, YourModel)
```

### Step 4: Update API Endpoints

```python
# src/main.py or routes
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()

@router.delete("/{record_id}")
def delete_record(
    record_id: str,
    user_id: str,
    session: Session = Depends(get_db)
):
    service = YourService(session)
    return service.delete_record(record_id, user_id)

@router.post("/{record_id}/restore")
def restore_record(
    record_id: str,
    session: Session = Depends(get_db)
):
    service = YourService(session)
    return service.restore_record(record_id)
```

## Migration Strategy

### Phase 1: Planning (Week 1)

1. **Identify Models**: List all models that need soft delete
2. **Assess Impact**: Check for foreign key constraints
3. **Plan Excluded Models**: Decide which models should NOT use soft delete

### Phase 2: Implementation (Week 2-3)

1. **Start with One Service**: Use marketplace-service or billing-core as template
2. **Test Thoroughly**: Unit tests, integration tests, manual testing
3. **Deploy to Staging**: Validate in staging environment
4. **Monitor Performance**: Check query performance with indexes

### Phase 3: Rollout (Week 4+)

1. **Deploy Service by Service**: Don't rush
2. **Monitor Each Deployment**: Watch for issues
3. **Document Learnings**: Update this guide with findings

## Testing

### Unit Tests (TypeScript/Prisma)

```typescript
describe("Soft Delete", () => {
  it("should soft delete a record", async () => {
    const product = await prisma.product.create({
      data: { name: "Test", price: 100 },
    });

    await softDelete(
      prisma.product,
      { id: product.id },
      { deletedBy: "test-user" },
    );

    const deleted = await prisma.product.findUnique({
      where: { id: product.id },
      includeDeleted: true,
    });

    expect(deleted.deletedAt).toBeDefined();
    expect(deleted.deletedBy).toBe("test-user");
  });

  it("should exclude deleted from queries", async () => {
    const products = await prisma.product.findMany();
    expect(products.every((p) => !p.deletedAt)).toBe(true);
  });

  it("should restore deleted record", async () => {
    const product = await prisma.product.create({
      data: { name: "Test", price: 100 },
    });

    await softDelete(prisma.product, { id: product.id });
    await restore(prisma.product, { id: product.id });

    const restored = await prisma.product.findUnique({
      where: { id: product.id },
    });

    expect(restored.deletedAt).toBeNull();
  });
});
```

### Unit Tests (Python/SQLAlchemy)

```python
def test_soft_delete(session):
    """Test soft deleting a record"""
    record = YourModel(name="Test")
    session.add(record)
    session.commit()

    soft_delete_record(session, YourModel, record.id, deleted_by="test-user")
    session.commit()

    deleted = session.query(YourModel).filter_by(id=record.id).first()
    assert deleted.deleted_at is not None
    assert deleted.deleted_by == "test-user"


def test_filter_active(session):
    """Test that active filter excludes deleted records"""
    record1 = YourModel(name="Active")
    record2 = YourModel(name="Deleted")
    session.add_all([record1, record2])
    session.commit()

    record2.soft_delete(deleted_by="test")
    session.commit()

    active = get_active_records(session, YourModel)
    assert len(active) == 1
    assert active[0].id == record1.id


def test_restore(session):
    """Test restoring a deleted record"""
    record = YourModel(name="Test")
    session.add(record)
    session.commit()

    record.soft_delete()
    session.commit()

    restore_record(session, YourModel, record.id)
    session.commit()

    restored = session.query(YourModel).filter_by(id=record.id).first()
    assert restored.deleted_at is None
```

## Common Pitfalls

### 1. Unique Constraints

**Problem**: Unique constraints fail when trying to re-create deleted records.

**Solution**: Include `deletedAt` in unique constraints:

```prisma
@@unique([email, deletedAt])
```

### 2. Foreign Key Cascades

**Problem**: CASCADE DELETE still hard deletes child records.

**Solution**:

- Add soft delete to child models too
- Handle cascades manually in application code

### 3. Performance Issues

**Problem**: Queries slow down without proper indexing.

**Solution**: Always add index on `deletedAt`:

```prisma
@@index([deletedAt])
```

### 4. Missing deletedBy

**Problem**: Audit trail incomplete without knowing who deleted.

**Solution**: Always pass `deletedBy`:

```typescript
await softDelete(prisma.product, { id }, { deletedBy: userId });
```

### 5. Transaction Issues

**Problem**: Soft delete in transactions can cause deadlocks.

**Solution**: Keep transactions short, commit after soft delete:

```typescript
await prisma.$transaction(async (tx) => {
  await softDelete(tx.product, { id }, { deletedBy: userId });
  // Minimize other operations
});
```

## Monitoring & Maintenance

### Regular Tasks

1. **Monitor Deletion Rates**: Track how many records are being deleted
2. **Review Restoration Requests**: Understand why records are being restored
3. **Cleanup Old Deletions**: Periodically hard delete very old soft-deleted records
4. **Audit Compliance**: Ensure deletion tracking meets regulatory requirements

### Metrics to Track

- Active vs deleted record counts
- Deletion rate by model
- Restoration frequency
- Time-to-restoration
- Storage impact of soft deleted records

## Support

For questions or issues:

1. Check the [README](./README.md)
2. Review examples in marketplace-service or billing-core
3. Create an issue in the repository
4. Contact the platform team

## Changelog

- **2026-01-01**: Initial implementation guide created
- Added Prisma and SQLAlchemy examples
- Included marketplace-service as complete example
