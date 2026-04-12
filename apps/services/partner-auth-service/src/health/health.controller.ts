/**
 * Health endpoints for K8s liveness/readiness + Prometheus scrape.
 * /healthz  → liveness (process alive)
 * /readyz   → readiness (DB reachable)
 * /health   → combined status (for curl/humans)
 */

import { Controller, Get } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";

const SERVICE_NAME = "partner-auth-service";
const SERVICE_VERSION = "16.0.0";

@Controller()
export class HealthzController {
  constructor(private readonly prisma: PrismaService) {}

  @Get("healthz")
  liveness() {
    return { status: "ok", service: SERVICE_NAME, version: SERVICE_VERSION };
  }

  @Get("readyz")
  async readiness() {
    let dbOk = false;
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      dbOk = true;
    } catch {
      dbOk = false;
    }
    return {
      status: dbOk ? "ok" : "not_ready",
      service: SERVICE_NAME,
      version: SERVICE_VERSION,
      database: dbOk,
    };
  }
}

@Controller("health")
export class HealthController {
  constructor(private readonly prisma: PrismaService) {}

  @Get()
  async health() {
    let dbOk = false;
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      dbOk = true;
    } catch {
      dbOk = false;
    }
    return {
      status: dbOk ? "ok" : "degraded",
      service: SERVICE_NAME,
      version: SERVICE_VERSION,
      database: dbOk,
      timestamp: new Date().toISOString(),
    };
  }
}
