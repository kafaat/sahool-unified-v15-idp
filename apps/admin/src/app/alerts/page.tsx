// @ts-nocheck - Temporary fix for types with React 19
'use client';

// Weather & Alerts Dashboard - الطقس والتنبيهات
// Real-time weather monitoring and agricultural alerts

import { useEffect, useState } from 'react';
import Header from '@/components/layout/Header';
import { cn } from '@/lib/utils';
import {
  Cloud,
  Sun,
  CloudRain,
  Wind,
  Droplets,
  AlertTriangle,
  Bell,
  MapPin,
  Calendar,
  RefreshCw,
} from 'lucide-react';

interface WeatherData {
  governorate: string;
  temperature: number;
  humidity: number;
  windSpeed: number;
  condition: 'sunny' | 'cloudy' | 'rainy' | 'windy';
  forecast: { day: string; temp: number; condition: string }[];
}

interface Alert {
  id: string;
  type: 'weather' | 'disease' | 'irrigation' | 'pest';
  severity: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  governorate: string;
  createdAt: string;
  isRead: boolean;
}

const WEATHER_ICONS = {
  sunny: Sun,
  cloudy: Cloud,
  rainy: CloudRain,
  windy: Wind,
};

// Mock data
function generateMockWeather(): WeatherData[] {
  const governorates = ['صنعاء', 'تعز', 'إب', 'حضرموت', 'الحديدة', 'عدن'];
  const conditions: Array<'sunny' | 'cloudy' | 'rainy' | 'windy'> = ['sunny', 'cloudy', 'rainy', 'windy'];

  return governorates.map(gov => ({
    governorate: gov,
    temperature: Math.round(20 + Math.random() * 20),
    humidity: Math.round(30 + Math.random() * 50),
    windSpeed: Math.round(5 + Math.random() * 25),
    condition: conditions[Math.floor(Math.random() * conditions.length)],
    forecast: Array.from({ length: 5 }, (_, i) => ({
      day: ['السبت', 'الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء'][i],
      temp: Math.round(18 + Math.random() * 22),
      condition: conditions[Math.floor(Math.random() * conditions.length)],
    })),
  }));
}

function generateMockAlerts(): Alert[] {
  const alerts: Alert[] = [
    {
      id: '1',
      type: 'weather',
      severity: 'warning',
      title: 'تحذير من موجة حر',
      message: 'درجات حرارة مرتفعة متوقعة خلال الأيام القادمة. يُنصح بزيادة الري.',
      governorate: 'صنعاء',
      createdAt: new Date().toISOString(),
      isRead: false,
    },
    {
      id: '2',
      type: 'disease',
      severity: 'critical',
      title: 'انتشار اللفحة المتأخرة',
      message: 'تم رصد حالات إصابة باللفحة المتأخرة في منطقة تعز. فحص المزارع فوراً.',
      governorate: 'تعز',
      createdAt: new Date(Date.now() - 3600000).toISOString(),
      isRead: false,
    },
    {
      id: '3',
      type: 'irrigation',
      severity: 'info',
      title: 'موعد الري الأمثل',
      message: 'الظروف الجوية مناسبة للري في الصباح الباكر أو بعد الغروب.',
      governorate: 'إب',
      createdAt: new Date(Date.now() - 7200000).toISOString(),
      isRead: true,
    },
    {
      id: '4',
      type: 'pest',
      severity: 'warning',
      title: 'نشاط حشري متزايد',
      message: 'ارتفاع في نشاط الحشرات بسبب الرطوبة العالية. المراقبة مطلوبة.',
      governorate: 'الحديدة',
      createdAt: new Date(Date.now() - 86400000).toISOString(),
      isRead: true,
    },
  ];

  return alerts;
}

