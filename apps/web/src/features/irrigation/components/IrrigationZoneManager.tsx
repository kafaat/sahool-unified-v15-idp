'use client';

import React, { useState } from 'react';
import {
  Droplets,
  MapPin,
  Clock,
  Play,
  Pause,
  Settings,
  AlertCircle,
  Check,
  RefreshCw,
  TrendingUp,
} from 'lucide-react';

// ==================== TypeScript Interfaces ====================

export interface ZoneSensor {
  id: string;
  type: 'soil_moisture' | 'temperature' | 'humidity';
  value: number;
  unit: string;
  lastUpdate: Date;
  status: 'normal' | 'warning' | 'critical';
}

export interface ZoneSchedule {
  id: string;
  enabled: boolean;
  startTime: string;
  duration: number; // minutes
  frequency: 'daily' | 'weekly' | 'custom';
  daysOfWeek?: number[]; // 0-6 (Sunday-Saturday)
  nextRun?: Date;
}

export interface IrrigationZone {
  id: string;
  name: string;
  nameAr: string;
  location: string;
  locationAr: string;
  area: number; // hectares
  status: 'optimal' | 'dry' | 'wet' | 'alert' | 'irrigating';
  sensors: ZoneSensor[];
  schedule: ZoneSchedule;
  metrics: {
    waterUsage: number; // liters
    efficiency: number; // percentage
    lastIrrigation: Date;
    cropType: string;
    cropTypeAr: string;
  };
  isActive: boolean;
}

// ==================== Mock Data ====================

const generateMockZones = (): IrrigationZone[] => [
  {
    id: 'zone-1',
    name: 'North Field - Wheat',
    nameAr: 'الحقل الشمالي - قمح',
    location: 'Sector A1',
    locationAr: 'القطاع أ1',
    area: 5.2,
    status: 'optimal',
    sensors: [
      {
        id: 'sensor-1-1',
        type: 'soil_moisture',
        value: 65,
        unit: '%',
        lastUpdate: new Date(Date.now() - 15 * 60000),
        status: 'normal',
      },
      {
        id: 'sensor-1-2',
        type: 'temperature',
        value: 28,
        unit: '°C',
        lastUpdate: new Date(Date.now() - 15 * 60000),
        status: 'normal',
      },
    ],
    schedule: {
      id: 'schedule-1',
      enabled: true,
      startTime: '06:00',
      duration: 45,
      frequency: 'daily',
      nextRun: new Date(Date.now() + 18 * 3600000),
    },
    metrics: {
      waterUsage: 12500,
      efficiency: 87,
      lastIrrigation: new Date(Date.now() - 24 * 3600000),
      cropType: 'Wheat',
      cropTypeAr: 'قمح',
    },
    isActive: false,
  },
  {
    id: 'zone-2',
    name: 'South Field - Tomatoes',
    nameAr: 'الحقل الجنوبي - طماطم',
    location: 'Sector B2',
    locationAr: 'القطاع ب2',
    area: 3.8,
    status: 'dry',
    sensors: [
      {
        id: 'sensor-2-1',
        type: 'soil_moisture',
        value: 35,
        unit: '%',
        lastUpdate: new Date(Date.now() - 10 * 60000),
        status: 'warning',
      },
      {
        id: 'sensor-2-2',
        type: 'temperature',
        value: 32,
        unit: '°C',
        lastUpdate: new Date(Date.now() - 10 * 60000),
        status: 'warning',
      },
    ],
    schedule: {
      id: 'schedule-2',
      enabled: true,
      startTime: '05:30',
      duration: 60,
      frequency: 'daily',
      nextRun: new Date(Date.now() + 12 * 3600000),
    },
    metrics: {
      waterUsage: 18200,
      efficiency: 82,
      lastIrrigation: new Date(Date.now() - 36 * 3600000),
      cropType: 'Tomatoes',
      cropTypeAr: 'طماطم',
    },
    isActive: false,
  },
  {
    id: 'zone-3',
    name: 'East Field - Corn',
    nameAr: 'الحقل الشرقي - ذرة',
    location: 'Sector C3',
    locationAr: 'القطاع ج3',
    area: 6.5,
    status: 'irrigating',
    sensors: [
      {
        id: 'sensor-3-1',
        type: 'soil_moisture',
        value: 48,
        unit: '%',
        lastUpdate: new Date(Date.now() - 5 * 60000),
        status: 'normal',
      },
      {
        id: 'sensor-3-2',
        type: 'temperature',
        value: 29,
        unit: '°C',
        lastUpdate: new Date(Date.now() - 5 * 60000),
        status: 'normal',
      },
    ],
    schedule: {
      id: 'schedule-3',
      enabled: true,
      startTime: '04:00',
      duration: 90,
      frequency: 'daily',
      nextRun: new Date(Date.now() + 22 * 3600000),
    },
    metrics: {
      waterUsage: 24800,
      efficiency: 91,
      lastIrrigation: new Date(Date.now() - 1 * 3600000),
      cropType: 'Corn',
      cropTypeAr: 'ذرة',
    },
    isActive: true,
  },
  {
    id: 'zone-4',
    name: 'West Field - Vegetables',
    nameAr: 'الحقل الغربي - خضروات',
    location: 'Sector D4',
    locationAr: 'القطاع د4',
    area: 4.1,
    status: 'alert',
    sensors: [
      {
        id: 'sensor-4-1',
        type: 'soil_moisture',
        value: 22,
        unit: '%',
        lastUpdate: new Date(Date.now() - 20 * 60000),
        status: 'critical',
      },
      {
        id: 'sensor-4-2',
        type: 'temperature',
        value: 35,
        unit: '°C',
        lastUpdate: new Date(Date.now() - 20 * 60000),
        status: 'critical',
      },
    ],
    schedule: {
      id: 'schedule-4',
      enabled: false,
      startTime: '06:30',
      duration: 50,
      frequency: 'daily',
      nextRun: undefined,
    },
    metrics: {
      waterUsage: 15600,
      efficiency: 75,
      lastIrrigation: new Date(Date.now() - 48 * 3600000),
      cropType: 'Mixed Vegetables',
      cropTypeAr: 'خضروات متنوعة',
    },
    isActive: false,
  },
];

