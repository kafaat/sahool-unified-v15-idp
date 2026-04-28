'use client';

/**
 * Phase 2 — IndexLegend
 * مفتاح المؤشر — الطور الثاني
 *
 * Per-index colour legend with health zone labels.
 * Fixes the critical gap: a shared colormap was used for ALL indices,
 * meaning "0.3" looked the same for NDVI, NDWI, and LAI — but means
 * completely different things agronomically.
 *
 * Now each index has its own legend with:
 *   - Correct value range (LAI goes 0–8, not -1 to 1)
 *   - Correct health zone labels (NDWI: "Drought Stress" ≠ NDVI: "Critical")
 *   - Bilingual labels
 */

import { getIndexSemantics, interpolateColor } from '@/features/ndvi/index-semantics';

export interface IndexLegendProps {
  /** Spectral index key */
  index: string;
  /** Current scalar value to highlight on legend */
  currentValue?: number;
  /** 'rtl' | 'ltr' */
  dir?: 'rtl' | 'ltr';
  /** Show health zone labels */
  showZones?: boolean;
  className?: string;
}

export function IndexLegend({
  index,
  currentValue,
  dir = 'ltr',
  showZones = true,
  className = '',
}: IndexLegendProps) {
  const isRtl = dir === 'rtl';
  const sem = getIndexSemantics(index);
  const [rangeMin, rangeMax] = sem.range;
  const rangeSpan = rangeMax - rangeMin;

  // Build gradient from color stops
  const gradientStops = sem.colorStops.map((stop) => {
    const pct = ((stop.value - rangeMin) / rangeSpan) * 100;
    return `${stop.color} ${pct.toFixed(1)}%`;
  });
  const gradient = `linear-gradient(to right, ${gradientStops.join(', ')})`;

  // Position of current value on the gradient bar (0–100%)
  const valuePct = currentValue !== undefined
    ? Math.min(100, Math.max(0, ((currentValue - rangeMin) / rangeSpan) * 100))
    : undefined;

  return (
    <div dir={dir} className={`space-y-1.5 ${className}`}>
      {/* Index name + unit */}
      <div className="flex items-baseline justify-between">
        <span className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
          {sem.displayName}
          {sem.unit && <span className="ml-1 text-[10px] font-normal text-gray-400">({sem.unit})</span>}
        </span>
        {currentValue !== undefined && (
          <span
            className="text-sm font-bold font-mono"
            style={{ color: interpolateColor(index, currentValue) }}
          >
            {currentValue.toFixed(2)}
          </span>
        )}
      </div>

      {/* Gradient bar */}
      <div className="relative">
        <div
          className="h-4 w-full rounded-full shadow-inner"
          style={{ background: gradient }}
          aria-hidden
        />
        {/* Current value indicator */}
        {valuePct !== undefined && (
          <div
            className="absolute top-1/2 -translate-y-1/2 h-5 w-0.5 bg-white shadow-md rounded-full border border-gray-400"
            style={{ left: `${isRtl ? 100 - valuePct : valuePct}%` }}
            aria-hidden
          />
        )}
        {/* Range labels */}
        <div className="flex justify-between mt-0.5">
          <span className="text-[9px] font-mono text-gray-400">{rangeMin}</span>
          <span className="text-[9px] font-mono text-gray-400">{rangeMax}</span>
        </div>
      </div>

      {/* Health zones */}
      {showZones && (
        <div className="flex flex-wrap gap-1 mt-1">
          {sem.healthZones.map((zone) => (
            <span
              key={zone.label}
              title={isRtl ? zone.interpretationAr : zone.interpretation}
              className="inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-[9px] font-medium"
              style={{
                backgroundColor: zone.color + '22',
                color: zone.color,
                border: `1px solid ${zone.color}55`,
              }}
            >
              <span
                className="h-1.5 w-1.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: zone.color }}
                aria-hidden
              />
              {isRtl ? zone.labelAr : zone.label}
            </span>
          ))}
        </div>
      )}

      {/* Agronomic guidance note */}
      <p className="text-[10px] text-gray-500 dark:text-gray-400 leading-relaxed italic">
        {isRtl ? sem.guidanceAr.split('.')[0] + '.' : sem.guidance.split('.')[0] + '.'}
      </p>
    </div>
  );
}
