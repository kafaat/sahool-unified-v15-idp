import { Test, TestingModule } from "@nestjs/testing";
import { HealthController } from "../health/health.controller";

describe("HealthController", () => {
  let controller: HealthController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [HealthController],
    }).compile();

    controller = module.get<HealthController>(HealthController);
  });

  it("should be defined", () => {
    expect(controller).toBeDefined();
  });

  it("should return health status", () => {
    const result = controller.healthCheck();
    expect(result).toHaveProperty("status", "ok");
    expect(result).toHaveProperty("service", "lai-estimation");
    expect(result).toHaveProperty("version", "16.0.0");
    expect(result).toHaveProperty("timestamp");
  });

  it("should return readiness status", () => {
    const result = controller.readinessCheck();
    expect(result).toHaveProperty("status", "ok");
    expect(result).toHaveProperty("service", "lai-estimation");
    expect(result).toHaveProperty("version", "16.0.0");
    expect(result).toHaveProperty("timestamp");
  });
});
