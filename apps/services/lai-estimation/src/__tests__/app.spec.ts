import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";

// Set JWT_SECRET_KEY for AuthModule.forRoot() validation
process.env.JWT_SECRET_KEY = "test-secret-key-for-unit-tests-only-32chars";

import { AppModule } from "../app.module";

describe("LAIEstimation (AppModule)", () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    if (app) {
      await app.close();
    }
  });

  it("should be defined", () => {
    expect(app).toBeDefined();
  });
});
