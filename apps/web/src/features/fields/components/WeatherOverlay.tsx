'use client';

/**
 * SAHOOL Weather Overlay Component
 * مكون عرض الطقس
 *
 * Similar to: Climate FieldView, FarmLogs, Granular Weather
 *
 * Features:
 * - Current weather display (temperature, humidity, wind)
 * - 7-day forecast
 * - Rainfall data
 * - Weather alerts
 * - Integration with field map
 * - Arabic labels and RTL support
 */

import React, { useState, useEffect } from 'react';
import {
  Cloud,
  Sun,
  Droplets,
  Wind,
  Thermometer,
  AlertCircle,
  Calendar,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';

// Weather condition types
type WeatherCondition = 'sunny' | 'partly-cloudy' | 'cloudy' | 'rainy' | 'stormy';

// Forecast day interface
export interface ForecastDay {
  date: string;
  dayName: string;
  dayNameAr: string;
  tempHigh: number;
  tempLow: number;
  condition: WeatherCondition;
  rainfall: number;
  humidity: number;
  windSpeed: number;
}

// Weather data interface
export interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  condition: string;
  forecast: ForecastDay[];
  rainfall24h?: number;
  rainfallWeek?: number;
  pressure?: number;
  uvIndex?: number;
}

// Weather alert interface
interface WeatherAlert {
  id: string;
  type: 'warning' | 'advisory' | 'watch';
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  severity: 'low' | 'medium' | 'high';
  validUntil: string;
}

// Component props
interface WeatherOverlayProps {
  fieldId: string;
  location?: { lat: number; lng: number };
  onWeatherDataLoad?: (data: WeatherData) => void;
  isLoading?: boolean;
}

// Mock weather data for Yemen climate (warm, dry with occasional rain)
const MOCK_WEATHER_DATA: WeatherData = {
  temperature: 28,
  humidity: 45,
  windSpeed: 12,
  condition: 'partly-cloudy',
  rainfall24h: 2.5,
  rainfallWeek: 8.3,
  pressure: 1013,
  uvIndex: 8,
  forecast: [
    {
      date: '2024-12-31',
      dayName: 'Tuesday',
      dayNameAr: 'الثلاثاء',
      tempHigh: 29,
      tempLow: 18,
      condition: 'sunny',
      rainfall: 0,
      humidity: 42,
      windSpeed: 10,
    },
    {
      date: '2025-01-01',
      dayName: 'Wednesday',
      dayNameAr: 'الأربعاء',
      tempHigh: 30,
      tempLow: 19,
      condition: 'sunny',
      rainfall: 0,
      humidity: 40,
      windSpeed: 11,
    },
    {
      date: '2025-01-02',
      dayName: 'Thursday',
      dayNameAr: 'الخميس',
      tempHigh: 28,
      tempLow: 17,
      condition: 'partly-cloudy',
      rainfall: 1.2,
      humidity: 48,
      windSpeed: 15,
    },
    {
      date: '2025-01-03',
      dayName: 'Friday',
      dayNameAr: 'الجمعة',
      tempHigh: 27,
      tempLow: 16,
      condition: 'rainy',
      rainfall: 8.5,
      humidity: 65,
      windSpeed: 18,
    },
    {
      date: '2025-01-04',
      dayName: 'Saturday',
      dayNameAr: 'السبت',
      tempHigh: 26,
      tempLow: 15,
      condition: 'cloudy',
      rainfall: 3.2,
      humidity: 58,
      windSpeed: 14,
    },
    {
      date: '2025-01-05',
      dayName: 'Sunday',
      dayNameAr: 'الأحد',
      tempHigh: 28,
      tempLow: 17,
      condition: 'partly-cloudy',
      rainfall: 0.5,
      humidity: 50,
      windSpeed: 12,
    },
    {
      date: '2025-01-06',
      dayName: 'Monday',
      dayNameAr: 'الإثنين',
      tempHigh: 29,
      tempLow: 18,
      condition: 'sunny',
      rainfall: 0,
      humidity: 44,
      windSpeed: 10,
    },
  ],
};

