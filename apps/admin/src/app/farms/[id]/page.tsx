'use client';

/**
 * Field Detail Page - صفحة تفاصيل الحقل
 *
 * Shows field info, map, NDVI/satellite, weather, and agricultural KPIs.
 */

import { useParams } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import {
  MapPin,
  Leaf,
  Droplets,
  Wind,
  Thermometer,
  CloudRain,
  Sun,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  RefreshCw,
  Calendar,
  Sprout,
  Activity,
} from 'lucide-react';
import { useField } from '@/hooks/api/use-fields';
import {
  useWeatherCurrent,
  useWeatherForecast,
  useAgriculturalReport,
} from '@/hooks/api/use-weather';
import type { BaseFarmData } from '@/components/maps/FarmsMap';

// ─────────────────────────────────────────────────────────────────────────────
// Weather / Agricultural data types
// ─────────────────────────────────────────────────────────────────────────────

interface WeatherData {
  temperature_c?: number;
  condition?: string;
  condition_ar?: string;
  humidity_percent?: number;
  humidity_pct?: number;
  wind_speed_kmh?: number;
  precipitation_mm?: number;
  cloud_cover_pct?: number;
  pressure_hpa?: number;
  uv_index?: number;
  [key: string]: unknown;
}

interface ForecastDay {
  date?: string;
  temp_max_c?: number;
  temp_min_c?: number;
  temperature_c?: number;
  precipitation_mm?: number;
  condition?: string;
  condition_ar?: string;
  [key: string]: unknown;
}

interface ForecastData {
  daily?: ForecastDay[];
  forecast?: ForecastDay[];
  data?: ForecastDay[] | { forecast?: ForecastDay[] };
  [key: string]: unknown;
}

interface AgReportData {
  et0?: number;
  evapotranspiration?: number | { et0?: number };
  gdd?: number;
  growing_degree_days?: number | { gdd?: number };
  spray_window?: { suitable?: boolean; suitability?: string } | boolean;
  spray_suitable?: boolean;
  data?: AgReportData;
  [key: string]: unknown;
}

// Dynamically import the map component (no SSR for Leaflet)
const FarmsMap = dynamic(() => import('@/components/maps/FarmsMap'), {
  ssr: false,
  loading: () => (
    <div className="h-full min-h-[300px] bg-gray-100 animate-pulse flex items-center justify-center rounded-xl">
      <p className="text-gray-400 text-sm">جاري تحميل الخريطة...</p>
    </div>
  ),
});

// ─────────────────────────────────────────────────────────────────────────────
// NDVI Health helpers
// ─────────────────────────────────────────────────────────────────────────────

interface NdviData {
  ndvi?: number;
  lai?: number;
  health_status?: string;
  trend?: string;
  timestamp?: string;
}

