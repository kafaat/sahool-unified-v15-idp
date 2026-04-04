'use client';
// Crop Catalog — كتالوج المحاصيل
// Visual cards showing crop varieties with icons, stages, and requirements

import { useState, useMemo } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CropVariety {
  code: string;
  name: string;
  nameAr: string;
  icon: string;
  category: 'grain' | 'vegetable' | 'fruit' | 'tree' | 'cash';
  categoryAr: string;
  season: string;
  seasonAr: string;
  plantingMonths: string;
  harvestMonths: string;
  daysToHarvest: number;
  waterNeed: 'low' | 'medium' | 'high';
  waterNeedMm: number;
  yieldTonsHa: number;
  soilTypes: string[];
  temperatureRange: [number, number];
  image?: string;
}

interface CropCatalogProps {
  onSelect?: (crop: CropVariety) => void;
  selectedCrop?: string;
  category?: string;
}

// ---------------------------------------------------------------------------
// Data — Yemen crop varieties
// ---------------------------------------------------------------------------

const CROPS: CropVariety[] = [
  {
    code: 'wheat',
    name: 'Wheat',
    nameAr: 'قمح',
    icon: '🌾',
    category: 'grain',
    categoryAr: 'حبوب',
    season: 'Winter',
    seasonAr: 'شتاء',
    plantingMonths: 'Oct–Nov',
    harvestMonths: 'Mar–Apr',
    daysToHarvest: 150,
    waterNeed: 'medium',
    waterNeedMm: 450,
    yieldTonsHa: 4.5,
    soilTypes: ['Loam', 'Clay loam', 'Silt loam'],
    temperatureRange: [10, 25],
    image: 'from-amber-100 to-yellow-200',
  },
  {
    code: 'barley',
    name: 'Barley',
    nameAr: 'شعير',
    icon: '🌾',
    category: 'grain',
    categoryAr: 'حبوب',
    season: 'Winter',
    seasonAr: 'شتاء',
    plantingMonths: 'Oct–Nov',
    harvestMonths: 'Feb–Mar',
    daysToHarvest: 120,
    waterNeed: 'low',
    waterNeedMm: 300,
    yieldTonsHa: 3.5,
    soilTypes: ['Sandy loam', 'Loam', 'Clay loam'],
    temperatureRange: [8, 24],
    image: 'from-yellow-100 to-amber-200',
  },
  {
    code: 'sorghum',
    name: 'Sorghum',
    nameAr: 'ذرة رفيعة',
    icon: '🌽',
    category: 'grain',
    categoryAr: 'حبوب',
    season: 'Summer',
    seasonAr: 'صيف',
    plantingMonths: 'Apr–May',
    harvestMonths: 'Aug–Sep',
    daysToHarvest: 120,
    waterNeed: 'low',
    waterNeedMm: 350,
    yieldTonsHa: 2.5,
    soilTypes: ['Loam', 'Sandy loam', 'Clay'],
    temperatureRange: [20, 38],
    image: 'from-orange-100 to-red-200',
  },
  {
    code: 'tomato',
    name: 'Tomato',
    nameAr: 'طماطم',
    icon: '🍅',
    category: 'vegetable',
    categoryAr: 'خضروات',
    season: 'Spring',
    seasonAr: 'ربيع',
    plantingMonths: 'Feb–Mar',
    harvestMonths: 'May–Jun',
    daysToHarvest: 90,
    waterNeed: 'high',
    waterNeedMm: 500,
    yieldTonsHa: 25,
    soilTypes: ['Loam', 'Sandy loam', 'Silt loam'],
    temperatureRange: [18, 30],
    image: 'from-red-100 to-rose-200',
  },
  {
    code: 'onion',
    name: 'Onion',
    nameAr: 'بصل',
    icon: '🧅',
    category: 'vegetable',
    categoryAr: 'خضروات',
    season: 'Autumn',
    seasonAr: 'خريف',
    plantingMonths: 'Sep–Oct',
    harvestMonths: 'Jan–Feb',
    daysToHarvest: 120,
    waterNeed: 'medium',
    waterNeedMm: 400,
    yieldTonsHa: 15,
    soilTypes: ['Loam', 'Sandy loam', 'Silt loam'],
    temperatureRange: [12, 28],
    image: 'from-purple-100 to-indigo-200',
  },
  {
    code: 'cucumber',
    name: 'Cucumber',
    nameAr: 'خيار',
    icon: '🥒',
    category: 'vegetable',
    categoryAr: 'خضروات',
    season: 'Spring',
    seasonAr: 'ربيع',
    plantingMonths: 'Feb–Mar',
    harvestMonths: 'Apr–May',
    daysToHarvest: 60,
    waterNeed: 'medium',
    waterNeedMm: 450,
    yieldTonsHa: 20,
    soilTypes: ['Loam', 'Sandy loam'],
    temperatureRange: [18, 32],
    image: 'from-green-100 to-emerald-200',
  },
  {
    code: 'date_palm',
    name: 'Date Palm',
    nameAr: 'نخيل',
    icon: '🌴',
    category: 'tree',
    categoryAr: 'أشجار',
    season: 'Perennial',
    seasonAr: 'دائم',
    plantingMonths: 'Feb–Apr',
    harvestMonths: 'Aug–Oct',
    daysToHarvest: 180,
    waterNeed: 'medium',
    waterNeedMm: 600,
    yieldTonsHa: 8,
    soilTypes: ['Sandy loam', 'Loam', 'Sandy'],
    temperatureRange: [20, 45],
    image: 'from-emerald-100 to-teal-200',
  },
  {
    code: 'coffee',
    name: 'Coffee',
    nameAr: 'بن',
    icon: '☕',
    category: 'tree',
    categoryAr: 'أشجار',
    season: 'Perennial',
    seasonAr: 'دائم',
    plantingMonths: 'Jun–Aug',
    harvestMonths: 'Nov–Jan',
    daysToHarvest: 365,
    waterNeed: 'high',
    waterNeedMm: 800,
    yieldTonsHa: 2,
    soilTypes: ['Volcanic', 'Loam', 'Clay loam'],
    temperatureRange: [15, 28],
    image: 'from-amber-200 to-stone-300',
  },
  {
    code: 'banana',
    name: 'Banana',
    nameAr: 'موز',
    icon: '🍌',
    category: 'fruit',
    categoryAr: 'فواكه',
    season: 'Perennial',
    seasonAr: 'دائم',
    plantingMonths: 'Mar–May',
    harvestMonths: 'Year-round',
    daysToHarvest: 300,
    waterNeed: 'high',
    waterNeedMm: 1200,
    yieldTonsHa: 30,
    soilTypes: ['Loam', 'Clay loam', 'Silt loam'],
    temperatureRange: [22, 35],
    image: 'from-yellow-100 to-lime-200',
  },
  {
    code: 'mango',
    name: 'Mango',
    nameAr: 'مانجو',
    icon: '🥭',
    category: 'fruit',
    categoryAr: 'فواكه',
    season: 'Summer',
    seasonAr: 'صيف',
    plantingMonths: 'Feb–Apr',
    harvestMonths: 'Jun–Aug',
    daysToHarvest: 365,
    waterNeed: 'medium',
    waterNeedMm: 700,
    yieldTonsHa: 10,
    soilTypes: ['Loam', 'Sandy loam', 'Alluvial'],
    temperatureRange: [24, 40],
    image: 'from-orange-100 to-yellow-200',
  },
  {
    code: 'qat',
    name: 'Qat',
    nameAr: 'قات',
    icon: '🌿',
    category: 'cash',
    categoryAr: 'نقدية',
    season: 'Perennial',
    seasonAr: 'دائم',
    plantingMonths: 'Year-round',
    harvestMonths: 'Year-round',
    daysToHarvest: 365,
    waterNeed: 'medium',
    waterNeedMm: 500,
    yieldTonsHa: 0,
    soilTypes: ['Loam', 'Clay loam', 'Volcanic'],
    temperatureRange: [15, 30],
    image: 'from-green-200 to-emerald-300',
  },
  {
    code: 'sesame',
    name: 'Sesame',
    nameAr: 'سمسم',
    icon: '🌻',
    category: 'grain',
    categoryAr: 'حبوب',
    season: 'Summer',
    seasonAr: 'صيف',
    plantingMonths: 'Apr–May',
    harvestMonths: 'Jul–Aug',
    daysToHarvest: 100,
    waterNeed: 'low',
    waterNeedMm: 300,
    yieldTonsHa: 0.8,
    soilTypes: ['Sandy loam', 'Loam'],
    temperatureRange: [25, 40],
    image: 'from-yellow-200 to-orange-200',
  },
];

