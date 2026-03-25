// Sahool Admin Dashboard - API Layer
// طبقة API للوحة الإدارة
//
// This module delegates to the unified @sahool/api-client via unified-client.ts.
// All exports are preserved for backward compatibility.

import type { Farm, DiagnosisRecord, DashboardStats, WeatherAlert, SensorReading } from '@/types';
import { apiClient as authApiClient } from './api-client';
export { apiClient as adminApiClient, extractErrorMessageAr } from './api-client';
export type { AdminRole, Permission, AuditLogEntry } from './api-client';
import { logger } from './logger';

// Import API configuration from centralized config
import { API_URLS, TIMEOUT_TIERS } from '@/config/api';

// Re-export API_URLS for consumers of this module
export { API_URLS };

// Unified API client — replaces raw axios.create() with @sahool/api-client instance.
// Provides: token refresh with queuing, retry with exponential backoff, HTTPS enforcement.
import { apiClient } from './unified-client';
export { apiClient };

// ═══════════════════════════════════════════════════════════════════════════
// Image Upload API (FormData support)
// دعم رفع الصور عبر FormData
// ═══════════════════════════════════════════════════════════════════════════

const MAX_IMAGE_SIZE_MB = 50;
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/tiff'];

/**
 * Upload an image for crop disease diagnosis
 * رفع صورة لتشخيص أمراض المحاصيل
 */
export async function uploadDiagnosisImage(
  file: File,
  metadata: {
    fieldId: string;
    cropType?: string;
    notes?: string;
  }
): Promise<{
  diagnosisId: string;
  imageUrl: string;
  disease?: string;
  confidence?: number;
}> {
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    throw new Error(
      `Unsupported image type: ${file.type}. Allowed: ${ALLOWED_IMAGE_TYPES.join(', ')}`
    );
  }
  if (file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024) {
    throw new Error(
      `Image too large: ${(file.size / 1024 / 1024).toFixed(1)}MB. Max: ${MAX_IMAGE_SIZE_MB}MB`
    );
  }

  const formData = new FormData();
  formData.append('image', file);
  formData.append('field_id', metadata.fieldId);
  if (metadata.cropType) formData.append('crop_type', metadata.cropType);
  if (metadata.notes) formData.append('notes', metadata.notes);

  const response = await apiClient.post(API_URLS.diagnoses.analyze, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: TIMEOUT_TIERS.upload,
  });
  return response.data;
}

/**
 * Upload an image for vision detection (pest/disease/weed)
 * رفع صورة لكشف الآفات/الأمراض/الأعشاب عبر خدمة الرؤية
 */
export async function uploadVisionImage(
  file: File,
  task: 'pest' | 'disease' | 'weed',
  options?: {
    confidence?: number;
    modelVariant?: 'n' | 's' | 'm' | 'l' | 'x';
  }
): Promise<{
  detections: Array<{
    class: string;
    confidence: number;
    bbox: [number, number, number, number];
  }>;
  imageUrl?: string;
  processingTime?: number;
}> {
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    throw new Error(
      `Unsupported image type: ${file.type}. Allowed: ${ALLOWED_IMAGE_TYPES.join(', ')}`
    );
  }
  if (file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024) {
    throw new Error(
      `Image too large: ${(file.size / 1024 / 1024).toFixed(1)}MB. Max: ${MAX_IMAGE_SIZE_MB}MB`
    );
  }

  const formData = new FormData();
  formData.append('image', file);
  if (options?.confidence) formData.append('confidence', String(options.confidence));
  if (options?.modelVariant) formData.append('model_variant', options.modelVariant);

  const endpoint = {
    pest: API_URLS.visionEndpoints.detectPest,
    disease: API_URLS.visionEndpoints.detectDisease,
    weed: API_URLS.visionEndpoints.detectWeed,
  }[task];

  const response = await apiClient.post(endpoint, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: TIMEOUT_TIERS.analysis,
  });
  return response.data;
}

// API Functions

