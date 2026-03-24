/**
 * Farms Feature - Types
 * أنواع ميزة المزارع
 */

export type FarmStatus = 'active' | 'inactive' | 'seasonal';

export interface Farm {
  id: string;
  name: string;
  nameAr: string;
  owner: string;
  ownerAr: string;
  location: string;
  locationAr: string;
  region: string;
  regionAr: string;
  totalAreaHa: number;
  cultivatedAreaHa: number;
  fieldsCount: number;
  workersCount: number;
  waterSource: string;
  waterSourceAr: string;
  status: FarmStatus;
  coordinates?: { lat: number; lng: number };
  createdAt: string;
  updatedAt: string;
}

export interface FarmFilters {
  status?: FarmStatus;
  region?: string;
  search?: string;
}

export interface FarmFormData {
  name: string;
  nameAr: string;
  location: string;
  locationAr: string;
  region: string;
  regionAr: string;
  totalAreaHa: number;
  waterSource: string;
  waterSourceAr: string;
  coordinates?: { lat: number; lng: number };
}

export interface FarmStats {
  totalFarms: number;
  activeFarms: number;
  totalAreaHa: number;
  cultivatedAreaHa: number;
  totalWorkers: number;
}
