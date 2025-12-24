/**
 * SAHOOL API Client
 * Unified API client for connecting frontend to backend services
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
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
    const { params, ...fetchOptions } = options;

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

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || data.message || 'An error occurred',
        };
      }

      return data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Generic HTTP Methods
  // ═══════════════════════════════════════════════════════════════════════════

  async get<T>(url: string, options?: { params?: Record<string, string> }): Promise<{ data: T }> {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'An error occurred' }));
      throw new Error(error.message || 'An error occurred');
    }

    const data = await response.json();
    return { data };
  }

  async post<T>(url: string, data?: any): Promise<{ data: T }> {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'An error occurred' }));
      throw new Error(error.message || 'An error occurred');
    }

    const responseData = await response.json();
    return { data: responseData };
  }

  async patch<T>(url: string, data?: any): Promise<{ data: T }> {
    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'An error occurred' }));
      throw new Error(error.message || 'An error occurred');
    }

    const responseData = await response.json();
    return { data: responseData };
  }

  async put<T>(url: string, data?: any): Promise<{ data: T }> {
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'An error occurred' }));
      throw new Error(error.message || 'An error occurred');
    }

    const responseData = await response.json();
    return { data: responseData };
  }

  async delete<T>(url: string): Promise<{ data: T }> {
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'An error occurred' }));
      throw new Error(error.message || 'An error occurred');
    }

    // DELETE might return empty response
    const text = await response.text();
    const responseData = text ? JSON.parse(text) : null;
    return { data: responseData };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Operations API
  // ═══════════════════════════════════════════════════════════════════════════

  async getFields(tenantId: string, options?: { limit?: number; offset?: number }) {
    return this.request<any[]>('/api/v1/fields', {
      params: {
        tenantId,
        limit: String(options?.limit || 100),
        offset: String(options?.offset || 0),
      },
    });
  }

  async getField(fieldId: string) {
    return this.request<any>(`/api/v1/fields/${fieldId}`);
  }

  async createField(data: {
    name: string;
    tenantId: string;
    cropType: string;
    coordinates?: number[][];
  }) {
    return this.request<any>('/api/v1/fields', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateField(fieldId: string, data: any, etag?: string) {
    const headers: HeadersInit = {};
    if (etag) {
      headers['If-Match'] = etag;
    }
    return this.request<any>(`/api/v1/fields/${fieldId}`, {
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
    return this.request<any[]>('/api/v1/fields/nearby', {
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
    return this.request<any>(`/api/v1/fields/${fieldId}/ndvi`);
  }

  async getNdviSummary(tenantId: string) {
    return this.request<any>('/api/v1/ndvi/summary', {
      params: { tenantId },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather API
  // ═══════════════════════════════════════════════════════════════════════════

  async getWeather(lat: number, lng: number) {
    return this.request<any>('/api/v1/weather/current', {
      params: {
        lat: String(lat),
        lng: String(lng),
      },
    });
  }

  async getWeatherForecast(lat: number, lng: number, days: number = 7) {
    return this.request<any>('/api/v1/weather/forecast', {
      params: {
        lat: String(lat),
        lng: String(lng),
        days: String(days),
      },
    });
  }

  async getAgriculturalRisks(lat: number, lng: number) {
    return this.request<any>('/api/v1/weather/risks', {
      params: {
        lat: String(lat),
        lng: String(lng),
      },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Crop Health AI API
  // ═══════════════════════════════════════════════════════════════════════════

  async analyzeCropHealth(imageFile: File) {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch(`${this.baseUrl}/api/v1/crop-health/analyze`, {
      method: 'POST',
      headers: this.token ? { Authorization: `Bearer ${this.token}` } : {},
      body: formData,
    });

    return response.json();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // IoT Sensors API
  // ═══════════════════════════════════════════════════════════════════════════

  async getSensorData(fieldId: string) {
    return this.request<any>(`/api/v1/iot/fields/${fieldId}/sensors`);
  }

  async getSensorHistory(sensorId: string, from: Date, to: Date) {
    return this.request<any[]>(`/api/v1/iot/sensors/${sensorId}/history`, {
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
    return this.request<any>(`/api/v1/irrigation/fields/${fieldId}/recommendation`);
  }

  async calculateET0(data: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    solarRadiation: number;
  }) {
    return this.request<any>('/api/v1/irrigation/et0', {
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
    return this.request<any>('/api/v1/fertilizer/recommend', {
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
    return this.request<any>(`/api/v1/field-chat/fields/${fieldId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message }),
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
    return this.request<any[]>('/api/v1/equipment', {
      params: { tenantId },
    });
  }

  async getEquipmentById(equipmentId: string) {
    return this.request<any>(`/api/v1/equipment/${equipmentId}`);
  }

  async createEquipment(data: {
    name: string;
    type: string;
    tenantId: string;
    specifications?: any;
  }) {
    return this.request<any>('/api/v1/equipment', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateEquipmentStatus(equipmentId: string, status: string) {
    return this.request<any>(`/api/v1/equipment/${equipmentId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async getEquipmentMaintenanceSchedule(equipmentId: string) {
    return this.request<any[]>(`/api/v1/equipment/${equipmentId}/maintenance`);
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

    return this.request<any[]>('/api/v1/tasks', { params });
  }

  async getTask(taskId: string) {
    return this.request<any>(`/api/v1/tasks/${taskId}`);
  }

  async updateTask(taskId: string, data: { status?: string; title?: string; description?: string }) {
    return this.request<any>(`/api/v1/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async createTask(data: {
    title: string;
    description?: string;
    fieldId: string;
    assigneeId?: string;
    dueDate?: string;
    priority?: 'low' | 'medium' | 'high';
    taskType: string;
  }) {
    return this.request<any>('/api/v1/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTaskStatus(taskId: string, status: 'pending' | 'in_progress' | 'completed' | 'cancelled') {
    return this.request<any>(`/api/v1/tasks/${taskId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async completeTask(taskId: string, notes?: string) {
    return this.request<any>(`/api/v1/tasks/${taskId}/complete`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
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
    return this.request<any[]>('/api/v1/marketplace/listings', {
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
    return this.request<any>('/api/v1/marketplace/listings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Billing Core API
  // ═══════════════════════════════════════════════════════════════════════════

  async getSubscription(tenantId: string) {
    return this.request<any>(`/api/v1/billing/tenants/${tenantId}/subscription`);
  }

  async getInvoices(tenantId: string) {
    return this.request<any[]>(`/api/v1/billing/tenants/${tenantId}/invoices`);
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