// ---------------------------------------------------------------------------
// Category tabs
// ---------------------------------------------------------------------------

const CATEGORIES: { key: string; label: string; labelAr: string }[] = [
  { key: 'all', label: 'All', labelAr: 'الكل' },
  { key: 'grain', label: 'Grains', labelAr: 'حبوب' },
  { key: 'vegetable', label: 'Vegetables', labelAr: 'خضروات' },
  { key: 'fruit', label: 'Fruits', labelAr: 'فواكه' },
  { key: 'tree', label: 'Trees', labelAr: 'أشجار' },
  { key: 'cash', label: 'Cash', labelAr: 'نقدية' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function waterDrops(level: 'low' | 'medium' | 'high'): string {
  if (level === 'low') return '💧';
  if (level === 'medium') return '💧💧';
  return '💧💧💧';
}

function waterLabelAr(level: 'low' | 'medium' | 'high'): string {
  if (level === 'low') return 'منخفض';
  if (level === 'medium') return 'متوسط';
  return 'عالي';
}

function temperatureBar(range: [number, number]): { left: number; width: number } {
  const minScale = 0;
  const maxScale = 50;
  const span = maxScale - minScale;
  const left = ((range[0] - minScale) / span) * 100;
  const width = ((range[1] - range[0]) / span) * 100;
  return { left, width };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CropCatalog({
  onSelect,
  selectedCrop,
  category: externalCategory,
}: CropCatalogProps) {
  const [activeCategory, setActiveCategory] = useState<string>(
    externalCategory ?? 'all',
  );

  const filtered = useMemo(() => {
    if (activeCategory === 'all') return CROPS;
    return CROPS.filter((c) => c.category === activeCategory);
  }, [activeCategory]);

  return (
    <div dir="rtl" className="w-full space-y-5">
      {/* ---- Title ---- */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">
          كتالوج المحاصيل
          <span className="mr-2 text-sm font-normal text-gray-500">
            Crop Catalog
          </span>
        </h2>
        <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
          {filtered.length} صنف
        </span>
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
              className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-green-600 text-white shadow-sm'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {cat.labelAr}
            </button>
          );
        })}
      </div>

      {/* ---- Grid ---- */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((crop) => {
          const isSelected = selectedCrop === crop.code;
          const tempBar = temperatureBar(crop.temperatureRange);

          return (
            <button
              key={crop.code}
              type="button"
              onClick={() => onSelect?.(crop)}
              className={`group relative rounded-2xl border-2 bg-white p-4 text-right transition-all hover:shadow-lg ${
                isSelected
                  ? 'border-green-500 shadow-[0_0_16px_rgba(34,197,94,0.3)]'
                  : 'border-gray-200 hover:border-green-300'
              }`}
            >
              {/* Selected indicator */}
              {isSelected && (
                <span className="absolute left-3 top-3 flex h-6 w-6 items-center justify-center rounded-full bg-green-500 text-xs text-white">
                  ✓
                </span>
              )}

              {/* Header: icon + name + season badge */}
              <div
                className={`mb-3 flex h-24 items-center justify-center rounded-xl bg-gradient-to-br ${crop.image ?? 'from-gray-100 to-gray-200'}`}
              >
                <span className="text-5xl drop-shadow">{crop.icon}</span>
              </div>

              <div className="mb-2 flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">
                    {crop.nameAr}
                  </h3>
                  <p className="text-xs text-gray-500">{crop.name}</p>
                </div>
                <span className="rounded-md bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                  {crop.seasonAr}
                </span>
              </div>

              {/* Category tag */}
              <span className="mb-3 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-[11px] text-gray-500">
                {crop.categoryAr}
              </span>

              {/* Requirements row */}
              <div className="mb-3 grid grid-cols-3 gap-2 text-center">
                {/* Days to harvest */}
                <div className="rounded-lg bg-gray-50 px-2 py-1.5">
                  <p className="text-xs text-gray-400">المدة</p>
                  <p className="text-sm font-semibold text-gray-800">
                    {crop.daysToHarvest}
                    <span className="text-[10px] font-normal text-gray-400">
                      {' '}
                      يوم
                    </span>
                  </p>
                </div>
                {/* Water need */}
                <div className="rounded-lg bg-gray-50 px-2 py-1.5">
                  <p className="text-xs text-gray-400">المياه</p>
                  <p className="text-sm font-semibold">
                    {waterDrops(crop.waterNeed)}
                  </p>
                  <p className="text-[10px] text-gray-400">
                    {waterLabelAr(crop.waterNeed)}
                  </p>
                </div>
                {/* Yield */}
                <div className="rounded-lg bg-gray-50 px-2 py-1.5">
                  <p className="text-xs text-gray-400">الإنتاج</p>
                  <p className="text-sm font-semibold text-gray-800">
                    {crop.yieldTonsHa > 0 ? (
                      <>
                        {crop.yieldTonsHa}
                        <span className="text-[10px] font-normal text-gray-400">
                          {' '}
                          ط/هـ
                        </span>
                      </>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </p>
                </div>
              </div>

              {/* Planting & harvest months */}
              <div className="mb-3 flex items-center justify-between text-xs text-gray-500">
                <span>
                  🌱 الزراعة:{' '}
                  <span className="font-medium text-gray-700">
                    {crop.plantingMonths}
                  </span>
                </span>
                <span>
                  🌿 الحصاد:{' '}
                  <span className="font-medium text-gray-700">
                    {crop.harvestMonths}
                  </span>
                </span>
              </div>

              {/* Temperature range bar */}
              <div className="mb-2">
                <div className="mb-1 flex items-center justify-between text-[10px] text-gray-400">
                  <span>🌡️ الحرارة</span>
                  <span>
                    {crop.temperatureRange[0]}°–{crop.temperatureRange[1]}°C
                  </span>
                </div>
                <div className="relative h-2 w-full overflow-hidden rounded-full bg-gray-100">
                  <div
                    className="absolute top-0 h-full rounded-full bg-gradient-to-l from-red-400 via-yellow-300 to-blue-400"
                    style={{
                      right: `${tempBar.left}%`,
                      width: `${tempBar.width}%`,
                    }}
                  />
                </div>
              </div>

              {/* Water mm */}
              <div className="flex items-center justify-between text-[10px] text-gray-400">
                <span>
                  احتياج مائي: {crop.waterNeedMm}{' '}
                  <span className="font-medium">مم/موسم</span>
                </span>
                <span className="truncate max-w-[120px]" title={crop.soilTypes.join(', ')}>
                  تربة: {crop.soilTypes.slice(0, 2).join('، ')}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Empty state */}
      {filtered.length === 0 && (
        <div className="rounded-xl border-2 border-dashed border-gray-200 py-16 text-center text-gray-400">
          <p className="text-4xl">🌱</p>
          <p className="mt-2 text-sm">لا توجد محاصيل في هذه الفئة</p>
        </div>
      )}
    </div>
  );
}

export type { CropVariety, CropCatalogProps };
