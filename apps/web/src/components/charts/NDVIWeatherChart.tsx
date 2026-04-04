'use client';

/**
 * NDVI + Weather Dual-Axis Chart — مخطط NDVI والطقس
 *
 * Dual-axis composed chart: NDVI area fill (left axis) + rainfall bars +
 * temperature dashed line (right axis). Includes date range selector and
 * bilingual Arabic/English tooltips.
 */

import { useState, useMemo, useCallback } from 'react';
import { Calendar, TrendingUp, Droplets } from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface TimePoint {
  date: string; // ISO date string
  ndvi: number;
  precipitation_mm?: number;
  temperature_c?: number;
}

type DateRange = '7d' | '30d' | '90d' | '180d' | 'all';

export interface NDVIWeatherChartProps {
  data: TimePoint[];
  fieldName?: string;
  fieldNameAr?: string;
  height?: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const DATE_RANGE_LABELS: Record<DateRange, { ar: string; en: string }> = {
  '7d': { ar: '٧ ايام', en: '7d' },
  '30d': { ar: '٣٠ يوم', en: '30d' },
  '90d': { ar: '٣ اشهر', en: '90d' },
  '180d': { ar: '٦ اشهر', en: '180d' },
  all: { ar: 'الكل', en: 'All' },
};

const RANGE_DAYS: Record<DateRange, number | null> = {
  '7d': 7,
  '30d': 30,
  '90d': 90,
  '180d': 180,
  all: null,
};

function formatDateAr(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('ar-YE', {
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function getNDVIStatus(ndvi: number): {
  labelAr: string;
  label: string;
  color: string;
} {
  if (ndvi >= 0.6) return { label: 'Healthy', labelAr: 'صحي', color: '#10B981' };
  if (ndvi >= 0.4) return { label: 'Moderate', labelAr: 'معتدل', color: '#F59E0B' };
  if (ndvi >= 0.2) return { label: 'Stressed', labelAr: 'مجهد', color: '#EF4444' };
  return { label: 'Critical', labelAr: 'حرج', color: '#991B1B' };
}

function statusBadgeClasses(ndvi: number): string {
  if (ndvi >= 0.6) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
  if (ndvi >= 0.4) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
  if (ndvi >= 0.2) return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
  return 'bg-red-200 text-red-900 dark:bg-red-900/50 dark:text-red-300';
}

// ---------------------------------------------------------------------------
// Custom Tooltip
// ---------------------------------------------------------------------------

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ dataKey: string; value?: number; color?: string; name?: string }>;
  label?: string;
}) {
  if (!active || !payload || payload.length === 0) return null;

  const ndviEntry = payload.find((p) => p.dataKey === 'ndvi');
  const ndviValue = typeof ndviEntry?.value === 'number' ? ndviEntry.value : null;
  const status = ndviValue !== null ? getNDVIStatus(ndviValue) : null;

  const LABELS: Record<string, { ar: string; unit: string }> = {
    ndvi: { ar: 'مؤشر NDVI', unit: '' },
    precipitation_mm: { ar: 'هطول الامطار', unit: ' مم' },
    temperature_c: { ar: 'درجة الحرارة', unit: ' °م' },
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-3 shadow-lg dark:border-gray-700 dark:bg-gray-800 min-w-[200px]">
      <p className="mb-2 text-sm font-medium text-gray-900 dark:text-gray-100">
        {label}
      </p>
      <div className="space-y-1.5">
        {payload.map((entry, i) => {
          if (entry.value == null) return null;
          const info = LABELS[entry.dataKey] ?? { ar: entry.dataKey, unit: '' };
          return (
            <div
              key={i}
              className="flex items-center justify-between gap-4 text-sm"
            >
              <div className="flex items-center gap-2">
                <div
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-gray-600 dark:text-gray-400">
                  {info.ar}
                </span>
              </div>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {entry.dataKey === 'ndvi'
                  ? entry.value.toFixed(2)
                  : entry.value.toFixed(1)}
                {info.unit}
              </span>
            </div>
          );
        })}
        {status && (
          <div className="flex items-center justify-between gap-4 border-t border-gray-200 pt-1 text-sm dark:border-gray-600">
            <span className="text-gray-600 dark:text-gray-400">الحالة</span>
            <span className="font-medium" style={{ color: status.color }}>
              {status.labelAr}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function NDVIWeatherChart({
  data,
  fieldName,
  fieldNameAr,
  height = 360,
}: NDVIWeatherChartProps) {
  const [range, setRange] = useState<DateRange>('all');

  // Filter data by date range
  const filteredData = useMemo(() => {
    const days = RANGE_DAYS[range];
    if (!days || data.length === 0) return data;
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    return data.filter((d) => new Date(d.date) >= cutoff);
  }, [data, range]);

  // Prepare chart data with formatted date labels
  const chartData = useMemo(
    () => filteredData.map((p) => ({ ...p, dateLabel: formatDateAr(p.date) })),
    [filteredData]
  );

  // Max precipitation for right axis
  const maxPrecip = useMemo(() => {
    const max = Math.max(...filteredData.map((d) => d.precipitation_mm ?? 0), 0);
    return Math.max(Math.ceil(max / 10) * 10, 10);
  }, [filteredData]);

  // Feature flags
  const hasPrecipitation = useMemo(
    () => filteredData.some((d) => d.precipitation_mm != null),
    [filteredData]
  );
  const hasTemperature = useMemo(
    () => filteredData.some((d) => d.temperature_c != null),
    [filteredData]
  );

  // Summary statistics
  const stats = useMemo(() => {
    const ndviValues = filteredData.map((d) => d.ndvi).filter((v) => v != null);
    if (ndviValues.length === 0) return null;
    const avg = ndviValues.reduce((a, b) => a + b, 0) / ndviValues.length;
    const latest = ndviValues[ndviValues.length - 1] ?? 0;
    const min = Math.min(...ndviValues);
    const max = Math.max(...ndviValues);
    const totalRain = filteredData.reduce(
      (s, d) => s + (d.precipitation_mm ?? 0),
      0
    );
    return { avg, latest, min, max, totalRain, status: getNDVIStatus(latest) };
  }, [filteredData]);

  const handleRangeChange = useCallback((r: DateRange) => setRange(r), []);

  return (
    <div
      dir="rtl"
      className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800"
    >
      {/* Header */}
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            مؤشر الغطاء النباتي والطقس
          </h3>
          {(fieldNameAr || fieldName) && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {fieldNameAr ?? fieldName}
            </p>
          )}
        </div>

        {stats && (
          <div className="flex items-center gap-3">
            <div className="text-left">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                NDVI الحالي
              </p>
              <p
                className="text-2xl font-bold"
                style={{ color: stats.status.color }}
              >
                {stats.latest.toFixed(2)}
              </p>
            </div>
            <span
              className={`rounded-md px-2 py-1 text-xs font-medium ${statusBadgeClasses(stats.latest)}`}
            >
              {stats.status.labelAr}
            </span>
          </div>
        )}
      </div>

      {/* Date Range Selector */}
      <div className="mb-4 flex items-center gap-2">
        <Calendar className="h-4 w-4 text-gray-400" />
        <div className="flex gap-1 rounded-lg bg-gray-100 p-0.5 dark:bg-gray-700">
          {(Object.keys(DATE_RANGE_LABELS) as DateRange[]).map((key) => (
            <button
              key={key}
              onClick={() => handleRangeChange(key)}
              className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
                range === key
                  ? 'bg-white text-gray-900 shadow-sm dark:bg-gray-600 dark:text-gray-100'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              {DATE_RANGE_LABELS[key].ar}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={chartData}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <defs>
            <linearGradient id="web-ndvi-grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#E5E7EB"
            vertical={false}
          />

          <XAxis
            dataKey="dateLabel"
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={{ stroke: '#E5E7EB' }}
            tickLine={false}
            interval="preserveStartEnd"
          />

          {/* Left axis: NDVI */}
          <YAxis
            yAxisId="ndvi"
            orientation="left"
            domain={[0, 1]}
            ticks={[0, 0.2, 0.4, 0.6, 0.8, 1.0]}
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => v.toFixed(1)}
            label={{
              value: 'م.غ.ن (NDVI)',
              angle: -90,
              position: 'insideLeft',
              offset: 10,
              style: { fontSize: 11, fill: '#6B7280' },
            }}
          />

          {/* Right axis: Precipitation / Temperature */}
          {(hasPrecipitation || hasTemperature) && (
            <YAxis
              yAxisId="weather"
              orientation="right"
              domain={[0, maxPrecip]}
              tick={{ fontSize: 11, fill: '#6B7280' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => `${v}`}
              label={{
                value: 'هطول (مم) / حرارة (°م)',
                angle: 90,
                position: 'insideRight',
                offset: 15,
                style: { fontSize: 10, fill: '#6B7280' },
              }}
            />
          )}

          <Tooltip content={<ChartTooltip />} />

          <Legend
            wrapperStyle={{ paddingTop: 16 }}
            formatter={(value: string) => {
              const labels: Record<string, string> = {
                ndvi: 'مؤشر NDVI',
                precipitation_mm: 'هطول الامطار (مم)',
                temperature_c: 'درجة الحرارة (°م)',
              };
              return (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {labels[value] ?? value}
                </span>
              );
            }}
          />

          {/* Precipitation bars */}
          {hasPrecipitation && (
            <Bar
              yAxisId="weather"
              dataKey="precipitation_mm"
              name="precipitation_mm"
              fill="#3B82F6"
              fillOpacity={0.6}
              radius={[2, 2, 0, 0]}
              barSize={12}
            />
          )}

          {/* NDVI area */}
          <Area
            yAxisId="ndvi"
            type="monotone"
            dataKey="ndvi"
            name="ndvi"
            stroke="#10B981"
            strokeWidth={2.5}
            fill="url(#web-ndvi-grad)"
            dot={{ fill: '#10B981', strokeWidth: 0, r: 3 }}
            activeDot={{ r: 5, strokeWidth: 0, fill: '#059669' }}
          />

          {/* Temperature line */}
          {hasTemperature && (
            <Line
              yAxisId="weather"
              type="monotone"
              dataKey="temperature_c"
              name="temperature_c"
              stroke="#F97316"
              strokeWidth={2}
              strokeDasharray="6 3"
              dot={false}
              activeDot={{ r: 4, fill: '#F97316', strokeWidth: 0 }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Summary Stats Bar */}
      {stats && (
        <div className="mt-4 flex flex-wrap items-center gap-5 border-t border-gray-100 pt-4 text-sm text-gray-600 dark:border-gray-700 dark:text-gray-400">
          <div className="flex items-center gap-1.5">
            <TrendingUp className="h-4 w-4 text-green-500" />
            <span>متوسط NDVI:</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {stats.avg.toFixed(2)}
            </span>
          </div>
          <div>
            <span>الحد الادنى: </span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {stats.min.toFixed(2)}
            </span>
            <span className="mx-1">-</span>
            <span>الاعلى: </span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {stats.max.toFixed(2)}
            </span>
          </div>
          {hasPrecipitation && (
            <div className="flex items-center gap-1.5">
              <Droplets className="h-4 w-4 text-blue-500" />
              <span>اجمالي الهطول:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {stats.totalRain.toFixed(1)} مم
              </span>
            </div>
          )}
          <div>
            <span>عدد القراءات: </span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {filteredData.length.toLocaleString('ar-YE')}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
