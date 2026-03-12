/**
 * Health Module - Service Health Checks
 */

import { Module } from "@nestjs/common";
import { HealthController } from "./health.controller";

// CacheService is provided globally by CacheModule (@Global) and does not need
// to be re-declared here; doing so would create a redundant local instance.
@Module({
  controllers: [HealthController],
})
export class HealthModule {}
