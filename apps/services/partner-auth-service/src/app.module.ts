/**
 * SAHOOL Partner Auth — Root Module
 * وحدة التطبيق الرئيسية
 */

import { Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler";
import { PrismaModule } from "./prisma/prisma.module";
import { HealthController, HealthzController } from "./health/health.controller";
import { OAuthModule } from "./oauth/oauth.module";
import { OidcModule } from "./oidc/oidc.module";

@Module({
  imports: [
    // Defense-in-depth rate limits. Kong does the primary per-partner
    // throttling via X-Sahool-Partner-Key; these guard against Kong outage
    // and against requests bypassing the gateway (internal/dev/test paths).
    ThrottlerModule.forRoot([
      { name: "short", ttl: 1_000, limit: 20 },
      { name: "medium", ttl: 60_000, limit: 200 },
      { name: "long", ttl: 3_600_000, limit: 5_000 },
    ]),
    PrismaModule,
    OAuthModule,
    OidcModule,
  ],
  controllers: [HealthController, HealthzController],
  providers: [
    { provide: APP_GUARD, useClass: ThrottlerGuard },
  ],
})
export class AppModule {}
