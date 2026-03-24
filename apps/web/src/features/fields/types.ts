/**
 * SAHOOL Fields Feature Types
 * أنواع ميزة الحقول
 */

// ═══════════════════════════════════════════════════════════════════════════
// GeoJSON Types
// ═══════════════════════════════════════════════════════════════════════════

export interface GeoPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface GeoPoint {
  type: 'Point';
  coordinates: [number, number]; // [lng, lat]
}

// ═══════════════════════════════════════════════════════════════════════════
// Field Core Types
// ═══════════════════════════════════════════════════════════════════════════

export type FieldStatus = 'active' | 'inactive' | 'deleted';
export type IrrigationType = 'drip' | 'sprinkler' | 'flood' | 'manual' | 'other';
export type SoilType = 'clay' | 'sandy' | 'loam' | 'silt' | 'peat' | 'chalk' | 'other';

export interface Field {
  id: string;
  name: string;
  nameAr: string;
  area: number; // in hectares
  crop?: string;
  cropAr?: string;
  farmId?: string;
  polygon?: GeoPolygon;
  centroid?: GeoPoint;
  description?: string;
  descriptionAr?: string;
  status?: FieldStatus;
  soilType?: string;
  irrigationType?: string;
  plantingDate?: string;
  expectedHarvest?: string;
  ndviValue?: number;
  healthScore?: number;
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Field Analytics & Monitoring Types
// ═══════════════════════════════════════════════════════════════════════════

// Field Zone
export interface FieldZone {
  id: string;
  fieldId: string;
  name: string;
  nameAr?: string;
  boundary: [number, number][];
  area: number; // hectares
  ndviValue: number;
  ndviTrend: 'improving' | 'stable' | 'declining';
  healthStatus: 'excellent' | 'good' | 'moderate' | 'poor' | 'critical';
  lastUpdated: Date;
}

// Field Alert
export interface FieldAlert {
  id: string;
  fieldId: string;
  zoneId?: string;
  type: 'ndvi_drop' | 'weather_warning' | 'soil_moisture' | 'task_overdue' | 'astral_favorable';
  severity: 'critical' | 'warning' | 'info';
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  data: Record<string, any>;
  createdAt: Date;
  expiresAt?: Date;
  acknowledged: boolean;
  actionTaken?: string;
}

// Living Field Score
export interface LivingFieldScore {
  overall: number;
  health: number;
  hydration: number;
  attention: number;
  astral: number;
  trend: 'improving' | 'stable' | 'declining';
  alerts: FieldAlert[];
  recommendations: FieldRecommendation[];
  lastUpdated: Date;
}

// Field Recommendation
export interface FieldRecommendation {
  id: string;
  type: 'task' | 'alert' | 'info';
  priority: 'high' | 'medium' | 'low';
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  action?: {
    type: 'create_task' | 'view_details' | 'external_link';
    data: Record<string, any>;
  };
  source: 'ndvi' | 'weather' | 'irrigation' | 'astronomical' | 'ai';
}

// ═══════════════════════════════════════════════════════════════════════════
// Form & Input Types
// ═══════════════════════════════════════════════════════════════════════════

export interface FieldFormData {
  name: string;
  nameAr: string;
  area: number;
  crop?: string;
  cropAr?: string;
  polygon?: GeoPolygon;
  farmId?: string;
  description?: string;
  descriptionAr?: string;
  status?: 'active' | 'inactive';
  soilType?: string;
  irrigationType?: string;
  plantingDate?: string;
  expectedHarvest?: string;
  metadata?: Record<string, unknown>;
}

export interface FieldFilters {
  search?: string;
  farmId?: string;
  crop?: string;
  minArea?: number;
  maxArea?: number;
  status?: string;
  soilType?: string;
  irrigationType?: string;
  healthScore?: {
    min?: number;
    max?: number;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Statistics Types
// ═══════════════════════════════════════════════════════════════════════════

export interface FieldStats {
  total: number;
  totalArea: number;
  byCrop: Record<string, number>;
  byStatus?: Record<FieldStatus, number>;
  averageArea?: number;
  healthyFields?: number;
  averageHealthScore?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// View & UI Types
// ═══════════════════════════════════════════════════════════════════════════

export type FieldViewMode = 'grid' | 'list' | 'map';

export interface FieldViewSettings {
  mode: FieldViewMode;
  sortBy?: 'name' | 'area' | 'crop' | 'createdAt' | 'healthScore';
  sortOrder?: 'asc' | 'desc';
  showInactive?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Types
// ═══════════════════════════════════════════════════════════════════════════

export interface FieldError {
  message: string;
  messageAr: string;
  code?: string;
  field?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Response Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ApiFieldResponse {
  success: boolean;
  data?: Field;
  error?: FieldError;
}

export interface ApiFieldsListResponse {
  success: boolean;
  data?: Field[];
  total?: number;
  error?: FieldError;
}

export interface ApiFieldStatsResponse {
  success: boolean;
  data?: FieldStats;
  error?: FieldError;
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Payload Types
// ═══════════════════════════════════════════════════════════════════════════

export interface CreateFieldPayload {
  data: FieldFormData;
  tenantId?: string;
}

export interface UpdateFieldPayload {
  id: string;
  data: Partial<FieldFormData>;
  tenantId?: string;
}

export interface DeleteFieldPayload {
  id: string;
  reason?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Hook Return Types
// ═══════════════════════════════════════════════════════════════════════════

export interface UseFieldsReturn {
  data: Field[] | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}

export interface UseFieldReturn {
  data: Field | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}

export interface UseFieldStatsReturn {
  data: FieldStats | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}
