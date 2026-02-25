import { Test, TestingModule } from "@nestjs/testing";
import { YieldController } from "../yield/yield.controller";
import { YieldService } from "../yield/yield.service";

describe("YieldController (Health)", () => {
  let controller: YieldController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [YieldController],
      providers: [YieldService],
    }).compile();

    controller = module.get<YieldController>(YieldController);
  });

  it("should be defined", () => {
    expect(controller).toBeDefined();
  });

  it("should return health status", () => {
    const result = controller.healthCheck();
    expect(result).toHaveProperty("status", "ok");
    expect(result).toHaveProperty("service", "yield-prediction");
    expect(result).toHaveProperty("timestamp");
  });
});