// Mock weather alerts
const MOCK_ALERTS: WeatherAlert[] = [
  {
    id: '1',
    type: 'advisory',
    title: 'High Temperature Advisory',
    titleAr: 'تنبيه درجات حرارة مرتفعة',
    message: 'Expected high temperatures above 35°C this week. Ensure adequate irrigation.',
    messageAr: 'متوقع درجات حرارة مرتفعة فوق 35 درجة مئوية هذا الأسبوع. تأكد من الري الكافي.',
    severity: 'medium',
    validUntil: '2025-01-03',
  },
  {
    id: '2',
    type: 'warning',
    title: 'Heavy Rain Warning',
    titleAr: 'تحذير من أمطار غزيرة',
    message: 'Heavy rainfall expected on Friday. Risk of flooding in low-lying areas.',
    messageAr: 'متوقع هطول أمطار غزيرة يوم الجمعة. خطر الفيضانات في المناطق المنخفضة.',
    severity: 'high',
    validUntil: '2025-01-04',
  },
];

// Get weather icon based on condition
const getWeatherIcon = (condition: WeatherCondition, className?: string) => {
  switch (condition) {
    case 'sunny':
      return <Sun className={className} />;
    case 'partly-cloudy':
      return <Cloud className={className} />;
    case 'cloudy':
      return <Cloud className={className} />;
    case 'rainy':
      return <Droplets className={className} />;
    case 'stormy':
      return <Cloud className={className} />;
    default:
      return <Sun className={className} />;
  }
};

// Get condition color
const getConditionColor = (condition: WeatherCondition): string => {
  switch (condition) {
    case 'sunny':
      return 'text-yellow-500';
    case 'partly-cloudy':
      return 'text-blue-400';
    case 'cloudy':
      return 'text-gray-500';
    case 'rainy':
      return 'text-blue-600';
    case 'stormy':
      return 'text-purple-600';
    default:
      return 'text-gray-500';
  }
};

// Get condition background
const getConditionBg = (condition: WeatherCondition): string => {
  switch (condition) {
    case 'sunny':
      return 'from-yellow-50 to-orange-50';
    case 'partly-cloudy':
      return 'from-blue-50 to-gray-50';
    case 'cloudy':
      return 'from-gray-50 to-slate-50';
    case 'rainy':
      return 'from-blue-100 to-cyan-50';
    case 'stormy':
      return 'from-purple-100 to-indigo-50';
    default:
      return 'from-gray-50 to-white';
  }
};

// Get alert color
const getAlertColor = (severity: 'low' | 'medium' | 'high'): string => {
  switch (severity) {
    case 'high':
      return 'bg-red-50 border-red-300 text-red-800';
    case 'medium':
      return 'bg-yellow-50 border-yellow-300 text-yellow-800';
    case 'low':
      return 'bg-blue-50 border-blue-300 text-blue-800';
  }
};

// Format date in Arabic
const formatDateAr = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ar-YE', {
    month: 'short',
    day: 'numeric',
  });
};

