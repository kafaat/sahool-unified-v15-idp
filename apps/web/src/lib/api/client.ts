/**
 * SAHOOL API Client
 * Domain-specific API methods for the web frontend.
 *
 * Transport layer is delegated to the unified client (@sahool/api-client),
 * which provides: JWT auth, token refresh, CSRF, retry, HTTPS enforcement.
 * This file only contains domain method wrappers.
 */

import axios from 'axios';
import {
  ADVISORY_ENDPOINTS,
  ALERT_ENDPOINTS,
  AUTH_ENDPOINTS,
  CHAT_ENDPOINTS,
  CROP_HEALTH_ENDPOINTS,
  DISASTER_ENDPOINTS,
  EQUIPMENT_ENDPOINTS,
  FIELD_ENDPOINTS,
  INTELLIGENCE_ENDPOINTS,
  IOT_ENDPOINTS,
  IRRIGATION_ENDPOINTS,
  MARKETPLACE_ENDPOINTS,
  PROVIDER_ENDPOINTS,
  SATELLITE_ENDPOINTS,
  TASK_ENDPOINTS,
  BILLING_ENDPOINTS,
  WEATHER_ENDPOINTS,
  YIELD_ENDPOINTS,
  buildUrl,
} from '@sahool/shared-types/contracts';
import { sanitizers, validators, validationErrors } from '../validation';
import { unifiedApiClient } from './unified-client';
import type {
  AgriculturalRisk,
  ApiResponse,
  Field,
  FieldCreateRequest,
  FieldUpdateRequest,
  NdviData,
  NdviSummary,
  WeatherData,
  WeatherForecast,
  Sensor,
  SensorReading,
  IrrigationRecommendation,
  IrrigationSchedule,
  IrrigationScheduleCreate,
  ET0Calculation,
  FertilizerRecommendation,
  CropHealthAnalysis,
  GDDRecord,
  SprayWindow,
  SprayHistoryRecord,
  Task,
  TaskCreateRequest,
  Equipment,
  MaintenanceSchedule,
  MarketplaceListing,
  Subscription,
  Invoice,
  User,
} from './types';

// Note: tenant_id is extracted server-side from the JWT in the httpOnly cookie.
// The access_token cookie cannot be read by client-side JS (httpOnly).
// Weather API endpoints receive the JWT via withCredentials: true and the
// backend extracts tenant_id from the token's `tid` claim automatically.

class SahoolApiClient {
  /**
   * Set auth token. No-op in cookie-based auth mode — token management
   * is handled by httpOnly cookies via the unified client.
   * Retained for backward compatibility with tests and legacy code.
   */
  setToken(_token: string): void {
    // No-op: auth is cookie-based via withCredentials
  }

  /**
   * Clear auth token. No-op in cookie-based auth mode.
   * Retained for backward compatibility with tests and legacy code.
   */
  clearToken(): void {
    // No-op: auth is cookie-based via withCredentials
  }

  /**
   * Core request method — delegates to the unified axios instance.
   * Token management, retry, CSRF, and 401 handling are all provided
   * by the shared @sahool/api-client interceptors.
   */
  private async request<T>(
    endpoint: string,
    options: {
      method?: string;
      body?: string;
      params?: Record<string, string>;
      headers?: Record<string, string>;
      timeout?: number;
    } = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await unifiedApiClient.request({
        url: endpoint,
        method: (options.method as any) || 'GET',
        data: options.body ? JSON.parse(options.body) : undefined,
        params: options.params,
        headers: options.headers,
        timeout: options.timeout,
      });

      const data = response.data;
      return typeof data === 'object' && data !== null ? data : { success: true, data: data as T };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const data = error.response?.data;
        return {
          success: false,
          error: data?.error || data?.message || error.message || 'Request failed',
        };
      }
      return {
        success: false,
        error:
          error instanceof Error ? error.message : 'Network error - please check your connection',
      };
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Authentication API
  // ═══════════════════════════════════════════════════════════════════════════

