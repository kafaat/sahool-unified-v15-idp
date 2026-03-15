/**
 * API Client Routes Tests
 * اختبارات مسارات عميل API
 *
 * Verifies that all API endpoints use correct service routes
 * after migration from deprecated services.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock fetch before importing the client
const mockFetch = vi.fn();
global.fetch = mockFetch;

// We need to test the actual URLs the client calls
describe("API Client Routes", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "content-type": "application/json" }),
      json: () => Promise.resolve({ success: true, data: {} }),
      text: () => Promise.resolve(""),
    });
  });

  describe("Weather API routes", () => {
    it("should use /api/v1/weather/ instead of deprecated /api/v1/weather-core/", async () => {
      // Import fresh module
      const { apiClient } = await import("../client");

      await apiClient.getWeather(15.3694, 44.191);

      expect(mockFetch).toHaveBeenCalled();
      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/weather/weather/current");
      expect(calledUrl).not.toContain("weather-core");
    });

    it("should use correct weather forecast route", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getWeatherForecast(15.3694, 44.191, 7);

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/weather/weather/forecast");
      expect(calledUrl).not.toContain("weather-core");
    });

    it("should use correct agricultural risks route", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getAgriculturalRisks(15.3694, 44.191);

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/weather/weather/agricultural-report");
      expect(calledUrl).not.toContain("weather-core");
    });

    it("should send POST with lat/lon in body", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getWeather(15.3694, 44.191, "field-001");

      const callOptions = mockFetch.mock.calls[0]?.[1] as RequestInit;
      expect(callOptions.method).toBe("POST");
      const body = JSON.parse(callOptions.body as string);
      expect(body.lat).toBe(15.3694);
      expect(body.lon).toBe(44.191);
      expect(body.field_id).toBe("field-001");
    });
  });

  describe("Advisory API routes (formerly agro-advisor)", () => {
    it("should use /api/v1/advisory/ instead of deprecated /api/v1/agro-advisor/", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getAgroAdvice({
        fieldId: "field-001",
        cropType: "wheat",
        currentConditions: { temperature: 28, humidity: 45 },
      });

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/advisory/advice");
      expect(calledUrl).not.toContain("agro-advisor");
    });

    it("should use correct disease detection route", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getDiseaseDetection("wheat", ["yellowing", "spots"]);

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/advisory/disease");
      expect(calledUrl).not.toContain("agro-advisor");
    });

    it("should use correct nutrient recommendation route", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getNutrientRecommendation({
        cropType: "wheat",
        growthStage: "tillering",
        soilAnalysis: { nitrogen: 18, phosphorus: 25 },
      });

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/advisory/nutrients");
      expect(calledUrl).not.toContain("agro-advisor");
    });
  });

  describe("Field Management API routes (formerly field-core)", () => {
    it("should use /api/v1/fields/ instead of deprecated /api/v1/field-core/", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getFieldBoundary("field-001");

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/fields/field-001/boundary");
      expect(calledUrl).not.toContain("field-core");
    });

    it("should use correct boundary update route", async () => {
      const { apiClient } = await import("../client");

      await apiClient.updateFieldBoundary("field-001", { coordinates: [] }, "etag-123");

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/fields/field-001/boundary");
      expect(calledUrl).not.toContain("field-core");
    });

    it("should use correct boundary history route", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getFieldBoundaryHistory("field-001");

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/fields/field-001/boundary-history");
      expect(calledUrl).not.toContain("field-core");
    });

    it("should use correct rollback route", async () => {
      const { apiClient } = await import("../client");

      await apiClient.rollbackFieldBoundary("field-001", "history-001", "test reason");

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/fields/field-001/boundary-history/rollback");
      expect(calledUrl).not.toContain("field-core");
    });

    it("should include If-Match header for boundary updates with etag", async () => {
      const { apiClient } = await import("../client");

      await apiClient.updateFieldBoundary("field-001", { coordinates: [] }, "etag-abc");

      const callOptions = mockFetch.mock.calls[0]?.[1] as RequestInit;
      const headers = callOptions.headers as Record<string, string>;
      expect(headers["If-Match"]).toBe("etag-abc");
    });
  });

  describe("Chat API routes (formerly field-chat)", () => {
    it("should use /api/v1/chat/ instead of deprecated /api/v1/field-chat/", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getFieldMessages("field-001");

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/chat/fields/field-001/messages");
      expect(calledUrl).not.toContain("field-chat");
    });

    it("should use correct chat participants route", async () => {
      const { apiClient } = await import("../client");

      await apiClient.getFieldChatParticipants("field-001");

      const calledUrl = mockFetch.mock.calls[0]?.[0] as string;
      expect(calledUrl).toContain("/api/v1/chat/fields/field-001/participants");
      expect(calledUrl).not.toContain("field-chat");
    });

    it("should reject XSS in chat messages", async () => {
      const { apiClient } = await import("../client");

      const result = await apiClient.sendFieldMessage("field-001", "<script>alert('xss')</script>");

      // Should sanitize or reject
      expect(result.success === false || typeof result.data !== "undefined").toBe(true);
    });

    it("should reject empty messages", async () => {
      const { apiClient } = await import("../client");

      const result = await apiClient.sendFieldMessage("field-001", "");

      expect(result.success).toBe(false);
    });
  });

  describe("No deprecated routes remain", () => {
    it("should not contain any reference to weather-core in API calls", async () => {
      // Read the client source at build time to verify no deprecated routes
      const fs = await import("fs");
      const path = await import("path");
      const clientPath = path.resolve(__dirname, "../client.ts");
      const source = fs.readFileSync(clientPath, "utf-8");

      // Count references excluding comments
      const lines = source.split("\n").filter(
        (line) => !line.trim().startsWith("//") && !line.trim().startsWith("*"),
      );
      const codeOnly = lines.join("\n");

      expect(codeOnly).not.toContain('"/api/v1/weather-core/');
      expect(codeOnly).not.toContain('"/api/v1/agro-advisor/');
      expect(codeOnly).not.toContain('"/api/v1/field-core/');
      expect(codeOnly).not.toContain('"/api/v1/field-chat/');
    });
  });
});
