'use client';

/**
 * Growth Stages Timeline — مراحل النمو
 * Horizontal timeline from planting to harvest with stage indicators,
 * current stage highlight, NDVI targets, and Arabic stage names.
 */

import { useState, useMemo, useCallback } from 'react';
import { clsx } from 'clsx';
import { Droplets, Leaf } from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GrowthStage {
  id: string;
  name: string;
  nameAr: string;
  startDay: number;
  endDay: number;
  ndviTarget: number;
  waterNeed: 'low' | 'medium' | 'high';
  icon: string;
  tasks: string[];
  color: string;
}

export interface GrowthStagesTimelineProps {
  cropType: string;
  plantingDate: string;
  currentDay?: number;
  currentNdvi?: number;
  className?: string;
}

// ---------------------------------------------------------------------------
// Crop stage data
// ---------------------------------------------------------------------------

const WHEAT_STAGES: GrowthStage[] = [
  { id: 'germination', name: 'Germination', nameAr: 'انبات', startDay: 0, endDay: 15, ndviTarget: 0.15, waterNeed: 'low', icon: '\u{1F331}', tasks: ['ري خفيف للانبات', 'مراقبة كثافة البادرات', 'مكافحة الاعشاب المبكرة'], color: 'emerald' },
  { id: 'tillering', name: 'Tillering', nameAr: 'تفريع', startDay: 15, endDay: 45, ndviTarget: 0.35, waterNeed: 'medium', icon: '\u{1F33F}', tasks: ['تسميد نيتروجيني اول', 'ري منتظم كل 10 ايام', 'مراقبة الحشرات', 'مكافحة الاعشاب'], color: 'green' },
  { id: 'elongation', name: 'Elongation', nameAr: 'استطالة', startDay: 45, endDay: 75, ndviTarget: 0.55, waterNeed: 'high', icon: '\u{1F4CF}', tasks: ['تسميد نيتروجيني ثاني', 'ري غزير كل 7 ايام', 'مراقبة الصدأ', 'رصد حشرة المن'], color: 'teal' },
  { id: 'heading', name: 'Heading', nameAr: 'اسبال', startDay: 75, endDay: 100, ndviTarget: 0.7, waterNeed: 'high', icon: '\u{1F33E}', tasks: ['ري غزير منتظم', 'مكافحة صدأ الساق', 'تسميد ورقي بالعناصر الصغرى', 'مراقبة التبقع'], color: 'amber' },
  { id: 'flowering', name: 'Flowering', nameAr: 'ازهار', startDay: 100, endDay: 115, ndviTarget: 0.65, waterNeed: 'medium', icon: '\u{1F338}', tasks: ['تجنب الري الزائد', 'مراقبة حشرة السونة', 'عدم رش مبيدات فطرية اثناء الازهار'], color: 'pink' },
  { id: 'grain-filling', name: 'Grain Filling', nameAr: 'امتلاء الحبة', startDay: 115, endDay: 135, ndviTarget: 0.55, waterNeed: 'medium', icon: '\u{1F7E1}', tasks: ['ري معتدل', 'مراقبة جودة الحبوب', 'تحضير معدات الحصاد', 'تقييم الانتاجية'], color: 'yellow' },
  { id: 'maturity', name: 'Maturity', nameAr: 'نضج', startDay: 135, endDay: 150, ndviTarget: 0.3, waterNeed: 'low', icon: '\u{1F7E4}', tasks: ['ايقاف الري', 'فحص رطوبة الحبوب (< 14%)', 'حصاد عند الجفاف', 'تخزين سليم'], color: 'orange' },
];