function getHealthColor(status: string | undefined): string {
  switch (status) {
    case 'healthy':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'moderate':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'stressed':
      return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'critical':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
}

function getHealthLabel(status: string | undefined): string {
  switch (status) {
    case 'healthy':
      return 'صحي';
    case 'moderate':
      return 'معتدل';
    case 'stressed':
      return 'مجهد';
    case 'critical':
      return 'حرج';
    default:
      return 'غير معروف';
  }
}

function getStatusBadge(status: string | undefined): { label: string; className: string } {
  switch (status) {
    case 'active':
      return { label: 'نشط', className: 'bg-green-100 text-green-700' };
    case 'fallow':
      return { label: 'بور', className: 'bg-yellow-100 text-yellow-700' };
    case 'harvested':
      return { label: 'تم الحصاد', className: 'bg-blue-100 text-blue-700' };
    case 'planned':
      return { label: 'مخطط', className: 'bg-purple-100 text-purple-700' };
    default:
      return { label: status ?? 'غير معروف', className: 'bg-gray-100 text-gray-700' };
  }
}

function TrendIcon({ trend }: { trend?: string }) {
  if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-500" />;
  if (trend === 'down') return <TrendingDown className="w-4 h-4 text-red-500" />;
  return <Minus className="w-4 h-4 text-gray-400" />;
}

// ─────────────────────────────────────────────────────────────────────────────
// Skeleton Components
// ─────────────────────────────────────────────────────────────────────────────

function CardSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 p-6 animate-pulse ${className}`}>
      <div className="h-4 bg-gray-200 rounded w-1/3 mb-4" />
      <div className="space-y-3">
        <div className="h-3 bg-gray-200 rounded w-2/3" />
        <div className="h-3 bg-gray-200 rounded w-1/2" />
        <div className="h-3 bg-gray-200 rounded w-3/4" />
      </div>
    </div>
  );
}

function ErrorCard({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="bg-white rounded-xl border border-red-200 p-6 flex flex-col items-center justify-center gap-3">
      <AlertTriangle className="w-8 h-8 text-red-400" />
      <p className="text-sm text-red-600 text-center">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1 text-sm text-red-600 hover:text-red-800 border border-red-300 rounded-lg px-3 py-1.5 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          إعادة المحاولة
        </button>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Page
// ─────────────────────────────────────────────────────────────────────────────

export default function FieldDetailPage() {
  const params = useParams();
  const fieldId = params.id as string;

  // ── Field data ──────────────────────────────────────────────────────────
  const {
    data: field,
    isLoading: fieldLoading,
    isError: fieldError,
    refetch: refetchField,
  } = useField(fieldId);

  // ── Coordinates (must be computed before NDVI/Weather hooks) ─────────────
  // Backend may include boundary (GeoJSON) not in the base Farm type
  const fieldBoundary = (field as Record<string, unknown> | undefined)?.boundary as number[][][] | undefined;
  const lat = field?.coordinates?.lat
    ?? (fieldBoundary?.[0]
      ? fieldBoundary[0].reduce((s: number, c: number[]) => s + (c[1] ?? 0), 0) / fieldBoundary[0].length
      : 0);
  const lng = field?.coordinates?.lng
    ?? (fieldBoundary?.[0]
      ? fieldBoundary[0].reduce((s: number, c: number[]) => s + (c[0] ?? 0), 0) / fieldBoundary[0].length
      : 0);
  const hasCoords = lat !== 0 || lng !== 0;

  // ── NDVI / Satellite data ──────────────────────────────────────────────
  const [ndvi, setNdvi] = useState<NdviData | null>(null);
  const [ndviLoading, setNdviLoading] = useState(true);
  const [ndviError, setNdviError] = useState(false);

  const fetchNdvi = useCallback(async () => {
    if (!fieldId) return;
    setNdviLoading(true);
    setNdviError(false);
    try {
      const params = new URLSearchParams({ action: 'indices', fieldId });
      if (lat) params.set('lat', String(lat));
      if (lng) params.set('lon', String(lng));
      const response = await fetch(`/api/satellite?${params}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setNdvi(data?.data ?? data);
    } catch {
      setNdviError(true);
    } finally {
      setNdviLoading(false);
    }
  }, [fieldId, lat, lng]);

  useEffect(() => {
    fetchNdvi();
  }, [fetchNdvi]);

  // ── Weather data ────────────────────────────────────────────────────────

  const {
    data: weatherRaw,
    isLoading: weatherLoading,
    isError: weatherError,
    refetch: refetchWeather,
  } = useWeatherCurrent(lat, lng, fieldId);
  const weather = ((weatherRaw as Record<string, unknown>)?.data ?? weatherRaw ?? {}) as WeatherData;

  const {
    data: forecastRaw,
    isLoading: forecastLoading,
    isError: forecastError,
    refetch: refetchForecast,
  } = useWeatherForecast(lat, lng, 7, fieldId);
  const forecast = forecastRaw as ForecastData | null;

  // ── Agricultural report ─────────────────────────────────────────────────
  const {
    data: agRaw,
    isLoading: agLoading,
    isError: agError,
    refetch: refetchAg,
  } = useAgriculturalReport(lat, lng, fieldId);
  const agReport = ((agRaw as Record<string, unknown>)?.data ?? agRaw ?? null) as AgReportData | null;

  // ── Map data ────────────────────────────────────────────────────────────
  const mapFarms: BaseFarmData[] = field
    ? [
        {
          id: field.id,
          name: field.name,
          nameAr: field.nameAr,
          coordinates: field.coordinates ?? { lat: 15.37, lng: 44.19 },
          healthScore: field.healthScore ?? 0,
          area: field.area ?? 0,
          crops: field.crops ?? [],
          status: field.status,
          boundary: (field as any).boundary,
        },
      ]
    : [];

  // ── Full-page error ─────────────────────────────────────────────────────
  if (fieldError) {
    return (
      <div dir="rtl" className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <ErrorCard
          message="تعذر تحميل بيانات الحقل. يرجى المحاولة مرة أخرى."
          onRetry={() => refetchField()}
        />
      </div>
    );
  }

  // ── Loading ─────────────────────────────────────────────────────────────
  if (fieldLoading) {
    return (
      <div dir="rtl" className="min-h-screen bg-gray-50 p-4 md:p-6 space-y-4">
        <CardSkeleton className="h-28" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <CardSkeleton className="h-80" />
          <CardSkeleton className="h-80" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <CardSkeleton className="h-64" />
          <CardSkeleton className="h-64" />
        </div>
      </div>
    );
  }

  const statusBadge = getStatusBadge(field?.status);

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-4 md:p-6 space-y-4">
      {/* ───────────── Field Info Header ───────────── */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
              <Sprout className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {field?.nameAr ?? field?.name ?? 'حقل'}
              </h1>
              {field?.name && field?.nameAr && (
                <p className="text-sm text-gray-500">{field.name}</p>
              )}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Crop type */}
            {field?.crops?.[0] && (
              <span className="inline-flex items-center gap-1 text-sm bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full">
                <Leaf className="w-3.5 h-3.5" />
                {field.crops[0]}
              </span>
            )}

            {/* Area */}
            {field?.area != null && (
              <span className="inline-flex items-center gap-1 text-sm bg-blue-50 text-blue-700 px-3 py-1 rounded-full">
                <MapPin className="w-3.5 h-3.5" />
                {field.area.toFixed(1)} هكتار
              </span>
            )}

            {/* Status */}
            <span
              className={`inline-flex items-center text-sm px-3 py-1 rounded-full font-medium ${statusBadge.className}`}
            >
              {statusBadge.label}
            </span>

            {/* Health score */}
            {field?.healthScore != null && (
              <span className="inline-flex items-center gap-1 text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
                <Activity className="w-3.5 h-3.5" />
                {field.healthScore}%
              </span>
            )}
          </div>
        </div>

        {/* Extra info row */}
        {(field?.lastUpdated || field?.createdAt) && (
          <div className="mt-3 pt-3 border-t border-gray-100 flex flex-wrap gap-4 text-xs text-gray-400">
            {field?.createdAt && (
              <span className="inline-flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                تاريخ الإنشاء: {new Date(field.createdAt).toLocaleDateString('ar')}
              </span>
            )}
            {field?.lastUpdated && (
              <span className="inline-flex items-center gap-1">
                <RefreshCw className="w-3 h-3" />
                آخر تحديث: {new Date(field.lastUpdated).toLocaleDateString('ar')}
              </span>
            )}
          </div>
        )}
      </div>

      {/* ───────────── Middle Row: Map + NDVI ───────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Map Panel */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-blue-500" />
              موقع الحقل
            </h2>
          </div>
          <div className="h-80">
            {hasCoords ? (
              <FarmsMap farms={mapFarms} showHealthOverlay className="h-full w-full" />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400 text-sm">
                لا توجد إحداثيات متاحة
              </div>
            )}
          </div>
        </div>

        {/* NDVI / Satellite Panel */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
          <div className="px-5 py-3 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <Leaf className="w-4 h-4 text-green-500" />
              صحة الغطاء النباتي (NDVI)
            </h2>
          </div>

          <div className="p-5 h-[calc(100%-3rem)]">
            {ndviLoading ? (
              <div className="animate-pulse space-y-4 h-full flex flex-col justify-center">
                <div className="h-16 bg-gray-100 rounded-lg" />
                <div className="h-4 bg-gray-100 rounded w-1/2" />
                <div className="h-4 bg-gray-100 rounded w-2/3" />
              </div>
            ) : ndviError ? (
              <ErrorCard
                message="تعذر تحميل بيانات القمر الصناعي"
                onRetry={fetchNdvi}
              />
            ) : (
              <div className="space-y-5">
                {/* Health status badge */}
                <div
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium ${getHealthColor(ndvi?.health_status)}`}
                >
                  <Leaf className="w-4 h-4" />
                  {getHealthLabel(ndvi?.health_status)}
                </div>

                {/* NDVI value */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 mb-1">قيمة NDVI</p>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold text-gray-900">
                        {ndvi?.ndvi != null ? ndvi.ndvi.toFixed(2) : '—'}
                      </span>
                      <TrendIcon trend={ndvi?.trend} />
                    </div>
                    {/* NDVI bar */}
                    {ndvi?.ndvi != null && (
                      <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="h-2 rounded-full transition-all"
                          style={{
                            width: `${Math.max(0, Math.min(100, ndvi.ndvi * 100))}%`,
                            backgroundColor:
                              ndvi.ndvi >= 0.6
                                ? '#16a34a'
                                : ndvi.ndvi >= 0.4
                                  ? '#ca8a04'
                                  : ndvi.ndvi >= 0.2
                                    ? '#ea580c'
                                    : '#dc2626',
                          }}
                        />
                      </div>
                    )}
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 mb-1">مؤشر مساحة الورقة (LAI)</p>
                    <span className="text-2xl font-bold text-gray-900">
                      {ndvi?.lai != null ? ndvi.lai.toFixed(1) : '—'}
                    </span>
                  </div>
                </div>

                {/* Timestamp */}
                {ndvi?.timestamp && (
                  <p className="text-xs text-gray-400">
                    آخر تحديث: {new Date(ndvi.timestamp).toLocaleDateString('ar')}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ───────────── Bottom Row: Weather + Forecast & KPIs ───────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Current Weather */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
          <div className="px-5 py-3 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <Sun className="w-4 h-4 text-amber-500" />
              الطقس الحالي
            </h2>
          </div>

          <div className="p-5">
            {!hasCoords ? (
              <p className="text-sm text-gray-400 text-center py-8">
                لا توجد إحداثيات لعرض بيانات الطقس
              </p>
            ) : weatherLoading ? (
              <div className="animate-pulse space-y-3">
                <div className="h-12 bg-gray-100 rounded-lg" />
                <div className="grid grid-cols-2 gap-3">
                  <div className="h-16 bg-gray-100 rounded-lg" />
                  <div className="h-16 bg-gray-100 rounded-lg" />
                </div>
              </div>
            ) : weatherError ? (
              <ErrorCard
                message="تعذر تحميل بيانات الطقس"
                onRetry={() => refetchWeather()}
              />
            ) : (
              <div className="space-y-4">
                {/* Temperature highlight */}
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-amber-50 flex items-center justify-center">
                    <Thermometer className="w-7 h-7 text-amber-500" />
                  </div>
                  <div>
                    <p className="text-3xl font-bold text-gray-900">
                      {weather?.temperature_c != null
                        ? `${weather.temperature_c.toFixed(0)}°`
                        : '—'}
                    </p>
                    <p className="text-sm text-gray-500">{weather?.condition ?? ''}</p>
                  </div>
                </div>

                {/* Weather details grid */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-blue-50 rounded-lg p-3 text-center">
                    <Droplets className="w-4 h-4 text-blue-500 mx-auto mb-1" />
                    <p className="text-xs text-gray-500">الرطوبة</p>
                    <p className="text-sm font-semibold text-gray-800">
                      {(weather?.humidity_pct ?? weather?.humidity_percent) != null
                        ? `${weather?.humidity_pct ?? weather?.humidity_percent}%`
                        : '—'}
                    </p>
                  </div>
                  <div className="bg-cyan-50 rounded-lg p-3 text-center">
                    <Wind className="w-4 h-4 text-cyan-500 mx-auto mb-1" />
                    <p className="text-xs text-gray-500">الرياح</p>
                    <p className="text-sm font-semibold text-gray-800">
                      {weather?.wind_speed_kmh != null
                        ? `${weather.wind_speed_kmh.toFixed(0)} كم/س`
                        : '—'}
                    </p>
                  </div>
                  <div className="bg-indigo-50 rounded-lg p-3 text-center">
                    <CloudRain className="w-4 h-4 text-indigo-500 mx-auto mb-1" />
                    <p className="text-xs text-gray-500">المطر</p>
                    <p className="text-sm font-semibold text-gray-800">
                      {(weather as any)?.precipitation_mm != null
                        ? `${(weather as any).precipitation_mm.toFixed(1)} مم`
                        : '—'}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Forecast & Agricultural KPIs */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
          <div className="px-5 py-3 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <Activity className="w-4 h-4 text-violet-500" />
              التوقعات والمؤشرات الزراعية
            </h2>
          </div>

          <div className="p-5 space-y-5">
            {/* 7-day forecast summary */}
            {!hasCoords ? (
              <p className="text-sm text-gray-400 text-center py-4">
                لا توجد إحداثيات
              </p>
            ) : forecastLoading ? (
              <div className="animate-pulse flex gap-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-16 flex-1 bg-gray-100 rounded-lg" />
                ))}
              </div>
            ) : forecastError ? (
              <ErrorCard
                message="تعذر تحميل التوقعات"
                onRetry={() => refetchForecast()}
              />
            ) : (
              <div>
                <p className="text-xs text-gray-500 mb-2">التوقعات - 7 أيام</p>
                <div className="flex gap-2 overflow-x-auto pb-1">
                  {(Array.isArray(forecast) ? forecast : (forecast?.daily ?? forecast?.forecast ?? (forecast?.data as ForecastDay[] | undefined) ?? []))
                    .slice(0, 7)
                    .map((day: ForecastDay, i: number) => (
                      <div
                        key={i}
                        className="flex-shrink-0 w-16 bg-gray-50 rounded-lg p-2 text-center"
                      >
                        <p className="text-[10px] text-gray-400">
                          {day.date
                            ? new Date(day.date).toLocaleDateString('ar', { weekday: 'short' })
                            : `يوم ${i + 1}`}
                        </p>
                        <p className="text-sm font-bold text-gray-800 mt-1">
                          {day.temp_max_c != null
                            ? `${Math.round(day.temp_max_c)}°`
                            : day.temperature_c != null
                              ? `${Math.round(day.temperature_c)}°`
                              : '—'}
                        </p>
                        <p className="text-[10px] text-gray-400">
                          {day.temp_min_c != null ? `${Math.round(day.temp_min_c)}°` : ''}
                        </p>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Agricultural KPIs */}
            {agLoading ? (
              <div className="animate-pulse grid grid-cols-3 gap-3">
                <div className="h-20 bg-gray-100 rounded-lg" />
                <div className="h-20 bg-gray-100 rounded-lg" />
                <div className="h-20 bg-gray-100 rounded-lg" />
              </div>
            ) : agError ? (
              <ErrorCard
                message="تعذر تحميل التقرير الزراعي"
                onRetry={() => refetchAg()}
              />
            ) : agReport ? (
              <div>
                <p className="text-xs text-gray-500 mb-2">المؤشرات الزراعية</p>
                <div className="grid grid-cols-3 gap-3">
                  {/* ET0 */}
                  <div className="bg-orange-50 rounded-lg p-3 text-center">
                    <Thermometer className="w-4 h-4 text-orange-500 mx-auto mb-1" />
                    <p className="text-[10px] text-gray-500">التبخر-نتح (ET0)</p>
                    <p className="text-sm font-bold text-gray-800">
                      {agReport.et0 != null
                        ? `${Number(agReport.et0).toFixed(1)} مم`
                        : agReport.evapotranspiration != null
                          ? `${Number(typeof agReport.evapotranspiration === 'object' ? (agReport.evapotranspiration as { et0?: number }).et0 : agReport.evapotranspiration).toFixed(1)} مم`
                          : '—'}
                    </p>
                  </div>

                  {/* GDD */}
                  <div className="bg-emerald-50 rounded-lg p-3 text-center">
                    <Sprout className="w-4 h-4 text-emerald-500 mx-auto mb-1" />
                    <p className="text-[10px] text-gray-500">وحدات حرارة النمو</p>
                    <p className="text-sm font-bold text-gray-800">
                      {agReport.gdd != null
                        ? `${Number(agReport.gdd).toFixed(0)}`
                        : agReport.growing_degree_days != null
                          ? `${Number(typeof agReport.growing_degree_days === 'object' ? (agReport.growing_degree_days as { gdd?: number }).gdd : agReport.growing_degree_days).toFixed(0)}`
                          : '—'}
                    </p>
                  </div>

                  {/* Spray window */}
                  <div className="bg-sky-50 rounded-lg p-3 text-center">
                    <Droplets className="w-4 h-4 text-sky-500 mx-auto mb-1" />
                    <p className="text-[10px] text-gray-500">نافذة الرش</p>
                    <p className="text-sm font-bold text-gray-800">
                      {(() => {
                        const sw = agReport.spray_window ?? agReport.spray_suitable;
                        if (sw == null) return '—';
                        const ok = typeof sw === 'object' ? (sw as { suitable?: boolean }).suitable : sw;
                        return ok ? 'مناسبة' : 'غير مناسبة';
                      })()}
                    </p>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
