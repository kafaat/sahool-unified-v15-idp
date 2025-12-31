# Prisma Service Template

This template provides the standard configuration for adding Prisma to any SAHOOL service.

---

## 1. package.json Configuration

```json
{
  "name": "your-service-name",
  "version": "16.0.0",
  "scripts": {
    "start": "node dist/index.js",
    "build": "prisma generate && tsc",
    "dev": "prisma generate && ts-node-dev --respawn src/index.ts",
    "test": "jest",

    "prisma:generate": "prisma generate",
    "prisma:migrate": "prisma migrate dev",
    "prisma:migrate:deploy": "prisma migrate deploy",
    "prisma:migrate:status": "prisma migrate status",
    "prisma:migrate:reset": "prisma migrate reset",
    "prisma:db:push": "prisma db push",
    "prisma:db:pull": "prisma db pull",
    "prisma:studio": "prisma studio",
    "prisma:seed": "ts-node prisma/seed.ts",
    "db:setup": "npm run prisma:migrate:deploy && npm run prisma:generate",
    "db:reset": "npm run prisma:migrate:reset -- --force"
  },
  "dependencies": {
    "@prisma/client": "^5.22.0",
    "express": "^4.21.2",
    "pg": "^8.13.1",
    "dotenv": "^16.4.7",
    "cors": "^2.8.5",
    "uuid": "^11.0.3"
  },
  "devDependencies": {
    "prisma": "^5.22.0",
    "typescript": "^5.7.2",
    "@types/node": "^22.10.2",
    "@types/express": "^5.0.0",
    "ts-node-dev": "^2.0.0",
    "ts-node": "^10.9.2",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.1"
  },
  "prisma": {
    "schema": "prisma/schema.prisma",
    "seed": "ts-node prisma/seed.ts"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

---

## 2. Prisma Schema Template

**File**: `prisma/schema.prisma`

### Standard PostgreSQL Service

```prisma
// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL [Service Name] - Prisma Schema
// Database: PostgreSQL
// ═══════════════════════════════════════════════════════════════════════════

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// ─────────────────────────────────────────────────────────────────────────────
// Example Model
// ─────────────────────────────────────────────────────────────────────────────

model ExampleEntity {
  id String @id @default(uuid()) @db.Uuid

  // Basic Info
  name     String  @db.VarChar(255)
  tenantId String  @map("tenant_id") @db.VarChar(100)

  // Status
  status   Status  @default(active)

  // Metadata
  metadata Json?   @db.JsonB

  // Timestamps
  createdAt DateTime @default(now()) @map("created_at") @db.Timestamptz
  updatedAt DateTime @updatedAt @map("updated_at") @db.Timestamptz

  // Relations
  // relatedEntities RelatedEntity[]

  // Indexes
  @@index([tenantId], name: "idx_entity_tenant")
  @@index([status], name: "idx_entity_status")
  @@map("example_entities")
}

// Enums
enum Status {
  active
  inactive
  deleted

  @@map("status")
}
```

### PostgreSQL with PostGIS Extension

```prisma
generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["postgresqlExtensions"]
}

datasource db {
  provider   = "postgresql"
  url        = env("DATABASE_URL")
  extensions = [postgis]
}

model GeoEntity {
  id String @id @default(uuid()) @db.Uuid

  // Geospatial fields (PostGIS)
  location Unsupported("geometry(Point, 4326)")?
  boundary Unsupported("geometry(Polygon, 4326)")?

  // Regular fields
  name String @db.VarChar(255)

  @@map("geo_entities")
}
```

---

## 3. Prisma Client Setup

**File**: `src/lib/prisma.ts` (or `src/prisma/prisma.service.ts` for NestJS)

### Express/Node.js

```typescript
import { PrismaClient } from '@prisma/client';

// Create Prisma Client instance
export const prisma = new PrismaClient({
  log: process.env.NODE_ENV !== 'production'
    ? ['query', 'info', 'warn', 'error']
    : ['error'],
});

// Graceful shutdown
process.on('beforeExit', async () => {
  await prisma.$disconnect();
});

