/**
 * SAHOOL Fields Feature Types
 * أنواع ميزة الحقول
 */

import type { Field, GeoPolygon } from '@sahool/api-client';

export interface FieldFormData {
  name: string;
  name_ar: string;
  area: number;
  crop?: string;
  crop_ar?: string;
  polygon?: GeoPolygon;
  farm_id?: string;
  description?: string;
  description_ar?: string;
}

export interface FieldFilters {
  search?: string;
  farm_id?: string;
  crop?: string;
  minArea?: number;
  maxArea?: number;
  status?: string;
}

export interface FieldViewMode {
  mode: 'grid' | 'list' | 'map';
}

export type { Field };
