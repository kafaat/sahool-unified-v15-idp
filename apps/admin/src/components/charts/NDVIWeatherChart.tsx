'use client';

/**
 * NDVI + Weather Overlay Chart
 * مخطط NDVI مع الطقس
 *
 * Dual-axis chart: NDVI area fill + precipitation bars + temperature dashed line.
 * Inspired by OneSoil's combined NDVI + Weather visualization.
 */

import { useMemo } from 'react';
import {
  ComposedChart,
  Area,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from 'recharts';
import { cn } from '@/lib/utils';

export interface TimePoint {
  date: string;
  ndvi: number;
  precipitation_mm?: number;
  temperature_c?: number;
  gdd?: number;
}

export interface NDVIWeatherChartProps {
  data: TimePoint[];
  fieldName?: string;
  height?: number;
}

/** Format ISO date string to Arabic locale short date */
function formatDateAr(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ar-YE', { month: 'short', day: 'numeric' });
  } catch {
    return dateStr;
  }
}

/** Map NDVI value to a health label */
function getNDVIStatus(ndvi: number): { label: string; labelAr: string; color: string } {
  if (ndvi >= 0.6) return { label: 'Healthy', labelAr: 'صحي', color: '#10B981' };
  if (ndvi >= 0.4) return { label: 'Moderate', labelAr: 'معتدل', color: '#F59E0B' };
  if (ndvi >= 0.2) return { label: 'Stressed', labelAr: 'مجهد', color: '#EF4444' };
  return { label: 'Critical', labelAr: 'حرج', color: '#991B1B' };
}

/** Custom bilingual tooltip */
function ChartTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload || !payload.length) return null;

  const ndviEntry = payload.find((p) => p.dataKey === 'ndvi');
  const ndviValue = typeof ndviEntry?.value === 'number' ? ndviEntry.value : null;
  const status = ndviValue !== null ? getNDVIStatus(ndviValue) : null;

  return (
    <div className="bg-white dark:bg-gray-800 shadow-lg rounded-xl border border-gray-200 dark:border-gray-700 p-3 min-w-[180px]">
      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">{label}</p>
      <div className="space-y-1.5">
        {payload.map((entry, index) => {
          if (entry.value == null) return null;

          let unit = '';
          let nameAr = entry.name || '';
          if (entry.dataKey === 'ndvi') {
            nameAr = 'مؤشر NDVI';
          } else if (entry.dataKey === 'precipitation_mm') {
            nameAr = 'هطول الأمطار';
            unit = ' مم';
          } else if (entry.dataKey === 'temperature_c') {
            nameAr = 'درجة الحرارة';
            unit = ' °م';
          } else if (entry.dataKey === 'gdd') {
            nameAr = 'وحدات حرارية';
          }

          return (
            <div key={index} className="flex items-center justify-between gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-gray-600 dark:text-gray-400">{nameAr}</span>
              </div>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {typeof entry.value === 'number' ? entry.value.toFixed(entry.dataKey === 'ndvi' ? 2 : 1) : entry.value}
                {unit}
              </span>
            </div>
          );
        })}
        {status && (
          <div className="flex items-center justify-between gap-4 text-sm pt-1 border-t border-gray-200 dark:border-gray-600">
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

export default function NDVIWeatherChart({ data, fieldName, height = 350 }: NDVIWeatherChartProps) {
  /** Pre-process data: add formatted date for X-axis */
  const chartData = useMemo(
    () =>
      data.map((point) => ({
        ...point,
        dateLabel: formatDateAr(point.date),
      })),
    [data]
  );

  /** Compute max precipitation for right Y-axis domain */
  const maxPrecip = useMemo(() => {
    const values = data.map((d) => d.precipitation_mm ?? 0);
    const max = Math.max(...values, 0);
    return Math.max(Math.ceil(max / 10) * 10, 10);
  }, [data]);

  /** Check which optional series have data */
  const hasPrecipitation = useMemo(() => data.some((d) => d.precipitation_mm != null), [data]);
  const hasTemperature = useMemo(() => data.some((d) => d.temperature_c != null), [data]);

  /** Compute summary stats */
  const stats = useMemo(() => {
    const ndviValues = data.map((d) => d.ndvi).filter((v) => v != null);
    if (ndviValues.length === 0) return null;
    const avg = ndviValues.reduce((a, b) => a + b, 0) / ndviValues.length;
    const latest = ndviValues[ndviValues.length - 1] ?? 0;
    return { avg, latest, status: getNDVIStatus(latest) };
  }, [data]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            مؤشر الغطاء النباتي والطقس
          </h3>
          {fieldName && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{fieldName}</p>
          )}
        </div>
        {stats && (
          <div className="text-left flex items-center gap-3">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">NDVI الحالي</p>
              <p className="text-2xl font-bold" style={{ color: stats.status.color }}>
                {stats.latest.toFixed(2)}
              </p>
            </div>
            <div
              className={cn(
                'px-2 py-1 rounded-md text-xs font-medium',
                stats.latest >= 0.6
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                  : stats.latest >= 0.4
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                    : stats.latest >= 0.2
                      ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                      : 'bg-red-200 text-red-900 dark:bg-red-900/50 dark:text-red-300'
              )}
            >
              {stats.status.labelAr}
            </div>
          </div>
        )}
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="ndvi-gradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />

          {/* X-axis: dates */}
          <XAxis
            dataKey="dateLabel"
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={{ stroke: '#E5E7EB' }}
            tickLine={false}
            interval="preserveStartEnd"
          />

          {/* Left Y-axis: NDVI (0-1) */}
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
              value: 'NDVI',
              angle: -90,
              position: 'insideLeft',
              offset: 10,
              style: { fontSize: 11, fill: '#6B7280' },
            }}
          />

          {/* Right Y-axis: Precipitation (mm) */}
          {hasPrecipitation && (
            <YAxis
              yAxisId="precip"
              orientation="right"
              domain={[0, maxPrecip]}
              tick={{ fontSize: 11, fill: '#6B7280' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => `${v}`}
              label={{
                value: 'مم',
                angle: 90,
                position: 'insideRight',
                offset: 10,
                style: { fontSize: 11, fill: '#6B7280' },
              }}
            />
          )}

          <Tooltip content={<ChartTooltip />} />

          <Legend
            wrapperStyle={{ paddingTop: 16 }}
            formatter={(value: string) => {
              const labels: Record<string, string> = {
                ndvi: 'مؤشر NDVI',
                precipitation_mm: 'هطول الأمطار (مم)',
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
              yAxisId="precip"
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
            fill="url(#ndvi-gradient)"
            dot={{ fill: '#10B981', strokeWidth: 0, r: 3 }}
            activeDot={{ r: 5, strokeWidth: 0, fill: '#059669' }}
          />

          {/* Temperature line */}
          {hasTemperature && (
            <Line
              yAxisId="ndvi"
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

      {/* Summary bar */}
      {stats && (
        <div className="flex items-center gap-6 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400">
          <div>
            <span>متوسط NDVI: </span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {stats.avg.toFixed(2)}
            </span>
          </div>
          <div>
            <span>عدد القراءات: </span>
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {data.length.toLocaleString('ar-YE')}
            </span>
          </div>
          {data.length > 0 && (
            <div>
              <span>الفترة: </span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {formatDateAr(data[0]!.date)} - {formatDateAr(data[data.length - 1]!.date)}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
