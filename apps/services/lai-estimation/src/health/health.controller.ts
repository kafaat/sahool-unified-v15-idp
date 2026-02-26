/**
 * Health Controller - مراقب الصحة
 * Kubernetes health check endpoints for lai-estimation service
 */

import { Controller, Get } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import { SkipTenantCheck } from "@sahool/nestjs-auth";

@ApiTags("health")
@Controller()
@SkipTenantCheck()
export class HealthController {
  @Get("healthz")
  @ApiOperation({ summary: "Liveness probe | فحص الحياة" })
  @ApiResponse({ status: 200, description: "Service is alive" })
  healthCheck() {
    return {
      status: "ok",
      service: "lai-estimation",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }

  @Get("readyz")
  @ApiOperation({ summary: "Readiness probe | فحص الجاهزية" })
  @ApiResponse({ status: 200, description: "Service is ready" })
  readinessCheck() {
    return {
      status: "ready",
      service: "lai-estimation",
      version: "16.0.0",
      checks: {
        lai_engine: "initialized",
        indices_engine: "initialized",
      },
      timestamp: new Date().toISOString(),
    };
  }
}
