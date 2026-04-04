'use client';

/**
 * Field Zones Client Component — VRI Zone Management
 * مناطق الحقل — إدارة مناطق الري المتغير والزراعة الدقيقة
 *
 * Manages VRI (Variable Rate Irrigation) zones per field with
 * zone stats, NDVI trends, and recommended actions.
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
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ZoneProductivity = 'high' | 'medium' | 'low';
type ZoneStrategy = 'manual' | 'ndvi' | 'soil' | 'auto-ai';

interface HistoricalNDVI {
  month: string;
  value: number;
}

interface FieldZone {
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

interface FieldOption {
  id: string;
  nameAr: string;
  cropAr: string;
  areaHa: number;
}

// ---------------------------------------------------------------------------
// Mock Data
// ---------------------------------------------------------------------------

const FIELDS: FieldOption[] = [
  { id: 'FIELD-001', nameAr: 'حقل القمح الشمالي', cropAr: 'قمح', areaHa: 25.4 },
  { id: 'FIELD-002', nameAr: 'شريط الشعير الجنوبي', cropAr: 'شعير', areaHa: 18.0 },
  { id: 'FIELD-003', nameAr: 'بستان النخيل الشرقي', cropAr: 'نخيل', areaHa: 12.5 },
];

const MOCK_ZONES: Record<string, FieldZone[]> = {
  'FIELD-001': [
    {
      id: 'Z-001-A', nameAr: 'المنطقة أ — الشمال الغربي', type: 'high', typeAr: 'إنتاجية عالية',
      areaHa: 6.2, ndvi: 0.78, irrigationRate: 12, fertilizerRate: 180, seedRate: 150,
      status: 'active', statusAr: 'نشط',
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.45 }, { month: 'نوفمبر', value: 0.58 },
        { month: 'ديسمبر', value: 0.68 }, { month: 'يناير', value: 0.75 }, { month: 'فبراير', value: 0.78 },
      ],
      recommendedActions: ['الاستمرار في جدول الري الحالي — كفاءة ممتازة', 'تطبيق الجرعة الثانية من النيتروجين خلال أسبوع'],
    },
    {
      id: 'Z-001-B', nameAr: 'المنطقة ب — الشمال الشرقي', type: 'medium', typeAr: 'إنتاجية متوسطة',
      areaHa: 5.8, ndvi: 0.55, irrigationRate: 15, fertilizerRate: 200, seedRate: 160,
      status: 'active', statusAr: 'نشط',
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.38 }, { month: 'نوفمبر', value: 0.42 },
        { month: 'ديسمبر', value: 0.48 }, { month: 'يناير', value: 0.52 }, { month: 'فبراير', value: 0.55 },
      ],
      recommendedActions: ['زيادة معدل الري بنسبة 15% لتحسين رطوبة التربة', 'فحص التربة للكشف عن نقص المغذيات', 'مراقبة مؤشر NDVI أسبوعياً'],
    },
    {
      id: 'Z-001-C', nameAr: 'المنطقة ج — الوسطى', type: 'high', typeAr: 'إنتاجية عالية',
      areaHa: 5.0, ndvi: 0.72, irrigationRate: 12, fertilizerRate: 175, seedRate: 150,
      status: 'completed', statusAr: 'مكتمل',
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.50 }, { month: 'نوفمبر', value: 0.60 },
        { month: 'ديسمبر', value: 0.65 }, { month: 'يناير', value: 0.70 }, { month: 'فبراير', value: 0.72 },
      ],
      recommendedActions: ['اكتملت دورة الري — الحالة ممتازة', 'تجهيز الجدول الزمني للحصاد'],
    },
    {
      id: 'Z-001-D', nameAr: 'المنطقة د — الجنوب الغربي', type: 'low', typeAr: 'إنتاجية منخفضة',
      areaHa: 4.8, ndvi: 0.32, irrigationRate: 20, fertilizerRate: 240, seedRate: 180,
      status: 'active', statusAr: 'نشط',
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.22 }, { month: 'نوفمبر', value: 0.25 },
        { month: 'ديسمبر', value: 0.28 }, { month: 'يناير', value: 0.30 }, { month: 'فبراير', value: 0.32 },
      ],
      recommendedActions: ['تحليل التربة عاجل — اشتباه بملوحة مرتفعة', 'زيادة الري بنسبة 40% مع رصد الصرف', 'تطبيق سماد عضوي لتحسين بنية التربة'],
    },
    {
      id: 'Z-001-E', nameAr: 'المنطقة هـ — الجنوب الشرقي', type: 'medium', typeAr: 'إنتاجية متوسطة',
      areaHa: 3.6, ndvi: 0.48, irrigationRate: 16, fertilizerRate: 210, seedRate: 165,
      status: 'scheduled', statusAr: 'مجدول',
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.30 }, { month: 'نوفمبر', value: 0.35 },
        { month: 'ديسمبر', value: 0.40 }, { month: 'يناير', value: 0.45 }, { month: 'فبراير', value: 0.48 },
      ],
      recommendedActions: ['بدء دورة الري المجدولة خلال 48 ساعة', 'تطبيق سماد الفوسفور قبل الري'],
    },
  ],
};

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

function computeCV(zones: FieldZone[]): number {
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
  const [selectedFieldId, setSelectedFieldId] = useState(FIELDS[0]!.id);
  const [strategy, setStrategy] = useState<ZoneStrategy>('ndvi');
  const [expandedZoneId, setExpandedZoneId] = useState<string | null>(null);

  const zones = useMemo(() => MOCK_ZONES[selectedFieldId] ?? [], [selectedFieldId]);
  const avgNdvi = useMemo(() => (zones.length ? zones.reduce((s, z) => s + z.ndvi, 0) / zones.length : 0), [zones]);
  const cv = useMemo(() => computeCV(zones), [zones]);
  const totalArea = useMemo(() => zones.reduce((s, z) => s + z.areaHa, 0), [zones]);
  const estimatedSavings = useMemo(() => (cv > 10 ? Math.round(totalArea * cv * 2.5) : 0), [cv, totalArea]);

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
                value={selectedFieldId}
                onChange={(e) => { setSelectedFieldId(e.target.value); setExpandedZoneId(null); }}
                className="w-full rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {FIELDS.map((f) => (
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
