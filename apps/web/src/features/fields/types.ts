/**
 * SAHOOL Fields Feature Types
 * أنواع ميزة الحقول
 */

import type { Field, GeoPolygon } from '@sahool/api-client';

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

export type { Field };
