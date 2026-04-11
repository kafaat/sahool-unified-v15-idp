'use client';

import React, { useState, useMemo } from 'react';
import {
  Radio,
  Search,
  Wifi,
  WifiOff,
  Battery,
  Thermometer,
  Droplets,
  Wind,
  AlertTriangle,
  Loader2,
  X,
} from 'lucide-react';
import { useSensors, useSensor } from '@/features/iot';
import type { SensorType, SensorStatus, SensorFilters } from '@/features/iot';

const sensorTypes: Record<string, { icon: React.ReactNode; label: string; labelAr: string }> = {
  soil_moisture: {
    icon: <Droplets className="w-5 h-5" />,
    label: 'Soil Moisture',
    labelAr: 'رطوبة التربة',
  },
  temperature: {
    icon: <Thermometer className="w-5 h-5" />,
    label: 'Temperature',
    labelAr: 'الحرارة',
  },
  humidity: { icon: <Droplets className="w-5 h-5" />, label: 'Humidity', labelAr: 'الرطوبة' },
  wind: { icon: <Wind className="w-5 h-5" />, label: 'Wind', labelAr: 'الرياح' },
  rain: { icon: <Droplets className="w-5 h-5" />, label: 'Rain', labelAr: 'الأمطار' },
  ndvi: { icon: <Radio className="w-5 h-5" />, label: 'NDVI', labelAr: 'مؤشر النبات' },
  ph: { icon: <Radio className="w-5 h-5" />, label: 'pH', labelAr: 'الحموضة' },
  light: { icon: <Radio className="w-5 h-5" />, label: 'Light', labelAr: 'الإضاءة' },
  pressure: { icon: <Radio className="w-5 h-5" />, label: 'Pressure', labelAr: 'الضغط' },
};

