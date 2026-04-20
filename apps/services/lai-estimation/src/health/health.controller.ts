/**
 * Health Controller - مراقب الصحة
 * Kubernetes health check endpoints for lai-estimation service
 */

import { Controller, Get } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import { Public } from "@sahool/nestjs-auth";

@ApiTags("health")
@Controller()
export class HealthController {
  @Get("healthz")
  @Public()
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
  @Public()
  @ApiOperation({ summary: "Readiness probe | فحص الجاهزية" })
  @ApiResponse({ status: 200, description: "Service is ready" })
  readinessCheck() {
    return {
      status: "ok",
      service: "lai-estimation",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }
}
