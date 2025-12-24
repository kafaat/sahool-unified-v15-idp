/**
 * SAHOOL Weather Feature Types
 * أنواع ميزة الطقس
 */

import type { WeatherData, WeatherForecast, DailyForecast, WeatherAlert } from '@sahool/api-client';

export interface WeatherLocation {
  lat: number;
  lon: number;
  name: string;
  nameAr: string;
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

export type { WeatherData, WeatherForecast, DailyForecast, WeatherAlert };
