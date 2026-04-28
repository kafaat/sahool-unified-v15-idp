'use client';

/**
 * Phase 2 — CloudCoverageBadge
 * شارة الغطاء السحابي — الطور الثاني
 *
 * Shows cloud coverage % for the current satellite image.
 * When cloud cover is too high the badge warns the user that
 * the NDVI values may be unreliable — fixing the silent failure
 * where cloudy images were shown with no warning.
 */

import type { ComponentPropsWithoutRef } from 'react';

export interface CloudCoverageBadgeProps extends ComponentPropsWithoutRef<'span'> {
  /** Cloud coverage percentage 0–100 */
  cloudPercent: number;
  /** Whether the image is marked as usable by cloud masker */
  usable?: boolean;
  /** 'rtl' | 'ltr' */
  dir?: 'rtl' | 'ltr';
  /** Show full label or just icon + number */
  compact?: boolean;
}

function getCloudStyle(cloudPercent: number, usable: boolean) {
  if (!usable || cloudPercent > 40) {
    return {
      bg: 'bg-red-100 dark:bg-red-900/40',
      text: 'text-red-800 dark:text-red-300',
      icon: '⛅',
      tooltip: 'Cloud cover too high — values may be unreliable',
      tooltipAr: 'الغطاء السحابي مرتفع جدًا — القيم قد تكون غير موثوقة',
    };
  }
  if (cloudPercent > 20) {
    return {
      bg: 'bg-amber-100 dark:bg-amber-900/40',
      text: 'text-amber-800 dark:text-amber-300',
      icon: '⛅',
      tooltip: 'Moderate cloud cover — some pixels masked',
      tooltipAr: 'غطاء سحابي معتدل — بعض البكسلات محجوبة',
    };
  }
  return {
    bg: 'bg-green-100 dark:bg-green-900/40',
    text: 'text-green-800 dark:text-green-300',
    icon: '☀️',
    tooltip: 'Good image quality — low cloud cover',
    tooltipAr: 'جودة صورة جيدة — غطاء سحابي منخفض',
  };
}

export function CloudCoverageBadge({
  cloudPercent,
  usable = true,
  dir = 'ltr',
  compact = false,
  className = '',
  ...rest
}: CloudCoverageBadgeProps) {
  const isRtl = dir === 'rtl';
  const style = getCloudStyle(cloudPercent, usable);

  return (
    <span
      role="status"
      aria-label={isRtl ? style.tooltipAr : style.tooltip}
      title={isRtl ? style.tooltipAr : style.tooltip}
      dir={dir}
      className={[
        'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
        style.bg,
        style.text,
        className,
      ].join(' ')}
      {...rest}
    >
      <span aria-hidden="true">{style.icon}</span>
      <span>{cloudPercent.toFixed(0)}%</span>
      {!compact && (
        <span className="hidden sm:inline">
          {isRtl ? 'سحاب' : 'cloud'}
        </span>
      )}
      {/* Warning indicator for unusable images */}
      {(!usable || cloudPercent > 40) && (
        <span aria-hidden="true" className="font-bold">!</span>
      )}
    </span>
  );
}
