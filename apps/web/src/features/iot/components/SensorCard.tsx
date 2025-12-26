/**
 * Sensor Card Component
 * مكون بطاقة المستشعر
 */

'use client';

import Link from 'next/link';
import { useLatestReading } from '../hooks/useSensors';
import type { Sensor } from '../types';
import { Activity, Battery, MapPin, Signal, TrendingUp } from 'lucide-react';

interface SensorCardProps {
  sensor: Sensor;
  onClick?: (sensorId: string) => void;
}

const statusColors = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  error: 'bg-red-100 text-red-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
};

const statusLabels = {
  active: 'نشط',
  inactive: 'غير نشط',
  error: 'خطأ',
  maintenance: 'صيانة',
};

const typeLabels = {
  soil_moisture: 'رطوبة التربة',
  temperature: 'درجة الحرارة',
  humidity: 'الرطوبة',
  ph: 'الحموضة pH',
  light: 'الإضاءة',
  pressure: 'الضغط',
  rain: 'المطر',
  wind: 'الرياح',
};

const typeIcons = {
  soil_moisture: '💧',
  temperature: '🌡️',
  humidity: '💨',
  ph: '⚗️',
  light: '☀️',
  pressure: '📊',
  rain: '🌧️',
  wind: '🌬️',
};

export function SensorCard({ sensor, onClick }: SensorCardProps) {
  const { data: latestReading } = useLatestReading(sensor.id);

  const reading = latestReading || sensor.lastReading;

  const handleClick = () => {
    if (onClick) {
      onClick(sensor.id);
    }
  };

  const cardContent = (
    <div
      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 space-y-4 cursor-pointer"
      onClick={onClick ? handleClick : undefined}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && handleClick() : undefined}
    >
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <div className="text-3xl">{typeIcons[sensor.type]}</div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">{sensor.nameAr}</h3>
              <p className="text-sm text-gray-500">{sensor.name}</p>
              <p className="text-xs text-gray-400 mt-1">{typeLabels[sensor.type]}</p>
            </div>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[sensor.status]}`}
          >
            {statusLabels[sensor.status]}
          </span>
        </div>

        {/* Latest Reading */}
        {reading && (
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">القراءة الحالية</p>
                <p className="text-3xl font-bold text-green-700 mt-1">
                  {reading.value.toFixed(1)}
                  <span className="text-lg mr-2">{reading.unit}</span>
                </p>
              </div>
              <Activity className="w-8 h-8 text-green-600 opacity-50" />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              آخر تحديث: {new Date(reading.timestamp).toLocaleString('ar-YE')}
            </p>
          </div>
        )}

        {/* Sensor Info */}
        <div className="space-y-2 text-sm">
          {sensor.location && (
            <div className="flex items-center text-gray-600">
              <MapPin className="w-4 h-4 ml-2" />
              <span>{sensor.location.fieldName || 'موقع المستشعر'}</span>
            </div>
          )}

          <div className="flex items-center justify-between">
            {sensor.battery !== undefined && (
              <div className="flex items-center text-gray-600">
                <Battery className="w-4 h-4 ml-2" />
                <span>{sensor.battery}%</span>
              </div>
            )}

            {sensor.signalStrength !== undefined && (
              <div className="flex items-center text-gray-600">
                <Signal className="w-4 h-4 ml-2" />
                <span>{sensor.signalStrength}%</span>
              </div>
            )}
          </div>

          <div className="pt-2 border-t border-gray-100">
            <p className="text-xs text-gray-400">معرف الجهاز: {sensor.deviceId}</p>
          </div>
        </div>
      </div>
  );

  // If onClick is provided, don't wrap with Link
  if (onClick) {
    return cardContent;
  }

  return (
    <Link href={`/iot/sensors/${sensor.id}`}>
      {cardContent}
    </Link>
  );
}
