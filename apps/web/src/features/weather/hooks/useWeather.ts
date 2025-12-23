/**
 * SAHOOL Weather Hook
 * خطاف الطقس
 */

import { useQuery } from '@tanstack/react-query';
import type { WeatherData, WeatherForecast, WeatherAlert, ForecastDataPoint } from '../types';

async function fetchCurrentWeather(location?: string): Promise<WeatherData> {
  // TODO: Replace with actual API call
  // const response = await fetch(`/api/weather/current?location=${location}`);
  // return response.json();

  // Mock data
  return {
    temperature: 28,
    humidity: 65,
    windSpeed: 12,
    windDirection: 'NE',
    pressure: 1013,
    visibility: 10,
    uvIndex: 7,
    condition: 'Partly Cloudy',
    conditionAr: 'غائم جزئياً',
    location: location || 'صنعاء، اليمن',
    timestamp: new Date().toISOString(),
  };
}

async function fetchWeatherForecast(location?: string): Promise<ForecastDataPoint[]> {
  // TODO: Replace with actual API call
  // const response = await fetch(`/api/weather/forecast?location=${location}`);
  // return response.json();

  // Mock 7-day forecast
  const days = 7;
  const forecast: ForecastDataPoint[] = [];

  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() + i);

    forecast.push({
      date: date.toISOString(),
      temperature: 25 + Math.random() * 10,
      humidity: 50 + Math.random() * 30,
      precipitation: Math.random() * 20,
      windSpeed: 10 + Math.random() * 15,
      condition: i % 2 === 0 ? 'Sunny' : 'Partly Cloudy',
      conditionAr: i % 2 === 0 ? 'مشمس' : 'غائم جزئياً',
    });
  }

  return forecast;
}

async function fetchWeatherAlerts(location?: string): Promise<WeatherAlert[]> {
  // TODO: Replace with actual API call
  // const response = await fetch(`/api/weather/alerts?location=${location}`);
  // return response.json();

  // Mock data
  return [
    {
      id: '1',
      type: 'temperature',
      severity: 'warning',
      title: 'High Temperature Alert',
      titleAr: 'تنبيه درجة حرارة عالية',
      description: 'Expected high temperatures above 35°C',
      descriptionAr: 'من المتوقع درجات حرارة عالية تتجاوز 35 درجة مئوية',
      startDate: new Date().toISOString(),
      endDate: new Date(Date.now() + 1000 * 60 * 60 * 48).toISOString(),
      affectedAreas: ['Sana\'a', 'Aden'],
      affectedAreasAr: ['صنعاء', 'عدن'],
      recommendations: ['Stay hydrated', 'Avoid outdoor activities during peak hours'],
      recommendationsAr: ['حافظ على رطوبة جسمك', 'تجنب الأنشطة الخارجية خلال ساعات الذروة'],
    },
  ];
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
