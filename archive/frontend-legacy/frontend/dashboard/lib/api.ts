/**
 * SAHOOL API Client
 * خدمة الاتصال بـ API
 */

const API_URL = process.env.API_URL || 'http://localhost:8080'

interface ApiResponse<T> {
  data: T
  error?: string
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  setToken(token: string) {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    return response.json()
  }

  // Tasks API
  async getTasks(params?: { field_id?: string; status?: string }) {
    const query = new URLSearchParams(params as Record<string, string>).toString()
    return this.request<Task[]>(`/api/v1/tasks${query ? `?${query}` : ''}`)
  }

  async getTask(taskId: string) {
    return this.request<Task>(`/api/v1/tasks/${taskId}`)
  }

  async createTask(task: CreateTaskRequest) {
    return this.request<Task>('/api/v1/tasks', {
      method: 'POST',
      body: JSON.stringify(task),
    })
  }

  async completeTask(taskId: string, evidence?: TaskEvidence) {
    return this.request<Task>(`/api/v1/tasks/${taskId}/complete`, {
      method: 'POST',
      body: JSON.stringify(evidence || {}),
    })
  }

  // Fields API
  async getFields(params?: { farm_id?: string }) {
    const query = new URLSearchParams(params as Record<string, string>).toString()
    return this.request<Field[]>(`/api/v1/fields${query ? `?${query}` : ''}`)
  }

  async getField(fieldId: string) {
    return this.request<Field>(`/api/v1/fields/${fieldId}`)
  }

  // Weather API
  async getWeather(locationId: string) {
    return this.request<WeatherData>(`/api/v1/weather/current/${locationId}`)
  }

  async getWeatherForecast(locationId: string, days = 7) {
    return this.request<WeatherForecast>(`/api/v1/weather/forecast/${locationId}?days=${days}`)
  }

  // Indicators API
  async getFieldIndicators(fieldId: string) {
    return this.request<FieldIndicators>(`/api/v1/indicators/field/${fieldId}`)
  }

  async getDashboard(tenantId: string) {
    return this.request<DashboardData>(`/api/v1/indicators/dashboard/${tenantId}`)
  }

  // Health check
  async health() {
    return this.request<{ status: string }>('/healthz')
  }
}

// Types
export interface Task {
  id: string
  tenant_id: string
  field_id: string
  farm_id?: string
  title: string
  description?: string
  status: 'open' | 'in_progress' | 'done' | 'canceled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  due_date?: string
  assigned_to?: string
  evidence_photos?: string[]
  evidence_notes?: string
  created_at: string
  updated_at: string
}

export interface CreateTaskRequest {
  tenant_id: string
  field_id: string
  farm_id?: string
  title: string
  description?: string
  priority?: string
  due_date?: string
  assigned_to?: string
}

export interface TaskEvidence {
  evidence_notes?: string
  evidence_photos?: string[]
}

export interface Field {
  id: string
  name: string
  farm_id: string
  area_hectares: number
  crop_type: string
  geometry: GeoJSON.Polygon
  status: string
  ndvi_current?: number
}

export interface WeatherData {
  location_id: string
  temperature_c: number
  humidity_percent: number
  wind_speed_kmh: number
  condition: string
  condition_ar: string
}

export interface WeatherForecast {
  location_id: string
  daily_forecast: Array<{
    date: string
    temp_max_c: number
    temp_min_c: number
    condition: string
    condition_ar: string
  }>
}

export interface FieldIndicators {
  field_id: string
  indicators: Array<{
    id: string
    name_ar: string
    value: number
    status: string
  }>
  overall_score: number
}

export interface DashboardData {
  total_fields: number
  total_area_hectares: number
  average_health_score: number
  active_alerts: number
}

// Export singleton instance
export const api = new ApiClient(API_URL)