const BARLEY_STAGES: GrowthStage[] = [
  { id: 'germination', name: 'Germination', nameAr: 'انبات', startDay: 0, endDay: 12, ndviTarget: 0.14, waterNeed: 'low', icon: '\u{1F331}', tasks: ['ري خفيف للانبات', 'مراقبة كثافة البادرات'], color: 'emerald' },
  { id: 'tillering', name: 'Tillering', nameAr: 'تفريع', startDay: 12, endDay: 40, ndviTarget: 0.33, waterNeed: 'medium', icon: '\u{1F33F}', tasks: ['تسميد نيتروجيني', 'ري كل 12 يوم', 'مكافحة الاعشاب'], color: 'green' },
  { id: 'elongation', name: 'Elongation', nameAr: 'استطالة', startDay: 40, endDay: 65, ndviTarget: 0.52, waterNeed: 'high', icon: '\u{1F4CF}', tasks: ['ري غزير كل 8 ايام', 'مراقبة التبقع الشبكي', 'تسميد ثاني'], color: 'teal' },
  { id: 'heading', name: 'Heading', nameAr: 'اسبال', startDay: 65, endDay: 85, ndviTarget: 0.65, waterNeed: 'high', icon: '\u{1F33E}', tasks: ['ري منتظم', 'مكافحة البياض الدقيقي', 'تسميد ورقي'], color: 'amber' },
  { id: 'flowering', name: 'Flowering', nameAr: 'ازهار', startDay: 85, endDay: 95, ndviTarget: 0.6, waterNeed: 'medium', icon: '\u{1F338}', tasks: ['تجنب الاجهاد المائي', 'مراقبة حشرة المن'], color: 'pink' },
  { id: 'grain-filling', name: 'Grain Filling', nameAr: 'امتلاء الحبة', startDay: 95, endDay: 115, ndviTarget: 0.5, waterNeed: 'medium', icon: '\u{1F7E1}', tasks: ['ري معتدل', 'مراقبة جودة الحبوب'], color: 'yellow' },
  { id: 'maturity', name: 'Maturity', nameAr: 'نضج', startDay: 115, endDay: 130, ndviTarget: 0.28, waterNeed: 'low', icon: '\u{1F7E4}', tasks: ['ايقاف الري', 'حصاد عند رطوبة < 13%'], color: 'orange' },
];

const TOMATO_STAGES: GrowthStage[] = [
  { id: 'seedling', name: 'Seedling', nameAr: 'شتلة', startDay: 0, endDay: 20, ndviTarget: 0.18, waterNeed: 'low', icon: '\u{1F331}', tasks: ['ري خفيف يومي', 'تظليل الشتلات', 'مراقبة الذبابة البيضاء'], color: 'emerald' },
  { id: 'vegetative', name: 'Vegetative', nameAr: 'نمو خضري', startDay: 20, endDay: 45, ndviTarget: 0.42, waterNeed: 'medium', icon: '\u{1F33F}', tasks: ['تسميد متوازن NPK', 'تربيط النباتات', 'ازالة الفروع الجانبية', 'ري بالتنقيط'], color: 'green' },
  { id: 'flowering', name: 'Flowering', nameAr: 'ازهار', startDay: 45, endDay: 65, ndviTarget: 0.6, waterNeed: 'high', icon: '\u{1F338}', tasks: ['ري منتظم', 'تسميد بوتاسي', 'مكافحة التوتا ابسلوتا', 'هز النباتات للتلقيح'], color: 'pink' },
  { id: 'fruit-setting', name: 'Fruit Setting', nameAr: 'عقد الثمار', startDay: 65, endDay: 85, ndviTarget: 0.65, waterNeed: 'high', icon: '\u{1F345}', tasks: ['ري غزير منتظم', 'تسميد كالسيوم', 'مراقبة تعفن الطرف الزهري', 'دعم الثمار'], color: 'red' },
  { id: 'ripening', name: 'Ripening', nameAr: 'نضج', startDay: 85, endDay: 110, ndviTarget: 0.5, waterNeed: 'medium', icon: '\u{1F7E1}', tasks: ['تقليل الري تدريجيا', 'حصاد الثمار الناضجة', 'فرز وتعبئة', 'مراقبة الآفات'], color: 'yellow' },
  { id: 'harvest', name: 'Harvest', nameAr: 'حصاد', startDay: 110, endDay: 140, ndviTarget: 0.35, waterNeed: 'low', icon: '\u{1F4E6}', tasks: ['حصاد متكرر كل 3-5 ايام', 'فرز حسب الجودة', 'تخزين مبرد', 'تسويق'], color: 'orange' },
];

