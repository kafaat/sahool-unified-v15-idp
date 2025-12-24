/**
 * Sensors Dashboard Component
 * مكون لوحة المستشعرات
 */

'use client';

import { useSensors, useSensorStats } from '../hooks/useSensors';
import { SensorCard } from './SensorCard';
import { Activity, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

interface SensorsDashboardProps {
  onSensorClick?: (sensorId: string) => void;
}

export function SensorsDashboard({ onSensorClick }: SensorsDashboardProps) {
  const { data: sensors, isLoading: sensorsLoading } = useSensors();
  const { data: stats, isLoading: statsLoading } = useSensorStats();

  if (sensorsLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <span className="mr-3 text-gray-600">جاري التحميل...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">إجمالي المستشعرات</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
              </div>
              <Activity className="w-12 h-12 text-blue-600 opacity-50" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">المستشعرات النشطة</p>
                <p className="text-3xl font-bold text-green-600 mt-2">{stats.active}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-600 opacity-50" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">رطوبة التربة</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">
                  {stats.byType.soil_moisture || 0}
                </p>
              </div>
              <div className="text-4xl opacity-50">💧</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">درجة الحرارة</p>
                <p className="text-3xl font-bold text-orange-600 mt-2">
                  {stats.byType.temperature || 0}
                </p>
              </div>
              <div className="text-4xl opacity-50">🌡️</div>
            </div>
          </div>
        </div>
      )}

      {/* Status Overview */}
      {stats && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">حالة المستشعرات</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.byStatus.active || 0}</div>
              <div className="text-sm text-gray-600">نشط</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">{stats.byStatus.inactive || 0}</div>
              <div className="text-sm text-gray-600">غير نشط</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{stats.byStatus.error || 0}</div>
              <div className="text-sm text-gray-600">خطأ</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {stats.byStatus.maintenance || 0}
              </div>
              <div className="text-sm text-gray-600">صيانة</div>
            </div>
          </div>
        </div>
      )}

      {/* Sensors Grid */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">المستشعرات</h3>
        {sensors && sensors.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sensors.map((sensor) => (
              <div key={sensor.id} onClick={() => onSensorClick?.(sensor.id)}>
                <SensorCard sensor={sensor} />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500">لا توجد مستشعرات</p>
          </div>
        )}
      </div>
    </div>
  );
}
