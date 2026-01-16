// Sahool Admin Dashboard - API Configuration
// إعدادات الاتصال بالخادم

import axios, {
  type AxiosResponse,
  type AxiosError,
  type InternalAxiosRequestConfig,
} from "axios";
import type {
  Farm,
  DiagnosisRecord,
  DashboardStats,
  WeatherAlert,
  SensorReading,
} from "@/types";
import { apiClient as authApiClient } from "./api-client";
import Cookies from "js-cookie";
import { logger } from "./logger";

// Import API configuration from centralized config
import { API_URLS, API_CONFIG } from "@/config/api";

// Re-export API_URLS for consumers of this module
export { API_URLS };

// Helper function to get token from cookies
// NOTE: This will return undefined since tokens are now stored in httpOnly cookies
// and are not accessible from client-side JavaScript for security reasons.
//
// Authentication flow uses Next.js API routes as server-side proxies which can
// access httpOnly cookies. See implementations in:
//   - /app/api/auth/me/route.ts - Current user endpoint
//   - /app/api/auth/login/route.ts - Login with cookie setting
//   - /app/api/auth/logout/route.ts - Logout with cookie clearing
//   - /app/api/auth/refresh/route.ts - Token refresh
//
// For other API calls that require authentication, the backend services should
// be configured to accept cookie-based authentication via Kong gateway, or
// additional Next.js API routes should be created following the same pattern.
function getToken(): string | undefined {
  return Cookies.get("sahool_admin_token");
}

// Axios instance with defaults
// NOTE: withCredentials is set to true to send httpOnly cookies with requests
export const apiClient = axios.create({
  timeout: API_CONFIG.timeout,
  withCredentials: true, // Send cookies with cross-origin requests
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
    "Accept-Language": "ar,en",
  },
});

// Add auth token interceptor - uses centralized token management
// NOTE: With httpOnly cookies, this interceptor may not be able to add the
// Authorization header. Backend services should be configured to accept
// cookie-based authentication, OR these API calls should be proxied through
// Next.js API routes where tokens can be injected server-side.
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for auth errors - consistent with auth store
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear session via logout endpoint
      try {
        await fetch("/api/auth/logout", {
          method: "POST",
          credentials: "same-origin",
        });
      } catch (logoutError) {
        logger.error("Logout error:", logoutError);
      }

      authApiClient.clearToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

// API Functions

// Dashboard Stats
export async function fetchDashboardStats(): Promise<DashboardStats> {
  try {
    const response = await apiClient.get(
      `${API_URLS.indicators}/api/v1/indicators/dashboard`,
    );
    return response.data;
  } catch (error) {
    // Return mock data for development
    return {
      totalFarms: 156,
      activeFarms: 142,
      totalArea: 2450.5,
      totalDiagnoses: 1247,
      pendingReviews: 23,
      criticalAlerts: 5,
      avgHealthScore: 78.5,
      weeklyDiagnoses: 89,
    };
  }
}

// Farms
export async function fetchFarms(): Promise<Farm[]> {
  try {
    const response = await apiClient.get(`${API_URLS.fieldCore}/api/v1/fields`);
    return response.data;
  } catch (error) {
    // Return static mock data for development when backend is unavailable.
    // Note: This returns the same data on every call to ensure UI consistency.
    // See MOCK_FARMS constant at the bottom of this file for the data source.
    logger.log("Falling back to static mock farms data");
    return getMockFarms();
  }
}

export async function fetchFarmById(id: string): Promise<Farm> {
  const response = await apiClient.get(
    `${API_URLS.fieldCore}/api/v1/fields/${id}`,
  );
  return response.data;
}

