/**
 * SAHOOL Field Management Service - App Module
 * Version: 16.0.0
 *
 * Unified field management with NestJS architecture
 */

import { Module } from "@nestjs/common";
import { APP_GUARD, APP_INTERCEPTOR, APP_FILTER } from "@nestjs/core";
import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler";
import { JwtAuthGuard } from "./auth/jwt-auth.guard";
import { TenantGuard } from "./auth/tenant.guard";

// Core modules
import { PrismaModule } from "./prisma/prisma.module";
import { CacheModule } from "./cache/cache.module";
import { CacheInterceptor } from "./cache/cache.interceptor";
import { HttpExceptionFilter } from "./filters/http-exception.filter";

// Feature modules
import { FieldsModule } from "./fields/fields.module";
import { TasksModule } from "./tasks/tasks.module";
import { NdviModule } from "./ndvi/ndvi.module";
import { SyncModule } from "./sync/sync.module";
import { HealthModule } from "./health/health.module";
import { CropSeasonsModule } from "./crop-seasons/crop-seasons.module";
import { DashboardModule } from "./dashboard/dashboard.module";
import { FieldOperationsModule } from "./field-operations/field-operations.module";
import { FieldSubZonesModule } from "./field-sub-zones/field-sub-zones.module";
import { FieldReportsModule } from "./field-reports/field-reports.module";
import { OutboxModule } from "./outbox/outbox.module";
import { IdempotencyModule } from "./idempotency/idempotency.module";
import { ErpSyncModule } from "./erp-sync/erp-sync.module";

@Module({
  imports: [
    // Rate limiting configuration
    ThrottlerModule.forRoot([
      {
        name: "short",
        ttl: 1000,
        limit: 20,
      },
      {
        name: "medium",
        ttl: 60000,
        limit: 200,
      },
      {
        name: "long",
        ttl: 3600000,
        limit: 2000,
      },
    ]),

    // Redis cache configuration (global module)
    CacheModule,

    // Core modules
    PrismaModule,

    // Feature modules
    FieldsModule,
    TasksModule,
    NdviModule,
    SyncModule,
    HealthModule,
    CropSeasonsModule,
    DashboardModule,
    FieldOperationsModule,
    FieldSubZonesModule,
    FieldReportsModule,
    // Infrastructure modules for enterprise accounting + reliability
    OutboxModule,
    IdempotencyModule,
    ErpSyncModule,
  ],
  providers: [
    // Global rate limiting guard
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
    // Global JWT authentication guard
    {
      provide: APP_GUARD,
      useClass: JwtAuthGuard,
    },
    // Global tenant isolation guard
    {
      provide: APP_GUARD,
      useClass: TenantGuard,
    },
    // Global cache interceptor
    {
      provide: APP_INTERCEPTOR,
      useClass: CacheInterceptor,
    },
    // Global exception filter
    {
      provide: APP_FILTER,
      useClass: HttpExceptionFilter,
    },
  ],
})
export class AppModule {}
