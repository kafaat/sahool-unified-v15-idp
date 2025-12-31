// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Unified API Client
// عميل API الموحد لمنصة سهول
// ═══════════════════════════════════════════════════════════════════════════════

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import type {
  ApiClientConfig,
  ServicePorts,
  Task,
  CreateTaskRequest,
  TaskEvidence,
  Field,
  Farm,
  WeatherData,
  WeatherForecast,
  WeatherAlert,
  DiagnosisRecord,
  DiagnosisStats,
  DashboardStats,
  DashboardData,
  FieldIndicators,
  SensorReading,
  Equipment,
  Notification,
  CommunityPost,
  Severity,
  DiagnosisStatus,
} from './types';

// Re-export all types
export * from './types';

// ─────────────────────────────────────────────────────────────────────────────
// Default Configuration
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_PORTS: ServicePorts = {
  fieldCore: 3000,
  satellite: 8090,
  indicators: 8091,
  weather: 8092,
  fertilizer: 8093,
  irrigation: 8094,
  cropHealth: 8095,
  virtualSensors: 8096,
  communityChat: 8097,
  yieldEngine: 8098,
  equipment: 8101,
  community: 8102,
  task: 8103,
  providerConfig: 8104,
  notifications: 8110,
  wsGateway: 8090,
  marketplace: 3010,
  auth: 8001,
};

// ─────────────────────────────────────────────────────────────────────────────
// SAHOOL API Client Class
// ─────────────────────────────────────────────────────────────────────────────

export class SahoolApiClient {
  private client: AxiosInstance;
  private config: ApiClientConfig;
  private ports: ServicePorts;
  private isProduction: boolean;

  constructor(config: ApiClientConfig, ports: Partial<ServicePorts> = {}) {
    this.config = {
      timeout: 30000,
      locale: 'ar',
      enableMockData: false,
      ...config,
    };
    this.ports = { ...DEFAULT_PORTS, ...ports };
    this.isProduction = process.env.NODE_ENV === 'production';

    // Create axios instance
    this.client = axios.create({
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Language': `${this.config.locale},en`,
      },
    });

    // Setup interceptors
    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor - add auth token
    this.client.interceptors.request.use((config) => {
      const token = this.config.getToken?.();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.config.onUnauthorized?.();
        }
        return Promise.reject(error);
      }
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // URL Helpers
  // ─────────────────────────────────────────────────────────────────────────

  private getServiceUrl(port: number): string {
    return this.isProduction
      ? `${this.config.baseUrl}/api`
      : `${this.config.baseUrl}:${port}`;
  }

