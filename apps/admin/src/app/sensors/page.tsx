'use client';

// Virtual Sensors Dashboard - المستشعرات الافتراضية
// AI-powered sensor predictions for Yemen farms

import { useEffect, useState } from 'react';
import Header from '@/components/layout/Header';
import { API_URLS, apiClient } from '@/lib/api';
import { cn } from '@/lib/utils';
import {
  Cpu,
  Thermometer,
  Droplets,
  Wind,
  Sun,
  Leaf,
  RefreshCw,
  MapPin,
  TrendingUp,
  TrendingDown,
  Activity,
} from 'lucide-react';

interface VirtualSensor {
  id: string;
  type: 'temperature' | 'humidity' | 'soil_moisture' | 'wind_speed' | 'solar_radiation' | 'ndvi';
  name: string;
  nameAr: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  confidence: number;
  lastUpdated: string;
  status: 'normal' | 'warning' | 'critical';
}

interface FarmSensors {
  farmId: string;
  farmName: string;
  governorate: string;
  sensors: VirtualSensor[];
}

const SENSOR_ICONS = {
  temperature: Thermometer,
  humidity: Droplets,
  soil_moisture: Droplets,
  wind_speed: Wind,
  solar_radiation: Sun,
  ndvi: Leaf,
};

const SENSOR_COLORS = {
  temperature: 'text-red-500 bg-red-50',
  humidity: 'text-blue-500 bg-blue-50',
  soil_moisture: 'text-cyan-500 bg-cyan-50',
  wind_speed: 'text-gray-500 bg-gray-50',
  solar_radiation: 'text-yellow-500 bg-yellow-50',
  ndvi: 'text-green-500 bg-green-50',
};

// Mock data generator
function generateMockSensors(): FarmSensors[] {
  const farms = [
    { id: 'farm-1', name: 'مزرعة الخير', governorate: 'صنعاء' },
    { id: 'farm-2', name: 'مزرعة البركة', governorate: 'تعز' },
    { id: 'farm-3', name: 'مزرعة السعادة', governorate: 'إب' },
    { id: 'farm-4', name: 'مزرعة الأمل', governorate: 'حضرموت' },
    { id: 'farm-5', name: 'مزرعة النور', governorate: 'الحديدة' },
  ];

  return farms.map(farm => ({
    farmId: farm.id,
    farmName: farm.name,
    governorate: farm.governorate,
    sensors: [
      {
        id: `${farm.id}-temp`,
        type: 'temperature',
        name: 'Temperature',
        nameAr: 'درجة الحرارة',
        value: Math.round(25 + Math.random() * 15),
        unit: '°C',
        trend: Math.random() > 0.5 ? 'up' : 'down',
        confidence: 85 + Math.random() * 10,
        lastUpdated: new Date().toISOString(),
        status: Math.random() > 0.8 ? 'warning' : 'normal',
      },
      {
        id: `${farm.id}-humidity`,
        type: 'humidity',
        name: 'Humidity',
        nameAr: 'الرطوبة',
        value: Math.round(40 + Math.random() * 40),
        unit: '%',
        trend: Math.random() > 0.5 ? 'up' : 'stable',
        confidence: 80 + Math.random() * 15,
        lastUpdated: new Date().toISOString(),
        status: 'normal',
      },
      {
        id: `${farm.id}-soil`,
        type: 'soil_moisture',
        name: 'Soil Moisture',
        nameAr: 'رطوبة التربة',
        value: Math.round(20 + Math.random() * 60),
        unit: '%',
        trend: Math.random() > 0.6 ? 'down' : 'stable',
        confidence: 75 + Math.random() * 20,
        lastUpdated: new Date().toISOString(),
        status: Math.random() > 0.7 ? 'warning' : 'normal',
      },
      {
        id: `${farm.id}-ndvi`,
        type: 'ndvi',
        name: 'NDVI',
        nameAr: 'مؤشر الخضرة',
        value: parseFloat((0.3 + Math.random() * 0.5).toFixed(2)),
        unit: '',
        trend: Math.random() > 0.5 ? 'up' : 'down',
        confidence: 90 + Math.random() * 8,
        lastUpdated: new Date().toISOString(),
        status: 'normal',
      },
    ],
  }));
}

