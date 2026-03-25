/**
 * SAHOOL API Client
 * Domain-specific API methods for the web frontend.
 *
 * Transport layer is delegated to the unified client (@sahool/api-client),
 * which provides: JWT auth, token refresh, CSRF, retry, HTTPS enforcement.
 * This file only contains domain method wrappers.
 */

import axios from 'axios';
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
    }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: sanitizedEmail, password }),
      // Auth requests don't need retry (handled by unified client's interceptors)
    });
  }

  async getCurrentUser() {
    return this.request<User>('/api/v1/auth/me');
  }

  async refreshToken(refreshToken: string) {
    return this.request<{ access_token: string }>('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Operations API
  // ═══════════════════════════════════════════════════════════════════════════

  async getFields(tenantId: string, options?: { limit?: number; offset?: number }) {
    return this.request<Field[]>('/api/v1/fields', {
      params: {
        tenantId,
        limit: String(options?.limit || 100),
        offset: String(options?.offset || 0),
      },
    });
  }

  async getField(fieldId: string) {
    return this.request<Field>(`/api/v1/fields/${fieldId}`);
  }

  async createField(data: FieldCreateRequest) {
    return this.request<Field>('/api/v1/fields', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateField(fieldId: string, data: FieldUpdateRequest, etag?: string) {
    const headers: Record<string, string> = {};
    if (etag) {
      headers['If-Match'] = etag;
    }
    return this.request<Field>(`/api/v1/fields/${fieldId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
      headers,
    });
  }

  async deleteField(fieldId: string) {
    return this.request<void>(`/api/v1/fields/${fieldId}`, {
      method: 'DELETE',
    });
  }

  async getNearbyFields(lat: number, lng: number, radius: number = 5000) {
    return this.request<Field[]>('/api/v1/fields/nearby', {
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
    return this.request<NdviData>(`/api/v1/fields/${fieldId}/ndvi`);
  }

  async getNdviSummary(tenantId: string) {
    return this.request<NdviSummary>('/api/v1/ndvi/summary', {
      params: { tenantId },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather API (weather-service on port 8092)
  // Kong route: /api/v1/weather → strips to / → service has /weather/* endpoints
  // ═══════════════════════════════════════════════════════════════════════════

  async getWeather(lat: number, lng: number, fieldId: string = 'default') {
    return this.request<WeatherData>('/api/v1/weather/weather/current', {
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
    return this.request<WeatherForecast>('/api/v1/weather/weather/forecast', {
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
    return this.request<AgriculturalRisk[]>('/api/v1/weather/weather/agricultural-report', {
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
    return this.request<WeatherData>(`/api/v1/weather/v1/current/${locationId}`);
  }

  async getWeatherForecastByLocation(locationId: string, days: number = 7) {
    return this.request<WeatherForecast>(`/api/v1/weather/v1/forecast/${locationId}?days=${days}`);
  }

  async getWeatherLocations(): Promise<ApiResponse<unknown>> {
    return this.request('/api/v1/weather/v1/locations');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Crop Health AI API
  // ═══════════════════════════════════════════════════════════════════════════

  async analyzeCropHealth(imageFile: File): Promise<ApiResponse<CropHealthAnalysis>> {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(imageFile.type)) {
      return {
        success: false,
        error: 'Invalid file type. Please upload a JPEG, PNG, or WebP image.',
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
      const response = await unifiedApiClient.post('/api/v1/crop-intelligence/analyze', formData, {
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
    return this.request<Sensor[]>(`/api/v1/iot/fields/${fieldId}/sensors`);
  }

  async getSensorHistory(sensorId: string, from: Date, to: Date) {
    return this.request<SensorReading[]>(`/api/v1/iot/sensors/${sensorId}/history`, {
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
    return this.request<IrrigationSchedule[]>("/api/v1/irrigation/schedules");
  }

  async createIrrigationSchedule(data: IrrigationScheduleCreate) {
    return this.request<IrrigationSchedule>("/api/v1/irrigation/schedules", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateIrrigationSchedule(id: string, data: Partial<IrrigationScheduleCreate>) {
    return this.request<IrrigationSchedule>(`/api/v1/irrigation/schedules/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteIrrigationSchedule(id: string) {
    return this.request<void>(`/api/v1/irrigation/schedules/${id}`, {
      method: "DELETE",
    });
  }

  async startIrrigationSchedule(id: string) {
    return this.request<IrrigationSchedule>(`/api/v1/irrigation/schedules/${id}`, {
      method: "PUT",
      body: JSON.stringify({ status: "active" }),
    });
  }

  async stopIrrigationSchedule(id: string) {
    return this.request<IrrigationSchedule>(`/api/v1/irrigation/schedules/${id}`, {
      method: "PUT",
      body: JSON.stringify({ status: "paused" }),
    });
  }

  async getIrrigationRecommendation(fieldId: string) {
    return this.request<IrrigationRecommendation>(
      `/api/v1/irrigation/fields/${fieldId}/recommendation`
    );
  }

  async calculateET0(data: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    solarRadiation: number;
  }) {
    return this.request<ET0Calculation>('/api/v1/irrigation/et0', {
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
    return this.request<FertilizerRecommendation>('/api/v1/fertilizer/recommend', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync API (for Mobile)
  // ═══════════════════════════════════════════════════════════════════════════

  async syncFields(tenantId: string, since?: string) {
    const params: Record<string, string> = { tenantId };
    if (since) params.since = since;

    return this.request<any>('/api/v1/fields/sync', { params });
  }

  async batchSync(data: { deviceId: string; userId: string; tenantId: string; fields: any[] }) {
    return this.request<any>('/api/v1/fields/sync/batch', {
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
    return this.request<any>('/api/v1/advisory/advice', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDiseaseDetection(cropType: string, symptoms: string[]) {
    return this.request<any>('/api/v1/advisory/disease', {
      method: 'POST',
      body: JSON.stringify({ cropType, symptoms }),
    });
  }

  async getNutrientRecommendation(data: {
    cropType: string;
    growthStage: string;
    soilAnalysis: any;
  }) {
    return this.request<any>('/api/v1/advisory/nutrients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Agro Rules API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getIoTRules(fieldId: string) {
    return this.request<any>(`/api/v1/agro-rules/fields/${fieldId}/rules`);
  }

  async createIoTRule(data: {
    fieldId: string;
    condition: string;
    action: string;
    threshold: number;
  }) {
    return this.request<any>('/api/v1/agro-rules/rules', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async triggerRule(ruleId: string) {
    return this.request<any>(`/api/v1/agro-rules/rules/${ruleId}/trigger`, {
      method: 'POST',
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Chat Service API (خدمة المحادثات - port 8115)
  // Kong route: /api/v1/chat → chat-service:8115
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldMessages(fieldId: string, options?: { limit?: number; offset?: number }) {
    return this.request<any[]>(`/api/v1/chat/fields/${fieldId}/messages`, {
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

    return this.request<any>(`/api/v1/chat/fields/${fieldId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message: sanitizedMessage }),
    });
  }

  async getFieldChatParticipants(fieldId: string) {
    return this.request<any[]>(`/api/v1/chat/fields/${fieldId}/participants`);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Management Service API (خدمة إدارة الحقول - port 3000)
  // Kong route: /api/v1/fields → field-management-service:3000
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldBoundary(fieldId: string) {
    return this.request<any>(`/api/v1/fields/${fieldId}/boundary`);
  }

  async updateFieldBoundary(fieldId: string, boundary: any, etag?: string) {
    const headers: Record<string, string> = {};
    if (etag) headers['If-Match'] = etag;

    return this.request<any>(`/api/v1/fields/${fieldId}/boundary`, {
      method: 'PUT',
      body: JSON.stringify({ boundary }),
      headers,
    });
  }

  async getFieldBoundaryHistory(fieldId: string) {
    return this.request<any[]>(`/api/v1/fields/${fieldId}/boundary-history`);
  }

  async rollbackFieldBoundary(fieldId: string, historyId: string, reason?: string) {
    return this.request<any>(`/api/v1/fields/${fieldId}/boundary-history/rollback`, {
      method: 'POST',
      body: JSON.stringify({ historyId, reason }),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Equipment Service API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getEquipment(tenantId: string) {
    return this.request<Equipment[]>('/api/v1/equipment', {
      params: { tenantId },
    });
  }

  async getEquipmentById(equipmentId: string) {
    return this.request<Equipment>(`/api/v1/equipment/${equipmentId}`);
  }

  async createEquipment(data: {
    name: string;
    type: string;
    tenantId: string;
    specifications?: any;
  }) {
    return this.request<Equipment>('/api/v1/equipment', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateEquipmentStatus(equipmentId: string, status: string) {
    return this.request<Equipment>(`/api/v1/equipment/${equipmentId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async getEquipmentMaintenanceSchedule(equipmentId: string) {
    return this.request<MaintenanceSchedule[]>(`/api/v1/equipment/${equipmentId}/maintenance`);
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

    return this.request<Task[]>('/api/v1/tasks', { params });
  }

  async getTask(taskId: string) {
    return this.request<Task>(`/api/v1/tasks/${taskId}`);
  }

  async updateTask(
    taskId: string,
    data: { status?: string; title?: string; description?: string }
  ) {
    return this.request<Task>(`/api/v1/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async createTask(data: TaskCreateRequest) {
    return this.request<Task>('/api/v1/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTaskStatus(
    taskId: string,
    status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  ) {
    return this.request<Task>(`/api/v1/tasks/${taskId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async completeTask(taskId: string, notes?: string) {
    return this.request<Task>(`/api/v1/tasks/${taskId}/complete`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  async deleteTask(taskId: string) {
    return this.request<void>(`/api/v1/tasks/${taskId}`, {
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

    return this.request<any[]>('/api/v1/alerts', { params });
  }

  async acknowledgeAlert(alertId: string) {
    return this.request<any>(`/api/v1/alerts/${alertId}/acknowledge`, {
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
  // Provider Config API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getProviders() {
    return this.request<any[]>('/api/v1/providers');
  }

  async getProviderConfig(providerId: string) {
    return this.request<any>(`/api/v1/providers/${providerId}/config`);
  }

  async updateProviderConfig(providerId: string, config: any) {
    return this.request<any>(`/api/v1/providers/${providerId}/config`, {
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
    return this.request<any>('/api/v1/crop-intelligence/decision', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCropHealthHistory(fieldId: string, days: number = 30) {
    return this.request<any[]>(`/api/v1/crop-intelligence/fields/${fieldId}/history`, {
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
    return this.request<any[]>(`/api/v1/satellite/v1/timeseries/${fieldId}`, {
      params: params as Record<string, string>,
    });
  }

  async requestSatelliteAnalysis(fieldId: string, analysisType: 'ndvi' | 'moisture' | 'thermal') {
    // Maps to vegetation-analysis-service /v1/analyze (POST)
    return this.request<any>(`/api/v1/satellite/v1/analyze`, {
      method: 'POST',
      body: JSON.stringify({ field_id: fieldId, analysis_type: analysisType }),
    });
  }

  async getSatelliteIndices(fieldId: string) {
    // Maps to vegetation-analysis-service /v1/indices/{field_id}
    return this.request<any>(`/api/v1/satellite/v1/indices/${fieldId}`);
  }

  async getSatelliteSatellites() {
    // Maps to vegetation-analysis-service /v1/satellites
    return this.request<any>(`/api/v1/satellite/v1/satellites`);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Marketplace API
  // ═══════════════════════════════════════════════════════════════════════════

  async getMarketplaceListings(options?: { category?: string; region?: string }) {
    const params = options
      ? Object.fromEntries(Object.entries(options).filter(([, v]) => v != null))
      : undefined;
    return this.request<MarketplaceListing[]>('/api/v1/marketplace/listings', {
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
    return this.request<MarketplaceListing>('/api/v1/marketplace/listings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Billing Core API
  // ═══════════════════════════════════════════════════════════════════════════

  async getSubscription(tenantId: string) {
    return this.request<Subscription>(`/api/v1/billing/tenants/${tenantId}/subscription`);
  }

  async getInvoices(tenantId: string) {
    return this.request<Invoice[]>(`/api/v1/billing/tenants/${tenantId}/invoices`);
  }

  async getUsageStats(tenantId: string) {
    return this.request<any>(`/api/v1/billing/tenants/${tenantId}/usage`);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Yield Prediction API
  // ═══════════════════════════════════════════════════════════════════════════

  async predictYield(fieldId: string) {
    return this.request<any>(`/api/v1/yield/fields/${fieldId}/predict`);
  }

  async getYieldHistory(fieldId: string) {
    return this.request<any[]>(`/api/v1/yield/fields/${fieldId}/history`);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Disaster Assessment API
  // ═══════════════════════════════════════════════════════════════════════════

  async assessDisaster(fieldId: string, disasterType: string) {
    return this.request<any>('/api/v1/disasters/assess', {
      method: 'POST',
      body: JSON.stringify({ fieldId, disasterType }),
    });
  }

  async getDisasterAlerts(region: string) {
    return this.request<any[]>('/api/v1/disasters/alerts', {
      params: { region },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Intelligence API
  // ═══════════════════════════════════════════════════════════════════════════

  async getLivingFieldScore(fieldId: string) {
    return this.request<any>(`/api/v1/fields/${fieldId}/intelligence/score`);
  }

  async getFieldZones(fieldId: string) {
    return this.request<any[]>(`/api/v1/fields/${fieldId}/intelligence/zones`);
  }

  async getFieldIntelligenceAlerts(fieldId: string) {
    return this.request<any[]>(`/api/v1/fields/${fieldId}/intelligence/alerts`, {
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
    return this.request<any>(`/api/v1/intelligence/alerts/${alertId}/create-task`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async getBestDaysForActivity(activity: string, days: number = 14) {
    return this.request<any[]>('/api/v1/intelligence/best-days', {
      params: {
        activity: activity.toLowerCase(),
        days: String(Math.max(1, Math.min(days, 30))),
      },
    });
  }

  async validateTaskDate(date: string, activity: string) {
    return this.request<any>('/api/v1/intelligence/validate-date', {
      method: 'POST',
      body: JSON.stringify({
        date: new Date(date).toISOString(),
        activity: activity.toLowerCase(),
      }),
    });
  }

  async getFieldRecommendations(fieldId: string) {
    return this.request<any[]>(`/api/v1/fields/${fieldId}/intelligence/recommendations`);
  }
}

// Singleton instance
export const apiClient = new SahoolApiClient();
export default apiClient;
