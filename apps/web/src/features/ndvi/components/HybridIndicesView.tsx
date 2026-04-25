'use client';

/**
 * HybridIndicesView
 * عرض هجين لمؤشرين طيفيين على خريطة واحدة (نمط Farmonaut)
 *
 * Farmonaut-style two-index split overlay: a single field is shown with two
 * spectral indices simultaneously, separated by a vertical draggable divider.
 * The user toggles which index drives each side via a dedicated
 * {@link SpectralIndexSwitcher} per side, mirroring how Farmonaut, EOS Crop
 * Monitoring, and Climate FieldView present comparative views.
 *
 * The component is **base-map agnostic**: it renders absolutely-positioned
 * overlays inside a parent container the caller controls. This works on top
 * of MapLibre, Google Maps (via `<GoogleMap>` containerStyle), Leaflet, or
 * any other map engine — the caller is responsible for matching the
 * container's bounding box to the field bounds.
 *
 * Architecture::
 *
 *   ┌─ container (caller) ───────────────────────────────────────────────┐
 *   │  ┌─ left-pane (clip-path: inset(0 N% 0 0)) ──────────────────────┐ │
 *   │  │   <img rasterUrl=index_left>                                  │ │
 *   │  └───────────────────────────────────────────────────────────────┘ │
 *   │  ┌─ right-pane (clip-path: inset(0 0 0 100-N%)) ─────────────────┐ │
 *   │  │   <img rasterUrl=index_right>                                 │ │
 *   │  └───────────────────────────────────────────────────────────────┘ │
 *   │  ┌─ divider (draggable) at N% ──────────────────────────────────┐ │
 *   │  └───────────────────────────────────────────────────────────────┘ │
 *   └────────────────────────────────────────────────────────────────────┘
 *
 * The divider position is controlled by `splitPercent` (0-100). Drag/keyboard
 * interactions update internal state via the standard ARIA `slider` pattern.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useIndexMap } from '../hooks/useNDVI';
import {
  buildCssGradient,
  getIndexMetadata,
  type SpectralIndexId,
} from '../lib/spectral-colormaps';
import { SpectralIndexSwitcher } from './SpectralIndexSwitcher';

export interface HybridIndicesViewProps {
  /** Field identifier — معرّف الحقل */
  fieldId: string;
  /** Initial left-side index — defaults to ``"ndvi"`` */
  leftIndex?: SpectralIndexId;
  /** Initial right-side index — defaults to ``"ndwi"`` */
  rightIndex?: SpectralIndexId;
  /** Optional acquisition date (ISO 8601 ``YYYY-MM-DD``) */
  date?: string;
  /** Initial divider position percentage (0-100) — defaults to ``50`` */
  initialSplitPercent?: number;
  /** Overlay opacity 0–1 — defaults to ``0.85`` */
  opacity?: number;
  /** Show per-side legend gradient chips — defaults to ``true`` */
  showLegends?: boolean;
  /** Show per-side `SpectralIndexSwitcher` selectors — defaults to ``true`` */
  showSwitchers?: boolean;
  /** UI language — defaults to ``"ar"`` */
  language?: 'ar' | 'en';
  /** Container className — caller-controlled sizing */
  className?: string;
  /** Notify when either side's index changes */
  onIndicesChange?: (left: SpectralIndexId, right: SpectralIndexId) => void;
}

const clampPercent = (n: number) => Math.max(0, Math.min(100, n));

/**
 * Hybrid two-index overlay.
 *
 * Both raster sources are fetched in parallel via {@link useIndexMap}; the
 * loading state is shown as a translucent overlay so the previous render
 * doesn't disappear when the user toggles the index.
 */
