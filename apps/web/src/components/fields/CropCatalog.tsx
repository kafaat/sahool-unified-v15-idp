'use client';

/**
 * Crop Catalog — كتالوج المحاصيل
 * 12 Yemen crop variety visual cards with Arabic + English names,
 * seasonal info, water requirements, yield data, and temperature ranges.
 */

import { useState, useMemo } from 'react';
import { clsx } from 'clsx';
import {
  Droplets,
  Thermometer,
  CalendarDays,
  Wheat,
  Search,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CropVariety {
  code: string;
  name: string;
  nameAr: string;
  icon: string;
  category: 'grain' | 'vegetable' | 'fruit' | 'tree' | 'cash';
  categoryAr: string;
  season: string;
  seasonAr: string;
  plantingMonths: string;
  plantingMonthsAr: string;
  harvestMonths: string;
  harvestMonthsAr: string;
  daysToHarvest: number;
  waterNeed: 'low' | 'medium' | 'high';
  waterNeedMm: number;
  yieldTonsHa: number;
  soilTypes: string[];
  soilTypesAr: string[];
  temperatureRange: [number, number];
  gradient: string;
}

export interface CropCatalogProps {
  onSelect?: (crop: CropVariety) => void;
  selectedCrop?: string;
  category?: string;
  className?: string;
}

// ---------------------------------------------------------------------------
// Data — 12 Yemen crop varieties
// ---------------------------------------------------------------------------

const CROPS: CropVariety[] = [
  {
    code: 'wheat',
    name: 'Wheat',
    nameAr: 'قمح',
    icon: '\u{1F33E}',
    category: 'grain',
    categoryAr: 'حبوب',
    season: 'Winter',
    seasonAr: 'شتاء',
    plantingMonths: 'Oct\u2013Nov',
    plantingMonthsAr: 'اكتوبر\u2013نوفمبر',
    harvestMonths: 'Mar\u2013Apr',
    harvestMonthsAr: 'مارس\u2013ابريل',
    daysToHarvest: 150,
    waterNeed: 'medium',
    waterNeedMm: 450,
    yieldTonsHa: 4.5,
    soilTypes: ['Loam', 'Clay loam', 'Silt loam'],
    soilTypesAr: ['طميية', 'طينية طميية', 'غرينية طميية'],
    temperatureRange: [10, 25],
    gradient: 'from-amber-100 to-yellow-200',
  },
  {
    code: 'barley',
    name: 'Barley',
    nameAr: 'شعير',
    icon: '\u{1F33E}',
    category: 'grain',
    categoryAr: 'حبوب',
    season: 'Winter',
    seasonAr: 'شتاء',
    plantingMonths: 'Oct\u2013Nov',
    plantingMonthsAr: 'اكتوبر\u2013نوفمبر',
    harvestMonths: 'Feb\u2013Mar',
    harvestMonthsAr: 'فبراير\u2013مارس',
    daysToHarvest: 120,
    waterNeed: 'low',
    waterNeedMm: 300,
    yieldTonsHa: 3.5,
    soilTypes: ['Sandy loam', 'Loam', 'Clay loam'],
    soilTypesAr: ['رملية طميية', 'طميية', 'طينية طميية'],
    temperatureRange: [8, 24],
    gradient: 'from-yellow-100 to-amber-200',
  },
  {
    code: 'sorghum',
    name: 'Sorghum',
    nameAr: 'ذرة رفيعة',
    icon: '\u{1F33D}',
    category: 'grain',
    categoryAr: 'حبوب',
    season: 'Summer',
    seasonAr: 'صيف',
    plantingMonths: 'Apr\u2013May',
    plantingMonthsAr: 'ابريل\u2013مايو',
    harvestMonths: 'Aug\u2013Sep',
    harvestMonthsAr: 'اغسطس\u2013سبتمبر',
    daysToHarvest: 120,
    waterNeed: 'low',
    waterNeedMm: 350,
    yieldTonsHa: 2.5,
    soilTypes: ['Loam', 'Sandy loam', 'Clay'],
    soilTypesAr: ['طميية', 'رملية طميية', 'طينية'],
    temperatureRange: [20, 38],
    gradient: 'from-orange-100 to-red-200',
  },
  {
    code: 'tomato',
    name: 'Tomato',
    nameAr: 'طماطم',
    icon: '\u{1F345}',
    category: 'vegetable',
    categoryAr: 'خضروات',
    season: 'Spring',
    seasonAr: 'ربيع',
    plantingMonths: 'Feb\u2013Mar',
    plantingMonthsAr: 'فبراير\u2013مارس',
    harvestMonths: 'May\u2013Jun',
    harvestMonthsAr: 'مايو\u2013يونيو',
    daysToHarvest: 90,
    waterNeed: 'high',
    waterNeedMm: 500,
    yieldTonsHa: 25,
    soilTypes: ['Loam', 'Sandy loam', 'Silt loam'],
    soilTypesAr: ['طميية', 'رملية طميية', 'غرينية طميية'],
    temperatureRange: [18, 30],
    gradient: 'from-red-100 to-rose-200',
  },
  {
    code: 'onion',
    name: 'Onion',
    nameAr: 'بصل',
    icon: '\u{1F9C5}',
    category: 'vegetable',
    categoryAr: 'خضروات',
    season: 'Autumn',
    seasonAr: 'خريف',
    plantingMonths: 'Sep\u2013Oct',
    plantingMonthsAr: 'سبتمبر\u2013اكتوبر',
    harvestMonths: 'Jan\u2013Feb',
    harvestMonthsAr: 'يناير\u2013فبراير',
    daysToHarvest: 120,
    waterNeed: 'medium',
    waterNeedMm: 400,
    yieldTonsHa: 15,
    soilTypes: ['Loam', 'Sandy loam', 'Silt loam'],
    soilTypesAr: ['طميية', 'رملية طميية', 'غرينية طميية'],
    temperatureRange: [12, 28],
    gradient: 'from-purple-100 to-indigo-200',
  },
  {
    code: 'cucumber',
    name: 'Cucumber',
    nameAr: 'خيار',
    icon: '\u{1F952}',
    category: 'vegetable',
    categoryAr: 'خضروات',
    season: 'Spring',
    seasonAr: 'ربيع',
    plantingMonths: 'Feb\u2013Mar',
    plantingMonthsAr: 'فبراير\u2013مارس',
    harvestMonths: 'Apr\u2013May',
    harvestMonthsAr: 'ابريل\u2013مايو',
    daysToHarvest: 60,
    waterNeed: 'medium',
    waterNeedMm: 450,
    yieldTonsHa: 20,
    soilTypes: ['Loam', 'Sandy loam'],
    soilTypesAr: ['طميية', 'رملية طميية'],
    temperatureRange: [18, 32],
    gradient: 'from-green-100 to-emerald-200',
  },
  {
    code: 'date_palm',
    name: 'Date Palm',
    nameAr: 'نخيل',
    icon: '\u{1F334}',
    category: 'tree',
    categoryAr: 'اشجار',
    season: 'Perennial',
    seasonAr: 'دائم',
    plantingMonths: 'Feb\u2013Apr',
    plantingMonthsAr: 'فبراير\u2013ابريل',
    harvestMonths: 'Aug\u2013Oct',
    harvestMonthsAr: 'اغسطس\u2013اكتوبر',
    daysToHarvest: 180,
    waterNeed: 'medium',
    waterNeedMm: 600,
    yieldTonsHa: 8,
    soilTypes: ['Sandy loam', 'Loam', 'Sandy'],
    soilTypesAr: ['رملية طميية', 'طميية', 'رملية'],
    temperatureRange: [20, 45],
    gradient: 'from-emerald-100 to-teal-200',
  },
  {
    code: 'coffee',
    name: 'Coffee',
    nameAr: 'بن',
    icon: '\u2615',
    category: 'tree',
    categoryAr: 'اشجار',
    season: 'Perennial',
    seasonAr: 'دائم',
    plantingMonths: 'Jun\u2013Aug',
    plantingMonthsAr: 'يونيو\u2013اغسطس',
    harvestMonths: 'Nov\u2013Jan',
    harvestMonthsAr: 'نوفمبر\u2013يناير',
    daysToHarvest: 365,
    waterNeed: 'high',
    waterNeedMm: 800,
    yieldTonsHa: 2,
    soilTypes: ['Volcanic', 'Loam', 'Clay loam'],
    soilTypesAr: ['بركانية', 'طميية', 'طينية طميية'],
    temperatureRange: [15, 28],
    gradient: 'from-amber-200 to-stone-300',
  },
  {
    code: 'banana',
    name: 'Banana',
    nameAr: 'موز',
    icon: '\u{1F34C}',
    category: 'fruit',
    categoryAr: 'فواكه',
    season: 'Perennial',
    seasonAr: 'دائم',
    plantingMonths: 'Mar\u2013May',
    plantingMonthsAr: 'مارس\u2013مايو',
    harvestMonths: 'Year-round',
    harvestMonthsAr: 'على مدار السنة',
    daysToHarvest: 300,
    waterNeed: 'high',
    waterNeedMm: 1200,
    yieldTonsHa: 30,
    soilTypes: ['Loam', 'Clay loam', 'Silt loam'],
    soilTypesAr: ['طميية', 'طينية طميية', 'غرينية طميية'],
    temperatureRange: [22, 35],
    gradient: 'from-yellow-100 to-lime-200',
  },
  {
    code: 'mango',
    name: 'Mango',
    nameAr: 'مانجو',
    icon: '\u{1F96D}',
    category: 'fruit',
    categoryAr: 'فواكه',
    season: 'Summer',
    seasonAr: 'صيف',
    plantingMonths: 'Feb\u2013Apr',
    plantingMonthsAr: 'فبراير\u2013ابريل',
    harvestMonths: 'Jun\u2013Aug',
    harvestMonthsAr: 'يونيو\u2013اغسطس',
    daysToHarvest: 365,
    waterNeed: 'medium',
    waterNeedMm: 700,
    yieldTonsHa: 10,
    soilTypes: ['Loam', 'Sandy loam', 'Alluvial'],
    soilTypesAr: ['طميية', 'رملية طميية', 'فيضية'],
    temperatureRange: [24, 40],
    gradient: 'from-orange-100 to-yellow-200',
  },
  {
    code: 'qat',
    name: 'Qat',
    nameAr: 'قات',
    icon: '\u{1F33F}',
    category: 'cash',
    categoryAr: 'نقدية',
    season: 'Perennial',
    seasonAr: 'دائم',
    plantingMonths: 'Year-round',
    plantingMonthsAr: 'على مدار السنة',
    harvestMonths: 'Year-round',
    harvestMonthsAr: 'على مدار السنة',
    daysToHarvest: 365,
    waterNeed: 'medium',
    waterNeedMm: 500,
    yieldTonsHa: 0,
    soilTypes: ['Loam', 'Clay loam', 'Volcanic'],
    soilTypesAr: ['طميية', 'طينية طميية', 'بركانية'],
    temperatureRange: [15, 30],
    gradient: 'from-green-200 to-emerald-300',
  },
  {
    code: 'sesame',
    name: 'Sesame',
    nameAr: 'سمسم',
    icon: '\u{1F33B}',
    category: 'grain',
    categoryAr: 'حبوب',
    season: 'Summer',
    seasonAr: 'صيف',
    plantingMonths: 'Apr\u2013May',
    plantingMonthsAr: 'ابريل\u2013مايو',
    harvestMonths: 'Jul\u2013Aug',
    harvestMonthsAr: 'يوليو\u2013اغسطس',
    daysToHarvest: 100,
    waterNeed: 'low',
    waterNeedMm: 300,
    yieldTonsHa: 0.8,
    soilTypes: ['Sandy loam', 'Loam'],
    soilTypesAr: ['رملية طميية', 'طميية'],
    temperatureRange: [25, 40],
    gradient: 'from-yellow-200 to-orange-200',
  },
];

// ---------------------------------------------------------------------------
// Category tabs
// ---------------------------------------------------------------------------

const CATEGORIES = [
  { key: 'all', labelAr: 'الكل' },
  { key: 'grain', labelAr: 'حبوب' },
  { key: 'vegetable', labelAr: 'خضروات' },
  { key: 'fruit', labelAr: 'فواكه' },
  { key: 'tree', labelAr: 'اشجار' },
  { key: 'cash', labelAr: 'نقدية' },
] as const;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function waterLabel(level: 'low' | 'medium' | 'high'): {
  drops: string;
  labelAr: string;
  color: string;
} {
  if (level === 'low')
    return { drops: '\u{1F4A7}', labelAr: 'منخفض', color: 'text-blue-400' };
  if (level === 'medium')
    return { drops: '\u{1F4A7}\u{1F4A7}', labelAr: 'متوسط', color: 'text-blue-500' };
  return { drops: '\u{1F4A7}\u{1F4A7}\u{1F4A7}', labelAr: 'عالي', color: 'text-blue-600' };
}

function temperatureBar(range: [number, number]): { left: number; width: number } {
  const minScale = 0;
  const maxScale = 50;
  const span = maxScale - minScale;
  return {
    left: ((range[0] - minScale) / span) * 100,
    width: ((range[1] - range[0]) / span) * 100,
  };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CropCatalog({
  onSelect,
  selectedCrop,
  category: externalCategory,
  className,
}: CropCatalogProps) {
  const [activeCategory, setActiveCategory] = useState(externalCategory ?? 'all');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    let list = CROPS;
    if (activeCategory !== 'all') {
      list = list.filter((c) => c.category === activeCategory);
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(
        (c) =>
          c.nameAr.includes(q) ||
          c.name.toLowerCase().includes(q) ||
          c.categoryAr.includes(q),
      );
    }
    return list;
  }, [activeCategory, search]);

  return (
    <div dir="rtl" className={clsx('w-full space-y-5', className)}>
      {/* ---- Title ---- */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
          كتالوج المحاصيل
          <span className="mr-2 text-sm font-normal text-gray-500 dark:text-gray-400">
            Crop Catalog
          </span>
        </h2>
        <span className="rounded-full bg-green-100 dark:bg-green-900/30 px-3 py-1 text-xs font-medium text-green-700 dark:text-green-300">
          {filtered.length} صنف
        </span>
      </div>

      {/* ---- Search ---- */}
      <div className="relative">
        <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="البحث عن محصول..."
          className={clsx(
            'w-full pr-10 pl-4 py-2.5 rounded-xl border text-sm',
            'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
            'border-gray-200 dark:border-gray-700',
            'placeholder:text-gray-400 dark:placeholder:text-gray-500',
            'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
          )}
        />
      </div>

      {/* ---- Category tabs ---- */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {CATEGORIES.map((cat) => {
          const isActive = activeCategory === cat.key;
          return (
            <button
              key={cat.key}
              type="button"
              onClick={() => setActiveCategory(cat.key)}
              className={clsx(
                'whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-green-600 text-white shadow-sm'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700',
              )}
            >
              {cat.labelAr}
            </button>
          );
        })}
      </div>

      {/* ---- Grid ---- */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filtered.map((crop) => {
          const isSelected = selectedCrop === crop.code;
          const tempBar = temperatureBar(crop.temperatureRange);
          const water = waterLabel(crop.waterNeed);

          return (
            <button
              key={crop.code}
              type="button"
              onClick={() => onSelect?.(crop)}
              className={clsx(
                'group relative rounded-2xl border-2 bg-white dark:bg-gray-800 p-4 text-right transition-all hover:shadow-lg',
                isSelected
                  ? 'border-green-500 shadow-[0_0_16px_rgba(34,197,94,0.25)]'
                  : 'border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-700',
              )}
            >
              {/* Selected check */}
              {isSelected && (
                <span className="absolute left-3 top-3 flex h-6 w-6 items-center justify-center rounded-full bg-green-500 text-xs text-white">
                  \u2713
                </span>
              )}

              {/* Icon header */}
              <div
                className={clsx(
                  'mb-3 flex h-20 items-center justify-center rounded-xl bg-gradient-to-br',
                  crop.gradient,
                )}
              >
                <span className="text-5xl drop-shadow">{crop.icon}</span>
              </div>

              {/* Name + season */}
              <div className="mb-2 flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {crop.nameAr}
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{crop.name}</p>
                </div>
                <span className="rounded-md bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 text-xs font-medium text-blue-700 dark:text-blue-300">
                  {crop.seasonAr}
                </span>
              </div>

              {/* Category tag */}
              <span className="mb-3 inline-block rounded-full bg-gray-100 dark:bg-gray-700 px-2 py-0.5 text-[11px] text-gray-500 dark:text-gray-400">
                {crop.categoryAr}
              </span>

              {/* Requirements row */}
              <div className="mb-3 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-lg bg-gray-50 dark:bg-gray-700/50 px-2 py-1.5">
                  <p className="text-xs text-gray-400">
                    <CalendarDays className="h-3 w-3 inline ml-0.5" />
                    المدة
                  </p>
                  <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                    {crop.daysToHarvest}
                    <span className="text-[10px] font-normal text-gray-400"> يوم</span>
                  </p>
                </div>
                <div className="rounded-lg bg-gray-50 dark:bg-gray-700/50 px-2 py-1.5">
                  <p className="text-xs text-gray-400">
                    <Droplets className="h-3 w-3 inline ml-0.5" />
                    المياه
                  </p>
                  <p className={clsx('text-sm font-semibold', water.color)}>
                    {water.drops}
                  </p>
                  <p className="text-[10px] text-gray-400">{water.labelAr}</p>
                </div>
                <div className="rounded-lg bg-gray-50 dark:bg-gray-700/50 px-2 py-1.5">
                  <p className="text-xs text-gray-400">
                    <Wheat className="h-3 w-3 inline ml-0.5" />
                    الانتاج
                  </p>
                  <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                    {crop.yieldTonsHa > 0 ? (
                      <>
                        {crop.yieldTonsHa}
                        <span className="text-[10px] font-normal text-gray-400"> ط/هـ</span>
                      </>
                    ) : (
                      <span className="text-gray-400">\u2014</span>
                    )}
                  </p>
                </div>
              </div>

              {/* Planting & harvest months */}
              <div className="mb-3 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>
                  الزراعة:{' '}
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {crop.plantingMonthsAr}
                  </span>
                </span>
                <span>
                  الحصاد:{' '}
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {crop.harvestMonthsAr}
                  </span>
                </span>
              </div>

              {/* Temperature range bar */}
              <div className="mb-2">
                <div className="mb-1 flex items-center justify-between text-[10px] text-gray-400 dark:text-gray-500">
                  <span>
                    <Thermometer className="h-3 w-3 inline ml-0.5" />
                    الحرارة
                  </span>
                  <span>
                    {crop.temperatureRange[0]}\u00B0\u2013{crop.temperatureRange[1]}\u00B0C
                  </span>
                </div>
                <div className="relative h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-700">
                  <div
                    className="absolute top-0 h-full rounded-full bg-gradient-to-l from-red-400 via-yellow-300 to-blue-400"
                    style={{
                      right: `${tempBar.left}%`,
                      width: `${tempBar.width}%`,
                    }}
                  />
                </div>
              </div>

              {/* Water mm + soil */}
              <div className="flex items-center justify-between text-[10px] text-gray-400 dark:text-gray-500">
                <span>
                  احتياج مائي: {crop.waterNeedMm}{' '}
                  <span className="font-medium">مم/موسم</span>
                </span>
                <span
                  className="truncate max-w-[120px]"
                  title={crop.soilTypesAr.join('\u060C ')}
                >
                  تربة: {crop.soilTypesAr.slice(0, 2).join('\u060C ')}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Empty state */}
      {filtered.length === 0 && (
        <div className="rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700 py-16 text-center text-gray-400 dark:text-gray-500">
          <p className="text-4xl mb-2">{'🌱'}</p>
          <p className="text-sm">لا توجد محاصيل مطابقة</p>
          <p className="text-xs mt-1">No matching crops found</p>
        </div>
      )}
    </div>
  );
}

export type { CropVariety as CropVarietyType };
