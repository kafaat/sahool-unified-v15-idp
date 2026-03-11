/**
 * Health Controller - مراقب الصحة
 * Kubernetes health check endpoints for crop-growth-model service
 */

import { Controller, Get } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";

@ApiTags("health")
@Controller()
export class HealthController {
  @Get("healthz")
  @ApiOperation({ summary: "Liveness probe | فحص الحياة" })
  @ApiResponse({ status: 200, description: "Service is alive" })
  healthCheck() {
    return {
      status: "ok",
      service: "crop-growth-model",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }

  @Get("readyz")
  @ApiOperation({ summary: "Readiness probe | فحص الجاهزية" })
  @ApiResponse({ status: 200, description: "Service is ready" })
  readinessCheck() {
    return {
      status: "ok",
      service: "crop-growth-model",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }
}
