'use client';

/**
 * SAHOOL Current Weather Component
 * مكون الطقس الحالي
 */

import React from 'react';
import { Cloud, CloudRain, Sun, Wind, Droplets, Gauge, Eye, Sunrise } from 'lucide-react';
import { useCurrentWeather } from '../hooks/useWeather';

interface CurrentWeatherProps {
  location?: string;
}

const getWeatherIcon = (condition?: string) => {
  if (!condition) return <Cloud className="w-16 h-16" />;

  const lower = condition.toLowerCase();
  if (lower.includes('rain')) return <CloudRain className="w-16 h-16 text-blue-500" />;
  if (lower.includes('clear') || lower.includes('sunny')) return <Sun className="w-16 h-16 text-yellow-500" />;
  return <Cloud className="w-16 h-16 text-gray-400" />;
};

export const CurrentWeather: React.FC<CurrentWeatherProps> = ({ location }) => {
  const { data: weather, isLoading } = useCurrentWeather(location);

  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-8">
        <div className="h-64 flex items-center justify-center">
          <div className="animate-pulse text-gray-400">جاري تحميل بيانات الطقس...</div>
        </div>
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-8">
        <div className="text-center py-8 text-gray-500">
          <Cloud className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p>بيانات الطقس غير متوفرة</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">الطقس الحالي</h2>
        <span className="text-sm text-gray-600">Current Weather</span>
      </div>

      {/* Main Weather Display */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-6">
          {getWeatherIcon(weather.condition)}
          <div>
            <p className="text-6xl font-bold text-gray-900">{Math.round(weather.temperature ?? weather.temperature_c)}°C</p>
            <p className="text-xl text-gray-600 mt-2">{weather.conditionAr || weather.condition}</p>
            {weather.location && (
              <p className="text-sm text-gray-500 mt-1">{weather.location}</p>
            )}
          </div>
        </div>
      </div>

      {/* Weather Details Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Droplets className="w-5 h-5 text-blue-600" />
            <p className="text-sm text-gray-600">الرطوبة</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">{weather.humidity}%</p>
        </div>

        <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Wind className="w-5 h-5 text-cyan-600" />
            <p className="text-sm text-gray-600">الرياح</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">{weather.windSpeed} km/h</p>
          {weather.windDirection && (
            <p className="text-xs text-gray-500">{weather.windDirection}</p>
          )}
        </div>

        {weather.pressure && (
          <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Gauge className="w-5 h-5 text-purple-600" />
              <p className="text-sm text-gray-600">الضغط</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">{weather.pressure}</p>
            <p className="text-xs text-gray-500">hPa</p>
          </div>
        )}

        {weather.visibility && (
          <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Eye className="w-5 h-5 text-green-600" />
              <p className="text-sm text-gray-600">الرؤية</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">{weather.visibility}</p>
            <p className="text-xs text-gray-500">km</p>
          </div>
        )}

        {weather.uvIndex !== undefined && (
          <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Sunrise className="w-5 h-5 text-orange-600" />
              <p className="text-sm text-gray-600">مؤشر UV</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">{weather.uvIndex}</p>
          </div>
        )}
      </div>

      {/* Timestamp */}
      {weather.timestamp && (
        <div className="mt-6 text-center text-sm text-gray-500">
          آخر تحديث: {new Date(weather.timestamp).toLocaleString('ar-EG')}
        </div>
      )}
    </div>
  );
};

export default CurrentWeather;