// Dashboard Stats
export async function fetchDashboardStats(): Promise<DashboardStats> {
  try {
    const response = await apiClient.get(API_URLS.dashboard.stats);
    return response.data;
  } catch (error) {
    logger.error('fetchDashboardStats failed', { error });
    throw error;
  }
}

// Farms / Fields
export async function fetchFarms(): Promise<Farm[]> {
  try {
    const response = await apiClient.get(API_URLS.fields.list);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch farms:', error);
    return [];
  }
}

export async function fetchFarmById(id: string): Promise<Farm> {
  try {
    const response = await apiClient.get(API_URLS.fields.byId(id));
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch farm by ID:', error);
    throw error;
  }
}

// Diagnoses - connects to crop-intelligence-service (formerly crop-health-ai)
export async function fetchDiagnoses(params?: {
  status?: string;
  severity?: string;
  farmId?: string;
  governorate?: string;
  limit?: number;
  offset?: number;
  timeRange?: 'day' | 'week' | 'month';
}): Promise<DiagnosisRecord[]> {
  try {
    const response = await apiClient.get(API_URLS.diagnoses.list, {
      params: {
        status: params?.status,
        severity: params?.severity,
        governorate: params?.governorate,
        limit: params?.limit || 50,
        offset: params?.offset || 0,
        time_range: params?.timeRange,
      },
    });

    // Map backend response to our frontend model
    return (response.data || []).map((d: Record<string, unknown>, _index: number) => ({
      id: d.id as string,
      farmId: (d.field_id as string) || `farm-${(d.id as string) || 'unknown'}`,
      farmName: d.governorate ? `مزرعة في ${d.governorate}` : 'مزرعة',
      imageUrl: (d.image_url as string) || '',
      thumbnailUrl: (d.thumbnail_url as string) || (d.image_url as string) || '',
      cropType: (d.crop_type as string) || 'unknown',
      diseaseId: d.disease_id as string,
      diseaseName: d.disease_name as string,
      diseaseNameAr: d.disease_name_ar as string,
      confidence: Number.isFinite(d.confidence as number) ? (d.confidence as number) * 100 : 0,
      severity: d.severity as 'low' | 'medium' | 'high' | 'critical',
      status: d.status as 'pending' | 'confirmed' | 'rejected' | 'treated',
      location: (d.location as { lat: number; lng: number }) || {
        lat: 15.3694,
        lng: 44.191,
      },
      diagnosedAt: d.timestamp as string,
      createdBy: (d.farmer_id as string) || 'unknown',
      expertReview: d.expert_notes
        ? {
            expertId: 'expert-1',
            expertName: 'خبير زراعي',
            notes: d.expert_notes as string,
            reviewedAt: d.updated_at as string,
          }
        : undefined,
    }));
  } catch (error) {
    logger.error('Failed to fetch diagnoses:', error);
    return [];
  }
}

// Diagnosis Statistics for Dashboard
export async function fetchDiagnosisStats(params?: {
  timeRange?: 'day' | 'week' | 'month';
}): Promise<{
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
    const response = await apiClient.get(API_URLS.diagnoses.stats, {
      params: { time_range: params?.timeRange },
    });
    const data = response.data || {};
    return {
      total: data.total || 0,
      pending: data.pending || 0,
      confirmed: data.confirmed || 0,
      treated: data.treated || 0,
      criticalCount: data.critical_count || 0,
      highCount: data.high_count || 0,
      byDisease: data.by_disease || {},
      byGovernorate: data.by_governorate || {},
    };
  } catch (error) {
    logger.error('Failed to fetch diagnosis stats:', error);
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
  status: 'confirmed' | 'rejected' | 'treated',
  notes?: string
): Promise<{ success: boolean; diagnosis_id: string; status: string }> {
  try {
    const response = await apiClient.patch(API_URLS.diagnoses.byId(id), null, {
      params: {
        status,
        expert_notes: notes,
      },
    });
    return response.data;
  } catch (error) {
    logger.error('Failed to update diagnosis status:', error);
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Weather API (POST-based with lat/lon coordinates)
// Uses weather-service (port 8092) — weather-core (8108) deprecated & archived
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Weather API functions — proxied through Next.js API route (/api/weather)
 * to extract tenant_id from the httpOnly JWT cookie server-side.
 *
 * واجهة الطقس — تمر عبر وكيل Next.js لاستخراج معرف المستأجر من الكوكي
 */

/**
 * Helper to handle weather proxy responses consistently.
 * Redirects to login on 401 (matching apiClient interceptor behavior).
 */
async function handleWeatherResponse(response: Response): Promise<unknown | null> {
  if (response.status === 401) {
    try {
      await fetch('/api/auth/logout', { method: 'POST', credentials: 'same-origin' });
    } catch (logoutError) {
      logger.error('Logout error during weather auth redirect:', logoutError);
    }
    authApiClient.clearToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return null;
  }
  if (!response.ok) return null;
  return await response.json();
}

export async function getWeatherCurrent(lat: number, lng: number, fieldId: string = 'default') {
  try {
    const response = await fetch('/api/weather', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'current', lat, lon: lng, field_id: fieldId }),
    });
    return await handleWeatherResponse(response);
  } catch (error) {
    logger.error('Failed to fetch current weather:', error);
    return null;
  }
}

