/**
 * Health Controller - مراقب الصحة
 * Kubernetes health check endpoints for crop-growth-model service
 */

import { Controller, Get, HttpStatus, Res } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import type { Response } from "express";
import { Public } from "@sahool/nestjs-auth";

@ApiTags("health")
@Controller()
export class HealthController {
  private readonly startTime = Date.now();

  @Get("healthz")
  @Public()
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
  @Public()
  @ApiOperation({ summary: "Readiness probe | فحص الجاهزية" })
  @ApiResponse({ status: 200, description: "Service is ready" })
  @ApiResponse({ status: 503, description: "Service is not ready" })
  readinessCheck(@Res() res: Response) {
    const checks: Record<string, string> = {};
    const uptime = Math.floor((Date.now() - this.startTime) / 1000);

    // Verify memory is not exhausted
    const memUsage = process.memoryUsage();
    const heapUsedMB = Math.round(memUsage.heapUsed / 1024 / 1024);
    const heapTotalMB = Math.round(memUsage.heapTotal / 1024 / 1024);
    const heapPercent = Math.round((memUsage.heapUsed / memUsage.heapTotal) * 100);

    checks["memory"] = heapPercent < 95 ? "ok" : "pressure";
    checks["event_loop"] = "ok";

    const allReady = Object.values(checks).every((v) => v !== "pressure");
    const status = allReady ? "ready" : "degraded";
    const httpStatus = allReady ? HttpStatus.OK : HttpStatus.SERVICE_UNAVAILABLE;

    res.status(httpStatus).json({
      status,
      service: "crop-growth-model",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
      uptime_seconds: uptime,
      checks,
      memory: {
        heap_used_mb: heapUsedMB,
        heap_total_mb: heapTotalMB,
        heap_percent: heapPercent,
      },
    });
  }
}
