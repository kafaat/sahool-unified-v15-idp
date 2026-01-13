/**
 * Health Controller for Chat Service
 * نقاط فحص صحة الخدمة
 */

import { Controller, Get } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import { PrismaService } from "../prisma/prisma.service";

@ApiTags("Health")
@Controller()
export class HealthController {
  private readonly startTime: Date;

  constructor(private readonly prisma: PrismaService) {
    this.startTime = new Date();
  }

  @Get("health")
  @ApiOperation({ summary: "Health check endpoint" })
  @ApiResponse({ status: 200, description: "Service is healthy" })
  async health() {
    // Check database connection
    let databaseHealthy = false;
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      databaseHealthy = true;
    } catch (error) {
      console.error("Database health check failed:", error);
    }

    return {
      status: "healthy",
      service: "chat-service",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
      uptime: this.getUptime(),
      dependencies: {
        database: databaseHealthy ? "connected" : "disconnected",
      },
    };
  }

  @Get("healthz")
  @ApiOperation({ summary: "Kubernetes health check" })
  @ApiResponse({ status: 200, description: "Service is healthy" })
  healthz() {
    return {
      status: "ok",
      service: "chat-service",
      timestamp: new Date().toISOString(),
      uptime: this.getUptime(),
    };
  }

  @Get("readyz")
  @ApiOperation({ summary: "Kubernetes readiness check" })
  @ApiResponse({ status: 200, description: "Service is ready" })
  async readyz() {
    // Check if service is ready to accept traffic
    let ready = true;

    try {
      await this.prisma.$queryRaw`SELECT 1`;
    } catch (error) {
      ready = false;
    }

    return {
      status: ready ? "ready" : "not_ready",
      service: "chat-service",
      timestamp: new Date().toISOString(),
      database: ready,
    };
  }

  @Get("livez")
  @ApiOperation({ summary: "Liveness check endpoint" })
  @ApiResponse({ status: 200, description: "Service is alive" })
  livenessCheck() {
    return {
      status: "alive",
      service: "chat-service",
      timestamp: new Date().toISOString(),
      uptime: this.getUptime(),
    };
  }

  private getUptime(): string {
    const uptime = Date.now() - this.startTime.getTime();
    const seconds = Math.floor(uptime / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  }
}
