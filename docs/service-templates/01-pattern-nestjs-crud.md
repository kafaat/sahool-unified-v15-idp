# 01 · NestJS + Prisma CRUD Service Template

**Gold standard:** `apps/services/field-management-service/`
**Use when:** the service owns persistent tenant data, exposes
HTTP REST/GraphQL, and publishes domain events.

> القالب الذهبي لخدمات Node.js / NestJS التي تمتلك بياناتها الخاصة
> وتنشر أحداث NATS.

---

## Why `field-management-service`?

Of the 9 NestJS services on the platform it is the most complete:

| Capability | field-management | Others (best competitor) |
|---|---|---|
| Models / entities | **15** (Farm, Field, Task, CropSeason, FieldOperation, OutboxEvent, IdempotencyKey, …) | marketplace 15, user 5 |
| `@@index` coverage | **66** | marketplace 69, user 26 |
| PostGIS extension declared | ✅ | disaster-assessment ✅ |
| Transactional Outbox | ✅ `OutboxEvent` + worker | — |
| IdempotencyKey model | ✅ | marketplace ✅ |
| Explicit `onDelete` on all FK | 10 relations | marketplace 3 → 12 after R-2 |
| NATS publisher using `EventSubjects` constants | ✅ (after R-2 in this branch) | iot ⚠ |
| Directory layout | feature modules + shared utils + cache | user-service flat |
| Test coverage | unit + integration + contract | user 36, marketplace mixed |

Everything in this template is cross-referenced to an actual file path
inside `field-management-service`.

---

## Canonical directory layout

```
apps/services/<service-name>/
├── Dockerfile                          # multi-stage (base · builder · production)
├── .dockerignore
├── package.json                        # scripts: build | start | test | prisma:*
├── tsconfig.json
├── nest-cli.json
├── jest.config.ts
├── README.md                           # bilingual Purpose · Architecture · API · Events · Ops
├── prisma/
│   ├── schema.prisma                   # generator+datasource with directUrl; every table has tenantId
│   └── migrations/
│       ├── migration_lock.toml
│       └── <timestamp>_<name>/
│           └── migration.sql
└── src/
    ├── main.ts                         # bootstrap — see §"Bootstrap anatomy"
    ├── app.module.ts                   # imports PrismaModule, EventsModule, HealthModule, domain modules
    ├── prisma/
    │   ├── prisma.module.ts
    │   └── prisma.service.ts           # lifecycle hooks — see §"Prisma service"
    ├── events/
    │   ├── events.module.ts            # @Global() exports the events service
    │   └── <domain>-events.service.ts  # NATS lifecycle + typed publish methods
    ├── health/
    │   └── health.controller.ts        # /healthz + /readyz + /health
    ├── auth/                           # JwtAuthGuard, Roles decorator, TenantGuard
    ├── utils/                          # http-exception filter, request-logging interceptor, db-utils
    ├── <domain>/                       # ONE module per aggregate — feature slices, not layers
    │   ├── <domain>.module.ts
    │   ├── <domain>.controller.ts
    │   ├── <domain>.service.ts
    │   ├── dto/
    │   │   ├── create-<domain>.dto.ts
    │   │   └── update-<domain>.dto.ts
    │   └── __tests__/
    │       └── <domain>.service.spec.ts
    └── __tests__/                       # cross-cutting (middleware, guards, config)
```

**Rule of thumb:** one folder per aggregate root, not per layer (no
`controllers/`, `services/`, `repositories/` at top level). Cross-cutting
concerns live in `auth/`, `utils/`, `events/`, `prisma/`, `health/`.

---

## Bootstrap anatomy (`src/main.ts`)

Required sequence — order matters:

```ts
import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import helmet from 'helmet';
import { ValidationPipe, RequestMethod } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from './utils/http-exception.filter';
import { RequestLoggingInterceptor } from './utils/request-logging.interceptor';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    bufferLogs: true,                     // structured logs from onModuleInit
  });

  app.use(helmet());                      // security headers
  app.enableCors({                        // explicit allow-list, never '*' in prod
    origin: process.env.CORS_ORIGINS?.split(',') ?? ['https://sahool.io'],
    credentials: true,
  });

  app.useGlobalFilters(new HttpExceptionFilter());
  app.useGlobalInterceptors(new RequestLoggingInterceptor('<service>', false, false));
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,                       // drop unknown fields
    forbidNonWhitelisted: true,            // reject them loudly
    transform: true,
  }));

  // Health endpoints NEVER under /api/v1 — K8s probes hit them directly.
  app.setGlobalPrefix('api/v1', {
    exclude: [
      { path: 'healthz', method: RequestMethod.GET },
      { path: 'readyz',  method: RequestMethod.GET },
      { path: 'health',  method: RequestMethod.GET },
    ],
  });

  if (process.env.NODE_ENV !== 'production') {
    const config = new DocumentBuilder()
      .setTitle('<Service> API')
      .setVersion('16.0.0')
      .addBearerAuth()
      .build();
    SwaggerModule.setup('docs', app, SwaggerModule.createDocument(app, config));
  }

  const port = Number(process.env.PORT ?? 3000);
  await app.listen(port);

  // Graceful shutdown — drain HTTP, then Prisma, then NATS.
  let shuttingDown = false;
  const stop = async (signal: string) => {
    if (shuttingDown) return;
    shuttingDown = true;
    console.log(`Received ${signal}, shutting down gracefully…`);
    await app.close();                    // fires onModuleDestroy on every module
    process.exit(0);
  };
  process.on('SIGTERM', () => void stop('SIGTERM'));
  process.on('SIGINT',  () => void stop('SIGINT'));
}
bootstrap();
```

