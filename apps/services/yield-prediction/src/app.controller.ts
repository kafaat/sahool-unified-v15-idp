import { Controller, Get, HttpStatus, Res } from "@nestjs/common";
import type { Response } from "express";
import { SkipTenantCheck } from "./auth/tenant.guard";

@Controller()
export class AppController {
  @Get("healthz")
  @SkipTenantCheck()
  healthz() {
    return {
      status: "ok",
      service: "yield-prediction",
      version: "16.0.0",
    };
  }

  @Get("readyz")
  @SkipTenantCheck()
  readyz(@Res({ passthrough: true }) res?: Response) {
    const hasDatabaseDependency = Boolean(process.env.DATABASE_URL);
    const databaseReady = !hasDatabaseDependency; // No DB configured = no DB dependency; configured DB is not verified here.
    if (hasDatabaseDependency) {
      res?.status(HttpStatus.SERVICE_UNAVAILABLE);
    }
    const status = databaseReady ? "ready" : "not_ready";

    return {
      status,
      service: "yield-prediction",
      version: "16.0.0",
      database: databaseReady,
      checks: {
        database: hasDatabaseDependency ? "configured_but_not_verified" : "not_configured",
      },
    };
  }
}
