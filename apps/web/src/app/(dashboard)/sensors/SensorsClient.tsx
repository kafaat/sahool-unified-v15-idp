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
} from 'lucide-react';

type SensorType = 'soil_moisture' | 'temperature' | 'humidity' | 'wind' | 'rain' | 'ndvi';
type SensorStatus = 'online' | 'offline' | 'warning' | 'maintenance';

interface Sensor {
  id: string;
  name: string;
  nameAr: string;
  type: SensorType;
  fieldId: string;
  fieldName: string;
  status: SensorStatus;
  lastReading: number;
  unit: string;
  battery: number;
  lastUpdate: string;
}

const mockSensors: Sensor[] = [
  {
    id: '1',
    name: 'Soil Moisture Sensor A1',
    nameAr: 'حساس رطوبة التربة A1',
    type: 'soil_moisture',
    fieldId: 'field-1',
    fieldName: 'الحقل الشمالي',
    status: 'online',
    lastReading: 42,
    unit: '%',
    battery: 85,
    lastUpdate: '2025-01-25T09:30:00Z',
  },
  {
    id: '2',
    name: 'Temperature Sensor B2',
    nameAr: 'حساس الحرارة B2',
    type: 'temperature',
    fieldId: 'field-2',
    fieldName: 'الحقل الجنوبي',
    status: 'online',
    lastReading: 28,
    unit: '°C',
    battery: 72,
    lastUpdate: '2025-01-25T09:28:00Z',
  },
  {
    id: '3',
    name: 'Humidity Sensor C3',
    nameAr: 'حساس الرطوبة C3',
    type: 'humidity',
    fieldId: 'field-3',
    fieldName: 'حقل القمح',
    status: 'warning',
    lastReading: 65,
    unit: '%',
    battery: 15,
    lastUpdate: '2025-01-25T09:25:00Z',
  },
  {
    id: '4',
    name: 'Wind Sensor D4',
    nameAr: 'حساس الرياح D4',
    type: 'wind',
    fieldId: 'field-4',
    fieldName: 'بستان النخيل',
    status: 'offline',
    lastReading: 0,
    unit: 'km/h',
    battery: 0,
    lastUpdate: '2025-01-24T18:00:00Z',
  },
  {
    id: '5',
    name: 'Soil Moisture Sensor E5',
    nameAr: 'حساس رطوبة التربة E5',
    type: 'soil_moisture',
    fieldId: 'field-5',
    fieldName: 'الصوب الزراعية',
    status: 'online',
    lastReading: 55,
    unit: '%',
    battery: 90,
    lastUpdate: '2025-01-25T09:29:00Z',
  },
  {
    id: '6',
    name: 'Temperature Sensor F6',
    nameAr: 'حساس الحرارة F6',
    type: 'temperature',
    fieldId: 'field-1',
    fieldName: 'الحقل الشمالي',
    status: 'maintenance',
    lastReading: 25,
    unit: '°C',
    battery: 50,
    lastUpdate: '2025-01-23T12:00:00Z',
  },
];

const sensorTypes: Record<SensorType, { icon: React.ReactNode; label: string; labelAr: string }> = {
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
};

export default function SensorsClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<SensorStatus | 'all'>('all');
  const [typeFilter, setTypeFilter] = useState<SensorType | 'all'>('all');

  const filteredSensors = useMemo(() => {
    return mockSensors.filter((sensor) => {
      const matchesSearch =
        !searchTerm ||
        sensor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        sensor.nameAr.includes(searchTerm);
      const matchesStatus = statusFilter === 'all' || sensor.status === statusFilter;
      const matchesType = typeFilter === 'all' || sensor.type === typeFilter;
      return matchesSearch && matchesStatus && matchesType;
    });
  }, [searchTerm, statusFilter, typeFilter]);

  const getStatusBadge = (status: SensorStatus) => {
    const styles = {
      online: 'bg-green-100 text-green-800',
      offline: 'bg-red-100 text-red-800',
      warning: 'bg-yellow-100 text-yellow-800',
      maintenance: 'bg-blue-100 text-blue-800',
    };
    const labels = {
      online: 'متصل',
      offline: 'غير متصل',
      warning: 'تحذير',
      maintenance: 'صيانة',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const getStatusIcon = (status: SensorStatus) => {
    if (status === 'online') return <Wifi className="w-4 h-4 text-green-500" />;
    if (status === 'offline') return <WifiOff className="w-4 h-4 text-red-500" />;
    return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
  };

  const getBatteryColor = (level: number) => {
    if (level > 50) return 'text-green-600';
    if (level > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const onlineCount = mockSensors.filter((s) => s.status === 'online').length;
  const offlineCount = mockSensors.filter((s) => s.status === 'offline').length;
  const warningCount = mockSensors.filter((s) => s.status === 'warning' || s.battery < 20).length;

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
              <div className="text-xl font-bold text-gray-900">{mockSensors.length}</div>
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
              <div className="text-xl font-bold text-yellow-600">
                {mockSensors.filter((s) => s.battery < 20).length}
              </div>
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
          <option value="warning">تحذير</option>
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

      {/* Sensors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSensors.map((sensor) => (
          <div
            key={sensor.id}
            className={`bg-white rounded-lg border p-4 hover:shadow-md transition-shadow ${
              sensor.status === 'offline' ? 'border-red-200' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div
                  className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    sensor.status === 'online'
                      ? 'bg-green-100 text-green-600'
                      : sensor.status === 'offline'
                        ? 'bg-red-100 text-red-600'
                        : 'bg-yellow-100 text-yellow-600'
                  }`}
                >
                  {sensorTypes[sensor.type].icon}
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{sensor.nameAr}</h3>
                  <p className="text-sm text-gray-500">{sensor.fieldName}</p>
                </div>
              </div>
              {getStatusIcon(sensor.status)}
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">القراءة الأخيرة</span>
                <span className="text-lg font-bold text-gray-900">
                  {sensor.lastReading}
                  {sensor.unit}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">البطارية</span>
                <span className={`text-sm font-medium ${getBatteryColor(sensor.battery)}`}>
                  {sensor.battery}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">الحالة</span>
                {getStatusBadge(sensor.status)}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t flex justify-between items-center">
              <span className="text-xs text-gray-400">
                آخر تحديث: {new Date(sensor.lastUpdate).toLocaleTimeString('ar-SA')}
              </span>
              <button
                disabled
                title="قريباً - Coming soon"
                className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
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
