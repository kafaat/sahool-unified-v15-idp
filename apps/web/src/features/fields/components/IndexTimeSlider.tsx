'use client';

/**
 * Phase 2 — IndexTimeSlider
 * منزلق التاريخ لخريطة المؤشرات — الطور الثاني
 *
 * Date slider that:
 *   1. Shows the available satellite dates as a timeline
 *   2. Colours each date by cloud coverage (green/amber/red)
 *   3. On date change, calls onDateChange → triggers raster reload
 *
 * This resolves the CRITICAL gap:
 *   ❌ Before: a date slider existed in the UI but did NOT reload the raster
 *   ✅  After: every date change propagates through useIndexMap → new tile URL
 *
 * Props consumed from useIndexMap:
 *   - calendar         (CalendarDate[])
 *   - calendarLoading
 *   - selectedDate
 *   - setSelectedDate
 */

import { useId, useMemo, useRef } from 'react';
import type { CalendarDate } from '@/features/ndvi/hooks/useIndexMap';

export interface IndexTimeSliderProps {
  /** Calendar dates returned by useIndexMap */
  calendar: CalendarDate[] | undefined;
  calendarLoading: boolean;
  /** Currently selected ISO date string */
  selectedDate: string | undefined;
  /** Called when user selects a new date — triggers raster reload */
  onDateChange: (date: string) => void;
  /** 'rtl' | 'ltr' */
  dir?: 'rtl' | 'ltr';
  className?: string;
}

function cloudColor(date: CalendarDate): { dot: string; label: string } {
  if (!date.usable || date.cloudCoverPercent > 40) {
    return { dot: 'bg-red-400', label: 'text-red-600 dark:text-red-400' };
  }
  if (date.cloudCoverPercent > 20) {
    return { dot: 'bg-amber-400', label: 'text-amber-600 dark:text-amber-400' };
  }
  return { dot: 'bg-green-500', label: 'text-green-700 dark:text-green-400' };
}

function formatDate(iso: string, isRtl: boolean): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(isRtl ? 'ar-YE' : 'en-GB', {
      day: '2-digit',
      month: 'short',
    });
  } catch {
    return iso;
  }
}

export function IndexTimeSlider({
  calendar,
  calendarLoading,
  selectedDate,
  onDateChange,
  dir = 'ltr',
  className = '',
}: IndexTimeSliderProps) {
  const sliderId = useId();
  const isRtl = dir === 'rtl';
  const containerRef = useRef<HTMLDivElement>(null);

  // Hooks must be declared before any early returns (Rules of Hooks).
  const allDates = calendar ?? [];
  const usableDates = useMemo(() => allDates.filter((d) => d.usable), [allDates]);
  const selectedIdx = useMemo(
    () => allDates.findIndex((d) => d.date === selectedDate),
    [allDates, selectedDate],
  );

  if (calendarLoading) {
    return (
      <div className={`animate-pulse rounded-lg bg-gray-100 dark:bg-gray-800 h-16 ${className}`} />
    );
  }

  if (!calendar || calendar.length === 0) {
    return (
      <p className={`text-sm text-gray-500 dark:text-gray-400 ${className}`}>
        {isRtl ? 'لا توجد بيانات تاريخية متاحة' : 'No historical dates available'}
      </p>
    );
  }

  function handleSliderChange(e: React.ChangeEvent<HTMLInputElement>) {
    const idx = parseInt(e.target.value, 10);
    if (!isNaN(idx) && idx >= 0 && idx < allDates.length) {
      onDateChange(allDates[idx]!.date);
      // Scroll the dot into view
      const dot = containerRef.current?.querySelector(`[data-date-idx="${idx}"]`);
      dot?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }
  }

  return (
    <div dir={dir} className={`space-y-2 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <span id={`${sliderId}-label`}>
          {isRtl ? 'تاريخ الصورة' : 'Image date'}
        </span>
        <span className="flex items-center gap-2">
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-green-500" aria-hidden />
            {isRtl ? 'جيد' : 'Clear'}
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-amber-400" aria-hidden />
            {isRtl ? 'جزئي' : 'Partial'}
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-red-400" aria-hidden />
            {isRtl ? 'سحابي' : 'Cloudy'}
          </span>
        </span>
      </div>

      {/* Timeline dot strip */}
      <div
        ref={containerRef}
        className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin scrollbar-thumb-gray-300"
      >
        {allDates.map((d, idx) => {
          const colors = cloudColor(d);
          const isSelected = d.date === selectedDate;
          return (
            <button
              key={d.date}
              data-date-idx={idx}
              onClick={() => onDateChange(d.date)}
              title={`${d.date} — ⛅ ${d.cloudCoverPercent.toFixed(0)}%${!d.usable ? ' (⚠ cloudy)' : ''}`}
              aria-label={`${isRtl ? 'تاريخ' : 'Date'} ${formatDate(d.date, isRtl)} — ${d.cloudCoverPercent.toFixed(0)}% ${isRtl ? 'سحاب' : 'cloud'}`}
              aria-pressed={isSelected}
              className={[
                'relative flex-shrink-0 flex flex-col items-center rounded-md border px-1.5 py-1 transition-all',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-green-500',
                isSelected
                  ? 'border-green-600 bg-green-50 dark:border-green-400 dark:bg-green-900/30 shadow-sm'
                  : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600',
              ].join(' ')}
            >
              {/* Cloud quality dot */}
              <span className={`h-2 w-2 rounded-full ${colors.dot}`} aria-hidden />
              {/* Short date label */}
              <span className={`mt-0.5 text-[9px] whitespace-nowrap font-mono ${isSelected ? 'text-green-700 dark:text-green-300 font-bold' : colors.label}`}>
                {formatDate(d.date, isRtl)}
              </span>
            </button>
          );
        })}
      </div>

      {/* Range input for keyboard/mouse drag — CONNECTED to raster reload */}
      <input
        type="range"
        id={sliderId}
        aria-labelledby={`${sliderId}-label`}
        min={0}
        max={allDates.length - 1}
        value={selectedIdx < 0 ? allDates.length - 1 : selectedIdx}
        step={1}
        onChange={handleSliderChange}
        className="w-full h-1.5 rounded-full accent-green-600 cursor-pointer"
        aria-valuetext={selectedDate ? formatDate(selectedDate, isRtl) : ''}
      />

      {/* Selected date details */}
      {selectedDate && (() => {
        const sel = allDates.find((d) => d.date === selectedDate);
        if (!sel) return null;
        const colors = cloudColor(sel);
        return (
          <div className="flex items-center gap-2 text-xs">
            <span className={`font-medium ${colors.label}`}>
              {formatDate(sel.date, isRtl)}
            </span>
            <span className="text-gray-400">|</span>
            <span className={colors.label}>
              ⛅ {sel.cloudCoverPercent.toFixed(0)}% {isRtl ? 'سحاب' : 'cloud'}
            </span>
            {!sel.usable && (
              <span className="text-red-600 dark:text-red-400 font-medium">
                ⚠ {isRtl ? 'قد تكون القيم غير موثوقة' : 'values may be unreliable'}
              </span>
            )}
          </div>
        );
      })()}

      {/* Summary */}
      <p className="text-[10px] text-gray-400 dark:text-gray-500">
        {usableDates.length} / {allDates.length}{' '}
        {isRtl ? 'تاريخ صافٍ من السحاب' : 'dates with acceptable cloud cover'}
      </p>
    </div>
  );
}