// Export types for convenience
export type { Prisma } from '@prisma/client';
```

### NestJS Module

```typescript
import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  constructor() {
    super({
      log: process.env.NODE_ENV !== 'production'
        ? ['query', 'info', 'warn', 'error']
        : ['error'],
    });
  }

  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
```

---

## 4. Environment Configuration

**File**: `.env`

```bash
# Database
DATABASE_URL="postgresql://sahool:sahool@postgres:5432/your_service_db"

# Database Pool Settings (optional)
# DATABASE_URL="postgresql://user:pass@host:5432/db?connection_limit=10&pool_timeout=20"

# Application
NODE_ENV=development
PORT=3000

# Service-specific vars
SERVICE_NAME=your-service-name
LOG_LEVEL=info
```

**File**: `.env.example`

```bash
DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
NODE_ENV=development
PORT=3000
```

---

## 5. TypeScript Configuration

**File**: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

---

## 6. Usage Examples

### Basic CRUD Operations

```typescript
import { prisma } from './lib/prisma';

// Create
const newEntity = await prisma.exampleEntity.create({
  data: {
    name: 'Example',
    tenantId: 'tenant-123',
    status: 'active'
  }
});

// Read - Find Unique
const entity = await prisma.exampleEntity.findUnique({
  where: { id: 'entity-id' }
});

// Read - Find Many
const entities = await prisma.exampleEntity.findMany({
  where: { tenantId: 'tenant-123' },
  orderBy: { createdAt: 'desc' },
  take: 10
});

// Update
const updated = await prisma.exampleEntity.update({
  where: { id: 'entity-id' },
  data: { name: 'Updated Name' }
});

// Delete
await prisma.exampleEntity.delete({
  where: { id: 'entity-id' }
});

// Soft Delete (update status)
await prisma.exampleEntity.update({
  where: { id: 'entity-id' },
  data: { status: 'deleted' }
});
```

### With Relations

```typescript
// Include relations
const entityWithRelations = await prisma.exampleEntity.findUnique({
  where: { id: 'entity-id' },
  include: {
    relatedEntities: true,
    otherRelation: {
      select: {
        id: true,
        name: true
      }
    }
  }
});

// Create with relations
const newEntity = await prisma.exampleEntity.create({
  data: {
    name: 'Example',
    tenantId: 'tenant-123',
    relatedEntities: {
      create: [
        { name: 'Related 1' },
        { name: 'Related 2' }
      ]
    }
  },
  include: {
    relatedEntities: true
  }
});
```

### Transactions

```typescript
// Simple transaction
const [entity1, entity2] = await prisma.$transaction([
  prisma.exampleEntity.create({ data: data1 }),
  prisma.exampleEntity.create({ data: data2 })
]);

// Interactive transaction
const result = await prisma.$transaction(async (tx) => {
  const entity = await tx.exampleEntity.create({ data });
  await tx.auditLog.create({
    data: {
      action: 'create',
      entityId: entity.id
    }
  });
  return entity;
});
```

### Raw SQL (for PostGIS or complex queries)

```typescript
// Raw query
const results = await prisma.$queryRaw`
  SELECT id, name, ST_AsGeoJSON(location) as location
  FROM geo_entities
  WHERE tenant_id = ${tenantId}
`;

