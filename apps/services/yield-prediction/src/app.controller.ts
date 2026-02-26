import { Controller, Get } from "@nestjs/common";

@Controller()
export class AppController {
  @Get("healthz")
  healthz() {
    return {
      status: "ok",
      service: "yield-prediction",
      version: "16.0.0",
    };
  }

  @Get("readyz")
  readyz() {
    return {
      status: "ok",
      service: "yield-prediction",
      version: "16.0.0",
      database: true,
    };
  }
}
