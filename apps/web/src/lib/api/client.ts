/**
 * SAHOOL API Client
 * Unified API client for connecting frontend to backend services
 */

import type {
  ApiResponse,
  Field,
  FieldCreateRequest,
  FieldUpdateRequest,
  NdviData,
  NdviSummary,
  WeatherData,
  WeatherForecast,
  AgriculturalRisk,
  Sensor,
  SensorReading,
  IrrigationRecommendation,
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
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Enforce HTTPS in production (only at runtime in browser, not during build)
if (
  typeof window !== 'undefined' &&
  process.env.NODE_ENV === 'production' &&
  !API_BASE_URL.startsWith('https://') &&
  !API_BASE_URL.includes('localhost')
) {
  console.warn('Warning: API_BASE_URL should use HTTPS in production environment');
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
  skipRetry?: boolean;
  timeout?: number;
}

// Configuration
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 1000; // 1 second

// Helper function to sanitize HTML and prevent XSS
function sanitizeInput(input: string): string {
  if (typeof input !== 'string') return input;
  return input
    .replace(/[<>]/g, '') // Remove < and > to prevent HTML injection
    .trim();
}

// Helper function to delay for retry logic
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class SahoolApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const { params, skipRetry = false, timeout = DEFAULT_TIMEOUT, ...fetchOptions } = options;

    // Build URL with query params
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    // Set headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    // Retry logic
    let lastError: Error | null = null;
    const maxAttempts = skipRetry ? 1 : MAX_RETRY_ATTEMPTS;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          ...fetchOptions,
          headers,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Parse response
        let data: any;
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
          try {
            data = await response.json();
          } catch (parseError) {
            return {
              success: false,
              error: 'Invalid JSON response from server',
            };
          }
        } else {
          data = await response.text();
        }

        // Handle HTTP errors
        if (!response.ok) {
          // Don't retry client errors (4xx), only server errors (5xx) and network issues
          if (response.status >= 400 && response.status < 500) {
            return {
              success: false,
              error: data.error || data.message || `Request failed with status ${response.status}`,
            };
          }

          // For server errors, retry if we have attempts left
          if (attempt < maxAttempts - 1) {
            await delay(RETRY_DELAY * (attempt + 1)); // Exponential backoff
            continue;
          }

          return {
            success: false,
            error: data.error || data.message || `Server error: ${response.status}`,
          };
        }

        // Successful response
        return typeof data === 'object' && data !== null
          ? data
          : { success: true, data: data as T };

      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error');

        // Handle abort/timeout
        if (error instanceof Error && error.name === 'AbortError') {
          return {
            success: false,
            error: 'Request timeout - please try again',
          };
        }

        // Retry on network errors if we have attempts left
        if (attempt < maxAttempts - 1) {
          await delay(RETRY_DELAY * (attempt + 1));
          continue;
        }
      }
    }

    // All retries failed
    return {
      success: false,
      error: lastError?.message || 'Network error - please check your connection',
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Authentication API
  // ═══════════════════════════════════════════════════════════════════════════

  async login(email: string, password: string) {
    // Sanitize email input to prevent XSS
    const sanitizedEmail = sanitizeInput(email);

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(sanitizedEmail)) {
      return {
        success: false,
        error: 'Invalid email format',
      };
    }

    // Use relative URL to hit Next.js API routes (for E2E testing and when no backend is available)
    // In production with a backend, set NEXT_PUBLIC_API_URL to the backend URL
    const authBaseUrl = typeof window !== 'undefined' ? '' : this.baseUrl;

    try {
      const response = await fetch(`${authBaseUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: sanitizedEmail, password }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Login failed',
      };
    }
  }

  async getCurrentUser() {
    // Use relative URL for auth endpoints
    const authBaseUrl = typeof window !== 'undefined' ? '' : this.baseUrl;

    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (this.token) {
        headers['Authorization'] = `Bearer ${this.token}`;
      }

      const response = await fetch(`${authBaseUrl}/api/v1/auth/me`, {
        method: 'GET',
        headers,
      });

      const data = await response.json();
      return data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get user',
      };
    }
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
    const headers: HeadersInit = {};
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
  // Weather API
  // ═══════════════════════════════════════════════════════════════════════════

  async getWeather(lat: number, lng: number) {
    return this.request<WeatherData>('/api/v1/weather/current', {
      params: {
        lat: String(lat),
        lng: String(lng),
      },
    });
  }

  async getWeatherForecast(lat: number, lng: number, days: number = 7) {
    return this.request<WeatherForecast>('/api/v1/weather/forecast', {
      params: {
        lat: String(lat),
        lng: String(lng),
        days: String(days),
      },
    });
  }

  async getAgriculturalRisks(lat: number, lng: number) {
    return this.request<AgriculturalRisk[]>('/api/v1/weather/risks', {
      params: {
        lat: String(lat),
        lng: String(lng),
      },
    });
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
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout for image upload

      const response = await fetch(`${this.baseUrl}/api/v1/crop-health/analyze`, {
        method: 'POST',
        headers: this.token ? { Authorization: `Bearer ${this.token}` } : {},
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      let data: any;
      try {
        data = await response.json();
      } catch (parseError) {
        return {
          success: false,
          error: 'Invalid response from server',
        };
      }

      if (!response.ok) {
        return {
          success: false,
          error: data.error || data.message || 'Failed to analyze image',
        };
      }

      return data;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return {
          success: false,
          error: 'Upload timeout - please try again with a smaller image',
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

  async getIrrigationRecommendation(fieldId: string) {
    return this.request<IrrigationRecommendation>(`/api/v1/irrigation/fields/${fieldId}/recommendation`);
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

  async batchSync(data: {
    deviceId: string;
    userId: string;
    tenantId: string;
    fields: any[];
  }) {
    return this.request<any>('/api/v1/fields/sync/batch', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Agro Advisor API (خدمة مسترجعة من kernel)
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
    return this.request<any>('/api/v1/agro-advisor/advice', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDiseaseDetection(cropType: string, symptoms: string[]) {
    return this.request<any>('/api/v1/agro-advisor/disease', {
      method: 'POST',
      body: JSON.stringify({ cropType, symptoms }),
    });
  }

  async getNutrientRecommendation(data: {
    cropType: string;
    growthStage: string;
    soilAnalysis: any;
  }) {
    return this.request<any>('/api/v1/agro-advisor/nutrients', {
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
  // Field Chat API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldMessages(fieldId: string, options?: { limit?: number; offset?: number }) {
    return this.request<any[]>(`/api/v1/field-chat/fields/${fieldId}/messages`, {
      params: {
        limit: String(options?.limit || 50),
        offset: String(options?.offset || 0),
      },
    });
  }

  async sendFieldMessage(fieldId: string, message: string) {
    // Sanitize message to prevent XSS
    const sanitizedMessage = sanitizeInput(message);

    // Validate message length
    if (sanitizedMessage.length === 0) {
      return {
        success: false,
        error: 'Message cannot be empty',
      };
    }

    if (sanitizedMessage.length > 2000) {
      return {
        success: false,
        error: 'Message exceeds maximum length of 2000 characters',
      };
    }

    return this.request<any>(`/api/v1/field-chat/fields/${fieldId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message: sanitizedMessage }),
    });
  }

  async getFieldChatParticipants(fieldId: string) {
    return this.request<any[]>(`/api/v1/field-chat/fields/${fieldId}/participants`);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Core API (خدمة مسترجعة من kernel - TypeScript/Prisma)
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldBoundary(fieldId: string) {
    return this.request<any>(`/api/v1/field-core/fields/${fieldId}/boundary`);
  }

  async updateFieldBoundary(fieldId: string, boundary: any, etag?: string) {
    const headers: HeadersInit = {};
    if (etag) headers['If-Match'] = etag;

    return this.request<any>(`/api/v1/field-core/fields/${fieldId}/boundary`, {
      method: 'PUT',
      body: JSON.stringify({ boundary }),
      headers,
    });
  }

  async getFieldBoundaryHistory(fieldId: string) {
    return this.request<any[]>(`/api/v1/field-core/fields/${fieldId}/boundary-history`);
  }

  async rollbackFieldBoundary(fieldId: string, historyId: string, reason?: string) {
    return this.request<any>(`/api/v1/field-core/fields/${fieldId}/boundary-history/rollback`, {
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

  async updateTask(taskId: string, data: { status?: string; title?: string; description?: string }) {
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

  async updateTaskStatus(taskId: string, status: 'pending' | 'in_progress' | 'completed' | 'cancelled') {
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
    const wsProtocol = this.baseUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = this.baseUrl.replace(/^https?:\/\//, '');
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
  // Crop Health API (خدمة مسترجعة من kernel - مع OpenAPI)
  // ═══════════════════════════════════════════════════════════════════════════

  async getCropHealthDecision(data: {
    cropType: string;
    ndviValue: number;
    weatherConditions: any;
    soilMoisture?: number;
  }) {
    return this.request<any>('/api/v1/crop-health/decision', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCropHealthHistory(fieldId: string, days: number = 30) {
    return this.request<any[]>(`/api/v1/crop-health/fields/${fieldId}/history`, {
      params: { days: String(days) },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Satellite Service API
  // ═══════════════════════════════════════════════════════════════════════════

  async getSatelliteImagery(fieldId: string, options?: { from?: string; to?: string }) {
    return this.request<any[]>(`/api/v1/satellite/fields/${fieldId}/imagery`, {
      params: options as Record<string, string>,
    });
  }

  async requestSatelliteAnalysis(fieldId: string, analysisType: 'ndvi' | 'moisture' | 'thermal') {
    return this.request<any>(`/api/v1/satellite/fields/${fieldId}/analyze`, {
      method: 'POST',
      body: JSON.stringify({ analysisType }),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Marketplace API
  // ═══════════════════════════════════════════════════════════════════════════

  async getMarketplaceListings(options?: { category?: string; region?: string }) {
    return this.request<MarketplaceListing[]>('/api/v1/marketplace/listings', {
      params: options as Record<string, string>,
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
}

// Singleton instance
export const apiClient = new SahoolApiClient();
export default apiClient;
