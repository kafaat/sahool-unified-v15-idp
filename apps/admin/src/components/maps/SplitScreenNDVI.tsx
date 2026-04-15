'use client';
// Split Screen NDVI Comparison — مقارنة NDVI بشاشة مقسومة
// Shows same field at two dates for visual change detection

import { useMemo } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface NDVISnapshot {
  date: string;
  ndviMean: number;
  healthStatus: string;
  healthStatusAr: string;
  cloudCoverPct: number;
  dataSource: string;
}

interface SplitScreenNDVIProps {
  fieldId: string;
  fieldName: string;
  leftSnapshot: NDVISnapshot;
  rightSnapshot: NDVISnapshot;
  onDateChange?: (side: 'left' | 'right', date: string) => void;
}

// ---------------------------------------------------------------------------
// NDVI 8-color scale (low → high)
// ---------------------------------------------------------------------------

const NDVI_COLOR_SCALE = [
  { min: -1.0, max: 0.0, color: '#d73027', label: 'Bare / Water', labelAr: 'تربة / ماء' },
  { min: 0.0, max: 0.1, color: '#f46d43', label: 'Very Low', labelAr: 'منخفض جداً' },
  { min: 0.1, max: 0.2, color: '#fdae61', label: 'Low', labelAr: 'منخفض' },
  { min: 0.2, max: 0.3, color: '#fee08b', label: 'Sparse', labelAr: 'متناثر' },
  { min: 0.3, max: 0.4, color: '#d9ef8b', label: 'Moderate-Low', labelAr: 'معتدل منخفض' },
  { min: 0.4, max: 0.6, color: '#a6d96a', label: 'Moderate', labelAr: 'معتدل' },
  { min: 0.6, max: 0.8, color: '#66bd63', label: 'Healthy', labelAr: 'صحي' },
  { min: 0.8, max: 1.0, color: '#1a9850', label: 'Very Healthy', labelAr: 'صحي جداً' },
] as const;

function getNDVIColor(value: number): (typeof NDVI_COLOR_SCALE)[number] {
  const clamped = Math.max(-1, Math.min(1, value));
  for (let i = NDVI_COLOR_SCALE.length - 1; i >= 0; i--) {
    const entry = NDVI_COLOR_SCALE[i];
    if (entry && clamped >= entry.min) {
      return entry;
    }
  }
  return NDVI_COLOR_SCALE[0];
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-CA'); // YYYY-MM-DD
  } catch {
    return dateStr;
  }
}

