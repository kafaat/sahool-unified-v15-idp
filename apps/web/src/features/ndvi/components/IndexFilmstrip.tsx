'use client';

/**
 * IndexFilmstrip — horizontal carousel of per-date thumbnails.
 * شريط الصور — صفّ أفقي من المصغّرات لعدة تواريخ
 *
 * Renders one thumbnail per frame, each showing:
 *   - a colour swatch sampled from the index's ramp based on the
 *     frame value (no raster fetch — just a deterministic preview so
 *     we stay fast with 20 frames);
 *   - the date + numeric value + bilingual status badge;
 *   - click → emits `onSelectDate(date)` so the parent can pipe that
 *     date into the primary map layer.
 *
 * The active date is highlighted. Designed to be parked below the
 * primary map so it mirrors EOSDA's "scrollable date row".
 */

import { useCallback, useMemo } from 'react';
import type { IndexFilmstrip as FilmstripData, FilmstripFrame } from '../api';

export interface IndexFilmstripProps {
  data: FilmstripData | undefined;
  activeDate?: string | null;
  onSelectDate?: (date: string) => void;
  loading?: boolean;
  error?: Error | null;
  className?: string;
}

function sampleColor(value: number | null, colorScale: FilmstripData['colorScale']): string {
  if (value == null || !Number.isFinite(value)) return '#e5e7eb';
  const { min, max, colors } = colorScale;
  if (!colors.length) return '#e5e7eb';
  if (max <= min) return colors[Math.floor(colors.length / 2)] ?? colors[0]!;
  const clamped = Math.max(min, Math.min(max, value));
  const ratio = (clamped - min) / (max - min);
  const idx = Math.min(colors.length - 1, Math.floor(ratio * colors.length));
  return colors[idx] ?? colors[colors.length - 1]!;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.valueOf())) return iso;
  return d.toLocaleDateString('en', { day: '2-digit', month: 'short' });
}

export const IndexFilmstrip: React.FC<IndexFilmstripProps> = ({
  data,
  activeDate,
  onSelectDate,
  loading = false,
  error,
  className = '',
}) => {
  const colorScale = data?.colorScale;
  const frames = useMemo(() => data?.frames ?? [], [data]);

  const handleClick = useCallback(
    (frame: FilmstripFrame) => {
      if (!onSelectDate || frame.date === activeDate) return;
      onSelectDate(frame.date);
    },
    [onSelectDate, activeDate]
  );

  if (loading) {
    return (
      <div
        className={`flex items-center justify-center py-4 text-xs text-gray-500 ${className}`}
        data-testid="index-filmstrip-loading"
      >
        جاري تحميل الشريط… <span className="ml-2">Loading filmstrip…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div
        role="alert"
        className={`py-3 px-2 text-xs text-red-700 bg-red-50 rounded ${className}`}
        data-testid="index-filmstrip-error"
      >
        {error.message || 'Failed to load filmstrip | فشل تحميل الشريط'}
      </div>
    );
  }

  if (!data || frames.length === 0) {
    return (
      <div
        className={`py-4 text-center text-xs text-gray-400 ${className}`}
        data-testid="index-filmstrip-empty"
      >
        No acquisitions in this window · لا توجد بيانات
      </div>
    );
  }

  return (
    <section
      aria-label={`Filmstrip for ${data.indexName.toUpperCase()}`}
      data-testid="index-filmstrip"
      className={`bg-white/95 backdrop-blur-sm rounded-lg shadow p-3 ${className}`}
    >
      <header className="flex items-center justify-between mb-2">
        <h4 className="text-xs font-bold text-gray-800 uppercase">
          {data.label.en} <span className="text-gray-500">· {data.label.ar}</span>
        </h4>
        <span className="text-[10px] text-gray-500">
          every {data.stepDays} day{data.stepDays === 1 ? '' : 's'} · كل {data.stepDays} يوم
        </span>
      </header>

      <ol
        className="flex gap-2 overflow-x-auto pb-1 snap-x snap-mandatory"
        data-testid="index-filmstrip-track"
      >
        {frames.map((frame) => {
          const active = frame.date === activeDate;
          const bg = sampleColor(frame.value, colorScale!);
          return (
            <li
              key={frame.date}
              className="snap-start shrink-0"
              data-testid={`index-filmstrip-frame-${frame.date}`}
            >
              <button
                type="button"
                onClick={() => handleClick(frame)}
                aria-pressed={active}
                aria-label={`${frame.date} · ${frame.status.en}`}
                className={[
                  'w-24 text-left rounded-md border transition-all',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500',
                  active
                    ? 'border-green-600 ring-2 ring-green-500'
                    : 'border-gray-200 hover:border-green-400',
                ].join(' ')}
              >
                <div
                  className="h-14 rounded-t-md flex items-center justify-center text-white text-xs font-semibold"
                  style={{ backgroundColor: bg }}
                  aria-hidden="true"
                >
                  {frame.value == null ? '—' : frame.value.toFixed(2)}
                </div>
                <div className="px-2 py-1">
                  <div className="text-[11px] font-medium text-gray-900">
                    {formatDate(frame.date)}
                  </div>
                  <div className="text-[10px] text-gray-500 flex items-center justify-between">
                    <span>{frame.status.en}</span>
                    <span>{frame.status.ar}</span>
                  </div>
                  {typeof frame.cloudCover === 'number' && (
                    <div className="text-[9px] text-gray-400">
                      ☁ {frame.cloudCover.toFixed(0)}%
                    </div>
                  )}
                </div>
              </button>
            </li>
          );
        })}
      </ol>
    </section>
  );
};

export default IndexFilmstrip;