// ==================== Helper Functions ====================

const getStatusColor = (status: IrrigationZone['status']) => {
  switch (status) {
    case 'optimal':
      return 'bg-green-100 border-green-500 text-green-800';
    case 'dry':
      return 'bg-orange-100 border-orange-500 text-orange-800';
    case 'wet':
      return 'bg-blue-100 border-blue-500 text-blue-800';
    case 'alert':
      return 'bg-red-100 border-red-500 text-red-800';
    case 'irrigating':
      return 'bg-cyan-100 border-cyan-500 text-cyan-800';
    default:
      return 'bg-gray-100 border-gray-500 text-gray-800';
  }
};

const getStatusBadgeColor = (status: IrrigationZone['status']) => {
  switch (status) {
    case 'optimal':
      return 'bg-green-500 text-white';
    case 'dry':
      return 'bg-orange-500 text-white';
    case 'wet':
      return 'bg-blue-500 text-white';
    case 'alert':
      return 'bg-red-500 text-white';
    case 'irrigating':
      return 'bg-cyan-500 text-white animate-pulse';
    default:
      return 'bg-gray-500 text-white';
  }
};

const getStatusLabel = (status: IrrigationZone['status']) => {
  switch (status) {
    case 'optimal':
      return { en: 'Optimal', ar: 'مثالي' };
    case 'dry':
      return { en: 'Dry', ar: 'جاف' };
    case 'wet':
      return { en: 'Wet', ar: 'رطب' };
    case 'alert':
      return { en: 'Alert', ar: 'تنبيه' };
    case 'irrigating':
      return { en: 'Irrigating', ar: 'يروي' };
    default:
      return { en: 'Unknown', ar: 'غير معروف' };
  }
};

