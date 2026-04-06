'use client';

import React, { useState, useMemo } from 'react';
import {
  Cpu,
  Search,
  Wifi,
  WifiOff,
  HardDrive,
  Thermometer,
  Upload,
  AlertTriangle,
  Activity,
  Server,
  Loader2,
} from 'lucide-react';
import { useEdgeDevices } from '../hooks/useEdgeDevices';
import type { EdgeDevice, EdgeFilters } from '../types';

type DeviceStatus = EdgeDevice['status'];

const modelLabels: Record<string, { label: string; labelAr: string }> = {
  jetson_orin: { label: 'Jetson Orin', labelAr: 'جيتسون أورين' },
  jetson_orin_nano: { label: 'Jetson Orin Nano', labelAr: 'جيتسون أورين نانو' },
  jetson_orin_nx: { label: 'Jetson Orin NX', labelAr: 'جيتسون أورين NX' },
  jetson_agx_orin: { label: 'Jetson AGX Orin', labelAr: 'جيتسون AGX أورين' },
  jetson_nano: { label: 'Jetson Nano', labelAr: 'جيتسون نانو' },
  raspberry_pi: { label: 'Raspberry Pi', labelAr: 'راسبيري باي' },
  custom: { label: 'Custom', labelAr: 'مخصص' },
};

export default function EdgeDevicesClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<DeviceStatus | 'all'>('all');

  // Build API filters
  const apiFilters: EdgeFilters | undefined = useMemo(() => {
    const filters: EdgeFilters = {};
    if (statusFilter !== 'all') filters.status = statusFilter;
    return Object.keys(filters).length > 0 ? filters : undefined;
  }, [statusFilter]);

  const { data: devices = [], isLoading, isError, error } = useEdgeDevices(apiFilters);

  // Client-side search filtering
  const filteredDevices = useMemo(() => {
    if (!searchTerm) return devices;
    return devices.filter((device) => {
      const matchesSearch =
        device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.nameAr.includes(searchTerm);
      return matchesSearch;
    });
  }, [devices, searchTerm]);

  const getStatusBadge = (status: DeviceStatus) => {
    const styles: Record<DeviceStatus, string> = {
      online: 'bg-green-100 text-green-800',
      offline: 'bg-red-100 text-red-800',
      syncing: 'bg-blue-100 text-blue-800',
      error: 'bg-orange-100 text-orange-800',
    };
    const labels: Record<DeviceStatus, string> = {
      online: 'متصل',
      offline: 'غير متصل',
      syncing: 'جاري المزامنة',
      error: 'خطأ',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] ?? 'bg-gray-100 text-gray-800'}`}>
        {labels[status] ?? status}
      </span>
    );
  };

  const getUsageColor = (value: number) => {
    if (value > 85) return 'bg-red-500';
    if (value > 60) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const onlineCount = devices.filter((d) => d.status === 'online').length;
  const errorCount = devices.filter((d) => d.status === 'error').length;
  const totalModels = devices.reduce((sum, d) => sum + (d.models?.length ?? 0), 0);

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-600 font-medium">جاري تحميل بيانات الأجهزة الطرفية...</p>
          <p className="text-sm text-gray-400 mt-1">Loading edge devices data...</p>
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
            فشل في تحميل بيانات الأجهزة الطرفية
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            {error instanceof Error ? error.message : 'Failed to load edge devices data'}
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
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">أجهزة الحوسبة الطرفية</h1>
          <p className="text-gray-500 mt-1">Edge Computing Devices</p>
        </div>
        <button
          disabled
          title="قريبا - Coming soon"
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Upload className="w-4 h-4" />
          نشر نموذج
        </button>
      </div>

      {/* Alerts */}
      {errorCount > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <span className="font-medium text-orange-800">
              تنبيه: {errorCount} جهاز يواجه أخطاء ويحتاج تدخل فوري
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Server className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الأجهزة</div>
              <div className="text-xl font-bold text-gray-900">{devices.length}</div>
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
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Cpu className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">نماذج منشورة</div>
              <div className="text-xl font-bold text-purple-600">{totalModels}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">أخطاء</div>
              <div className="text-xl font-bold text-orange-600">{errorCount}</div>
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
            placeholder="بحث عن جهاز..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as DeviceStatus | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع الحالات</option>
          <option value="online">متصل</option>
          <option value="offline">غير متصل</option>
          <option value="syncing">جاري المزامنة</option>
          <option value="error">خطأ</option>
        </select>
      </div>

      {/* Empty state */}
      {filteredDevices.length === 0 && (
        <div className="bg-white rounded-lg border p-8 text-center">
          <Server className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد أجهزة</h3>
          <p className="text-gray-500 text-sm">
            {searchTerm || statusFilter !== 'all'
              ? 'لا توجد نتائج تطابق معايير البحث'
              : 'لم يتم تسجيل أي أجهزة طرفية بعد'}
          </p>
        </div>
      )}

      {/* Devices Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredDevices.map((device) => {
          const typeLabel = modelLabels[device.type] ?? { label: device.type, labelAr: device.type };

          return (
            <div
              key={device.id}
              className={`bg-white rounded-lg border p-5 hover:shadow-md transition-shadow ${
                device.status === 'error' ? 'border-orange-300' : device.status === 'offline' ? 'border-red-200' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    device.status === 'online' ? 'bg-green-100 text-green-600' :
                    device.status === 'error' ? 'bg-orange-100 text-orange-600' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    <HardDrive className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{device.nameAr}</h3>
                    <p className="text-sm text-gray-500">{typeLabel.labelAr}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(device.status)}
                  {device.status === 'online' ? (
                    <Wifi className="w-4 h-4 text-green-500" />
                  ) : device.status === 'offline' ? (
                    <WifiOff className="w-4 h-4 text-red-500" />
                  ) : null}
                </div>
              </div>

              {device.status !== 'offline' && (
                <div className="space-y-3 mb-4">
                  {[
                    { label: 'المعالج', value: device.cpuUsage },
                    ...(device.gpuUsage != null ? [{ label: 'GPU', value: device.gpuUsage }] : []),
                    { label: 'الذاكرة', value: device.memoryUsage },
                  ].map((metric) => (
                    <div key={metric.label}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-500">{metric.label}</span>
                        <span className="font-medium">{metric.value}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${getUsageColor(metric.value)}`}
                          style={{ width: `${metric.value}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between text-sm mb-3">
                <div className="flex items-center gap-1 text-gray-500">
                  <Thermometer className="w-4 h-4" />
                  <span>{device.diskUsage}% قرص</span>
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                  <Activity className="w-4 h-4" />
                  <span>{device.location?.fieldName ?? '-'}</span>
                </div>
              </div>

              {device.models.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {device.models.map((model) => (
                    <span key={model} className="px-2 py-0.5 bg-purple-50 text-purple-700 rounded text-xs">
                      {model}
                    </span>
                  ))}
                </div>
              )}

              <div className="pt-3 border-t flex justify-between items-center">
                <span className="text-xs text-gray-400">
                  آخر ظهور: {new Date(device.lastSeen).toLocaleTimeString('ar-SA')}
                </span>
                <button
                  disabled
                  title="قريبا - Coming soon"
                  className="text-green-600 hover:text-green-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  التفاصيل
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
