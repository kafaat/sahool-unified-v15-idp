'use client';

/**
 * SAHOOL Weather Alerts Component
 * مكون تنبيهات الطقس
 */

import React from 'react';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { useWeatherAlerts } from '../hooks/useWeather';
import type { WeatherAlert } from '../types';

interface WeatherAlertsProps {
  location?: string;
}

const severityIcons: Record<string, React.ReactElement> = {
  critical: <AlertTriangle className="w-6 h-6 text-red-600" />,
  high: <AlertTriangle className="w-6 h-6 text-red-500" />,
  warning: <AlertCircle className="w-6 h-6 text-orange-600" />,
  medium: <AlertCircle className="w-6 h-6 text-orange-500" />,
  low: <Info className="w-6 h-6 text-yellow-600" />,
  info: <Info className="w-6 h-6 text-blue-600" />,
};

const severityColors: Record<string, string> = {
  critical: 'bg-red-50 border-red-200',
  high: 'bg-red-50 border-red-200',
  warning: 'bg-orange-50 border-orange-200',
  medium: 'bg-orange-50 border-orange-200',
  low: 'bg-yellow-50 border-yellow-200',
  info: 'bg-blue-50 border-blue-200',
};

const severityLabels: Record<string, string> = {
  critical: 'حرج',
  high: 'مرتفع',
  warning: 'تحذير',
  medium: 'متوسط',
  low: 'منخفض',
  info: 'معلومات',
};

const AlertCard: React.FC<{ alert: WeatherAlert }> = ({ alert }) => {
  return (
    <div className={`rounded-xl border-2 p-5 ${severityColors[alert.severity]}`}>
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 mt-1">
          {severityIcons[alert.severity]}
        </div>
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-lg font-bold text-gray-900">
                {alert.titleAr || alert.title}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {severityLabels[alert.severity]} - {alert.severity}
              </p>
            </div>
          </div>

          {/* Description */}
          <p className="text-gray-700 mb-4">
            {alert.descriptionAr || alert.description}
          </p>

          {/* Time Period */}
          <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
            <div>
              <span className="font-medium">من: </span>
              {new Date(alert.startTime || alert.start_date || '').toLocaleString('ar-EG')}
            </div>
            {alert.endTime && (
              <div>
                <span className="font-medium">إلى: </span>
                {new Date(alert.endTime).toLocaleString('ar-EG')}
              </div>
            )}
          </div>

          {/* Affected Areas */}
          {alert.affectedAreas && alert.affectedAreas.length > 0 && (
            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">المناطق المتأثرة:</p>
              <div className="flex flex-wrap gap-2">
                {alert.affectedAreas.map((area, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-white rounded-full text-sm text-gray-700"
                  >
                    {area}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const WeatherAlerts: React.FC<WeatherAlertsProps> = ({ location }) => {
  const { data: alerts, isLoading } = useWeatherAlerts(location);

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">تنبيهات الطقس</h2>
        <div className="space-y-4">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">تنبيهات الطقس</h2>
        <div className="text-center py-8 bg-green-50 rounded-lg">
          <Info className="w-12 h-12 mx-auto mb-3 text-green-600" />
          <p className="text-green-700 font-medium">لا توجد تنبيهات طقس حالية</p>
          <p className="text-sm text-green-600 mt-1">الأحوال الجوية طبيعية</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">تنبيهات الطقس</h2>
        <span className="text-sm text-gray-600">Weather Alerts</span>
      </div>

      <div className="space-y-4">
        {alerts.map((alert) => (
          <AlertCard key={alert.id} alert={alert} />
        ))}
      </div>
    </div>
  );
};

export default WeatherAlerts;
