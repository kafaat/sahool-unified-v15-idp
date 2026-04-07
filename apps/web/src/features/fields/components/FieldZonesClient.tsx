'use client';

/**
 * Field Zones Client Component — VRI Zone Management
 * مناطق الحقل — إدارة مناطق الري المتغير والزراعة الدقيقة
 *
 * Manages VRI (Variable Rate Irrigation) zones per field with
 * zone stats, NDVI trends, and recommended actions.
 *
 * Field selector uses real field data from the fields API.
 * Zone data remains client-side (no dedicated zones API exists);
 * in a future iteration zones would come from the vegetation-analysis
 * or field-intelligence services.
 */

import { useState, useMemo } from 'react';
import {
  Grid3X3,
  Leaf,
  BarChart3,
  Layers,
  Droplets,
  Sprout,
  MapPin,
  Download,
  ChevronDown,
  ChevronUp,
  Wheat,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { useFieldsList } from '../hooks/useFieldsList';
import type { Field } from '../types';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ZoneProductivity = 'high' | 'medium' | 'low';
type ZoneStrategy = 'manual' | 'ndvi' | 'soil' | 'auto-ai';

interface HistoricalNDVI {
  month: string;
  value: number;
}

interface FieldZoneData {
  id: string;
  nameAr: string;
  type: ZoneProductivity;
  typeAr: string;
  areaHa: number;
  ndvi: number;
  irrigationRate: number;
  fertilizerRate: number;
  seedRate: number;
  status: 'active' | 'scheduled' | 'completed';
  statusAr: string;
  historicalNdvi: HistoricalNDVI[];
  recommendedActions: string[];
}

// ---------------------------------------------------------------------------
// Zone Data (client-side — would come from vegetation-analysis API in future)
// ---------------------------------------------------------------------------

const ZONE_DATA: Record<string, FieldZoneData[]> = {
  // Default zones shown when a field doesn't have specific zone data.
  // Keyed by field ID for any fields that have specific zones defined.
};

/** Generate placeholder zones from a real field's metadata */
function generateZonesFromField(field: Field): FieldZoneData[] {
  const ndvi = field.ndviValue ?? 0.55;
  const areaPerZone = field.area / 3;
  return [
    {
      id: `${field.id}-A`, nameAr: `المنطقة أ — ${field.nameAr || field.name}`,
      type: ndvi >= 0.6 ? 'high' : ndvi >= 0.4 ? 'medium' : 'low',
      typeAr: ndvi >= 0.6 ? 'إنتاجية عالية' : ndvi >= 0.4 ? 'إنتاجية متوسطة' : 'إنتاجية منخفضة',
      areaHa: Math.round(areaPerZone * 10) / 10, ndvi: Math.min(ndvi + 0.1, 0.95),
      irrigationRate: 12, fertilizerRate: 180, seedRate: 150,
      status: 'active', statusAr: 'نشط',
      historicalNdvi: [
        { month: 'أكتوبر', value: ndvi - 0.2 }, { month: 'نوفمبر', value: ndvi - 0.12 },
        { month: 'ديسمبر', value: ndvi - 0.05 }, { month: 'يناير', value: ndvi }, { month: 'فبراير', value: ndvi + 0.1 },
      ],
      recommendedActions: ['الاستمرار في جدول الري الحالي', 'مراقبة مؤشر NDVI أسبوعياً'],
    },
    {
      id: `${field.id}-B`, nameAr: `المنطقة ب — ${field.nameAr || field.name}`,
      type: 'medium', typeAr: 'إنتاجية متوسطة',
      areaHa: Math.round(areaPerZone * 10) / 10, ndvi: ndvi,
      irrigationRate: 15, fertilizerRate: 200, seedRate: 160,
      status: 'active', statusAr: 'نشط',
      historicalNdvi: [
        { month: 'أكتوبر', value: ndvi - 0.15 }, { month: 'نوفمبر', value: ndvi - 0.1 },
        { month: 'ديسمبر', value: ndvi - 0.05 }, { month: 'يناير', value: ndvi - 0.02 }, { month: 'فبراير', value: ndvi },
      ],
      recommendedActions: ['زيادة معدل الري بنسبة 15%', 'فحص التربة للكشف عن نقص المغذيات'],
    },
    {
      id: `${field.id}-C`, nameAr: `المنطقة ج — ${field.nameAr || field.name}`,
      type: ndvi < 0.4 ? 'low' : 'medium', typeAr: ndvi < 0.4 ? 'إنتاجية منخفضة' : 'إنتاجية متوسطة',
      areaHa: Math.round(areaPerZone * 10) / 10, ndvi: Math.max(ndvi - 0.15, 0.1),
      irrigationRate: 20, fertilizerRate: 240, seedRate: 180,
      status: 'scheduled', statusAr: 'مجدول',
      historicalNdvi: [
        { month: 'أكتوبر', value: ndvi - 0.25 }, { month: 'نوفمبر', value: ndvi - 0.2 },
        { month: 'ديسمبر', value: ndvi - 0.18 }, { month: 'يناير', value: ndvi - 0.16 }, { month: 'فبراير', value: ndvi - 0.15 },
      ],
      recommendedActions: ['تحليل التربة عاجل', 'زيادة الري بنسبة 40%', 'تطبيق سماد عضوي لتحسين بنية التربة'],
    },
  ];
}

const ZONE_STRATEGIES: { value: ZoneStrategy; labelAr: string }[] = [
  { value: 'manual', labelAr: 'يدوي' },
  { value: 'ndvi', labelAr: 'بناءً على NDVI' },
  { value: 'soil', labelAr: 'بناءً على التربة' },
  { value: 'auto-ai', labelAr: 'ذكاء اصطناعي تلقائي' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const ZONE_COLORS: Record<ZoneProductivity, { bg: string; text: string; dot: string }> = {
  high: { bg: 'bg-green-50 dark:bg-green-900/20', text: 'text-green-700 dark:text-green-400', dot: 'bg-green-500' },
  medium: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', text: 'text-yellow-700 dark:text-yellow-400', dot: 'bg-yellow-500' },
  low: { bg: 'bg-red-50 dark:bg-red-900/20', text: 'text-red-700 dark:text-red-400', dot: 'bg-red-500' },
};

const STATUS_BADGE: Record<string, string> = {
  active: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  scheduled: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
  completed: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
};

function computeCV(zones: FieldZoneData[]): number {
  if (zones.length < 2) return 0;
  const vals = zones.map((z) => z.ndvi);
  const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
  const variance = vals.reduce((sum, v) => sum + (v - mean) ** 2, 0) / vals.length;
  return Math.round((Math.sqrt(variance) / mean) * 100);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function FieldZonesClient() {
  const { data: apiFields, isLoading, isError, error, refetch } = useFieldsList();

  const fieldOptions = useMemo(
    () =>
      (apiFields ?? []).map((f: Field) => ({
        id: f.id,
        nameAr: f.nameAr || f.name,
        cropAr: f.cropAr || f.crop || '-',
        areaHa: f.area,
        _raw: f,
      })),
    [apiFields],
  );

  const [selectedFieldId, setSelectedFieldId] = useState<string>('');
  const [strategy, setStrategy] = useState<ZoneStrategy>('ndvi');
  const [expandedZoneId, setExpandedZoneId] = useState<string | null>(null);

  const effectiveFieldId = selectedFieldId || fieldOptions[0]?.id || '';

  const zones = useMemo(() => {
    // Check if we have pre-defined zone data for this field
    if (ZONE_DATA[effectiveFieldId]) return ZONE_DATA[effectiveFieldId];
    // Otherwise, generate zones from the actual field data
    const fieldOpt = fieldOptions.find((f) => f.id === effectiveFieldId);
    if (fieldOpt) return generateZonesFromField(fieldOpt._raw);
    return [];
  }, [effectiveFieldId, fieldOptions]);

  const avgNdvi = useMemo(() => (zones.length ? zones.reduce((s, z) => s + z.ndvi, 0) / zones.length : 0), [zones]);
  const cv = useMemo(() => computeCV(zones), [zones]);
  const totalArea = useMemo(() => zones.reduce((s, z) => s + z.areaHa, 0), [zones]);
  const estimatedSavings = useMemo(() => (cv > 10 ? Math.round(totalArea * cv * 2.5) : 0), [cv, totalArea]);

  // ── Loading State ──────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto" />
          <p className="text-gray-600 text-sm">جاري تحميل الحقول...</p>
          <p className="text-gray-400 text-xs">Loading fields...</p>
        </div>
      </div>
    );
  }

  // ── Error State ────────────────────────────────────────────────────
  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3 max-w-md">
          <AlertTriangle className="w-8 h-8 text-red-500 mx-auto" />
          <p className="text-gray-900 font-semibold">تعذر تحميل الحقول</p>
          <p className="text-gray-500 text-sm">
            {error instanceof Error ? error.message : 'Failed to load fields'}
          </p>
          <button
            onClick={() => refetch()}
            className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-5">
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
          مناطق الحقل — Field Zone Management
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          إدارة مناطق الري المتغير والزراعة الدقيقة — Valley VRI
        </p>
      </div>

      <main className="p-6 space-y-6 max-w-7xl mx-auto">
        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'إجمالي المناطق', value: zones.length, icon: Grid3X3, color: 'text-indigo-600' },
            { label: 'متوسط NDVI', value: avgNdvi.toFixed(2), icon: Leaf, color: 'text-green-600' },
            { label: 'تباين الحقل (CV%)', value: `${cv}%`, icon: BarChart3, color: 'text-orange-600' },
            { label: 'التوفير المقدر (VRI)', value: estimatedSavings > 0 ? `${estimatedSavings} ريال` : 'غير متاح', icon: Layers, color: 'text-purple-600' },
          ].map((stat) => (
            <div key={stat.label} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 flex items-center gap-4">
              <div className={`w-10 h-10 rounded-lg bg-gray-50 dark:bg-gray-700 flex items-center justify-center ${stat.color}`}>
                <stat.icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">{stat.label}</p>
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Selectors */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="field-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                <MapPin className="w-4 h-4 inline-block ml-1" />
                الحقل
              </label>
              <select
                id="field-select"
                value={effectiveFieldId}
                onChange={(e) => { setSelectedFieldId(e.target.value); setExpandedZoneId(null); }}
                className="w-full rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {fieldOptions.length === 0 && (
                  <option value="">لا توجد حقول</option>
                )}
                {fieldOptions.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.nameAr} — {f.cropAr} ({f.areaHa} هـ)
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                <Layers className="w-4 h-4 inline-block ml-1" />
                استراتيجية التقسيم
              </label>
              <div className="flex gap-2 flex-wrap">
                {ZONE_STRATEGIES.map((s) => (
                  <button
                    key={s.value}
                    type="button"
                    onClick={() => setStrategy(s.value)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      strategy === s.value
                        ? 'bg-green-600 text-white shadow-sm'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    {s.labelAr}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Zone Cards */}
        {zones.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-10 text-center text-gray-500 dark:text-gray-400">
            لا توجد مناطق لهذا الحقل — اختر حقلاً آخر أو أنشئ تقسيماً جديداً
          </div>
        ) : (
          <div className="space-y-3">
            {zones.map((zone) => {
              const color = ZONE_COLORS[zone.type];
              const isExpanded = expandedZoneId === zone.id;

              return (
                <div key={zone.id} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
                  {/* Zone Row */}
                  <button
                    type="button"
                    onClick={() => setExpandedZoneId(isExpanded ? null : zone.id)}
                    className="w-full flex items-center gap-4 p-4 text-right hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${color.bg} ${color.text}`}>
                      <span className={`w-2 h-2 rounded-full ${color.dot}`} />
                      {zone.typeAr}
                    </span>
                    <span className="flex-1 text-sm font-semibold text-gray-900 dark:text-gray-100">{zone.nameAr}</span>
                    <span className="text-sm text-gray-600 dark:text-gray-300">{zone.areaHa} هـ</span>
                    <span className={`font-semibold text-sm ${zone.ndvi >= 0.6 ? 'text-green-600' : zone.ndvi >= 0.4 ? 'text-yellow-600' : 'text-red-600'}`}>
                      NDVI: {zone.ndvi.toFixed(2)}
                    </span>
                    <div className="flex items-center gap-1.5 text-sm text-blue-600">
                      <Droplets className="w-3.5 h-3.5" />
                      {zone.irrigationRate} مم/س
                    </div>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_BADGE[zone.status]}`}>
                      {zone.statusAr}
                    </span>
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                  </button>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className={`border-t border-gray-100 dark:border-gray-700 ${color.bg} p-5`}>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Zone Stats */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">معلومات المنطقة</h4>
                          <div className="space-y-2">
                            {[
                              { label: 'معدل السماد', value: `${zone.fertilizerRate} كجم/هـ`, icon: Sprout },
                              { label: 'معدل البذور', value: `${zone.seedRate} كجم/هـ`, icon: Wheat },
                              { label: 'معدل الري', value: `${zone.irrigationRate} مم/س`, icon: Droplets },
                            ].map((item) => (
                              <div key={item.label} className="flex items-center gap-2 text-sm">
                                <item.icon className="w-3.5 h-3.5 text-gray-400" />
                                <span className="text-gray-500 dark:text-gray-400">{item.label}:</span>
                                <span className="font-medium text-gray-900 dark:text-gray-100">{item.value}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* NDVI Trend */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">اتجاه NDVI التاريخي</h4>
                          <div className="flex items-end gap-2 h-20">
                            {zone.historicalNdvi.map((point, i) => {
                              const heightPct = Math.max(10, point.value * 100);
                              const barColor = point.value >= 0.6 ? 'bg-green-500' : point.value >= 0.4 ? 'bg-yellow-500' : 'bg-red-500';
                              return (
                                <div key={i} className="flex flex-col items-center flex-1 gap-1">
                                  <span className="text-[10px] text-gray-500 dark:text-gray-400">{point.value.toFixed(2)}</span>
                                  <div className={`w-full rounded-t ${barColor}`} style={{ height: `${heightPct}%` }} />
                                  <span className="text-[9px] text-gray-400 dark:text-gray-500 truncate w-full text-center">{point.month}</span>
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        {/* Actions */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">الإجراءات الموصى بها</h4>
                          <ul className="space-y-2">
                            {zone.recommendedActions.map((action, i) => (
                              <li key={i} className="flex items-start gap-2 text-xs text-gray-700 dark:text-gray-300">
                                <span className={`mt-0.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${color.dot}`} />
                                {action}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Summary Footer */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex flex-wrap gap-6 text-sm">
              <div>
                <span className="text-gray-500 dark:text-gray-400">إجمالي المساحة: </span>
                <span className="font-semibold text-gray-900 dark:text-gray-100">{totalArea.toFixed(1)} هـ</span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">حالة VRI: </span>
                <span className={`font-semibold ${cv > 20 ? 'text-green-600' : cv > 10 ? 'text-yellow-600' : 'text-gray-500'}`}>
                  {cv > 20 ? 'موصى بشدة' : cv > 10 ? 'اختياري' : 'غير ضروري'}
                </span>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => alert(`تصدير GeoJSON — ${zones.length} مناطق`)}
                className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                GeoJSON
              </button>
              <button
                type="button"
                onClick={() => alert(`تصدير Shapefile — ${zones.length} مناطق`)}
                className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                Shapefile
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