---

## Prisma service

```ts
@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  async onModuleInit()    { await this.$connect(); }
  async onModuleDestroy() { await this.$disconnect(); }
}
```

- `DATABASE_URL` → PgBouncer (transaction mode).
- `DATABASE_URL_DIRECT` → direct to Postgres for migrations.
- Every table has `tenantId` + an index containing it — `./scripts/prisma-check.sh`
  enforces `prisma format --check` + `prisma validate`.

---

## Events module

Copy `field-management-service/src/events/field-events.service.ts` verbatim,
rename `FIELD_SUBJECTS` to `<DOMAIN>_SUBJECTS`, and add a typed publish
method per event.

Non-negotiables:

- NATS connects in `onModuleInit` **and tolerates failure** (degraded mode,
  NOT a crash) — a fresh deploy must succeed even if the NATS cluster is
  momentarily rolling.
- Every publish includes `{ tenantId, eventId, timestamp, version }`.
- Subjects use `EventSubjects.*` constants from `@sahool/shared-events`.
  Domain-specific ones (e.g. `sahool.field.crop_season.started`) declared
  as `as const` locally until promoted to the shared package.
- Every mutation on a domain aggregate must emit exactly one
  after-commit event. Use the transactional outbox if the caller is
  inside a `$transaction`.

---

## Critical cross-cutting files to copy

| File in gold standard | What it gives you | Should you copy verbatim? |
|---|---|---|
| `src/utils/http-exception.filter.ts` | Unified error envelope `{ success:false, error, error_ar, requestId }` | **Yes** |
| `src/utils/request-logging.interceptor.ts` | JSON access logs + `x-request-id` propagation | **Yes** |
| `src/utils/db-utils.ts` | `createPaginatedResponse`, `calculatePagination`, `GENERAL_TRANSACTION_CONFIG` | **Yes** |
| `src/auth/jwt-auth.guard.ts` + `tenant.guard.ts` | JWT verify + `tid` extraction | Copy, adapt |
| `src/auth/roles.guard.ts` + `roles.decorator.ts` | RBAC | Copy, adapt |
| `src/cache/` | Redis cache-manager wrapper | Copy if the service has read-heavy endpoints |
| `src/events/field-events.service.ts` | NATS publisher skeleton | Copy, rename |
| `src/prisma/prisma.service.ts` | Prisma lifecycle | **Yes** |
| `src/health/health.controller.ts` | K8s probes | **Yes** |
| `Dockerfile` | multi-stage Node build with `sahool` non-root user | **Yes** |

---

## Testing

- `src/<domain>/__tests__/<domain>.service.spec.ts` — unit tests per
  service, mocking Prisma + Events + external clients. Jest.
- `src/__tests__/` — middleware, guards, config.
- `integration_test/` or `test/` — spins up a Postgres + NATS via
  `testcontainers-node` and runs the real service.
- Every new public method needs at least one happy-path + one error-path
  spec. CI fails if coverage drops.

Example test-module shape (works for any service):

```ts
const module: TestingModule = await Test.createTestingModule({
  providers: [
    YourService,
    { provide: PrismaService, useValue: mockPrisma },
    { provide: YourEventsService, useValue: { publishX: jest.fn(), publishY: jest.fn() } },
  ],
}).compile();
```

---

## Known trade-offs

- NestJS DI adds ~150 ms cold-start on t3.medium K8s pods. Acceptable
  for tenant-data services; use Pattern 02 (FastAPI) when cold-start
  latency matters more (e.g. IoT ingest).
- Prisma transaction mode + PgBouncer forces either `pgbouncer=true` on
  the pooled URL or `directUrl` for migrations. Both are required
  together — the Prisma template already declares both.

---

## Coverage matrix (fill in during each audit)

| Service | Pattern 01? | OutboxEvent | IdempotencyKey | EventSubjects usage | onDelete explicit | Integration tests | Last audit |
|---|---|---|---|---|---|---|---|
| field-management-service | ✅ gold | ✅ | ✅ | ✅ | 10/10 | ✅ | 2026-04 |
| marketplace-service | ✅ | — | ✅ | constants | 12/12 (after audit) | partial | 2026-04 |
| user-service | ✅ | — | — | ✅ (after R-1a) | 3/3 | ✅ jest 36/36 | 2026-04 |
| chat-service | ✅ | — | — | ✅ (after R-1b) | 2/2 | ✅ jest 278/278 | 2026-04 |
| iot-service | ✅ | — | — | ✅ (after NATS fix) | 6/6 | — | 2026-04 |
| disaster-assessment | ✅ | — | — | — | 3/3 | — | — |
| research-core | ✅ | — | — | — | 14/14 | — | — |
| yield-prediction-service | ✅ | — | — | — | — | — | — |
| weather-service | ✅ | — | — | — | 0/0 (design) | — | — |
| partner-auth-service | ✅ | — | — | — | 4/4 | — | baseline migration created 2026-04 |

**Conformance action items** (any `—` or missing row above should become
a ticket in the service's tracker).
