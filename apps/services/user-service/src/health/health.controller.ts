/**
 * Health Check Controller
 * متحكم فحص الصحة
 *
 * Provides Kubernetes-compatible health check endpoints:
 * - /health - Basic health check
 * - /healthz - Liveness probe (alias)
 * - /readyz - Readiness probe with dependency checks
 */

import {
  Controller,
  Get,
  HttpStatus,
  HttpException,
  Inject,
  Optional,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import { Throttle } from "@nestjs/throttler";
import { PrismaService } from "../prisma/prisma.service";
import { RedisTokenRevocationStore } from "../utils/token-revocation";

interface HealthResponse {
  success: boolean;
  service: string;
  version: string;
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  uptime?: number;
  dependencies?: {
    database: "connected" | "disconnected";
    redis: "connected" | "disconnected";
  };
}

@ApiTags("Health")
@Controller("health")
export class HealthController {
  private readonly startTime = Date.now();

  constructor(
    private readonly prisma: PrismaService,
    @Optional()
    @Inject(RedisTokenRevocationStore)
    private readonly redisStore?: RedisTokenRevocationStore,
  ) {}

  /**
   * Basic health check - GET /api/v1/health
   * فحص صحة أساسي
   */
  @Get()
  @Throttle({ default: { ttl: 60000, limit: 10 } })
  @ApiOperation({
    summary: "Health check endpoint",
    description: "نقطة فحص صحة الخدمة",
  })
  @ApiResponse({
    status: 200,
    description: "Service is healthy",
  })
  check(): HealthResponse {
    return {
      success: true,
      service: "user-service",
      version: "16.0.0",
      status: "healthy",
      timestamp: new Date().toISOString(),
      uptime: Math.floor((Date.now() - this.startTime) / 1000),
    };
  }

  /**
   * Liveness probe - GET /api/v1/health/live or /api/v1/healthz
   * فحص حيوية الخدمة - للتأكد من أن الخدمة تعمل
   */
  @Get("live")
  @Throttle({ default: { ttl: 60000, limit: 30 } })
  @ApiOperation({
    summary: "Liveness probe",
    description: "فحص حيوية الخدمة - Kubernetes liveness probe",
  })
  @ApiResponse({ status: 200, description: "Service is alive" })
  liveness(): HealthResponse {
    return {
      success: true,
      service: "user-service",
      version: "16.0.0",
      status: "healthy",
      timestamp: new Date().toISOString(),
      uptime: Math.floor((Date.now() - this.startTime) / 1000),
    };
  }

  /**
   * Readiness probe - GET /api/v1/health/ready or /api/v1/readyz
   * فحص جاهزية الخدمة - للتأكد من أن الخدمة جاهزة لاستقبال الطلبات
   */
  @Get("ready")
  @Throttle({ default: { ttl: 60000, limit: 30 } })
  @ApiOperation({
    summary: "Readiness probe",
    description:
      "فحص جاهزية الخدمة مع فحص التبعيات - Kubernetes readiness probe",
  })
  @ApiResponse({ status: 200, description: "Service is ready" })
  @ApiResponse({ status: 503, description: "Service not ready" })
  async readiness(): Promise<HealthResponse> {
    const dbStatus = await this.checkDatabase();
    const redisStatus = await this.checkRedis();

    const isReady = dbStatus === "connected";
    const status = isReady
      ? redisStatus === "connected"
        ? "healthy"
        : "degraded"
      : "unhealthy";

    const response: HealthResponse = {
      success: isReady,
      service: "user-service",
      version: "16.0.0",
      status,
      timestamp: new Date().toISOString(),
      uptime: Math.floor((Date.now() - this.startTime) / 1000),
      dependencies: {
        database: dbStatus,
        redis: redisStatus,
      },
    };

    if (!isReady) {
      throw new HttpException(response, HttpStatus.SERVICE_UNAVAILABLE);
    }

    return response;
  }

  /**
   * Check database connectivity
   * فحص اتصال قاعدة البيانات
   */
  private async checkDatabase(): Promise<"connected" | "disconnected"> {
    try {
      const result = await this.prisma.getConnectionStatus();
      return result.connected ? "connected" : "disconnected";
    } catch {
      return "disconnected";
    }
  }

  /**
   * Check Redis connectivity
   * فحص اتصال Redis
   */
  private async checkRedis(): Promise<"connected" | "disconnected"> {
    try {
      if (!this.redisStore) {
        return "disconnected";
      }
      const isHealthy = await this.redisStore.healthCheck();
      return isHealthy ? "connected" : "disconnected";
    } catch {
      return "disconnected";
    }
  }
}

/**
 * Separate controller for root-level Kubernetes endpoints
 * متحكم منفصل لنقاط نهاية Kubernetes على المستوى الجذري
 */
@ApiTags("Health")
@Controller()
export class HealthzController {
  private readonly startTime = Date.now();

  constructor(
    private readonly prisma: PrismaService,
    @Optional()
    @Inject(RedisTokenRevocationStore)
    private readonly redisStore?: RedisTokenRevocationStore,
  ) {}

  /**
   * Kubernetes liveness probe - GET /api/v1/healthz
   */
  @Get("healthz")
  @Throttle({ default: { ttl: 60000, limit: 30 } })
  @ApiOperation({
    summary: "Kubernetes liveness probe",
    description: "فحص حيوية Kubernetes",
  })
  healthz(): HealthResponse {
    return {
      success: true,
      service: "user-service",
      version: "16.0.0",
      status: "healthy",
      timestamp: new Date().toISOString(),
      uptime: Math.floor((Date.now() - this.startTime) / 1000),
    };
  }

  /**
   * Kubernetes readiness probe - GET /api/v1/readyz
   */
  @Get("readyz")
  @Throttle({ default: { ttl: 60000, limit: 30 } })
  @ApiOperation({
    summary: "Kubernetes readiness probe",
    description: "فحص جاهزية Kubernetes مع فحص التبعيات",
  })
  async readyz(): Promise<HealthResponse> {
    const dbStatus = await this.checkDatabase();
    const redisStatus = await this.checkRedis();

    const isReady = dbStatus === "connected";
    const status = isReady
      ? redisStatus === "connected"
        ? "healthy"
        : "degraded"
      : "unhealthy";

    const response: HealthResponse = {
      success: isReady,
      service: "user-service",
      version: "16.0.0",
      status,
      timestamp: new Date().toISOString(),
      uptime: Math.floor((Date.now() - this.startTime) / 1000),
      dependencies: {
        database: dbStatus,
        redis: redisStatus,
      },
    };

    if (!isReady) {
      throw new HttpException(response, HttpStatus.SERVICE_UNAVAILABLE);
    }

    return response;
  }

  private async checkDatabase(): Promise<"connected" | "disconnected"> {
    try {
      const result = await this.prisma.getConnectionStatus();
      return result.connected ? "connected" : "disconnected";
    } catch {
      return "disconnected";
    }
  }

  private async checkRedis(): Promise<"connected" | "disconnected"> {
    try {
      if (!this.redisStore) {
        return "disconnected";
      }
      const isHealthy = await this.redisStore.healthCheck();
      return isHealthy ? "connected" : "disconnected";
    } catch {
      return "disconnected";
    }
  }
}