  get urls() {
    return {
      fieldCore: this.getServiceUrl(this.ports.fieldCore),
      satellite: this.getServiceUrl(this.ports.satellite),
      indicators: this.getServiceUrl(this.ports.indicators),
      weather: this.getServiceUrl(this.ports.weather),
      fertilizer: this.getServiceUrl(this.ports.fertilizer),
      irrigation: this.getServiceUrl(this.ports.irrigation),
      cropHealth: this.getServiceUrl(this.ports.cropHealth),
      virtualSensors: this.getServiceUrl(this.ports.virtualSensors),
      communityChat: this.getServiceUrl(this.ports.communityChat),
      yieldEngine: this.getServiceUrl(this.ports.yieldEngine),
      equipment: this.getServiceUrl(this.ports.equipment),
      community: this.getServiceUrl(this.ports.community),
      task: this.getServiceUrl(this.ports.task),
      providerConfig: this.getServiceUrl(this.ports.providerConfig),
      notifications: this.getServiceUrl(this.ports.notifications),
      wsGateway: this.getServiceUrl(this.ports.wsGateway),
      marketplace: this.getServiceUrl(this.ports.marketplace),
      auth: this.getServiceUrl(this.ports.auth),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Generic Request Method
  // ─────────────────────────────────────────────────────────────────────────

  private async request<T>(
    url: string,
    options: AxiosRequestConfig = {}
  ): Promise<T> {
    const response = await this.client.request<T>({ url, ...options });
    return response.data;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Auth Token Management
  // ─────────────────────────────────────────────────────────────────────────

  setToken(token: string): void {
    this.config.setToken?.(token);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Tasks API
  // ─────────────────────────────────────────────────────────────────────────

  async getTasks(params?: {
    field_id?: string;
    status?: string;
    type?: string;
    assigned_to?: string;
    limit?: number;
  }): Promise<Task[]> {
    try {
      return await this.request<Task[]>(`${this.urls.task}/api/v1/tasks`, {
        params,
      });
    } catch {
      return [];
    }
  }

  async getTask(taskId: string): Promise<Task> {
    return this.request<Task>(`${this.urls.task}/api/v1/tasks/${taskId}`);
  }

  async createTask(task: CreateTaskRequest): Promise<Task> {
    return this.request<Task>(`${this.urls.task}/api/v1/tasks`, {
      method: 'POST',
      data: task,
    });
  }

  async updateTask(taskId: string, data: Partial<CreateTaskRequest>): Promise<Task> {
    return this.request<Task>(`${this.urls.task}/api/v1/tasks/${taskId}`, {
      method: 'PUT',
      data,
    });
  }

  async updateTaskStatus(taskId: string, status: string): Promise<boolean> {
    try {
      await this.request(`${this.urls.task}/api/v1/tasks/${taskId}`, {
        method: 'PATCH',
        data: { status },
      });
      return true;
    } catch {
      return false;
    }
  }

  async deleteTask(taskId: string): Promise<void> {
    await this.request<void>(`${this.urls.task}/api/v1/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async completeTask(taskId: string, evidence?: TaskEvidence): Promise<Task> {
    return this.request<Task>(`${this.urls.task}/api/v1/tasks/${taskId}/complete`, {
      method: 'POST',
      data: evidence || {},
    });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Fields API
  // ─────────────────────────────────────────────────────────────────────────

  async getFields(params?: { farm_id?: string }): Promise<Field[]> {
    try {
      return await this.request<Field[]>(`${this.urls.fieldCore}/api/v1/fields`, {
        params,
      });
    } catch {
      return [];
    }
  }

  async getField(fieldId: string): Promise<Field> {
    return this.request<Field>(`${this.urls.fieldCore}/api/v1/fields/${fieldId}`);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Farms API
  // ─────────────────────────────────────────────────────────────────────────

  async getFarms(): Promise<Farm[]> {
    try {
      const response = await this.request<Field[]>(`${this.urls.fieldCore}/api/v1/fields`);
      // Map fields to farms format
      return response.map((f) => ({
        id: f.id,
        name: f.name,
        nameAr: f.name_ar,
        ownerId: f.tenant_id || '',
        governorate: '',
        area: f.area_hectares || f.area || 0,
        coordinates: f.coordinates || { lat: 0, lng: 0 },
        crops: [f.crop_type || f.crop || ''],
        status: f.status as 'active' | 'inactive' | 'suspended',
        healthScore: f.health_score || 0,
        lastUpdated: f.updated_at || new Date().toISOString(),
        createdAt: f.created_at || new Date().toISOString(),
      }));
    } catch {
      if (this.config.enableMockData) {
        return this.generateMockFarms();
      }
      return [];
    }
  }

  async getFarmById(id: string): Promise<Farm | null> {
    try {
      const field = await this.getField(id);
      return {
        id: field.id,
        name: field.name,
        nameAr: field.name_ar,
        ownerId: field.tenant_id || '',
        governorate: '',
        area: field.area_hectares || field.area || 0,
        coordinates: field.coordinates || { lat: 0, lng: 0 },
        crops: [field.crop_type || field.crop || ''],
        status: field.status as 'active' | 'inactive' | 'suspended',
        healthScore: field.health_score || 0,
        lastUpdated: field.updated_at || new Date().toISOString(),
        createdAt: field.created_at || new Date().toISOString(),
      };
    } catch {
      return null;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Weather API
  // ─────────────────────────────────────────────────────────────────────────

  async getWeather(locationId: string): Promise<WeatherData | null> {
    try {
      return await this.request<WeatherData>(
        `${this.urls.weather}/api/v1/weather/current/${locationId}`
      );
    } catch {
      return null;
    }
  }

  async getWeatherForecast(locationId: string, days = 7): Promise<WeatherForecast | null> {
    try {
      return await this.request<WeatherForecast>(
        `${this.urls.weather}/api/v1/weather/forecast/${locationId}`,
        { params: { days } }
      );
    } catch {
      return null;
    }
  }

  async getWeatherAlerts(): Promise<WeatherAlert[]> {
    try {
      return await this.request<WeatherAlert[]>(`${this.urls.weather}/v1/alerts`);
    } catch {
      return [];
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Diagnosis API
  // ─────────────────────────────────────────────────────────────────────────

  async getDiagnoses(params?: {
    status?: string;
    severity?: string;
    farmId?: string;
    governorate?: string;
    limit?: number;
    offset?: number;
  }): Promise<DiagnosisRecord[]> {
    try {
      const response = await this.request<Record<string, unknown>[]>(
        `${this.urls.cropHealth}/v1/diagnoses`,
        {
          params: {
            status: params?.status,
            severity: params?.severity,
            governorate: params?.governorate,
            limit: params?.limit || 50,
            offset: params?.offset || 0,
          },
        }
      );

      return response.map((d) => ({
        id: d.id as string,
        farmId: (d.field_id as string) || `farm-${Math.floor(Math.random() * 25) + 1}`,
        farmName: d.governorate ? `مزرعة في ${d.governorate}` : 'مزرعة',
        imageUrl: (d.image_url as string) || '/api/placeholder/400/300',
        thumbnailUrl: (d.thumbnail_url as string) || (d.image_url as string) || '/api/placeholder/100/100',
        cropType: (d.crop_type as string) || 'unknown',
        diseaseId: d.disease_id as string,
        diseaseName: d.disease_name as string,
        diseaseNameAr: d.disease_name_ar as string,
        confidence: (d.confidence as number) * 100,
        severity: d.severity as Severity,
        status: d.status as DiagnosisStatus,
        location: (d.location as { lat: number; lng: number }) || { lat: 15.3694, lng: 44.191 },
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
    } catch {
      if (this.config.enableMockData) {
        return this.generateMockDiagnoses();
      }
      return [];
    }
  }

  async getDiagnosisStats(): Promise<DiagnosisStats> {
    try {
      const response = await this.request<Record<string, unknown>>(
        `${this.urls.cropHealth}/v1/diagnoses/stats`
      );
      return {
        total: response.total as number,
        pending: response.pending as number,
        confirmed: response.confirmed as number,
        treated: response.treated as number,
        criticalCount: response.critical_count as number,
        highCount: response.high_count as number,
        byDisease: response.by_disease as Record<string, number>,
        byGovernorate: response.by_governorate as Record<string, number>,
      };
    } catch {
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

  async updateDiagnosisStatus(
    id: string,
    status: DiagnosisStatus,
    notes?: string
  ): Promise<{ success: boolean; diagnosis_id: string; status: string }> {
    try {
      return await this.request(`${this.urls.cropHealth}/v1/diagnoses/${id}`, {
        method: 'PATCH',
        params: { status, expert_notes: notes },
      });
    } catch {
      return { success: true, diagnosis_id: id, status };
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Dashboard & Indicators API
  // ─────────────────────────────────────────────────────────────────────────

  async getDashboardStats(): Promise<DashboardStats> {
    try {
      return await this.request<DashboardStats>(`${this.urls.indicators}/v1/dashboard`);
    } catch {
      if (this.config.enableMockData) {
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
      return {
        totalFarms: 0,
        activeFarms: 0,
        totalArea: 0,
        totalDiagnoses: 0,
        pendingReviews: 0,
        criticalAlerts: 0,
        avgHealthScore: 0,
        weeklyDiagnoses: 0,
      };
    }
  }

  async getDashboard(tenantId: string): Promise<DashboardData | null> {
    try {
      return await this.request<DashboardData>(
        `${this.urls.indicators}/api/v1/indicators/dashboard/${tenantId}`
      );
    } catch {
      return null;
    }
  }

  async getFieldIndicators(fieldId: string): Promise<FieldIndicators | null> {
    try {
      return await this.request<FieldIndicators>(
        `${this.urls.indicators}/api/v1/indicators/field/${fieldId}`
      );
    } catch {
      return null;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Sensors & Equipment API
  // ─────────────────────────────────────────────────────────────────────────

  async getSensorReadings(farmId: string): Promise<SensorReading[]> {
    try {
      return await this.request<SensorReading[]>(
        `${this.urls.virtualSensors}/v1/readings/${farmId}`
      );
    } catch {
      return [];
    }
  }

  async getEquipment(params?: { type?: string; status?: string }): Promise<Equipment[]> {
    try {
      return await this.request<Equipment[]>(`${this.urls.equipment}/api/v1/equipment`, {
        params,
      });
    } catch {
      return [];
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Notifications API
  // ─────────────────────────────────────────────────────────────────────────

  async getNotifications(params?: {
    type?: string;
    priority?: string;
    limit?: number;
  }): Promise<Notification[]> {
    try {
      return await this.request<Notification[]>(
        `${this.urls.notifications}/v1/notifications`,
        { params }
      );
    } catch {
      return [];
    }
  }

  async markNotificationRead(id: string): Promise<boolean> {
    try {
      await this.request(`${this.urls.notifications}/v1/notifications/${id}/read`, {
        method: 'PATCH',
      });
      return true;
    } catch {
      return false;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Community API
  // ─────────────────────────────────────────────────────────────────────────

  async getCommunityPosts(params?: {
    category?: string;
    limit?: number;
  }): Promise<CommunityPost[]> {
    try {
      return await this.request<CommunityPost[]>(
        `${this.urls.community}/api/v1/posts`,
        { params }
      );
    } catch {
      return [];
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────

  async health(): Promise<{ status: string }> {
    return this.request<{ status: string }>(`${this.urls.fieldCore}/healthz`);
  }

  async checkServicesHealth(): Promise<Record<string, boolean>> {
    const services = Object.entries(this.urls);
    const results: Record<string, boolean> = {};

    await Promise.all(
      services.map(async ([name, url]) => {
        try {
          await this.client.get(`${url}/healthz`, { timeout: 5000 });
          results[name] = true;
        } catch {
          results[name] = false;
        }
      })
    );

    return results;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Mock Data Generators
  // ─────────────────────────────────────────────────────────────────────────

  private generateMockFarms(): Farm[] {
    const governorates = ['sanaa', 'taiz', 'ibb', 'hadramaut', 'hodeidah', 'dhamar'] as const;
    const crops = ['wheat', 'coffee', 'qat', 'date_palm', 'mango', 'banana', 'sorghum'] as const;

    return Array.from({ length: 25 }, (_, i) => ({
      id: `farm-${i + 1}`,
      name: `Farm ${i + 1}`,
      nameAr: `مزرعة ${i + 1}`,
      ownerId: `user-${Math.floor(Math.random() * 10) + 1}`,
      governorate: governorates[Math.floor(Math.random() * governorates.length)] ?? 'sanaa',
      district: 'District',
      area: Math.random() * 50 + 5,
      coordinates: {
        lat: 13.5 + Math.random() * 3,
        lng: 43.5 + Math.random() * 5,
      },
      crops: [crops[Math.floor(Math.random() * crops.length)] ?? 'wheat'],
      status: 'active' as const,
      healthScore: Math.floor(Math.random() * 40) + 60,
      lastUpdated: new Date().toISOString(),
      createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
    }));
  }

  private generateMockDiagnoses(): DiagnosisRecord[] {
    const diseases = [
      { id: 'tomato_late_blight', name: 'Late Blight', nameAr: 'اللفحة المتأخرة' },
      { id: 'tomato_early_blight', name: 'Early Blight', nameAr: 'اللفحة المبكرة' },
      { id: 'powdery_mildew', name: 'Powdery Mildew', nameAr: 'البياض الدقيقي' },
      { id: 'bacterial_spot', name: 'Bacterial Spot', nameAr: 'التبقع البكتيري' },
    ] as const;
    const defaultDisease = diseases[0];
    const severities: Severity[] = ['low', 'medium', 'high', 'critical'];
    const statuses: DiagnosisStatus[] = ['pending', 'confirmed', 'rejected', 'treated'];

    return Array.from({ length: 20 }, (_, i) => {
      const disease = diseases[Math.floor(Math.random() * diseases.length)] ?? defaultDisease;
      return {
        id: `diag-${i + 1}`,
        farmId: `farm-${Math.floor(Math.random() * 25) + 1}`,
        farmName: `مزرعة ${Math.floor(Math.random() * 25) + 1}`,
        imageUrl: `/api/placeholder/400/300`,
        thumbnailUrl: `/api/placeholder/100/100`,
        cropType: 'tomato',
        diseaseId: disease.id,
        diseaseName: disease.name,
        diseaseNameAr: disease.nameAr,
        confidence: Math.random() * 30 + 70,
        severity: severities[Math.floor(Math.random() * severities.length)] ?? 'medium',
        status: statuses[Math.floor(Math.random() * statuses.length)] ?? 'pending',
        location: {
          lat: 13.5 + Math.random() * 3,
          lng: 43.5 + Math.random() * 5,
        },
        diagnosedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        createdBy: `user-${Math.floor(Math.random() * 10) + 1}`,
      };
    });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Factory Function
// ─────────────────────────────────────────────────────────────────────────────

export function createApiClient(config: ApiClientConfig): SahoolApiClient {
  return new SahoolApiClient(config);
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Export
// ─────────────────────────────────────────────────────────────────────────────

export default SahoolApiClient;
