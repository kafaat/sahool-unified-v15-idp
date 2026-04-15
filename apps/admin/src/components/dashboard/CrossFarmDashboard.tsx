'use client';
// Cross-Farm Dashboard — لوحة مقارنة المزارع
// Shows all fields in a sortable table with key metrics for quick comparison

import { useState, useMemo } from 'react';
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  AlertTriangle,
  Trophy,
  Leaf,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface FieldSummary {
  id: string;
  name: string;
  nameAr: string;
  cropType: string;
  areaHa: number;
  ndvi: number;
  healthScore: number;
  soilMoisture?: number;
  lastIrrigation?: string;
  diseaseRisk: 'low' | 'medium' | 'high';
  yieldEstimate?: number;
}

export interface CrossFarmDashboardProps {
  fields: FieldSummary[];
  onFieldClick?: (fieldId: string) => void;
}

// ---------------------------------------------------------------------------
// Sort helpers
// ---------------------------------------------------------------------------

type SortKey =
  | 'name'
  | 'cropType'
  | 'areaHa'
  | 'ndvi'
  | 'healthScore'
  | 'diseaseRisk'
  | 'yieldEstimate';

type SortDir = 'asc' | 'desc';

const DISEASE_RISK_ORDER: Record<string, number> = {
  low: 0,
  medium: 1,
  high: 2,
};

function compareFields(a: FieldSummary, b: FieldSummary, key: SortKey): number {
  if (key === 'name') return a.nameAr.localeCompare(b.nameAr, 'ar');
  if (key === 'cropType') return a.cropType.localeCompare(b.cropType);
  if (key === 'diseaseRisk')
    return (DISEASE_RISK_ORDER[a.diseaseRisk] ?? 0) - (DISEASE_RISK_ORDER[b.diseaseRisk] ?? 0);
  if (key === 'yieldEstimate')
    return (a.yieldEstimate ?? 0) - (b.yieldEstimate ?? 0);
  return (a[key] as number) - (b[key] as number);
}

// ---------------------------------------------------------------------------
// Color helpers
// ---------------------------------------------------------------------------

function ndviColor(v: number): string {
  if (v >= 0.6) return 'bg-green-100 text-green-800';
  if (v >= 0.4) return 'bg-yellow-100 text-yellow-800';
  if (v >= 0.2) return 'bg-orange-100 text-orange-800';
  return 'bg-red-100 text-red-800';
}

function healthColor(v: number): string {
  if (v >= 80) return 'bg-green-100 text-green-800';
  if (v >= 60) return 'bg-yellow-100 text-yellow-800';
  if (v >= 40) return 'bg-orange-100 text-orange-800';
  return 'bg-red-100 text-red-800';
}

function diseaseColor(risk: string): string {
  if (risk === 'low') return 'bg-green-100 text-green-800';
  if (risk === 'medium') return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
}

