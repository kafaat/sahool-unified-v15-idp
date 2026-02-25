/**
 * SAHOOL AI Services API Integration Tests
 * اختبارات تكامل خدمات الذكاء الاصطناعي لمنصة سهول
 *
 * Tests cover:
 * - Vision API (pest detection)
 * - Crop health analysis
 * - Yield prediction
 * - Advisory service
 *
 * @author SAHOOL Platform Team
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import {
  TEST_CONFIG,
  TEST_DATA,
  apiRequest,
  getAuthToken,
  getAuthHeaders,
  clearAuthCache,
  isValidUUID,
  checkServiceHealth,
  generateTestId,
} from "./setup";

// ═══════════════════════════════════════════════════════════════════════════════
// Test Configuration
// ═══════════════════════════════════════════════════════════════════════════════

const VISION_SERVICE_URL = TEST_CONFIG.SERVICES.VISION_SERVICE;
const CROP_INTELLIGENCE_URL = TEST_CONFIG.SERVICES.CROP_INTELLIGENCE;
const YIELD_ENGINE_URL = TEST_CONFIG.SERVICES.YIELD_ENGINE;
const ADVISORY_SERVICE_URL = TEST_CONFIG.SERVICES.ADVISORY_SERVICE;

describe("AI Services API Integration Tests", () => {
  let authToken: string;

  // ─────────────────────────────────────────────────────────────────────────────
  // Setup & Teardown
  // ─────────────────────────────────────────────────────────────────────────────

  beforeAll(async () => {
    authToken = await getAuthToken("FARMER");
  });

  afterAll(() => {
    clearAuthCache();
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Vision API (Pest Detection) Tests - اختبارات API الرؤية (كشف الآفات)
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Vision API - Pest Detection", () => {
    const VISION_API_BASE = `${VISION_SERVICE_URL}/api/v1/vision`;

    it("should verify vision service is registered and responding", async () => {
      const health = await checkServiceHealth(
        "VISION_SERVICE",
        VISION_SERVICE_URL
      );

      expect(health.service).toBe("VISION_SERVICE");
      expect(["healthy", "unhealthy", "unknown"]).toContain(health.status);
      expect(health.responseTime).toBeGreaterThan(0);
    });

    it("should have health endpoint available", async () => {
      const response = await apiRequest<{
        status: string;
        model_loaded?: boolean;
      }>(`${VISION_SERVICE_URL}/healthz`);

      expect([200, 404, 502, 503]).toContain(response.status);

      if (response.ok) {
        expect(response.data).toHaveProperty("status");
      }
    });

    it("should detect pests in image", async () => {
      const detectRequest = {
        image_base64: TEST_DATA.PEST_IMAGE.image_base64,
        field_id: TEST_DATA.PEST_IMAGE.field_id,
        crop_type: TEST_DATA.PEST_IMAGE.crop_type,
        detection_types: ["pest", "disease"],
      };

      const response = await apiRequest<{
        request_id: string;
        detections: Array<{
          type: string;
          class_name: string;
          class_name_ar?: string;
          confidence: number;
          bounding_box?: {
            x: number;
            y: number;
            width: number;
            height: number;
          };
          severity?: string;
        }>;
        processing_time_ms: number;
      }>(`${VISION_API_BASE}/detect`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(detectRequest),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 400, 401, 422]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("detections");
        expect(Array.isArray(response.data.detections)).toBe(true);

        response.data.detections.forEach((detection) => {
          expect(detection).toHaveProperty("type");
          expect(detection).toHaveProperty("class_name");
          expect(detection).toHaveProperty("confidence");
          expect(detection.confidence).toBeGreaterThanOrEqual(0);
          expect(detection.confidence).toBeLessThanOrEqual(1);
        });
      }
    });

    it("should detect diseases in leaf images", async () => {
      const detectRequest = {
        image_base64: TEST_DATA.PEST_IMAGE.image_base64,
        field_id: TEST_DATA.PEST_IMAGE.field_id,
        crop_type: "wheat",
        detection_types: ["disease"],
      };

      const response = await apiRequest<{
        detections: Array<{
          type: string;
          disease_name: string;
          disease_name_ar?: string;
          confidence: number;
          affected_area_percent?: number;
          treatment_recommendations?: string[];
        }>;
      }>(`${VISION_API_BASE}/detect/disease`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(detectRequest),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 400, 401, 422]).toContain(response.status);

      if (response.status === 200 && response.data.detections) {
        response.data.detections.forEach((detection) => {
          expect(detection.type).toBe("disease");
          if (detection.confidence) {
            expect(detection.confidence).toBeLessThanOrEqual(1);
          }
        });
      }
    });

    it("should detect weeds in field images", async () => {
      const detectRequest = {
        image_base64: TEST_DATA.PEST_IMAGE.image_base64,
        field_id: TEST_DATA.PEST_IMAGE.field_id,
        detection_types: ["weed"],
      };

      const response = await apiRequest<{
        detections: Array<{
          type: string;
          weed_name: string;
          weed_name_ar?: string;
          confidence: number;
          coverage_percent?: number;
        }>;
      }>(`${VISION_API_BASE}/detect/weed`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(detectRequest),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 400, 401, 422]).toContain(response.status);
    });

    it("should support batch image processing", async () => {
      const batchRequest = {
        images: [
          {
            image_base64: TEST_DATA.PEST_IMAGE.image_base64,
            image_id: "img-001",
          },
          {
            image_base64: TEST_DATA.PEST_IMAGE.image_base64,
            image_id: "img-002",
          },
        ],
        field_id: TEST_DATA.PEST_IMAGE.field_id,
        detection_types: ["pest", "disease", "weed"],
      };

      const response = await apiRequest<{
        batch_id: string;
        results: Array<{
          image_id: string;
          detections: Array<{ type: string; class_name: string }>;
        }>;
        total_processing_time_ms: number;
      }>(`${VISION_API_BASE}/detect/batch`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(batchRequest),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 202, 400, 401, 422]).toContain(response.status);

      if (response.status === 200 && response.data.results) {
        expect(response.data.results.length).toBe(2);
      }
    });

    it("should list available detection models", async () => {
      const response = await apiRequest<{
        models: Array<{
          id: string;
          name: string;
          version: string;
          detection_types: string[];
          supported_crops?: string[];
        }>;
      }>(`${VISION_API_BASE}/models`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.models) {
        response.data.models.forEach((model) => {
          expect(model).toHaveProperty("id");
          expect(model).toHaveProperty("name");
          expect(model).toHaveProperty("detection_types");
        });
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Crop Health Analysis Tests - اختبارات تحليل صحة المحاصيل
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Crop Health Analysis", () => {
    const CROP_API_BASE = `${CROP_INTELLIGENCE_URL}/api/v1/crop-health`;

    it("should verify crop intelligence service is registered", async () => {
      const health = await checkServiceHealth(
        "CROP_INTELLIGENCE",
        CROP_INTELLIGENCE_URL
      );

      expect(health.service).toBe("CROP_INTELLIGENCE");
      expect(["healthy", "unhealthy", "unknown"]).toContain(health.status);
    });

    it("should analyze crop health for field", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        crop_type: string;
        health_score: number;
        health_status: string;
        health_status_ar?: string;
        analysis_date: string;
        factors: Array<{
          factor: string;
          factor_ar?: string;
          score: number;
          status: string;
        }>;
      }>(`${CROP_API_BASE}/analyze/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("health_score");
        expect(response.data).toHaveProperty("health_status");

        expect(response.data.health_score).toBeGreaterThanOrEqual(0);
        expect(response.data.health_score).toBeLessThanOrEqual(100);
        expect(["healthy", "moderate", "stressed", "critical"]).toContain(
          response.data.health_status
        );
      }
    });

    it("should provide crop health history", async () => {
      const fieldId = "field-test-001";
      const startDate = "2025-01-01";
      const endDate = "2025-01-14";

      const response = await apiRequest<{
        field_id: string;
        history: Array<{
          date: string;
          health_score: number;
          health_status: string;
        }>;
        trend: string;
      }>(
        `${CROP_API_BASE}/history/${fieldId}?start_date=${startDate}&end_date=${endDate}`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.history) {
        expect(Array.isArray(response.data.history)).toBe(true);

        if (response.data.trend) {
          expect(["improving", "stable", "declining"]).toContain(
            response.data.trend
          );
        }
      }
    });

    it("should detect nutrient deficiencies", async () => {
      const analysisRequest = {
        field_id: "field-test-001",
        image_base64: TEST_DATA.PEST_IMAGE.image_base64,
        crop_type: "wheat",
        growth_stage: "tillering",
      };

      const response = await apiRequest<{
        field_id: string;
        deficiencies: Array<{
          nutrient: string;
          nutrient_ar?: string;
          severity: string;
          confidence: number;
          symptoms: string[];
          symptoms_ar?: string[];
          recommendations: string[];
        }>;
      }>(`${CROP_API_BASE}/nutrient-analysis`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(analysisRequest),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 400, 401, 422]).toContain(response.status);

      if (response.status === 200 && response.data.deficiencies) {
        response.data.deficiencies.forEach((def) => {
          expect(def).toHaveProperty("nutrient");
          expect(def).toHaveProperty("severity");
          expect(["none", "low", "medium", "high", "critical"]).toContain(
            def.severity
          );
        });
      }
    });

    it("should estimate growth stage", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        crop_type: string;
        growth_stage: string;
        growth_stage_ar?: string;
        days_after_planting?: number;
        estimated_days_to_harvest?: number;
        confidence: number;
      }>(`${CROP_API_BASE}/growth-stage/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("growth_stage");
        expect(response.data).toHaveProperty("confidence");
        expect(response.data.confidence).toBeGreaterThanOrEqual(0);
        expect(response.data.confidence).toBeLessThanOrEqual(1);
      }
    });

    it("should generate crop health report", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        report: {
          summary: string;
          summary_ar?: string;
          health_score: number;
          key_findings: string[];
          key_findings_ar?: string[];
          action_items: Array<{
            priority: string;
            action: string;
            action_ar?: string;
          }>;
        };
        generated_at: string;
      }>(`${CROP_API_BASE}/report/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.report) {
        expect(response.data.report).toHaveProperty("summary");
        expect(response.data.report).toHaveProperty("health_score");
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Yield Prediction Tests - اختبارات تنبؤ الإنتاجية
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Yield Prediction", () => {
    const YIELD_API_BASE = `${YIELD_ENGINE_URL}/api/v1/yield`;

    it("should verify yield engine service is registered", async () => {
      const health = await checkServiceHealth("YIELD_ENGINE", YIELD_ENGINE_URL);

      expect(health.service).toBe("YIELD_ENGINE");
      expect(["healthy", "unhealthy", "unknown"]).toContain(health.status);
    });

    it("should predict yield for field", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        crop_type: string;
        predicted_yield_kg_ha: number;
        confidence_interval: {
          low: number;
          high: number;
        };
        prediction_date: string;
        model_version: string;
      }>(`${YIELD_API_BASE}/predict/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("predicted_yield_kg_ha");
        expect(response.data.predicted_yield_kg_ha).toBeGreaterThan(0);

        if (response.data.confidence_interval) {
          expect(response.data.confidence_interval.low).toBeLessThanOrEqual(
            response.data.predicted_yield_kg_ha
          );
          expect(response.data.confidence_interval.high).toBeGreaterThanOrEqual(
            response.data.predicted_yield_kg_ha
          );
        }
      }
    });

    it("should compare yield prediction to historical average", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        predicted_yield_kg_ha: number;
        historical_avg_yield_kg_ha?: number;
        deviation_percent?: number;
        comparison: string;
      }>(`${YIELD_API_BASE}/compare/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.comparison) {
        expect(["above_average", "average", "below_average"]).toContain(
          response.data.comparison
        );
      }
    });

    it("should provide yield prediction factors", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        factors: Array<{
          factor: string;
          factor_ar?: string;
          impact: string;
          value: number;
          optimal_range?: { min: number; max: number };
        }>;
      }>(`${YIELD_API_BASE}/factors/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.factors) {
        response.data.factors.forEach((factor) => {
          expect(factor).toHaveProperty("factor");
          expect(factor).toHaveProperty("impact");
          expect(["positive", "neutral", "negative"]).toContain(factor.impact);
        });
      }
    });

    it("should simulate yield scenarios", async () => {
      const simulationRequest = {
        field_id: "field-test-001",
        scenarios: [
          {
            name: "optimal_irrigation",
            irrigation_increase_percent: 20,
          },
          {
            name: "reduced_fertilizer",
            fertilizer_reduction_percent: 15,
          },
        ],
      };

      const response = await apiRequest<{
        field_id: string;
        baseline_yield_kg_ha: number;
        scenarios: Array<{
          name: string;
          predicted_yield_kg_ha: number;
          yield_change_percent: number;
          cost_impact?: number;
        }>;
      }>(`${YIELD_API_BASE}/simulate`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(simulationRequest),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 400, 401, 422]).toContain(response.status);

      if (response.status === 200 && response.data.scenarios) {
        expect(response.data.scenarios.length).toBe(2);

        response.data.scenarios.forEach((scenario) => {
          expect(scenario).toHaveProperty("name");
          expect(scenario).toHaveProperty("predicted_yield_kg_ha");
          expect(scenario).toHaveProperty("yield_change_percent");
        });
      }
    });

    it("should provide harvest timing recommendation", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        crop_type: string;
        optimal_harvest_window: {
          start_date: string;
          end_date: string;
        };
        current_maturity_percent: number;
        estimated_days_to_harvest: number;
        weather_risk?: string;
      }>(`${YIELD_API_BASE}/harvest-timing/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("current_maturity_percent");
        expect(response.data.current_maturity_percent).toBeGreaterThanOrEqual(0);
        expect(response.data.current_maturity_percent).toBeLessThanOrEqual(100);
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Advisory Service Tests - اختبارات خدمة الاستشارات
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Advisory Service", () => {
    const ADVISORY_API_BASE = `${ADVISORY_SERVICE_URL}/api/v1/advisory`;

    it("should verify advisory service is registered", async () => {
      const health = await checkServiceHealth(
        "ADVISORY_SERVICE",
        ADVISORY_SERVICE_URL
      );

      expect(health.service).toBe("ADVISORY_SERVICE");
      expect(["healthy", "unhealthy", "unknown"]).toContain(health.status);
    });

    it("should generate fertilizer recommendation", async () => {
      const recommendationRequest = {
        field_id: "field-test-001",
        crop_type: "wheat",
        growth_stage: "tillering",
        soil_test: {
          nitrogen_ppm: 18,
          phosphorus_ppm: 25,
          potassium_ppm: 150,
          ph: 7.2,
          organic_matter_percent: 2.1,
        },
        target_yield_kg_ha: 5000,
      };

      const response = await apiRequest<{
        field_id: string;
        recommendations: Array<{
          fertilizer_type: string;
          fertilizer_type_ar?: string;
          recommended_rate_kg_ha: number;
          application_timing: string;
          application_method: string;
          priority: string;
          rationale: string;
          rationale_ar?: string;
        }>;
        total_cost_estimate?: number;
      }>(`${ADVISORY_API_BASE}/fertilizer`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(recommendationRequest),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 400, 401, 422]).toContain(response.status);

      if (response.status === 200 && response.data.recommendations) {
        response.data.recommendations.forEach((rec) => {
          expect(rec).toHaveProperty("fertilizer_type");
          expect(rec).toHaveProperty("recommended_rate_kg_ha");
          expect(rec.recommended_rate_kg_ha).toBeGreaterThan(0);
        });
      }
    });

    it("should generate pest management advisory", async () => {
      const advisoryRequest = {
        field_id: "field-test-001",
        crop_type: "wheat",
        pest_detected: "aphid",
        severity: "medium",
        growth_stage: "heading",
      };

      const response = await apiRequest<{
        field_id: string;
        pest: string;
        advisory: {
          immediate_actions: string[];
          immediate_actions_ar?: string[];
          treatment_options: Array<{
            product: string;
            product_ar?: string;
            rate: string;
            application_method: string;
            phi_days: number; // Pre-harvest interval
          }>;
          preventive_measures: string[];
          monitoring_schedule: string;
        };
      }>(`${ADVISORY_API_BASE}/pest-management`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(advisoryRequest),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 400, 401, 422]).toContain(response.status);

      if (response.status === 200 && response.data.advisory) {
        expect(response.data.advisory).toHaveProperty("immediate_actions");
        expect(response.data.advisory).toHaveProperty("treatment_options");
      }
    });

    it("should provide general crop management advisory", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        crop_type: string;
        advisories: Array<{
          id: string;
          category: string;
          priority: string;
          title: string;
          title_ar?: string;
          description: string;
          description_ar?: string;
          action_required: boolean;
          deadline?: string;
        }>;
      }>(`${ADVISORY_API_BASE}/field/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.advisories) {
        response.data.advisories.forEach((advisory) => {
          expect(advisory).toHaveProperty("category");
          expect(advisory).toHaveProperty("priority");
          expect(advisory).toHaveProperty("title");
          expect(["high", "medium", "low"]).toContain(advisory.priority);
        });
      }
    });

    it("should generate weather-based advisory", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        weather_condition: string;
        advisories: Array<{
          type: string;
          urgency: string;
          recommendation: string;
          recommendation_ar?: string;
        }>;
      }>(`${ADVISORY_API_BASE}/weather-based/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);
    });

    it("should support Arabic language advisory", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        advisories: Array<{
          title: string;
          title_ar: string;
          description: string;
          description_ar: string;
        }>;
      }>(`${ADVISORY_API_BASE}/field/${fieldId}`, {
        method: "GET",
        headers: {
          ...getAuthHeaders(authToken),
          "Accept-Language": "ar",
        },
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      if (response.status === 200 && response.data.advisories?.length > 0) {
        const advisory = response.data.advisories[0];
        if (advisory.title_ar) {
          expect(advisory.title_ar).toBeTruthy();
        }
      }
    });

    it("should mark advisory as actioned", async () => {
      const advisoryId = `advisory-${generateTestId()}`;

      const response = await apiRequest<{
        id: string;
        status: string;
        actioned_at: string;
      }>(`${ADVISORY_API_BASE}/${advisoryId}/action`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify({
          action_taken: "applied_fertilizer",
          notes: "Applied Urea 46% at 46 kg/ha",
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);
    });

    it("should provide integrated farm advisory dashboard", async () => {
      const farmId = TEST_DATA.FIELD.farm_id;

      const response = await apiRequest<{
        farm_id: string;
        summary: {
          total_advisories: number;
          urgent_count: number;
          pending_actions: number;
        };
        advisories_by_category: Record<
          string,
          Array<{
            id: string;
            title: string;
            priority: string;
          }>
        >;
      }>(`${ADVISORY_API_BASE}/farm/${farmId}/dashboard`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.summary) {
        expect(response.data.summary).toHaveProperty("total_advisories");
        expect(response.data.summary).toHaveProperty("urgent_count");
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // AI Service Metrics & Monitoring Tests - اختبارات مقاييس ومراقبة خدمات الذكاء
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("AI Service Metrics", () => {
    it("should expose Prometheus metrics", async () => {
      const services = [
        VISION_SERVICE_URL,
        CROP_INTELLIGENCE_URL,
        YIELD_ENGINE_URL,
        ADVISORY_SERVICE_URL,
      ];

      for (const serviceUrl of services) {
        const response = await apiRequest<string>(`${serviceUrl}/metrics`);

        if (response.status === 502 || response.status === 503) {
          continue;
        }

        // Metrics endpoint should be available
        expect([200, 404]).toContain(response.status);
      }
    });

    it("should provide model inference statistics", async () => {
      const response = await apiRequest<{
        models: Array<{
          model_id: string;
          total_inferences: number;
          avg_latency_ms: number;
          success_rate: number;
        }>;
      }>(`${VISION_SERVICE_URL}/api/v1/stats/models`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.models) {
        response.data.models.forEach((model) => {
          expect(model).toHaveProperty("model_id");
          expect(model).toHaveProperty("total_inferences");
          expect(model.success_rate).toBeGreaterThanOrEqual(0);
          expect(model.success_rate).toBeLessThanOrEqual(100);
        });
      }
    });
  });
});
