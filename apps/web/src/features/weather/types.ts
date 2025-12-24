/**
 * SAHOOL Weather Feature Types
 * أنواع ميزة الطقس
 */

import type { Severity } from '@sahool/api-client';

export interface WeatherLocation {
  lat: number;
  lon: number;
  name: string;
  nameAr: string;
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  windDirection: string;
  pressure: number;
  visibility: number;
  uvIndex: number;
  condition: string;
  conditionAr: string;
  location: string;
  timestamp: string;
}

export interface ForecastDataPoint {
  date: string;
  temperature: number;
  humidity: number;
  precipitation: number;
  windSpeed: number;
  condition: string;
  conditionAr: string;
}

export interface WeatherForecast {
  location: string;
  forecast: ForecastDataPoint[];
  timestamp: string;
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
  severity: Severity | 'warning' | 'info';
  title: string;
  titleAr?: string;
  description: string;
  descriptionAr?: string;
  affectedAreas: string[];
  affectedAreasAr?: string[];
  startTime: string;
  endTime?: string;
  isActive: boolean;
}
