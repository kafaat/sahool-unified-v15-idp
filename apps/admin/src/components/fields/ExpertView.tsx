'use client';

/**
 * Expert View — نظرة خبير
 * Shows: weather risk + disease risk + growth stage + nutrition + NDVI in one card
 *
 * Inspired by xarvio FIELD MANAGER's "Expert View" — a compact widget
 * showing ALL critical field information in ONE glance.
 */

import React, { useMemo } from 'react';
import { cn } from '@/lib/utils';
import {
  Eye,
  Thermometer,
  Droplets,
  Leaf,
  Bug,
  Wheat,
  Wind,
  CloudRain,
  Calendar,
  AlertTriangle,
  Clock,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface ExpertViewProps {
  fieldId: string;
  cropType: string;
  ndvi?: number;
  temperature?: number;
  humidity?: number;
  windSpeed?: number;
  precipitation?: number;
  growthStage?: string;
  diseaseRisk?: RiskLevel;
  pestRisk?: RiskLevel;
  soilMoisture?: number;
  lastIrrigation?: string;
  daysToHarvest?: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const RISK_CONFIG: Record<RiskLevel, { label: string; labelAr: string; color: string; bg: string }> = {
  low: {
    label: 'Low',
    labelAr: 'منخفض',
    color: 'text-emerald-700 dark:text-emerald-400',
    bg: 'bg-emerald-50 dark:bg-emerald-950/40',
  },
  medium: {
    label: 'Med',
    labelAr: 'متوسط',
    color: 'text-yellow-700 dark:text-yellow-400',
    bg: 'bg-yellow-50 dark:bg-yellow-950/40',
  },
  high: {
    label: 'High',
    labelAr: 'عالي',
    color: 'text-orange-700 dark:text-orange-400',
    bg: 'bg-orange-50 dark:bg-orange-950/40',
  },
  critical: {
    label: 'Crit',
    labelAr: 'حرج',
    color: 'text-red-700 dark:text-red-400',
    bg: 'bg-red-50 dark:bg-red-950/40',
  },
};

function getNdviColor(ndvi: number): string {
  if (ndvi >= 0.6) return 'text-emerald-700 dark:text-emerald-400';
  if (ndvi >= 0.4) return 'text-yellow-700 dark:text-yellow-400';
  if (ndvi >= 0.2) return 'text-orange-700 dark:text-orange-400';
  return 'text-red-700 dark:text-red-400';
}

function getNdviBg(ndvi: number): string {
  if (ndvi >= 0.6) return 'bg-emerald-50 dark:bg-emerald-950/40';
  if (ndvi >= 0.4) return 'bg-yellow-50 dark:bg-yellow-950/40';
  if (ndvi >= 0.2) return 'bg-orange-50 dark:bg-orange-950/40';
  return 'bg-red-50 dark:bg-red-950/40';
}

function formatDaysAgo(isoDate: string): string {
  const diff = Math.floor(
    (Date.now() - new Date(isoDate).getTime()) / (1000 * 60 * 60 * 24)
  );
  if (diff <= 0) return 'اليوم';
  if (diff === 1) return 'أمس';
  return `قبل ${diff} أيام`;
}

function getDiseaseWarning(
  diseaseRisk?: RiskLevel,
  cropType?: string
): string | null {
  if (!diseaseRisk || diseaseRisk === 'low') return null;

  const cropAr: Record<string, string> = {
    wheat: 'القمح',
    barley: 'الشعير',
    tomato: 'الطماطم',
    date_palm: 'النخيل',
  };

  const crop = cropAr[cropType ?? ''] ?? cropType ?? '';

  if (diseaseRisk === 'critical') {
    return `خطر مرض ${crop} حرج — تدخل فوري مطلوب`;
  }
  if (diseaseRisk === 'high') {
    return `خطر صدأ ${crop} عالي — نافذة الرش: مناسبة`;
  }
  return `خطر صدأ ${crop} متوسط — نافذة الرش: مناسبة`;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface MetricCellProps {
  icon: React.ReactNode;
  value: string;
  labelAr: string;
  colorClass?: string;
  bgClass?: string;
}

function MetricCell({ icon, value, labelAr, colorClass, bgClass }: MetricCellProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-0.5 px-2 py-1.5 rounded-md min-w-0',
        bgClass ?? 'bg-gray-50 dark:bg-gray-800'
      )}
    >
      <div className={cn('flex items-center gap-1 text-sm font-semibold', colorClass ?? 'text-gray-900 dark:text-gray-100')}>
        {icon}
        <span className="truncate">{value}</span>
      </div>
      <span className="text-[10px] text-gray-500 dark:text-gray-400 leading-none">
        {labelAr}
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function ExpertView({
  fieldId,
  cropType,
  ndvi,
  temperature,
  humidity,
  windSpeed,
  precipitation,
  growthStage,
  diseaseRisk,
  pestRisk,
  soilMoisture,
  lastIrrigation,
  daysToHarvest,
}: ExpertViewProps) {
  const diseaseConfig = diseaseRisk ? RISK_CONFIG[diseaseRisk] : null;
  const pestConfig = pestRisk ? RISK_CONFIG[pestRisk] : null;

  const warningMessage = useMemo(
    () => getDiseaseWarning(diseaseRisk, cropType),
    [diseaseRisk, cropType]
  );

  const irrigationAgo = useMemo(
    () => (lastIrrigation ? formatDaysAgo(lastIrrigation) : null),
    [lastIrrigation]
  );

  return (
    <div
      dir="rtl"
      className="w-full rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-sm overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <Eye className="h-4 w-4 text-blue-600 dark:text-blue-400 shrink-0" />
        <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">
          نظرة خبير
          <span className="text-gray-400 dark:text-gray-500 font-normal mr-1 text-xs">
            — Expert View
          </span>
        </h3>
        <span className="mr-auto text-[10px] text-gray-400 dark:text-gray-500 font-mono">
          {fieldId}
        </span>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-5 gap-1.5 p-2">
        {/* Temperature */}
        <MetricCell
          icon={<Thermometer className="h-3.5 w-3.5" />}
          value={temperature != null ? `${temperature}°C` : '—'}
          labelAr="الحرارة"
        />

        {/* Humidity */}
        <MetricCell
          icon={<Droplets className="h-3.5 w-3.5" />}
          value={humidity != null ? `${humidity}%` : '—'}
          labelAr="الرطوبة"
        />

        {/* NDVI */}
        <MetricCell
          icon={<Leaf className="h-3.5 w-3.5" />}
          value={ndvi != null ? ndvi.toFixed(2) : '—'}
          labelAr="NDVI"
          colorClass={ndvi != null ? getNdviColor(ndvi) : undefined}
          bgClass={ndvi != null ? getNdviBg(ndvi) : undefined}
        />

        {/* Disease Risk */}
        <MetricCell
          icon={<Bug className="h-3.5 w-3.5" />}
          value={diseaseConfig?.labelAr ?? '—'}
          labelAr="مرض"
          colorClass={diseaseConfig?.color}
          bgClass={diseaseConfig?.bg}
        />

        {/* Growth Stage */}
        <MetricCell
          icon={<Wheat className="h-3.5 w-3.5" />}
          value={growthStage ?? '—'}
          labelAr="مرحلة"
        />
      </div>

      {/* Secondary Row — wind, rain, soil moisture, pest risk */}
      <div className="grid grid-cols-4 gap-1.5 px-2 pb-2">
        <MetricCell
          icon={<Wind className="h-3.5 w-3.5" />}
          value={windSpeed != null ? `${windSpeed} كم/س` : '—'}
          labelAr="الرياح"
        />
        <MetricCell
          icon={<CloudRain className="h-3.5 w-3.5" />}
          value={precipitation != null ? `${precipitation} مم` : '—'}
          labelAr="الأمطار"
        />
        <MetricCell
          icon={<Droplets className="h-3.5 w-3.5" />}
          value={soilMoisture != null ? `${soilMoisture}%` : '—'}
          labelAr="رطوبة التربة"
        />
        <MetricCell
          icon={<Bug className="h-3.5 w-3.5" />}
          value={pestConfig?.labelAr ?? '—'}
          labelAr="آفات"
          colorClass={pestConfig?.color}
          bgClass={pestConfig?.bg}
        />
      </div>

      {/* Footer — warnings & harvest info */}
      <div className="border-t border-gray-200 dark:border-gray-700 px-3 py-2 space-y-1 bg-gray-50/50 dark:bg-gray-800/50">
        {/* Disease warning */}
        {warningMessage && (
          <div
            className={cn(
              'flex items-center gap-1.5 text-xs font-medium',
              diseaseRisk === 'critical'
                ? 'text-red-700 dark:text-red-400'
                : diseaseRisk === 'high'
                  ? 'text-orange-700 dark:text-orange-400'
                  : 'text-yellow-700 dark:text-yellow-400'
            )}
          >
            <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
            <span>{warningMessage}</span>
          </div>
        )}

        {/* Harvest & irrigation info */}
        {(daysToHarvest != null || irrigationAgo) && (
          <div className="flex items-center gap-3 text-[11px] text-gray-600 dark:text-gray-400">
            {daysToHarvest != null && (
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3 shrink-0" />
                الحصاد المتوقع: {daysToHarvest} يوم
              </span>
            )}
            {irrigationAgo && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3 shrink-0" />
                آخر ري: {irrigationAgo}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
