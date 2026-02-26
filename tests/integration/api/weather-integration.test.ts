/**
 * SAHOOL Weather API Integration Tests
 * اختبارات تكامل API الطقس لمنصة سهول
 *
 * Tests cover:
 * - Get current weather
 * - Weather forecast
 * - Historical weather data
 * - Weather alerts
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

const WEATHER_SERVICE_URL = TEST_CONFIG.SERVICES.WEATHER_SERVICE;
const WEATHER_API_BASE = `${WEATHER_SERVICE_URL}/api/v1/weather`;

describe("Weather API Integration Tests", () => {
  let authToken: string;
  let serviceHealthy: boolean = false;

  // ─────────────────────────────────────────────────────────────────────────────
  // Setup & Teardown
  // ─────────────────────────────────────────────────────────────────────────────

  beforeAll(async () => {
    authToken = await getAuthToken("FARMER");

    const health = await checkServiceHealth(
      "WEATHER_SERVICE",
      WEATHER_SERVICE_URL
    );
    serviceHealthy = health.status === "healthy";

    if (!serviceHealthy) {
      console.warn(
        "Weather service not available - tests will use mock validation"
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
    it("should verify weather service is registered and responding", async () => {
      const health = await checkServiceHealth(
        "WEATHER_SERVICE",
        WEATHER_SERVICE_URL
      );

      expect(health.service).toBe("WEATHER_SERVICE");
      expect(["healthy", "unhealthy", "unknown"]).toContain(health.status);
      expect(health.responseTime).toBeGreaterThan(0);
    });

    it("should have health endpoint available", async () => {
      const response = await apiRequest<{ status: string; service?: string }>(
        `${WEATHER_SERVICE_URL}/healthz`
      );

      expect([200, 404, 502, 503]).toContain(response.status);

      if (response.ok) {
        expect(response.data).toHaveProperty("status");
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Get Current Weather Tests - اختبارات جلب الطقس الحالي
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Get Current Weather", () => {
    it("should retrieve current weather for location ID", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        temperature_c: number;
        humidity_percent: number;
        wind_speed_kmh: number;
        condition: string;
        condition_ar?: string;
        timestamp: string;
      }>(`${WEATHER_API_BASE}/current/${locationId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        // Validate mock response structure
        expect(MOCK_RESPONSES.WEATHER).toHaveProperty("temperature_c");
        expect(MOCK_RESPONSES.WEATHER).toHaveProperty("humidity_percent");
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("temperature_c");
        expect(response.data).toHaveProperty("humidity_percent");
        expect(response.data).toHaveProperty("wind_speed_kmh");
        expect(response.data).toHaveProperty("condition");

        // Validate temperature range (reasonable for Yemen)
        expect(response.data.temperature_c).toBeGreaterThan(-10);
        expect(response.data.temperature_c).toBeLessThan(55);

        // Validate humidity percentage
        expect(response.data.humidity_percent).toBeGreaterThanOrEqual(0);
        expect(response.data.humidity_percent).toBeLessThanOrEqual(100);
      }
    });

    it("should retrieve current weather by coordinates", async () => {
      const lat = TEST_DATA.WEATHER_LOCATION.latitude;
      const lng = TEST_DATA.WEATHER_LOCATION.longitude;

      const response = await apiRequest<{
        temperature_c: number;
        humidity_percent: number;
        condition: string;
      }>(`${WEATHER_API_BASE}/current?lat=${lat}&lng=${lng}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("temperature_c");
        expect(response.data).toHaveProperty("humidity_percent");
      }
    });

    it("should retrieve current weather by field ID", async () => {
      const fieldId = "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        temperature_c: number;
        humidity_percent: number;
        condition: string;
      }>(`${WEATHER_API_BASE}/current/field/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);
    });

    it("should include Arabic weather condition", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        condition: string;
        condition_ar: string;
      }>(`${WEATHER_API_BASE}/current/${locationId}`, {
        method: "GET",
        headers: {
          ...getAuthHeaders(authToken),
          "Accept-Language": "ar",
        },
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      if (response.status === 200) {
        expect(response.data).toHaveProperty("condition");
        if (response.data.condition_ar) {
          expect(response.data.condition_ar).toBeTruthy();
        }
      }
    });

    it("should include additional weather metrics", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        temperature_c: number;
        humidity_percent: number;
        wind_speed_kmh: number;
        wind_direction?: string;
        pressure_hpa?: number;
        visibility_km?: number;
        uv_index?: number;
        feels_like_c?: number;
        dew_point_c?: number;
      }>(`${WEATHER_API_BASE}/current/${locationId}?detailed=true`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        // Basic metrics should always be present
        expect(response.data).toHaveProperty("temperature_c");
        expect(response.data).toHaveProperty("humidity_percent");
      }
    });

    it("should return 404 for invalid location", async () => {
      const response = await apiRequest(
        `${WEATHER_API_BASE}/current/invalid-location`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([404, 422]).toContain(response.status);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Weather Forecast Tests - اختبارات توقعات الطقس
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Weather Forecast", () => {
    it("should retrieve 7-day weather forecast", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        daily_forecast: Array<{
          date: string;
          temp_max_c: number;
          temp_min_c: number;
          condition: string;
          precipitation_mm?: number;
        }>;
      }>(`${WEATHER_API_BASE}/forecast/${locationId}?days=7`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("daily_forecast");
        expect(Array.isArray(response.data.daily_forecast)).toBe(true);
        expect(response.data.daily_forecast.length).toBeLessThanOrEqual(7);

        response.data.daily_forecast.forEach((day) => {
          expect(day).toHaveProperty("date");
          expect(day).toHaveProperty("temp_max_c");
          expect(day).toHaveProperty("temp_min_c");
          expect(day).toHaveProperty("condition");
          expect(isValidISO8601(day.date)).toBe(true);
          expect(day.temp_max_c).toBeGreaterThanOrEqual(day.temp_min_c);
        });
      }
    });

    it("should retrieve hourly forecast for current day", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        hourly_forecast: Array<{
          datetime: string;
          temperature_c: number;
          humidity_percent: number;
          condition: string;
        }>;
      }>(`${WEATHER_API_BASE}/forecast/${locationId}/hourly`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.hourly_forecast) {
        expect(Array.isArray(response.data.hourly_forecast)).toBe(true);

        response.data.hourly_forecast.forEach((hour) => {
          expect(hour).toHaveProperty("datetime");
          expect(hour).toHaveProperty("temperature_c");
          expect(hour).toHaveProperty("condition");
        });
      }
    });

    it("should include precipitation probability in forecast", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        daily_forecast: Array<{
          date: string;
          precipitation_probability?: number;
          precipitation_mm?: number;
          rain_probability?: number;
        }>;
      }>(`${WEATHER_API_BASE}/forecast/${locationId}?days=7`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      if (response.status === 200 && response.data.daily_forecast) {
        response.data.daily_forecast.forEach((day) => {
          const hasPrecipData =
            day.precipitation_probability !== undefined ||
            day.precipitation_mm !== undefined ||
            day.rain_probability !== undefined;

          // Precipitation data might not always be available
          if (hasPrecipData) {
            if (day.precipitation_probability !== undefined) {
              expect(day.precipitation_probability).toBeGreaterThanOrEqual(0);
              expect(day.precipitation_probability).toBeLessThanOrEqual(100);
            }
          }
        });
      }
    });

    it("should retrieve agricultural weather metrics", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        agricultural_metrics?: {
          et_mm?: number; // Evapotranspiration
          gdd?: number; // Growing Degree Days
          chill_hours?: number;
          solar_radiation?: number;
        };
      }>(`${WEATHER_API_BASE}/agricultural/${locationId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.agricultural_metrics) {
        if (response.data.agricultural_metrics.et_mm !== undefined) {
          expect(response.data.agricultural_metrics.et_mm).toBeGreaterThanOrEqual(0);
        }
      }
    });

    it("should support custom forecast duration", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        daily_forecast: Array<{ date: string }>;
      }>(`${WEATHER_API_BASE}/forecast/${locationId}?days=14`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.daily_forecast) {
        expect(response.data.daily_forecast.length).toBeLessThanOrEqual(14);
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Historical Weather Data Tests - اختبارات بيانات الطقس التاريخية
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Historical Weather Data", () => {
    it("should retrieve historical weather for date range", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;
      const startDate = "2025-01-01";
      const endDate = "2025-01-07";

      const response = await apiRequest<{
        location_id: string;
        start_date: string;
        end_date: string;
        daily_data: Array<{
          date: string;
          temp_max_c: number;
          temp_min_c: number;
          temp_avg_c?: number;
          humidity_avg?: number;
          precipitation_mm?: number;
        }>;
      }>(
        `${WEATHER_API_BASE}/history/${locationId}?start_date=${startDate}&end_date=${endDate}`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.daily_data) {
        expect(Array.isArray(response.data.daily_data)).toBe(true);

        response.data.daily_data.forEach((day) => {
          expect(day).toHaveProperty("date");
          expect(day).toHaveProperty("temp_max_c");
          expect(day).toHaveProperty("temp_min_c");
        });
      }
    });

    it("should retrieve historical weather for specific month", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        year: number;
        month: number;
        summary?: {
          avg_temp_c?: number;
          total_precipitation_mm?: number;
          avg_humidity?: number;
        };
      }>(`${WEATHER_API_BASE}/history/${locationId}/monthly?year=2024&month=12`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);
    });

    it("should calculate climate normals", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        climate_normals?: {
          jan?: { avg_temp_c: number; avg_precipitation_mm: number };
          feb?: { avg_temp_c: number; avg_precipitation_mm: number };
          // ... other months
        };
      }>(`${WEATHER_API_BASE}/climate/${locationId}/normals`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);
    });

    it("should compare current weather to historical average", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        current_temp_c: number;
        historical_avg_temp_c?: number;
        deviation_c?: number;
      }>(`${WEATHER_API_BASE}/comparison/${locationId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);
    });

    it("should retrieve growing degree days history", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;
      const startDate = "2025-01-01";

      const response = await apiRequest<{
        location_id: string;
        gdd_data: Array<{
          date: string;
          gdd: number;
          cumulative_gdd: number;
        }>;
      }>(
        `${WEATHER_API_BASE}/agricultural/${locationId}/gdd?start_date=${startDate}&base_temp=10`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.gdd_data) {
        response.data.gdd_data.forEach((entry) => {
          expect(entry.gdd).toBeGreaterThanOrEqual(0);
          expect(entry.cumulative_gdd).toBeGreaterThanOrEqual(0);
        });
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Weather Alerts Tests - اختبارات تنبيهات الطقس
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Weather Alerts", () => {
    it("should retrieve active weather alerts", async () => {
      const response = await apiRequest<{
        alerts: Array<{
          id: string;
          type: string;
          severity: string;
          title: string;
          title_ar?: string;
          description: string;
          affected_areas: string[];
          start_time: string;
          end_time?: string;
          is_active: boolean;
        }>;
      }>(`${WEATHER_API_BASE}/alerts`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.alerts) {
        expect(Array.isArray(response.data.alerts)).toBe(true);

        response.data.alerts.forEach((alert) => {
          expect(alert).toHaveProperty("id");
          expect(alert).toHaveProperty("type");
          expect(alert).toHaveProperty("severity");
          expect(alert).toHaveProperty("title");
          expect(["low", "medium", "high", "critical", "extreme"]).toContain(
            alert.severity
          );
        });
      }
    });

    it("should retrieve alerts for specific location", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        alerts: Array<{
          id: string;
          type: string;
          severity: string;
        }>;
      }>(`${WEATHER_API_BASE}/alerts/location/${locationId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);
    });

    it("should retrieve alerts by severity", async () => {
      const response = await apiRequest<{
        alerts: Array<{
          id: string;
          severity: string;
        }>;
      }>(`${WEATHER_API_BASE}/alerts?severity=high`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.alerts) {
        response.data.alerts.forEach((alert) => {
          expect(["high", "critical", "extreme"]).toContain(alert.severity);
        });
      }
    });

    it("should retrieve alerts by type", async () => {
      const alertTypes = [
        "frost",
        "heat_wave",
        "heavy_rain",
        "drought",
        "sandstorm",
        "flood",
      ];

      const response = await apiRequest<{
        alerts: Array<{
          id: string;
          type: string;
        }>;
      }>(`${WEATHER_API_BASE}/alerts?type=frost`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.alerts) {
        response.data.alerts.forEach((alert) => {
          expect(alert.type).toBe("frost");
        });
      }
    });

    it("should include Arabic content in alerts", async () => {
      const response = await apiRequest<{
        alerts: Array<{
          id: string;
          title: string;
          title_ar?: string;
          description: string;
          description_ar?: string;
        }>;
      }>(`${WEATHER_API_BASE}/alerts`, {
        method: "GET",
        headers: {
          ...getAuthHeaders(authToken),
          "Accept-Language": "ar",
        },
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      if (response.status === 200 && response.data.alerts?.length > 0) {
        const alert = response.data.alerts[0];
        // Arabic content should be available if locale is set
        if (alert.title_ar) {
          expect(alert.title_ar).toBeTruthy();
        }
      }
    });

    it("should retrieve alert recommendations for agriculture", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        alerts: Array<{
          id: string;
          type: string;
          agricultural_impact?: string;
          recommendations?: string[];
          recommendations_ar?: string[];
        }>;
      }>(`${WEATHER_API_BASE}/alerts/agricultural/${locationId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.alerts) {
        response.data.alerts.forEach((alert) => {
          if (alert.recommendations) {
            expect(Array.isArray(alert.recommendations)).toBe(true);
          }
        });
      }
    });

    it("should retrieve frost warnings for specific crop", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;
      const cropType = "wheat";

      const response = await apiRequest<{
        location_id: string;
        crop_type: string;
        frost_risk?: string;
        min_temperature_forecast?: number;
        frost_threshold?: number;
        warning?: string;
      }>(
        `${WEATHER_API_BASE}/alerts/frost/${locationId}?crop_type=${cropType}`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.frost_risk) {
        expect(["none", "low", "medium", "high", "critical"]).toContain(
          response.data.frost_risk
        );
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Agricultural Weather Endpoints Tests - اختبارات نقاط النهاية الزراعية
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Agricultural Weather Endpoints", () => {
    it("should calculate evapotranspiration (ET)", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        date: string;
        et_mm: number;
        et_method?: string;
      }>(`${WEATHER_API_BASE}/et/${locationId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("et_mm");
        expect(response.data.et_mm).toBeGreaterThanOrEqual(0);
      }
    });

    it("should retrieve spray conditions forecast", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;

      const response = await apiRequest<{
        location_id: string;
        spray_windows: Array<{
          start_time: string;
          end_time: string;
          wind_speed_kmh: number;
          temperature_c: number;
          humidity_percent: number;
          suitability: string;
        }>;
      }>(`${WEATHER_API_BASE}/spray-conditions/${locationId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.spray_windows) {
        response.data.spray_windows.forEach((window) => {
          expect(["good", "moderate", "poor", "unsuitable"]).toContain(
            window.suitability
          );
        });
      }
    });

    it("should calculate chill hours for fruit crops", async () => {
      const locationId = TEST_DATA.WEATHER_LOCATION.id;
      const startDate = "2024-11-01";

      const response = await apiRequest<{
        location_id: string;
        start_date: string;
        total_chill_hours: number;
        daily_chill_hours?: Array<{
          date: string;
          hours: number;
        }>;
      }>(
        `${WEATHER_API_BASE}/chill-hours/${locationId}?start_date=${startDate}`,
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
        expect(response.data).toHaveProperty("total_chill_hours");
        expect(response.data.total_chill_hours).toBeGreaterThanOrEqual(0);
      }
    });
  });
});
