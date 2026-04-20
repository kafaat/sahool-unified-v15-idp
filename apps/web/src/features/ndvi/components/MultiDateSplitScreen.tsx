'use client';

/**
 * MultiDateSplitScreen — compare a single vegetation index across 2-6
 * dates side by side.
 * شاشة مُقسّمة متعددة التواريخ — مقارنة المؤشر لعدة تواريخ جنب جنب
 *
 * Supersedes the legacy `SplitScreenNDVI` (NDVI-only, 2-date max). Reads
 * a `MultiDateCompare` payload from the backend and renders N panels,
 * each panel showing the date, value, status, and delta-from-previous.
 * The panels are coloured using the same ramp sampling trick as
 * `IndexFilmstrip`, so the visual pattern (green -> yellow -> red)
 * matches the rest of the map UX.
 *
 * Parent owns the date set. This component is a pure renderer.
 */

import { useMemo } from 'react';
import type {
  MultiDateCompare,
  MultiDateCompareRow,
  IndexMapData,
} from '../api';

export interface MultiDateSplitScreenProps {
  data: MultiDateCompare | undefined;
  /** Color scale from the current index (optional — skips background tinting if absent). */
  colorScale?: IndexMapData['colorScale'];
  loading?: boolean;
  error?: Error | null;
  className?: string;
}

export const PANEL_COUNTS = [2, 3, 4, 6] as const;
export type PanelCount = (typeof PANEL_COUNTS)[number];

function nearestAllowedPanelCount(n: number): PanelCount {
  // Snap to the closest supported grid (2 / 3 / 4 / 6).
  return (
    [...PANEL_COUNTS]
      .map((c) => ({ c, d: Math.abs(c - n) }))
      .sort((a, b) => a.d - b.d)[0]?.c ?? 2
  );
}

function sampleColor(
  value: number | null,
  scale: IndexMapData['colorScale'] | undefined
): string {
  if (!scale || value == null || !Number.isFinite(value)) return '#f3f4f6';
  const { min, max, colors } = scale;
  if (!colors.length || max <= min) return colors[0] ?? '#f3f4f6';
  const clamped = Math.max(min, Math.min(max, value));
  const ratio = (clamped - min) / (max - min);
  const idx = Math.min(colors.length - 1, Math.floor(ratio * colors.length));
  return colors[idx] ?? colors[colors.length - 1]!;
}

function arrowFor(delta: number | null): { glyph: string; tone: string } {
  if (delta == null) return { glyph: '—', tone: 'text-gray-400' };
  if (delta > 0.02) return { glyph: '▲', tone: 'text-green-600' };
  if (delta < -0.02) return { glyph: '▼', tone: 'text-red-600' };
  return { glyph: '■', tone: 'text-gray-500' };
}

export const MultiDateSplitScreen: React.FC<MultiDateSplitScreenProps> = ({
  data,
  colorScale,
  loading = false,
  error,
  className = '',
}) => {
  const rows: MultiDateCompareRow[] = useMemo(() => data?.rows ?? [], [data]);
  const panelCount: PanelCount = useMemo(
    () => nearestAllowedPanelCount(rows.length || 2),
    [rows.length]
  );

  if (loading) {
    return (
      <div
        className={`py-6 text-center text-sm text-gray-500 ${className}`}
        data-testid="multi-date-split-loading"
      >
        جاري المقارنة… <span className="ml-2">Comparing…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div
        role="alert"
        className={`py-3 px-2 text-xs text-red-700 bg-red-50 rounded ${className}`}
        data-testid="multi-date-split-error"
      >
        {error.message || 'Failed to load comparison | فشل في تحميل المقارنة'}
      </div>
    );
  }

  // A 1-row payload is logically empty for a *comparison* view — the
  // empty-state copy asks for "at least 2 dates", so a lone row would
  // render a single panel and contradict the message. Treat <2 as empty.
  if (!data || rows.length < 2) {
    return (
      <div
        className={`py-6 text-center text-sm text-gray-400 ${className}`}
        data-testid="multi-date-split-empty"
      >
        Pick at least 2 dates to compare · اختر تاريخَين على الأقل
      </div>
    );
  }

  const gridCols: Record<PanelCount, string> = {
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-2 md:grid-cols-4',
    6: 'grid-cols-2 md:grid-cols-3 lg:grid-cols-6',
  };

  return (
    <section
      aria-label={`Multi-date compare for ${data.indexName.toUpperCase()}`}
      data-testid="multi-date-split"
      className={`bg-white rounded-lg shadow p-4 ${className}`}
    >
      <header className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-bold text-gray-900">
          {data.indexName.toUpperCase()} · Multi-date compare
          <span className="text-gray-500 font-normal"> · مقارنة متعددة التواريخ</span>
        </h3>
        <span className="text-[10px] text-gray-500" data-testid="multi-date-split-grid">
          {panelCount}-panel · {rows.length} date{rows.length === 1 ? '' : 's'}
        </span>
      </header>

      <div
        className={`grid gap-3 ${gridCols[panelCount]}`}
        data-testid="multi-date-split-panels"
      >
        {rows.map((row) => {
          const arrow = arrowFor(row.delta_from_previous);
          const bg = sampleColor(row.value, colorScale);
          return (
            <article
              key={row.date}
              data-testid={`multi-date-panel-${row.date}`}
              className="rounded-md border border-gray-200 overflow-hidden"
            >
              <div
                className="h-20 flex items-center justify-center text-white font-semibold"
                style={{ backgroundColor: bg }}
                aria-hidden="true"
              >
                {row.value == null ? '—' : row.value.toFixed(3)}
              </div>
              <div className="p-2 text-xs">
                <div className="flex items-center justify-between font-medium text-gray-900">
                  <span>{row.date}</span>
                  <span className={arrow.tone} aria-label="delta from previous">
                    {arrow.glyph}{' '}
                    {row.delta_from_previous == null
                      ? ''
                      : row.delta_from_previous.toFixed(3)}
                  </span>
                </div>
                <div className="flex items-center justify-between text-gray-500 mt-0.5">
                  <span>{row.status.en}</span>
                  <span>{row.status.ar}</span>
                </div>
              </div>
            </article>
          );
        })}
      </div>

      {data.summary.overall_delta != null && (
        <footer
          className="mt-3 pt-2 border-t border-gray-100 text-xs text-gray-600 flex items-center justify-between"
          data-testid="multi-date-split-summary"
        >
          <span>
            Range · المدى:{' '}
            <strong>
              {data.summary.min?.toFixed(3) ?? '—'}
              {' '}→{' '}
              {data.summary.max?.toFixed(3) ?? '—'}
            </strong>
          </span>
          <span>
            Overall delta · التغيّر الكلّي:{' '}
            <strong className={arrowFor(data.summary.overall_delta).tone}>
              {data.summary.overall_delta.toFixed(3)}
            </strong>
          </span>
        </footer>
      )}
    </section>
  );
};

export default MultiDateSplitScreen;
