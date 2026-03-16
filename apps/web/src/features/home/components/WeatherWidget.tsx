"use client";

/**
 * SAHOOL Weather Widget Component
 * مكون عنصر الطقس
 */

import React, { useState, useCallback } from "react";
import {
  Cloud,
  CloudRain,
  Sun,
  Wind,
  Droplets,
  RefreshCw,
} from "lucide-react";
import { useWeather } from "../hooks/useWeather";

const getWeatherIcon = (condition?: string) => {
  if (!condition) return <Cloud className="w-8 h-8" />;

  const lower = condition.toLowerCase();
  if (lower.includes("rain"))
    return <CloudRain className="w-8 h-8 text-blue-500" />;
  if (lower.includes("clear") || lower.includes("sunny"))
    return <Sun className="w-8 h-8 text-yellow-500" />;
  return <Cloud className="w-8 h-8 text-gray-400 dark:text-gray-500" />;
};

export const WeatherWidget: React.FC = () => {
  const { data: weather, isLoading, dataUpdatedAt, refetch } = useWeather();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await refetch();
    } finally {
      setIsRefreshing(false);
    }
  }, [refetch]);

  const lastUpdated = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString("ar-EG", {
        hour: "2-digit",
        minute: "2-digit",
      })
    : null;

  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-cyan-900/30 rounded-xl border-2 border-blue-200 dark:border-blue-800 p-6 transition-colors">
        <div className="h-48 flex items-center justify-center">
          <div className="animate-pulse text-gray-400 dark:text-gray-500">
            جاري التحميل...
          </div>
        </div>
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-cyan-900/30 rounded-xl border-2 border-blue-200 dark:border-blue-800 p-6 transition-colors">
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <Cloud className="w-12 h-12 mx-auto mb-2 opacity-20" />
          <p>بيانات الطقس غير متوفرة</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-cyan-900/30 rounded-xl border-2 border-blue-200 dark:border-blue-800 p-6 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white">
            الطقس الحالي
          </h3>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Current Weather
          </span>
        </div>
        <div className="flex items-center gap-2">
          {lastUpdated && (
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {lastUpdated}
            </span>
          )}
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-1.5 text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg hover:bg-blue-100/50 dark:hover:bg-blue-900/50 transition-colors disabled:opacity-50"
            title="تحديث الطقس"
            aria-label="تحديث الطقس"
          >
            <RefreshCw
              className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`}
            />
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="transition-transform hover:scale-110">
            {getWeatherIcon(weather.condition)}
          </div>
          <div>
            <p className="text-4xl font-bold text-gray-900 dark:text-white">
              {weather.temperature}°C
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {weather.conditionAr || weather.condition}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2">
          <Droplets className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">الرطوبة</p>
            <p className="font-semibold text-gray-900 dark:text-white">
              {weather.humidity}%
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Wind className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">الرياح</p>
            <p className="font-semibold text-gray-900 dark:text-white">
              {weather.windSpeed} km/h
            </p>
          </div>
        </div>
      </div>

      {weather.location && (
        <div className="mt-4 pt-4 border-t border-blue-200 dark:border-blue-800">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            {weather.location}
          </p>
        </div>
      )}
    </div>
  );
};

export default WeatherWidget;
