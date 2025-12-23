'use client';

/**
 * SAHOOL Weather Widget Component
 * مكون عنصر الطقس
 */

import React from 'react';
import { Cloud, CloudRain, Sun, Wind, Droplets } from 'lucide-react';
import { useDashboardData } from '../hooks/useDashboardData';

const getWeatherIcon = (condition?: string) => {
  if (!condition) return <Cloud className="w-8 h-8" />;

  const lower = condition.toLowerCase();
  if (lower.includes('rain')) return <CloudRain className="w-8 h-8 text-blue-500" />;
  if (lower.includes('clear') || lower.includes('sunny')) return <Sun className="w-8 h-8 text-yellow-500" />;
  return <Cloud className="w-8 h-8 text-gray-400" />;
};

export const WeatherWidget: React.FC = () => {
  const { data, isLoading } = useDashboardData();

  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-6">
        <div className="h-48 flex items-center justify-center">
          <div className="animate-pulse text-gray-400">جاري التحميل...</div>
        </div>
      </div>
    );
  }

  const weather = data?.weather;

  if (!weather) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-6">
        <div className="text-center py-8 text-gray-500">
          <Cloud className="w-12 h-12 mx-auto mb-2 opacity-20" />
          <p>بيانات الطقس غير متوفرة</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">الطقس الحالي</h3>
        <span className="text-sm text-gray-500">Current Weather</span>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          {getWeatherIcon(weather.condition)}
          <div>
            <p className="text-4xl font-bold text-gray-900">{weather.temperature}°C</p>
            <p className="text-sm text-gray-600">{weather.conditionAr || weather.condition}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2">
          <Droplets className="w-5 h-5 text-blue-600" />
          <div>
            <p className="text-xs text-gray-500">الرطوبة</p>
            <p className="font-semibold text-gray-900">{weather.humidity}%</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Wind className="w-5 h-5 text-cyan-600" />
          <div>
            <p className="text-xs text-gray-500">الرياح</p>
            <p className="font-semibold text-gray-900">{weather.windSpeed} km/h</p>
          </div>
        </div>
      </div>

      {weather.location && (
        <div className="mt-4 pt-4 border-t border-blue-200">
          <p className="text-xs text-gray-500 text-center">{weather.location}</p>
        </div>
      )}
    </div>
  );
};

export default WeatherWidget;
