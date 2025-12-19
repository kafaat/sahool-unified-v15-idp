/**
 * Weather Mock Data
 * بيانات الطقس الوهمية
 */

import { generateId, randomFloat, randomItem } from './utils';

export type WeatherCondition = 'sunny' | 'cloudy' | 'rainy' | 'partly_cloudy' | 'windy' | 'stormy';

export interface MockWeatherData {
  id: string;
  fieldId: string;
  timestamp: string;
  temperature: number;
  humidity: number;
  windSpeed: number;
  windDirection: string;
  precipitation: number;
  condition: WeatherCondition;
  uvIndex: number;
  visibility: number;
  pressure: number;
}

export interface MockWeatherForecast {
  id: string;
  fieldId: string;
  date: string;
  high: number;
  low: number;
  condition: WeatherCondition;
  precipitationChance: number;
  humidity: number;
  windSpeed: number;
}

const windDirections = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];

const conditionArabic: Record<WeatherCondition, string> = {
  sunny: 'مشمس',
  cloudy: 'غائم',
  rainy: 'ممطر',
  partly_cloudy: 'غائم جزئياً',
  windy: 'عاصف',
  stormy: 'عاصف مع أمطار',
};

/**
 * Generate mock weather data for a field
 */
export function generateMockWeather(fieldId?: string): MockWeatherData {
  const condition = randomItem<WeatherCondition>([
    'sunny',
    'cloudy',
    'rainy',
    'partly_cloudy',
    'windy',
    'stormy',
  ]);

  return {
    id: generateId(),
    fieldId: fieldId || generateId(),
    timestamp: new Date().toISOString(),
    temperature: randomFloat(20, 45, 1), // Yemen is hot
    humidity: randomFloat(30, 80, 0),
    windSpeed: randomFloat(0, 30, 1),
    windDirection: randomItem(windDirections),
    precipitation: condition === 'rainy' || condition === 'stormy' ? randomFloat(0, 50, 1) : 0,
    condition,
    uvIndex: randomFloat(1, 11, 0),
    visibility: randomFloat(5, 20, 1),
    pressure: randomFloat(1010, 1025, 0),
  };
}

/**
 * Generate mock weather forecast
 */
export function generateMockForecast(fieldId?: string, days: number = 7): MockWeatherForecast[] {
  const forecasts: MockWeatherForecast[] = [];
  const startDate = new Date();

  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);

    const condition = randomItem<WeatherCondition>([
      'sunny',
      'cloudy',
      'rainy',
      'partly_cloudy',
      'windy',
      'stormy',
    ]);

    forecasts.push({
      id: generateId(),
      fieldId: fieldId || generateId(),
      date: date.toISOString().split('T')[0],
      high: randomFloat(30, 45, 0),
      low: randomFloat(18, 28, 0),
      condition,
      precipitationChance:
        condition === 'rainy' || condition === 'stormy'
          ? randomFloat(60, 100, 0)
          : randomFloat(0, 30, 0),
      humidity: randomFloat(30, 80, 0),
      windSpeed: randomFloat(5, 25, 0),
    });
  }

  return forecasts;
}

/**
 * Get Arabic label for weather condition
 */
export function getWeatherConditionLabel(condition: WeatherCondition): string {
  return conditionArabic[condition] || condition;
}

/**
 * Generate historical weather data
 */
export function generateHistoricalWeather(
  fieldId: string,
  days: number = 30
): MockWeatherData[] {
  const data: MockWeatherData[] = [];
  const now = new Date();

  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    const weatherData = generateMockWeather(fieldId);
    weatherData.timestamp = date.toISOString();
    data.push(weatherData);
  }

  return data;
}
