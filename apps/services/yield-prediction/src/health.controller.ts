/**
 * Health Controller - Kubernetes Health Probes
 * نقاط فحص الصحة لـ Kubernetes
 */

import { Controller, Get } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";

@ApiTags("health")
@Controller()
export class HealthController {
  @Get("healthz")
  @ApiOperation({ summary: "Liveness probe - فحص الحياة" })
  healthz() {
    return {
      status: "ok",
      service: "yield-prediction",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }

  @Get("readyz")
  @ApiOperation({ summary: "Readiness probe - فحص الجاهزية" })
  readyz() {
    return {
      status: "ready",
      service: "yield-prediction",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }
}
