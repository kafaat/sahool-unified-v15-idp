// Sahool Admin Dashboard - Weather & Climate Page
// صفحة الطقس والمناخ

'use client';

import { useState, useEffect, useMemo } from 'react';
import { apiClient, API_URLS } from '@/lib/api';
import { API_PATHS } from '@/config/api';
import { logger } from '@/lib/logger';
import {
  Cloud,
  Droplets,
  Wind,
  Thermometer,
  Sun,
  AlertTriangle,
  MapPin,
  Calendar,
  Eye,
  Gauge,
  Loader2,
  RefreshCw,
  Sunrise,
  Sunset,
  CloudRain,
  CloudSnow,
  Cloudy,
  Waves,
} from 'lucide-react';

// ─── Types ───────────────────────────────────────────────────────────────────

interface WeatherLocation {
  id: string;
  name: string;
  name_ar: string;
  latitude: number;
  longitude: number;
  governorate?: string;
}

interface CurrentWeather {
  temperature: number;
  feels_like: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_direction: string;
  wind_direction_ar: string;
  visibility: number;
  uv_index: number;
  cloud_cover: number;
  description: string;
  description_ar: string;
  icon: string;
  sunrise: string;
  sunset: string;
  dew_point?: number;
  rain_last_1h?: number;
}

interface ForecastDay {
  date: string;
  day_name_ar: string;
  temp_max: number;
  temp_min: number;
  humidity: number;
  wind_speed: number;
  rain_probability: number;
  rain_amount_mm: number;
  description_ar: string;
  icon: string;
  uv_index: number;
}

interface AgriculturalReport {
  gdd_accumulated: number;
  gdd_daily: number;
  et_reference: number;
  soil_moisture_estimate: number;
  spray_window: {
    is_suitable: boolean;
    reason_ar: string;
    next_window_ar?: string;
    wind_ok: boolean;
    rain_ok: boolean;
    temp_ok: boolean;
    humidity_ok: boolean;
  };
  frost_risk: {
    level: 'none' | 'low' | 'moderate' | 'high';
    level_ar: string;
    min_temp_forecast: number;
  };
  irrigation_recommendation: {
    should_irrigate: boolean;
    reason_ar: string;
    recommended_amount_mm?: number;
  };
  heat_stress: {
    level: 'none' | 'low' | 'moderate' | 'high';
    level_ar: string;
    max_temp_forecast: number;
  };
}

interface WeatherAlert {
  id: string;
  type: string;
  type_ar: string;
  severity: 'info' | 'warning' | 'critical';
  message_ar: string;
  start_time: string;
  end_time: string;
  affected_area_ar: string;
}

// ─── Mock Data ───────────────────────────────────────────────────────────────

const MOCK_LOCATIONS: WeatherLocation[] = [
  {
    id: 'loc-1',
    name: "Sana'a",
    name_ar: 'صنعاء',
    latitude: 15.3694,
    longitude: 44.191,
    governorate: 'صنعاء',
  },
  {
    id: 'loc-2',
    name: 'Aden',
    name_ar: 'عدن',
    latitude: 12.7855,
    longitude: 45.0187,
    governorate: 'عدن',
  },
  {
    id: 'loc-3',
    name: 'Taiz',
    name_ar: 'تعز',
    latitude: 13.5789,
    longitude: 44.0219,
    governorate: 'تعز',
  },
  {
    id: 'loc-4',
    name: 'Hodeidah',
    name_ar: 'الحديدة',
    latitude: 14.7979,
    longitude: 42.9544,
    governorate: 'الحديدة',
  },
  {
    id: 'loc-5',
    name: 'Ibb',
    name_ar: 'إب',
    latitude: 13.9667,
    longitude: 44.1667,
    governorate: 'إب',
  },
];

