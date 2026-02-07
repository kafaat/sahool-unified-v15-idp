/**
 * Health Module - Service Health Checks
 */

import { Module } from "@nestjs/common";
import { HealthController } from "./health.controller";
import { CacheService } from "../cache/cache.service";

@Module({
  controllers: [HealthController],
  providers: [CacheService],
})
export class HealthModule {}
