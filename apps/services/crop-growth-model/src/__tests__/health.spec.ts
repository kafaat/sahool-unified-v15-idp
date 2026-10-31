import { Test, TestingModule } from "@nestjs/testing";
import type { Response } from "express";
import { HealthController } from "../health/health.controller";

describe("HealthController", () => {
  let controller: HealthController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [HealthController],
    }).compile();

    controller = module.get<HealthController>(HealthController);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("should be defined", () => {
    expect(controller).toBeDefined();
  });

  it("should return health status", () => {
    const result = controller.healthCheck();
    expect(result).toHaveProperty("status", "ok");
    expect(result).toHaveProperty("service", "crop-growth-model");
    expect(result).toHaveProperty("version", "16.0.0");
    expect(result).toHaveProperty("timestamp");
  });

  it.each([
    { heapPercent: 80, httpStatus: 200, status: "ready", memory: "ok" },
    { heapPercent: 95, httpStatus: 503, status: "degraded", memory: "pressure" },
  ])("responds with $httpStatus when memory is $memory", ({ heapPercent, httpStatus, status, memory }) => {
    jest.spyOn(process, "memoryUsage").mockReturnValue({
      rss: 128 * 1024 * 1024,
      heapTotal: 100 * 1024 * 1024,
      heapUsed: heapPercent * 1024 * 1024,
      external: 0,
      arrayBuffers: 0,
    });
    const response = { status: jest.fn().mockReturnThis(), json: jest.fn() };

    controller.readinessCheck(response as unknown as Response);

    expect(response.status).toHaveBeenCalledWith(httpStatus);
    expect(response.json).toHaveBeenCalledWith(expect.objectContaining({
      status,
      service: "crop-growth-model",
      version: "16.0.0",
      timestamp: expect.any(String),
      checks: { memory, event_loop: "ok" },
      memory: expect.objectContaining({ heap_percent: heapPercent }),
    }));
  });
});