  async login(email: string, password: string) {
    // Sanitize email input to prevent XSS
    const sanitizedEmail = sanitizers.email(email);

    // Validate email format using comprehensive validator
    if (!validators.email(sanitizedEmail)) {
      return {
        success: false,
        error: validationErrors.email,
      };
    }

    return this.request<{
      access_token: string;
      refresh_token?: string;
      user: User;
    }>(AUTH_ENDPOINTS.LOGIN, {
      method: 'POST',
      body: JSON.stringify({ email: sanitizedEmail, password }),
      // Auth requests don't need retry (handled by unified client's interceptors)
    });
  }

  async getCurrentUser() {
    return this.request<User>(AUTH_ENDPOINTS.ME);
  }

  /**
   * Gap #4/#13: Token refresh must go through the Next.js server-side proxy
   * (/api/auth/refresh) which reads the httpOnly refresh_token cookie.
   * Calling /api/v1/auth/refresh directly from client-side JS would fail
   * because the httpOnly cookie is not accessible to JavaScript.
   */
  async refreshToken() {
    const response = await fetch('/api/auth/refresh', { method: 'POST', credentials: 'include' });
    if (!response.ok) {
      throw new Error('Token refresh failed');
    }
    return response.json() as Promise<{ success: boolean; access_token: string }>;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Operations API
  // ═══════════════════════════════════════════════════════════════════════════

  async getFields(tenantId: string, options?: { limit?: number; offset?: number }) {
    return this.request<Field[]>(FIELD_ENDPOINTS.LIST, {
      params: {
        tenantId,
        limit: String(options?.limit || 100),
        offset: String(options?.offset || 0),
      },
    });
  }

  async getField(fieldId: string) {
    return this.request<Field>(buildUrl(FIELD_ENDPOINTS.GET, { fieldId }));
  }

  async createField(data: FieldCreateRequest) {
    return this.request<Field>(FIELD_ENDPOINTS.LIST, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateField(fieldId: string, data: FieldUpdateRequest, etag?: string) {
    const headers: Record<string, string> = {};
    if (etag) {
      headers['If-Match'] = etag;
    }
    return this.request<Field>(buildUrl(FIELD_ENDPOINTS.GET, { fieldId }), {
      method: 'PUT',
      body: JSON.stringify(data),
      headers,
    });
  }

  async deleteField(fieldId: string) {
    return this.request<void>(buildUrl(FIELD_ENDPOINTS.GET, { fieldId }), {
      method: 'DELETE',
    });
  }

  async getNearbyFields(lat: number, lng: number, radius: number = 5000) {
    if (lat < -90 || lat > 90) {
      return { success: false as const, error: 'Latitude must be between -90 and 90' };
    }
    if (lng < -180 || lng > 180) {
      return { success: false as const, error: 'Longitude must be between -180 and 180' };
    }
    if (radius <= 0 || !isFinite(radius)) {
      return { success: false as const, error: 'Radius must be a positive finite number' };
    }
    return this.request<Field[]>(FIELD_ENDPOINTS.NEARBY, {
      params: {
        lat: String(lat),
        lng: String(lng),
        radius: String(radius),
      },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Analysis API
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldNdvi(fieldId: string) {
    return this.request<NdviData>(buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId }));
  }

  async getNdviSummary(tenantId: string) {
    return this.request<NdviSummary>(SATELLITE_ENDPOINTS.NDVI_SUMMARY, {
      params: { tenantId },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather API (weather-service on port 8092)
  // Kong route: /api/v1/weather → strips to / → service has /weather/* endpoints
  // ═══════════════════════════════════════════════════════════════════════════

  async getWeather(lat: number, lng: number, fieldId: string = 'default') {
    return this.request<WeatherData>(WEATHER_ENDPOINTS.KONG_CURRENT, {
      method: 'POST',
      body: JSON.stringify({
        field_id: fieldId,
        lat,
        lon: lng,
      }),
    });
  }

  async getWeatherForecast(
    lat: number,
    lng: number,
    days: number = 7,
    fieldId: string = 'default'
  ) {
    return this.request<WeatherForecast>(WEATHER_ENDPOINTS.KONG_FORECAST, {
      method: 'POST',
      body: JSON.stringify({
        field_id: fieldId,
        lat,
        lon: lng,
        days,
      }),
    });
  }

  async getAgriculturalRisks(lat: number, lng: number, fieldId: string = 'default') {
    return this.request<AgriculturalRisk[]>(WEATHER_ENDPOINTS.KONG_AGRICULTURAL_REPORT, {
      method: 'POST',
      body: JSON.stringify({
        field_id: fieldId,
        lat,
        lon: lng,
      }),
    });
  }

  // Weather Advanced API (location_id based - for Yemen locations)
  // Kong route: /api/v1/weather → strips to / → service has /v1/* endpoints
  async getWeatherByLocation(locationId: string) {
    return this.request<WeatherData>(buildUrl(WEATHER_ENDPOINTS.KONG_CURRENT_BY_LOCATION, { locationId }));
  }

  async getWeatherForecastByLocation(locationId: string, days: number = 7) {
    return this.request<WeatherForecast>(`${buildUrl(WEATHER_ENDPOINTS.KONG_FORECAST_BY_LOCATION, { locationId })}?days=${days}`);
  }

  async getWeatherLocations(): Promise<ApiResponse<unknown>> {
    return this.request(WEATHER_ENDPOINTS.KONG_LOCATIONS);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Crop Health AI API
  // ═══════════════════════════════════════════════════════════════════════════

  async analyzeCropHealth(imageFile: File): Promise<ApiResponse<CropHealthAnalysis>> {
    // Validate file type by MIME type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(imageFile.type)) {
      return {
        success: false,
        error: 'Invalid file type. Please upload a JPEG, PNG, or WebP image.',
      };
    }

    // Validate file extension as a secondary check against extension spoofing
    const allowedExtensions = /\.(jpg|jpeg|png|webp)$/i;
    if (!allowedExtensions.test(imageFile.name)) {
      return {
        success: false,
        error: 'Invalid file extension. Please upload a JPEG, PNG, or WebP image.',
      };
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (imageFile.size > maxSize) {
      return {
        success: false,
        error: 'File size exceeds 10MB limit.',
      };
    }

    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const response = await unifiedApiClient.post(CROP_HEALTH_ENDPOINTS.INTELLIGENCE_ANALYZE, formData, {
        timeout: 60000, // 60 second timeout for image upload
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      return response.data as ApiResponse<CropHealthAnalysis>;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const data = error.response?.data;
        if (error.code === 'ECONNABORTED') {
          return {
            success: false,
            error: 'Upload timeout - please try again with a smaller image',
          };
        }
        return {
          success: false,
          error: data?.error || data?.message || 'Failed to analyze image',
        };
      }
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // IoT Sensors API
  // ═══════════════════════════════════════════════════════════════════════════

  async getSensorData(fieldId: string) {
    return this.request<Sensor[]>(buildUrl(IOT_ENDPOINTS.FIELD_SENSORS, { fieldId }));
  }

  async getSensorHistory(sensorId: string, from: Date, to: Date) {
    return this.request<SensorReading[]>(buildUrl(IOT_ENDPOINTS.SENSOR_HISTORY, { sensorId }), {
      params: {
        from: from.toISOString(),
        to: to.toISOString(),
      },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation API
  // ═══════════════════════════════════════════════════════════════════════════

  async getIrrigationSchedules() {
    return this.request<IrrigationSchedule[]>(IRRIGATION_ENDPOINTS.SCHEDULES_LIST);
  }

  async createIrrigationSchedule(data: IrrigationScheduleCreate) {
    return this.request<IrrigationSchedule>(IRRIGATION_ENDPOINTS.SCHEDULES_LIST, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateIrrigationSchedule(id: string, data: Partial<IrrigationScheduleCreate>) {
    return this.request<IrrigationSchedule>(buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_GET, { scheduleId: id }), {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteIrrigationSchedule(id: string) {
    return this.request<void>(buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_GET, { scheduleId: id }), {
      method: 'DELETE',
    });
  }

  async startIrrigationSchedule(id: string) {
    return this.request<IrrigationSchedule>(buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_GET, { scheduleId: id }), {
      method: 'PUT',
      body: JSON.stringify({ status: 'active' }),
    });
  }

  async stopIrrigationSchedule(id: string) {
    return this.request<IrrigationSchedule>(buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_GET, { scheduleId: id }), {
      method: 'PUT',
      body: JSON.stringify({ status: 'paused' }),
    });
  }

  async getIrrigationRecommendation(fieldId: string) {
    return this.request<IrrigationRecommendation>(
      buildUrl(IRRIGATION_ENDPOINTS.RECOMMENDATION, { fieldId })
    );
  }

  async calculateET0(data: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    solarRadiation: number;
  }) {
    return this.request<ET0Calculation>(IRRIGATION_ENDPOINTS.ET0, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Fertilizer Advisor API
  // ═══════════════════════════════════════════════════════════════════════════

  async getFertilizerRecommendation(data: {
    cropType: string;
    growthStage: string;
    soilType: string;
    soilAnalysis?: {
      nitrogen: number;
      phosphorus: number;
      potassium: number;
      ph: number;
    };
  }) {
    return this.request<FertilizerRecommendation>(ADVISORY_ENDPOINTS.RECOMMEND, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Growing Degree Days (GDD) API
  // Kong route: /api/v1/weather → weather-service:8092
  // ═══════════════════════════════════════════════════════════════════════════

  async getGDDData() {
    return this.request<GDDRecord[]>(WEATHER_ENDPOINTS.GDD);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Spray Management API
  // Kong route: /api/v1/weather → weather-service:8092 (spray windows)
  //             /api/v1/advisory → advisory-service:8093 (spray history)
  // ═══════════════════════════════════════════════════════════════════════════

  async getSprayWindows() {
    return this.request<SprayWindow[]>(WEATHER_ENDPOINTS.SPRAY_WINDOWS);
  }

  async getSprayHistory(params?: { limit?: number }) {
    const queryParams = params?.limit ? { limit: String(params.limit) } : undefined;
    return this.request<SprayHistoryRecord[]>(ADVISORY_ENDPOINTS.SPRAY_HISTORY, {
      params: queryParams,
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync API (for Mobile)
  // ═══════════════════════════════════════════════════════════════════════════

  async syncFields(tenantId: string, since?: string) {
    const params: Record<string, string> = { tenantId };
    if (since) params.since = since;

    return this.request<any>(FIELD_ENDPOINTS.SYNC, { params });
  }

  async batchSync(data: { deviceId: string; userId: string; tenantId: string; fields: any[] }) {
    return this.request<any>(FIELD_ENDPOINTS.SYNC_BATCH, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Advisory Service API (خدمة الاستشارات - port 8093)
  // Kong route: /api/v1/advisory → advisory-service:8093
  // ═══════════════════════════════════════════════════════════════════════════

  async getAgroAdvice(data: {
    fieldId: string;
    cropType: string;
    currentConditions: {
      temperature?: number;
      humidity?: number;
      soilMoisture?: number;
    };
  }) {
    return this.request<any>(ADVISORY_ENDPOINTS.ADVICE, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDiseaseDetection(cropType: string, symptoms: string[]) {
    return this.request<any>(ADVISORY_ENDPOINTS.DISEASE, {
      method: 'POST',
      body: JSON.stringify({ cropType, symptoms }),
    });
  }

  async getNutrientRecommendation(data: {
    cropType: string;
    growthStage: string;
    soilAnalysis: any;
  }) {
    return this.request<any>(ADVISORY_ENDPOINTS.NUTRIENTS, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Agro Rules — REMOVED: agro-rules is a NATS-only worker with no HTTP port.
  // These methods called /api/v1/agro-rules/* which has no Kong route.
  // IoT automation rules are handled via NATS events, not REST.
  // ═══════════════════════════════════════════════════════════════════════════

  // ═══════════════════════════════════════════════════════════════════════════
  // Chat Service API (خدمة المحادثات - port 8115)
  // Kong route: /api/v1/chat → chat-service:8115
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldMessages(fieldId: string, options?: { limit?: number; offset?: number }) {
    return this.request<any[]>(buildUrl(CHAT_ENDPOINTS.FIELD_MESSAGES_V2, { fieldId }), {
      params: {
        limit: String(options?.limit || 50),
        offset: String(options?.offset || 0),
      },
    });
  }

  async sendFieldMessage(fieldId: string, message: string) {
    // Sanitize message to prevent XSS using comprehensive sanitizer
    const sanitizedMessage = sanitizers.html(message);

    // Validate message is safe text
    if (!validators.safeText(sanitizedMessage)) {
      return {
        success: false,
        error: validationErrors.unsafeText,
      };
    }

    // Validate message length
    if (sanitizedMessage.length === 0) {
      return {
        success: false,
        error: validationErrors.required,
      };
    }

    if (sanitizedMessage.length > 2000) {
      return {
        success: false,
        error: validationErrors.tooLong,
      };
    }

    return this.request<any>(buildUrl(CHAT_ENDPOINTS.FIELD_MESSAGES_V2, { fieldId }), {
      method: 'POST',
      body: JSON.stringify({ message: sanitizedMessage }),
    });
  }

  async getFieldChatParticipants(fieldId: string) {
    return this.request<any[]>(buildUrl(CHAT_ENDPOINTS.FIELD_PARTICIPANTS_V2, { fieldId }));
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Management Service API (خدمة إدارة الحقول - port 3000)
  // Kong route: /api/v1/fields → field-management-service:3000
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldBoundary(fieldId: string) {
    return this.request<any>(buildUrl(FIELD_ENDPOINTS.BOUNDARY, { fieldId }));
  }

  async updateFieldBoundary(fieldId: string, boundary: any, etag?: string) {
    const headers: Record<string, string> = {};
    if (etag) headers['If-Match'] = etag;

    return this.request<any>(buildUrl(FIELD_ENDPOINTS.BOUNDARY, { fieldId }), {
      method: 'PUT',
      body: JSON.stringify({ boundary }),
      headers,
    });
  }

  async getFieldBoundaryHistory(fieldId: string) {
    return this.request<any[]>(buildUrl(FIELD_ENDPOINTS.BOUNDARY_HISTORY, { fieldId }));
  }

  async rollbackFieldBoundary(fieldId: string, historyId: string, reason?: string) {
    return this.request<any>(buildUrl(FIELD_ENDPOINTS.BOUNDARY_ROLLBACK, { fieldId }), {
      method: 'POST',
      body: JSON.stringify({ historyId, reason }),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Equipment Service API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getEquipment(tenantId: string) {
    return this.request<Equipment[]>(EQUIPMENT_ENDPOINTS.LIST, {
      params: { tenantId },
    });
  }

  async getEquipmentById(equipmentId: string) {
    return this.request<Equipment>(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId }));
  }

  async createEquipment(data: {
    name: string;
    type: string;
    tenantId: string;
    specifications?: any;
  }) {
    return this.request<Equipment>(EQUIPMENT_ENDPOINTS.LIST, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateEquipmentStatus(equipmentId: string, status: string) {
    return this.request<Equipment>(buildUrl(EQUIPMENT_ENDPOINTS.STATUS, { equipmentId }), {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async getEquipmentMaintenanceSchedule(equipmentId: string) {
    return this.request<MaintenanceSchedule[]>(buildUrl(EQUIPMENT_ENDPOINTS.MAINTENANCE, { equipmentId }));
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Task Service API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getTasks(options: {
    tenantId?: string;
    fieldId?: string;
    userId?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) {
    const params: Record<string, string> = {};
    if (options.tenantId) params.tenantId = options.tenantId;
    if (options.fieldId) params.fieldId = options.fieldId;
    if (options.userId) params.userId = options.userId;
    if (options.status) params.status = options.status;
    if (options.limit) params.limit = String(options.limit);
    if (options.offset) params.offset = String(options.offset);

    return this.request<Task[]>(TASK_ENDPOINTS.LIST, { params });
  }

  async getTask(taskId: string) {
    return this.request<Task>(buildUrl(TASK_ENDPOINTS.GET, { taskId }));
  }

  async updateTask(
    taskId: string,
    data: { status?: string; title?: string; description?: string }
  ) {
    return this.request<Task>(buildUrl(TASK_ENDPOINTS.GET, { taskId }), {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async createTask(data: TaskCreateRequest) {
    return this.request<Task>(TASK_ENDPOINTS.LIST, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTaskStatus(
    taskId: string,
    status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  ) {
    return this.request<Task>(buildUrl(TASK_ENDPOINTS.STATUS, { taskId }), {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async completeTask(taskId: string, notes?: string) {
    return this.request<Task>(buildUrl(TASK_ENDPOINTS.COMPLETE, { taskId }), {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  async deleteTask(taskId: string) {
    return this.request<void>(buildUrl(TASK_ENDPOINTS.GET, { taskId }), {
      method: 'DELETE',
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Alerts API
  // ═══════════════════════════════════════════════════════════════════════════

  async getAlerts(options: { tenantId?: string; status?: string; fieldId?: string }) {
    const params: Record<string, string> = {};
    if (options.tenantId) params.tenantId = options.tenantId;
    if (options.status) params.status = options.status;
    if (options.fieldId) params.fieldId = options.fieldId;

    return this.request<any[]>(ALERT_ENDPOINTS.LIST, { params });
  }

  async acknowledgeAlert(alertId: string) {
    return this.request<any>(buildUrl(ALERT_ENDPOINTS.ACKNOWLEDGE, { alertId }), {
      method: 'POST',
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // WebSocket Gateway API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  getWebSocketUrl(): string {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    const wsProtocol = baseUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = baseUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${wsHost}/ws`;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Provider Config API (provider-config service, port 8104)
  // Kong route: /api/v1/provider-config  (was incorrectly /api/v1/providers)
  // ═══════════════════════════════════════════════════════════════════════════

  async getProviders() {
    return this.request<any[]>(PROVIDER_ENDPOINTS.PROVIDER_CONFIG_LIST);
  }

  async getProviderConfig(providerId: string) {
    return this.request<any>(buildUrl(PROVIDER_ENDPOINTS.PROVIDER_CONFIG_ITEM, { providerId }));
  }

  async updateProviderConfig(providerId: string, config: any) {
    return this.request<any>(buildUrl(PROVIDER_ENDPOINTS.PROVIDER_CONFIG_ITEM, { providerId }), {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Crop Intelligence API (خدمة ذكاء المحاصيل - مع OpenAPI)
  // ═══════════════════════════════════════════════════════════════════════════

  async getCropHealthDecision(data: {
    cropType: string;
    ndviValue: number;
    weatherConditions: any;
    soilMoisture?: number;
  }) {
    return this.request<any>(CROP_HEALTH_ENDPOINTS.INTELLIGENCE_DECISION, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCropHealthHistory(fieldId: string, days: number = 30) {
    return this.request<any[]>(buildUrl(CROP_HEALTH_ENDPOINTS.INTELLIGENCE_HISTORY, { fieldId }), {
      params: { days: String(days) },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Satellite Service API (vegetation-analysis-service)
  // Kong route: /api/v1/satellite → strips to / → service has /v1/* endpoints
  // ═══════════════════════════════════════════════════════════════════════════

  async getSatelliteImagery(fieldId: string, options?: { from?: string; to?: string }) {
    // Maps to vegetation-analysis-service /v1/timeseries/{field_id}
    // Filter out undefined values to prevent "undefined" string in query params
    const params = options
      ? Object.fromEntries(Object.entries(options).filter(([, v]) => v != null))
      : undefined;
    return this.request<any[]>(buildUrl(SATELLITE_ENDPOINTS.TIMESERIES, { fieldId }), {
      params: params as Record<string, string>,
    });
  }

  async requestSatelliteAnalysis(fieldId: string, analysisType: 'ndvi' | 'moisture' | 'thermal') {
    // Maps to vegetation-analysis-service /v1/analyze (POST)
    return this.request<any>(SATELLITE_ENDPOINTS.ANALYZE, {
      method: 'POST',
      body: JSON.stringify({ field_id: fieldId, analysis_type: analysisType }),
    });
  }

  async getSatelliteIndices(fieldId: string) {
    // Maps to vegetation-analysis-service /v1/indices/{field_id}
    return this.request<any>(buildUrl(SATELLITE_ENDPOINTS.INDICES, { fieldId }));
  }

  async getSatelliteSatellites() {
    // Maps to vegetation-analysis-service /v1/satellites
    return this.request<any>(SATELLITE_ENDPOINTS.SATELLITES);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Marketplace API
  // ═══════════════════════════════════════════════════════════════════════════

  async getMarketplaceListings(options?: { category?: string; region?: string }) {
    const params = options
      ? Object.fromEntries(Object.entries(options).filter(([, v]) => v != null))
      : undefined;
    return this.request<MarketplaceListing[]>(MARKETPLACE_ENDPOINTS.LISTINGS, {
      params: params as Record<string, string>,
    });
  }

  async createListing(data: {
    title: string;
    description: string;
    category: string;
    price: number;
    quantity: number;
    unit: string;
  }) {
    return this.request<MarketplaceListing>(MARKETPLACE_ENDPOINTS.LISTINGS, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Billing Core API
  // ═══════════════════════════════════════════════════════════════════════════

  async getSubscription(tenantId: string) {
    return this.request<Subscription>(buildUrl(BILLING_ENDPOINTS.TENANT_SUBSCRIPTION, { tenantId }));
  }

  async getInvoices(tenantId: string) {
    return this.request<Invoice[]>(buildUrl(BILLING_ENDPOINTS.TENANT_INVOICES, { tenantId }));
  }

  async getUsageStats(tenantId: string) {
    return this.request<any>(buildUrl(BILLING_ENDPOINTS.TENANT_USAGE, { tenantId }));
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Yield Prediction API
  // ═══════════════════════════════════════════════════════════════════════════

  async predictYield(fieldId: string) {
    return this.request<any>(buildUrl(YIELD_ENDPOINTS.PREDICT, { fieldId }));
  }

  async getYieldHistory(fieldId: string) {
    return this.request<any[]>(buildUrl(YIELD_ENDPOINTS.HISTORY, { fieldId }));
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Disaster Assessment API (disaster-assessment service, port 3020)
  // Kong route: /api/v1/disaster  (was incorrectly /api/v1/disasters — note: singular)
  // ═══════════════════════════════════════════════════════════════════════════

  async assessDisaster(fieldId: string, disasterType: string) {
    return this.request<any>(DISASTER_ENDPOINTS.ASSESS_SINGULAR, {
      method: 'POST',
      body: JSON.stringify({ fieldId, disasterType }),
    });
  }

  async getDisasterAlerts(region: string) {
    return this.request<any[]>(DISASTER_ENDPOINTS.ALERTS_SINGULAR, {
      params: { region },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Intelligence API
  // ═══════════════════════════════════════════════════════════════════════════

  async getLivingFieldScore(fieldId: string) {
    return this.request<any>(buildUrl(INTELLIGENCE_ENDPOINTS.FIELD_SCORE, { fieldId }));
  }

  async getFieldZones(fieldId: string) {
    return this.request<any[]>(buildUrl(INTELLIGENCE_ENDPOINTS.FIELD_ZONES, { fieldId }));
  }

  async getFieldIntelligenceAlerts(fieldId: string) {
    return this.request<any[]>(buildUrl(INTELLIGENCE_ENDPOINTS.FIELD_ALERTS, { fieldId }), {
      params: { status: 'active' },
    });
  }

  async createTaskFromAlert(
    alertId: string,
    taskData: {
      title: string;
      titleAr: string;
      description?: string;
      descriptionAr?: string;
      priority: 'urgent' | 'high' | 'medium' | 'low';
      dueDate?: string;
      assigneeId?: string;
    }
  ) {
    return this.request<any>(buildUrl(INTELLIGENCE_ENDPOINTS.CREATE_TASK, { alertId }), {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async getBestDaysForActivity(activity: string, days: number = 14) {
    return this.request<any[]>(INTELLIGENCE_ENDPOINTS.BEST_DAYS, {
      params: {
        activity: activity.toLowerCase(),
        days: String(Math.max(1, Math.min(days, 30))),
      },
    });
  }

  async validateTaskDate(date: string, activity: string) {
    return this.request<any>(INTELLIGENCE_ENDPOINTS.VALIDATE_DATE, {
      method: 'POST',
      body: JSON.stringify({
        date: new Date(date).toISOString(),
        activity: activity.toLowerCase(),
      }),
    });
  }

  async getFieldRecommendations(fieldId: string) {
    return this.request<any[]>(buildUrl(INTELLIGENCE_ENDPOINTS.FIELD_RECOMMENDATIONS, { fieldId }));
  }
}

// Singleton instance
export const apiClient = new SahoolApiClient();
export default apiClient;
