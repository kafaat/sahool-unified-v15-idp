'use client';

/**
 * Cross-Farm Dashboard — لوحة مقارنة المزارع
 *
 * Sortable multi-farm comparison table with key agricultural metrics.
 * Arabic-first bilingual headers, color-coded health indicators, and
 * built-in mock data for demonstration.
 */

import { useState, useMemo } from 'react';
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  AlertTriangle,
  Trophy,
  Leaf,
  MapPin,
  BarChart3,
  Search,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface FarmSummary {
  id: string;
  name: string;
  nameAr: string;
  areaHa: number;
  ndvi: number;
  healthScore: number;
  cropType: string;
  cropTypeAr: string;
  status: 'active' | 'fallow' | 'harvested' | 'planned';
  soilMoisture?: number;
  yieldEstimate?: number;
}

export interface CrossFarmDashboardProps {
  farms?: FarmSummary[];
  onFarmClick?: (farmId: string) => void;
}

// ---------------------------------------------------------------------------
// Sort helpers
// ---------------------------------------------------------------------------

type SortKey = 'name' | 'areaHa' | 'ndvi' | 'healthScore' | 'cropType' | 'status';
type SortDir = 'asc' | 'desc';

function compareFarms(a: FarmSummary, b: FarmSummary, key: SortKey): number {
  if (key === 'name') return a.nameAr.localeCompare(b.nameAr, 'ar');
  if (key === 'cropType') return a.cropTypeAr.localeCompare(b.cropTypeAr, 'ar');
  if (key === 'status') return a.status.localeCompare(b.status);
  return (a[key] as number) - (b[key] as number);
}

// ---------------------------------------------------------------------------
// Color & label helpers
// ---------------------------------------------------------------------------

function ndviColor(v: number): string {
  if (v >= 0.6) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
  if (v >= 0.4) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
  if (v >= 0.2) return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400';
  return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
}

function healthColor(v: number): string {
  if (v >= 80) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
  if (v >= 60) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
  if (v >= 40) return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400';
  return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
}