export const WeatherOverlay: React.FC<WeatherOverlayProps> = ({
  fieldId,
  location,
  onWeatherDataLoad,
  isLoading: externalLoading = false,
}) => {
  const [weatherData, setWeatherData] = useState<WeatherData>(MOCK_WEATHER_DATA);
  const [alerts, setAlerts] = useState<WeatherAlert[]>(MOCK_ALERTS);
  const [isLoading, setIsLoading] = useState(false);
  const [showAlerts, setShowAlerts] = useState(true);

  // Simulate data loading
  useEffect(() => {
    setIsLoading(true);

    // Simulate API call
    const timer = setTimeout(() => {
      setWeatherData(MOCK_WEATHER_DATA);
      setAlerts(MOCK_ALERTS);
      setIsLoading(false);

      // Call the callback with loaded data
      if (onWeatherDataLoad) {
        onWeatherDataLoad(MOCK_WEATHER_DATA);
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [fieldId, location, onWeatherDataLoad]);

  const loading = isLoading || externalLoading;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className={`p-4 border-b border-gray-200 bg-gradient-to-r ${getConditionBg(weatherData.condition as WeatherCondition)}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cloud className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-gray-900">حالة الطقس</h3>
            <span className="text-sm text-gray-500">Weather</span>
          </div>

          {location && (
            <div className="text-xs text-gray-600">
              <span>📍 {location.lat.toFixed(4)}, {location.lng.toFixed(4)}</span>
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="p-8 flex items-center justify-center">
          <div className="text-center">
            <Cloud className="w-12 h-12 text-gray-400 animate-pulse mx-auto mb-2" />
            <p className="text-gray-500">جاري تحميل بيانات الطقس...</p>
          </div>
        </div>
      ) : (
        <>
          {/* Current Weather */}
          <div className={`p-6 bg-gradient-to-br ${getConditionBg(weatherData.condition as WeatherCondition)}`}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Temperature */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <Thermometer className="w-5 h-5 text-red-500" />
                  <span className="text-xs text-gray-500">درجة الحرارة</span>
                </div>
                <div className="text-3xl font-bold text-gray-900">{weatherData.temperature}°</div>
                <div className="text-xs text-gray-600 mt-1">Temperature</div>
              </div>

              {/* Humidity */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <Droplets className="w-5 h-5 text-blue-500" />
                  <span className="text-xs text-gray-500">الرطوبة</span>
                </div>
                <div className="text-3xl font-bold text-gray-900">{weatherData.humidity}%</div>
                <div className="text-xs text-gray-600 mt-1">Humidity</div>
              </div>

              {/* Wind Speed */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <Wind className="w-5 h-5 text-cyan-500" />
                  <span className="text-xs text-gray-500">سرعة الرياح</span>
                </div>
                <div className="text-3xl font-bold text-gray-900">{weatherData.windSpeed}</div>
                <div className="text-xs text-gray-600 mt-1">km/h</div>
              </div>

              {/* Rainfall */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <Droplets className="w-5 h-5 text-indigo-500" />
                  <span className="text-xs text-gray-500">الأمطار (24 ساعة)</span>
                </div>
                <div className="text-3xl font-bold text-gray-900">{weatherData.rainfall24h}</div>
                <div className="text-xs text-gray-600 mt-1">mm</div>
              </div>
            </div>

            {/* Additional Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
              <div className="bg-white/50 rounded-lg p-3 text-center">
                <div className="text-xs text-gray-600 mb-1">أمطار الأسبوع</div>
                <div className="text-lg font-semibold text-gray-900">{weatherData.rainfallWeek} mm</div>
              </div>
              <div className="bg-white/50 rounded-lg p-3 text-center">
                <div className="text-xs text-gray-600 mb-1">الضغط الجوي</div>
                <div className="text-lg font-semibold text-gray-900">{weatherData.pressure} hPa</div>
              </div>
              <div className="bg-white/50 rounded-lg p-3 text-center">
                <div className="text-xs text-gray-600 mb-1">مؤشر الأشعة فوق البنفسجية</div>
                <div className="text-lg font-semibold text-gray-900">{weatherData.uvIndex}/10</div>
              </div>
              <div className="bg-white/50 rounded-lg p-3 text-center">
                <div className="text-xs text-gray-600 mb-1">الحالة</div>
                <div className="text-lg font-semibold text-gray-900 capitalize">{weatherData.condition}</div>
              </div>
            </div>
          </div>

          {/* Weather Alerts */}
          {alerts.length > 0 && showAlerts && (
            <div className="p-4 bg-gray-50 border-b border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-orange-600" />
                  <h4 className="font-semibold text-gray-900">تنبيهات الطقس</h4>
                </div>
                <button
                  onClick={() => setShowAlerts(false)}
                  className="text-xs text-gray-500 hover:text-gray-700"
                >
                  إخفاء
                </button>
              </div>

              <div className="space-y-2">
                {alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded-lg border ${getAlertColor(alert.severity)}`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className="font-semibold text-sm mb-1">{alert.titleAr}</div>
                        <div className="text-xs opacity-90">{alert.messageAr}</div>
                        <div className="text-xs opacity-70 mt-2">
                          صالح حتى: {formatDateAr(alert.validUntil)}
                        </div>
                      </div>
                      <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 7-Day Forecast */}
          <div className="p-4">
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="w-5 h-5 text-blue-600" />
              <h4 className="font-semibold text-gray-900">توقعات الأسبوع</h4>
              <span className="text-sm text-gray-500">7-Day Forecast</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
              {weatherData.forecast.map((day, index) => {
                const prevDay = weatherData.forecast[index - 1];
                const tempChange = index > 0 && prevDay
                  ? day.tempHigh - prevDay.tempHigh
                  : 0;

                return (
                  <div
                    key={day.date}
                    className={`p-3 rounded-xl border transition-all hover:shadow-md ${
                      index === 0
                        ? 'bg-blue-50 border-blue-300'
                        : 'bg-white border-gray-200'
                    }`}
                  >
                    {/* Day Name */}
                    <div className="text-center mb-3">
                      <div className="text-sm font-semibold text-gray-900">
                        {day.dayNameAr}
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatDateAr(day.date)}
                      </div>
                    </div>

                    {/* Weather Icon */}
                    <div className="flex justify-center mb-3">
                      {getWeatherIcon(day.condition, `w-8 h-8 ${getConditionColor(day.condition)}`)}
                    </div>

                    {/* Temperature */}
                    <div className="text-center mb-2">
                      <div className="flex items-center justify-center gap-1">
                        <span className="text-lg font-bold text-gray-900">{day.tempHigh}°</span>
                        {tempChange !== 0 && (
                          tempChange > 0 ? (
                            <TrendingUp className="w-3 h-3 text-red-500" />
                          ) : (
                            <TrendingDown className="w-3 h-3 text-blue-500" />
                          )
                        )}
                      </div>
                      <div className="text-xs text-gray-500">{day.tempLow}°</div>
                    </div>

                    {/* Rainfall */}
                    {day.rainfall > 0 && (
                      <div className="flex items-center justify-center gap-1 text-xs text-blue-600 bg-blue-50 rounded px-2 py-1">
                        <Droplets className="w-3 h-3" />
                        <span>{day.rainfall}mm</span>
                      </div>
                    )}

                    {/* Additional Info */}
                    <div className="mt-2 pt-2 border-t border-gray-100 space-y-1">
                      <div className="flex items-center justify-between text-xs text-gray-600">
                        <Droplets className="w-3 h-3" />
                        <span>{day.humidity}%</span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-600">
                        <Wind className="w-3 h-3" />
                        <span>{day.windSpeed} km/h</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Rainfall Summary */}
          <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 border-t border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Droplets className="w-5 h-5 text-blue-600" />
              <h4 className="font-semibold text-gray-900">ملخص الأمطار</h4>
              <span className="text-sm text-gray-500">Rainfall Summary</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-white/70 rounded-lg p-3">
                <div className="text-xs text-gray-600 mb-1">آخر 24 ساعة</div>
                <div className="text-xl font-bold text-blue-600">{weatherData.rainfall24h} mm</div>
              </div>
              <div className="bg-white/70 rounded-lg p-3">
                <div className="text-xs text-gray-600 mb-1">آخر 7 أيام</div>
                <div className="text-xl font-bold text-blue-600">{weatherData.rainfallWeek} mm</div>
              </div>
              <div className="bg-white/70 rounded-lg p-3">
                <div className="text-xs text-gray-600 mb-1">متوقع (7 أيام)</div>
                <div className="text-xl font-bold text-blue-600">
                  {weatherData.forecast.reduce((sum, day) => sum + day.rainfall, 0).toFixed(1)} mm
                </div>
              </div>
              <div className="bg-white/70 rounded-lg p-3">
                <div className="text-xs text-gray-600 mb-1">أعلى معدل</div>
                <div className="text-xl font-bold text-blue-600">
                  {Math.max(...weatherData.forecast.map(d => d.rainfall)).toFixed(1)} mm
                </div>
              </div>
            </div>

            {/* Rainfall Chart (Simple Bar Visualization) */}
            <div className="mt-4 bg-white/70 rounded-lg p-3">
              <div className="text-xs text-gray-600 mb-2 text-center">توزيع الأمطار المتوقعة</div>
              <div className="flex items-end justify-between gap-1 h-24">
                {weatherData.forecast.map((day) => {
                  const maxRainfall = Math.max(...weatherData.forecast.map(d => d.rainfall));
                  const height = maxRainfall > 0 ? (day.rainfall / maxRainfall) * 100 : 0;

                  return (
                    <div key={day.date} className="flex-1 flex flex-col items-center gap-1">
                      <div className="text-xs text-gray-600 font-medium">
                        {day.rainfall > 0 ? `${day.rainfall}` : ''}
                      </div>
                      <div
                        className="w-full bg-gradient-to-t from-blue-500 to-blue-300 rounded-t transition-all hover:from-blue-600 hover:to-blue-400"
                        style={{ height: `${height}%`, minHeight: day.rainfall > 0 ? '8px' : '2px' }}
                        title={`${day.dayNameAr}: ${day.rainfall}mm`}
                      />
                      <div className="text-xs text-gray-500 text-center">
                        {day.dayNameAr.substring(0, 3)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Footer Info */}
          <div className="p-3 bg-gray-50 border-t border-gray-200 text-center">
            <p className="text-xs text-gray-500">
              آخر تحديث: {new Date().toLocaleString('ar-YE', {
                hour: '2-digit',
                minute: '2-digit',
                day: 'numeric',
                month: 'short'
              })} |
              Last updated: {new Date().toLocaleTimeString('en', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default WeatherOverlay;
