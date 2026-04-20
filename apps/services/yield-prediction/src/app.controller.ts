import { Controller, Get } from "@nestjs/common";
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
  readyz() {
    const dbUrl = process.env.DATABASE_URL;
    const databaseReady = dbUrl ? false : true; // No DB configured = no DB dependency; DB configured = not verified
    const status = databaseReady ? "ok" : "degraded";

    return {
      status,
      service: "yield-prediction",
      version: "16.0.0",
      database: databaseReady,
      checks: {
        database: dbUrl ? "configured_but_not_verified" : "not_configured",
      },
    };
  }
}
