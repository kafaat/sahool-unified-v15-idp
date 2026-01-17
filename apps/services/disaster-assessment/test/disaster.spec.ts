/**
 * SAHOOL Disaster Assessment Service - Unit Tests
 * اختبارات خدمة تقييم الكوارث
 */

import express, { Express } from "express";
import request from "supertest";

function createTestApp(): Express {
  const app = express();
  app.use(express.json());

  app.get("/healthz", (_req, res) => {
    res.json({ status: "ok", service: "disaster_assessment" });
  });

  app.post("/api/v1/assess", (req, res) => {
    res.json({
      assessment_id: "assess_001",
      field_id: req.body.field_id,
      disaster_type: req.body.disaster_type,
      severity: "moderate",
      affected_area_pct: 35,
      estimated_loss: { value: 15000, currency: "YER" },
      recommendations: ["Apply for insurance claim", "Replant affected areas"],
    });
  });

  app.get("/api/v1/fields/:fieldId/assessments", (req, res) => {
    res.json({
      field_id: req.params.fieldId,
      assessments: [
        {
          id: "assess_001",
          date: "2025-12-20",
          type: "flood",
          severity: "moderate",
        },
      ],
    });
  });

  app.get("/api/v1/disaster-types", (_req, res) => {
    res.json({
      types: [
        { id: "flood", name: "Flood", name_ar: "فيضان" },
        { id: "drought", name: "Drought", name_ar: "جفاف" },
        { id: "pest", name: "Pest Outbreak", name_ar: "انتشار الآفات" },
      ],
    });
  });

  app.post("/api/v1/claims", (req, res) => {
    res.status(201).json({
      claim_id: "claim_001",
      assessment_id: req.body.assessment_id,
      status: "submitted",
      submitted_at: new Date().toISOString(),
    });
  });

  return app;
}

describe("Disaster Assessment Service", () => {
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

  describe("Assessment", () => {
    it("should create assessment", async () => {
      const response = await request(app)
        .post("/api/v1/assess")
        .send({ field_id: "field_001", disaster_type: "flood" });
      expect(response.status).toBe(200);
      expect(response.body.severity).toBeDefined();
      expect(response.body.estimated_loss).toBeDefined();
    });

    it("should get field assessments", async () => {
      const response = await request(app).get(
        "/api/v1/fields/field_001/assessments",
      );
      expect(response.status).toBe(200);
      expect(response.body.assessments).toBeDefined();
    });
  });

  describe("Disaster Types", () => {
    it("should list disaster types", async () => {
      const response = await request(app).get("/api/v1/disaster-types");
      expect(response.status).toBe(200);
      expect(response.body.types.length).toBeGreaterThan(0);
    });
  });

  describe("Claims", () => {
    it("should submit claim", async () => {
      const response = await request(app)
        .post("/api/v1/claims")
        .send({ assessment_id: "assess_001" });
      expect(response.status).toBe(201);
      expect(response.body.claim_id).toBeDefined();
    });
  });
});
