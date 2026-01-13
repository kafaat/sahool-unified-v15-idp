# ORM Standardization Guide for SAHOOL Services

## Executive Summary

This document standardizes ORM (Object-Relational Mapping) usage across all SAHOOL microservices. After analyzing the codebase, we recommend **Prisma** as the standard ORM for all database-enabled services.

**Date**: 2025-12-31
**Status**: RECOMMENDATION
**Migration Priority**: HIGH for field-core and field-management-service

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Recommendation: Prisma as Standard](#recommendation-prisma-as-standard)
3. [Services Requiring Migration](#services-requiring-migration)
4. [Migration Guide](#migration-guide)
5. [Best Practices](#best-practices)
6. [Implementation Checklist](#implementation-checklist)

---

## Current State Analysis

### Services Using Prisma (8 services)

The following services are already using Prisma and represent the **standard implementation**:

| Service                    | Prisma Version | Database   | Schema Location                                           |
| -------------------------- | -------------- | ---------- | --------------------------------------------------------- |
| `chat-service`             | 5.22.0         | PostgreSQL | `/apps/services/chat-service/prisma/schema.prisma`        |
| `crop-growth-model`        | 5.22.0         | PostgreSQL | N/A (schema not yet created)                              |
| `disaster-assessment`      | 5.22.0         | PostgreSQL | N/A (schema not yet created)                              |
| `lai-estimation`           | 5.22.0         | PostgreSQL | N/A (schema not yet created)                              |
| `marketplace-service`      | 5.22.0         | PostgreSQL | `/apps/services/marketplace-service/prisma/schema.prisma` |
| `research-core`            | 5.22.0         | PostgreSQL | `/apps/services/research-core/prisma/schema.prisma`       |
| `yield-prediction`         | 5.22.0         | PostgreSQL | N/A (schema not yet created)                              |
| `yield-prediction-service` | 5.22.0         | PostgreSQL | N/A (schema not yet created)                              |

**Status**: These services are compliant with the standard. No action required.

---

### Services Using TypeORM (2 services - REQUIRES MIGRATION)

| Service                    | TypeORM Version | Prisma Version     | Status               | Migration Priority |
| -------------------------- | --------------- | ------------------ | -------------------- | ------------------ |
| `field-core`               | 0.3.20          | 5.22.0 (installed) | **MIGRATION NEEDED** | HIGH               |
| `field-management-service` | 0.3.20          | 5.22.0 (installed) | **MIGRATION NEEDED** | HIGH               |

**Critical Finding**: Both services have Prisma schemas already defined alongside TypeORM entities, indicating a **migration is in progress** but incomplete.

#### field-core Current Implementation:

- **Active ORM**: TypeORM (via `src/data-source.ts`)
- **TypeORM Entities**: `Field`, `FieldBoundaryHistory`, `SyncStatus`
- **Prisma Schema**: Available at `prisma/schema.prisma` (mirrors TypeORM entities)
- **Special Requirements**: PostGIS extension for geospatial operations

#### field-management-service Current Implementation:

- **Active ORM**: TypeORM (via `src/data-source.ts`)
- **TypeORM Entities**: `Field`, `FieldBoundaryHistory`, `SyncStatus`
- **Prisma Schema**: Available at `prisma/schema.prisma` (mirrors TypeORM entities)
- **Special Requirements**: PostGIS extension for geospatial operations

---

### Services Without ORM

The following services do not use database ORMs (in-memory, stateless, or external storage):

- `community-chat` (uses Socket.IO, in-memory)
- `iot-service` (no ORM dependencies)
- Multiple other services

**Status**: No action required.

---

## Recommendation: Prisma as Standard

### Why Prisma?

1. **Majority Adoption**: 8 out of 10 database-enabled services already use Prisma
2. **Type Safety**: Auto-generated TypeScript types eliminate runtime errors
3. **Developer Experience**: Intuitive schema definition language
4. **Migration System**: Built-in migration management (`prisma migrate`)
5. **Performance**: Optimized query generation and connection pooling
6. **Modern Features**: Built-in support for PostgreSQL extensions (including PostGIS)
7. **Tooling**: Prisma Studio for database visualization

### Prisma Advantages Over TypeORM

| Feature               | Prisma                               | TypeORM                          |
| --------------------- | ------------------------------------ | -------------------------------- |
| **Type Safety**       | Fully type-safe, auto-generated      | Manual type definitions required |
| **Schema Definition** | Declarative Prisma Schema Language   | Decorator-based entities         |
| **Migrations**        | Built-in, version-controlled         | Requires manual setup            |
| **Query Builder**     | Type-safe, auto-complete             | Runtime type checking            |
| **PostGIS Support**   | Native via `Unsupported()` + raw SQL | Requires manual configuration    |
| **Performance**       | Optimized query generation           | Good, but requires tuning        |
| **Learning Curve**    | Gentle                               | Steep                            |

---

## Services Requiring Migration

### Priority 1: field-core

**Path**: `/home/user/sahool-unified-v15-idp/apps/services/field-core`

**Current State**:

- Uses TypeORM with 3 entities: `Field`, `FieldBoundaryHistory`, `SyncStatus`
- Prisma schema already defined (ready for migration)
- PostGIS extension for geospatial operations
- Complex geospatial queries using raw SQL

**Migration Complexity**: **MEDIUM**

- Prisma schema already exists and mirrors TypeORM entities
- Need to update service layer to use PrismaClient
- PostGIS operations already use raw SQL (compatible with Prisma)

---

### Priority 2: field-management-service

**Path**: `/home/user/sahool-unified-v15-idp/apps/services/field-management-service`

**Current State**:

- Identical to field-core (same entities and schema)
- Uses TypeORM with 3 entities: `Field`, `FieldBoundaryHistory`, `SyncStatus`
- Prisma schema already defined
- PostGIS extension for geospatial operations

**Migration Complexity**: **MEDIUM**

- Can leverage migration strategy from field-core
- Same entities and operations

---

## Migration Guide

### Phase 1: Pre-Migration Preparation

#### Step 1: Review Existing Prisma Schema

Both services already have Prisma schemas. Verify they are complete:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/field-core
cat prisma/schema.prisma
```

The schema includes:

- ✅ PostgreSQL datasource
- ✅ PostGIS extension support
- ✅ All TypeORM entities (Field, FieldBoundaryHistory, SyncStatus, Task, NdviReading)
- ✅ Proper indexes
- ✅ Enums (FieldStatus, ChangeSource, SyncState, TaskType, Priority, TaskState)

#### Step 2: Set Up Prisma Environment

```bash
# Set DATABASE_URL in .env
echo "DATABASE_URL=postgresql://sahool:sahool@postgres:5432/sahool" > .env

# Generate Prisma Client
npm run prisma:generate
```

---

### Phase 2: Database Migration

#### Step 1: Create Initial Migration from Existing Schema

Since the database already exists (managed by TypeORM), use Prisma's introspection:

```bash
# Option A: If you want to keep existing data (RECOMMENDED)
# Create migration from existing schema
npm run prisma:migrate:dev --name init_from_typeorm

# Option B: If starting fresh (NOT RECOMMENDED for production)
npm run prisma:db:push
```

#### Step 2: Verify Migration

```bash
# Check migration status
npm run prisma:migrate:status

# Open Prisma Studio to verify data
npm run prisma:studio
```

---

### Phase 3: Code Migration

#### Step 1: Create Prisma Service Module

Create a Prisma service for dependency injection (if using NestJS) or as a singleton:

**File**: `src/prisma/prisma.service.ts` (or `src/lib/prisma.ts` for Express)

```typescript
import { PrismaClient } from "@prisma/client";

// Express/Node.js approach
export const prisma = new PrismaClient({
  log:
    process.env.NODE_ENV !== "production"
      ? ["query", "info", "warn", "error"]
      : ["error"],
});

// Graceful shutdown
process.on("beforeExit", async () => {
  await prisma.$disconnect();
});
```

#### Step 2: Update Data Access Layer

Replace TypeORM repository patterns with Prisma Client:

**Before (TypeORM)**:

```typescript
import { AppDataSource } from "./data-source";
import { Field } from "./entity/Field";

const fieldRepo = AppDataSource.getRepository(Field);
const fields = await fieldRepo.find({
  where: { tenantId: "abc123" },
});
```

**After (Prisma)**:

```typescript
import { prisma } from "./lib/prisma";

const fields = await prisma.field.findMany({
  where: { tenantId: "abc123" },
});
```

#### Step 3: Migration Patterns

##### Pattern 1: Find Operations

```typescript
// TypeORM
const field = await fieldRepo.findOne({ where: { id } });

// Prisma
const field = await prisma.field.findUnique({ where: { id } });
```

##### Pattern 2: Create Operations

```typescript
// TypeORM
const newField = fieldRepo.create({ name, tenantId, cropType });
const saved = await fieldRepo.save(newField);

// Prisma
const saved = await prisma.field.create({
  data: { name, tenantId, cropType },
});
```

##### Pattern 3: Update Operations

```typescript
// TypeORM
const field = await fieldRepo.findOne({ where: { id } });
field.name = newName;
await fieldRepo.save(field);

// Prisma
const updated = await prisma.field.update({
  where: { id },
  data: { name: newName },
});
```

##### Pattern 4: Delete Operations

```typescript
// TypeORM
await fieldRepo.delete(id);

// Prisma
await prisma.field.delete({ where: { id } });
```

##### Pattern 5: Complex Queries with Relations

```typescript
// TypeORM
const field = await fieldRepo.findOne({
  where: { id },
  relations: ["boundaryHistory", "tasks"],
});

// Prisma
const field = await prisma.field.findUnique({
  where: { id },
  include: {
    boundaryHistory: true,
    tasks: true,
  },
});
```

##### Pattern 6: Raw SQL Queries (PostGIS)

```typescript
// TypeORM
const fields = await AppDataSource.query(
  `
  SELECT id, ST_AsGeoJSON(boundary) as boundary
  FROM fields WHERE id = $1
`,
  [id],
);

// Prisma (same approach - Prisma supports raw SQL)
const fields = await prisma.$queryRaw`
  SELECT id, ST_AsGeoJSON(boundary) as boundary
  FROM fields WHERE id = ${id}
`;
```

##### Pattern 7: Transactions

```typescript
// TypeORM
await AppDataSource.transaction(async (transactionalEntityManager) => {
  await transactionalEntityManager.save(field);
  await transactionalEntityManager.save(history);
});

// Prisma
await prisma.$transaction([
  prisma.field.create({ data: fieldData }),
  prisma.fieldBoundaryHistory.create({ data: historyData }),
]);

// Or with callback for complex logic
await prisma.$transaction(async (tx) => {
  const field = await tx.field.create({ data: fieldData });
  await tx.fieldBoundaryHistory.create({
    data: { ...historyData, fieldId: field.id },
  });
});
```

---

### Phase 4: Testing

#### Step 1: Unit Tests

Update unit tests to use Prisma Client:

```typescript
import { PrismaClient } from "@prisma/client";
import { mockDeep, DeepMockProxy } from "jest-mock-extended";

let prisma: DeepMockProxy<PrismaClient>;

beforeEach(() => {
  prisma = mockDeep<PrismaClient>();
});

it("should create a field", async () => {
  const mockField = { id: "1", name: "Test Field" /* ... */ };
  prisma.field.create.mockResolvedValue(mockField);

  const result = await createField({ name: "Test Field" });

  expect(result).toEqual(mockField);
  expect(prisma.field.create).toHaveBeenCalled();
});
```

#### Step 2: Integration Tests

```bash
# Use a test database
export DATABASE_URL="postgresql://sahool:sahool@postgres:5432/sahool_test"

# Run migrations
npm run prisma:migrate:deploy

# Run tests
npm test

# Clean up
npm run prisma:migrate:reset -- --force
```

---

### Phase 5: Deployment

#### Step 1: Update package.json

Remove TypeORM dependencies:

```json
{
  "dependencies": {
    "@prisma/client": "^5.22.0"
  },
  "devDependencies": {
    "prisma": "^5.22.0"
  }
}
```

Remove these lines:

```json
"typeorm": "^0.3.20",
"reflect-metadata": "^0.2.2"
```

#### Step 2: Update Build Scripts

Update `package.json` scripts:

```json
{
  "scripts": {
    "build": "prisma generate && tsc",
    "dev": "prisma generate && ts-node-dev --respawn src/index.ts",
    "db:migrate": "prisma migrate deploy",
    "db:reset": "prisma migrate reset --force"
  }
}
```

#### Step 3: Update Dockerfile

```dockerfile
# Generate Prisma Client before build
RUN npm run prisma:generate

# Copy prisma directory
COPY prisma ./prisma
```

#### Step 4: Remove TypeORM Artifacts

```bash
# Remove TypeORM entities
rm -rf src/entity/

# Remove TypeORM data source
rm src/data-source.ts

# Remove reflect-metadata imports
grep -r "reflect-metadata" src/ --files-with-matches | xargs sed -i '/reflect-metadata/d'
```

---

## Best Practices

### 1. Schema Organization

```prisma
// Use clear naming conventions
model Field {
  id String @id @default(uuid()) @db.Uuid

  // Group related fields with comments
  // Basic Info
  name     String  @db.VarChar(255)
  tenantId String  @map("tenant_id") @db.VarChar(100)

  // Always map to snake_case database columns
  createdAt DateTime @default(now()) @map("created_at")

  @@map("fields") // Explicit table name
  @@index([tenantId]) // Add indexes for performance
}
```

### 2. Connection Management

```typescript
// Use connection pooling
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
  // Add connection pool settings via DATABASE_URL
  // postgresql://user:pass@host:5432/db?connection_limit=10&pool_timeout=20
});
```

### 3. Error Handling

```typescript
import { Prisma } from "@prisma/client";

try {
  await prisma.field.create({ data: fieldData });
} catch (error) {
  if (error instanceof Prisma.PrismaClientKnownRequestError) {
    // Handle specific Prisma errors
    if (error.code === "P2002") {
      throw new Error("Unique constraint violation");
    }
  }
  throw error;
}
```

### 4. Type Safety

```typescript
// Use generated types
import { Field, Prisma } from "@prisma/client";

type FieldWithHistory = Prisma.FieldGetPayload<{
  include: { boundaryHistory: true };
}>;

function processField(field: FieldWithHistory) {
  // field.boundaryHistory is properly typed
  console.log(field.boundaryHistory.length);
}
```

### 5. Migrations

```bash
# Development: Create and apply migrations
npm run prisma:migrate:dev --name add_health_score

# Production: Only apply migrations (no schema changes)
npm run prisma:migrate:deploy

# Check migration status
npm run prisma:migrate:status
```

### 6. PostGIS Integration

```prisma
// Use Unsupported for PostGIS types
model Field {
  boundary Unsupported("geometry(Polygon, 4326)")?
  centroid Unsupported("geometry(Point, 4326)")?

  @@map("fields")
}

// Enable PostGIS extension
datasource db {
  provider   = "postgresql"
  url        = env("DATABASE_URL")
  extensions = [postgis]
}
```

```typescript
// Use raw SQL for PostGIS operations
const nearbyFields = await prisma.$queryRaw`
  SELECT id, name,
    ST_AsGeoJSON(boundary) as boundary,
    ST_Distance(
      centroid::geography,
      ST_SetSRID(ST_MakePoint(${lng}, ${lat}), 4326)::geography
    ) as distance_meters
  FROM fields
  WHERE ST_DWithin(
    centroid::geography,
    ST_SetSRID(ST_MakePoint(${lng}, ${lat}), 4326)::geography,
    ${radiusMeters}
  )
  ORDER BY distance_meters ASC
`;
```

---

## Implementation Checklist

### For field-core Migration

- [ ] **Phase 1: Preparation**
  - [ ] Review existing Prisma schema
  - [ ] Set up DATABASE_URL in .env
  - [ ] Generate Prisma Client (`npm run prisma:generate`)
  - [ ] Backup production database

- [ ] **Phase 2: Database Migration**
  - [ ] Create initial migration from TypeORM schema
  - [ ] Verify migration with Prisma Studio
  - [ ] Test on staging environment

- [ ] **Phase 3: Code Migration**
  - [ ] Create Prisma service module
  - [ ] Update all repository calls in `src/index.ts`
  - [ ] Update Field operations
  - [ ] Update FieldBoundaryHistory operations
  - [ ] Update SyncStatus operations
  - [ ] Update Task operations
  - [ ] Update NdviReading operations
  - [ ] Test PostGIS raw SQL queries

- [ ] **Phase 4: Testing**
  - [ ] Unit tests pass
  - [ ] Integration tests pass
  - [ ] E2E tests pass
  - [ ] Load testing on staging

- [ ] **Phase 5: Cleanup**
  - [ ] Remove TypeORM dependencies
  - [ ] Remove entity files
  - [ ] Remove data-source.ts
  - [ ] Update Dockerfile
  - [ ] Update CI/CD pipelines

- [ ] **Phase 6: Deployment**
  - [ ] Deploy to staging
  - [ ] Verify all endpoints work
  - [ ] Monitor performance
  - [ ] Deploy to production
  - [ ] Monitor for errors

### For field-management-service Migration

- [ ] Use same checklist as field-core
- [ ] Leverage lessons learned from field-core migration
- [ ] Ensure identical schema and behavior

---

## Migration Timeline Estimate

| Service                    | Complexity | Estimated Time | Priority |
| -------------------------- | ---------- | -------------- | -------- |
| `field-core`               | Medium     | 2-3 days       | HIGH     |
| `field-management-service` | Medium     | 1-2 days       | HIGH     |

**Total Estimated Time**: 3-5 days (one developer)

---

## Support and Resources

### Official Documentation

- [Prisma Documentation](https://www.prisma.io/docs)
- [Prisma Migrate](https://www.prisma.io/docs/concepts/components/prisma-migrate)
- [TypeORM to Prisma Migration Guide](https://www.prisma.io/docs/guides/migrate-to-prisma/migrate-from-typeorm)

### Internal Resources

- Existing Prisma implementations:
  - `/apps/services/chat-service` - Clean Prisma implementation
  - `/apps/services/marketplace-service` - Prisma with relations
  - `/apps/services/field-core/prisma/schema.prisma` - PostGIS example

### Getting Help

- Review existing Prisma schemas in other services
- Check Prisma Discord community
- Consult SAHOOL architecture team

---

## Appendix A: Full Schema Comparison

### field-core TypeORM Entities vs Prisma Schema

Both implementations are functionally equivalent. The Prisma schema already mirrors all TypeORM entities:

**Entities/Models**:

- ✅ Field
- ✅ FieldBoundaryHistory
- ✅ SyncStatus
- ✅ Task
- ✅ NdviReading

**Enums**:

- ✅ FieldStatus
- ✅ ChangeSource
- ✅ SyncState
- ✅ TaskType
- ✅ Priority
- ✅ TaskState

**Special Features**:

- ✅ PostGIS geometry types (via `Unsupported()`)
- ✅ Optimistic locking (version field)
- ✅ Cascade deletes
- ✅ Proper indexes

---

## Appendix B: Common Prisma Patterns for SAHOOL

### Pattern: Multi-Tenant Filtering

```typescript
// Always filter by tenantId for multi-tenant services
const fields = await prisma.field.findMany({
  where: { tenantId: req.user.tenantId },
});
```

### Pattern: Soft Deletes

```typescript
// Use status field instead of hard deletes
await prisma.field.update({
  where: { id },
  data: { status: "inactive", isDeleted: true },
});

// Filter out soft-deleted records
const activeFields = await prisma.field.findMany({
  where: { isDeleted: false },
});
```

### Pattern: Optimistic Locking

```typescript
// Prisma doesn't have built-in optimistic locking
// Implement manually using version field
try {
  await prisma.field.updateMany({
    where: {
      id: fieldId,
      version: currentVersion,
    },
    data: {
      name: newName,
      version: { increment: 1 },
    },
  });
} catch (error) {
  if (result.count === 0) {
    throw new Error("Conflict: Field was updated by another user");
  }
}
```

### Pattern: Batch Operations

```typescript
// Use transactions for batch operations
const results = await prisma.$transaction(
  fields.map((field) => prisma.field.create({ data: field })),
);
```

---

## Conclusion

Migrating to Prisma as the standard ORM will:

- ✅ Unify ORM usage across all services
- ✅ Improve type safety and developer experience
- ✅ Reduce maintenance complexity
- ✅ Enable better tooling and IDE support
- ✅ Provide a clear migration path for new services

The migration is **RECOMMENDED** and should be prioritized for `field-core` and `field-management-service`.

---

**Document Version**: 1.0
**Last Updated**: 2025-12-31
**Author**: SAHOOL Engineering Team
**Status**: APPROVED FOR IMPLEMENTATION
