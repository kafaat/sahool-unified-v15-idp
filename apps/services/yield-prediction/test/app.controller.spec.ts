import { HttpStatus } from "@nestjs/common";
import { AppController } from "../src/app.controller";

describe("AppController", () => {
  const originalDatabaseUrl = process.env.DATABASE_URL;

  afterEach(() => {
    if (originalDatabaseUrl === undefined) {
      delete process.env.DATABASE_URL;
    } else {
      process.env.DATABASE_URL = originalDatabaseUrl;
    }
  });

  it("returns liveness metadata without checking dependencies", () => {
    const controller = new AppController();

    expect(controller.healthz()).toEqual({
      status: "ok",
      service: "yield-prediction",
      version: "16.0.0",
    });
  });

  it("reports ready when no database dependency is configured", () => {
    delete process.env.DATABASE_URL;
    const controller = new AppController();

    expect(controller.readyz()).toMatchObject({
      status: "ready",
      service: "yield-prediction",
      database: true,
      checks: { database: "not_configured" },
    });
  });

  it("returns HTTP 503 when database is configured but not verified", () => {
    process.env.DATABASE_URL = "postgresql://example.invalid/sahool";
    const status = jest.fn();
    const controller = new AppController();

    const result = controller.readyz({ status } as any);

    expect(status).toHaveBeenCalledWith(HttpStatus.SERVICE_UNAVAILABLE);
    expect(result).toMatchObject({
      status: "not_ready",
      database: false,
      checks: { database: "configured_but_not_verified" },
    });
  });
});
