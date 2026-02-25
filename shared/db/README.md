# Database Utilities

> أدوات قاعدة البيانات | Database Utilities

Shared TypeScript database utilities providing standardized patterns for connection pooling, pagination, backup strategies, and common database operations across all Node.js/NestJS services.

## Modules

| File | Purpose |
|------|---------|
| `index.ts` | Central barrel export (`DatabaseConfig` default export) |
| `db-utils.ts` | Pagination helpers, cursor pagination, common query utilities |
| `connection-pool-config.ts` | PgBouncer/Prisma connection pool configuration |
| `backup-strategies.ts` | WAL-G backup strategies and scheduling |

## Usage

```typescript
import { DatabaseConfig } from "@sahool/shared-db";
// or individual imports
import { PaginationParams, PaginatedResponse, CursorPaginationParams } from "@sahool/shared-db";
```

## Pagination

### Offset-Based Pagination

```typescript
interface PaginationParams {
  page: number;    // Current page (1-based)
  limit: number;   // Items per page
  take: number;    // Prisma take
  skip: number;    // Prisma skip
}

interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}
```

### Cursor-Based Pagination

```typescript
interface CursorPaginationParams {
  cursor?: string;
  take: number;
}

interface CursorPaginationMeta {
  hasNext: boolean;
  nextCursor?: string;
}
```

## Connection Pool Configuration

Standardized PgBouncer settings for all NestJS services:

| Setting | Value | Description |
|---------|-------|-------------|
| Pool Mode | Transaction | Recommended for Prisma |
| Max Connections | 250 | PgBouncer limit |
| Min Pool Size | 2 | Per-service minimum |
| Max Pool Size | 10 | Per-service maximum |

## Backup Strategies

WAL-G integration for PostgreSQL backup and point-in-time recovery. See `docker-compose.walg.yml` for deployment configuration.

## Related

- [PostgreSQL HA](../../infrastructure/core/postgres/) — Patroni HA setup
- [PgBouncer](../../infrastructure/core/pgbouncer/) — Connection pooling deployment
- [Database Tests](../../tests/database/) — Database-specific tests
