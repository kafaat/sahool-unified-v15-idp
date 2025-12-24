/**
 * SAHOOL API Types
 * TypeScript interfaces for all API entities
 */

// ═══════════════════════════════════════════════════════════════════════════
// Common Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  error_ar?: string;
  message?: string;
  pagination?: Pagination;
}

export interface Pagination {
  total: number;
  limit: number;
  offset: number;
  hasMore?: boolean;
}

export interface GeoPoint {
  type: 'Point';
  coordinates: [number, number]; // [lng, lat]
}

export interface GeoPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

// ═══════════════════════════════════════════════════════════════════════════
// Field Types
// ═══════════════════════════════════════════════════════════════════════════

export interface Field {
  id: string;
  name: string;
  tenantId: string;
  ownerId?: string;
  cropType: string;
  status: 'active' | 'inactive' | 'deleted';
  boundary?: GeoPolygon;
  centroid?: GeoPoint;
  areaHectares?: number;
  irrigationType?: string;
  soilType?: string;
  plantingDate?: string;
  expectedHarvest?: string;
  ndviValue?: number;
  healthScore?: number;
  metadata?: Record<string, any>;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface FieldCreateRequest {
  name: string;
  tenantId: string;
  cropType: string;
  coordinates?: number[][];
  ownerId?: string;
  irrigationType?: string;
  soilType?: string;
  plantingDate?: string;
  expectedHarvest?: string;
  metadata?: Record<string, any>;
}

export interface FieldUpdateRequest {
  name?: string;
  cropType?: string;
  status?: 'active' | 'inactive';
  irrigationType?: string;
  soilType?: string;
  plantingDate?: string;
  expectedHarvest?: string;
  metadata?: Record<string, any>;
}

// ═══════════════════════════════════════════════════════════════════════════
// NDVI Types
// ═══════════════════════════════════════════════════════════════════════════

export interface NdviData {
  fieldId: string;
  fieldName: string;
  current: {
    value: number;
    category: NdviCategory;
    date: string;
  };
  statistics: {
    average: number;
    min: number;
    max: number;
    trend: number;
    trendDirection: 'improving' | 'declining' | 'stable';
  };
  history: NdviHistoryPoint[];
  lastUpdated: string;
}

export interface NdviHistoryPoint {
  date: string;
  value: number;
  cloudCover?: number;
}

export interface NdviCategory {
  name: string;
  nameAr: string;
  color: string;
}

export interface NdviSummary {
  tenantId: string;
  totalFields: number;
  averageNdvi: number;
  averageHealth: number;
  totalAreaHectares: number;
  distribution: {
    healthy: number;
    moderate: number;
    stressed: number;
    critical: number;
  };
  timestamp: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Weather Types
// ═══════════════════════════════════════════════════════════════════════════

export interface WeatherData {
  location: {
    lat: number;
    lng: number;
    name?: string;
  };
  current: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    windDirection: number;
    pressure: number;
    cloudCover: number;
    uvIndex: number;
    description: string;
    icon: string;
  };
  timestamp: string;
}

export interface WeatherForecast {
  location: {
    lat: number;
    lng: number;
  };
  daily: DailyForecast[];
  hourly?: HourlyForecast[];
}

export interface DailyForecast {
  date: string;
  tempMax: number;
  tempMin: number;
  humidity: number;
  precipitation: number;
  precipitationProbability: number;
  windSpeed: number;
  description: string;
  icon: string;
}

export interface HourlyForecast {
  time: string;
  temperature: number;
  humidity: number;
  precipitation: number;
  windSpeed: number;
  icon: string;
}

export interface AgriculturalRisk {
  type: 'frost' | 'heat' | 'drought' | 'flood' | 'pest' | 'disease';
  severity: 'low' | 'medium' | 'high' | 'critical';
  probability: number;
  description: string;
  descriptionAr: string;
  recommendations: string[];
  recommendationsAr: string[];
  validUntil: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// IoT / Sensor Types
// ═══════════════════════════════════════════════════════════════════════════

export interface Sensor {
  id: string;
  fieldId: string;
  name: string;
  type: 'soil_moisture' | 'temperature' | 'humidity' | 'ph' | 'ec' | 'rain' | 'wind';
  status: 'online' | 'offline' | 'warning';
  batteryLevel?: number;
  lastReading?: SensorReading;
  location?: GeoPoint;
  createdAt: string;
}

export interface SensorReading {
  sensorId: string;
  value: number;
  unit: string;
  timestamp: string;
  quality?: 'good' | 'fair' | 'poor';
}

// ═══════════════════════════════════════════════════════════════════════════
// Task Types
// ═══════════════════════════════════════════════════════════════════════════

export interface Task {
  id: string;
  title: string;
  description?: string;
  fieldId: string;
  fieldName?: string;
  assigneeId?: string;
  assigneeName?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high';
  taskType: string;
  dueDate?: string;
  completedAt?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  fieldId: string;
  assigneeId?: string;
  dueDate?: string;
  priority?: 'low' | 'medium' | 'high';
  taskType: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Equipment Types
// ═══════════════════════════════════════════════════════════════════════════

export interface Equipment {
  id: string;
  name: string;
  type: string;
  tenantId: string;
  status: 'available' | 'in_use' | 'maintenance' | 'retired';
  specifications?: Record<string, any>;
  lastMaintenanceDate?: string;
  nextMaintenanceDate?: string;
  location?: GeoPoint;
  createdAt: string;
}

export interface MaintenanceSchedule {
  id: string;
  equipmentId: string;
  type: string;
  scheduledDate: string;
  status: 'pending' | 'completed' | 'overdue';
  notes?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation Types
// ═══════════════════════════════════════════════════════════════════════════

export interface IrrigationRecommendation {
  fieldId: string;
  recommendedAmount: number; // mm
  recommendedDuration: number; // minutes
  urgency: 'none' | 'low' | 'medium' | 'high';
  reasoning: string;
  reasoningAr: string;
  et0: number; // Reference evapotranspiration
  soilMoistureDeficit: number;
  nextIrrigationDate?: string;
}

export interface ET0Calculation {
  value: number;
  unit: 'mm/day';
  inputs: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    solarRadiation: number;
  };
  method: 'FAO-56 Penman-Monteith';
}

// ═══════════════════════════════════════════════════════════════════════════
// Fertilizer Types
// ═══════════════════════════════════════════════════════════════════════════

export interface FertilizerRecommendation {
  cropType: string;
  growthStage: string;
  recommendations: FertilizerApplication[];
  totalCost?: number;
  currency?: string;
}

export interface FertilizerApplication {
  fertilizer: string;
  amount: number;
  unit: string;
  timing: string;
  method: string;
  notes?: string;
  notesAr?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Crop Health Types
// ═══════════════════════════════════════════════════════════════════════════

export interface CropHealthAnalysis {
  imageId: string;
  fieldId?: string;
  diagnosis: {
    condition: string;
    conditionAr: string;
    confidence: number;
    severity: 'healthy' | 'mild' | 'moderate' | 'severe';
  };
  diseases?: DiseaseDetection[];
  recommendations: string[];
  recommendationsAr: string[];
  timestamp: string;
}

export interface DiseaseDetection {
  name: string;
  nameAr: string;
  confidence: number;
  affectedArea: number; // percentage
  treatment: string;
  treatmentAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Marketplace Types
// ═══════════════════════════════════════════════════════════════════════════

export interface MarketplaceListing {
  id: string;
  title: string;
  description: string;
  category: string;
  price: number;
  currency: string;
  quantity: number;
  unit: string;
  sellerId: string;
  sellerName?: string;
  location?: string;
  images?: string[];
  status: 'active' | 'sold' | 'expired';
  createdAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Billing Types
// ═══════════════════════════════════════════════════════════════════════════

export interface Subscription {
  id: string;
  tenantId: string;
  plan: 'free' | 'basic' | 'professional' | 'enterprise';
  status: 'active' | 'cancelled' | 'expired' | 'past_due';
  currentPeriodStart: string;
  currentPeriodEnd: string;
  features: string[];
  limits: {
    fields: number;
    users: number;
    storage: number; // GB
    apiCalls: number;
  };
}

export interface Invoice {
  id: string;
  tenantId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'overdue' | 'cancelled';
  dueDate: string;
  paidAt?: string;
  items: InvoiceItem[];
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: number;
  total: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// User Types
// ═══════════════════════════════════════════════════════════════════════════

export interface User {
  id: string;
  email: string;
  name: string;
  tenantId: string;
  role: 'admin' | 'manager' | 'operator' | 'viewer';
  avatar?: string;
  phone?: string;
  language: 'ar' | 'en';
  createdAt: string;
}

export interface Tenant {
  id: string;
  name: string;
  logo?: string;
  subscription: Subscription;
  settings: TenantSettings;
  createdAt: string;
}

export interface TenantSettings {
  defaultLanguage: 'ar' | 'en';
  timezone: string;
  currency: string;
  units: 'metric' | 'imperial';
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Sync Types (for Mobile)
// ═══════════════════════════════════════════════════════════════════════════

export interface SyncStatus {
  deviceId: string;
  userId: string;
  tenantId: string;
  lastSyncAt?: string;
  status: 'idle' | 'syncing' | 'conflict' | 'error';
  pendingDownloads: number;
  conflictsCount: number;
}

export interface SyncResult {
  clientId: string;
  serverId?: string;
  status: 'created' | 'updated' | 'conflict' | 'error';
  server_version?: number;
  etag?: string;
  serverData?: any;
  error?: string;
}
