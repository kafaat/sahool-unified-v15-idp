'use client';

/**
 * Phase 2 — SpectralIndexSwitcher
 * مُبدِّل المؤشرات الطيفية — الطور الثاني
 *
 * Tab/button group that lets the user switch between spectral indices.
 * Each tab shows the per-index semantics so the user immediately knows
 * what they are looking at (fixes the "NDWI mistaken for NDVI" problem).
 *
 * Features:
 * - Shows what each index MEASURES (not just its name)
 * - RTL/LTR support
 * - keyboard navigation (←→ or arrow keys)
 * - ARIA roles for screen readers
 */

import { useId, useRef } from 'react';
import { MAP_SUPPORTED_INDICES, getIndexSemantics } from '@/features/ndvi/index-semantics';

// Indices shown by default in the switcher (ordered by agronomic priority)
const DEFAULT_INDICES = ['ndvi', 'ndwi', 'evi', 'savi', 'ndre', 'lai'] as const;

export interface SpectralIndexSwitcherProps {
  /** Currently selected index key */
  selectedIndex: string;
  /** Called when user selects a different index */
  onIndexChange: (index: string) => void;
  /** Subset of indices to show (defaults to 6 primary indices) */
  indices?: string[];
  /** 'rtl' | 'ltr' (default: 'ltr') */
  dir?: 'rtl' | 'ltr';
  /** Additional CSS class */
  className?: string;
}

export function SpectralIndexSwitcher({
  selectedIndex,
  onIndexChange,
  indices = DEFAULT_INDICES as unknown as string[],
  dir = 'ltr',
  className = '',
}: SpectralIndexSwitcherProps) {
  const listId = useId();
  const isRtl = dir === 'rtl';
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const validIndices = indices.filter((i) => MAP_SUPPORTED_INDICES.includes(i));
  const selectedIdx = validIndices.indexOf(selectedIndex);

  function handleKeyDown(e: React.KeyboardEvent, positionInList: number) {
    const prev = isRtl ? 'ArrowRight' : 'ArrowLeft';
    const next = isRtl ? 'ArrowLeft' : 'ArrowRight';
    let newPos: number | null = null;
    if (e.key === next) newPos = (positionInList + 1) % validIndices.length;
    if (e.key === prev) newPos = (positionInList - 1 + validIndices.length) % validIndices.length;
    if (newPos !== null) {
      e.preventDefault();
      tabRefs.current[newPos]?.focus();
      onIndexChange(validIndices[newPos]!);
    }
  }

  return (
    <div
      role="tablist"
      aria-label={isRtl ? 'المؤشرات الطيفية' : 'Spectral Indices'}
      id={listId}
      dir={dir}
      className={`flex flex-wrap gap-1.5 ${className}`}
    >
      {validIndices.map((indexKey, pos) => {
        const sem = getIndexSemantics(indexKey);
        const isSelected = indexKey === selectedIndex;

        return (
          <button
            key={indexKey}
            role="tab"
            aria-selected={isSelected}
            aria-controls={`${listId}-panel`}
            ref={(el) => { tabRefs.current[pos] = el; }}
            tabIndex={isSelected || (selectedIdx < 0 && pos === 0) ? 0 : -1}
            onClick={() => onIndexChange(indexKey)}
            onKeyDown={(e) => handleKeyDown(e, pos)}
            title={isRtl ? sem.guidanceAr : sem.guidance}
            className={[
              'group relative flex flex-col items-start rounded-lg border px-3 py-2 text-start',
              'text-sm font-medium transition-all duration-150',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-green-500',
              isSelected
                ? 'border-green-600 bg-green-50 text-green-800 shadow-sm dark:border-green-400 dark:bg-green-900/30 dark:text-green-200'
                : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300',
            ].join(' ')}
          >
            {/* Index display name */}
            <span className="font-bold tracking-wide uppercase text-xs">
              {sem.displayName}
            </span>

            {/* What it measures — key differentiator preventing NDWI/NDVI confusion */}
            <span className={`mt-0.5 text-[10px] leading-tight ${isSelected ? 'text-green-600 dark:text-green-400' : 'text-gray-500'}`}>
              {isRtl ? sem.measuresAr : sem.measures}
            </span>

            {/* Unit badge (shows 'm²/m²' for LAI — signals different scale) */}
            {sem.unit && (
              <span className={`mt-1 rounded px-1 py-px text-[9px] font-mono ${
                isSelected
                  ? 'bg-green-200 text-green-800 dark:bg-green-800 dark:text-green-200'
                  : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
              }`}>
                {sem.unit}
              </span>
            )}

            {/* Active indicator dot */}
            {isSelected && (
              <span
                aria-hidden
                className="absolute bottom-1 left-1/2 -translate-x-1/2 h-1 w-1 rounded-full bg-green-600 dark:bg-green-400"
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