export default function SensorsClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<SensorStatus | 'all'>('all');
  const [typeFilter, setTypeFilter] = useState<SensorType | 'all'>('all');
  const [selectedSensorId, setSelectedSensorId] = useState<string | null>(null);

  // Build API filters from UI state
  const apiFilters: SensorFilters | undefined = useMemo(() => {
    const filters: SensorFilters = {};
    if (statusFilter !== 'all') filters.status = statusFilter;
    if (typeFilter !== 'all') filters.type = typeFilter;
    if (searchTerm) filters.search = searchTerm;
    return Object.keys(filters).length > 0 ? filters : undefined;
  }, [statusFilter, typeFilter, searchTerm]);

  const { data: sensors = [], isLoading, isError, error } = useSensors(apiFilters);
  const { data: sensorDetail } = useSensor(selectedSensorId ?? '');

  // Client-side search fallback (in case API does not support text search)
  const filteredSensors = useMemo(() => {
    if (!searchTerm) return sensors;
    return sensors.filter((sensor) => {
      const matchesSearch =
        sensor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        sensor.nameAr.includes(searchTerm);
      return matchesSearch;
    });
  }, [sensors, searchTerm]);

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      online: 'bg-green-100 text-green-800',
      active: 'bg-green-100 text-green-800',
      offline: 'bg-red-100 text-red-800',
      inactive: 'bg-red-100 text-red-800',
      error: 'bg-red-100 text-red-800',
      warning: 'bg-yellow-100 text-yellow-800',
      maintenance: 'bg-blue-100 text-blue-800',
    };
    const labels: Record<string, string> = {
      online: 'متصل',
      active: 'متصل',
      offline: 'غير متصل',
      inactive: 'غير متصل',
      error: 'خطأ',
      warning: 'تحذير',
      maintenance: 'صيانة',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] ?? 'bg-gray-100 text-gray-800'}`}>
        {labels[status] ?? status}
      </span>
    );
  };

  const getStatusIcon = (status: string) => {
    if (status === 'online' || status === 'active')
      return <Wifi className="w-4 h-4 text-green-500" />;
    if (status === 'offline' || status === 'inactive')
      return <WifiOff className="w-4 h-4 text-red-500" />;
    return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
  };

  const getBatteryColor = (level: number) => {
    if (level > 50) return 'text-green-600';
    if (level > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const onlineCount = sensors.filter(
    (s) => s.status === 'online' || s.status === 'active'
  ).length;
  const offlineCount = sensors.filter(
    (s) => s.status === 'offline' || s.status === 'inactive'
  ).length;
  const warningCount = sensors.filter(
    (s) => s.status === 'error' || s.status === 'maintenance' || (s.battery != null && s.battery < 20)
  ).length;
  const lowBatteryCount = sensors.filter((s) => s.battery != null && s.battery < 20).length;

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-600 font-medium">جاري تحميل بيانات الحساسات...</p>
          <p className="text-sm text-gray-400 mt-1">Loading sensors data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            فشل في تحميل بيانات الحساسات
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            {error instanceof Error ? error.message : 'Failed to load sensors data'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 transition-colors"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">مراقبة الحساسات</h1>
          <p className="text-gray-500 mt-1">Sensors Monitoring</p>
        </div>
      </div>

      {/* Alerts */}
      {(offlineCount > 0 || warningCount > 0) && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span className="font-medium text-amber-800">
              تنبيه: {offlineCount} حساس غير متصل، {warningCount} يحتاج اهتمام
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Radio className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الحساسات</div>
              <div className="text-xl font-bold text-gray-900">{sensors.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Wifi className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متصل</div>
              <div className="text-xl font-bold text-green-600">{onlineCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <WifiOff className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">غير متصل</div>
              <div className="text-xl font-bold text-red-600">{offlineCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Battery className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">بطارية منخفضة</div>
              <div className="text-xl font-bold text-yellow-600">{lowBatteryCount}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث عن حساس..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as SensorStatus | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الحالات</option>
          <option value="online">متصل</option>
          <option value="offline">غير متصل</option>
          <option value="error">خطأ</option>
          <option value="maintenance">صيانة</option>
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as SensorType | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الأنواع</option>
          <option value="soil_moisture">رطوبة التربة</option>
          <option value="temperature">الحرارة</option>
          <option value="humidity">الرطوبة</option>
          <option value="wind">الرياح</option>
        </select>
      </div>

      {/* Empty state */}
      {filteredSensors.length === 0 && (
        <div className="bg-white rounded-lg border p-8 text-center">
          <Radio className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد حساسات</h3>
          <p className="text-gray-500 text-sm">
            {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
              ? 'لا توجد نتائج تطابق معايير البحث'
              : 'لم يتم تسجيل أي حساسات بعد'}
          </p>
        </div>
      )}

      {/* Sensors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSensors.map((sensor) => {
          const sType = sensorTypes[sensor.type];
          // Defensive formatting: guard against null/undefined/NaN values
          // that may arrive from the backend for freshly-provisioned sensors.
          const rawValue = sensor.lastReading?.value;
          const readingValue =
            typeof rawValue === 'number' && Number.isFinite(rawValue)
              ? rawValue.toFixed(2)
              : '-';
          const readingUnit = sensor.lastReading?.unit ?? sensor.unit ?? '';
          const readingTime = sensor.lastReading?.timestamp ?? sensor.updatedAt;
          const batteryLevel = sensor.battery ?? 0;

          return (
            <div
              key={sensor.id}
              className={`bg-white rounded-lg border p-4 hover:shadow-md transition-shadow ${
                sensor.status === 'offline' || sensor.status === 'inactive' ? 'border-red-200' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      sensor.status === 'online' || sensor.status === 'active'
                        ? 'bg-green-100 text-green-600'
                        : sensor.status === 'offline' || sensor.status === 'inactive'
                          ? 'bg-red-100 text-red-600'
                          : 'bg-yellow-100 text-yellow-600'
                    }`}
                  >
                    {sType?.icon ?? <Radio className="w-5 h-5" />}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{sensor.nameAr}</h3>
                    <p className="text-sm text-gray-500">
                      {sensor.location?.fieldName ?? sensor.name}
                    </p>
                  </div>
                </div>
                {getStatusIcon(sensor.status)}
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">القراءة الأخيرة</span>
                  <span className="text-lg font-bold text-gray-900">
                    {readingValue}
                    {readingUnit ? ` ${readingUnit}` : ''}
                  </span>
                </div>
                {sensor.battery != null && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">البطارية</span>
                    <span className={`text-sm font-medium ${getBatteryColor(batteryLevel)}`}>
                      {batteryLevel}%
                    </span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">الحالة</span>
                  {getStatusBadge(sensor.status)}
                </div>
              </div>

              <div className="mt-4 pt-4 border-t flex justify-between items-center">
                <span className="text-xs text-gray-400">
                  آخر تحديث: {readingTime ? new Date(readingTime).toLocaleTimeString('ar-SA') : '-'}
                </span>
                <button
                  onClick={() => setSelectedSensorId(sensor.id)}
                  className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                >
                  التفاصيل
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Sensor Detail Modal */}
      {selectedSensorId && sensorDetail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative">
            <button onClick={() => setSelectedSensorId(null)} className="absolute top-3 left-3 text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-bold text-gray-900 mb-1">تفاصيل الحساس</h2>
            <p className="text-sm text-gray-500 mb-4">Sensor Details</p>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-sm text-gray-500">الاسم</span>
                <span className="text-sm font-medium text-gray-900">{sensorDetail.nameAr}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-sm text-gray-500">النوع</span>
                <span className="text-sm font-medium text-gray-900">{sensorTypes[sensorDetail.type]?.labelAr ?? sensorDetail.type}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-sm text-gray-500">الحالة</span>
                {getStatusBadge(sensorDetail.status)}
              </div>
              {sensorDetail.location && (
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-sm text-gray-500">الموقع</span>
                  <span className="text-sm font-medium text-gray-900">{sensorDetail.location.fieldName ?? `${sensorDetail.location.latitude}, ${sensorDetail.location.longitude}`}</span>
                </div>
              )}
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-sm text-gray-500">القراءة الأخيرة</span>
                <span className="text-sm font-bold text-gray-900">
                  {typeof sensorDetail.lastReading?.value === 'number' &&
                  Number.isFinite(sensorDetail.lastReading.value)
                    ? sensorDetail.lastReading.value.toFixed(2)
                    : '-'}{' '}
                  {sensorDetail.lastReading?.unit ?? sensorDetail.unit ?? ''}
                </span>
              </div>
              {sensorDetail.battery != null && (
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-sm text-gray-500">مستوى البطارية</span>
                  <span className={`text-sm font-medium ${getBatteryColor(sensorDetail.battery)}`}>{sensorDetail.battery}%</span>
                </div>
              )}
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-sm text-gray-500">تاريخ التركيب</span>
                <span className="text-sm font-medium text-gray-900">{new Date(sensorDetail.createdAt).toLocaleDateString('ar-SA')}</span>
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <button onClick={() => setSelectedSensorId(null)} className="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50">إغلاق</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