export async function getWeatherForecast(
  lat: number,
  lng: number,
  days: number = 7,
  fieldId: string = 'default'
) {
  try {
    const response = await fetch('/api/weather', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'forecast', lat, lon: lng, field_id: fieldId, days }),
    });
    return await handleWeatherResponse(response);
  } catch (error) {
    logger.error('Failed to fetch weather forecast:', error);
    return null;
  }
}

export async function getAgriculturalReport(lat: number, lng: number, fieldId: string = 'default') {
  try {
    const response = await fetch('/api/weather', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'agricultural', lat, lon: lng, field_id: fieldId }),
    });
    return await handleWeatherResponse(response);
  } catch (error) {
    logger.error('Failed to fetch agricultural report:', error);
    return null;
  }
}

// Weather API (location_id based - for Yemen locations)
// Uses weather-service (port 8092) for location-based weather data
// Note: weather-advanced has been consolidated into weather-service
export async function getWeatherByLocation(locationId: string) {
  try {
    const response = await apiClient.get(API_URLS.weatherEndpoints.byLocation(locationId));
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch weather by location:', error);
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
    logger.error('Failed to fetch weather forecast by location:', error);
    return null;
  }
}

export async function getWeatherLocations() {
  try {
    const response = await apiClient.get(API_URLS.weatherEndpoints.locations);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch weather locations:', error);
    return { locations: [] };
  }
}

// Weather Alerts (from weather-service)
export async function fetchWeatherAlerts(locationId: string = 'sanaa'): Promise<WeatherAlert[]> {
  try {
    const response = await apiClient.get(API_URLS.weatherEndpoints.alerts(locationId));
    return response.data?.alerts || [];
  } catch (error) {
    logger.error('Failed to fetch weather alerts:', error);
    return [];
  }
}

// Sensor Readings
export async function fetchSensorReadings(farmId: string): Promise<SensorReading[]> {
  try {
    const response = await apiClient.get(API_URLS.sensors.readings(farmId));
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch sensor readings:', error);
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
    const response = await apiClient.get(API_URLS.notificationEndpoints.list, { params });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch notifications:', error);
    return [];
  }
}

export async function markNotificationRead(id: string): Promise<boolean> {
  try {
    await apiClient.patch(API_URLS.notificationEndpoints.markRead(id));
    return true;
  } catch (error) {
    logger.error('Failed to mark notification as read:', error);
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
    const response = await apiClient.get(API_URLS.taskEndpoints.list, {
      params,
    });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch tasks:', error);
    return [];
  }
}

export async function updateTaskStatus(id: string, status: string): Promise<boolean> {
  try {
    await apiClient.patch(API_URLS.taskEndpoints.byId(id), { status });
    return true;
  } catch (error) {
    logger.error('Failed to update task status:', error);
    return false;
  }
}

