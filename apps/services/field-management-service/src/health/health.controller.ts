/**
 * Health Controller - Health Check Endpoints
 *
 * Provides:
 * - /healthz - Liveness probe
 * - /readyz - Readiness probe
 * - /health - Detailed health status
 */

import { Controller, Get, HttpStatus, Res } from "@nestjs/common";
import { Response } from "express";
import { Throttle, SkipThrottle } from "@nestjs/throttler";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import { Public } from "../auth/public.decorator";
import { PrismaService } from "../prisma/prisma.service";
import { CacheService } from "../cache/cache.service";
import { SkipTenantCheck } from "../auth/tenant.guard";

@ApiTags("Health - الصحة")
@SkipTenantCheck()
@Controller()
export class HealthController {
  constructor(
    private prisma: PrismaService,
    private cacheService: CacheService,
  ) {}

  /**
   * Liveness probe - is the service running?
   */
  @Get("healthz")
  @Public()
  @SkipThrottle()
  @ApiOperation({ summary: "Liveness probe" })
  @ApiResponse({ status: 200, description: "Service is alive" })
  healthz() {
    return {
      status: "healthy",
      service: "field-management-service",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Readiness probe - is the service ready to accept traffic?
   */
  @Get("readyz")
  @Public()
  @SkipThrottle()
  @ApiOperation({ summary: "Readiness probe" })
  @ApiResponse({ status: 200, description: "Service is ready" })
  @ApiResponse({ status: 503, description: "Service not ready" })
  async readyz(@Res() res: Response) {
    const checks = {
      database: false,
      cache: false,
    };

    try {
      // Check database
      const dbStatus = await this.prisma.getConnectionStatus();
      checks.database = dbStatus.connected;
    } catch {
      checks.database = false;
    }

    try {
      // Check cache
      checks.cache = await this.cacheService.isHealthy();
    } catch {
      checks.cache = false;
    }

    const isReady = checks.database; // Database is required

    const status = isReady ? HttpStatus.OK : HttpStatus.SERVICE_UNAVAILABLE;

    return res.status(status).json({
      status: isReady ? "ready" : "not ready",
      checks,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Detailed health status
   */
  @Get("health")
  @Public()
  @Throttle({ default: { limit: 10, ttl: 60000 } })
  @ApiOperation({ summary: "Detailed health status" })
  @ApiResponse({ status: 200, description: "Health status retrieved" })
  async health() {
    const checks: Record<string, any> = {};

    // Database check
    try {
      const dbStatus = await this.prisma.getConnectionStatus();
      checks.database = {
        status: dbStatus.connected ? "healthy" : "unhealthy",
        latency: null, // Could add latency measurement
        details: dbStatus,
      };
    } catch (error) {
      checks.database = {
        status: "unhealthy",
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }

    // Cache check
    try {
      const cacheHealthy = await this.cacheService.isHealthy();
      checks.cache = {
        status: cacheHealthy ? "healthy" : "unhealthy",
      };
    } catch (error) {
      checks.cache = {
        status: "unhealthy",
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }

    // Memory check
    const memUsage = process.memoryUsage();
    checks.memory = {
      status: "healthy",
      heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024) + " MB",
      heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024) + " MB",
      rss: Math.round(memUsage.rss / 1024 / 1024) + " MB",
    };

    // Uptime
    checks.uptime = {
      seconds: Math.floor(process.uptime()),
      human: this.formatUptime(process.uptime()),
    };

    const allHealthy = Object.values(checks).every(
      (check) => (check as any).status === "healthy",
    );

    return {
      status: allHealthy ? "healthy" : "degraded",
      service: "field-management-service",
      version: "16.0.0",
      checks,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Prometheus metrics endpoint
   */
  @Get("metrics")
  @Public()
  @SkipThrottle()
  @ApiOperation({ summary: "Prometheus metrics" })
  async metrics(@Res() res: Response) {
    const memUsage = process.memoryUsage();

    const metrics = `
# HELP nodejs_heap_size_used_bytes Process heap size used in bytes
# TYPE nodejs_heap_size_used_bytes gauge
nodejs_heap_size_used_bytes ${memUsage.heapUsed}

# HELP nodejs_heap_size_total_bytes Process heap size total in bytes
# TYPE nodejs_heap_size_total_bytes gauge
nodejs_heap_size_total_bytes ${memUsage.heapTotal}

# HELP process_uptime_seconds Process uptime in seconds
# TYPE process_uptime_seconds counter
process_uptime_seconds ${Math.floor(process.uptime())}

# HELP service_info Service information
# TYPE service_info gauge
service_info{service="field-management-service",version="16.0.0"} 1
`.trim();

    res.set("Content-Type", "text/plain; charset=utf-8").send(metrics);
  }

  private formatUptime(seconds: number): string {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    const parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);

    return parts.join(" ") || "< 1m";
  }
}