function formatDateAr(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('ar-SA', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function getTrendArrow(delta: number): string {
  if (delta > 0.02) return '\u2191'; // ↑
  if (delta < -0.02) return '\u2193'; // ↓
  return '\u2194'; // ↔
}

function getTrendLabel(delta: number): { en: string; ar: string } {
  if (delta > 0.1) return { en: 'Significant improvement', ar: '\u062A\u062D\u0633\u0646 \u0645\u0644\u062D\u0648\u0638' };
  if (delta > 0.02) return { en: 'Slight improvement', ar: '\u062A\u062D\u0633\u0646 \u0637\u0641\u064A\u0641' };
  if (delta < -0.1) return { en: 'Significant decline', ar: '\u062A\u0631\u0627\u062C\u0639 \u0645\u0644\u062D\u0648\u0638' };
  if (delta < -0.02) return { en: 'Slight decline', ar: '\u062A\u0631\u0627\u062C\u0639 \u0637\u0641\u064A\u0641' };
  return { en: 'Stable', ar: '\u0645\u0633\u062A\u0642\u0631' };
}

function getTrendColor(delta: number): string {
  if (delta > 0.02) return 'text-green-600 dark:text-green-400';
  if (delta < -0.02) return 'text-red-600 dark:text-red-400';
  return 'text-gray-600 dark:text-gray-400';
}

function daysBetween(a: string, b: string): number {
  try {
    const msPerDay = 86_400_000;
    return Math.round(
      Math.abs(new Date(b).getTime() - new Date(a).getTime()) / msPerDay,
    );
  } catch {
    return 0;
  }
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function NDVIPanel({
  snapshot,
  side,
  onDateChange,
}: {
  snapshot: NDVISnapshot;
  side: 'left' | 'right';
  onDateChange?: (side: 'left' | 'right', date: string) => void;
}) {
  const colorEntry = getNDVIColor(snapshot.ndviMean);

  return (
    <div className="flex flex-1 flex-col gap-3 rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
      {/* Date selector */}
      <div className="flex items-center justify-between gap-2">
        <input
          type="date"
          value={formatDate(snapshot.date)}
          onChange={(e) => onDateChange?.(side, e.target.value)}
          className="rounded-lg border border-gray-300 bg-gray-50 px-3 py-1.5 text-sm text-gray-700 focus:border-sahool-500 focus:outline-none focus:ring-1 focus:ring-sahool-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"
          dir="ltr"
        />
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {formatDateAr(snapshot.date)}
        </span>
      </div>

      {/* NDVI value + health status */}
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-bold text-gray-900 dark:text-white" dir="ltr">
          {snapshot.ndviMean.toFixed(2)}
        </span>
        <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
          ({snapshot.healthStatusAr})
        </span>
      </div>

      {/* Large NDVI color block */}
      <div
        className="flex min-h-[140px] flex-1 items-center justify-center rounded-lg sm:min-h-[180px]"
        style={{ backgroundColor: colorEntry.color }}
      >
        <div className="rounded-md bg-black/30 px-4 py-2 text-center backdrop-blur-sm">
          <p className="text-lg font-bold text-white" dir="ltr">
            NDVI {snapshot.ndviMean.toFixed(2)}
          </p>
          <p className="text-sm text-white/90">
            {colorEntry.labelAr} &mdash; {colorEntry.label}
          </p>
        </div>
      </div>

      {/* Cloud cover + data source */}
      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <span dir="ltr">
          \u2601\uFE0F {snapshot.cloudCoverPct}%
          <span className="mr-1 text-gray-400"> \u063A\u0637\u0627\u0621 \u0633\u062D\u0627\u0628\u064A</span>
        </span>
        <span className="rounded bg-gray-100 px-2 py-0.5 dark:bg-gray-700">
          {snapshot.dataSource}
        </span>
      </div>
    </div>
  );
}

function ColorScaleLegend() {
  return (
    <div className="flex items-center gap-1 overflow-x-auto py-1" dir="ltr">
      {NDVI_COLOR_SCALE.map((entry) => (
        <div key={entry.label} className="flex flex-col items-center">
          <div
            className="h-3 w-6 rounded-sm sm:w-8"
            style={{ backgroundColor: entry.color }}
            title={`${entry.label} (${entry.min.toFixed(1)} – ${entry.max.toFixed(1)})`}
          />
          <span className="mt-0.5 text-[9px] leading-tight text-gray-400">
            {entry.min.toFixed(1)}
          </span>
        </div>
      ))}
      <span className="mr-1 text-[9px] text-gray-400">1.0</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function SplitScreenNDVI({
  fieldId,
  fieldName,
  leftSnapshot,
  rightSnapshot,
  onDateChange,
}: SplitScreenNDVIProps) {
  const delta = useMemo(
    () => rightSnapshot.ndviMean - leftSnapshot.ndviMean,
    [leftSnapshot.ndviMean, rightSnapshot.ndviMean],
  );

  const pctChange = useMemo(() => {
    if (leftSnapshot.ndviMean === 0) return 0;
    return (delta / Math.abs(leftSnapshot.ndviMean)) * 100;
  }, [delta, leftSnapshot.ndviMean]);

  const days = useMemo(
    () => daysBetween(leftSnapshot.date, rightSnapshot.date),
    [leftSnapshot.date, rightSnapshot.date],
  );

  const trendLabel = getTrendLabel(delta);
  const trendArrow = getTrendArrow(delta);
  const trendColor = getTrendColor(delta);

  return (
    <section
      dir="rtl"
      data-field-id={fieldId}
      className="w-full rounded-2xl border border-gray-200 bg-gray-50 shadow-sm dark:border-gray-700 dark:bg-gray-900"
    >
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-200 px-5 py-3 dark:border-gray-700">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white">
          {fieldName}
          <span className="mr-2 text-sm font-normal text-gray-500 dark:text-gray-400">
            — \u0645\u0642\u0627\u0631\u0646\u0629 NDVI
          </span>
        </h3>
        <span className="rounded-md bg-gray-200 px-2 py-0.5 text-xs text-gray-600 dark:bg-gray-700 dark:text-gray-300" dir="ltr">
          {fieldId}
        </span>
      </div>

      {/* Split panels */}
      <div className="flex flex-col gap-3 p-4 sm:flex-row">
        <NDVIPanel
          snapshot={leftSnapshot}
          side="left"
          onDateChange={onDateChange}
        />
        <NDVIPanel
          snapshot={rightSnapshot}
          side="right"
          onDateChange={onDateChange}
        />
      </div>

      {/* Color scale legend */}
      <div className="flex justify-center px-4">
        <ColorScaleLegend />
      </div>

      {/* Change summary bar */}
      <div className="mx-4 mb-4 mt-2 rounded-xl border border-gray-200 bg-white px-5 py-3 dark:border-gray-700 dark:bg-gray-800">
        <div className="flex flex-col items-center gap-1 text-center sm:flex-row sm:justify-between sm:text-start">
          {/* Arabic summary */}
          <p className="text-sm font-medium text-gray-800 dark:text-gray-200">
            <span className="ml-1 text-gray-500">\u0627\u0644\u062A\u063A\u064A\u0631:</span>
            <span className={`mx-1 font-bold ${trendColor}`} dir="ltr">
              {delta >= 0 ? '+' : ''}{delta.toFixed(2)}
            </span>
            <span className={`${trendColor}`}>
              ({trendArrow} {Math.abs(pctChange).toFixed(0)}%)
            </span>
            <span className="mx-1">&mdash;</span>
            <span className={trendColor}>{trendLabel.ar}</span>
          </p>

          {/* English summary */}
          <p className="text-xs text-gray-500 dark:text-gray-400" dir="ltr">
            &Delta; = {delta >= 0 ? '+' : ''}{delta.toFixed(2)} NDVI over{' '}
            {days > 0 ? (
              <>
                {days} day{days !== 1 ? 's' : ''}
              </>
            ) : (
              'same date'
            )}
            {' '}&mdash; {trendLabel.en}
          </p>
        </div>
      </div>
    </section>
  );
}