export default function AlertsPage() {
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedGovernorate, setSelectedGovernorate] = useState<string | null>(null);
  const [alertFilter, setAlertFilter] = useState<'all' | 'unread'>('all');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    setWeatherData(generateMockWeather());
    setAlerts(generateMockAlerts());
    setIsLoading(false);
  }

  const markAsRead = (alertId: string) => {
    setAlerts(prev =>
      prev.map(a => (a.id === alertId ? { ...a, isRead: true } : a))
    );
  };

  const filteredAlerts = alertFilter === 'unread'
    ? alerts.filter(a => !a.isRead)
    : alerts;

  const selectedWeather = selectedGovernorate
    ? weatherData.find(w => w.governorate === selectedGovernorate)
    : weatherData[0];

  const alertTypeIcons = {
    weather: Cloud,
    disease: AlertTriangle,
    irrigation: Droplets,
    pest: AlertTriangle,
  };

  const severityColors = {
    info: 'bg-blue-100 text-blue-700 border-blue-200',
    warning: 'bg-amber-100 text-amber-700 border-amber-200',
    critical: 'bg-red-100 text-red-700 border-red-200',
  };

  return (
    <div className="p-6">
      <Header
        title="الطقس والتنبيهات"
        subtitle="مراقبة الأحوال الجوية والتنبيهات الزراعية"
      />

      {/* Refresh Button */}
      <div className="mt-6 flex justify-end">
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          تحديث
        </button>
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weather Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Main Weather Card */}
          {selectedWeather && (
            <div className="bg-gradient-to-br from-sahool-500 to-sahool-700 rounded-2xl p-6 text-white">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sahool-100 mb-1">الطقس الآن</p>
                  <h2 className="text-3xl font-bold flex items-center gap-2">
                    <MapPin className="w-6 h-6" />
                    {selectedWeather.governorate}
                  </h2>
                </div>
                {(() => {
                  const WeatherIcon = WEATHER_ICONS[selectedWeather.condition];
                  return <WeatherIcon className="w-16 h-16 text-white/80" />;
                })()}
              </div>

              <div className="mt-6 flex items-end gap-4">
                <span className="text-6xl font-bold">{selectedWeather.temperature}°</span>
                <div className="mb-2 text-sahool-100">
                  <p>الرطوبة: {selectedWeather.humidity}%</p>
                  <p>الرياح: {selectedWeather.windSpeed} كم/س</p>
                </div>
              </div>

              {/* 5-Day Forecast */}
              <div className="mt-6 pt-6 border-t border-white/20">
                <p className="text-sm text-sahool-100 mb-3">توقعات الأيام القادمة</p>
                <div className="grid grid-cols-5 gap-2">
                  {selectedWeather.forecast.map((day, i) => {
                    const DayIcon = WEATHER_ICONS[day.condition as keyof typeof WEATHER_ICONS] || Sun;
                    return (
                      <div key={i} className="text-center">
                        <p className="text-xs text-sahool-100">{day.day}</p>
                        <DayIcon className="w-6 h-6 mx-auto my-1" />
                        <p className="font-bold">{day.temp}°</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Governorate Selector */}
          <div className="bg-white rounded-xl border border-gray-100 p-4">
            <p className="text-sm text-gray-500 mb-3">اختر المحافظة</p>
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
              {weatherData.map(weather => {
                const WeatherIcon = WEATHER_ICONS[weather.condition];
                const isSelected = selectedGovernorate === weather.governorate ||
                  (!selectedGovernorate && weather === weatherData[0]);

                return (
                  <button
                    key={weather.governorate}
                    onClick={() => setSelectedGovernorate(weather.governorate)}
                    className={cn(
                      'p-3 rounded-lg text-center transition-all',
                      isSelected
                        ? 'bg-sahool-50 border-2 border-sahool-500'
                        : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                    )}
                  >
                    <WeatherIcon className={cn(
                      'w-5 h-5 mx-auto mb-1',
                      isSelected ? 'text-sahool-600' : 'text-gray-400'
                    )} />
                    <p className="text-xs font-medium">{weather.governorate}</p>
                    <p className="text-lg font-bold">{weather.temperature}°</p>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Alerts Section */}
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <Bell className="w-5 h-5 text-sahool-600" />
              التنبيهات
            </h3>
            <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setAlertFilter('all')}
                className={cn(
                  'px-3 py-1 text-xs rounded-md transition-colors',
                  alertFilter === 'all'
                    ? 'bg-white shadow-sm'
                    : 'text-gray-600'
                )}
              >
                الكل
              </button>
              <button
                onClick={() => setAlertFilter('unread')}
                className={cn(
                  'px-3 py-1 text-xs rounded-md transition-colors',
                  alertFilter === 'unread'
                    ? 'bg-white shadow-sm'
                    : 'text-gray-600'
                )}
              >
                غير مقروء ({alerts.filter(a => !a.isRead).length})
              </button>
            </div>
          </div>

          <div className="space-y-3 max-h-[500px] overflow-y-auto">
            {filteredAlerts.length > 0 ? (
              filteredAlerts.map(alert => {
                const AlertIcon = alertTypeIcons[alert.type];
                return (
                  <div
                    key={alert.id}
                    className={cn(
                      'p-4 rounded-lg border transition-all cursor-pointer',
                      severityColors[alert.severity],
                      !alert.isRead && 'ring-2 ring-offset-2 ring-sahool-500'
                    )}
                    onClick={() => markAsRead(alert.id)}
                  >
                    <div className="flex items-start gap-3">
                      <AlertIcon className="w-5 h-5 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-bold text-sm">{alert.title}</h4>
                          {!alert.isRead && (
                            <span className="w-2 h-2 bg-sahool-500 rounded-full" />
                          )}
                        </div>
                        <p className="text-xs opacity-80 line-clamp-2">{alert.message}</p>
                        <div className="mt-2 flex items-center gap-2 text-xs opacity-70">
                          <MapPin className="w-3 h-3" />
                          {alert.governorate}
                          <Calendar className="w-3 h-3 mr-2" />
                          {new Date(alert.createdAt).toLocaleDateString('ar-YE')}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Bell className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>لا توجد تنبيهات</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
