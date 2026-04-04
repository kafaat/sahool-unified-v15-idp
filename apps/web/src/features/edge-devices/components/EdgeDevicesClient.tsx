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
} from 'lucide-react';

type DeviceStatus = 'online' | 'offline' | 'deploying' | 'error';
type DeviceModel = 'jetson_orin_nano' | 'jetson_orin_nx' | 'jetson_agx_orin' | 'raspberry_pi';

interface EdgeDevice {
  id: string;
  name: string;
  nameAr: string;
  model: DeviceModel;
  fieldId: string;
  fieldName: string;
  status: DeviceStatus;
  cpuUsage: number;
  gpuUsage: number;
  memoryUsage: number;
  temperature: number;
  deployedModels: string[];
  lastSync: string;
  uptime: string;
}

const mockDevices: EdgeDevice[] = [
  {
    id: 'edge-001',
    name: 'Orin NX - North Field',
    nameAr: 'أورين NX - الحقل الشمالي',
    model: 'jetson_orin_nx',
    fieldId: 'field-1',
    fieldName: 'الحقل الشمالي',
    status: 'online',
    cpuUsage: 45,
    gpuUsage: 72,
    memoryUsage: 68,
    temperature: 52,
    deployedModels: ['yolo26-pest-v3', 'crop-disease-v2'],
    lastSync: '2026-04-04T08:15:00Z',
    uptime: '14d 6h',
  },
  {
    id: 'edge-002',
    name: 'AGX Orin - Palm Grove',
    nameAr: 'AGX أورين - بستان النخيل',
    model: 'jetson_agx_orin',
    fieldId: 'field-4',
    fieldName: 'بستان النخيل',
    status: 'deploying',
    cpuUsage: 88,
    gpuUsage: 95,
    memoryUsage: 82,
    temperature: 67,
    deployedModels: ['rpw-detection-v4'],
    lastSync: '2026-04-04T08:10:00Z',
    uptime: '3d 12h',
  },
  {
    id: 'edge-003',
    name: 'Orin Nano - Greenhouse',
    nameAr: 'أورين نانو - الصوب الزراعية',
    model: 'jetson_orin_nano',
    fieldId: 'field-5',
    fieldName: 'الصوب الزراعية',
    status: 'online',
    cpuUsage: 32,
    gpuUsage: 41,
    memoryUsage: 55,
    temperature: 44,
    deployedModels: ['tomato-ripeness-v1'],
    lastSync: '2026-04-04T08:14:00Z',
    uptime: '28d 2h',
  },
  {
    id: 'edge-004',
    name: 'RPi 5 - Weather Station',
    nameAr: 'راسبيري باي 5 - محطة الطقس',
    model: 'raspberry_pi',
    fieldId: 'field-2',
    fieldName: 'الحقل الجنوبي',
    status: 'offline',
    cpuUsage: 0,
    gpuUsage: 0,
    memoryUsage: 0,
    temperature: 0,
    deployedModels: [],
    lastSync: '2026-04-03T22:30:00Z',
    uptime: '0h',
  },
  {
    id: 'edge-005',
    name: 'Orin NX - Wheat Field',
    nameAr: 'أورين NX - حقل القمح',
    model: 'jetson_orin_nx',
    fieldId: 'field-3',
    fieldName: 'حقل القمح',
    status: 'error',
    cpuUsage: 12,
    gpuUsage: 0,
    memoryUsage: 91,
    temperature: 78,
    deployedModels: ['weed-detect-v2', 'wheat-rust-v1'],
    lastSync: '2026-04-04T07:45:00Z',
    uptime: '1d 8h',
  },
];

const modelLabels: Record<DeviceModel, { label: string; labelAr: string }> = {
  jetson_orin_nano: { label: 'Jetson Orin Nano', labelAr: 'جيتسون أورين نانو' },
  jetson_orin_nx: { label: 'Jetson Orin NX', labelAr: 'جيتسون أورين NX' },
  jetson_agx_orin: { label: 'Jetson AGX Orin', labelAr: 'جيتسون AGX أورين' },
  raspberry_pi: { label: 'Raspberry Pi', labelAr: 'راسبيري باي' },
};

export default function EdgeDevicesClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<DeviceStatus | 'all'>('all');

  const filteredDevices = useMemo(() => {
    return mockDevices.filter((device) => {
      const matchesSearch =
        !searchTerm ||
        device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.nameAr.includes(searchTerm);
      const matchesStatus = statusFilter === 'all' || device.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [searchTerm, statusFilter]);

  const getStatusBadge = (status: DeviceStatus) => {
    const styles: Record<DeviceStatus, string> = {
      online: 'bg-green-100 text-green-800',
      offline: 'bg-red-100 text-red-800',
      deploying: 'bg-blue-100 text-blue-800',
      error: 'bg-orange-100 text-orange-800',
    };
    const labels: Record<DeviceStatus, string> = {
      online: 'متصل',
      offline: 'غير متصل',
      deploying: 'جاري النشر',
      error: 'خطأ',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const getUsageColor = (value: number) => {
    if (value > 85) return 'bg-red-500';
    if (value > 60) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const onlineCount = mockDevices.filter((d) => d.status === 'online').length;
  const errorCount = mockDevices.filter((d) => d.status === 'error').length;
  const totalModels = mockDevices.reduce((sum, d) => sum + d.deployedModels.length, 0);

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
              <div className="text-xl font-bold text-gray-900">{mockDevices.length}</div>
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
          <option value="deploying">جاري النشر</option>
          <option value="error">خطأ</option>
        </select>
      </div>

      {/* Devices Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredDevices.map((device) => (
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
                  <p className="text-sm text-gray-500">{modelLabels[device.model].labelAr}</p>
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
                  { label: 'GPU', value: device.gpuUsage },
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
                <span>{device.temperature}°C</span>
              </div>
              <div className="flex items-center gap-1 text-gray-500">
                <Activity className="w-4 h-4" />
                <span>{device.uptime}</span>
              </div>
            </div>

            {device.deployedModels.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {device.deployedModels.map((model) => (
                  <span key={model} className="px-2 py-0.5 bg-purple-50 text-purple-700 rounded text-xs">
                    {model}
                  </span>
                ))}
              </div>
            )}

            <div className="pt-3 border-t flex justify-between items-center">
              <span className="text-xs text-gray-400">
                آخر مزامنة: {new Date(device.lastSync).toLocaleTimeString('ar-SA')}
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
        ))}
      </div>
    </div>
  );
}
