// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL API Types - الأنواع الموحدة
// Unified type definitions for all API interactions
// ═══════════════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────────────
// Core Types
// ─────────────────────────────────────────────────────────────────────────────

export type Locale = 'ar' | 'en';
export type Priority = 'urgent' | 'high' | 'medium' | 'low';
export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type TaskStatus = 'open' | 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type DiagnosisStatus = 'pending' | 'confirmed' | 'rejected' | 'treated';
export type FarmStatus = 'active' | 'inactive' | 'suspended';

// ─────────────────────────────────────────────────────────────────────────────
// Geometry Types (GeoJSON-compatible)
// ─────────────────────────────────────────────────────────────────────────────

export interface Coordinates {
  lat: number;
  lng: number;
}

/** GeoJSON Position [longitude, latitude, altitude?] */
export type GeoPosition = [number, number] | [number, number, number];

/** GeoJSON Point */
export interface GeoPoint {
  type: 'Point';
  coordinates: GeoPosition;
}

/** GeoJSON Polygon */
export interface GeoPolygon {
  type: 'Polygon';
  coordinates: GeoPosition[][] | number[][][];
}

/** GeoJSON MultiPolygon */
export interface GeoMultiPolygon {
  type: 'MultiPolygon';
  coordinates: GeoPosition[][][];
}

/** GeoJSON LineString */
export interface GeoLineString {
  type: 'LineString';
  coordinates: GeoPosition[];
}

/** Union of all GeoJSON geometry types used in SAHOOL */
export type GeoGeometry = GeoPoint | GeoPolygon | GeoMultiPolygon | GeoLineString;

/** GeoJSON Feature */
export interface GeoFeature<G extends GeoGeometry = GeoGeometry, P = Record<string, unknown>> {
  type: 'Feature';
  geometry: G;
  properties: P;
  id?: string | number;
}

/** GeoJSON FeatureCollection */
export interface GeoFeatureCollection<G extends GeoGeometry = GeoGeometry, P = Record<string, unknown>> {
  type: 'FeatureCollection';
  features: GeoFeature<G, P>[];
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
  title_ar?: string;
  description?: string;
  description_ar?: string;
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
  title_ar?: string;
  description?: string;
  description_ar?: string;
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
  area: number; // area in hectares
  area_hectares?: number; // alias for backward compatibility
  crop?: string;
  crop_ar?: string;
  crop_type?: string; // alias for backward compatibility
  description?: string;
  description_ar?: string;
  polygon?: GeoPolygon;
  geometry?: GeoPolygon;
  coordinates?: Coordinates;
  status: string;
  soil_type?: string;
  irrigation_type?: string;
  health_score?: number;
  ndvi_current?: number;
  ndvi_value?: number; // alias for backward compatibility
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
  // Aliases for component compatibility
  temperature?: number;
  humidity?: number;
  windSpeed?: number;
  conditionAr?: string;
  location?: string;
  windDirection?: string;
  pressure?: number;
  visibility?: number;
  uvIndex?: number;
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
  start_date?: string;
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
// Alert Types
// ─────────────────────────────────────────────────────────────────────────────

export type AlertSeverity = 'info' | 'warning' | 'critical' | 'emergency';
export type AlertCategory = 'ndvi' | 'weather' | 'irrigation' | 'pest' | 'disease' | 'system';
export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'dismissed';

export interface Alert {
  id: string;
  title: string;
  titleAr?: string;
  message: string;
  messageAr?: string;
  severity: AlertSeverity;
  category: AlertCategory;
  status: AlertStatus;
  fieldId?: string;
  fieldName?: string;
  farmId?: string;
  farmName?: string;
  createdAt: string;
  updatedAt?: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
  read: boolean;
  actionUrl?: string;
  metadata?: Record<string, unknown>;
}

export interface AlertFilters {
  severity?: AlertSeverity[];
  category?: AlertCategory[];
  status?: AlertStatus[];
  fieldId?: string;
  farmId?: string;
  startDate?: string;
  endDate?: string;
}

export interface AlertStats {
  total: number;
  active: number;
  resolved: number;
  bySeverity: Record<AlertSeverity, number>;
  byCategory: Record<AlertCategory, number>;
}

// ─────────────────────────────────────────────────────────────────────────────
// User & Auth Types
// ─────────────────────────────────────────────────────────────────────────────

export type UserRole = 'admin' | 'expert' | 'farmer' | 'agronomist' | 'manager' | 'operator' | 'viewer';

export interface User {
  id: string;
  email: string;
  name: string;
  nameAr?: string;
  role: UserRole;
  tenantId: string;
  tenantName?: string;
  governorate?: string;
  phone?: string;
  avatar?: string;
  isActive: boolean;
  lastLogin?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  token?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
  refreshToken?: string;
  expiresAt: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// KPI Types
// ─────────────────────────────────────────────────────────────────────────────

export type TrendDirection = 'up' | 'down' | 'stable';
export type HealthStatus = 'good' | 'warning' | 'critical' | 'healthy' | 'moderate' | 'stressed';

export interface KPI {
  id: string;
  label: string;
  labelAr?: string;
  value: number;
  unit: string;
  trend: TrendDirection;
  trendValue: number;
  status: HealthStatus;
  icon?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Governorate Types (Yemen-specific)
// ─────────────────────────────────────────────────────────────────────────────

export interface Governorate {
  id: string;
  name: string;
  nameAr: string;
  farmCount: number;
  totalArea: number;
  avgHealthScore: number;
  coordinates: Coordinates;
}

// ─────────────────────────────────────────────────────────────────────────────
// Treatment Types
// ─────────────────────────────────────────────────────────────────────────────

export interface Treatment {
  id: string;
  diagnosisId: string;
  recommendation: string;
  recommendationAr?: string;
  appliedAt?: string;
  status: 'pending' | 'applied' | 'effective' | 'ineffective';
  notes?: string;
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