// Raw execution (for INSERT/UPDATE/DELETE)
await prisma.$executeRaw`
  UPDATE geo_entities
  SET location = ST_SetSRID(ST_MakePoint(${lng}, ${lat}), 4326)
  WHERE id = ${id}
`;
```

---

## 7. Seed Data Template

**File**: `prisma/seed.ts`

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding database...');

  // Clear existing data (development only)
  if (process.env.NODE_ENV === 'development') {
    await prisma.exampleEntity.deleteMany();
  }

  // Create seed data
  const entities = await Promise.all([
    prisma.exampleEntity.create({
      data: {
        name: 'Example 1',
        tenantId: 'tenant-123',
        status: 'active'
      }
    }),
    prisma.exampleEntity.create({
      data: {
        name: 'Example 2',
        tenantId: 'tenant-123',
        status: 'active'
      }
    })
  ]);

  console.log(`Created ${entities.length} entities`);
}

main()
  .catch((e) => {
    console.error('Error seeding database:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

**Run seed**:
```bash
npm run prisma:seed
```

---

## 8. Docker Configuration

**File**: `Dockerfile`

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy prisma schema
COPY prisma ./prisma

# Generate Prisma Client
RUN npx prisma generate

# Copy source
COPY . .

# Build
RUN npm run build

# Expose port
EXPOSE 3000

# Start command
CMD ["sh", "-c", "npx prisma migrate deploy && npm start"]
```

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_USER: sahool
      POSTGRES_PASSWORD: sahool
      POSTGRES_DB: your_service_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://sahool:sahool@postgres:5432/your_service_db
      NODE_ENV: development
    depends_on:
      - postgres
    volumes:
      - .:/app
      - /app/node_modules

volumes:
  postgres_data:
```

---

## 9. Testing Configuration

**File**: `jest.config.js`

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
    '!src/**/__tests__/**'
  ],
  setupFilesAfterEnv: ['<rootDir>/src/test/setup.ts']
};
```

**File**: `src/test/setup.ts`

```typescript
import { PrismaClient } from '@prisma/client';
import { mockDeep, DeepMockProxy } from 'jest-mock-extended';

export type MockPrisma = DeepMockProxy<PrismaClient>;

export const createMockPrisma = (): MockPrisma => {
  return mockDeep<PrismaClient>();
};
```

---

## 10. Migration Workflow

### Initial Setup

```bash
# 1. Install dependencies
npm install

# 2. Create database
createdb your_service_db

# 3. Set DATABASE_URL
echo "DATABASE_URL=postgresql://sahool:sahool@localhost:5432/your_service_db" > .env

# 4. Create initial migration
npm run prisma:migrate:dev --name init

# 5. Generate Prisma Client
npm run prisma:generate

# 6. Seed database (optional)
npm run prisma:seed
```

### Development Workflow

```bash
# 1. Make schema changes in prisma/schema.prisma

# 2. Create and apply migration
npm run prisma:migrate:dev --name add_new_field

# 3. Prisma Client is auto-generated
```

### Production Deployment

```bash
# 1. Apply migrations (no dev dependencies)
npm run prisma:migrate:deploy

# 2. Start application
npm start
```

---

## 11. Checklist for New Service

- [ ] Copy this template structure
- [ ] Update `package.json` with service name
- [ ] Create `prisma/schema.prisma`
- [ ] Set up `.env` with DATABASE_URL
- [ ] Run `npm install`
- [ ] Run `npm run prisma:generate`
- [ ] Create initial migration
- [ ] Create Prisma client module (`src/lib/prisma.ts`)
- [ ] Implement service logic using Prisma
- [ ] Write tests
- [ ] Create seed data (optional)
- [ ] Update Dockerfile
- [ ] Document service-specific patterns

---

## 12. Best Practices

1. **Always use transactions** for operations affecting multiple tables
2. **Use snake_case** for database columns (via `@map`)
3. **Add indexes** for frequently queried fields
4. **Use enums** for status fields and fixed value sets
5. **Filter by tenantId** in multi-tenant services
6. **Use soft deletes** instead of hard deletes
7. **Version your migrations** (never edit existing migrations)
8. **Keep schemas documented** with comments
9. **Use Prisma Studio** for database inspection
10. **Test migrations** in staging before production

---

## Resources

- **Prisma Documentation**: https://www.prisma.io/docs
- **Prisma Schema Reference**: https://www.prisma.io/docs/reference/api-reference/prisma-schema-reference
- **Prisma Client API**: https://www.prisma.io/docs/reference/api-reference/prisma-client-reference
- **SAHOOL Examples**:
  - `/apps/services/chat-service`
  - `/apps/services/marketplace-service`
  - `/apps/services/field-core/prisma/schema.prisma`

---

**Template Version**: 1.0
**Last Updated**: 2025-12-31
**Maintained By**: SAHOOL Architecture Team