// Community Posts
export async function fetchCommunityPosts(params?: { category?: string; limit?: number }): Promise<
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
    const response = await apiClient.get(`${API_URLS.chatService}/api/v1/posts`, {
      params,
    });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch community posts:', error);
    return [];
  }
}

// Equipment
export async function fetchEquipment(params?: { type?: string; status?: string }): Promise<
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
    const response = await apiClient.get(API_URLS.equipmentEndpoints.list, { params });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch equipment:', error);
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
    const response = await apiClient.get(API_URLS.satelliteEndpoints.timeseries(fieldId), {
      params: options,
    });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch satellite timeseries:', error);
    return [];
  }
}

export async function requestSatelliteAnalysis(
  fieldId: string,
  analysisType: 'ndvi' | 'moisture' | 'thermal'
) {
  try {
    const response = await apiClient.post(API_URLS.satelliteEndpoints.analyze, {
      field_id: fieldId,
      analysis_type: analysisType,
    });
    return response.data;
  } catch (error) {
    logger.error('Failed to request satellite analysis:', error);
    return null;
  }
}

export async function getSatelliteIndices(fieldId: string) {
  try {
    const response = await apiClient.get(API_URLS.satelliteEndpoints.indices(fieldId));
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch satellite indices:', error);
    return null;
  }
}

