"use client";

/**
 * SAHOOL Weather Dashboard Component
 * مكون لوحة الطقس
 */

import React from "react";
import { CurrentWeather } from "./CurrentWeather";
import { ForecastChart } from "./ForecastChart";
import { WeatherAlerts } from "./WeatherAlerts";

interface WeatherDashboardProps {
  lat?: number;
  lon?: number;
  enabled?: boolean;
}

export const WeatherDashboard: React.FC<WeatherDashboardProps> = ({
  lat,
  lon,
  enabled,
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">الطقس</h1>
        <p className="text-gray-600">Weather Dashboard</p>
      </div>

      {/* Weather Alerts */}
      <WeatherAlerts lat={lat} lon={lon} enabled={enabled} />

      {/* Current Weather */}
      <CurrentWeather lat={lat} lon={lon} enabled={enabled} />

      {/* Forecast Chart */}
      <ForecastChart lat={lat} lon={lon} enabled={enabled} />
    </div>
  );
};

export default WeatherDashboard;
