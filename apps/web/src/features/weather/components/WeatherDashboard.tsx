'use client';

/**
 * SAHOOL Weather Dashboard Component
 * مكون لوحة الطقس
 */

import React from 'react';
import { CurrentWeather } from './CurrentWeather';
import { ForecastChart } from './ForecastChart';
import { WeatherAlerts } from './WeatherAlerts';

interface WeatherDashboardProps {
  location?: string;
}

export const WeatherDashboard: React.FC<WeatherDashboardProps> = ({ location }) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">الطقس</h1>
        <p className="text-gray-600">Weather Dashboard</p>
      </div>

      {/* Weather Alerts */}
      <WeatherAlerts location={location} />

      {/* Current Weather */}
      <CurrentWeather location={location} />

      {/* Forecast Chart */}
      <ForecastChart location={location} />
    </div>
  );
};

export default WeatherDashboard;
