'use client';

/**
 * SatelliteTimeline — horizontal scrollable timeline for Sentinel-2 acquisition dates
 * شريط الجدول الزمني — يعرض تواريخ اقتناء Sentinel-2 مجمّعة شهرياً
 *
 * - Groups date pills by month/year with separator labels
 * - Shows cloud cover badge when available from CDSE catalog
 * - Horizontally scrollable with smooth scroll
 * - "الأحدث" (Latest) always pinned at left
 */

import React, { useRef } from 'react';
import { Calendar, Cloud, Loader2 } from 'lucide-react';
import type { TimeseriesEntry } from '../hooks/useTimeseriesLayers';

interface Props {
  dates: TimeseriesEntry[];
  activeDate: string | null;
  onDateChange: (date: string | null) => void;
  loading?: boolean;
  hidden?: boolean;
}

interface MonthGroup {
  key: string;       // e.g. "2026-03"
  label: string;     // e.g. "مارس 2026"
  entries: TimeseriesEntry[];
}

function groupByMonth(dates: TimeseriesEntry[]): MonthGroup[] {
  const map = new Map<string, TimeseriesEntry[]>();
  for (const entry of dates) {
    const key = entry.date.slice(0, 7); // "YYYY-MM"
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(entry);
  }
  return Array.from(map.entries()).map(([key, entries]) => {
    const [year, month] = key.split('-').map(Number);
    const label = new Date(year!, month! - 1, 1).toLocaleDateString('ar-SA', {
      month: 'long',
      year: 'numeric',
    });
    return { key, label, entries };
  });
}

function cloudBadge(cc: number | undefined): React.ReactNode {
  if (cc == null) return null;
  const color = cc <= 10 ? 'bg-green-500' : cc <= 30 ? 'bg-yellow-400' : cc <= 60 ? 'bg-orange-400' : 'bg-red-400';
  return (
    <span className={`absolute -top-1 -right-1 ${color} text-white text-[8px] font-bold px-0.5 rounded-full leading-none`}>
      {Math.round(cc)}%
    </span>
  );
}

function formatDay(isoDate: string): string {
  const d = new Date(isoDate + 'T00:00:00Z');
  if (isNaN(d.getTime())) return isoDate;
  return d.toLocaleDateString('ar-SA', { day: 'numeric', month: 'short', timeZone: 'UTC' });
}

export function SatelliteTimeline({ dates, activeDate, onDateChange, loading, hidden }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);

  if (hidden) return null;

  const groups = groupByMonth(dates);

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-white/95 backdrop-blur-sm border-t border-gray-100">
      <Calendar className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />

      <div
        ref={scrollRef}
        className="flex items-center gap-1 overflow-x-auto scrollbar-none flex-1 min-w-0 scroll-smooth"
      >
        {/* "Latest" pill — always first */}
        <button
          onClick={() => onDateChange(null)}
          className={`flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-semibold transition-colors whitespace-nowrap ${
            activeDate === null
              ? 'bg-green-600 text-white shadow'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          الأحدث
        </button>

        {loading && <Loader2 className="w-3.5 h-3.5 text-gray-400 animate-spin flex-shrink-0 ml-1" />}

        {/* Month groups — most-recent first */}
        {groups.map((group) => (
          <React.Fragment key={group.key}>
            {/* Month separator */}
            <span className="flex-shrink-0 text-[9px] font-semibold text-gray-400 px-1.5 border-l border-gray-200 ml-1 whitespace-nowrap">
              {group.label}
            </span>

            {/* Date pills within this month */}
            {group.entries.map((entry) => {
              const isActive = activeDate === entry.date;
              return (
                <button
                  key={entry.date}
                  onClick={() => onDateChange(entry.date)}
                  title={`${entry.date}${entry.cloudCover != null ? ` · ${Math.round(entry.cloudCover)}% غيوم` : ''}`}
                  className={`relative flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-medium transition-all whitespace-nowrap ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md scale-105'
                      : 'bg-gray-100 text-gray-600 hover:bg-blue-50 hover:text-blue-700'
                  }`}
                >
                  {formatDay(entry.date)}
                  {cloudBadge(entry.cloudCover)}
                </button>
              );
            })}
          </React.Fragment>
        ))}

        {dates.length === 0 && !loading && (
          <span className="text-xs text-gray-400 px-2">لا توجد صور متاحة</span>
        )}
      </div>

      {/* Summary */}
      <span className="text-[10px] text-gray-400 flex-shrink-0 hidden sm:block whitespace-nowrap">
        {dates.length > 0 ? `${dates.length} مشهد` : ''}
      </span>
    </div>
  );
}
