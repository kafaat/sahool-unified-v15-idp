import { Controller, Get } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import { Public } from "@sahool/nestjs-auth";

@ApiTags("health")
@Controller()
export class HealthController {
  @Public()
  @Get("healthz")
  @ApiOperation({ summary: "Liveness probe | فحص الحياة" })
  @ApiResponse({ status: 200, description: "Service is alive" })
  healthCheck() {
    return {
      status: "ok",
      service: "yield-prediction",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }

  @Public()
  @Get("readyz")
  @ApiOperation({ summary: "Readiness probe | فحص الجاهزية" })
  @ApiResponse({ status: 200, description: "Service is ready" })
  readinessCheck() {
    return {
      status: "ready",
      service: "yield-prediction",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }
}
