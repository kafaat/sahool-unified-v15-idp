/**
 * SAHOOL Weather Hook
 * خطاف الطقس
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { WeatherData, WeatherForecast, WeatherAlert, ForecastDataPoint } from '../types';

async function fetchCurrentWeather(location: string = 'sanaa'): Promise<WeatherData> {
  const response = await apiClient.get<{
    location_id: string;
    location_name_ar: string;
    latitude: number;
    longitude: number;
    timestamp: string;
    temperature_c: number;
    feels_like_c: number;
    humidity_percent: number;
    pressure_hpa: number;
    wind_speed_kmh: number;
    wind_direction: string;
    wind_gust_kmh: number;
    visibility_km: number;
    cloud_cover_percent: number;
    uv_index: number;
    dew_point_c: number;
    condition: string;
    condition_ar: string;
  }>(`http://localhost:8092/v1/current/${location}`);

  const data = response.data;
  return {
    temperature: data.temperature_c,
    humidity: data.humidity_percent,
    windSpeed: data.wind_speed_kmh,
    windDirection: data.wind_direction,
    pressure: data.pressure_hpa,
    visibility: data.visibility_km,
    uvIndex: data.uv_index,
    condition: data.condition,
    conditionAr: data.condition_ar,
    location: data.location_name_ar,
    timestamp: data.timestamp,
  };
}

async function fetchWeatherForecast(location: string = 'sanaa'): Promise<ForecastDataPoint[]> {
  const response = await apiClient.get<{
    location_id: string;
    location_name_ar: string;
    generated_at: string;
    current: Record<string, unknown>;
    hourly_forecast: Array<Record<string, unknown>>;
    daily_forecast: Array<{
      date: string;
      temp_max_c: number;
      temp_min_c: number;
      humidity_avg: number;
      wind_speed_avg_kmh: number;
      precipitation_total_mm: number;
      precipitation_probability: number;
      sunrise: string;
      sunset: string;
      uv_index_max: number;
      condition: string;
      condition_ar: string;
      agricultural_summary_ar: string;
      agricultural_summary_en: string;
    }>;
    alerts: Array<Record<string, unknown>>;
    growing_degree_days: number;
    evapotranspiration_mm: number;
    spray_window_hours: string[];
    irrigation_recommendation_ar: string;
    irrigation_recommendation_en: string;
  }>(`http://localhost:8092/v1/forecast/${location}`, { params: { days: 7 } });

  // Transform backend daily forecast to frontend format
  return response.data.daily_forecast.map(day => ({
    date: day.date,
    temperature: (day.temp_max_c + day.temp_min_c) / 2,
    humidity: day.humidity_avg,
    precipitation: day.precipitation_total_mm,
    windSpeed: day.wind_speed_avg_kmh,
    condition: day.condition,
    conditionAr: day.condition_ar,
  }));
}

async function fetchWeatherAlerts(location: string = 'sanaa'): Promise<WeatherAlert[]> {
  try {
    const response = await apiClient.get<{
      location_id: string;
      location_name_ar: string;
      generated_at: string;
      current: Record<string, unknown>;
      hourly_forecast: Array<Record<string, unknown>>;
      daily_forecast: Array<Record<string, unknown>>;
      alerts: Array<{
        alert_id: string;
        alert_type: string;
        severity: string;
        title_ar: string;
        title_en: string;
        description_ar: string;
        description_en: string;
        start_time: string;
        end_time: string;
        affected_crops_ar: string[];
        recommendations_ar: string[];
        recommendations_en: string[];
      }>;
      growing_degree_days: number;
      evapotranspiration_mm: number;
      spray_window_hours: string[];
      irrigation_recommendation_ar: string;
      irrigation_recommendation_en: string;
    }>(`http://localhost:8092/v1/forecast/${location}`);

    // Transform backend alerts to frontend format
    return response.data.alerts.map(alert => ({
      id: alert.alert_id,
      type: alert.alert_type,
      severity: alert.severity as 'low' | 'medium' | 'high' | 'critical',
      title: alert.title_en,
      titleAr: alert.title_ar,
      description: alert.description_en,
      descriptionAr: alert.description_ar,
      startDate: alert.start_time,
      endDate: alert.end_time,
      affectedAreas: alert.affected_crops_ar,
      affectedAreasAr: alert.affected_crops_ar,
      recommendations: alert.recommendations_en,
      recommendationsAr: alert.recommendations_ar,
    }));
  } catch (error) {
    console.error('Error fetching weather alerts:', error);
    return [];
  }
}

export function useCurrentWeather(location?: string) {
  return useQuery({
    queryKey: ['weather', 'current', location],
    queryFn: () => fetchCurrentWeather(location),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 minutes
  });
}

export function useWeatherForecast(location?: string) {
  return useQuery({
    queryKey: ['weather', 'forecast', location],
    queryFn: () => fetchWeatherForecast(location),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

export function useWeatherAlerts(location?: string) {
  return useQuery({
    queryKey: ['weather', 'alerts', location],
    queryFn: () => fetchWeatherAlerts(location),
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 15 * 60 * 1000, // Refetch every 15 minutes
  });
}