const getSensorStatusColor = (status: ZoneSensor['status']) => {
  switch (status) {
    case 'normal':
      return 'text-green-600';
    case 'warning':
      return 'text-orange-600';
    case 'critical':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

const formatRelativeTime = (date: Date): string => {
  const diff = Date.now() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
};

// ==================== Main Component ====================

export const IrrigationZoneManager: React.FC = () => {
  const [zones, setZones] = useState<IrrigationZone[]>(generateMockZones());
  const [loadingZones, setLoadingZones] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<'en' | 'ar'>('en');

  // ==================== Handlers ====================

  const handleStartIrrigation = async (zoneId: string) => {
    try {
      setLoadingZones((prev) => new Set(prev).add(zoneId));
      setError(null);

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500));

      setZones((prevZones) =>
        prevZones.map((zone) =>
          zone.id === zoneId
            ? { ...zone, status: 'irrigating', isActive: true }
            : zone
        )
      );
    } catch (err) {
      setError(`Failed to start irrigation for zone ${zoneId}`);
      console.error('Start irrigation error:', err);
    } finally {
      setLoadingZones((prev) => {
        const newSet = new Set(prev);
        newSet.delete(zoneId);
        return newSet;
      });
    }
  };

  const handleStopIrrigation = async (zoneId: string) => {
    try {
      setLoadingZones((prev) => new Set(prev).add(zoneId));
      setError(null);

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500));

      setZones((prevZones) =>
        prevZones.map((zone) =>
          zone.id === zoneId
            ? { ...zone, status: 'optimal', isActive: false }
            : zone
        )
      );
    } catch (err) {
      setError(`Failed to stop irrigation for zone ${zoneId}`);
      console.error('Stop irrigation error:', err);
    } finally {
      setLoadingZones((prev) => {
        const newSet = new Set(prev);
        newSet.delete(zoneId);
        return newSet;
      });
    }
  };

  const handleRefreshZone = async (zoneId: string) => {
    try {
      setLoadingZones((prev) => new Set(prev).add(zoneId));
      setError(null);

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setZones((prevZones) =>
        prevZones.map((zone) =>
          zone.id === zoneId
            ? {
                ...zone,
                sensors: zone.sensors.map((sensor) => ({
                  ...sensor,
                  lastUpdate: new Date(),
                  value:
                    sensor.type === 'soil_moisture'
                      ? Math.floor(Math.random() * 40) + 40
                      : Math.floor(Math.random() * 10) + 25,
                })),
              }
            : zone
        )
      );
    } catch (err) {
      setError(`Failed to refresh zone ${zoneId}`);
      console.error('Refresh zone error:', err);
    } finally {
      setLoadingZones((prev) => {
        const newSet = new Set(prev);
        newSet.delete(zoneId);
        return newSet;
      });
    }
  };

  const handleToggleSchedule = async (zoneId: string) => {
    try {
      setLoadingZones((prev) => new Set(prev).add(zoneId));
      setError(null);

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 800));

      setZones((prevZones) =>
        prevZones.map((zone) =>
          zone.id === zoneId
            ? {
                ...zone,
                schedule: {
                  ...zone.schedule,
                  enabled: !zone.schedule.enabled,
                  nextRun: !zone.schedule.enabled
                    ? new Date(Date.now() + 12 * 3600000)
                    : undefined,
                },
              }
            : zone
        )
      );
    } catch (err) {
      setError(`Failed to toggle schedule for zone ${zoneId}`);
      console.error('Toggle schedule error:', err);
    } finally {
      setLoadingZones((prev) => {
        const newSet = new Set(prev);
        newSet.delete(zoneId);
        return newSet;
      });
    }
  };

  // ==================== Render Zone Card ====================

  const renderZoneCard = (zone: IrrigationZone) => {
    const isLoading = loadingZones.has(zone.id);
    const statusLabel = getStatusLabel(zone.status);
    const moistureSensor = zone.sensors.find((s) => s.type === 'soil_moisture');
    const tempSensor = zone.sensors.find((s) => s.type === 'temperature');

    return (
      <div
        key={zone.id}
        className={`border-l-4 rounded-lg shadow-lg p-6 transition-all hover:shadow-xl ${getStatusColor(
          zone.status
        )}`}
        dir={language === 'ar' ? 'rtl' : 'ltr'}
      >
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-1">
              {language === 'en' ? zone.name : zone.nameAr}
            </h3>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <MapPin className="w-4 h-4" />
              <span>{language === 'en' ? zone.location : zone.locationAr}</span>
              <span className="mx-2">•</span>
              <span>
                {zone.area} {language === 'en' ? 'ha' : 'هكتار'}
              </span>
            </div>
          </div>
          <div
            className={`px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1 ${getStatusBadgeColor(
              zone.status
            )}`}
          >
            {zone.status === 'irrigating' && <Droplets className="w-4 h-4" />}
            {zone.status === 'alert' && <AlertCircle className="w-4 h-4" />}
            {zone.status === 'optimal' && <Check className="w-4 h-4" />}
            {language === 'en' ? statusLabel.en : statusLabel.ar}
          </div>
        </div>

        {/* Sensor Readings */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          {moistureSensor && (
            <div className="bg-white rounded-lg p-3 shadow-sm">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">
                  {language === 'en' ? 'Soil Moisture' : 'رطوبة التربة'}
                </span>
                <Droplets className={`w-4 h-4 ${getSensorStatusColor(moistureSensor.status)}`} />
              </div>
              <div className="text-2xl font-bold">
                {moistureSensor.value}
                <span className="text-sm ml-1">{moistureSensor.unit}</span>
              </div>
              <div className="text-xs text-gray-400">
                {formatRelativeTime(moistureSensor.lastUpdate)}
              </div>
            </div>
          )}

          {tempSensor && (
            <div className="bg-white rounded-lg p-3 shadow-sm">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">
                  {language === 'en' ? 'Temperature' : 'درجة الحرارة'}
                </span>
                <TrendingUp className={`w-4 h-4 ${getSensorStatusColor(tempSensor.status)}`} />
              </div>
              <div className="text-2xl font-bold">
                {tempSensor.value}
                <span className="text-sm ml-1">{tempSensor.unit}</span>
              </div>
              <div className="text-xs text-gray-400">
                {formatRelativeTime(tempSensor.lastUpdate)}
              </div>
            </div>
          )}
        </div>

        {/* Metrics */}
        <div className="bg-white rounded-lg p-4 mb-4 shadow-sm">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <div className="text-xs text-gray-500 mb-1">
                {language === 'en' ? 'Water Usage' : 'استهلاك الماء'}
              </div>
              <div className="text-lg font-semibold">
                {(zone.metrics.waterUsage / 1000).toFixed(1)}
                <span className="text-xs ml-1">{language === 'en' ? 'k L' : 'ك ل'}</span>
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">
                {language === 'en' ? 'Efficiency' : 'الكفاءة'}
              </div>
              <div className="text-lg font-semibold">
                {zone.metrics.efficiency}
                <span className="text-xs ml-1">%</span>
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">
                {language === 'en' ? 'Last Irrigation' : 'آخر ري'}
              </div>
              <div className="text-lg font-semibold">
                {formatRelativeTime(zone.metrics.lastIrrigation)}
              </div>
            </div>
          </div>
        </div>

        {/* Schedule Info */}
        <div className="bg-white rounded-lg p-3 mb-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium">
                {language === 'en' ? 'Schedule' : 'الجدول الزمني'}
              </span>
            </div>
            <div className="text-sm">
              {zone.schedule.enabled ? (
                <span className="text-green-600 font-medium">
                  {zone.schedule.startTime} ({zone.schedule.duration}{' '}
                  {language === 'en' ? 'min' : 'دقيقة'})
                </span>
              ) : (
                <span className="text-gray-400">
                  {language === 'en' ? 'Disabled' : 'معطل'}
                </span>
              )}
            </div>
          </div>
          {zone.schedule.enabled && zone.schedule.nextRun && (
            <div className="text-xs text-gray-500 mt-1">
              {language === 'en' ? 'Next run: ' : 'المرة القادمة: '}
              {zone.schedule.nextRun.toLocaleString()}
            </div>
          )}
        </div>

        {/* Control Buttons */}
        <div className="grid grid-cols-2 gap-2">
          {!zone.isActive ? (
            <button
              onClick={() => handleStartIrrigation(zone.id)}
              disabled={isLoading}
              className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              {isLoading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {language === 'en' ? 'Start' : 'بدء'}
            </button>
          ) : (
            <button
              onClick={() => handleStopIrrigation(zone.id)}
              disabled={isLoading}
              className="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              {isLoading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Pause className="w-4 h-4" />
              )}
              {language === 'en' ? 'Stop' : 'إيقاف'}
            </button>
          )}

          <button
            onClick={() => handleToggleSchedule(zone.id)}
            disabled={isLoading}
            className={`flex items-center justify-center gap-2 ${
              zone.schedule.enabled
                ? 'bg-blue-600 hover:bg-blue-700'
                : 'bg-gray-600 hover:bg-gray-700'
            } disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors`}
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Clock className="w-4 h-4" />
            )}
            {zone.schedule.enabled
              ? language === 'en'
                ? 'Scheduled'
                : 'مجدول'
              : language === 'en'
              ? 'Schedule'
              : 'جدولة'}
          </button>

          <button
            onClick={() => handleRefreshZone(zone.id)}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            {language === 'en' ? 'Refresh' : 'تحديث'}
          </button>

          <button
            disabled={isLoading}
            className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Settings className="w-4 h-4" />
            )}
            {language === 'en' ? 'Settings' : 'إعدادات'}
          </button>
        </div>
      </div>
    );
  };

  // ==================== Main Render ====================

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {language === 'en' ? 'Irrigation Zone Management' : 'إدارة مناطق الري'}
              </h1>
              <p className="text-gray-600">
                {language === 'en'
                  ? 'Monitor and control irrigation zones across your farm'
                  : 'مراقبة والتحكم في مناطق الري في مزرعتك'}
              </p>
            </div>
            <button
              onClick={() => setLanguage(language === 'en' ? 'ar' : 'en')}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              {language === 'en' ? 'العربية' : 'English'}
            </button>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500 mb-1">
                {language === 'en' ? 'Total Zones' : 'إجمالي المناطق'}
              </div>
              <div className="text-2xl font-bold">{zones.length}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500 mb-1">
                {language === 'en' ? 'Active' : 'نشط'}
              </div>
              <div className="text-2xl font-bold text-cyan-600">
                {zones.filter((z) => z.isActive).length}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500 mb-1">
                {language === 'en' ? 'Alerts' : 'تنبيهات'}
              </div>
              <div className="text-2xl font-bold text-red-600">
                {zones.filter((z) => z.status === 'alert').length}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500 mb-1">
                {language === 'en' ? 'Avg Efficiency' : 'متوسط الكفاءة'}
              </div>
              <div className="text-2xl font-bold text-green-600">
                {Math.round(zones.reduce((acc, z) => acc + z.metrics.efficiency, 0) / zones.length)}%
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-700 hover:text-red-900"
            >
              ×
            </button>
          </div>
        )}

        {/* Zone Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {zones.map((zone) => renderZoneCard(zone))}
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-gray-500">
          {language === 'en'
            ? 'Last updated: ' + new Date().toLocaleString()
            : 'آخر تحديث: ' + new Date().toLocaleString('ar-YE')}
        </div>
      </div>
    </div>
  );
};

export default IrrigationZoneManager;
