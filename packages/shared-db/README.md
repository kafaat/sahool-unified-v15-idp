# @sahool/shared-db

Shared database utilities for SAHOOL platform, providing a comprehensive soft delete pattern implementation for both Prisma (TypeScript) and SQLAlchemy (Python) ORMs.

## Features

- 🗑️ **Soft Delete Pattern**: Mark records as deleted instead of removing them
- 🔄 **Automatic Filtering**: Middleware automatically excludes deleted records
- 🔍 **Query Helpers**: Utility functions for common soft delete operations
- 📝 **Audit Trail**: Track who deleted what and when
- ♻️ **Restore Capability**: Easily restore soft-deleted records
- 🎯 **Type-Safe**: Full TypeScript support with Prisma
- 🐍 **Python Support**: SQLAlchemy mixin for Python services
- ⚡ **Zero Config**: Works out of the box with sensible defaults

## Installation

```bash
npm install @sahool/shared-db
# or
yarn add @sahool/shared-db
```

## Quick Start

### For Prisma Services (TypeScript/JavaScript)

#### 1. Update Your Prisma Schema

Add soft delete fields to your models:

```prisma
model Product {
  id          String   @id @default(uuid())
  name        String
  price       Float

  // Soft Delete Fields
  deletedAt   DateTime? @map("deleted_at")
  deletedBy   String?   @map("deleted_by")

  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")

  @@index([deletedAt]) // Optimize soft delete queries
  @@map("products")
}
```

#### 2. Apply the Middleware

In your Prisma service:

```typescript
import { PrismaClient } from "@prisma/client";
import { createSoftDeleteMiddleware } from "@sahool/shared-db";

const prisma = new PrismaClient();

// Apply soft delete middleware
prisma.$use(
  createSoftDeleteMiddleware({
    excludedModels: ["AuditLog", "Transaction"], // Models to exclude
    enableLogging: process.env.NODE_ENV === "development",
  }),
);
```

#### 3. Use Soft Delete Operations

```typescript
import { softDelete, restore, findWithDeleted } from "@sahool/shared-db";

// Soft delete a product
const deleted = await softDelete(
  prisma.product,
  { id: "product-123" },
  { deletedBy: "user-456" },
);

// Or use regular Prisma delete (automatically converted to soft delete)
await prisma.product.delete({
  where: { id: "product-123" },
});

// Find active products (deleted ones are automatically excluded)
const activeProducts = await prisma.product.findMany();

// Find including deleted products
const allProducts = await findWithDeleted(prisma.product);

// Restore a deleted product
const restored = await restore(prisma.product, { id: "product-123" });
```

### For SQLAlchemy Services (Python)

#### 1. Add SoftDeleteMixin to Your Models

```python
from packages.shared_db.src.soft_delete_sqlalchemy import SoftDeleteMixin
from sqlalchemy import Column, String, Float
from sqlalchemy.orm import Mapped, mapped_column

class Product(Base, SoftDeleteMixin):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)

    # deletedAt and deletedBy are inherited from SoftDeleteMixin
```

#### 2. Use Soft Delete Operations

```python
from packages.shared_db.src.soft_delete_sqlalchemy import (
    soft_delete_record,
    restore_record,
    get_active_records,
)

# Soft delete a product
deleted_product = soft_delete_record(
    session,
    Product,
    "product-123",
    deleted_by="user-456"
)
session.commit()

# Get only active products
active_products = get_active_records(session, Product)

# Restore a deleted product
restored = restore_record(session, Product, "product-123")
session.commit()

# Check if a record is deleted
product = session.query(Product).filter_by(id="product-123").first()
if product and product.is_deleted():
    print("This product has been deleted")
```

## Database Migration

### Prisma Migration

Create a migration to add soft delete fields:

```sql
-- Add soft delete fields to products table
ALTER TABLE "products"
ADD COLUMN "deleted_at" TIMESTAMPTZ,
ADD COLUMN "deleted_by" VARCHAR(255);

-- Create index for soft delete queries
CREATE INDEX "idx_products_deleted_at" ON "products"("deleted_at");

-- Add comments
COMMENT ON COLUMN "products"."deleted_at" IS 'Soft delete timestamp';
COMMENT ON COLUMN "products"."deleted_by" IS 'User who deleted the record';
```

### Alembic Migration (SQLAlchemy)

```python
def upgrade():
    # Add soft delete columns
    op.add_column('products',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column('products',
        sa.Column('deleted_by', sa.String(255), nullable=True)
    )

    # Add index
    op.create_index('idx_products_deleted_at', 'products', ['deleted_at'])

def downgrade():
    op.drop_index('idx_products_deleted_at', table_name='products')
    op.drop_column('products', 'deleted_by')
    op.drop_column('products', 'deleted_at')
```

## API Reference

### Prisma (TypeScript)

#### Middleware

##### `createSoftDeleteMiddleware(config?)`

Creates Prisma middleware that implements soft delete pattern.

**Parameters:**

- `config.excludedModels` (string[]): Models to exclude from soft delete behavior
- `config.enableLogging` (boolean): Enable logging for debugging
- `config.logger` (function): Custom logger function

**Returns:** Prisma middleware function

#### Helper Functions

##### `softDelete(model, where, options?)`

Soft delete a single record.

**Parameters:**

- `model`: Prisma model delegate
- `where`: Where clause to identify the record
- `options.deletedBy`: User ID performing the deletion

**Returns:** Promise with the soft-deleted record

##### `softDeleteMany(model, where, options?)`

Soft delete multiple records.

**Returns:** Promise with `{ count: number }`

##### `restore(model, where, options?)`

Restore a soft-deleted record.

