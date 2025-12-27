/**
 * SAHOOL Fields Feature Types
 * أنواع ميزة الحقول
 */

// GeoJSON types
export interface GeoPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface GeoPoint {
  type: 'Point';
  coordinates: [number, number]; // [lng, lat]
}

// Field type
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
  status?: 'active' | 'inactive' | 'deleted';
  soilType?: string;
  irrigationType?: string;
  plantingDate?: string;
  expectedHarvest?: string;
  ndviValue?: number;
  healthScore?: number;
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

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
  metadata?: Record<string, any>;
}

export interface FieldFilters {
  search?: string;
  farmId?: string;
  crop?: string;
  minArea?: number;
  maxArea?: number;
  status?: string;
}

export interface FieldViewMode {
  mode: 'grid' | 'list' | 'map';
}

export interface FieldStats {
  total: number;
  totalArea: number;
  byCrop: Record<string, number>;
}

export interface FieldError {
  message: string;
  messageAr: string;
}
