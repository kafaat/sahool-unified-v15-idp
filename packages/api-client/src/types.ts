// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL API Types - الأنواع الموحدة
// Unified type definitions for all API interactions
// ═══════════════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────────────
// Core Types
// ─────────────────────────────────────────────────────────────────────────────

export type Locale = 'ar' | 'en';
export type Priority = 'low' | 'medium' | 'high' | 'urgent';
export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type TaskStatus = 'open' | 'in_progress' | 'done' | 'canceled';
export type DiagnosisStatus = 'pending' | 'confirmed' | 'rejected' | 'treated';
export type FarmStatus = 'active' | 'inactive' | 'suspended';

// ─────────────────────────────────────────────────────────────────────────────
// Geometry Types
// ─────────────────────────────────────────────────────────────────────────────

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface GeoPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

// ─────────────────────────────────────────────────────────────────────────────
// Task Types
// ─────────────────────────────────────────────────────────────────────────────

export interface Task {
  id: string;
  tenant_id: string;
  field_id: string;
  farm_id?: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: Priority;
  type?: string;
  due_date?: string;
  assigned_to?: string;
  evidence_photos?: string[];
  evidence_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  tenant_id: string;
  field_id: string;
  farm_id?: string;
  title: string;
  description?: string;
  priority?: Priority;
  type?: string;
  due_date?: string;
  assigned_to?: string;
}

export interface TaskEvidence {
  evidence_notes?: string;
  evidence_photos?: string[];
}

// ─────────────────────────────────────────────────────────────────────────────
// Field Types
// ─────────────────────────────────────────────────────────────────────────────

export interface Field {
  id: string;
  name: string;
  name_ar?: string;
  farm_id: string;
  tenant_id?: string;
  area_hectares: number;
  crop_type: string;
  geometry?: GeoPolygon;
  coordinates?: Coordinates;
  status: string;
  health_score?: number;
  ndvi_current?: number;
  created_at?: string;
  updated_at?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Farm Types
// ─────────────────────────────────────────────────────────────────────────────

export interface Farm {
  id: string;
  name: string;
  nameAr?: string;
  ownerId: string;
  governorate: string;
  district?: string;
  area: number;
  coordinates: Coordinates;
  crops: string[];
  status: FarmStatus;
  healthScore: number;
  lastUpdated: string;
  createdAt: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Weather Types
// ─────────────────────────────────────────────────────────────────────────────

export interface WeatherData {
  location_id: string;
  temperature_c: number;
  humidity_percent: number;
  wind_speed_kmh: number;
  condition: string;
  condition_ar: string;
  timestamp?: string;
}

export interface WeatherForecast {
  location_id: string;
  daily_forecast: DailyForecast[];
}

export interface DailyForecast {
  date: string;
  temp_max_c: number;
  temp_min_c: number;
  condition: string;
  condition_ar: string;
  precipitation_mm?: number;
}

export interface WeatherAlert {
  id: string;
  type: string;
  severity: Severity;
  title: string;
  titleAr?: string;
  description: string;
  descriptionAr?: string;
  affectedAreas: string[];
  startTime: string;
  endTime?: string;
  isActive: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Diagnosis Types
// ─────────────────────────────────────────────────────────────────────────────

export interface DiagnosisRecord {
  id: string;
  farmId: string;
  farmName?: string;
  imageUrl: string;
  thumbnailUrl?: string;
  cropType: string;
  diseaseId: string;
  diseaseName: string;
  diseaseNameAr: string;
  confidence: number;
  severity: Severity;
  status: DiagnosisStatus;
  location: Coordinates;
  diagnosedAt: string;
  createdBy: string;
  expertReview?: ExpertReview;
}

export interface ExpertReview {
  expertId: string;
  expertName: string;
  notes: string;
  reviewedAt: string;
}

export interface DiagnosisStats {
  total: number;
  pending: number;
  confirmed: number;
  treated: number;
  criticalCount: number;
  highCount: number;
  byDisease: Record<string, number>;
  byGovernorate: Record<string, number>;
}

// ─────────────────────────────────────────────────────────────────────────────
// Dashboard & Indicators Types
// ─────────────────────────────────────────────────────────────────────────────

export interface DashboardStats {
  totalFarms: number;
  activeFarms: number;
  totalArea: number;
  totalDiagnoses: number;
  pendingReviews: number;
  criticalAlerts: number;
  avgHealthScore: number;
  weeklyDiagnoses: number;
}

export interface DashboardData {
  total_fields: number;
  total_area_hectares: number;
  average_health_score: number;
  active_alerts: number;
}

export interface FieldIndicators {
  field_id: string;
  indicators: Indicator[];
  overall_score: number;
}

export interface Indicator {
  id: string;
  name: string;
  name_ar: string;
  value: number;
  unit?: string;
  status: string;
  trend?: 'up' | 'down' | 'stable';
}

// ─────────────────────────────────────────────────────────────────────────────
// Sensor & IoT Types
// ─────────────────────────────────────────────────────────────────────────────

export interface SensorReading {
  id: string;
  sensorId: string;
  fieldId: string;
  type: string;
  value: number;
  unit: string;
  timestamp: string;
  batteryLevel?: number;
}

export interface Equipment {
  id: string;
  name: string;
  type: string;
  status: string;
  lastMaintenance: string;
  nextMaintenance: string;
  fuelLevel?: number;
  hoursUsed?: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Notification Types
// ─────────────────────────────────────────────────────────────────────────────

export interface Notification {
  id: string;
  type: string;
  title: string;
  titleAr?: string;
  message: string;
  messageAr?: string;
  priority: Priority;
  read: boolean;
  createdAt: string;
  data?: Record<string, unknown>;
}

// ─────────────────────────────────────────────────────────────────────────────
// Community Types
// ─────────────────────────────────────────────────────────────────────────────

export interface CommunityPost {
  id: string;
  title: string;
  content: string;
  authorId: string;
  authorName: string;
  category: string;
  likes: number;
  comments: number;
  createdAt: string;
  updatedAt?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// API Response Types
// ─────────────────────────────────────────────────────────────────────────────

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Configuration Types
// ─────────────────────────────────────────────────────────────────────────────

export interface ApiClientConfig {
  baseUrl: string;
  timeout?: number;
  locale?: Locale;
  onUnauthorized?: () => void;
  getToken?: () => string | null;
  setToken?: (token: string) => void;
  enableMockData?: boolean;
}

export interface ServicePorts {
  fieldCore: number;
  satellite: number;
  indicators: number;
  weather: number;
  fertilizer: number;
  irrigation: number;
  cropHealth: number;
  virtualSensors: number;
  communityChat: number;
  yieldEngine: number;
  equipment: number;
  community: number;
  task: number;
  providerConfig: number;
  notifications: number;
  wsGateway: number;
  marketplace: number;
  auth: number;
}