export async function getAvailableSatellites() {
  try {
    const response = await apiClient.get(API_URLS.satelliteEndpoints.satellites);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch available satellites:', error);
    return { satellites: [] };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Dashboard Analytics API (dynamic data for charts)
// بيانات تحليلية ديناميكية للرسوم البيانية
// ═══════════════════════════════════════════════════════════════════════════

/** Fetch yield trend data from indicators service */
export async function fetchYieldTrends(
  period: '7d' | '30d' | '90d' = '30d'
): Promise<Array<{ month: string; yield: number; forecast: number }>> {
  try {
    const response = await apiClient.get(API_URLS.dashboard.trends, {
      params: { metric: 'yield', period },
    });
    return response.data?.data || [];
  } catch (error) {
    logger.error('Failed to fetch yield trends:', error);
    return [];
  }
}

/** Fetch crop distribution data from indicators dashboard */
export async function fetchCropDistribution(): Promise<Array<{ name: string; value: number }>> {
  try {
    const response = await apiClient.get(API_URLS.dashboard.stats);
    return (
      response.data?.crop_distribution?.map((c: { crop: string; area: number }) => ({
        name: c.crop,
        value: c.area,
      })) || []
    );
  } catch (error) {
    logger.error('Failed to fetch crop distribution:', error);
    return [];
  }
}

/** Fetch weekly activity data (diagnoses, irrigations, alerts) */
export async function fetchWeeklyActivity(): Promise<
  Array<{ day: string; diagnoses: number; irrigations: number; alerts: number }>
> {
  try {
    const response = await apiClient.get(API_URLS.dashboard.trends, {
      params: { metric: 'weekly_activity', period: '7d' },
    });
    return response.data?.data || [];
  } catch (error) {
    logger.error('Failed to fetch weekly activity:', error);
    return [];
  }
}

/** Fetch platform performance metrics for today */
export async function fetchPlatformMetrics(): Promise<{
  activeFarmers: number;
  dailySales: number;
  irrigationOps: number;
  avgTemperature: number;
  monthlyGrowthRate: number;
}> {
  try {
    const response = await apiClient.get(API_URLS.dashboard.stats);
    const data = response.data;
    return {
      activeFarmers: data?.active_users || 0,
      dailySales: data?.daily_sales || 0,
      irrigationOps: data?.pending_tasks || 0,
      avgTemperature: data?.avg_temperature || 0,
      monthlyGrowthRate: data?.monthly_growth_rate || 0,
    };
  } catch (error) {
    logger.error('Failed to fetch platform metrics:', error);
    return {
      activeFarmers: 0,
      dailySales: 0,
      irrigationOps: 0,
      avgTemperature: 0,
      monthlyGrowthRate: 0,
    };
  }
}

/** Fetch advisory recommendations for a field */
export async function fetchAdvisoryRecommendations(fieldId: string, cropType?: string) {
  try {
    const response = await apiClient.post(`${API_URLS.advisory}/api/v1/advisory/recommendations`, {
      field_id: fieldId,
      crop_type: cropType,
    });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch advisory recommendations:', error);
    return { recommendations: [], sources: [] };
  }
}

/** Fetch yield prediction for a field */
export async function fetchYieldPrediction(fieldId: string, cropType: string) {
  try {
    const response = await apiClient.post(`${API_URLS.yieldPrediction}/api/v1/yield/predict`, {
      field_id: fieldId,
      crop_type: cropType,
    });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch yield prediction:', error);
    return null;
  }
}

/** Fetch field intelligence data */
export async function fetchFieldIntelligence(fieldId: string) {
  try {
    const response = await apiClient.get(
      `${API_URLS.fieldIntelligence}/api/v1/field-intelligence/${fieldId}`
    );
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch field intelligence:', error);
    return null;
  }
}

/** Fetch alert-service alerts */
export async function fetchAlerts(params?: {
  severity?: string;
  type?: string;
  acknowledged?: boolean;
  limit?: number;
}) {
  try {
    const response = await apiClient.get(`${API_URLS.alerts}/api/v1/alerts`, { params });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch alerts:', error);
    return { data: [], meta: { total: 0, page: 1, limit: 20 } };
  }
}

/** Fetch billing subscription info */
export async function fetchBillingSubscription() {
  try {
    const response = await apiClient.get(`${API_URLS.billing}/api/v1/billing/subscription`);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch billing subscription:', error);
    return null;
  }
}

/** Fetch astronomical calendar info */
export async function fetchAstronomicalToday(lat?: number, lon?: number) {
  try {
    const response = await apiClient.get(
      `${API_URLS.astronomicalCalendar}/api/v1/astronomical/today`,
      { params: { lat, lon } }
    );
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch astronomical data:', error);
    return null;
  }
}

// Health checks
export async function checkServicesHealth(): Promise<Record<string, boolean>> {
  const services = Object.entries(API_URLS);
  const results: Record<string, boolean> = {};

  await Promise.all(
    services
      .filter(([, url]) => typeof url === 'string')
      .map(async ([name, url]) => {
        try {
          await apiClient.get(`${url}/healthz`, { timeout: TIMEOUT_TIERS.healthCheck });
          results[name] = true;
        } catch {
          results[name] = false;
        }
      })
  );

  return results;
}

// ═══════════════════════════════════════════════════════════════════════════
// Error handling policy
// سياسة التعامل مع الأخطاء
// ═══════════════════════════════════════════════════════════════════════════
// Critical functions (fetchDashboardStats) throw errors for React Query to handle.
// List functions return empty arrays on error for graceful degradation.
// The UI should display proper empty-state or error messages when data is unavailable.

// ═══════════════════════════════════════════════════════════════════════════
// Re-export services and types from api/ directory
// TypeScript resolves @/lib/api to this file (api.ts) rather than api/index.ts,
// so we re-export all service-based APIs here for consuming pages.
// ═══════════════════════════════════════════════════════════════════════════

export {
  // Core Services
  userService,
  iotService,
  irrigationService,
  alertService,
  equipmentService,
  // Core Types
  type User,
  type CreateUserData,
  type UpdateUserData,
  type IoTDevice,
  type CreateDeviceData,
  type IrrigationSchedule,
  type CreateIrrigationData,
  type Alert,
  type CreateAlertData,
  type Equipment,
  type CreateEquipmentData,
  type PaginationParams,
  type PaginatedResponse,
  type ApiResponse as ServiceApiResponse,
  type SensorReading,
} from './api/services';

export {
  // Extended Services
  taskService,
  inventoryService,
  researchService,
  marketplaceService,
  // Extended Types
  type Task,
  type CreateTaskData,
  type InventoryItem,
  type CreateInventoryData,
  type InventoryTransaction,
  type ResearchProject,
  type Experiment,
  type CreateProjectData,
  type CreateExperimentData,
  type MarketplaceListing,
  type CreateListingData,
} from './api/extended-services';
