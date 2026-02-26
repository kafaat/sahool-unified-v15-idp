/**
 * SAHOOL API Integration Test Setup
 * اعداد اختبارات التكامل لـ API
 *
 * This file provides common test utilities, fixtures, and configuration
 * for API integration tests through Kong Gateway.
 */

import { vi, beforeAll, afterAll, beforeEach, afterEach } from "vitest";

// ═══════════════════════════════════════════════════════════════════════════════
// Environment Configuration
// ═══════════════════════════════════════════════════════════════════════════════

export const TEST_CONFIG = {
  // Kong Gateway URL
  KONG_URL: process.env.KONG_URL || "http://localhost:8000",
  KONG_ADMIN_URL: process.env.KONG_ADMIN_URL || "http://localhost:8001",

  // Direct service URLs for testing
  SERVICES: {
    USER_SERVICE: process.env.USER_SERVICE_URL || "http://localhost:3025",
    FIELD_SERVICE:
      process.env.FIELD_SERVICE_URL || "http://localhost:3000",
    WEATHER_SERVICE:
      process.env.WEATHER_SERVICE_URL || "http://localhost:8092",
    IRRIGATION_SERVICE:
      process.env.IRRIGATION_SERVICE_URL || "http://localhost:8094",
    NOTIFICATION_SERVICE:
      process.env.NOTIFICATION_SERVICE_URL || "http://localhost:8110",
    VISION_SERVICE:
      process.env.VISION_SERVICE_URL || "http://localhost:8150",
    CROP_INTELLIGENCE:
      process.env.CROP_INTELLIGENCE_URL || "http://localhost:8095",
    YIELD_ENGINE: process.env.YIELD_ENGINE_URL || "http://localhost:8098",
    ADVISORY_SERVICE:
      process.env.ADVISORY_SERVICE_URL || "http://localhost:8093",
  },

  // Test timeouts
  TIMEOUT: {
    REQUEST: 10000,
    LONG_RUNNING: 30000,
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// Test User Credentials - اعتمادات المستخدم للاختبار
// ═══════════════════════════════════════════════════════════════════════════════

export const TEST_USERS = {
  ADMIN: {
    email: "admin@sahool.test",
    password: "TestAdmin123!",
    role: "admin",
    tenantId: "tenant-test-001",
  },
  FARMER: {
    email: "farmer@sahool.test",
    password: "TestFarmer123!",
    role: "farmer",
    tenantId: "tenant-test-001",
  },
  AGRONOMIST: {
    email: "agronomist@sahool.test",
    password: "TestAgro123!",
    role: "agronomist",
    tenantId: "tenant-test-001",
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// Sample Test Data - بيانات الاختبار
// ═══════════════════════════════════════════════════════════════════════════════

export const TEST_DATA = {
  // Sample GeoJSON field boundary (Al-Rashid Farm, Yemen)
  FIELD_GEOJSON: {
    type: "Polygon" as const,
    coordinates: [
      [
        [44.191, 15.3694],
        [44.195, 15.3694],
        [44.195, 15.3734],
        [44.191, 15.3734],
        [44.191, 15.3694],
      ],
    ],
  },

  // Sample field data
  FIELD: {
    name: "Test Field - Al-Rashid",
    name_ar: "حقل الرشيد للاختبار",
    tenant_id: "tenant-test-001",
    farm_id: "farm-test-001",
    area_hectares: 5.2,
    crop_type: "wheat",
    crop_type_ar: "قمح",
    soil_type: "loamy",
    irrigation_type: "drip",
    status: "active",
  },

  // Sample weather location (Sana'a, Yemen)
  WEATHER_LOCATION: {
    id: "loc-sanaa-001",
    name: "Sana'a",
    name_ar: "صنعاء",
    latitude: 15.3694,
    longitude: 44.191,
    elevation: 2250,
  },

  // Sample irrigation schedule
  IRRIGATION_SCHEDULE: {
    field_id: "field-test-001",
    crop_type: "wheat",
    growth_stage: "tillering",
    soil_moisture_percent: 35,
    et_mm_day: 5.5,
    scheduled_date: new Date().toISOString().split("T")[0],
    duration_minutes: 45,
    amount_mm: 25,
  },

  // Sample notification
  NOTIFICATION: {
    type: "irrigation_reminder",
    priority: "high",
    title: "Irrigation Required",
    title_ar: "مطلوب الري",
    message: "Field Al-Rashid requires irrigation today",
    message_ar: "حقل الرشيد يحتاج للري اليوم",
    recipient_id: "user-test-001",
    field_id: "field-test-001",
  },

  // Sample pest detection image (base64 placeholder)
  PEST_IMAGE: {
    field_id: "field-test-001",
    crop_type: "wheat",
    image_type: "leaf_sample",
    // In real tests, this would be actual base64 image data
    image_base64: "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// HTTP Client Helper
// ═══════════════════════════════════════════════════════════════════════════════

export interface ApiResponse<T = unknown> {
  status: number;
  data: T;
  headers: Record<string, string>;
  ok: boolean;
}

export async function apiRequest<T = unknown>(
  url: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const controller = new AbortController();
  const timeoutId = setTimeout(
    () => controller.abort(),
    TEST_CONFIG.TIMEOUT.REQUEST
  );

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "Accept-Language": "ar,en",
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    let data: T;
    const contentType = response.headers.get("content-type");

    if (contentType?.includes("application/json")) {
      data = await response.json();
    } else {
      data = (await response.text()) as unknown as T;
    }

    const headers: Record<string, string> = {};
    response.headers.forEach((value, key) => {
      headers[key] = value;
    });

    return {
      status: response.status,
      data,
      headers,
      ok: response.ok,
    };
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error && error.name === "AbortError") {
      throw new Error(`Request timeout after ${TEST_CONFIG.TIMEOUT.REQUEST}ms`);
    }

    // Return a 503 response for connection errors (service not running)
    // This allows tests to handle unavailable services gracefully
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    if (
      errorMessage.includes("fetch failed") ||
      errorMessage.includes("ECONNREFUSED") ||
      errorMessage.includes("ECONNRESET") ||
      errorMessage.includes("ENOTFOUND")
    ) {
      return {
        status: 503,
        data: {
          error: "Service unavailable",
          message: errorMessage,
        } as unknown as T,
        headers: {},
        ok: false,
      };
    }

    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Authentication Helpers
// ═══════════════════════════════════════════════════════════════════════════════

export interface AuthTokens {
  accessToken: string;
  refreshToken?: string;
  expiresAt: string;
}

let cachedTokens: Map<string, AuthTokens> = new Map();

export async function getAuthToken(
  userType: keyof typeof TEST_USERS = "FARMER"
): Promise<string> {
  const cached = cachedTokens.get(userType);
  if (cached && new Date(cached.expiresAt) > new Date()) {
    return cached.accessToken;
  }

  const user = TEST_USERS[userType];
  const response = await apiRequest<{
    token: string;
    refresh_token?: string;
    expires_at: string;
  }>(`${TEST_CONFIG.SERVICES.USER_SERVICE}/api/v1/auth/login`, {
    method: "POST",
    body: JSON.stringify({
      email: user.email,
      password: user.password,
    }),
  });

  if (!response.ok) {
    // Return mock token for testing when auth service is not available
    return "test-jwt-token-for-integration-tests";
  }

  const tokens: AuthTokens = {
    accessToken: response.data.token,
    refreshToken: response.data.refresh_token,
    expiresAt: response.data.expires_at,
  };

  cachedTokens.set(userType, tokens);
  return tokens.accessToken;
}

export function getAuthHeaders(token: string): Record<string, string> {
  return {
    Authorization: `Bearer ${token}`,
    "X-Tenant-ID": TEST_USERS.FARMER.tenantId,
  };
}

export function clearAuthCache(): void {
  cachedTokens.clear();
}

// ═══════════════════════════════════════════════════════════════════════════════
// Service Health Check Helpers
// ═══════════════════════════════════════════════════════════════════════════════

export interface ServiceHealth {
  service: string;
  status: "healthy" | "unhealthy" | "unknown";
  responseTime: number;
  version?: string;
  error?: string;
}

export async function checkServiceHealth(
  serviceName: string,
  serviceUrl: string
): Promise<ServiceHealth> {
  const startTime = Date.now();

  try {
    const response = await apiRequest<{
      status: string;
      version?: string;
      service?: string;
    }>(`${serviceUrl}/healthz`);

    return {
      service: serviceName,
      status: response.ok ? "healthy" : "unhealthy",
      responseTime: Date.now() - startTime,
      version: response.data?.version,
    };
  } catch (error) {
    return {
      service: serviceName,
      status: "unknown",
      responseTime: Date.now() - startTime,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

export async function checkKongHealth(): Promise<boolean> {
  try {
    const response = await apiRequest(`${TEST_CONFIG.KONG_ADMIN_URL}/status`);
    return response.ok;
  } catch {
    return false;
  }
}

export async function checkAllServices(): Promise<ServiceHealth[]> {
  const healthChecks = Object.entries(TEST_CONFIG.SERVICES).map(
    ([name, url]) => checkServiceHealth(name, url)
  );

  return Promise.all(healthChecks);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Test Utilities
// ═══════════════════════════════════════════════════════════════════════════════

export function generateTestId(prefix: string = "test"): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function isValidUUID(str: string): boolean {
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export function isValidISO8601(str: string): boolean {
  const date = new Date(str);
  return !isNaN(date.getTime());
}

// ═══════════════════════════════════════════════════════════════════════════════
// Mock Response Helpers (for when services are not available)
// ═══════════════════════════════════════════════════════════════════════════════

export const MOCK_RESPONSES = {
  AUTH: {
    LOGIN: {
      token: "mock-jwt-token-for-testing",
      refresh_token: "mock-refresh-token",
      expires_at: new Date(Date.now() + 3600000).toISOString(),
      user: {
        id: "user-test-001",
        email: "farmer@sahool.test",
        name: "Test Farmer",
        name_ar: "مزارع اختباري",
        role: "farmer",
        tenant_id: "tenant-test-001",
      },
    },
  },

  FIELD: {
    id: "field-test-001",
    name: "Test Field",
    name_ar: "حقل اختباري",
    area_hectares: 5.2,
    crop_type: "wheat",
    status: "active",
    ndvi_current: 0.72,
    health_score: 85,
    created_at: new Date().toISOString(),
  },

  WEATHER: {
    location_id: "loc-sanaa-001",
    temperature_c: 22,
    humidity_percent: 45,
    wind_speed_kmh: 12,
    condition: "partly_cloudy",
    condition_ar: "غائم جزئيا",
    timestamp: new Date().toISOString(),
  },

  IRRIGATION: {
    field_id: "field-test-001",
    recommended_amount_mm: 25,
    recommended_duration_minutes: 45,
    next_irrigation_date: new Date(Date.now() + 86400000)
      .toISOString()
      .split("T")[0],
    crop_water_stress: 0.15,
    soil_moisture_percent: 35,
    et_mm_day: 5.5,
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// Test Lifecycle Hooks
// ═══════════════════════════════════════════════════════════════════════════════

export function setupIntegrationTests(): void {
  beforeAll(async () => {
    // Check if Kong is available
    const kongHealthy = await checkKongHealth();
    if (!kongHealthy) {
      console.warn(
        "Kong Gateway not available - some tests may use mock responses"
      );
    }
  });

  afterAll(() => {
    clearAuthCache();
  });

  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  afterEach(() => {
    vi.useRealTimers();
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// Assertion Helpers
// ═══════════════════════════════════════════════════════════════════════════════

export function expectValidApiResponse<T>(
  response: ApiResponse<T>,
  expectedStatus: number = 200
): void {
  if (response.status !== expectedStatus) {
    throw new Error(
      `Expected status ${expectedStatus}, got ${response.status}. Response: ${JSON.stringify(response.data)}`
    );
  }
}

export function expectFieldStructure(field: Record<string, unknown>): void {
  const requiredFields = ["id", "name", "status"];
  for (const field_name of requiredFields) {
    if (!(field_name in field)) {
      throw new Error(`Missing required field: ${field_name}`);
    }
  }
}

export function expectPaginatedResponse(
  response: Record<string, unknown>
): void {
  const paginationFields = ["data", "total", "page", "limit"];
  for (const field of paginationFields) {
    if (!(field in response)) {
      throw new Error(`Missing pagination field: ${field}`);
    }
  }
}
