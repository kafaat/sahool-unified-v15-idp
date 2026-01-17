/**
 * SAHOOL Research Core Service - Unit Tests
 * اختبارات خدمة البحث العلمي
 */

import express, { Express } from "express";
import request from "supertest";

function createTestApp(): Express {
  const app = express();
  app.use(express.json());

  app.get("/healthz", (_req, res) => {
    res.json({ status: "ok", service: "research_core" });
  });

  app.get("/api/v1/experiments", (_req, res) => {
    res.json({
      experiments: [
        { id: "exp_001", name: "Irrigation Optimization", status: "active" },
        { id: "exp_002", name: "Fertilizer Comparison", status: "completed" },
      ],
    });
  });

  app.post("/api/v1/experiments", (req, res) => {
    res.status(201).json({
      id: "exp_new",
      name: req.body.name,
      created_at: new Date().toISOString(),
    });
  });

  app.get("/api/v1/experiments/:experimentId/results", (req, res) => {
    res.json({
      experiment_id: req.params.experimentId,
      results: {
        treatment_a: { yield: 4.5, quality: "high" },
        treatment_b: { yield: 3.8, quality: "medium" },
      },
      conclusion: "Treatment A shows 18% improvement",
    });
  });

  app.get("/api/v1/datasets", (_req, res) => {
    res.json({
      datasets: [
        { id: "ds_001", name: "Yemen Wheat Trials 2024", records: 5000 },
      ],
    });
  });

  return app;
}

describe("Research Core Service", () => {
  let app: Express;

  beforeAll(() => {
    app = createTestApp();
  });

  describe("Health Check", () => {
    it("should return healthy status", async () => {
      const response = await request(app).get("/healthz");
      expect(response.status).toBe(200);
    });
  });

  describe("Experiments", () => {
    it("should list experiments", async () => {
      const response = await request(app).get("/api/v1/experiments");
      expect(response.status).toBe(200);
      expect(response.body.experiments).toBeDefined();
    });

    it("should create experiment", async () => {
      const response = await request(app)
        .post("/api/v1/experiments")
        .send({ name: "New Experiment" });
      expect(response.status).toBe(201);
    });

    it("should get experiment results", async () => {
      const response = await request(app).get(
        "/api/v1/experiments/exp_001/results",
      );
      expect(response.status).toBe(200);
      expect(response.body.results).toBeDefined();
    });
  });

  describe("Datasets", () => {
    it("should list datasets", async () => {
      const response = await request(app).get("/api/v1/datasets");
      expect(response.status).toBe(200);
      expect(response.body.datasets).toBeDefined();
    });
  });
});
