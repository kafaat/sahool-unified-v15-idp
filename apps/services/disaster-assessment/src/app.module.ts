// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Assessment App Module
// ═══════════════════════════════════════════════════════════════════════════════

import { Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler";
import { DisasterController } from "./disaster/disaster.controller";
import { DisasterService } from "./disaster/disaster.service";
import { AlertController } from "./alert/alert.controller";
import { AlertService } from "./alert/alert.service";

@Module({
  imports: [
    // Rate limiting configuration
    ThrottlerModule.forRoot([
      {
        name: "short",
        ttl: 1000, // 1 second
        limit: 10, // 10 requests per second
      },
      {
        name: "medium",
        ttl: 60000, // 1 minute
        limit: 100, // 100 requests per minute
      },
      {
        name: "long",
        ttl: 3600000, // 1 hour
        limit: 1000, // 1000 requests per hour
      },
    ]),
  ],
  controllers: [DisasterController, AlertController],
  providers: [
    DisasterService,
    AlertService,
    // Global rate limiting guard
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
})
export class AppModule {}
