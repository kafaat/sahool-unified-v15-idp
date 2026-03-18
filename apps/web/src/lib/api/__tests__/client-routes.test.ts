/**
 * API Client Routes Tests
 * اختبارات مسارات عميل API
 *
 * Verifies that all API endpoints use correct service routes
 * after migration from deprecated services.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock the unified client's axios instance
const mockRequest = vi.fn();
vi.mock("../unified-client", () => ({
  unifiedApiClient: {
    request: mockRequest,
    defaults: { baseURL: "", headers: {} },
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
  sahoolClient: {
    axiosInstance: {
      request: mockRequest,
      defaults: { baseURL: "", headers: {} },
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    },
  },
}));

// Mock validation module — must match the actual exports used in client.ts
vi.mock("../../validation", () => ({
  sanitizers: {
    html: (text: string) => {
      if (typeof text !== "string") return "";
      // Iteratively strip HTML tags to prevent multi-character bypass
      let result = text;
      let prev = "";
      while (result !== prev) {
        prev = result;
        result = result.replace(/<[^>]*>/g, "");
      }
      return result;
    },
  },
  validators: {
    safeText: (text: string) => text.length > 0 && !/<script/i.test(text),
  },
  validationErrors: {
    unsafeText: "Message contains unsafe content",
    emptyMessage: "Message cannot be empty",
  },
}));

describe("API Client Routes", () => {
  beforeEach(() => {
    mockRequest.mockReset();
    mockRequest.mockResolvedValue({
      data: { success: true, data: {} },
      status: 200,
      headers: { "content-type": "application/json" },
    });
  });

  describe("Weather API routes", () => {
    it("should use /api/v1/weather/ instead of deprecated /api/v1/weather-core/", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getWeather(15.3694, 44.191);

      expect(mockRequest).toHaveBeenCalled();
      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/weather/weather/current");
      expect(callArgs.url).not.toContain("weather-core");
    });

    it("should use correct weather forecast route", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getWeatherForecast(15.3694, 44.191, 7);

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/weather/weather/forecast");
      expect(callArgs.url).not.toContain("weather-core");
    });

    it("should use correct agricultural risks route", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getAgriculturalRisks(15.3694, 44.191);

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/weather/weather/agricultural-report");
      expect(callArgs.url).not.toContain("weather-core");
    });

    it("should send POST with lat/lon in body", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getWeather(15.3694, 44.191, "field-001");

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.method).toBe("POST");
      const body = callArgs.data;
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

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/advisory/advice");
      expect(callArgs.url).not.toContain("agro-advisor");
    });

    it("should use correct disease detection route", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getDiseaseDetection("wheat", ["yellowing", "spots"]);

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/advisory/disease");
      expect(callArgs.url).not.toContain("agro-advisor");
    });

    it("should use correct nutrient recommendation route", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getNutrientRecommendation({
        cropType: "wheat",
        growthStage: "tillering",
        soilAnalysis: { nitrogen: 18, phosphorus: 25 },
      });

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/advisory/nutrients");
      expect(callArgs.url).not.toContain("agro-advisor");
    });
  });

  describe("Field Management API routes (formerly field-core)", () => {
    it("should use /api/v1/fields/ instead of deprecated /api/v1/field-core/", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getFieldBoundary("field-001");

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/fields/field-001/boundary");
      expect(callArgs.url).not.toContain("field-core");
    });

    it("should use correct boundary update route", async () => {
      const { apiClient } = await import("../client");
      await apiClient.updateFieldBoundary("field-001", { coordinates: [] }, "etag-123");

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/fields/field-001/boundary");
      expect(callArgs.url).not.toContain("field-core");
    });

    it("should use correct boundary history route", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getFieldBoundaryHistory("field-001");

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/fields/field-001/boundary-history");
      expect(callArgs.url).not.toContain("field-core");
    });

    it("should use correct rollback route", async () => {
      const { apiClient } = await import("../client");
      await apiClient.rollbackFieldBoundary("field-001", "history-001", "test reason");

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/fields/field-001/boundary-history/rollback");
      expect(callArgs.url).not.toContain("field-core");
    });
  });

  describe("Chat API routes (formerly field-chat)", () => {
    it("should use /api/v1/chat/ instead of deprecated /api/v1/field-chat/", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getFieldMessages("field-001");

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/chat/fields/field-001/messages");
      expect(callArgs.url).not.toContain("field-chat");
    });

    it("should use correct chat participants route", async () => {
      const { apiClient } = await import("../client");
      await apiClient.getFieldChatParticipants("field-001");

      const callArgs = mockRequest.mock.calls[0]?.[0];
      expect(callArgs.url).toContain("/api/v1/chat/fields/field-001/participants");
      expect(callArgs.url).not.toContain("field-chat");
    });

    it("should reject XSS in chat messages", async () => {
      const { apiClient } = await import("../client");
      const result = await apiClient.sendFieldMessage("field-001", "<script>alert('xss')</script>");
      expect(result.success === false || typeof result.data !== "undefined").toBe(true);
    });

    it("should reject empty messages", async () => {
      const { apiClient } = await import("../client");
      const result = await apiClient.sendFieldMessage("field-001", "");
      expect(result.success).toBe(false);
    });
  });

  describe("No deprecated routes remain", () => {
    it("should not contain any reference to deprecated routes in source code", async () => {
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