const STATUS_LABELS: Record<string, { ar: string; classes: string }> = {
  active: { ar: 'نشط', classes: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' },
  fallow: { ar: 'بور', classes: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400' },
  harvested: { ar: 'محصود', classes: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' },
  planned: { ar: 'مخطط', classes: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400' },
};

// ---------------------------------------------------------------------------
// Column definitions
// ---------------------------------------------------------------------------

interface Column {
  key: SortKey;
  labelAr: string;
  labelEn: string;
}

const COLUMNS: Column[] = [
  { key: 'name', labelAr: 'اسم المزرعة', labelEn: 'Farm' },
  { key: 'areaHa', labelAr: 'المساحة (هـ)', labelEn: 'Area (ha)' },
  { key: 'ndvi', labelAr: 'م.غ.ن', labelEn: 'NDVI' },
  { key: 'healthScore', labelAr: 'درجة الصحة', labelEn: 'Health' },
  { key: 'cropType', labelAr: 'المحصول', labelEn: 'Crop' },
  { key: 'status', labelAr: 'الحالة', labelEn: 'Status' },
];

// ---------------------------------------------------------------------------
// Mock data (5-8 farms)
// ---------------------------------------------------------------------------

const MOCK_FARMS: FarmSummary[] = [
  {
    id: 'farm-001',
    name: 'Al-Rashid Farm',
    nameAr: 'مزرعة الراشد',
    areaHa: 45.2,
    ndvi: 0.72,
    healthScore: 88,
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    status: 'active',
    soilMoisture: 42,
    yieldEstimate: 4.8,
  },
  {
    id: 'farm-002',
    name: 'Green Valley',
    nameAr: 'الوادي الاخضر',
    areaHa: 28.7,
    ndvi: 0.58,
    healthScore: 72,
    cropType: 'Barley',
    cropTypeAr: 'شعير',
    status: 'active',
    soilMoisture: 35,
    yieldEstimate: 3.5,
  },
  {
    id: 'farm-003',
    name: 'Sunrise Fields',
    nameAr: 'حقول الشروق',
    areaHa: 62.0,
    ndvi: 0.81,
    healthScore: 93,
    cropType: 'Date Palm',
    cropTypeAr: 'نخيل',
    status: 'active',
    soilMoisture: 50,
    yieldEstimate: 12.0,
  },
  {
    id: 'farm-004',
    name: 'Desert Bloom',
    nameAr: 'زهرة الصحراء',
    areaHa: 15.3,
    ndvi: 0.35,
    healthScore: 48,
    cropType: 'Tomato',
    cropTypeAr: 'طماطم',
    status: 'active',
    soilMoisture: 28,
    yieldEstimate: 2.1,
  },
  {
    id: 'farm-005',
    name: 'Al-Noor Agricultural',
    nameAr: 'النور الزراعية',
    areaHa: 38.5,
    ndvi: 0.65,
    healthScore: 79,
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    status: 'active',
    soilMoisture: 40,
    yieldEstimate: 4.2,
  },
  {
    id: 'farm-006',
    name: 'Heritage Palms',
    nameAr: 'نخيل التراث',
    areaHa: 22.0,
    ndvi: 0.19,
    healthScore: 32,
    cropType: 'Date Palm',
    cropTypeAr: 'نخيل',
    status: 'harvested',
    soilMoisture: 20,
    yieldEstimate: 8.5,
  },
  {
    id: 'farm-007',
    name: 'Saba Fields',
    nameAr: 'حقول سبأ',
    areaHa: 50.8,
    ndvi: 0.44,
    healthScore: 55,
    cropType: 'Corn',
    cropTypeAr: 'ذرة',
    status: 'planned',
    soilMoisture: 33,
  },
  {
    id: 'farm-008',
    name: 'Wadi Al-Khair',
    nameAr: 'وادي الخير',
    areaHa: 33.1,
    ndvi: 0.69,
    healthScore: 85,
    cropType: 'Alfalfa',
    cropTypeAr: 'برسيم',
    status: 'active',
    soilMoisture: 46,
    yieldEstimate: 6.0,
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CrossFarmDashboard({
  farms = MOCK_FARMS,
  onFarmClick,
}: CrossFarmDashboardProps) {
  const [sortKey, setSortKey] = useState<SortKey>('healthScore');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [searchQuery, setSearchQuery] = useState('');

  // Filter by search
  const filtered = useMemo(() => {
    if (!searchQuery.trim()) return farms;
    const q = searchQuery.toLowerCase();
    return farms.filter(
      (f) =>
        f.nameAr.includes(q) ||
        f.name.toLowerCase().includes(q) ||
        f.cropTypeAr.includes(q) ||
        f.cropType.toLowerCase().includes(q)
    );
  }, [farms, searchQuery]);

  // Sort
  const sorted = useMemo(() => {
    const copy = [...filtered];
    copy.sort((a, b) => {
      const cmp = compareFarms(a, b, sortKey);
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return copy;
  }, [filtered, sortKey, sortDir]);

  // Summary
  const summary = useMemo(() => {
    if (filtered.length === 0) return null;
    const len = filtered.length;
    const totalArea = filtered.reduce((s, f) => s + f.areaHa, 0);
    const avgNdvi = filtered.reduce((s, f) => s + f.ndvi, 0) / len;
    const avgHealth = filtered.reduce((s, f) => s + f.healthScore, 0) / len;
    const withYield = filtered.filter((f) => f.yieldEstimate != null);
    const avgYield =
      withYield.length > 0
        ? withYield.reduce((s, f) => s + (f.yieldEstimate ?? 0), 0) / withYield.length
        : undefined;
    return { totalArea, avgNdvi, avgHealth, avgYield };
  }, [filtered]);

  // Best / worst
  const bestId = useMemo(() => {
    if (filtered.length === 0) return null;
    return filtered.reduce((best, f) =>
      f.healthScore > best.healthScore ? f : best
    ).id;
  }, [filtered]);

  const worstId = useMemo(() => {
    if (filtered.length === 0) return null;
    return filtered.reduce((worst, f) =>
      f.healthScore < worst.healthScore ? f : worst
    ).id;
  }, [filtered]);

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  }

  function SortIcon({ columnKey }: { columnKey: SortKey }) {
    if (sortKey !== columnKey)
      return <ArrowUpDown className="inline-block h-3.5 w-3.5 opacity-40" />;
    return sortDir === 'asc' ? (
      <ArrowUp className="inline-block h-3.5 w-3.5" />
    ) : (
      <ArrowDown className="inline-block h-3.5 w-3.5" />
    );
  }

  if (farms.length === 0) {
    return (
      <div
        dir="rtl"
        className="flex items-center justify-center rounded-xl border border-gray-200 bg-white p-12 text-gray-500 dark:border-gray-700 dark:bg-gray-800"
      >
        <MapPin className="ml-2 h-5 w-5" />
        لا توجد مزارع للعرض
      </div>
    );
  }

  return (
    <div
      dir="rtl"
      className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800"
    >
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 bg-gray-50 px-5 py-3 dark:border-gray-700 dark:bg-gray-900/50">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-emerald-600" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            لوحة مقارنة المزارع
            <span className="mr-2 text-sm font-normal text-gray-500 dark:text-gray-400">
              Cross-Farm Dashboard
            </span>
          </h2>
        </div>

        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="بحث..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="rounded-lg border border-gray-200 bg-white py-1.5 pl-3 pr-8 text-sm text-gray-700 placeholder-gray-400 focus:border-emerald-400 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
            />
          </div>
          <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
            {filtered.length} مزرعة
          </span>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[850px] text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50/60 dark:border-gray-700 dark:bg-gray-900/30">
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key)}
                  className="cursor-pointer select-none whitespace-nowrap px-4 py-3 text-right font-medium text-gray-600 transition-colors hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <span className="ml-1">{col.labelAr}</span>
                  <SortIcon columnKey={col.key} />
                </th>
              ))}
              <th className="px-4 py-3 text-right font-medium text-gray-600 dark:text-gray-400">
                تقييم
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {sorted.map((farm) => {
              const isBest = farm.id === bestId;
              const isWorst = farm.id === worstId;

              return (
                <tr
                  key={farm.id}
                  onClick={() => onFarmClick?.(farm.id)}
                  className={`transition-colors ${
                    onFarmClick ? 'cursor-pointer' : ''
                  } ${
                    isBest
                      ? 'bg-green-50/50 hover:bg-green-50 dark:bg-green-950/20 dark:hover:bg-green-950/30'
                      : isWorst
                        ? 'bg-red-50/50 hover:bg-red-50 dark:bg-red-950/20 dark:hover:bg-red-950/30'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700/30'
                  }`}
                >
                  {/* Farm Name */}
                  <td className="px-4 py-3 font-medium text-gray-900 dark:text-gray-100">
                    <div>{farm.nameAr}</div>
                    <div className="text-xs text-gray-400">{farm.name}</div>
                  </td>

                  {/* Area */}
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                    {farm.areaHa.toFixed(1)}
                  </td>

                  {/* NDVI */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${ndviColor(farm.ndvi)}`}
                    >
                      {farm.ndvi.toFixed(2)}
                    </span>
                  </td>

                  {/* Health Score */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${healthColor(farm.healthScore)}`}
                    >
                      {farm.healthScore}%
                    </span>
                  </td>

                  {/* Crop */}
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                    {farm.cropTypeAr}
                  </td>

                  {/* Status */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_LABELS[farm.status]?.classes ?? ''}`}
                    >
                      {STATUS_LABELS[farm.status]?.ar ?? farm.status}
                    </span>
                  </td>

                  {/* Rating badge */}
                  <td className="px-4 py-3">
                    {isBest && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                        <Trophy className="h-3 w-3" />
                        الافضل
                      </span>
                    )}
                    {isWorst && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700 dark:bg-red-900/30 dark:text-red-400">
                        <AlertTriangle className="h-3 w-3" />
                        يحتاج اهتمام
                      </span>
                    )}
                    {!isBest && !isWorst && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-500 dark:bg-gray-700 dark:text-gray-400">
                        <Leaf className="h-3 w-3" />
                        عادي
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>

          {/* Summary footer */}
          {summary && (
            <tfoot>
              <tr className="border-t-2 border-gray-200 bg-gray-50 font-semibold text-gray-700 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-300">
                <td className="px-4 py-3">
                  المتوسط / الاجمالي
                  <span className="mr-1 text-xs font-normal text-gray-400">
                    Summary
                  </span>
                </td>
                <td className="px-4 py-3">{summary.totalArea.toFixed(1)}</td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${ndviColor(summary.avgNdvi)}`}
                  >
                    {summary.avgNdvi.toFixed(2)}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${healthColor(summary.avgHealth)}`}
                  >
                    {summary.avgHealth.toFixed(0)}%
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-400">--</td>
                <td className="px-4 py-3 text-gray-400">--</td>
                <td className="px-4 py-3" />
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    </div>
  );
}