export default function SensorsPage() {
  const [farmsData, setFarmsData] = useState<FarmSensors[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFarm, setSelectedFarm] = useState<string | null>(null);

  useEffect(() => {
    loadSensorData();
  }, []);

  async function loadSensorData() {
    setIsLoading(true);
    try {
      // Try to fetch from API
      const response = await apiClient.get(`${API_URLS.virtualSensors}/v1/farms/readings`);
      setFarmsData(response.data);
    } catch (error) {
      // Fallback to mock data
      console.log('Using mock sensor data');
      setFarmsData(generateMockSensors());
    } finally {
      setIsLoading(false);
    }
  }

  // Calculate overall stats
  const stats = {
    totalFarms: farmsData.length,
    totalSensors: farmsData.reduce((acc, f) => acc + f.sensors.length, 0),
    warningCount: farmsData.reduce(
      (acc, f) => acc + f.sensors.filter(s => s.status === 'warning').length,
      0
    ),
    avgConfidence:
      farmsData.length > 0
        ? Math.round(
            farmsData.reduce(
              (acc, f) => acc + f.sensors.reduce((a, s) => a + s.confidence, 0) / f.sensors.length,
              0
            ) / farmsData.length
          )
        : 0,
  };

  const selectedFarmData = selectedFarm
    ? farmsData.find(f => f.farmId === selectedFarm)
    : null;

  return (
    <div className="p-6">
      <Header
        title="المستشعرات الافتراضية"
        subtitle="قراءات ذكية مدعومة بالذكاء الاصطناعي"
      />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-sahool-100 rounded-lg">
              <MapPin className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.totalFarms}</p>
              <p className="text-xs text-gray-500">مزرعة متصلة</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Cpu className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.totalSensors}</p>
              <p className="text-xs text-gray-500">مستشعر افتراضي</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-100 rounded-lg">
              <Activity className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-600">{stats.warningCount}</p>
              <p className="text-xs text-gray-500">تحذيرات</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{stats.avgConfidence}%</p>
              <p className="text-xs text-gray-500">متوسط الدقة</p>
            </div>
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="mt-6 flex justify-end">
        <button
          onClick={loadSensorData}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          تحديث القراءات
        </button>
      </div>

      {/* Farms Grid */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-gray-100 animate-pulse rounded-xl h-64" />
          ))
        ) : (
          farmsData.map(farm => (
            <div
              key={farm.farmId}
              className={cn(
                'bg-white rounded-xl border-2 transition-all cursor-pointer',
                selectedFarm === farm.farmId
                  ? 'border-sahool-500 shadow-lg'
                  : 'border-gray-100 hover:border-gray-200'
              )}
              onClick={() => setSelectedFarm(
                selectedFarm === farm.farmId ? null : farm.farmId
              )}
            >
              {/* Farm Header */}
              <div className="p-4 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-gray-900">{farm.farmName}</h3>
                    <p className="text-sm text-gray-500 flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {farm.governorate}
                    </p>
                  </div>
                  <div className="flex -space-x-2">
                    {farm.sensors.slice(0, 3).map(sensor => {
                      const Icon = SENSOR_ICONS[sensor.type];
                      return (
                        <div
                          key={sensor.id}
                          className={cn(
                            'w-8 h-8 rounded-full flex items-center justify-center border-2 border-white',
                            SENSOR_COLORS[sensor.type].split(' ')[1]
                          )}
                        >
                          <Icon className={cn('w-4 h-4', SENSOR_COLORS[sensor.type].split(' ')[0])} />
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Sensors */}
              <div className="p-4 grid grid-cols-2 gap-3">
                {farm.sensors.map(sensor => {
                  const Icon = SENSOR_ICONS[sensor.type];
                  const TrendIcon = sensor.trend === 'up' ? TrendingUp :
                                    sensor.trend === 'down' ? TrendingDown : Activity;

                  return (
                    <div
                      key={sensor.id}
                      className={cn(
                        'p-3 rounded-lg',
                        sensor.status === 'warning'
                          ? 'bg-amber-50 border border-amber-200'
                          : 'bg-gray-50'
                      )}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <Icon className={cn('w-4 h-4', SENSOR_COLORS[sensor.type].split(' ')[0])} />
                        <TrendIcon className={cn(
                          'w-3 h-3',
                          sensor.trend === 'up' ? 'text-green-500' :
                          sensor.trend === 'down' ? 'text-red-500' :
                          'text-gray-400'
                        )} />
                      </div>
                      <p className="text-lg font-bold text-gray-900">
                        {sensor.value}{sensor.unit}
                      </p>
                      <p className="text-xs text-gray-500">{sensor.nameAr}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Selected Farm Details */}
      {selectedFarmData && (
        <div className="mt-6 bg-white rounded-xl border border-gray-100 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            تفاصيل {selectedFarmData.farmName}
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-right text-sm text-gray-500 border-b border-gray-100">
                  <th className="pb-3 font-medium">المستشعر</th>
                  <th className="pb-3 font-medium">القيمة</th>
                  <th className="pb-3 font-medium">الاتجاه</th>
                  <th className="pb-3 font-medium">الدقة</th>
                  <th className="pb-3 font-medium">الحالة</th>
                </tr>
              </thead>
              <tbody>
                {selectedFarmData.sensors.map(sensor => {
                  const Icon = SENSOR_ICONS[sensor.type];
                  return (
                    <tr key={sensor.id} className="border-b border-gray-50">
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <Icon className={cn('w-5 h-5', SENSOR_COLORS[sensor.type].split(' ')[0])} />
                          <span className="font-medium">{sensor.nameAr}</span>
                        </div>
                      </td>
                      <td className="py-3 font-bold">{sensor.value}{sensor.unit}</td>
                      <td className="py-3">
                        <span className={cn(
                          'px-2 py-1 rounded text-xs',
                          sensor.trend === 'up' ? 'bg-green-100 text-green-700' :
                          sensor.trend === 'down' ? 'bg-red-100 text-red-700' :
                          'bg-gray-100 text-gray-700'
                        )}>
                          {sensor.trend === 'up' ? 'صاعد' :
                           sensor.trend === 'down' ? 'هابط' : 'مستقر'}
                        </span>
                      </td>
                      <td className="py-3">{sensor.confidence.toFixed(1)}%</td>
                      <td className="py-3">
                        <span className={cn(
                          'px-2 py-1 rounded text-xs',
                          sensor.status === 'warning' ? 'bg-amber-100 text-amber-700' :
                          sensor.status === 'critical' ? 'bg-red-100 text-red-700' :
                          'bg-green-100 text-green-700'
                        )}>
                          {sensor.status === 'warning' ? 'تحذير' :
                           sensor.status === 'critical' ? 'حرج' : 'طبيعي'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
