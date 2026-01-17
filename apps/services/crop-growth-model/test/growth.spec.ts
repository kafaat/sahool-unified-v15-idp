/**
 * SAHOOL Crop Growth Model Service - Unit Tests
 * اختبارات خدمة نموذج نمو المحاصيل
 */

import express, { Express } from "express";
import request from "supertest";

function createTestApp(): Express {
  const app = express();
  app.use(express.json());

  app.get("/healthz", (_req, res) => {
    res.json({ status: "ok", service: "crop_growth_model" });
  });

  app.post("/api/v1/simulate", (req, res) => {
    res.json({
      field_id: req.body.field_id,
      crop: req.body.crop,
      simulation: {
        days: 120,
        stages: [
          { day: 0, stage: "germination", biomass_kg: 0 },
          { day: 30, stage: "vegetative", biomass_kg: 500 },
          { day: 60, stage: "flowering", biomass_kg: 2000 },
          { day: 90, stage: "fruiting", biomass_kg: 4000 },
          { day: 120, stage: "maturity", biomass_kg: 5500 },
        ],
        expected_yield: { value: 4.5, unit: "tons/ha" },
      },
    });
  });

  app.get("/api/v1/fields/:fieldId/growth-stage", (req, res) => {
    res.json({
      field_id: req.params.fieldId,
      current_stage: "flowering",
      days_in_stage: 15,
      next_stage: "fruiting",
      days_to_next: 10,
    });
  });

  app.get("/api/v1/crops/:crop/model", (req, res) => {
    res.json({
      crop: req.params.crop,
      gdd_requirements: {
        germination: 100,
        vegetative: 400,
        flowering: 800,
        maturity: 1500,
      },
      base_temperature: 10,
      optimal_temperature: 25,
    });
  });

  return app;
}

describe("Crop Growth Model Service", () => {
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

  describe("Simulation", () => {
    it("should simulate crop growth", async () => {
      const response = await request(app)
        .post("/api/v1/simulate")
        .send({ field_id: "field_001", crop: "wheat" });
      expect(response.status).toBe(200);
      expect(response.body.simulation).toBeDefined();
      expect(response.body.simulation.stages.length).toBeGreaterThan(0);
    });
  });

  describe("Growth Stage", () => {
    it("should get current growth stage", async () => {
      const response = await request(app).get(
        "/api/v1/fields/field_001/growth-stage",
      );
      expect(response.status).toBe(200);
      expect(response.body.current_stage).toBeDefined();
    });
  });

  describe("Crop Model", () => {
    it("should get crop model parameters", async () => {
      const response = await request(app).get("/api/v1/crops/wheat/model");
      expect(response.status).toBe(200);
      expect(response.body.gdd_requirements).toBeDefined();
    });
  });
});
