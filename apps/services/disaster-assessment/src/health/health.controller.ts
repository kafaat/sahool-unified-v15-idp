/**
 * Health Controller - مراقب الصحة
 * Kubernetes health check endpoints for disaster-assessment service
 */

import { Controller, Get, SetMetadata } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import { SkipThrottle } from "@nestjs/throttler";
import { PrismaService } from "../prisma/prisma.service";
import { SkipTenantCheck } from "../auth/tenant.guard";

@ApiTags("health")
@Controller()
@SkipThrottle()
@SkipTenantCheck()
@SetMetadata("isPublic", true)
export class HealthController {
  constructor(private readonly prisma: PrismaService) {}

  @Get("healthz")
  @ApiOperation({ summary: "Liveness probe | فحص الحياة" })
  @ApiResponse({ status: 200, description: "Service is alive" })
  healthCheck() {
    return {
      status: "ok",
      service: "disaster-assessment",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }

  @Get("readyz")
  @ApiOperation({ summary: "Readiness probe | فحص الجاهزية" })
  @ApiResponse({ status: 200, description: "Service is ready" })
  async readinessCheck() {
    let dbConnected = false;

    try {
      await this.prisma.$queryRaw`SELECT 1`;
      dbConnected = true;
    } catch {
      dbConnected = false;
    }

    return {
      status: dbConnected ? "ready" : "not_ready",
      service: "disaster-assessment",
      version: "16.0.0",
      checks: {
        database: dbConnected ? "connected" : "disconnected",
      },
      timestamp: new Date().toISOString(),
    };
  }
}