// Diagnoses - connects to crop-health-ai v2.1 service
export async function fetchDiagnoses(params?: {
  status?: string;
  severity?: string;
  farmId?: string;
  governorate?: string;
  limit?: number;
  offset?: number;
}): Promise<DiagnosisRecord[]> {
  try {
    const response = await apiClient.get(
      `${API_URLS.cropHealth}/api/v1/crop-health/diagnoses`,
      {
        params: {
          status: params?.status,
          severity: params?.severity,
          governorate: params?.governorate,
          limit: params?.limit || 50,
          offset: params?.offset || 0,
        },
      },
    );

    // Map backend response to our frontend model
    return response.data.map((d: Record<string, unknown>, index: number) => ({
      id: d.id as string,
      farmId:
        (d.field_id as string) || `farm-${crypto.randomUUID().slice(0, 8)}`,
      farmName: d.governorate ? `مزرعة في ${d.governorate}` : "مزرعة",
      imageUrl: (d.image_url as string) || "/api/placeholder/400/300",
      thumbnailUrl:
        (d.thumbnail_url as string) ||
        (d.image_url as string) ||
        "/api/placeholder/100/100",
      cropType: (d.crop_type as string) || "unknown",
      diseaseId: d.disease_id as string,
      diseaseName: d.disease_name as string,
      diseaseNameAr: d.disease_name_ar as string,
      confidence: (d.confidence as number) * 100, // Convert to percentage
      severity: d.severity as "low" | "medium" | "high" | "critical",
      status: d.status as "pending" | "confirmed" | "rejected" | "treated",
      location: (d.location as { lat: number; lng: number }) || {
        lat: 15.3694,
        lng: 44.191,
      },
      diagnosedAt: d.timestamp as string,
      createdBy: (d.farmer_id as string) || "unknown",
      expertReview: d.expert_notes
        ? {
            expertId: "expert-1",
            expertName: "خبير زراعي",
            notes: d.expert_notes as string,
            reviewedAt: d.updated_at as string,
          }
        : undefined,
    }));
  } catch (error) {
    // Return static mock data for development when backend is unavailable.
    // Note: This returns the same data on every call to ensure UI consistency.
    // See MOCK_DIAGNOSES constant at the bottom of this file for the data source.
    logger.log("Falling back to static mock diagnoses data");
    return getMockDiagnoses();
  }
}

// Diagnosis Statistics for Dashboard
export async function fetchDiagnosisStats(): Promise<{
  total: number;
  pending: number;
  confirmed: number;
  treated: number;
  criticalCount: number;
  highCount: number;
  byDisease: Record<string, number>;
  byGovernorate: Record<string, number>;
}> {
  try {
    const response = await apiClient.get(
      `${API_URLS.cropHealth}/api/v1/crop-health/diagnoses/stats`,
    );
    return {
      total: response.data.total,
      pending: response.data.pending,
      confirmed: response.data.confirmed,
      treated: response.data.treated,
      criticalCount: response.data.critical_count,
      highCount: response.data.high_count,
      byDisease: response.data.by_disease,
      byGovernorate: response.data.by_governorate,
    };
  } catch (error) {
    return {
      total: 0,
      pending: 0,
      confirmed: 0,
      treated: 0,
      criticalCount: 0,
      highCount: 0,
      byDisease: {},
      byGovernorate: {},
    };
  }
}