const MOCK_CURRENT: CurrentWeather = {
  temperature: 22,
  feels_like: 24,
  humidity: 45,
  pressure: 1013,
  wind_speed: 12,
  wind_direction: 'NW',
  wind_direction_ar: 'شمال غربي',
  visibility: 10,
  uv_index: 7,
  cloud_cover: 30,
  description: 'Partly Cloudy',
  description_ar: 'غائم جزئياً',
  icon: 'partly-cloudy',
  sunrise: '06:15',
  sunset: '18:32',
  dew_point: 10,
  rain_last_1h: 0,
};

const MOCK_FORECAST: ForecastDay[] = [
  {
    date: '2026-03-18',
    day_name_ar: 'الأربعاء',
    temp_max: 24,
    temp_min: 12,
    humidity: 40,
    wind_speed: 10,
    rain_probability: 10,
    rain_amount_mm: 0,
    description_ar: 'مشمس',
    icon: 'sunny',
    uv_index: 8,
  },
  {
    date: '2026-03-19',
    day_name_ar: 'الخميس',
    temp_max: 23,
    temp_min: 11,
    humidity: 45,
    wind_speed: 15,
    rain_probability: 20,
    rain_amount_mm: 0,
    description_ar: 'غائم جزئياً',
    icon: 'partly-cloudy',
    uv_index: 6,
  },
  {
    date: '2026-03-20',
    day_name_ar: 'الجمعة',
    temp_max: 20,
    temp_min: 10,
    humidity: 60,
    wind_speed: 20,
    rain_probability: 65,
    rain_amount_mm: 8,
    description_ar: 'أمطار خفيفة',
    icon: 'rain',
    uv_index: 3,
  },
  {
    date: '2026-03-21',
    day_name_ar: 'السبت',
    temp_max: 18,
    temp_min: 9,
    humidity: 70,
    wind_speed: 18,
    rain_probability: 80,
    rain_amount_mm: 15,
    description_ar: 'أمطار متوسطة',
    icon: 'rain',
    uv_index: 2,
  },
  {
    date: '2026-03-22',
    day_name_ar: 'الأحد',
    temp_max: 21,
    temp_min: 10,
    humidity: 55,
    wind_speed: 12,
    rain_probability: 30,
    rain_amount_mm: 2,
    description_ar: 'غائم',
    icon: 'cloudy',
    uv_index: 5,
  },
  {
    date: '2026-03-23',
    day_name_ar: 'الاثنين',
    temp_max: 25,
    temp_min: 13,
    humidity: 35,
    wind_speed: 8,
    rain_probability: 5,
    rain_amount_mm: 0,
    description_ar: 'مشمس',
    icon: 'sunny',
    uv_index: 9,
  },
  {
    date: '2026-03-24',
    day_name_ar: 'الثلاثاء',
    temp_max: 26,
    temp_min: 14,
    humidity: 30,
    wind_speed: 10,
    rain_probability: 0,
    rain_amount_mm: 0,
    description_ar: 'صافي',
    icon: 'sunny',
    uv_index: 9,
  },
];

const MOCK_AGRI_REPORT: AgriculturalReport = {
  gdd_accumulated: 485,
  gdd_daily: 12.5,
  et_reference: 4.2,
  soil_moisture_estimate: 38,
  spray_window: {
    is_suitable: true,
    reason_ar: 'الظروف مناسبة للرش - رياح هادئة ولا أمطار متوقعة خلال 6 ساعات',
    wind_ok: true,
    rain_ok: true,
    temp_ok: true,
    humidity_ok: true,
  },
  frost_risk: {
    level: 'low',
    level_ar: 'منخفض',
    min_temp_forecast: 9,
  },
  irrigation_recommendation: {
    should_irrigate: true,
    reason_ar: 'رطوبة التربة أقل من الحد الأمثل (38%) — يُنصح بالري خلال 24 ساعة',
    recommended_amount_mm: 20,
  },
  heat_stress: {
    level: 'none',
    level_ar: 'لا يوجد',
    max_temp_forecast: 26,
  },
};

