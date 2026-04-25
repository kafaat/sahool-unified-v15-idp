'use client';

/**
 * IndexTimeSlider — unified time navigation for the map view.
 * شريط زمني موحَّد للتنقل عبر تواريخ المؤشرات
 *
 * Replaces the previous pattern of "chart on one screen, map on
 * another". Sits below the map, renders the set of available
 * acquisition dates as tick marks, and emits `onChange(date)` so the
 * parent can pipe the same date into the tile layer, the legend, and
 * the pixel inspector simultaneously — the EOSDA "time scrubber"
 * pattern.
 *
 * Does NOT fetch anything itself; parent supplies the date list (usually
 * from `useIndexTimeSeries` or `useNDVITimeSeries`). Renders compact
 * previous/next buttons + a native range input so the control works on
 * mobile and with keyboards.
 */

import { useCallback, useMemo } from 'react';

export interface IndexTimeSliderProps {
  /** ISO date strings (YYYY-MM-DD) in chronological order. */
  dates: string[];
  /** Currently selected date (must be one of `dates`). */
  value: string;
  onChange: (date: string) => void;
  className?: string;
  /** Disable while tiles are loading. */
  disabled?: boolean;
}

function formatCompact(iso: string): string {
  // "2026-04-12" -> "12 Apr"
  const d = new Date(iso);
  if (Number.isNaN(d.valueOf())) return iso;
  return d.toLocaleDateString('en', { day: '2-digit', month: 'short' });
}

export const IndexTimeSlider: React.FC<IndexTimeSliderProps> = ({
  dates,
  value,
  onChange,
  className = '',
  disabled = false,
}) => {
  const sorted = useMemo(() => [...dates].sort(), [dates]);
  const currentIdx = Math.max(0, sorted.indexOf(value));

  const go = useCallback(
    (nextIdx: number) => {
      if (disabled || sorted.length === 0) return;
      const bounded = Math.max(0, Math.min(sorted.length - 1, nextIdx));
      const nextDate = sorted[bounded];
      if (nextDate && nextDate !== value) onChange(nextDate);
    },
    [disabled, sorted, value, onChange]
  );

  if (sorted.length === 0) {
    return (
      <div
        className={`flex items-center justify-center text-xs text-gray-400 py-2 ${className}`}
        data-testid="index-time-slider-empty"
      >
        No acquisitions available · لا توجد بيانات
      </div>
    );
  }

  return (
    <div
      role="group"
      aria-label="Time slider for vegetation index acquisitions"
      data-testid="index-time-slider"
      className={[
        'flex items-center gap-3 bg-white/95 backdrop-blur-sm rounded-lg shadow px-3 py-2',
        className,
      ].join(' ')}
    >
      <button
        type="button"
        aria-label="Previous acquisition | السابق"
        data-testid="index-time-prev"
        disabled={disabled || currentIdx <= 0}
        onClick={() => go(currentIdx - 1)}
        className={[
          'rounded-full h-7 w-7 flex items-center justify-center text-sm',
          disabled || currentIdx <= 0
            ? 'text-gray-300 cursor-not-allowed'
            : 'text-gray-700 hover:bg-gray-100',
        ].join(' ')}
      >
        ‹
      </button>

      <div className="flex-1 min-w-[12rem]">
        <input
          type="range"
          min={0}
          max={sorted.length - 1}
          step={1}
          value={currentIdx}
          onChange={(e) => go(Number(e.target.value))}
          disabled={disabled}
          aria-label="Select acquisition date"
          aria-valuemin={0}
          aria-valuemax={sorted.length - 1}
          aria-valuenow={currentIdx}
          aria-valuetext={sorted[currentIdx]}
          data-testid="index-time-range"
          className="w-full accent-green-600 disabled:opacity-50"
        />
        <div className="flex justify-between text-[10px] text-gray-500 mt-0.5">
          <span>{formatCompact(sorted[0] ?? '')}</span>
          <span
            className="font-semibold text-gray-800"
            data-testid="index-time-current"
            aria-live="polite"
          >
            {formatCompact(sorted[currentIdx] ?? '')}
          </span>
          <span>{formatCompact(sorted[sorted.length - 1] ?? '')}</span>
        </div>
      </div>

      <button
        type="button"
        aria-label="Next acquisition | التالي"
        data-testid="index-time-next"
        disabled={disabled || currentIdx >= sorted.length - 1}
        onClick={() => go(currentIdx + 1)}
        className={[
          'rounded-full h-7 w-7 flex items-center justify-center text-sm',
          disabled || currentIdx >= sorted.length - 1
            ? 'text-gray-300 cursor-not-allowed'
            : 'text-gray-700 hover:bg-gray-100',
        ].join(' ')}
      >
        ›
      </button>
    </div>
  );
};

export default IndexTimeSlider;