**Returns:** Promise with the restored record

##### `restoreMany(model, where, options?)`

Restore multiple soft-deleted records.

**Returns:** Promise with `{ count: number }`

##### `findWithDeleted(model, args?)`

Find records including soft-deleted ones.

**Returns:** Promise with array of records

##### `isDeleted(record)`

Check if a record is soft-deleted.

**Returns:** boolean

##### `getDeletionMetadata(record)`

Get deletion metadata from a record.

**Returns:** `{ deletedAt: Date, deletedBy: string | null } | null`

### SQLAlchemy (Python)

#### Mixin

##### `SoftDeleteMixin`

Mixin class that adds soft delete functionality to models.

**Added Fields:**

- `deleted_at`: DateTime - When the record was deleted
- `deleted_by`: String - Who deleted the record

**Methods:**

- `soft_delete(deleted_by?)`: Mark this record as deleted
- `restore()`: Restore this record
- `is_deleted()`: Check if record is deleted
- `filter_active(query)`: Filter query to only active records
- `filter_deleted(query)`: Filter query to only deleted records

#### Helper Functions

##### `soft_delete_record(session, model, record_id, deleted_by?, id_field?)`

Soft delete a single record by ID.

##### `soft_delete_many(session, model, deleted_by?, **filters)`

Soft delete multiple records matching filters.

##### `restore_record(session, model, record_id, id_field?)`

Restore a soft-deleted record by ID.

##### `restore_many(session, model, **filters)`

Restore multiple soft-deleted records.

##### `get_active_records(session, model, **filters)`

Get all active (non-deleted) records.

##### `get_deleted_records(session, model, **filters)`

Get all soft-deleted records.

## Best Practices

### 1. Choose Models Wisely

Not all models should use soft delete. Exclude:

- Audit logs
- Transaction records
- Historical data that must be permanent

```typescript
prisma.$use(
  createSoftDeleteMiddleware({
    excludedModels: [
      "AuditLog",
      "Transaction",
      "WalletAuditLog",
      "CreditEvent",
    ],
  }),
);
```

### 2. Index Soft Delete Fields

Always add an index on `deleted_at` for performance:

```prisma
@@index([deletedAt])
```

### 3. Track Who Deleted

Always provide `deletedBy` for audit purposes:

```typescript
await softDelete(
  prisma.product,
  { id: productId },
  { deletedBy: currentUserId }, // Important for audit trail
);
```

### 4. Handle Unique Constraints

For unique fields, consider including `deletedAt` in the constraint:

```prisma
@@unique([email, deletedAt])
```

This allows re-using emails after deletion.

### 5. Use with Caution in Transactions

Be aware of optimistic locking when using soft delete in transactions:

```typescript
await prisma.$transaction(async (tx) => {
  await softDelete(tx.product, { id: productId }, { deletedBy: userId });
  // Other operations...
});
```

## Advanced Usage

### Cascade Soft Delete

```typescript
async function cascadeDeleteOrder(orderId: string, deletedBy: string) {
  // Delete order items first (if they support soft delete)
  await softDeleteMany(prisma.orderItem, { orderId }, { deletedBy });

  // Then delete the order
  await softDelete(prisma.order, { id: orderId }, { deletedBy });
}
```

### Periodic Cleanup

Permanently delete old soft-deleted records:

```typescript
async function cleanupOldDeletedRecords() {
  const sixMonthsAgo = new Date();
  sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

  // Find old deleted records
  const oldDeleted = await prisma.product.findMany({
    where: {
      deletedAt: { lt: sixMonthsAgo },
    },
    includeDeleted: true,
  });

  // Hard delete them (requires excluding from middleware)
  for (const record of oldDeleted) {
    await hardDelete(prisma.product, { id: record.id });
  }
}
```

### Deletion Audit Reports

```typescript
async function getDeletionReport(startDate: Date, endDate: Date) {
  const deletedProducts = await prisma.product.findMany({
    where: {
      deletedAt: {
        gte: startDate,
        lte: endDate,
      },
    },
    includeDeleted: true,
  });

  return deletedProducts.map((p) => ({
    id: p.id,
    name: p.name,
    deletedAt: p.deletedAt,
    deletedBy: p.deletedBy,
  }));
}
```

## Testing

### Unit Tests

```typescript
describe("Soft Delete", () => {
  it("should soft delete a product", async () => {
    const product = await prisma.product.create({
      data: { name: "Test Product", price: 100 },
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

  it("should exclude deleted products from queries", async () => {
    const products = await prisma.product.findMany();

    expect(products.every((p) => p.deletedAt === null)).toBe(true);
  });
});
```

## Troubleshooting

### Issue: Middleware not working

**Solution:** Ensure middleware is applied before any database operations:

```typescript
const prisma = new PrismaClient();
prisma.$use(createSoftDeleteMiddleware()); // Apply immediately after creation
```

### Issue: TypeScript errors with `includeDeleted`

**Solution:** Add type assertion:

```typescript
const products = await prisma.product.findMany({
  // @ts-ignore - includeDeleted is handled by middleware
  includeDeleted: true,
});
```

### Issue: Unique constraint violations

**Solution:** Include `deletedAt` in unique constraints:

```prisma
@@unique([email, deletedAt])
```

## Migration from Hard Delete

1. **Add soft delete fields** to your models
2. **Run migration** to add columns
3. **Apply middleware** to your Prisma client
4. **Update tests** to account for soft delete behavior
5. **Gradually update** delete operations to use soft delete

## License

MIT

## Contributing

Contributions are welcome! Please read the contributing guidelines first.

## Support

For issues and questions, please use the GitHub issue tracker.