const MOCK_ALERTS: WeatherAlert[] = [
  {
    id: 'alert-1',
    type: 'rain',
    type_ar: 'أمطار',
    severity: 'warning',
    message_ar: 'أمطار غزيرة متوقعة يومي الجمعة والسبت — احتمال فيضانات في الأودية المنخفضة',
    start_time: '2026-03-20T06:00:00Z',
    end_time: '2026-03-21T18:00:00Z',
    affected_area_ar: 'صنعاء، إب، تعز',
  },
  {
    id: 'alert-2',
    type: 'wind',
    type_ar: 'رياح',
    severity: 'info',
    message_ar: 'رياح نشطة متوقعة يوم الجمعة — تجنب عمليات الرش',
    start_time: '2026-03-20T08:00:00Z',
    end_time: '2026-03-20T16:00:00Z',
    affected_area_ar: 'الحديدة، عدن',
  },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function getWeatherIcon(icon: string, size = 24) {
  const iconClass = `w-${size === 24 ? 6 : 8} h-${size === 24 ? 6 : 8}`;
  switch (icon) {
    case 'sunny':
      return <Sun className={`${iconClass} text-yellow-500`} />;
    case 'rain':
      return <CloudRain className={`${iconClass} text-blue-500`} />;
    case 'snow':
      return <CloudSnow className={`${iconClass} text-blue-300`} />;
    case 'cloudy':
      return <Cloudy className={`${iconClass} text-gray-400`} />;
    default:
      return <Cloud className={`${iconClass} text-gray-300`} />;
  }
}

function getSeverityColor(severity: string) {
  switch (severity) {
    case 'critical':
      return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-300';
    case 'warning':
      return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-300';
    default:
      return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-300';
  }
}

function getRiskColor(level: string) {
  switch (level) {
    case 'high':
      return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20';
    case 'moderate':
      return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20';
    case 'low':
      return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20';
    default:
      return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20';
  }
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function WeatherPage() {
  const [selectedLocation, setSelectedLocation] = useState<WeatherLocation>(MOCK_LOCATIONS[0]!);
  const [current, setCurrent] = useState<CurrentWeather | null>(null);
  const [forecast, setForecast] = useState<ForecastDay[]>([]);
  const [agriReport, setAgriReport] = useState<AgriculturalReport | null>(null);
  const [alerts, setAlerts] = useState<WeatherAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadWeatherData = async (location: WeatherLocation) => {
    setIsLoading(true);
    try {
      // Try fetching from the weather service
      const [currentRes, forecastRes, agriRes, alertsRes] = await Promise.allSettled([
        apiClient.get(`${API_URLS.weather}${API_PATHS.weather.byLocation(location.id)}`),
        apiClient.get(`${API_URLS.weather}${API_PATHS.weather.forecastByLocation(location.id)}`),
        apiClient.get(`${API_URLS.weather}${API_PATHS.weather.agricultural}`, {
          params: { location_id: location.id },
        }),
        apiClient.get(`${API_URLS.weather}${API_PATHS.weather.alerts(location.id)}`),
      ]);

      setCurrent(currentRes.status === 'fulfilled' ? currentRes.value.data : MOCK_CURRENT);
      setForecast(forecastRes.status === 'fulfilled' ? forecastRes.value.data : MOCK_FORECAST);
      setAgriReport(agriRes.status === 'fulfilled' ? agriRes.value.data : MOCK_AGRI_REPORT);
      setAlerts(alertsRes.status === 'fulfilled' ? alertsRes.value.data : MOCK_ALERTS);
      setLastUpdated(new Date());
    } catch (err) {
      logger.warn('Weather API unavailable, using demo data', err);
      setCurrent(MOCK_CURRENT);
      setForecast(MOCK_FORECAST);
      setAgriReport(MOCK_AGRI_REPORT);
      setAlerts(MOCK_ALERTS);
      setLastUpdated(new Date());
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadWeatherData(selectedLocation);
  }, [selectedLocation]);

  const totalRainForecast = useMemo(
    () => forecast.reduce((sum, d) => sum + d.rain_amount_mm, 0),
    [forecast]
  );

  if (isLoading && !current) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-600" />
        <span className="mr-3 text-gray-500 dark:text-gray-400">جاري تحميل بيانات الطقس...</span>
      </div>
    );
  }

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">الطقس والمناخ</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            بيانات الطقس الميدانية والتوصيات الزراعية المرتبطة
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Location selector */}
          <div className="relative">
            <select
              value={selectedLocation.id}
              onChange={(e) => {
                const loc = MOCK_LOCATIONS.find((l) => l.id === e.target.value);
                if (loc) setSelectedLocation(loc);
              }}
              className="appearance-none bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-2 pr-10 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            >
              {MOCK_LOCATIONS.map((loc) => (
                <option key={loc.id} value={loc.id}>
                  {loc.name_ar}
                </option>
              ))}
            </select>
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
          <button
            onClick={() => loadWeatherData(selectedLocation)}
            className="flex items-center gap-2 px-3 py-2 bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 rounded-lg text-sm hover:bg-sahool-100 dark:hover:bg-sahool-900/50 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            تحديث
          </button>
        </div>
      </div>

      {/* Weather Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`flex items-start gap-3 p-4 rounded-lg border ${getSeverityColor(alert.severity)}`}
            >
              <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm">{alert.type_ar}</span>
                  <span className="text-xs opacity-75">{alert.affected_area_ar}</span>
                </div>
                <p className="text-sm">{alert.message_ar}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Current Weather Card */}
      {current && (
        <div className="bg-gradient-to-br from-blue-500 to-blue-700 dark:from-blue-700 dark:to-blue-900 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <MapPin className="w-4 h-4 opacity-80" />
                <span className="text-sm opacity-90">
                  {selectedLocation.name_ar} — {selectedLocation.governorate}
                </span>
              </div>
              <div className="flex items-end gap-3 mt-3">
                <span className="text-6xl font-bold">{current.temperature}°</span>
                <div className="mb-2">
                  <p className="text-lg opacity-90">{current.description_ar}</p>
                  <p className="text-sm opacity-70">الإحساس: {current.feels_like}°م</p>
                </div>
              </div>
            </div>
            <div className="text-left space-y-2 text-sm opacity-90">
              <div className="flex items-center gap-2">
                <Sunrise className="w-4 h-4" />
                <span>الشروق: {current.sunrise}</span>
              </div>
              <div className="flex items-center gap-2">
                <Sunset className="w-4 h-4" />
                <span>الغروب: {current.sunset}</span>
              </div>
              {lastUpdated && (
                <p className="text-xs opacity-60 mt-2">
                  آخر تحديث: {lastUpdated.toLocaleTimeString('ar-YE')}
                </p>
              )}
            </div>
          </div>

          {/* Current metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4 mt-6 pt-4 border-t border-white/20">
            {[
              { icon: Droplets, label: 'الرطوبة', value: `${current.humidity}%` },
              {
                icon: Wind,
                label: 'الرياح',
                value: `${current.wind_speed} كم/س ${current.wind_direction_ar}`,
              },
              { icon: Gauge, label: 'الضغط', value: `${current.pressure} هبا` },
              { icon: Eye, label: 'الرؤية', value: `${current.visibility} كم` },
              { icon: Sun, label: 'مؤشر UV', value: `${current.uv_index}` },
              { icon: Waves, label: 'نقطة الندى', value: `${current.dew_point ?? '-'}°م` },
            ].map((m) => (
              <div key={m.label} className="flex items-center gap-2">
                <m.icon className="w-4 h-4 opacity-70" />
                <div>
                  <p className="text-xs opacity-60">{m.label}</p>
                  <p className="text-sm font-medium">{m.value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 7-Day Forecast */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-sahool-600" />
            توقعات 7 أيام
          </h2>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            إجمالي الأمطار المتوقعة:{' '}
            <span className="font-bold text-blue-600 dark:text-blue-400">
              {totalRainForecast} ملم
            </span>
          </div>
        </div>

        <div className="grid grid-cols-7 gap-3">
          {forecast.map((day) => (
            <div
              key={day.date}
              className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2">
                {day.day_name_ar}
              </p>
              <div className="flex justify-center mb-2">{getWeatherIcon(day.icon)}</div>
              <div className="flex items-center justify-center gap-1 text-sm mb-1">
                <span className="font-bold text-gray-900 dark:text-gray-100">{day.temp_max}°</span>
                <span className="text-gray-400">/</span>
                <span className="text-gray-500 dark:text-gray-400">{day.temp_min}°</span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{day.description_ar}</p>
              {day.rain_probability > 0 && (
                <div className="flex items-center justify-center gap-1 text-xs text-blue-600 dark:text-blue-400">
                  <CloudRain className="w-3 h-3" />
                  <span>{day.rain_probability}%</span>
                </div>
              )}
              {day.rain_amount_mm > 0 && (
                <p className="text-xs text-blue-500 font-medium mt-0.5">{day.rain_amount_mm} ملم</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Agricultural Insights */}
      {agriReport && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Spray Window */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Droplets className="w-5 h-5 text-blue-600" />
              نافذة الرش الذكية
            </h3>
            <div
              className={`p-4 rounded-lg mb-4 ${
                agriReport.spray_window.is_suitable
                  ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                  : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`w-3 h-3 rounded-full ${agriReport.spray_window.is_suitable ? 'bg-green-500' : 'bg-red-500'}`}
                />
                <span
                  className={`font-bold text-sm ${
                    agriReport.spray_window.is_suitable
                      ? 'text-green-800 dark:text-green-300'
                      : 'text-red-800 dark:text-red-300'
                  }`}
                >
                  {agriReport.spray_window.is_suitable ? 'مناسب للرش الآن' : 'غير مناسب للرش'}
                </span>
              </div>
              <p
                className={`text-sm ${
                  agriReport.spray_window.is_suitable
                    ? 'text-green-700 dark:text-green-400'
                    : 'text-red-700 dark:text-red-400'
                }`}
              >
                {agriReport.spray_window.reason_ar}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'الرياح', ok: agriReport.spray_window.wind_ok },
                { label: 'الأمطار', ok: agriReport.spray_window.rain_ok },
                { label: 'الحرارة', ok: agriReport.spray_window.temp_ok },
                { label: 'الرطوبة', ok: agriReport.spray_window.humidity_ok },
              ].map((c) => (
                <div
                  key={c.label}
                  className={`flex items-center gap-2 p-2 rounded text-sm ${
                    c.ok
                      ? 'bg-green-50 dark:bg-green-900/10 text-green-700 dark:text-green-400'
                      : 'bg-red-50 dark:bg-red-900/10 text-red-700 dark:text-red-400'
                  }`}
                >
                  <div className={`w-2 h-2 rounded-full ${c.ok ? 'bg-green-500' : 'bg-red-500'}`} />
                  {c.label}: {c.ok ? 'مناسب' : 'غير مناسب'}
                </div>
              ))}
            </div>
          </div>

          {/* GDD & ET */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Thermometer className="w-5 h-5 text-orange-600" />
              مؤشرات النمو والري
            </h3>

            <div className="space-y-4">
              {/* GDD */}
              <div className="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-900/10 rounded-lg">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    درجات النمو المتراكمة (GDD)
                  </p>
                  <p className="text-2xl font-bold text-orange-700 dark:text-orange-400">
                    {agriReport.gdd_accumulated}
                  </p>
                </div>
                <div className="text-left">
                  <p className="text-xs text-gray-500 dark:text-gray-400">اليوم</p>
                  <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
                    +{agriReport.gdd_daily}
                  </p>
                </div>
              </div>

              {/* ET */}
              <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    التبخر-نتح المرجعي (ET₀)
                  </p>
                  <p className="text-2xl font-bold text-blue-700 dark:text-blue-400">
                    {agriReport.et_reference} <span className="text-sm font-normal">ملم/يوم</span>
                  </p>
                </div>
                <Waves className="w-8 h-8 text-blue-300" />
              </div>

              {/* Soil Moisture */}
              <div className="p-3 bg-green-50 dark:bg-green-900/10 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-gray-500 dark:text-gray-400">رطوبة التربة التقديرية</p>
                  <span className="text-sm font-bold text-green-700 dark:text-green-400">
                    {agriReport.soil_moisture_estimate}%
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                  <div
                    className="h-full rounded-full bg-gradient-to-l from-green-500 to-green-400"
                    style={{ width: `${agriReport.soil_moisture_estimate}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Irrigation Recommendation */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Droplets className="w-5 h-5 text-cyan-600" />
              توصية الري
            </h3>
            <div
              className={`p-4 rounded-lg ${
                agriReport.irrigation_recommendation.should_irrigate
                  ? 'bg-cyan-50 dark:bg-cyan-900/20 border border-cyan-200 dark:border-cyan-800'
                  : 'bg-gray-50 dark:bg-gray-800/50'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`w-3 h-3 rounded-full ${agriReport.irrigation_recommendation.should_irrigate ? 'bg-cyan-500 animate-pulse' : 'bg-gray-400'}`}
                />
                <span
                  className={`font-bold text-sm ${
                    agriReport.irrigation_recommendation.should_irrigate
                      ? 'text-cyan-800 dark:text-cyan-300'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  {agriReport.irrigation_recommendation.should_irrigate
                    ? 'يُنصح بالري'
                    : 'لا حاجة للري حالياً'}
                </span>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                {agriReport.irrigation_recommendation.reason_ar}
              </p>
              {agriReport.irrigation_recommendation.recommended_amount_mm && (
                <p className="text-sm font-bold text-cyan-700 dark:text-cyan-400 mt-2">
                  الكمية المقترحة: {agriReport.irrigation_recommendation.recommended_amount_mm} ملم
                </p>
              )}
            </div>
          </div>

          {/* Frost & Heat Risk */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              مخاطر الطقس
            </h3>
            <div className="space-y-3">
              <div
                className={`flex items-center justify-between p-3 rounded-lg ${getRiskColor(agriReport.frost_risk.level)}`}
              >
                <div className="flex items-center gap-2">
                  <CloudSnow className="w-5 h-5" />
                  <div>
                    <p className="text-sm font-medium">خطر الصقيع</p>
                    <p className="text-xs opacity-75">
                      أدنى حرارة متوقعة: {agriReport.frost_risk.min_temp_forecast}°م
                    </p>
                  </div>
                </div>
                <span className="text-sm font-bold">{agriReport.frost_risk.level_ar}</span>
              </div>

              <div
                className={`flex items-center justify-between p-3 rounded-lg ${getRiskColor(agriReport.heat_stress.level)}`}
              >
                <div className="flex items-center gap-2">
                  <Thermometer className="w-5 h-5" />
                  <div>
                    <p className="text-sm font-medium">الإجهاد الحراري</p>
                    <p className="text-xs opacity-75">
                      أعلى حرارة متوقعة: {agriReport.heat_stress.max_temp_forecast}°م
                    </p>
                  </div>
                </div>
                <span className="text-sm font-bold">{agriReport.heat_stress.level_ar}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rainfall History Bar (visual) */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <CloudRain className="w-5 h-5 text-blue-600" />
          هطول الأمطار المتوقع (7 أيام)
        </h3>
        <div className="flex items-end gap-3 h-32">
          {forecast.map((day) => {
            const maxRain = Math.max(...forecast.map((d) => d.rain_amount_mm), 1);
            const height =
              day.rain_amount_mm > 0 ? Math.max((day.rain_amount_mm / maxRain) * 100, 8) : 4;
            return (
              <div key={day.date} className="flex-1 flex flex-col items-center gap-1">
                {day.rain_amount_mm > 0 && (
                  <span className="text-xs font-bold text-blue-600 dark:text-blue-400">
                    {day.rain_amount_mm}
                  </span>
                )}
                <div
                  className={`w-full rounded-t-md transition-all ${
                    day.rain_amount_mm > 0
                      ? 'bg-gradient-to-t from-blue-600 to-blue-400'
                      : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                  style={{ height: `${height}%` }}
                />
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {day.day_name_ar.slice(0, 3)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