const SORGHUM_STAGES: GrowthStage[] = [
  { id: 'germination', name: 'Germination', nameAr: 'انبات', startDay: 0, endDay: 10, ndviTarget: 0.12, waterNeed: 'low', icon: '\u{1F331}', tasks: ['ري خفيف', 'مراقبة الانبات'], color: 'emerald' },
  { id: 'vegetative', name: 'Vegetative', nameAr: 'نمو خضري', startDay: 10, endDay: 40, ndviTarget: 0.38, waterNeed: 'medium', icon: '\u{1F33F}', tasks: ['تسميد نيتروجيني', 'مكافحة الاعشاب', 'ري منتظم'], color: 'green' },
  { id: 'elongation', name: 'Elongation', nameAr: 'استطالة', startDay: 40, endDay: 65, ndviTarget: 0.58, waterNeed: 'high', icon: '\u{1F4CF}', tasks: ['ري غزير', 'مراقبة دودة الذرة', 'تسميد ثاني'], color: 'teal' },
  { id: 'heading', name: 'Heading', nameAr: 'طرد السنابل', startDay: 65, endDay: 80, ndviTarget: 0.68, waterNeed: 'high', icon: '\u{1F33E}', tasks: ['ري غزير منتظم', 'مكافحة حشرة المن', 'مراقبة الطيور'], color: 'amber' },
  { id: 'grain-filling', name: 'Grain Filling', nameAr: 'امتلاء الحبة', startDay: 80, endDay: 105, ndviTarget: 0.52, waterNeed: 'medium', icon: '\u{1F7E1}', tasks: ['ري معتدل', 'حماية من الطيور', 'تقييم الانتاجية'], color: 'yellow' },
  { id: 'maturity', name: 'Maturity', nameAr: 'نضج', startDay: 105, endDay: 120, ndviTarget: 0.25, waterNeed: 'low', icon: '\u{1F7E4}', tasks: ['ايقاف الري', 'حصاد يدوي او آلي', 'تجفيف وتخزين'], color: 'orange' },
];

const CROP_STAGES: Record<string, GrowthStage[]> = {
  wheat: WHEAT_STAGES,
  barley: BARLEY_STAGES,
  sorghum: SORGHUM_STAGES,
  tomato: TOMATO_STAGES,
};

const CROP_LABELS: Record<string, { name: string; nameAr: string }> = {
  wheat: { name: 'Wheat', nameAr: 'قمح' },
  barley: { name: 'Barley', nameAr: 'شعير' },
  sorghum: { name: 'Sorghum', nameAr: 'ذرة رفيعة' },
  tomato: { name: 'Tomato', nameAr: 'طماطم' },
};

// ---------------------------------------------------------------------------
// Color maps (Tailwind-safe static classes)
// ---------------------------------------------------------------------------

const DOT_BG: Record<string, string> = {
  emerald: 'bg-emerald-500', green: 'bg-green-500', teal: 'bg-teal-500',
  amber: 'bg-amber-500', pink: 'bg-pink-500', yellow: 'bg-yellow-500',
  orange: 'bg-orange-500', red: 'bg-red-500',
};

const DOT_RING: Record<string, string> = {
  emerald: 'ring-emerald-300 dark:ring-emerald-700', green: 'ring-green-300 dark:ring-green-700',
  teal: 'ring-teal-300 dark:ring-teal-700', amber: 'ring-amber-300 dark:ring-amber-700',
  pink: 'ring-pink-300 dark:ring-pink-700', yellow: 'ring-yellow-300 dark:ring-yellow-700',
  orange: 'ring-orange-300 dark:ring-orange-700', red: 'ring-red-300 dark:ring-red-700',
};

