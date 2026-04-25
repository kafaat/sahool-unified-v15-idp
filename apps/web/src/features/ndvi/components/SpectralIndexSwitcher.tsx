'use client';

/**
 * Spectral Index Switcher
 * شريط تبديل المؤشرات الطيفية فوق الخريطة
 *
 * Icon-chip toggle group for switching the active spectral index on a map
 * (NDVI / EVI / SAVI / NDRE / NDWI / LAI). Mirrors the pattern used by
 * Sentinel Hub Playground, EOS Crop Monitoring, and Climate FieldView:
 * a horizontal row of compact pills, each with an icon + short code, where
 * the active pill is highlighted and a tooltip shows the full bilingual
 * name + a one-line description.
 *
 * Designed to be drop-in for any map view; the component is purely
 * presentational and notifies the parent via `onChange`.
 */

import { type KeyboardEvent, useId } from 'react';
import {
  SPECTRAL_INDEX_METADATA,
  SPECTRAL_INDEX_ORDER,
  type SpectralIndexId,
} from '../lib/spectral-colormaps';

export interface SpectralIndexSwitcherProps {
  /** Currently active index. */
  value: SpectralIndexId;
  /** Called when the user picks a different index. */
  onChange: (next: SpectralIndexId) => void;
  /** Indices to expose. Defaults to all six. */
  indices?: readonly SpectralIndexId[];
  /** Display language. Defaults to Arabic for SAHOOL. */
  language?: 'en' | 'ar';
  /** Visual density. */
  size?: 'sm' | 'md';
  /** Extra className applied to the outer container. */
  className?: string;
  /** Disable interaction (e.g. while data is loading). */
  disabled?: boolean;
}

/**
 * Icon-chip toggle group for spectral indices.
 *
 * Accessibility: rendered as a `role="radiogroup"` so screen readers
 * announce it as a single mutually-exclusive selector. Keyboard support:
 * arrow-left/right cycles selection; Home/End jump to first/last.
 */
export function SpectralIndexSwitcher({
  value,
  onChange,
  indices = SPECTRAL_INDEX_ORDER,
  language = 'ar',
  size = 'md',
  className = '',
  disabled = false,
}: SpectralIndexSwitcherProps) {
  const groupId = useId();
  const isArabic = language === 'ar';
  const dir = isArabic ? 'rtl' : 'ltr';

  const sizeStyles =
    size === 'sm'
      ? 'h-8 px-2 text-[11px] gap-1'
      : 'h-9 px-3 text-xs gap-1.5';
  const iconSize = size === 'sm' ? 14 : 16;

  function handleKey(e: KeyboardEvent<HTMLButtonElement>, idx: number) {
    if (disabled) return;
    let next = idx;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      next = (idx + 1) % indices.length;
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      next = (idx - 1 + indices.length) % indices.length;
    } else if (e.key === 'Home') {
      next = 0;
    } else if (e.key === 'End') {
      next = indices.length - 1;
    } else {
      return;
    }
    e.preventDefault();
    const target = indices[next];
    if (target && target !== value) onChange(target);
  }

  return (
    <div
      role="radiogroup"
      aria-label={isArabic ? 'تبديل المؤشر الطيفي' : 'Switch spectral index'}
      dir={dir}
      className={`inline-flex items-center gap-1 rounded-xl border border-gray-200 bg-white/95 p-1 shadow-sm backdrop-blur-sm dark:border-gray-700 dark:bg-gray-800/95 ${className}`}
    >
      {indices.map((id, idx) => {
        const meta = SPECTRAL_INDEX_METADATA[id];
        const Icon = meta.icon;
        const isActive = id === value;
        const label = isArabic ? meta.nameAr : meta.nameEn;
        const description = isArabic ? meta.descriptionAr : meta.descriptionEn;
        return (
          <button
            key={id}
            type="button"
            role="radio"
            id={`${groupId}-${id}`}
            aria-checked={isActive}
            aria-label={`${meta.code} — ${label}`}
            title={`${meta.code} — ${label}\n${description}`}
            tabIndex={isActive ? 0 : -1}
            disabled={disabled}
            onClick={() => !disabled && !isActive && onChange(id)}
            onKeyDown={(e) => handleKey(e, idx)}
            className={[
              'inline-flex items-center justify-center rounded-lg font-medium transition-colors',
              sizeStyles,
              isActive
                ? 'bg-emerald-600 text-white shadow-sm hover:bg-emerald-600 dark:bg-emerald-500'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700',
              disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
            ].join(' ')}
          >
            <Icon size={iconSize} aria-hidden="true" />
            <span className="font-mono tracking-wide" dir="ltr">
              {meta.code}
            </span>
          </button>
        );
      })}
    </div>
  );
}

export default SpectralIndexSwitcher;
