'use client';

/**
 * SAHOOL Forecast Chart Component
 * مكون مخطط التنبؤ
 */

import React from 'react';
import { Calendar, TrendingUp } from 'lucide-react';
import { useWeatherForecast } from '../hooks/useWeather';

interface ForecastChartProps {
  lat?: number;
  lon?: number;
  days?: number;
  enabled?: boolean;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({ lat, lon, days = 7, enabled }) => {
  const { data: forecast, isLoading } = useWeatherForecast({ lat, lon, days, enabled });

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="forecast-loading">
        <h2 className="text-2xl font-bold text-gray-900 mb-6" data-testid="forecast-title">توقعات 7 أيام</h2>
        <div className="h-64 bg-gray-100 rounded-lg animate-pulse" />
      </div>
    );
  }

  if (!forecast || forecast.length === 0) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="forecast-no-data">
        <h2 className="text-2xl font-bold text-gray-900 mb-6" data-testid="forecast-title">توقعات 7 أيام</h2>
        <div className="text-center py-16 text-gray-500">
          <Calendar className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p data-testid="forecast-no-data-message">لا توجد بيانات توقعات متاحة</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="forecast-chart">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900" data-testid="forecast-title">توقعات 7 أيام</h2>
        <span className="text-sm text-gray-600" data-testid="forecast-subtitle">7-Day Forecast</span>
      </div>

      {/* Simple Bar Chart Representation */}
      <div className="space-y-4" data-testid="forecast-list">
        {forecast.map((day, index) => {
          const date = new Date(day.date);
          const maxTemp = Math.round(day.temperature);
          const tempPercent = ((maxTemp - 15) / 25) * 100; // Scale 15-40°C to 0-100%

          return (
            <div key={index} className="flex items-center gap-4" data-testid={`forecast-day-${index}`}>
              {/* Date */}
              <div className="w-24 text-sm" data-testid={`forecast-day-${index}-date`}>
                <p className="font-medium text-gray-900">
                  {date.toLocaleDateString('ar-EG', { weekday: 'short' })}
                </p>
                <p className="text-xs text-gray-500">
                  {date.toLocaleDateString('ar-EG', { month: 'short', day: 'numeric' })}
                </p>
              </div>

              {/* Condition */}
              <div className="w-32 text-sm text-gray-600" data-testid={`forecast-day-${index}-condition`}>
                {day.conditionAr}
              </div>

              {/* Temperature Bar */}
              <div className="flex-1">
                <div className="h-8 bg-gray-100 rounded-lg overflow-hidden relative" data-testid={`forecast-day-${index}-temp-bar`}>
                  <div
                    className="h-full bg-gradient-to-r from-blue-400 to-red-400 rounded-lg transition-all"
                    style={{ width: `${Math.max(20, Math.min(100, tempPercent))}%` }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-semibold text-gray-900" data-testid={`forecast-day-${index}-temp`}>
                      {maxTemp}°C
                    </span>
                  </div>
                </div>
              </div>

              {/* Additional Info */}
              <div className="w-24 text-sm text-gray-500 text-left" dir="ltr" data-testid={`forecast-day-${index}-humidity`}>
                💧 {Math.round(day.humidity)}%
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-6 border-t-2 border-gray-100 flex items-center justify-center gap-8 text-sm text-gray-600" data-testid="forecast-legend">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4" />
          <span>درجة الحرارة</span>
        </div>
        <div className="flex items-center gap-2">
          <span>💧</span>
          <span>الرطوبة</span>
        </div>
      </div>
    </div>
  );
};

export default ForecastChart;
