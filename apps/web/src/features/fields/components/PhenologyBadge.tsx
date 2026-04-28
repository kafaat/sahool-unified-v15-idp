'use client';

/**
 * Phase 2 — PhenologyBadge
 * شارة مرحلة النمو الفينولوجية — الطور الثاني
 *
 * Displays the current phenological growth stage of the crop in a field.
 * Wires to the backend /v1/phenology/{fieldId} endpoint via the
 * useIndexMap hook's `phenology` property.
 *
 * Resolves the gap: "no Zadoks / FAO stage mapping visible to user"
 */

import type { PhenologyStage } from '@/features/ndvi/hooks/useIndexMap';

// Maps stage key → emoji icon for quick visual recognition
const STAGE_ICONS: Record<string, string> = {
  dormancy: '😴',
  germination: '🌱',
  emergence: '🌿',
  leaf_dev: '🍃',
  tillering: '🌾',
  stem_elongation: '📏',
  booting: '🌰',
  heading: '🌾',
  flowering: '🌸',
  anthesis: '🌸',
  fruit_dev: '🍅',
  ripening: '🟡',
  maturation: '🟠',
  senescence: '🍂',
  harvest: '✂️',
  fallow: '🌵',
  vegetative: '🌿',
  reproductive: '🌸',
};

function getStageIcon(stage: string): string {
  return STAGE_ICONS[stage.toLowerCase()] ?? '🌱';
}

function getProgressColor(progress: number): string {
  if (progress < 30) return 'bg-green-400';
  if (progress < 60) return 'bg-emerald-500';
  if (progress < 85) return 'bg-yellow-500';
  return 'bg-orange-500';
}

export interface PhenologyBadgeProps {
  phenology: PhenologyStage | undefined;
  loading?: boolean;
  /** 'rtl' | 'ltr' */
  dir?: 'rtl' | 'ltr';
  /** Show progress bar and recommendations */
  expanded?: boolean;
  className?: string;
}

export function PhenologyBadge({
  phenology,
  loading = false,
  dir = 'ltr',
  expanded = false,
  className = '',
}: PhenologyBadgeProps) {
  const isRtl = dir === 'rtl';

  if (loading) {
    return (
      <div className={`animate-pulse rounded-lg bg-gray-100 dark:bg-gray-800 h-8 w-40 ${className}`} />
    );
  }

  if (!phenology) return null;

  const icon = getStageIcon(phenology.currentStage);
  const stageName = isRtl ? phenology.currentStageAr : phenology.currentStage.replace(/_/g, ' ');
  const progress = Math.min(100, Math.max(0, phenology.seasonProgressPercent));
  const progressColor = getProgressColor(progress);

  return (
    <div dir={dir} className={`rounded-lg border border-green-200 bg-green-50 p-3 dark:border-green-800 dark:bg-green-900/20 ${className}`}>
      {/* Header row */}
      <div className="flex items-center gap-2">
        <span className="text-xl" aria-hidden="true">{icon}</span>
        <div className="flex-1 min-w-0">
          <p className="text-xs text-green-600 dark:text-green-400 font-medium uppercase tracking-wide">
            {isRtl ? 'مرحلة النمو' : 'Growth Stage'}
          </p>
          <p className="text-sm font-semibold text-green-900 dark:text-green-100 capitalize truncate">
            {stageName}
          </p>
        </div>
        {/* Confidence badge */}
        <span className="rounded-full bg-green-200 dark:bg-green-800 px-2 py-0.5 text-[10px] font-mono text-green-800 dark:text-green-200">
          {Math.round(phenology.confidence * 100)}%
        </span>
      </div>

      {/* Season progress bar */}
      {expanded && (
        <>
          <div className="mt-2">
            <div className="flex justify-between text-[10px] text-gray-500 dark:text-gray-400 mb-1">
              <span>{isRtl ? 'تقدم الموسم' : 'Season progress'}</span>
              <span>{progress.toFixed(0)}%</span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-gray-200 dark:bg-gray-700">
              <div
                className={`h-1.5 rounded-full transition-all duration-500 ${progressColor}`}
                style={{ width: `${progress}%` }}
                role="progressbar"
                aria-valuenow={progress}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={isRtl ? `تقدم الموسم ${progress.toFixed(0)}%` : `Season progress ${progress.toFixed(0)}%`}
              />
            </div>
          </div>

          {/* Days in stage */}
          <p className="mt-1.5 text-[11px] text-gray-500 dark:text-gray-400">
            {isRtl
              ? `${phenology.daysInStage} يوم في هذه المرحلة`
              : `${phenology.daysInStage} days in this stage`}
          </p>

          {/* Harvest estimate */}
          {phenology.estimatedHarvestDate && (
            <p className="mt-1 text-[11px] font-medium text-amber-700 dark:text-amber-400">
              {isRtl
                ? `الحصاد المتوقع: ${phenology.estimatedHarvestDate}`
                : `Est. harvest: ${phenology.estimatedHarvestDate}`}
            </p>
          )}

          {/* Top recommendation */}
          {(isRtl ? phenology.recommendationsAr : phenology.recommendationsEn)[0] && (
            <p className="mt-2 text-xs text-green-800 dark:text-green-200 border-t border-green-200 dark:border-green-800 pt-2">
              💡 {(isRtl ? phenology.recommendationsAr : phenology.recommendationsEn)[0]}
            </p>
          )}
        </>
      )}
    </div>
  );
}
