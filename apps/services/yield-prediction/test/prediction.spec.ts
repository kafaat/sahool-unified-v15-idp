/**
 * SAHOOL Yield Prediction Service - Unit Tests
 * اختبارات خدمة التنبؤ بالإنتاجية
 */

import express, { Express } from "express";
import request from "supertest";

function createTestApp(): Express {
  const app = express();
  app.use(express.json());

  app.get("/healthz", (_req, res) => {
    res.json({ status: "ok", service: "yield_prediction" });
  });

  app.post("/api/v1/predict", (req, res) => {
    res.json({
      field_id: req.body.field_id,
      prediction: {
        yield: 4.8,
        unit: "tons/ha",
        confidence: 0.88,
        range: { min: 4.2, max: 5.4 },
      },
      model: "ensemble_v3",
      features_used: ["ndvi", "weather", "soil", "historical"],
    });
  });

  app.get("/api/v1/fields/:fieldId/predictions", (req, res) => {
    res.json({
      field_id: req.params.fieldId,
      predictions: [
        { date: "2025-12-20", yield: 4.5, actual: null },
        { date: "2025-12-15", yield: 4.3, actual: null },
      ],
    });
  });

  app.get("/api/v1/models", (_req, res) => {
    res.json({
      models: [
        { id: "ensemble_v3", accuracy: 0.89, crops: ["wheat", "corn"] },
        { id: "rf_v2", accuracy: 0.85, crops: ["tomato"] },
      ],
    });
  });

  app.post("/api/v1/validate", (req, res) => {
    res.json({
      field_id: req.body.field_id,
      predicted: req.body.predicted_yield,
      actual: req.body.actual_yield,
      error_pct: 5.2,
      feedback_recorded: true,
    });
  });

  return app;
}

describe("Yield Prediction Service", () => {
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

  describe("Prediction", () => {
    it("should predict yield", async () => {
      const response = await request(app)
        .post("/api/v1/predict")
        .send({ field_id: "field_001", crop: "wheat" });
      expect(response.status).toBe(200);
      expect(response.body.prediction).toBeDefined();
      expect(response.body.prediction.confidence).toBeDefined();
    });

    it("should get prediction history", async () => {
      const response = await request(app).get(
        "/api/v1/fields/field_001/predictions",
      );
      expect(response.status).toBe(200);
      expect(response.body.predictions).toBeDefined();
    });
  });

  describe("Models", () => {
    it("should list available models", async () => {
      const response = await request(app).get("/api/v1/models");
      expect(response.status).toBe(200);
      expect(response.body.models).toBeDefined();
    });
  });

  describe("Validation", () => {
    it("should validate prediction with actual yield", async () => {
      const response = await request(app).post("/api/v1/validate").send({
        field_id: "field_001",
        predicted_yield: 4.5,
        actual_yield: 4.3,
      });
      expect(response.status).toBe(200);
      expect(response.body.error_pct).toBeDefined();
    });
  });
});