export async function updateDiagnosisStatus(
  id: string,
  status: "confirmed" | "rejected" | "treated",
  notes?: string,
): Promise<{ success: boolean; diagnosis_id: string; status: string }> {
  try {
    const response = await apiClient.patch(
      `${API_URLS.cropHealth}/api/v1/crop-health/diagnoses/${id}`,
      null,
      {
        params: {
          status,
          expert_notes: notes,
        },
      },
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to update diagnosis status:", error);
    // Return mock success for development
    return { success: true, diagnosis_id: id, status };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Weather API (weather-core service - POST-based with lat/lon)
// Uses weather-core service (port 8108) for coordinate-based weather data
// ═══════════════════════════════════════════════════════════════════════════

export async function getWeatherCurrent(
  lat: number,
  lng: number,
  fieldId: string = "default"
) {
  try {
    const response = await apiClient.post(
      `${API_URLS.weatherCore}/weather/current`,
      { tenant_id: "default", field_id: fieldId, lat, lon: lng }
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch current weather:", error);
    return null;
  }
}

export async function getWeatherForecast(
  lat: number,
  lng: number,
  days: number = 7,
  fieldId: string = "default"
) {
  try {
    const response = await apiClient.post(
      `${API_URLS.weatherCore}/weather/forecast`,
      { tenant_id: "default", field_id: fieldId, lat, lon: lng }
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch weather forecast:", error);
    return null;
  }
}

export async function getAgriculturalReport(
  lat: number,
  lng: number,
  fieldId: string = "default"
) {
  try {
    const response = await apiClient.post(
      `${API_URLS.weatherCore}/weather/agricultural-report`,
      { tenant_id: "default", field_id: fieldId, lat, lon: lng }
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch agricultural report:", error);
    return null;
  }
}

// Weather Advanced API (location_id based - for Yemen locations)
// Uses weather-advanced service (port 8092) for location-based weather data
export async function getWeatherByLocation(locationId: string) {
  try {
    const response = await apiClient.get(
      `${API_URLS.weather}/v1/current/${locationId}`
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch weather by location:", error);
    return null;
  }
}

export async function getWeatherForecastByLocation(locationId: string, days: number = 7) {
  try {
    const response = await apiClient.get(
      `${API_URLS.weather}/v1/forecast/${locationId}?days=${days}`
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch weather forecast by location:", error);
    return null;
  }
}

export async function getWeatherLocations() {
  try {
    const response = await apiClient.get(
      `${API_URLS.weather}/v1/locations`
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch weather locations:", error);
    return { locations: [] };
  }
}

// Weather Alerts (from weather-advanced service)
export async function fetchWeatherAlerts(locationId: string = "sanaa"): Promise<WeatherAlert[]> {
  try {
    const response = await apiClient.get(
      `${API_URLS.weather}/v1/alerts/${locationId}`
    );
    return response.data?.alerts || [];
  } catch (error) {
    logger.error("Failed to fetch weather alerts:", error);
    return [];
  }
}

// Sensor Readings
export async function fetchSensorReadings(
  farmId: string,
): Promise<SensorReading[]> {
  try {
    const response = await apiClient.get(
      `${API_URLS.virtualSensors}/api/v1/iot/readings/${farmId}`,
    );
    return response.data;
  } catch (error) {
    return [];
  }
}

// Notifications
export async function fetchNotifications(params?: {
  type?: string;
  priority?: string;
  limit?: number;
}): Promise<
  Array<{
    id: string;
    type: string;
    title: string;
    message: string;
    priority: string;
    read: boolean;
    createdAt: string;
  }>
> {
  try {
    const response = await apiClient.get(
      `${API_URLS.notifications}/api/v1/notifications`,
      { params },
    );
    return response.data;
  } catch (error) {
    return [];
  }
}

export async function markNotificationRead(id: string): Promise<boolean> {
  try {
    await apiClient.patch(
      `${API_URLS.notifications}/api/v1/notifications/${id}/read`,
    );
    return true;
  } catch (error) {
    return false;
  }
}

// Tasks
export async function fetchTasks(params?: {
  status?: string;
  type?: string;
  assignedTo?: string;
  limit?: number;
}): Promise<
  Array<{
    id: string;
    title: string;
    description: string;
    type: string;
    status: string;
    priority: string;
    dueDate: string;
    assignedTo: string;
    fieldId: string;
  }>
> {
  try {
    const response = await apiClient.get(`${API_URLS.task}/api/v1/tasks`, {
      params,
    });
    return response.data;
  } catch (error) {
    return [];
  }
}

export async function updateTaskStatus(
  id: string,
  status: string,
): Promise<boolean> {
  try {
    await apiClient.patch(`${API_URLS.task}/api/v1/tasks/${id}`, { status });
    return true;
  } catch (error) {
    return false;
  }
}

// Community Posts
export async function fetchCommunityPosts(params?: {
  category?: string;
  limit?: number;
}): Promise<
  Array<{
    id: string;
    title: string;
    content: string;
    authorId: string;
    authorName: string;
    category: string;
    likes: number;
    comments: number;
    createdAt: string;
  }>
> {
  try {
    const response = await apiClient.get(`${API_URLS.community}/api/v1/posts`, {
      params,
    });
    return response.data;
  } catch (error) {
    return [];
  }
}

// Equipment
export async function fetchEquipment(params?: {
  type?: string;
  status?: string;
}): Promise<
  Array<{
    id: string;
    name: string;
    type: string;
    status: string;
    lastMaintenance: string;
    nextMaintenance: string;
    fuelLevel?: number;
    hoursUsed?: number;
  }>
> {
  try {
    const response = await apiClient.get(
      `${API_URLS.equipment}/api/v1/equipment`,
      { params },
    );
    return response.data;
  } catch (error) {
    return [];
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Satellite/Vegetation Analysis API
// خدمة تحليل الأقمار الصناعية والنباتات
// ═══════════════════════════════════════════════════════════════════════════

export async function getSatelliteTimeseries(
  fieldId: string,
  options?: { from?: string; to?: string }
) {
  try {
    const response = await apiClient.get(
      `${API_URLS.satellite}/v1/timeseries/${fieldId}`,
      { params: options }
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch satellite timeseries:", error);
    return [];
  }
}

export async function requestSatelliteAnalysis(
  fieldId: string,
  analysisType: "ndvi" | "moisture" | "thermal"
) {
  try {
    const response = await apiClient.post(
      `${API_URLS.satellite}/v1/analyze`,
      { field_id: fieldId, analysis_type: analysisType }
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to request satellite analysis:", error);
    return null;
  }
}

export async function getSatelliteIndices(fieldId: string) {
  try {
    const response = await apiClient.get(
      `${API_URLS.satellite}/v1/indices/${fieldId}`
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch satellite indices:", error);
    return null;
  }
}

export async function getAvailableSatellites() {
  try {
    const response = await apiClient.get(
      `${API_URLS.satellite}/v1/satellites`
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch available satellites:", error);
    return { satellites: [] };
  }
}

// Health checks
export async function checkServicesHealth(): Promise<Record<string, boolean>> {
  const services = Object.entries(API_URLS);
  const results: Record<string, boolean> = {};

  await Promise.all(
    services.map(async ([name, url]) => {
      try {
        await apiClient.get(`${url}/healthz`, { timeout: 5000 });
        results[name] = true;
      } catch {
        results[name] = false;
      }
    }),
  );

  return results;
}

// ═══════════════════════════════════════════════════════════════════════════
// Static Mock Data
// بيانات وهمية ثابتة للتطوير
// ═══════════════════════════════════════════════════════════════════════════
// IMPORTANT: These static mock data objects are generated ONCE at module load
// time and reused on every API error. This ensures consistent UI behavior
// when the backend services are unavailable. Previously, mock data was
// regenerated on every error, causing inconsistent displays (different IDs,
// random values, etc.) which led to poor UX and potential state issues.
//
// To update mock data: modify the static arrays below, do NOT add randomization.
// ═══════════════════════════════════════════════════════════════════════════

const MOCK_FARMS: Farm[] = [
  { id: "farm-1", name: "Farm 1", nameAr: "مزرعة ١", ownerId: "user-1", governorate: "sanaa", district: "District", area: 25.5, coordinates: { lat: 15.35, lng: 44.21 }, crops: ["wheat"], status: "active", healthScore: 85, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-10-15T00:00:00Z" },
  { id: "farm-2", name: "Farm 2", nameAr: "مزرعة ٢", ownerId: "user-2", governorate: "taiz", district: "District", area: 18.3, coordinates: { lat: 13.58, lng: 44.02 }, crops: ["coffee"], status: "active", healthScore: 72, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-09-20T00:00:00Z" },
  { id: "farm-3", name: "Farm 3", nameAr: "مزرعة ٣", ownerId: "user-3", governorate: "ibb", district: "District", area: 32.1, coordinates: { lat: 13.97, lng: 44.18 }, crops: ["qat"], status: "active", healthScore: 91, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-11-01T00:00:00Z" },
  { id: "farm-4", name: "Farm 4", nameAr: "مزرعة ٤", ownerId: "user-4", governorate: "hadramaut", district: "District", area: 45.8, coordinates: { lat: 15.95, lng: 48.78 }, crops: ["date_palm"], status: "active", healthScore: 78, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-08-10T00:00:00Z" },
  { id: "farm-5", name: "Farm 5", nameAr: "مزرعة ٥", ownerId: "user-5", governorate: "hodeidah", district: "District", area: 22.4, coordinates: { lat: 14.80, lng: 42.95 }, crops: ["mango"], status: "active", healthScore: 65, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-07-25T00:00:00Z" },
  { id: "farm-6", name: "Farm 6", nameAr: "مزرعة ٦", ownerId: "user-6", governorate: "dhamar", district: "District", area: 15.7, coordinates: { lat: 14.55, lng: 44.40 }, crops: ["sorghum"], status: "active", healthScore: 88, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-12-05T00:00:00Z" },
  { id: "farm-7", name: "Farm 7", nameAr: "مزرعة ٧", ownerId: "user-7", governorate: "sanaa", district: "District", area: 28.9, coordinates: { lat: 15.42, lng: 44.35 }, crops: ["wheat"], status: "active", healthScore: 76, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-09-15T00:00:00Z" },
  { id: "farm-8", name: "Farm 8", nameAr: "مزرعة ٨", ownerId: "user-8", governorate: "taiz", district: "District", area: 12.2, coordinates: { lat: 13.62, lng: 44.08 }, crops: ["banana"], status: "active", healthScore: 82, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-10-28T00:00:00Z" },
  { id: "farm-9", name: "Farm 9", nameAr: "مزرعة ٩", ownerId: "user-9", governorate: "ibb", district: "District", area: 38.5, coordinates: { lat: 14.02, lng: 44.22 }, crops: ["coffee"], status: "active", healthScore: 69, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-11-18T00:00:00Z" },
  { id: "farm-10", name: "Farm 10", nameAr: "مزرعة ١٠", ownerId: "user-10", governorate: "hadramaut", district: "District", area: 52.3, coordinates: { lat: 16.05, lng: 48.92 }, crops: ["date_palm"], status: "active", healthScore: 94, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-06-30T00:00:00Z" },
  { id: "farm-11", name: "Farm 11", nameAr: "مزرعة ١١", ownerId: "user-1", governorate: "hodeidah", district: "District", area: 19.8, coordinates: { lat: 14.72, lng: 42.88 }, crops: ["mango"], status: "active", healthScore: 71, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-08-22T00:00:00Z" },
  { id: "farm-12", name: "Farm 12", nameAr: "مزرعة ١٢", ownerId: "user-2", governorate: "dhamar", district: "District", area: 27.6, coordinates: { lat: 14.48, lng: 44.32 }, crops: ["wheat"], status: "active", healthScore: 87, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-09-08T00:00:00Z" },
  { id: "farm-13", name: "Farm 13", nameAr: "مزرعة ١٣", ownerId: "user-3", governorate: "sanaa", district: "District", area: 34.2, coordinates: { lat: 15.28, lng: 44.15 }, crops: ["sorghum"], status: "active", healthScore: 79, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-10-03T00:00:00Z" },
  { id: "farm-14", name: "Farm 14", nameAr: "مزرعة ١٤", ownerId: "user-4", governorate: "taiz", district: "District", area: 16.9, coordinates: { lat: 13.55, lng: 43.98 }, crops: ["coffee"], status: "active", healthScore: 83, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-11-25T00:00:00Z" },
  { id: "farm-15", name: "Farm 15", nameAr: "مزرعة ١٥", ownerId: "user-5", governorate: "ibb", district: "District", area: 41.4, coordinates: { lat: 13.92, lng: 44.12 }, crops: ["qat"], status: "active", healthScore: 68, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-07-12T00:00:00Z" },
  { id: "farm-16", name: "Farm 16", nameAr: "مزرعة ١٦", ownerId: "user-6", governorate: "hadramaut", district: "District", area: 48.7, coordinates: { lat: 15.88, lng: 48.65 }, crops: ["date_palm"], status: "active", healthScore: 92, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-08-05T00:00:00Z" },
  { id: "farm-17", name: "Farm 17", nameAr: "مزرعة ١٧", ownerId: "user-7", governorate: "hodeidah", district: "District", area: 23.1, coordinates: { lat: 14.85, lng: 43.02 }, crops: ["banana"], status: "active", healthScore: 75, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-09-28T00:00:00Z" },
  { id: "farm-18", name: "Farm 18", nameAr: "مزرعة ١٨", ownerId: "user-8", governorate: "dhamar", district: "District", area: 31.8, coordinates: { lat: 14.62, lng: 44.45 }, crops: ["wheat"], status: "active", healthScore: 86, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-10-18T00:00:00Z" },
  { id: "farm-19", name: "Farm 19", nameAr: "مزرعة ١٩", ownerId: "user-9", governorate: "sanaa", district: "District", area: 14.5, coordinates: { lat: 15.38, lng: 44.28 }, crops: ["sorghum"], status: "active", healthScore: 73, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-11-08T00:00:00Z" },
  { id: "farm-20", name: "Farm 20", nameAr: "مزرعة ٢٠", ownerId: "user-10", governorate: "taiz", district: "District", area: 36.4, coordinates: { lat: 13.68, lng: 44.15 }, crops: ["coffee"], status: "active", healthScore: 89, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-12-15T00:00:00Z" },
  { id: "farm-21", name: "Farm 21", nameAr: "مزرعة ٢١", ownerId: "user-1", governorate: "ibb", district: "District", area: 20.7, coordinates: { lat: 14.08, lng: 44.25 }, crops: ["qat"], status: "active", healthScore: 81, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-07-20T00:00:00Z" },
  { id: "farm-22", name: "Farm 22", nameAr: "مزرعة ٢٢", ownerId: "user-2", governorate: "hadramaut", district: "District", area: 55.2, coordinates: { lat: 16.12, lng: 49.05 }, crops: ["date_palm"], status: "active", healthScore: 67, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-08-28T00:00:00Z" },
  { id: "farm-23", name: "Farm 23", nameAr: "مزرعة ٢٣", ownerId: "user-3", governorate: "hodeidah", district: "District", area: 17.3, coordinates: { lat: 14.78, lng: 42.92 }, crops: ["mango"], status: "active", healthScore: 90, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-09-12T00:00:00Z" },
  { id: "farm-24", name: "Farm 24", nameAr: "مزرعة ٢٤", ownerId: "user-4", governorate: "dhamar", district: "District", area: 29.6, coordinates: { lat: 14.52, lng: 44.38 }, crops: ["wheat"], status: "active", healthScore: 77, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-10-25T00:00:00Z" },
  { id: "farm-25", name: "Farm 25", nameAr: "مزرعة ٢٥", ownerId: "user-5", governorate: "sanaa", district: "District", area: 42.8, coordinates: { lat: 15.45, lng: 44.32 }, crops: ["sorghum"], status: "active", healthScore: 84, lastUpdated: "2025-01-15T00:00:00Z", createdAt: "2024-11-30T00:00:00Z" },
];

const MOCK_DIAGNOSES: DiagnosisRecord[] = [
  { id: "diag-1", farmId: "farm-3", farmName: "مزرعة ٣", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_late_blight", diseaseName: "Late Blight", diseaseNameAr: "اللفحة المتأخرة", confidence: 92.5, severity: "high", status: "pending", location: { lat: 13.97, lng: 44.18 }, diagnosedAt: "2025-01-14T10:30:00Z", createdBy: "user-3" },
  { id: "diag-2", farmId: "farm-7", farmName: "مزرعة ٧", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "powdery_mildew", diseaseName: "Powdery Mildew", diseaseNameAr: "البياض الدقيقي", confidence: 87.3, severity: "medium", status: "confirmed", location: { lat: 15.42, lng: 44.35 }, diagnosedAt: "2025-01-13T14:15:00Z", createdBy: "user-7" },
  { id: "diag-3", farmId: "farm-12", farmName: "مزرعة ١٢", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "bacterial_spot", diseaseName: "Bacterial Spot", diseaseNameAr: "التبقع البكتيري", confidence: 78.9, severity: "low", status: "treated", location: { lat: 14.48, lng: 44.32 }, diagnosedAt: "2025-01-12T09:45:00Z", createdBy: "user-2" },
  { id: "diag-4", farmId: "farm-5", farmName: "مزرعة ٥", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_early_blight", diseaseName: "Early Blight", diseaseNameAr: "اللفحة المبكرة", confidence: 95.1, severity: "critical", status: "pending", location: { lat: 14.80, lng: 42.95 }, diagnosedAt: "2025-01-14T16:20:00Z", createdBy: "user-5" },
  { id: "diag-5", farmId: "farm-18", farmName: "مزرعة ١٨", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_late_blight", diseaseName: "Late Blight", diseaseNameAr: "اللفحة المتأخرة", confidence: 82.4, severity: "medium", status: "confirmed", location: { lat: 14.62, lng: 44.45 }, diagnosedAt: "2025-01-11T11:00:00Z", createdBy: "user-8" },
  { id: "diag-6", farmId: "farm-1", farmName: "مزرعة ١", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "powdery_mildew", diseaseName: "Powdery Mildew", diseaseNameAr: "البياض الدقيقي", confidence: 89.7, severity: "high", status: "pending", location: { lat: 15.35, lng: 44.21 }, diagnosedAt: "2025-01-14T08:30:00Z", createdBy: "user-1" },
  { id: "diag-7", farmId: "farm-21", farmName: "مزرعة ٢١", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "bacterial_spot", diseaseName: "Bacterial Spot", diseaseNameAr: "التبقع البكتيري", confidence: 74.2, severity: "low", status: "rejected", location: { lat: 14.08, lng: 44.25 }, diagnosedAt: "2025-01-10T13:45:00Z", createdBy: "user-1" },
  { id: "diag-8", farmId: "farm-9", farmName: "مزرعة ٩", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_early_blight", diseaseName: "Early Blight", diseaseNameAr: "اللفحة المبكرة", confidence: 91.8, severity: "critical", status: "confirmed", location: { lat: 14.02, lng: 44.22 }, diagnosedAt: "2025-01-13T17:00:00Z", createdBy: "user-9" },
  { id: "diag-9", farmId: "farm-14", farmName: "مزرعة ١٤", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_late_blight", diseaseName: "Late Blight", diseaseNameAr: "اللفحة المتأخرة", confidence: 85.6, severity: "medium", status: "treated", location: { lat: 13.55, lng: 43.98 }, diagnosedAt: "2025-01-09T10:15:00Z", createdBy: "user-4" },
  { id: "diag-10", farmId: "farm-23", farmName: "مزرعة ٢٣", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "powdery_mildew", diseaseName: "Powdery Mildew", diseaseNameAr: "البياض الدقيقي", confidence: 79.3, severity: "low", status: "pending", location: { lat: 14.78, lng: 42.92 }, diagnosedAt: "2025-01-14T12:30:00Z", createdBy: "user-3" },
  { id: "diag-11", farmId: "farm-6", farmName: "مزرعة ٦", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "bacterial_spot", diseaseName: "Bacterial Spot", diseaseNameAr: "التبقع البكتيري", confidence: 93.2, severity: "high", status: "confirmed", location: { lat: 14.55, lng: 44.40 }, diagnosedAt: "2025-01-12T15:45:00Z", createdBy: "user-6" },
  { id: "diag-12", farmId: "farm-16", farmName: "مزرعة ١٦", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_early_blight", diseaseName: "Early Blight", diseaseNameAr: "اللفحة المبكرة", confidence: 88.1, severity: "medium", status: "pending", location: { lat: 15.88, lng: 48.65 }, diagnosedAt: "2025-01-13T09:00:00Z", createdBy: "user-6" },
  { id: "diag-13", farmId: "farm-2", farmName: "مزرعة ٢", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_late_blight", diseaseName: "Late Blight", diseaseNameAr: "اللفحة المتأخرة", confidence: 76.8, severity: "low", status: "treated", location: { lat: 13.58, lng: 44.02 }, diagnosedAt: "2025-01-08T14:30:00Z", createdBy: "user-2" },
  { id: "diag-14", farmId: "farm-25", farmName: "مزرعة ٢٥", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "powdery_mildew", diseaseName: "Powdery Mildew", diseaseNameAr: "البياض الدقيقي", confidence: 94.5, severity: "critical", status: "pending", location: { lat: 15.45, lng: 44.32 }, diagnosedAt: "2025-01-14T18:00:00Z", createdBy: "user-5" },
  { id: "diag-15", farmId: "farm-10", farmName: "مزرعة ١٠", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "bacterial_spot", diseaseName: "Bacterial Spot", diseaseNameAr: "التبقع البكتيري", confidence: 81.9, severity: "medium", status: "confirmed", location: { lat: 16.05, lng: 48.92 }, diagnosedAt: "2025-01-11T16:15:00Z", createdBy: "user-10" },
  { id: "diag-16", farmId: "farm-19", farmName: "مزرعة ١٩", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_early_blight", diseaseName: "Early Blight", diseaseNameAr: "اللفحة المبكرة", confidence: 86.4, severity: "high", status: "pending", location: { lat: 15.38, lng: 44.28 }, diagnosedAt: "2025-01-14T07:45:00Z", createdBy: "user-9" },
  { id: "diag-17", farmId: "farm-8", farmName: "مزرعة ٨", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_late_blight", diseaseName: "Late Blight", diseaseNameAr: "اللفحة المتأخرة", confidence: 90.2, severity: "medium", status: "rejected", location: { lat: 13.62, lng: 44.08 }, diagnosedAt: "2025-01-10T11:30:00Z", createdBy: "user-8" },
  { id: "diag-18", farmId: "farm-22", farmName: "مزرعة ٢٢", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "powdery_mildew", diseaseName: "Powdery Mildew", diseaseNameAr: "البياض الدقيقي", confidence: 77.6, severity: "low", status: "treated", location: { lat: 16.12, lng: 49.05 }, diagnosedAt: "2025-01-07T13:00:00Z", createdBy: "user-2" },
  { id: "diag-19", farmId: "farm-13", farmName: "مزرعة ١٣", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "bacterial_spot", diseaseName: "Bacterial Spot", diseaseNameAr: "التبقع البكتيري", confidence: 83.7, severity: "high", status: "confirmed", location: { lat: 15.28, lng: 44.15 }, diagnosedAt: "2025-01-12T08:15:00Z", createdBy: "user-3" },
  { id: "diag-20", farmId: "farm-4", farmName: "مزرعة ٤", imageUrl: "/api/placeholder/400/300", thumbnailUrl: "/api/placeholder/100/100", cropType: "tomato", diseaseId: "tomato_early_blight", diseaseName: "Early Blight", diseaseNameAr: "اللفحة المبكرة", confidence: 96.3, severity: "critical", status: "pending", location: { lat: 15.95, lng: 48.78 }, diagnosedAt: "2025-01-14T19:30:00Z", createdBy: "user-4" },
];

/**
 * Returns static mock farm data for development/fallback scenarios.
 * This function returns a reference to the static MOCK_FARMS array,
 * ensuring consistent data across multiple calls when the backend is unavailable.
 */
function getMockFarms(): Farm[] {
  return MOCK_FARMS;
}

/**
 * Returns static mock diagnosis data for development/fallback scenarios.
 * This function returns a reference to the static MOCK_DIAGNOSES array,
 * ensuring consistent data across multiple calls when the backend is unavailable.
 */
function getMockDiagnoses(): DiagnosisRecord[] {
  return MOCK_DIAGNOSES;
}