export function HybridIndicesView({
  fieldId,
  leftIndex: leftIndexProp = 'ndvi',
  rightIndex: rightIndexProp = 'ndwi',
  date,
  initialSplitPercent = 50,
  opacity = 0.85,
  showLegends = true,
  showSwitchers = true,
  language = 'ar',
  className,
  onIndicesChange,
}: HybridIndicesViewProps) {
  const [leftIndex, setLeftIndex] = useState<SpectralIndexId>(leftIndexProp);
  const [rightIndex, setRightIndex] = useState<SpectralIndexId>(rightIndexProp);
  const [splitPercent, setSplitPercent] = useState<number>(clampPercent(initialSplitPercent));
  const containerRef = useRef<HTMLDivElement | null>(null);
  const draggingRef = useRef(false);

  const leftQuery = useIndexMap(fieldId, leftIndex, date);
  const rightQuery = useIndexMap(fieldId, rightIndex, date);

  useEffect(() => {
    onIndicesChange?.(leftIndex, rightIndex);
  }, [leftIndex, rightIndex, onIndicesChange]);

  // ── divider drag handlers ────────────────────────────────────────────────
  const updateFromClientX = useCallback((clientX: number) => {
    const el = containerRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    if (rect.width <= 0) return;
    // RTL containers: drag right → index decreases. We always compute LTR
    // percentage so the visual mapping stays consistent with the clip-path.
    const pct = ((clientX - rect.left) / rect.width) * 100;
    setSplitPercent(clampPercent(pct));
  }, []);

  const handlePointerDown = useCallback(
    (e: React.PointerEvent<HTMLDivElement>) => {
      draggingRef.current = true;
      (e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId);
      updateFromClientX(e.clientX);
    },
    [updateFromClientX],
  );

  const handlePointerMove = useCallback(
    (e: React.PointerEvent<HTMLDivElement>) => {
      if (!draggingRef.current) return;
      updateFromClientX(e.clientX);
    },
    [updateFromClientX],
  );

  const handlePointerUp = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    draggingRef.current = false;
    (e.currentTarget as HTMLElement).releasePointerCapture?.(e.pointerId);
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLDivElement>) => {
    const step = e.shiftKey ? 10 : 2;
    // In RTL the left/right keys feel more natural when reversed
    const isRtl = (e.currentTarget.closest('[dir="rtl"]') ?? null) !== null;
    switch (e.key) {
      case 'ArrowLeft':
        setSplitPercent((p) => clampPercent(p + (isRtl ? step : -step)));
        e.preventDefault();
        break;
      case 'ArrowRight':
        setSplitPercent((p) => clampPercent(p + (isRtl ? -step : step)));
        e.preventDefault();
        break;
      case 'Home':
        setSplitPercent(0);
        e.preventDefault();
        break;
      case 'End':
        setSplitPercent(100);
        e.preventDefault();
        break;
      default:
        break;
    }
  }, []);

  const leftMeta = getIndexMetadata(leftIndex);
  const rightMeta = getIndexMetadata(rightIndex);
  const isLoading = leftQuery.isLoading || rightQuery.isLoading;
  const isError = !!(leftQuery.error || rightQuery.error);

  return (
    <div
      ref={containerRef}
      data-testid="hybrid-indices-view"
      data-split-percent={Math.round(splitPercent)}
      dir={language === 'ar' ? 'rtl' : 'ltr'}
      className={[
        'relative isolate h-full w-full overflow-hidden rounded-lg bg-gray-900',
        className ?? '',
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {/* Left raster pane — clipped to [0, splitPercent] */}
      <div
        className="absolute inset-0"
        style={{
          clipPath: `inset(0 ${100 - splitPercent}% 0 0)`,
          opacity,
        }}
        aria-label={`${leftMeta.code} overlay`}
      >
        {leftQuery.data?.rasterUrl ? (
          <img
            src={leftQuery.data.rasterUrl}
            alt={leftMeta.code}
            className="h-full w-full object-cover"
            draggable={false}
          />
        ) : null}
        {/* Background gradient fallback so simulated mode still shows colour */}
        <div
          aria-hidden
          className="absolute inset-0 -z-10"
          style={{ background: buildCssGradient(leftIndex), opacity: 0.6 }}
        />
      </div>

      {/* Right raster pane — clipped to [splitPercent, 100] */}
      <div
        className="absolute inset-0"
        style={{
          clipPath: `inset(0 0 0 ${splitPercent}%)`,
          opacity,
        }}
        aria-label={`${rightMeta.code} overlay`}
      >
        {rightQuery.data?.rasterUrl ? (
          <img
            src={rightQuery.data.rasterUrl}
            alt={rightMeta.code}
            className="h-full w-full object-cover"
            draggable={false}
          />
        ) : null}
        <div
          aria-hidden
          className="absolute inset-0 -z-10"
          style={{ background: buildCssGradient(rightIndex), opacity: 0.6 }}
        />
      </div>

      {/* Divider — draggable handle */}
      <div
        role="slider"
        aria-label={
          language === 'ar' ? 'فاصل المقارنة بين المؤشرين' : 'Index comparison divider'
        }
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(splitPercent)}
        aria-orientation="vertical"
        tabIndex={0}
        className="absolute top-0 bottom-0 z-20 -translate-x-1/2 cursor-col-resize touch-none select-none"
        style={{ left: `${splitPercent}%`, width: 12 }}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        onKeyDown={handleKeyDown}
        data-testid="hybrid-indices-divider"
      >
        <div className="absolute left-1/2 top-0 bottom-0 w-0.5 -translate-x-1/2 bg-white/90 shadow-md" />
        <div className="absolute left-1/2 top-1/2 flex h-8 w-8 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-white text-gray-700 shadow-lg">
          <svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="currentColor"
            aria-hidden
          >
            <path d="M3 2v10l-3-5zM11 2v10l3-5z" />
          </svg>
        </div>
      </div>

      {/* Per-side index switchers + legends */}
      {showSwitchers && (
        <>
          <div
            className="absolute top-2 z-30"
            style={{ insetInlineStart: 8 }}
            data-testid="hybrid-switcher-left"
          >
            <SpectralIndexSwitcher
              value={leftIndex}
              onChange={setLeftIndex}
              language={language}
              size="sm"
            />
          </div>
          <div
            className="absolute top-2 z-30"
            style={{ insetInlineEnd: 8 }}
            data-testid="hybrid-switcher-right"
          >
            <SpectralIndexSwitcher
              value={rightIndex}
              onChange={setRightIndex}
              language={language}
              size="sm"
            />
          </div>
        </>
      )}

      {showLegends && (
        <>
          <div
            className="pointer-events-none absolute bottom-2 z-30 max-w-[40%]"
            style={{ insetInlineStart: 8 }}
            data-testid="hybrid-legend-left"
          >
            <LegendChip indexId={leftIndex} language={language} />
          </div>
          <div
            className="pointer-events-none absolute bottom-2 z-30 max-w-[40%]"
            style={{ insetInlineEnd: 8 }}
            data-testid="hybrid-legend-right"
          >
            <LegendChip indexId={rightIndex} language={language} />
          </div>
        </>
      )}

      {/* Loading / error overlay */}
      {(isLoading || isError) && (
        <div
          className="absolute inset-x-0 top-1/2 z-30 mx-auto flex w-fit -translate-y-1/2 items-center gap-2 rounded-full bg-black/60 px-3 py-1 text-xs text-white"
          role={isError ? 'alert' : 'status'}
          aria-live="polite"
        >
          {isError
            ? language === 'ar'
              ? 'تعذّر تحميل بيانات المؤشرات'
              : 'Failed to load index data'
            : language === 'ar'
              ? 'جاري تحميل المؤشرات…'
              : 'Loading indices…'}
        </div>
      )}
    </div>
  );
}

function LegendChip({
  indexId,
  language,
}: {
  indexId: SpectralIndexId;
  language: 'ar' | 'en';
}) {
  const meta = getIndexMetadata(indexId);
  const gradient = buildCssGradient(indexId);
  const label = language === 'ar' ? meta.nameAr : meta.nameEn;
  return (
    <div className="rounded-md bg-white/90 p-1.5 shadow-sm dark:bg-gray-900/90">
      <div className="flex items-center justify-between gap-2 text-[10px] font-medium text-gray-700 dark:text-gray-200">
        <span>{meta.code}</span>
        <span className="truncate">{label}</span>
      </div>
      <div className="mt-0.5 h-1.5 w-full rounded-sm" style={{ background: gradient }} />
    </div>
  );
}

export default HybridIndicesView;
