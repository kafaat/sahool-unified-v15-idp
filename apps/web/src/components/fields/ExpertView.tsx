'use client';

/**
 * Expert View — نظرة خبير
 * xarvio-inspired all-in-one field status card showing NDVI, weather,
 * soil, crop stage, disease/pest risk in a single compact card.
 *
 * Arabic-first with English secondary labels.
 */

import React, { useMemo } from 'react';
import { clsx } from 'clsx';
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
  Sun,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface ExpertViewProps {
  fieldId: string;
  fieldName?: string;
  cropType: string;
  areaHectares?: number;
  ndvi?: number;
  ndviTrend?: 'up' | 'down' | 'stable';
  temperature?: number;
  humidity?: number;
  windSpeed?: number;
  precipitation?: number;
  solarRadiation?: number;
  growthStage?: string;
  growthStageAr?: string;
  diseaseRisk?: RiskLevel;
  pestRisk?: RiskLevel;
  soilMoisture?: number;
  soilTemperature?: number;
  soilPH?: number;
  lastIrrigation?: string;
  nextIrrigation?: string;
  daysToHarvest?: number;
  className?: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RISK_CONFIG: Record<RiskLevel, { labelAr: string; color: string; bg: string }> = {
  low: {
    labelAr: 'منخفض',
    color: 'text-emerald-700 dark:text-emerald-400',
    bg: 'bg-emerald-50 dark:bg-emerald-950/40',
  },
  medium: {
    labelAr: 'متوسط',
    color: 'text-yellow-700 dark:text-yellow-400',
    bg: 'bg-yellow-50 dark:bg-yellow-950/40',
  },
  high: {
    labelAr: 'عالي',
    color: 'text-orange-700 dark:text-orange-400',
    bg: 'bg-orange-50 dark:bg-orange-950/40',
  },
  critical: {
    labelAr: 'حرج',
    color: 'text-red-700 dark:text-red-400',
    bg: 'bg-red-50 dark:bg-red-950/40',
  },
};

const CROP_NAMES_AR: Record<string, string> = {
  wheat: 'القمح',
  barley: 'الشعير',
  tomato: 'الطماطم',
  date_palm: 'النخيل',
  cucumber: 'الخيار',
  onion: 'البصل',
  sorghum: 'الذرة الرفيعة',
  coffee: 'البن',
  banana: 'الموز',
  mango: 'المانجو',
  sesame: 'السمسم',
  qat: 'القات',
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

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

function getNdviHealthAr(ndvi: number): string {
  if (ndvi >= 0.6) return 'صحي';
  if (ndvi >= 0.4) return 'معتدل';
  if (ndvi >= 0.2) return 'مجهد';
  return 'حرج';
}

function formatDaysAgo(isoDate: string): string {
  const diff = Math.floor(
    (Date.now() - new Date(isoDate).getTime()) / (1000 * 60 * 60 * 24),
  );
  if (diff <= 0) return 'اليوم';
  if (diff === 1) return 'أمس';
  return `قبل ${diff} أيام`;
}

function formatDaysUntil(isoDate: string): string {
  const diff = Math.ceil(
    (new Date(isoDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
  );
  if (diff <= 0) return 'اليوم';
  if (diff === 1) return 'غدا';
  return `بعد ${diff} أيام`;
}

function getDiseaseWarning(diseaseRisk?: RiskLevel, cropType?: string): string | null {
  if (!diseaseRisk || diseaseRisk === 'low') return null;
  const crop = CROP_NAMES_AR[cropType ?? ''] ?? cropType ?? '';
  if (diseaseRisk === 'critical') return `خطر مرض ${crop} حرج — تدخل فوري مطلوب`;
  if (diseaseRisk === 'high') return `خطر مرض ${crop} عالي — نافذة الرش: مناسبة`;
  return `خطر مرض ${crop} متوسط — مراقبة مطلوبة`;
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
  subValue?: string;
}

function MetricCell({ icon, value, labelAr, colorClass, bgClass, subValue }: MetricCellProps) {
  return (
    <div
      className={clsx(
        'flex flex-col items-center justify-center gap-0.5 px-2 py-2 rounded-lg min-w-0',
        bgClass ?? 'bg-gray-50 dark:bg-gray-800',
      )}
    >
      <div
        className={clsx(
          'flex items-center gap-1 text-sm font-semibold',
          colorClass ?? 'text-gray-900 dark:text-gray-100',
        )}
      >
        {icon}
        <span className="truncate">{value}</span>
      </div>
      <span className="text-[10px] text-gray-500 dark:text-gray-400 leading-none">
        {labelAr}
      </span>
      {subValue && (
        <span className="text-[9px] text-gray-400 dark:text-gray-500 leading-none">
          {subValue}
        </span>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function ExpertView({
  fieldId,
  fieldName,
  cropType,
  areaHectares,
  ndvi,
  ndviTrend,
  temperature,
  humidity,
  windSpeed,
  precipitation,
  solarRadiation,
  growthStage,
  growthStageAr,
  diseaseRisk,
  pestRisk,
  soilMoisture,
  soilTemperature,
  soilPH,
  lastIrrigation,
  nextIrrigation,
  daysToHarvest,
  className,
}: ExpertViewProps) {
  const diseaseConfig = diseaseRisk ? RISK_CONFIG[diseaseRisk] : null;
  const pestConfig = pestRisk ? RISK_CONFIG[pestRisk] : null;
  const cropNameAr = CROP_NAMES_AR[cropType] ?? cropType;

  const warningMessage = useMemo(
    () => getDiseaseWarning(diseaseRisk, cropType),
    [diseaseRisk, cropType],
  );

  const irrigationAgo = useMemo(
    () => (lastIrrigation ? formatDaysAgo(lastIrrigation) : null),
    [lastIrrigation],
  );

  const irrigationNext = useMemo(
    () => (nextIrrigation ? formatDaysUntil(nextIrrigation) : null),
    [nextIrrigation],
  );

  return (
    <div
      dir="rtl"
      className={clsx(
        'w-full rounded-xl border border-gray-200 dark:border-gray-700',
        'bg-white dark:bg-gray-900 shadow-sm overflow-hidden',
        className,
      )}
    >
      {/* ---- Header ---- */}
      <div className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-l from-green-50 to-blue-50 dark:from-green-950/30 dark:to-blue-950/30 border-b border-gray-200 dark:border-gray-700">
        <Eye className="h-4 w-4 text-blue-600 dark:text-blue-400 shrink-0" />
        <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">
          نظرة خبير
          <span className="text-gray-400 dark:text-gray-500 font-normal mr-1 text-xs">
            Expert View
          </span>
        </h3>
        <div className="mr-auto flex items-center gap-2">
          {fieldName && (
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
              {fieldName}
            </span>
          )}
          <span className="text-[10px] text-gray-400 dark:text-gray-500 font-mono">
            {fieldId}
          </span>
        </div>
      </div>

      {/* ---- Crop + Area bar ---- */}
      <div className="flex items-center gap-3 px-4 py-1.5 bg-gray-50/50 dark:bg-gray-800/50 border-b border-gray-100 dark:border-gray-800">
        <span className="text-xs text-gray-600 dark:text-gray-400">
          <Wheat className="h-3 w-3 inline ml-1" />
          {cropNameAr}
        </span>
        {growthStageAr && (
          <span className="text-xs text-gray-500 dark:text-gray-400">
            المرحلة: <span className="font-medium text-gray-700 dark:text-gray-300">{growthStageAr}</span>
            {growthStage && <span className="text-gray-400 mr-1">({growthStage})</span>}
          </span>
        )}
        {areaHectares != null && (
          <span className="text-xs text-gray-400 dark:text-gray-500 mr-auto">
            {areaHectares} هكتار
          </span>
        )}
      </div>

      {/* ---- Primary metrics: weather + NDVI ---- */}
      <div className="grid grid-cols-5 gap-1.5 p-3">
        <MetricCell
          icon={<Thermometer className="h-3.5 w-3.5" />}
          value={temperature != null ? `${temperature}°C` : '—'}
          labelAr="الحرارة"
        />
        <MetricCell
          icon={<Droplets className="h-3.5 w-3.5" />}
          value={humidity != null ? `${humidity}%` : '—'}
          labelAr="الرطوبة"
        />
        <MetricCell
          icon={<Leaf className="h-3.5 w-3.5" />}
          value={ndvi != null ? ndvi.toFixed(2) : '—'}
          labelAr="NDVI"
          colorClass={ndvi != null ? getNdviColor(ndvi) : undefined}
          bgClass={ndvi != null ? getNdviBg(ndvi) : undefined}
          subValue={ndvi != null ? getNdviHealthAr(ndvi) : undefined}
        />
        <MetricCell
          icon={<Bug className="h-3.5 w-3.5" />}
          value={diseaseConfig?.labelAr ?? '—'}
          labelAr="مرض"
          colorClass={diseaseConfig?.color}
          bgClass={diseaseConfig?.bg}
        />
        <MetricCell
          icon={
            ndviTrend === 'up' ? (
              <TrendingUp className="h-3.5 w-3.5" />
            ) : ndviTrend === 'down' ? (
              <TrendingDown className="h-3.5 w-3.5" />
            ) : (
              <Wheat className="h-3.5 w-3.5" />
            )
          }
          value={growthStageAr ?? growthStage ?? '—'}
          labelAr="المرحلة"
        />
      </div>

      {/* ---- Secondary metrics: wind, rain, soil, pests ---- */}
      <div className="grid grid-cols-5 gap-1.5 px-3 pb-3">
        <MetricCell
          icon={<Wind className="h-3.5 w-3.5" />}
          value={windSpeed != null ? `${windSpeed} كم/س` : '—'}
          labelAr="الرياح"
        />
        <MetricCell
          icon={<CloudRain className="h-3.5 w-3.5" />}
          value={precipitation != null ? `${precipitation} مم` : '—'}
          labelAr="الامطار"
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
        <MetricCell
          icon={<Sun className="h-3.5 w-3.5" />}
          value={solarRadiation != null ? `${solarRadiation}` : soilPH != null ? `${soilPH}` : '—'}
          labelAr={solarRadiation != null ? 'إشعاع' : 'pH التربة'}
        />
      </div>

      {/* ---- Soil details row (if data available) ---- */}
      {(soilTemperature != null || soilPH != null) && (
        <div className="grid grid-cols-3 gap-1.5 px-3 pb-3">
          {soilTemperature != null && (
            <MetricCell
              icon={<Thermometer className="h-3.5 w-3.5" />}
              value={`${soilTemperature}°C`}
              labelAr="حرارة التربة"
            />
          )}
          {soilPH != null && solarRadiation != null && (
            <MetricCell
              icon={<Droplets className="h-3.5 w-3.5" />}
              value={`${soilPH}`}
              labelAr="pH التربة"
            />
          )}
        </div>
      )}

      {/* ---- Footer: warnings, harvest, irrigation ---- */}
      <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-2.5 space-y-1.5 bg-gray-50/50 dark:bg-gray-800/50">
        {/* Disease warning */}
        {warningMessage && (
          <div
            className={clsx(
              'flex items-center gap-1.5 text-xs font-medium rounded-lg px-2.5 py-1.5',
              diseaseRisk === 'critical'
                ? 'text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-950/30'
                : diseaseRisk === 'high'
                  ? 'text-orange-700 dark:text-orange-400 bg-orange-50 dark:bg-orange-950/30'
                  : 'text-yellow-700 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-950/30',
            )}
          >
            <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
            <span>{warningMessage}</span>
          </div>
        )}

        {/* Harvest & irrigation info */}
        {(daysToHarvest != null || irrigationAgo || irrigationNext) && (
          <div className="flex items-center flex-wrap gap-3 text-[11px] text-gray-600 dark:text-gray-400">
            {daysToHarvest != null && (
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3 shrink-0" />
                الحصاد المتوقع: <span className="font-medium">{daysToHarvest} يوم</span>
              </span>
            )}
            {irrigationAgo && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3 shrink-0" />
                آخر ري: <span className="font-medium">{irrigationAgo}</span>
              </span>
            )}
            {irrigationNext && (
              <span className="flex items-center gap-1">
                <Droplets className="h-3 w-3 shrink-0" />
                الري القادم: <span className="font-medium">{irrigationNext}</span>
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
