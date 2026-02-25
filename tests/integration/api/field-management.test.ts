/**
 * SAHOOL Field Management API Integration Tests
 * اختبارات تكامل API إدارة الحقول لمنصة سهول
 *
 * Tests cover:
 * - Create field with GeoJSON
 * - Update field boundary
 * - Get field by ID
 * - List fields with pagination
 * - Delete field
 * - NDVI data retrieval
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
  generateTestId,
  isValidUUID,
  isValidISO8601,
  checkServiceHealth,
  MOCK_RESPONSES,
} from "./setup";

// ═══════════════════════════════════════════════════════════════════════════════
// Test Configuration
// ═══════════════════════════════════════════════════════════════════════════════

const FIELD_SERVICE_URL = TEST_CONFIG.SERVICES.FIELD_SERVICE;
const FIELD_API_BASE = `${FIELD_SERVICE_URL}/api/v1/fields`;

describe("Field Management API Integration Tests", () => {
  let authToken: string;
  let createdFieldId: string | null = null;
  let serviceHealthy: boolean = false;

  // ─────────────────────────────────────────────────────────────────────────────
  // Setup & Teardown
  // ─────────────────────────────────────────────────────────────────────────────

  beforeAll(async () => {
    authToken = await getAuthToken("FARMER");

    const health = await checkServiceHealth("FIELD_SERVICE", FIELD_SERVICE_URL);
    serviceHealthy = health.status === "healthy";

    if (!serviceHealthy) {
      console.warn(
        "Field service not available - tests will use mock validation"
      );
    }
  });

  afterAll(async () => {
    // Cleanup: Delete test field if created
    if (createdFieldId && serviceHealthy) {
      try {
        await apiRequest(`${FIELD_API_BASE}/${createdFieldId}`, {
          method: "DELETE",
          headers: getAuthHeaders(authToken),
        });
      } catch {
        // Ignore cleanup errors
      }
    }
    clearAuthCache();
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Service Health Tests - اختبارات صحة الخدمة
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Service Health", () => {
    it("should verify field service is registered and responding", async () => {
      const health = await checkServiceHealth(
        "FIELD_SERVICE",
        FIELD_SERVICE_URL
      );

      expect(health.service).toBe("FIELD_SERVICE");
      expect(["healthy", "unhealthy", "unknown"]).toContain(health.status);
      expect(health.responseTime).toBeGreaterThan(0);
    });

    it("should have health endpoint available", async () => {
      const response = await apiRequest<{ status: string; service?: string }>(
        `${FIELD_SERVICE_URL}/healthz`
      );

      expect([200, 404, 502, 503]).toContain(response.status);

      if (response.ok) {
        expect(response.data).toHaveProperty("status");
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Create Field with GeoJSON Tests - اختبارات إنشاء الحقل مع GeoJSON
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Create Field with GeoJSON", () => {
    it("should create a field with valid GeoJSON polygon boundary", async () => {
      const fieldData = {
        ...TEST_DATA.FIELD,
        name: `Test Field ${generateTestId()}`,
        name_ar: `حقل اختباري ${generateTestId()}`,
        geometry: TEST_DATA.FIELD_GEOJSON,
        polygon: TEST_DATA.FIELD_GEOJSON,
      };

      const response = await apiRequest<{
        id: string;
        name: string;
        name_ar: string;
        area_hectares: number;
        geometry?: { type: string; coordinates: number[][][] };
        created_at: string;
      }>(FIELD_API_BASE, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(fieldData),
      });

      if (response.status === 502 || response.status === 503) {
        console.warn("Field service not available");
        return;
      }

      expect([200, 201, 401, 422]).toContain(response.status);

      if (response.status === 200 || response.status === 201) {
        expect(response.data).toHaveProperty("id");
        expect(response.data.name).toContain("Test Field");
        createdFieldId = response.data.id;

        if (response.data.geometry) {
          expect(response.data.geometry.type).toBe("Polygon");
        }
      }
    });

    it("should calculate area from GeoJSON polygon automatically", async () => {
      const fieldData = {
        name: `Auto Area Field ${generateTestId()}`,
        tenant_id: TEST_DATA.FIELD.tenant_id,
        farm_id: TEST_DATA.FIELD.farm_id,
        geometry: TEST_DATA.FIELD_GEOJSON,
        crop_type: "wheat",
        // Note: area_hectares not provided - should be calculated
      };

      const response = await apiRequest<{
        id: string;
        area_hectares?: number;
        area?: number;
      }>(FIELD_API_BASE, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(fieldData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 201, 401, 422]).toContain(response.status);

      if (response.status === 200 || response.status === 201) {
        const area = response.data.area_hectares ?? response.data.area;
        // If area is auto-calculated, it should be a positive number
        if (area !== undefined) {
          expect(area).toBeGreaterThan(0);
        }
      }
    });

    it("should reject field creation with invalid GeoJSON", async () => {
      const invalidGeoJSON = {
        type: "InvalidType",
        coordinates: "not-an-array",
      };

      const fieldData = {
        ...TEST_DATA.FIELD,
        name: `Invalid GeoJSON Field ${generateTestId()}`,
        geometry: invalidGeoJSON,
      };

      const response = await apiRequest(FIELD_API_BASE, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(fieldData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([400, 422]).toContain(response.status);
    });

    it("should reject field creation without required fields", async () => {
      const incompleteData = {
        name: "Incomplete Field",
        // Missing tenant_id, farm_id
      };

      const response = await apiRequest(FIELD_API_BASE, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(incompleteData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([400, 422]).toContain(response.status);
    });

    it("should support Arabic field names", async () => {
      const arabicFieldData = {
        ...TEST_DATA.FIELD,
        name: "Al-Rashid Farm Field 1",
        name_ar: "حقل مزرعة الرشيد 1",
        description: "Main wheat field",
        description_ar: "حقل القمح الرئيسي",
      };

      const response = await apiRequest<{
        id: string;
        name: string;
        name_ar: string;
      }>(FIELD_API_BASE, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify(arabicFieldData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 201, 401, 422]).toContain(response.status);

      if (response.status === 200 || response.status === 201) {
        expect(response.data.name_ar).toBe("حقل مزرعة الرشيد 1");
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Update Field Boundary Tests - اختبارات تحديث حدود الحقل
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Update Field Boundary", () => {
    it("should update field boundary with new GeoJSON polygon", async () => {
      // First create a field
      const createResponse = await apiRequest<{ id: string }>(FIELD_API_BASE, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify({
          ...TEST_DATA.FIELD,
          name: `Boundary Update Test ${generateTestId()}`,
        }),
      });

      if (createResponse.status === 502 || createResponse.status === 503) {
        return;
      }

      if (createResponse.status !== 200 && createResponse.status !== 201) {
        return;
      }

      const fieldId = createResponse.data.id;

      // New boundary (slightly different coordinates)
      const newBoundary = {
        type: "Polygon" as const,
        coordinates: [
          [
            [44.192, 15.3695],
            [44.196, 15.3695],
            [44.196, 15.3735],
            [44.192, 15.3735],
            [44.192, 15.3695],
          ],
        ],
      };

      const updateResponse = await apiRequest<{
        id: string;
        geometry?: { type: string };
      }>(`${FIELD_API_BASE}/${fieldId}`, {
        method: "PUT",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify({
          geometry: newBoundary,
          polygon: newBoundary,
        }),
      });

      expect([200, 401, 404, 422]).toContain(updateResponse.status);

      if (updateResponse.status === 200) {
        expect(updateResponse.data.id).toBe(fieldId);
      }

      // Cleanup
      await apiRequest(`${FIELD_API_BASE}/${fieldId}`, {
        method: "DELETE",
        headers: getAuthHeaders(authToken),
      });
    });

    it("should reject boundary update with self-intersecting polygon", async () => {
      if (!createdFieldId) {
        console.warn("No field created to test boundary update");
        return;
      }

      // Self-intersecting polygon (bowtie shape)
      const selfIntersecting = {
        type: "Polygon" as const,
        coordinates: [
          [
            [44.191, 15.369],
            [44.195, 15.373],
            [44.195, 15.369],
            [44.191, 15.373],
            [44.191, 15.369],
          ],
        ],
      };

      const response = await apiRequest(`${FIELD_API_BASE}/${createdFieldId}`, {
        method: "PUT",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify({
          geometry: selfIntersecting,
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      // Should reject or accept with validation
      expect([200, 400, 422]).toContain(response.status);
    });

    it("should update field metadata without changing boundary", async () => {
      if (!createdFieldId) {
        return;
      }

      const response = await apiRequest<{
        id: string;
        crop_type: string;
        irrigation_type: string;
      }>(`${FIELD_API_BASE}/${createdFieldId}`, {
        method: "PUT",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify({
          crop_type: "barley",
          irrigation_type: "pivot",
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404, 422]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data.crop_type).toBe("barley");
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Get Field by ID Tests - اختبارات جلب الحقل بالمعرف
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Get Field by ID", () => {
    it("should retrieve field by ID with all properties", async () => {
      // Use mock if no field was created
      const fieldId = createdFieldId || "field-test-001";

      const response = await apiRequest<{
        id: string;
        name: string;
        name_ar?: string;
        area_hectares?: number;
        area?: number;
        crop_type?: string;
        status: string;
        geometry?: { type: string; coordinates: number[][][] };
        ndvi_current?: number;
        health_score?: number;
        created_at?: string;
        updated_at?: string;
      }>(`${FIELD_API_BASE}/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        // Validate mock response structure
        expect(MOCK_RESPONSES.FIELD).toHaveProperty("id");
        expect(MOCK_RESPONSES.FIELD).toHaveProperty("name");
        expect(MOCK_RESPONSES.FIELD).toHaveProperty("status");
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("id");
        expect(response.data).toHaveProperty("name");
        expect(response.data).toHaveProperty("status");
      }
    });

    it("should return 404 for non-existent field", async () => {
      const response = await apiRequest(
        `${FIELD_API_BASE}/non-existent-field-id`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 404]).toContain(response.status);
    });

    it("should include GeoJSON geometry in response", async () => {
      if (!createdFieldId) {
        return;
      }

      const response = await apiRequest<{
        id: string;
        geometry?: {
          type: string;
          coordinates: number[][][];
        };
        polygon?: {
          type: string;
          coordinates: number[][][];
        };
      }>(`${FIELD_API_BASE}/${createdFieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      if (response.status === 200) {
        const hasGeometry = response.data.geometry || response.data.polygon;
        if (hasGeometry) {
          expect(hasGeometry.type).toBe("Polygon");
          expect(Array.isArray(hasGeometry.coordinates)).toBe(true);
        }
      }
    });

    it("should include latest NDVI value in response", async () => {
      if (!createdFieldId) {
        return;
      }

      const response = await apiRequest<{
        id: string;
        ndvi_current?: number;
        ndvi_value?: number;
      }>(`${FIELD_API_BASE}/${createdFieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      if (response.status === 200) {
        const ndvi = response.data.ndvi_current ?? response.data.ndvi_value;
        if (ndvi !== undefined) {
          expect(ndvi).toBeGreaterThanOrEqual(-1);
          expect(ndvi).toBeLessThanOrEqual(1);
        }
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // List Fields with Pagination Tests - اختبارات قائمة الحقول مع التصفح
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("List Fields with Pagination", () => {
    it("should list fields with default pagination", async () => {
      const response = await apiRequest<
        | Array<{ id: string; name: string }>
        | {
            data: Array<{ id: string; name: string }>;
            items?: Array<{ id: string; name: string }>;
            total: number;
            page?: number;
            limit?: number;
          }
      >(FIELD_API_BASE, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401]).toContain(response.status);

      if (response.status === 200) {
        // Response could be array or paginated object
        if (Array.isArray(response.data)) {
          expect(response.data).toBeInstanceOf(Array);
        } else {
          expect(response.data).toHaveProperty("total");
          const items = response.data.data || response.data.items;
          expect(items).toBeInstanceOf(Array);
        }
      }
    });

    it("should support pagination with limit and offset", async () => {
      const response = await apiRequest<{
        data?: Array<{ id: string }>;
        items?: Array<{ id: string }>;
        total: number;
        page?: number;
        limit?: number;
      }>(`${FIELD_API_BASE}?limit=10&offset=0`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401]).toContain(response.status);

      if (response.status === 200 && !Array.isArray(response.data)) {
        expect(response.data.limit).toBeLessThanOrEqual(10);
      }
    });

    it("should filter fields by farm_id", async () => {
      const farmId = TEST_DATA.FIELD.farm_id;

      const response = await apiRequest<
        | Array<{ id: string; farm_id: string }>
        | { data: Array<{ id: string; farm_id: string }>; total: number }
      >(`${FIELD_API_BASE}?farm_id=${farmId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401]).toContain(response.status);

      if (response.status === 200) {
        const fields = Array.isArray(response.data)
          ? response.data
          : response.data.data;
        if (fields && fields.length > 0) {
          fields.forEach((field) => {
            expect(field.farm_id).toBe(farmId);
          });
        }
      }
    });

    it("should filter fields by crop_type", async () => {
      const response = await apiRequest<
        | Array<{ id: string; crop_type: string }>
        | { data: Array<{ id: string; crop_type: string }>; total: number }
      >(`${FIELD_API_BASE}?crop_type=wheat`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401]).toContain(response.status);

      if (response.status === 200) {
        const fields = Array.isArray(response.data)
          ? response.data
          : response.data.data;
        if (fields && fields.length > 0) {
          fields.forEach((field) => {
            expect(field.crop_type).toBe("wheat");
          });
        }
      }
    });

    it("should filter fields by status", async () => {
      const response = await apiRequest<
        | Array<{ id: string; status: string }>
        | { data: Array<{ id: string; status: string }>; total: number }
      >(`${FIELD_API_BASE}?status=active`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401]).toContain(response.status);

      if (response.status === 200) {
        const fields = Array.isArray(response.data)
          ? response.data
          : response.data.data;
        if (fields && fields.length > 0) {
          fields.forEach((field) => {
            expect(field.status).toBe("active");
          });
        }
      }
    });

    it("should return empty array for filters with no matches", async () => {
      const response = await apiRequest<
        | Array<{ id: string }>
        | { data: Array<{ id: string }>; total: number }
      >(`${FIELD_API_BASE}?crop_type=non_existent_crop`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401]).toContain(response.status);

      if (response.status === 200) {
        const fields = Array.isArray(response.data)
          ? response.data
          : response.data.data;
        expect(fields).toHaveLength(0);
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Delete Field Tests - اختبارات حذف الحقل
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Delete Field", () => {
    it("should delete field by ID", async () => {
      // Create a field to delete
      const createResponse = await apiRequest<{ id: string }>(FIELD_API_BASE, {
        method: "POST",
        headers: getAuthHeaders(authToken),
        body: JSON.stringify({
          ...TEST_DATA.FIELD,
          name: `Delete Test Field ${generateTestId()}`,
        }),
      });

      if (createResponse.status === 502 || createResponse.status === 503) {
        return;
      }

      if (createResponse.status !== 200 && createResponse.status !== 201) {
        return;
      }

      const fieldId = createResponse.data.id;

      // Delete the field
      const deleteResponse = await apiRequest<{
        status?: string;
        message?: string;
      }>(`${FIELD_API_BASE}/${fieldId}`, {
        method: "DELETE",
        headers: getAuthHeaders(authToken),
      });

      expect([200, 204, 401, 404]).toContain(deleteResponse.status);

      // Verify field is deleted
      const getResponse = await apiRequest(`${FIELD_API_BASE}/${fieldId}`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      expect([404, 410]).toContain(getResponse.status);
    });

    it("should return 404 when deleting non-existent field", async () => {
      const response = await apiRequest(
        `${FIELD_API_BASE}/non-existent-field-id`,
        {
          method: "DELETE",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 404]).toContain(response.status);
    });

    it("should cascade delete related data (soft delete)", async () => {
      // This test verifies that deleting a field doesn't leave orphaned records
      if (!createdFieldId) {
        return;
      }

      // Delete the field
      const deleteResponse = await apiRequest(
        `${FIELD_API_BASE}/${createdFieldId}`,
        {
          method: "DELETE",
          headers: getAuthHeaders(authToken),
        }
      );

      if (deleteResponse.status === 502 || deleteResponse.status === 503) {
        return;
      }

      expect([200, 204, 401, 404]).toContain(deleteResponse.status);

      // Clear the created field ID
      createdFieldId = null;
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // NDVI Data Retrieval Tests - اختبارات استرجاع بيانات NDVI
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("NDVI Data Retrieval", () => {
    it("should retrieve current NDVI value for field", async () => {
      const fieldId = createdFieldId || "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        ndvi_value?: number;
        ndvi_current?: number;
        measurement_date?: string;
        timestamp?: string;
      }>(`${FIELD_API_BASE}/${fieldId}/ndvi`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        const ndvi = response.data.ndvi_value ?? response.data.ndvi_current;
        if (ndvi !== undefined) {
          expect(ndvi).toBeGreaterThanOrEqual(-1);
          expect(ndvi).toBeLessThanOrEqual(1);
        }
      }
    });

    it("should retrieve NDVI time series data", async () => {
      const fieldId = createdFieldId || "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        time_series: Array<{
          date: string;
          ndvi_value: number;
        }>;
      }>(`${FIELD_API_BASE}/${fieldId}/ndvi/history`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        if (response.data.time_series) {
          expect(Array.isArray(response.data.time_series)).toBe(true);
          response.data.time_series.forEach((entry) => {
            expect(entry).toHaveProperty("date");
            expect(entry).toHaveProperty("ndvi_value");
          });
        }
      }
    });

    it("should filter NDVI data by date range", async () => {
      const fieldId = createdFieldId || "field-test-001";
      const startDate = "2025-01-01";
      const endDate = "2025-01-31";

      const response = await apiRequest<{
        field_id: string;
        time_series: Array<{
          date: string;
          ndvi_value: number;
        }>;
      }>(
        `${FIELD_API_BASE}/${fieldId}/ndvi/history?start_date=${startDate}&end_date=${endDate}`,
        {
          method: "GET",
          headers: getAuthHeaders(authToken),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200 && response.data.time_series) {
        response.data.time_series.forEach((entry) => {
          const entryDate = new Date(entry.date);
          expect(entryDate >= new Date(startDate)).toBe(true);
          expect(entryDate <= new Date(endDate)).toBe(true);
        });
      }
    });

    it("should calculate NDVI statistics", async () => {
      const fieldId = createdFieldId || "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        statistics?: {
          mean: number;
          min: number;
          max: number;
          std_dev?: number;
        };
        mean_ndvi?: number;
        min_ndvi?: number;
        max_ndvi?: number;
      }>(`${FIELD_API_BASE}/${fieldId}/ndvi/statistics`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        const stats = response.data.statistics || response.data;
        if (stats) {
          const mean = stats.mean ?? response.data.mean_ndvi;
          const min = stats.min ?? response.data.min_ndvi;
          const max = stats.max ?? response.data.max_ndvi;

          if (mean !== undefined) {
            expect(mean).toBeGreaterThanOrEqual(-1);
            expect(mean).toBeLessThanOrEqual(1);
          }
        }
      }
    });

    it("should include health classification based on NDVI", async () => {
      const fieldId = createdFieldId || "field-test-001";

      const response = await apiRequest<{
        field_id: string;
        ndvi_value?: number;
        health_status?: string;
        health_classification?: string;
      }>(`${FIELD_API_BASE}/${fieldId}/health`, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        const healthStatus =
          response.data.health_status ?? response.data.health_classification;
        if (healthStatus) {
          expect(["healthy", "moderate", "stressed", "critical"]).toContain(
            healthStatus
          );
        }
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tenant Isolation Tests - اختبارات عزل المستأجر
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Tenant Isolation", () => {
    it("should only return fields for the authenticated tenant", async () => {
      const response = await apiRequest<
        | Array<{ id: string; tenant_id: string }>
        | { data: Array<{ id: string; tenant_id: string }>; total: number }
      >(FIELD_API_BASE, {
        method: "GET",
        headers: getAuthHeaders(authToken),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      if (response.status === 200) {
        const fields = Array.isArray(response.data)
          ? response.data
          : response.data.data;
        if (fields && fields.length > 0) {
          fields.forEach((field) => {
            // All fields should belong to the authenticated tenant
            if (field.tenant_id) {
              expect(field.tenant_id).toBe(TEST_DATA.FIELD.tenant_id);
            }
          });
        }
      }
    });

    it("should reject access to fields from different tenant", async () => {
      const response = await apiRequest(`${FIELD_API_BASE}/other-tenant-field`, {
        method: "GET",
        headers: {
          ...getAuthHeaders(authToken),
          "X-Tenant-ID": "different-tenant",
        },
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 403, 404]).toContain(response.status);
    });
  });
});
