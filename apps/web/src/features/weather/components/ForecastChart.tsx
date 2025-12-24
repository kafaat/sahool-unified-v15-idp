'use client';

/**
 * SAHOOL Forecast Chart Component
 * مكون مخطط التنبؤ
 */

import React from 'react';
import { Calendar, TrendingUp } from 'lucide-react';
import { useWeatherForecast } from '../hooks/useWeather';

interface ForecastChartProps {
  location?: string;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({ location }) => {
  const { data: forecast, isLoading } = useWeatherForecast(location);

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">توقعات 7 أيام</h2>
        <div className="h-64 bg-gray-100 rounded-lg animate-pulse" />
      </div>
    );
  }

  if (!forecast || forecast.length === 0) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">توقعات 7 أيام</h2>
        <div className="text-center py-16 text-gray-500">
          <Calendar className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p>لا توجد بيانات توقعات متاحة</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">توقعات 7 أيام</h2>
        <span className="text-sm text-gray-600">7-Day Forecast</span>
      </div>

      {/* Simple Bar Chart Representation */}
      <div className="space-y-4">
        {forecast.map((day, index) => {
          const date = new Date(day.date);
          const maxTemp = Math.round(day.temperature);
          const tempPercent = ((maxTemp - 15) / 25) * 100; // Scale 15-40°C to 0-100%

          return (
            <div key={index} className="flex items-center gap-4">
              {/* Date */}
              <div className="w-24 text-sm">
                <p className="font-medium text-gray-900">
                  {date.toLocaleDateString('ar-EG', { weekday: 'short' })}
                </p>
                <p className="text-xs text-gray-500">
                  {date.toLocaleDateString('ar-EG', { month: 'short', day: 'numeric' })}
                </p>
              </div>

              {/* Condition */}
              <div className="w-32 text-sm text-gray-600">
                {day.conditionAr}
              </div>

              {/* Temperature Bar */}
              <div className="flex-1">
                <div className="h-8 bg-gray-100 rounded-lg overflow-hidden relative">
                  <div
                    className="h-full bg-gradient-to-r from-blue-400 to-red-400 rounded-lg transition-all"
                    style={{ width: `${Math.max(20, Math.min(100, tempPercent))}%` }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-semibold text-gray-900">
                      {maxTemp}°C
                    </span>
                  </div>
                </div>
              </div>

              {/* Additional Info */}
              <div className="w-24 text-sm text-gray-500 text-left" dir="ltr">
                💧 {Math.round(day.humidity)}%
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-6 border-t-2 border-gray-100 flex items-center justify-center gap-8 text-sm text-gray-600">
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
