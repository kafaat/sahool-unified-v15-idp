/**
 * Health Check & Metrics Controller
 * متحكم فحص الصحة ومقاييس Prometheus
 *
 * Provides Kubernetes-compatible health check endpoints:
 * - /health - Basic health check
 * - /healthz - Liveness probe (alias)
 * - /readyz - Readiness probe with dependency checks
 * - /metrics - Prometheus metrics
 */

import {
  Controller,
  Get,
  HttpStatus,
  HttpException,
  Inject,
  Optional,
  Header,
  Logger,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse } from "@nestjs/swagger";
import { Throttle } from "@nestjs/throttler";
import { PrismaService } from "../prisma/prisma.service";
import { RedisTokenRevocationStore } from "../utils/token-revocation";
import * as promClient from "prom-client";

// ─── Prometheus registry & default metrics ───────────────────────────────────

const register = new promClient.Registry();

register.setDefaultLabels({ service: "user-service", version: "16.0.0" });
promClient.collectDefaultMetrics({ register });

// Custom metrics
export const httpRequestDuration = new promClient.Histogram({
  name: "http_request_duration_seconds",
  help: "Duration of HTTP requests in seconds",
  labelNames: ["method", "route", "status_code"] as const,
  buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
  registers: [register],
});

export const httpRequestsTotal = new promClient.Counter({
  name: "http_requests_total",
  help: "Total number of HTTP requests",
  labelNames: ["method", "route", "status_code"] as const,
  registers: [register],
});

export const activeConnections = new promClient.Gauge({
  name: "active_connections",
  help: "Number of active connections",
  registers: [register],
});

export const dbHealthGauge = new promClient.Gauge({
  name: "dependency_health",
  help: "Health status of dependencies (1 = healthy, 0 = unhealthy)",
  labelNames: ["dependency"] as const,
  registers: [register],
});

export const metricsRegistry = register;

// ─── Types ───────────────────────────────────────────────────────────────────

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

// ─── Shared health-check logic ───────────────────────────────────────────────

class HealthChecker {
  private static readonly logger = new Logger("HealthChecker");

  static async checkDatabase(
    prisma: PrismaService,
  ): Promise<"connected" | "disconnected"> {
    try {
      const result = await prisma.getConnectionStatus();
      const status = result.connected ? "connected" : "disconnected";
      dbHealthGauge.set({ dependency: "database" }, status === "connected" ? 1 : 0);
      return status;
    } catch {
      dbHealthGauge.set({ dependency: "database" }, 0);
      return "disconnected";
    }
  }

  static async checkRedis(
    redisStore?: RedisTokenRevocationStore,
  ): Promise<"connected" | "disconnected"> {
    try {
      if (!redisStore) {
        dbHealthGauge.set({ dependency: "redis" }, 0);
        return "disconnected";
      }
      const isHealthy = await redisStore.healthCheck();
      const status = isHealthy ? "connected" : "disconnected";
      dbHealthGauge.set({ dependency: "redis" }, status === "connected" ? 1 : 0);
      return status;
    } catch {
      dbHealthGauge.set({ dependency: "redis" }, 0);
      return "disconnected";
    }
  }

  static buildReadinessResponse(
    dbStatus: "connected" | "disconnected",
    redisStatus: "connected" | "disconnected",
    startTime: number,
  ): HealthResponse {
    const isReady = dbStatus === "connected";
    const status: HealthResponse["status"] = isReady
      ? redisStatus === "connected"
        ? "healthy"
        : "degraded"
      : "unhealthy";

    return {
      success: isReady,
      service: "user-service",
      version: "16.0.0",
      status,
      timestamp: new Date().toISOString(),
      uptime: Math.floor((Date.now() - startTime) / 1000),
      dependencies: {
        database: dbStatus,
        redis: redisStatus,
      },
    };
  }
}

// ─── /health/* controller (behind api/v1 prefix) ────────────────────────────

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
   * Liveness probe - GET /api/v1/health/live
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
   * Readiness probe - GET /api/v1/health/ready
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
    const dbStatus = await HealthChecker.checkDatabase(this.prisma);
    const redisStatus = await HealthChecker.checkRedis(this.redisStore);
    const response = HealthChecker.buildReadinessResponse(
      dbStatus,
      redisStatus,
      this.startTime,
    );

    if (!response.success) {
      throw new HttpException(response, HttpStatus.SERVICE_UNAVAILABLE);
    }

    return response;
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
   * Kubernetes liveness probe - GET /healthz
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
   * Kubernetes readiness probe - GET /readyz
   * Checks Prisma (database) and Redis connectivity
   * يفحص اتصال قاعدة البيانات و Redis
   */
  @Get("readyz")
  @Throttle({ default: { ttl: 60000, limit: 30 } })
  @ApiOperation({
    summary: "Kubernetes readiness probe",
    description: "فحص جاهزية Kubernetes مع فحص التبعيات",
  })
  async readyz(): Promise<HealthResponse> {
    const dbStatus = await HealthChecker.checkDatabase(this.prisma);
    const redisStatus = await HealthChecker.checkRedis(this.redisStore);
    const response = HealthChecker.buildReadinessResponse(
      dbStatus,
      redisStatus,
      this.startTime,
    );

    if (!response.success) {
      throw new HttpException(response, HttpStatus.SERVICE_UNAVAILABLE);
    }

    return response;
  }

  /**
   * Prometheus metrics endpoint - GET /metrics
   * نقطة نهاية مقاييس Prometheus
   */
  @Get("metrics")
  @ApiOperation({
    summary: "Prometheus metrics",
    description: "مقاييس Prometheus لمراقبة الخدمة",
  })
  @ApiResponse({ status: 200, description: "Prometheus metrics" })
  @Header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
  async metrics(): Promise<string> {
    return register.metrics();
  }
}