const DISEASE_LABEL_AR: Record<string, string> = {
  low: 'منخفض',
  medium: 'متوسط',
  high: 'مرتفع',
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
  { key: 'name', labelAr: 'اسم الحقل', labelEn: 'Field' },
  { key: 'cropType', labelAr: 'المحصول', labelEn: 'Crop' },
  { key: 'areaHa', labelAr: 'المساحة (هـ)', labelEn: 'Area (ha)' },
  { key: 'ndvi', labelAr: 'م.غ.ن', labelEn: 'NDVI' },
  { key: 'healthScore', labelAr: 'الصحة', labelEn: 'Health' },
  { key: 'diseaseRisk', labelAr: 'خطر المرض', labelEn: 'Disease' },
  { key: 'yieldEstimate', labelAr: 'تقدير الإنتاج', labelEn: 'Yield Est.' },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CrossFarmDashboard({
  fields,
  onFieldClick,
}: CrossFarmDashboardProps) {
  const [sortKey, setSortKey] = useState<SortKey>('healthScore');
  const [sortDir, setSortDir] = useState<SortDir>('desc');

  // Sorting
  const sorted = useMemo(() => {
    const copy = [...fields];
    copy.sort((a, b) => {
      const cmp = compareFields(a, b, sortKey);
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return copy;
  }, [fields, sortKey, sortDir]);

  // Summary averages
  const summary = useMemo(() => {
    if (fields.length === 0) return null;
    const len = fields.length;
    const totalArea = fields.reduce((s, f) => s + f.areaHa, 0);
    const avgNdvi = fields.reduce((s, f) => s + f.ndvi, 0) / len;
    const avgHealth = fields.reduce((s, f) => s + f.healthScore, 0) / len;
    const yieldsWithData = fields.filter((f) => f.yieldEstimate != null);
    const avgYield =
      yieldsWithData.length > 0
        ? yieldsWithData.reduce((s, f) => s + (f.yieldEstimate ?? 0), 0) /
          yieldsWithData.length
        : undefined;
    return { totalArea, avgNdvi, avgHealth, avgYield };
  }, [fields]);

  // Best performer & needs attention
  const bestPerformerId = useMemo(() => {
    if (fields.length === 0) return null;
    return fields.reduce((best, f) => (f.healthScore > (best?.healthScore ?? 0) ? f : best), fields[0])?.id ?? null;
  }, [fields]);

  const needsAttentionId = useMemo(() => {
    if (fields.length === 0) return null;
    return fields.reduce((worst, f) => (f.healthScore < (worst?.healthScore ?? 100) ? f : worst), fields[0])
      ?.id ?? null;
  }, [fields]);

  // Toggle sort
  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  }

  // Sort icon
  function SortIcon({ columnKey }: { columnKey: SortKey }) {
    if (sortKey !== columnKey)
      return <ArrowUpDown className="inline-block h-3.5 w-3.5 opacity-40" />;
    return sortDir === 'asc' ? (
      <ArrowUp className="inline-block h-3.5 w-3.5" />
    ) : (
      <ArrowDown className="inline-block h-3.5 w-3.5" />
    );
  }

  if (fields.length === 0) {
    return (
      <div
        dir="rtl"
        className="flex items-center justify-center rounded-xl border border-gray-200 bg-white p-12 text-gray-500"
      >
        لا توجد حقول للعرض
      </div>
    );
  }

  return (
    <div dir="rtl" className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-100 bg-gray-50 px-5 py-3">
        <h2 className="text-lg font-semibold text-gray-900">
          لوحة مقارنة المزارع
          <span className="mr-2 text-sm font-normal text-gray-500">Cross-Farm Dashboard</span>
        </h2>
        <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
          {fields.length} حقل
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[800px] text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50/60">
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key)}
                  className="cursor-pointer select-none whitespace-nowrap px-4 py-3 text-right font-medium text-gray-600 transition-colors hover:text-gray-900"
                >
                  <span className="ml-1">{col.labelAr}</span>
                  <SortIcon columnKey={col.key} />
                </th>
              ))}
              <th className="px-4 py-3 text-right font-medium text-gray-600">حالة</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-100">
            {sorted.map((field) => {
              const isBest = field.id === bestPerformerId;
              const isWorst = field.id === needsAttentionId;

              return (
                <tr
                  key={field.id}
                  onClick={() => onFieldClick?.(field.id)}
                  className={`transition-colors ${
                    onFieldClick ? 'cursor-pointer' : ''
                  } ${
                    isBest
                      ? 'bg-green-50/50 hover:bg-green-50'
                      : isWorst
                        ? 'bg-red-50/50 hover:bg-red-50'
                        : 'hover:bg-gray-50'
                  }`}
                >
                  {/* Field Name */}
                  <td className="px-4 py-3 font-medium text-gray-900">
                    <div>{field.nameAr}</div>
                    <div className="text-xs text-gray-400">{field.name}</div>
                  </td>

                  {/* Crop */}
                  <td className="px-4 py-3 text-gray-700">{field.cropType}</td>

                  {/* Area */}
                  <td className="px-4 py-3 text-gray-700">{field.areaHa.toFixed(1)}</td>

                  {/* NDVI */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${ndviColor(field.ndvi)}`}
                    >
                      {field.ndvi.toFixed(2)}
                    </span>
                  </td>

                  {/* Health Score */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${healthColor(field.healthScore)}`}
                    >
                      {field.healthScore}%
                    </span>
                  </td>

                  {/* Disease Risk */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${diseaseColor(field.diseaseRisk)}`}
                    >
                      {DISEASE_LABEL_AR[field.diseaseRisk]}
                    </span>
                  </td>

                  {/* Yield Estimate */}
                  <td className="px-4 py-3 text-gray-700">
                    {field.yieldEstimate != null
                      ? `${field.yieldEstimate.toFixed(1)} طن/هـ`
                      : '—'}
                  </td>

                  {/* Status badge */}
                  <td className="px-4 py-3">
                    {isBest && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
                        <Trophy className="h-3 w-3" />
                        الأفضل
                      </span>
                    )}
                    {isWorst && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700">
                        <AlertTriangle className="h-3 w-3" />
                        يحتاج اهتمام
                      </span>
                    )}
                    {!isBest && !isWorst && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-500">
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
              <tr className="border-t-2 border-gray-200 bg-gray-50 font-semibold text-gray-700">
                <td className="px-4 py-3">
                  المتوسط / الإجمالي
                  <span className="mr-1 text-xs font-normal text-gray-400">Summary</span>
                </td>
                <td className="px-4 py-3 text-gray-400">—</td>
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
                <td className="px-4 py-3 text-gray-400">—</td>
                <td className="px-4 py-3">
                  {summary.avgYield != null
                    ? `${summary.avgYield.toFixed(1)} طن/هـ`
                    : '—'}
                </td>
                <td className="px-4 py-3" />
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    </div>
  );
}