const ACTIVE_CARD_BG: Record<string, string> = {
  emerald: 'bg-emerald-100 dark:bg-emerald-900/40 border-emerald-400 dark:border-emerald-600',
  green: 'bg-green-100 dark:bg-green-900/40 border-green-400 dark:border-green-600',
  teal: 'bg-teal-100 dark:bg-teal-900/40 border-teal-400 dark:border-teal-600',
  amber: 'bg-amber-100 dark:bg-amber-900/40 border-amber-400 dark:border-amber-600',
  pink: 'bg-pink-100 dark:bg-pink-900/40 border-pink-400 dark:border-pink-600',
  yellow: 'bg-yellow-100 dark:bg-yellow-900/40 border-yellow-400 dark:border-yellow-600',
  orange: 'bg-orange-100 dark:bg-orange-900/40 border-orange-400 dark:border-orange-600',
  red: 'bg-red-100 dark:bg-red-900/40 border-red-400 dark:border-red-600',
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const WATER_ICONS: Record<string, string> = { low: '\u{1F4A7}', medium: '\u{1F4A7}\u{1F4A7}', high: '\u{1F4A7}\u{1F4A7}\u{1F4A7}' };
const WATER_LABELS: Record<string, string> = { low: 'منخفض', medium: 'متوسط', high: 'عالي' };

function formatDate(plantingDate: string, dayOffset: number): string {
  const d = new Date(plantingDate);
  d.setDate(d.getDate() + dayOffset);
  return d.toLocaleDateString('ar-SA', { month: 'short', day: 'numeric' });
}

function getNdviStatus(actual: number | undefined, target: number) {
  if (actual === undefined) return { labelAr: 'لا توجد بيانات', color: 'text-gray-400' };
  const pct = target > 0 ? ((actual - target) / target) * 100 : 0;
  if (pct >= -5) return { labelAr: 'على المسار', color: 'text-emerald-600 dark:text-emerald-400' };
  if (pct >= -20) return { labelAr: 'متأخر قليلا', color: 'text-amber-600 dark:text-amber-400' };
  return { labelAr: 'متأخر', color: 'text-red-600 dark:text-red-400' };
}

function getActiveStageIndex(stages: GrowthStage[], currentDay?: number): number {
  if (currentDay === undefined) return -1;
  for (let i = 0; i < stages.length; i++) {
    if (currentDay >= stages[i]!.startDay && currentDay <= stages[i]!.endDay) return i;
  }
  if (stages.length > 0 && currentDay > stages[stages.length - 1]!.endDay) return stages.length - 1;
  return -1;
}

function getProgressInStage(stage: GrowthStage, currentDay: number): number {
  const duration = stage.endDay - stage.startDay;
  if (duration === 0) return 100;
  return Math.min(100, Math.max(0, ((currentDay - stage.startDay) / duration) * 100));
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function TasksTooltip({ tasks, visible }: { tasks: string[]; visible: boolean }) {
  if (!visible || tasks.length === 0) return null;
  return (
    <div
      className={clsx(
        'absolute bottom-full right-1/2 translate-x-1/2 mb-2 z-30',
        'w-56 rounded-lg border border-gray-200 dark:border-gray-700',
        'bg-white dark:bg-gray-800 shadow-lg p-3',
      )}
    >
      <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1.5">
        المهام المطلوبة
      </p>
      <ul className="space-y-1">
        {tasks.map((task, i) => (
          <li key={i} className="text-xs text-gray-700 dark:text-gray-300 flex gap-1.5 items-start">
            <span className="text-gray-400 mt-0.5 shrink-0">\u25CF</span>
            <span>{task}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function NdviBar({ target, actual }: { target: number; actual?: number }) {
  const targetPct = target * 100;
  const actualPct = actual !== undefined ? actual * 100 : undefined;

  return (
    <div className="mt-1.5">
      <div className="flex justify-between text-[10px] text-gray-500 dark:text-gray-400 mb-0.5">
        <span>NDVI</span>
        <span>{target.toFixed(2)}</span>
      </div>
      <div className="relative h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className="absolute inset-y-0 start-0 bg-gray-300 dark:bg-gray-600 rounded-full"
          style={{ width: `${targetPct}%` }}
        />
        {actualPct !== undefined && (
          <div
            className={clsx(
              'absolute inset-y-0 start-0 rounded-full transition-all duration-500',
              actualPct >= targetPct * 0.95
                ? 'bg-emerald-500'
                : actualPct >= targetPct * 0.8
                  ? 'bg-amber-500'
                  : 'bg-red-500',
            )}
            style={{ width: `${Math.min(actualPct, 100)}%` }}
          />
        )}
      </div>
      {actual !== undefined && (
        <div className="text-[10px] text-gray-500 dark:text-gray-400 mt-0.5 text-center">
          الفعلي: {actual.toFixed(2)}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function GrowthStagesTimeline({
  cropType,
  plantingDate,
  currentDay,
  currentNdvi,
  className,
}: GrowthStagesTimelineProps) {
  const [hoveredStage, setHoveredStage] = useState<string | null>(null);

  const stages = useMemo(() => CROP_STAGES[cropType] ?? WHEAT_STAGES, [cropType]);
  const cropLabel = CROP_LABELS[cropType] ?? CROP_LABELS.wheat;
  const activeIndex = useMemo(() => getActiveStageIndex(stages, currentDay), [stages, currentDay]);
  const totalDays = stages[stages.length - 1].endDay;

  const activeStage = activeIndex >= 0 ? stages[activeIndex] : null;
  const ndviStatus = activeStage ? getNdviStatus(currentNdvi, activeStage.ndviTarget) : null;

  const handleMouseEnter = useCallback((id: string) => setHoveredStage(id), []);
  const handleMouseLeave = useCallback(() => setHoveredStage(null), []);

  const currentDayPct = currentDay !== undefined ? (currentDay / totalDays) * 100 : null;

  return (
    <div dir="rtl" className={clsx('w-full', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Leaf className="h-4 w-4 text-green-600 dark:text-green-400" />
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            مراحل النمو
          </h3>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            \u2014 {cropLabel.nameAr} ({cropLabel.name})
          </span>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span>
            تاريخ الزراعة:{' '}
            {new Date(plantingDate).toLocaleDateString('ar-SA', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
            })}
          </span>
          {currentDay !== undefined && (
            <span className="font-medium text-gray-700 dark:text-gray-300">
              اليوم {currentDay} من {totalDays}
            </span>
          )}
        </div>
      </div>

      {/* Current stage status bar */}
      {activeStage && currentDay !== undefined && (
        <div
          className={clsx(
            'flex items-center justify-between gap-4 mb-4 px-4 py-2.5 rounded-lg border',
            ACTIVE_CARD_BG[activeStage.color],
          )}
        >
          <div className="flex items-center gap-3">
            <span className="text-xl">{activeStage.icon}</span>
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                المرحلة الحالية: {activeStage.nameAr}
                <span className="text-gray-400 dark:text-gray-500 font-normal mr-1 text-xs">
                  ({activeStage.name})
                </span>
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                يوم {currentDay} \u2014 تقدم المرحلة{' '}
                {Math.round(getProgressInStage(activeStage, currentDay))}%
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-center">
              <p className="text-[10px] text-gray-500 dark:text-gray-400">
                <Droplets className="h-3 w-3 inline" /> الاحتياج المائي
              </p>
              <p className="text-sm">{WATER_ICONS[activeStage.waterNeed]}</p>
            </div>
            {ndviStatus && (
              <div className="text-center">
                <p className="text-[10px] text-gray-500 dark:text-gray-400">حالة NDVI</p>
                <p className={clsx('text-xs font-semibold', ndviStatus.color)}>
                  {currentNdvi !== undefined ? currentNdvi.toFixed(2) : '\u2014'} /{' '}
                  {activeStage.ndviTarget.toFixed(2)}
                </p>
                <p className={clsx('text-[10px]', ndviStatus.color)}>{ndviStatus.labelAr}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Scrollable timeline */}
      <div className="overflow-x-auto pb-2 -mx-1 px-1">
        <div className="min-w-[640px]">
          <div className="relative mx-6 mt-2">
            {/* Connecting line */}
            <div className="absolute top-4 right-0 left-0 h-0.5 bg-gray-200 dark:bg-gray-700" />

            {/* Completed fill */}
            {currentDayPct !== null && (
              <div
                className="absolute top-4 right-0 h-0.5 bg-emerald-400 dark:bg-emerald-600 transition-all duration-700"
                style={{ width: `${Math.min(currentDayPct, 100)}%` }}
              />
            )}

            {/* Current day marker */}
            {currentDayPct !== null && currentDayPct <= 100 && (
              <div
                className="absolute top-0 z-20 flex flex-col items-center -translate-x-1/2 transition-all duration-700"
                style={{ right: `${currentDayPct}%` }}
              >
                <div className="w-2.5 h-2.5 rounded-full bg-blue-500 ring-4 ring-blue-200 dark:ring-blue-800 animate-pulse" />
                <div className="mt-1 text-[9px] font-bold text-blue-600 dark:text-blue-400 whitespace-nowrap">
                  \u25BC يوم {currentDay}
                </div>
              </div>
            )}

            {/* Stage dots */}
            <div className="relative flex justify-between">
              {stages.map((stage, i) => {
                const isActive = i === activeIndex;
                const isCompleted = activeIndex >= 0 && i < activeIndex;

                return (
                  <div
                    key={stage.id}
                    className="relative flex flex-col items-center"
                    style={{ width: `${((stage.endDay - stage.startDay) / totalDays) * 100}%` }}
                    onMouseEnter={() => handleMouseEnter(stage.id)}
                    onMouseLeave={handleMouseLeave}
                  >
                    {/* Dot */}
                    <div
                      className={clsx(
                        'w-8 h-8 rounded-full flex items-center justify-center text-sm cursor-pointer',
                        'transition-all duration-300 relative z-10',
                        isActive && clsx(DOT_BG[stage.color], 'ring-4', DOT_RING[stage.color], 'scale-110 shadow-md'),
                        isCompleted && clsx(DOT_BG[stage.color], 'opacity-80'),
                        !isActive && !isCompleted && 'bg-gray-200 dark:bg-gray-700',
                      )}
                    >
                      <span
                        className={clsx(
                          'text-base',
                          !isActive && !isCompleted && 'grayscale opacity-60',
                        )}
                      >
                        {stage.icon}
                      </span>
                    </div>

                    {/* Tasks tooltip */}
                    <TasksTooltip tasks={stage.tasks} visible={hoveredStage === stage.id} />

                    {/* Stage info below */}
                    <div className="mt-2 text-center w-full px-0.5">
                      <p
                        className={clsx(
                          'text-xs font-semibold truncate',
                          isActive
                            ? 'text-gray-900 dark:text-gray-100'
                            : 'text-gray-600 dark:text-gray-400',
                        )}
                      >
                        {stage.nameAr}
                      </p>
                      <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">
                        {formatDate(plantingDate, stage.startDay)} \u2013{' '}
                        {formatDate(plantingDate, stage.endDay)}
                      </p>
                      <p className="text-[10px] text-gray-400 dark:text-gray-500">
                        يوم {stage.startDay}\u2013{stage.endDay}
                      </p>

                      {/* Water need */}
                      <div className="mt-1 flex items-center justify-center gap-0.5">
                        <span className="text-[10px]">{WATER_ICONS[stage.waterNeed]}</span>
                        <span className="text-[9px] text-gray-400 dark:text-gray-500">
                          {WATER_LABELS[stage.waterNeed]}
                        </span>
                      </div>

                      {/* NDVI mini bar */}
                      {isActive && currentNdvi !== undefined ? (
                        <NdviBar target={stage.ndviTarget} actual={currentNdvi} />
                      ) : (
                        <NdviBar target={stage.ndviTarget} />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap items-center justify-center gap-x-4 gap-y-1.5 text-[10px] text-gray-500 dark:text-gray-400">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          اليوم الحالي
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-0.5 bg-emerald-400 inline-block rounded" />
          المراحل المكتملة
        </span>
        <span className="flex items-center gap-1">{'💧'} منخفض</span>
        <span className="flex items-center gap-1">{'💧💧'} متوسط</span>
        <span className="flex items-center gap-1">{'💧💧💧'} عالي</span>
        <span className="flex items-center gap-1 cursor-help" title="مرر الماوس على المرحلة لعرض المهام">
          مرر للمهام
        </span>
      </div>
    </div>
  );
}
