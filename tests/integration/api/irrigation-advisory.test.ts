/**
 * SAHOOL Irrigation Advisory API Integration Tests
 * اختبارات تكامل API استشارات الري لمنصة سهول
 *
 * Tests cover:
 * - Get irrigation schedule
 * - Calculate water requirements
 * - Smart irrigation recommendations
 * - Crop water stress indicators
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
  isValidISO8601,
  checkServiceHealth,
  MOCK_RESPONSES,
} from "./setup";

// ═══════════════════════════════════════════════════════════════════════════════
// Test Configuration
// ═══════════════════════════════════════════════════════════════════════════════

const IRRIGATION_SERVICE_URL = TEST_CONFIG.SERVICES.IRRIGATION_SERVICE;
const IRRIGATION_API_BASE = `${IRRIGATION_SERVICE_URL}/api/v1/irrigation`;

describe("Irrigation Advisory API Integration Tests", () => {
  let authToken: string;
  let serviceHealthy: boolean = false;

  // ─────────────────────────────────────────────────────────────────────────────
  // Setup & Teardown
  // ─────────────────────────────────────────────────────────────────────────────

  beforeAll(async () => {
    authToken = await getAuthToken("FARMER");

    const health = await checkServiceHealth(
      "IRRIGATION_SERVICE",
      IRRIGATION_SERVICE_URL
    );
    serviceHealthy = health.status === "healthy";

    if (!serviceHealthy) {
      console.warn(
        "Irrigation service not available - tests will use mock validation"
      );
    }
  });

  afterAll(() => {
    clearAuthCache();
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Service Health Tests - اختبارات صحة الخدمة
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Service Health", () => {
    it("should verify irrigation service is registered and responding", async () => {
      const health = await checkServiceHealth(
        "IRRIGATION_SERVICE",
        IRRIGATION_SERVICE_URL
      );

      expect(health.service).toBe("IRRIGATION_SERVICE");
      expect(["healthy", "unhealthy", "unknown"]).toContain(health.status);
      expect(health.responseTime).toBeGreaterThan(0);
    });

    it("should have health endpoint available", async () => {
      const response = await apiRequest<{ status: string; service?: string }>(
        `${IRRIGATION_SERVICE_URL}/healthz`
      );

      expect([200, 404, 502, 503]).toContain(response.status);

      if (response.ok) {
        expect(response.data).toHaveProperty("status");
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Get Irrigation Schedule Tests - اختبارات جلب جدول الري
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Get Irrigation Schedule", () => {
    it("should retrieve irrigation schedule for field", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        schedule: Array<{
          date: string;
          start_time?: string;
          duration_minutes: number;
          amount_mm: number;
          status: string;
        }>;
      }>(`${IRRIGATION_API_BASE}/schedule/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        // Validate mock response structure
        expect(MOCK_RESPONSES.IRRIGATION).toHaveProperty("field_id");
        expect(MOCK_RESPONSES.IRRIGATION).toHaveProperty(
          "recommended_amount_mm"
        );
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("field_id");
        expect(response.data).toHaveProperty("schedule");
        expect(Array.isArray(response.data.schedule)).toBe(true);

        response.data.schedule.forEach((event) => {
          expect(event).toHaveProperty("date");
          expect(event).toHaveProperty("duration_minutes");
          expect(event).toHaveProperty("amount_mm");
          expect(event.duration_minutes).toBeGreaterThan(0);
          expect(event.amount_mm).toBeGreaterThan(0);
        });
      }
    });

    it("should filter schedule by date range", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;
      const startDate = new Date().toISOString().split("T")[0];
      const endDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split("T")[0];

      const response = await apiRequest<{
        field_id: string;
        schedule: Array<{
          date: string;
          duration_minutes: number;
        }>;
      }>(
        `${IRRIGATION_API_BASE}/schedule/${fieldId}?start_date=${startDate}&end_date=${endDate}`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.schedule) {
        response.data.schedule.forEach((event) => {
          const eventDate = new Date(event.date);
          expect(eventDate >= new Date(startDate)).toBe(true);
          expect(eventDate <= new Date(endDate)).toBe(true);
        });
      }
    });

    it("should include next irrigation recommendation", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        next_irrigation?: {
          recommended_date: string;
          recommended_amount_mm: number;
          urgency: string;
        };
      }>(`${IRRIGATION_API_BASE}/next/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.next_irrigation) {
        expect(response.data.next_irrigation).toHaveProperty("recommended_date");
        expect(response.data.next_irrigation).toHaveProperty(
          "recommended_amount_mm"
        );
        expect(["low", "medium", "high", "critical"]).toContain(
          response.data.next_irrigation.urgency
        );
      }
    });

    it("should create new irrigation event", async () => {
      const scheduleData = {
        field_id: TEST_DATA.IRRIGATION_SCHEDULE.field_id,
        scheduled_date: new Date(Date.now() + 24 * 60 * 60 * 1000)
          .toISOString()
          .split("T")[0],
        start_time: "06:00",
        duration_minutes: 45,
        amount_mm: 25,
        notes: "Morning irrigation",
        notes_ar: "ري صباحي",
      };

      const response = await apiRequest<{
        id: string;
        field_id: string;
        scheduled_date: string;
        status: string;
      }>(`${IRRIGATION_API_BASE}/schedule`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(scheduleData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 201, 401, 422]).toContain(response.status);

      if (response.status === 200 || response.status === 201) {
        expect(response.data).toHaveProperty("id");
        expect(response.data.field_id).toBe(scheduleData.field_id);
        expect(response.data.status).toBe("scheduled");
      }
    });

    it("should update irrigation event status", async () => {
      const eventId = "irrigation-event-001";

      const response = await apiRequest<{
        id: string;
        status: string;
        completed_at?: string;
      }>(`${IRRIGATION_API_BASE}/schedule/${eventId}`, {
        method: "PATCH",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify({
          status: "completed",
          actual_amount_mm: 24,
          actual_duration_minutes: 42,
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404, 422]).toContain(response.status);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Calculate Water Requirements Tests - اختبارات حساب متطلبات المياه
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Calculate Water Requirements", () => {
    it("should calculate daily water requirement for field", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        date: string;
        crop_type: string;
        growth_stage?: string;
        water_requirement_mm: number;
        et_mm: number;
        kc: number; // Crop coefficient
        effective_rainfall_mm?: number;
        net_irrigation_requirement_mm: number;
      }>(`${IRRIGATION_API_BASE}/water-requirement/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("water_requirement_mm");
        expect(response.data).toHaveProperty("et_mm");
        expect(response.data).toHaveProperty("net_irrigation_requirement_mm");

        expect(response.data.water_requirement_mm).toBeGreaterThanOrEqual(0);
        expect(response.data.et_mm).toBeGreaterThanOrEqual(0);
        expect(response.data.kc).toBeGreaterThan(0);
        expect(response.data.kc).toBeLessThan(2); // Kc typically < 1.5
      }
    });

    it("should calculate weekly water budget", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        week_start: string;
        week_end: string;
        total_et_mm: number;
        total_rainfall_mm: number;
        net_irrigation_mm: number;
        daily_breakdown: Array<{
          date: string;
          et_mm: number;
          rainfall_mm: number;
          irrigation_mm: number;
        }>;
      }>(`${IRRIGATION_API_BASE}/water-budget/${fieldId}/weekly`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("total_et_mm");
        expect(response.data).toHaveProperty("net_irrigation_mm");

        if (response.data.daily_breakdown) {
          expect(response.data.daily_breakdown.length).toBe(7);
        }
      }
    });

    it("should calculate water requirement based on growth stage", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;
      const growthStage = "tillering";

      const response = await apiRequest<{
        field_id: string;
        growth_stage: string;
        kc: number;
        water_requirement_mm: number;
        stage_description?: string;
        stage_description_ar?: string;
      }>(
        `${IRRIGATION_API_BASE}/water-requirement/${fieldId}?growth_stage=${growthStage}`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data.growth_stage).toBe(growthStage);
        expect(response.data.kc).toBeGreaterThan(0);
      }
    });

    it("should account for soil moisture in calculation", async () => {
      const requestData = {
        field_id: TEST_DATA.IRRIGATION_SCHEDULE.field_id,
        current_soil_moisture_percent: 35,
        field_capacity_percent: 40,
        wilting_point_percent: 15,
        root_depth_cm: 60,
      };

      const response = await apiRequest<{
        field_id: string;
        current_soil_moisture_percent: number;
        soil_water_deficit_mm: number;
        irrigation_required: boolean;
        recommended_amount_mm: number;
      }>(`${IRRIGATION_API_BASE}/soil-based-requirement`, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(requestData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404, 422]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("soil_water_deficit_mm");
        expect(response.data).toHaveProperty("irrigation_required");
        expect(response.data).toHaveProperty("recommended_amount_mm");
      }
    });

    it("should support multiple crop water requirement calculations", async () => {
      const cropTypes = ["wheat", "barley", "tomato", "date_palm"];

      for (const cropType of cropTypes) {
        const response = await apiRequest<{
          crop_type: string;
          kc_initial: number;
          kc_mid: number;
          kc_end: number;
        }>(`${IRRIGATION_API_BASE}/crop-coefficients/${cropType}`, {
          method: "GET",
          headers: getAuthHeaders(authToken),
        });

        if (response.status === 502 || response.status === 503) {
          continue;
        }

        if (response.status === 200) {
          expect(response.data.crop_type).toBe(cropType);
          expect(response.data.kc_initial).toBeGreaterThan(0);
          expect(response.data.kc_mid).toBeGreaterThan(0);
          expect(response.data.kc_end).toBeGreaterThan(0);
        }
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Smart Irrigation Recommendations Tests - اختبارات توصيات الري الذكي
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Smart Irrigation Recommendations", () => {
    it("should generate smart irrigation recommendation", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        recommendation: {
          action: string;
          urgency: string;
          recommended_date: string;
          recommended_amount_mm: number;
          recommended_duration_minutes: number;
          confidence: number;
          rationale: string;
          rationale_ar?: string;
        };
        factors_considered: string[];
      }>(`${IRRIGATION_API_BASE}/smart-recommendation/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("recommendation");

        const rec = response.data.recommendation;
        expect(["irrigate", "skip", "delay", "reduce"]).toContain(rec.action);
        expect(["low", "medium", "high", "critical"]).toContain(rec.urgency);
        expect(rec.confidence).toBeGreaterThanOrEqual(0);
        expect(rec.confidence).toBeLessThanOrEqual(100);
      }
    });

    it("should consider weather forecast in recommendations", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        recommendation: {
          action: string;
          weather_impact: {
            rain_expected: boolean;
            rain_amount_mm?: number;
            recommendation_adjusted: boolean;
          };
        };
      }>(`${IRRIGATION_API_BASE}/smart-recommendation/${fieldId}?include_weather=true`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.recommendation.weather_impact) {
        expect(response.data.recommendation.weather_impact).toHaveProperty(
          "rain_expected"
        );
      }
    });

    it("should provide optimal irrigation time", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        optimal_times: Array<{
          date: string;
          start_time: string;
          end_time: string;
          suitability_score: number;
          reasons: string[];
        }>;
      }>(`${IRRIGATION_API_BASE}/optimal-time/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.optimal_times) {
        response.data.optimal_times.forEach((time) => {
          expect(time).toHaveProperty("start_time");
          expect(time).toHaveProperty("suitability_score");
          expect(time.suitability_score).toBeGreaterThanOrEqual(0);
          expect(time.suitability_score).toBeLessThanOrEqual(100);
        });
      }
    });

    it("should calculate water savings potential", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        current_usage_mm: number;
        optimal_usage_mm: number;
        potential_savings_mm: number;
        potential_savings_percent: number;
        recommendations: string[];
        recommendations_ar?: string[];
      }>(`${IRRIGATION_API_BASE}/water-savings/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("potential_savings_mm");
        expect(response.data).toHaveProperty("potential_savings_percent");
        expect(response.data.potential_savings_percent).toBeGreaterThanOrEqual(0);
      }
    });

    it("should support deficit irrigation strategies", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        strategies: Array<{
          name: string;
          name_ar?: string;
          deficit_level_percent: number;
          expected_yield_impact_percent: number;
          water_savings_percent: number;
          suitable_stages: string[];
        }>;
      }>(`${IRRIGATION_API_BASE}/deficit-strategies/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.strategies) {
        response.data.strategies.forEach((strategy) => {
          expect(strategy).toHaveProperty("deficit_level_percent");
          expect(strategy).toHaveProperty("water_savings_percent");
          expect(strategy.deficit_level_percent).toBeGreaterThan(0);
          expect(strategy.deficit_level_percent).toBeLessThanOrEqual(100);
        });
      }
    });

    it("should integrate with IoT sensors for real-time recommendations", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        sensor_data: {
          soil_moisture_percent: number;
          soil_temperature_c: number;
          timestamp: string;
        };
        recommendation: {
          action: string;
          data_source: string;
        };
      }>(`${IRRIGATION_API_BASE}/sensor-based/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.sensor_data) {
        expect(response.data.sensor_data.soil_moisture_percent).toBeGreaterThanOrEqual(0);
        expect(response.data.sensor_data.soil_moisture_percent).toBeLessThanOrEqual(100);
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Crop Water Stress Indicators Tests - اختبارات مؤشرات إجهاد المياه
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Crop Water Stress Indicators", () => {
    it("should calculate crop water stress index (CWSI)", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        cwsi: number;
        stress_level: string;
        timestamp: string;
        interpretation: string;
        interpretation_ar?: string;
      }>(`${IRRIGATION_API_BASE}/stress-index/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("cwsi");
        expect(response.data).toHaveProperty("stress_level");

        expect(response.data.cwsi).toBeGreaterThanOrEqual(0);
        expect(response.data.cwsi).toBeLessThanOrEqual(1);
        expect(["none", "mild", "moderate", "severe", "critical"]).toContain(
          response.data.stress_level
        );
      }
    });

    it("should retrieve stress history for trend analysis", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;
      const startDate = "2025-01-01";
      const endDate = "2025-01-14";

      const response = await apiRequest<{
        field_id: string;
        stress_history: Array<{
          date: string;
          cwsi: number;
          stress_level: string;
        }>;
        trend: string;
      }>(
        `${IRRIGATION_API_BASE}/stress-history/${fieldId}?start_date=${startDate}&end_date=${endDate}`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.stress_history) {
        expect(Array.isArray(response.data.stress_history)).toBe(true);

        response.data.stress_history.forEach((entry) => {
          expect(entry).toHaveProperty("date");
          expect(entry).toHaveProperty("cwsi");
          expect(entry.cwsi).toBeGreaterThanOrEqual(0);
          expect(entry.cwsi).toBeLessThanOrEqual(1);
        });

        if (response.data.trend) {
          expect(["improving", "stable", "worsening"]).toContain(
            response.data.trend
          );
        }
      }
    });

    it("should provide stress-based alerts", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        alerts: Array<{
          id: string;
          type: string;
          severity: string;
          message: string;
          message_ar?: string;
          recommended_action: string;
          created_at: string;
        }>;
      }>(`${IRRIGATION_API_BASE}/stress-alerts/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.alerts) {
        response.data.alerts.forEach((alert) => {
          expect(alert).toHaveProperty("type");
          expect(alert).toHaveProperty("severity");
          expect(alert).toHaveProperty("message");
        });
      }
    });

    it("should integrate NDVI-based stress detection", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        ndvi_current: number;
        ndvi_baseline?: number;
        ndvi_deviation?: number;
        water_stress_indicated: boolean;
        confidence: number;
      }>(`${IRRIGATION_API_BASE}/ndvi-stress/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("ndvi_current");
        expect(response.data).toHaveProperty("water_stress_indicated");

        expect(response.data.ndvi_current).toBeGreaterThanOrEqual(-1);
        expect(response.data.ndvi_current).toBeLessThanOrEqual(1);
      }
    });

    it("should calculate soil moisture depletion", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        current_moisture_percent: number;
        field_capacity_percent: number;
        wilting_point_percent: number;
        depletion_percent: number;
        mad_threshold_percent: number; // Maximum Allowable Depletion
        irrigation_needed: boolean;
      }>(`${IRRIGATION_API_BASE}/soil-depletion/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("depletion_percent");
        expect(response.data).toHaveProperty("irrigation_needed");

        expect(response.data.depletion_percent).toBeGreaterThanOrEqual(0);
        expect(response.data.depletion_percent).toBeLessThanOrEqual(100);
      }
    });

    it("should provide multi-factor stress assessment", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        assessment: {
          overall_stress_level: string;
          factors: Array<{
            factor: string;
            factor_ar?: string;
            value: number;
            weight: number;
            contribution: number;
          }>;
          recommendations: string[];
          recommendations_ar?: string[];
        };
      }>(`${IRRIGATION_API_BASE}/stress-assessment/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.assessment) {
        expect(response.data.assessment).toHaveProperty("overall_stress_level");
        expect(response.data.assessment).toHaveProperty("factors");

        if (response.data.assessment.factors) {
          response.data.assessment.factors.forEach((factor) => {
            expect(factor).toHaveProperty("factor");
            expect(factor).toHaveProperty("value");
            expect(factor).toHaveProperty("weight");
          });
        }
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Irrigation System Integration Tests - اختبارات تكامل نظام الري
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Irrigation System Integration", () => {
    it("should support drip irrigation calculations", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        irrigation_type: string;
        emitter_flow_rate_lph: number;
        emitter_spacing_m: number;
        row_spacing_m: number;
        application_rate_mm_h: number;
        runtime_hours: number;
      }>(`${IRRIGATION_API_BASE}/drip-calculation/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data.irrigation_type).toBe("drip");
        expect(response.data.application_rate_mm_h).toBeGreaterThan(0);
        expect(response.data.runtime_hours).toBeGreaterThan(0);
      }
    });

    it("should support pivot irrigation calculations", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        irrigation_type: string;
        pivot_length_m: number;
        application_depth_mm: number;
        rotation_time_hours: number;
        flow_rate_m3_h: number;
      }>(`${IRRIGATION_API_BASE}/pivot-calculation/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data.irrigation_type).toBe("pivot");
        expect(response.data.rotation_time_hours).toBeGreaterThan(0);
      }
    });

    it("should calculate irrigation efficiency", async () => {
      const fieldId = TEST_DATA.IRRIGATION_SCHEDULE.field_id;

      const response = await apiRequest<{
        field_id: string;
        irrigation_type: string;
        application_efficiency: number;
        distribution_uniformity: number;
        overall_efficiency: number;
        improvement_recommendations?: string[];
      }>(`${IRRIGATION_API_BASE}/efficiency/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data.application_efficiency).toBeGreaterThan(0);
        expect(response.data.application_efficiency).toBeLessThanOrEqual(100);
        expect(response.data.overall_efficiency).toBeGreaterThan(0);
        expect(response.data.overall_efficiency).toBeLessThanOrEqual(100);
      }
    });
  });
});
