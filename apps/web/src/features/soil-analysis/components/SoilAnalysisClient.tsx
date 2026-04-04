'use client';

/**
 * Soil Analysis Client Component
 * تحليل التربة — تحليل وتفسير نتائج فحص التربة
 *
 * Displays soil test results per field with nutrient levels,
 * health indicators, recommendations, and historical trends.
 */

import { useState, useMemo } from 'react';
import {
  FlaskConical,
  Leaf,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  MapPin,
  Download,
  Info,
  Layers,
  Thermometer,
  Zap,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type NutrientStatus = 'optimal' | 'adequate' | 'low' | 'deficient' | 'excess';

interface Nutrient {
  nameAr: string;
  nameEn: string;
  value: number;
  unit: string;
  optimalMin: number;
  optimalMax: number;
  status: NutrientStatus;
  statusAr: string;
  trend: 'up' | 'down' | 'stable';
}

interface SoilSample {
  id: string;
  fieldId: string;
  fieldNameAr: string;
  date: string;
  depth: string;
  pH: number;
  ec: number;
  organicMatter: number;
  texture: string;
  textureAr: string;
  nutrients: Nutrient[];
  recommendationsAr: string[];
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
  { id: 'FIELD-003', nameAr: 'حقل القمح', cropAr: 'قمح', areaHa: 8.5 },
  { id: 'FIELD-001', nameAr: 'حقل الشعير', cropAr: 'شعير', areaHa: 5.2 },
  { id: 'FIELD-007', nameAr: 'حقل الطماطم', cropAr: 'طماطم', areaHa: 3.0 },
  { id: 'FIELD-012', nameAr: 'حقل النخيل', cropAr: 'نخيل', areaHa: 12.0 },
];

const MOCK_SAMPLES: Record<string, SoilSample> = {
  'FIELD-003': {
    id: 'SA-2026-001', fieldId: 'FIELD-003', fieldNameAr: 'حقل القمح',
    date: '2026-03-15', depth: '0-30 سم', pH: 7.2, ec: 1.8, organicMatter: 1.4,
    texture: 'Sandy Loam', textureAr: 'طميية رملية',
    nutrients: [
      { nameAr: 'النيتروجين (N)', nameEn: 'Nitrogen', value: 22, unit: 'ppm', optimalMin: 25, optimalMax: 50, status: 'low', statusAr: 'منخفض', trend: 'down' },
      { nameAr: 'الفوسفور (P)', nameEn: 'Phosphorus', value: 18, unit: 'ppm', optimalMin: 15, optimalMax: 30, status: 'adequate', statusAr: 'كافٍ', trend: 'stable' },
      { nameAr: 'البوتاسيوم (K)', nameEn: 'Potassium', value: 180, unit: 'ppm', optimalMin: 150, optimalMax: 250, status: 'optimal', statusAr: 'مثالي', trend: 'up' },
      { nameAr: 'الكالسيوم (Ca)', nameEn: 'Calcium', value: 2800, unit: 'ppm', optimalMin: 2000, optimalMax: 4000, status: 'optimal', statusAr: 'مثالي', trend: 'stable' },
      { nameAr: 'المغنيسيوم (Mg)', nameEn: 'Magnesium', value: 120, unit: 'ppm', optimalMin: 100, optimalMax: 300, status: 'adequate', statusAr: 'كافٍ', trend: 'stable' },
      { nameAr: 'الحديد (Fe)', nameEn: 'Iron', value: 3.2, unit: 'ppm', optimalMin: 4, optimalMax: 12, status: 'deficient', statusAr: 'ناقص', trend: 'down' },
      { nameAr: 'الزنك (Zn)', nameEn: 'Zinc', value: 1.8, unit: 'ppm', optimalMin: 1.5, optimalMax: 5, status: 'adequate', statusAr: 'كافٍ', trend: 'up' },
      { nameAr: 'الكبريت (S)', nameEn: 'Sulfur', value: 8, unit: 'ppm', optimalMin: 10, optimalMax: 30, status: 'low', statusAr: 'منخفض', trend: 'down' },
    ],
    recommendationsAr: [
      'إضافة يوريا 46 كجم/هكتار لتعويض نقص النيتروجين',
      'تطبيق كبريتات الحديد 5 كجم/هكتار لمعالجة نقص الحديد',
      'إضافة الكبريت الزراعي 15 كجم/هكتار',
      'الحفاظ على مستوى البوتاسيوم الحالي — المستوى مثالي',
      'إعادة التحليل بعد 3 أشهر لتقييم التحسن',
    ],
  },
  'FIELD-001': {
    id: 'SA-2026-002', fieldId: 'FIELD-001', fieldNameAr: 'حقل الشعير',
    date: '2026-03-10', depth: '0-30 سم', pH: 7.8, ec: 2.5, organicMatter: 0.9,
    texture: 'Sandy', textureAr: 'رملية',
    nutrients: [
      { nameAr: 'النيتروجين (N)', nameEn: 'Nitrogen', value: 15, unit: 'ppm', optimalMin: 25, optimalMax: 50, status: 'deficient', statusAr: 'ناقص', trend: 'down' },
      { nameAr: 'الفوسفور (P)', nameEn: 'Phosphorus', value: 12, unit: 'ppm', optimalMin: 15, optimalMax: 30, status: 'low', statusAr: 'منخفض', trend: 'down' },
      { nameAr: 'البوتاسيوم (K)', nameEn: 'Potassium', value: 140, unit: 'ppm', optimalMin: 150, optimalMax: 250, status: 'low', statusAr: 'منخفض', trend: 'stable' },
      { nameAr: 'الكالسيوم (Ca)', nameEn: 'Calcium', value: 3200, unit: 'ppm', optimalMin: 2000, optimalMax: 4000, status: 'optimal', statusAr: 'مثالي', trend: 'stable' },
      { nameAr: 'المغنيسيوم (Mg)', nameEn: 'Magnesium', value: 85, unit: 'ppm', optimalMin: 100, optimalMax: 300, status: 'low', statusAr: 'منخفض', trend: 'down' },
      { nameAr: 'الحديد (Fe)', nameEn: 'Iron', value: 5.5, unit: 'ppm', optimalMin: 4, optimalMax: 12, status: 'adequate', statusAr: 'كافٍ', trend: 'stable' },
      { nameAr: 'الزنك (Zn)', nameEn: 'Zinc', value: 0.8, unit: 'ppm', optimalMin: 1.5, optimalMax: 5, status: 'deficient', statusAr: 'ناقص', trend: 'down' },
      { nameAr: 'الكبريت (S)', nameEn: 'Sulfur', value: 14, unit: 'ppm', optimalMin: 10, optimalMax: 30, status: 'adequate', statusAr: 'كافٍ', trend: 'stable' },
    ],
    recommendationsAr: [
      'إضافة سماد عضوي 5 طن/هكتار لرفع المادة العضوية',
      'تطبيق يوريا 60 كجم/هكتار — نقص حاد في النيتروجين',
      'إضافة DAP 40 كجم/هكتار لتعويض نقص الفوسفور',
      'تطبيق كبريتات الزنك 3 كجم/هكتار',
      'مراقبة الملوحة — EC مرتفعة (2.5 dS/m)',
    ],
  },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const STATUS_COLORS: Record<NutrientStatus, { bg: string; text: string; dot: string }> = {
  optimal: { bg: 'bg-green-50 dark:bg-green-900/20', text: 'text-green-700 dark:text-green-400', dot: 'bg-green-500' },
  adequate: { bg: 'bg-blue-50 dark:bg-blue-900/20', text: 'text-blue-700 dark:text-blue-400', dot: 'bg-blue-500' },
  low: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', text: 'text-yellow-700 dark:text-yellow-400', dot: 'bg-yellow-500' },
  deficient: { bg: 'bg-red-50 dark:bg-red-900/20', text: 'text-red-700 dark:text-red-400', dot: 'bg-red-500' },
  excess: { bg: 'bg-purple-50 dark:bg-purple-900/20', text: 'text-purple-700 dark:text-purple-400', dot: 'bg-purple-500' },
};

function getPhLabel(ph: number): { label: string; labelAr: string; color: string } {
  if (ph < 6.0) return { label: 'Acidic', labelAr: 'حمضية', color: 'text-red-600' };
  if (ph <= 7.5) return { label: 'Neutral', labelAr: 'متعادلة', color: 'text-green-600' };
  return { label: 'Alkaline', labelAr: 'قلوية', color: 'text-yellow-600' };
}

function getEcLabel(ec: number): { labelAr: string; color: string } {
  if (ec < 2) return { labelAr: 'طبيعية', color: 'text-green-600' };
  if (ec < 4) return { labelAr: 'معتدلة', color: 'text-yellow-600' };
  return { labelAr: 'مرتفعة', color: 'text-red-600' };
}

function getNutrientBarWidth(nutrient: Nutrient): number {
  const max = nutrient.optimalMax * 1.5;
  return Math.min(100, (nutrient.value / max) * 100);
}

function getNutrientBarColor(nutrient: Nutrient): string {
  if (nutrient.status === 'optimal') return 'bg-green-500';
  if (nutrient.status === 'adequate') return 'bg-blue-500';
  if (nutrient.status === 'low') return 'bg-yellow-500';
  if (nutrient.status === 'deficient') return 'bg-red-500';
  return 'bg-purple-500';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SoilAnalysisClient() {
  const [selectedFieldId, setSelectedFieldId] = useState(FIELDS[0]!.id);
  const [showAllNutrients, setShowAllNutrients] = useState(false);

  const sample = useMemo(() => MOCK_SAMPLES[selectedFieldId] ?? null, [selectedFieldId]);

  const nutrientSummary = useMemo(() => {
    if (!sample) return { optimal: 0, adequate: 0, low: 0, deficient: 0, total: 0 };
    const counts = { optimal: 0, adequate: 0, low: 0, deficient: 0, excess: 0 };
    sample.nutrients.forEach((n) => { counts[n.status]++; });
    return { ...counts, total: sample.nutrients.length };
  }, [sample]);

  const displayedNutrients = useMemo(() => {
    if (!sample) return [];
    if (showAllNutrients) return sample.nutrients;
    return sample.nutrients.slice(0, 5);
  }, [sample, showAllNutrients]);

  const phInfo = sample ? getPhLabel(sample.pH) : null;
  const ecInfo = sample ? getEcLabel(sample.ec) : null;

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-5">
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">تحليل التربة — Soil Analysis</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          تفسير نتائج فحص التربة والتوصيات الغذائية
        </p>
      </div>

      <main className="p-6 space-y-6 max-w-6xl mx-auto">
        {/* Field Selector */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
          <label htmlFor="field-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            <MapPin className="w-4 h-4 inline-block ml-1" />
            اختر الحقل
          </label>
          <select
            id="field-select"
            value={selectedFieldId}
            onChange={(e) => { setSelectedFieldId(e.target.value); setShowAllNutrients(false); }}
            className="w-full sm:w-80 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {FIELDS.map((f) => (
              <option key={f.id} value={f.id}>{f.nameAr} — {f.cropAr} ({f.areaHa} هـ)</option>
            ))}
          </select>
        </div>

        {!sample ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-10 text-center text-gray-500 dark:text-gray-400">
            <FlaskConical className="w-10 h-10 mx-auto mb-3 text-gray-300" />
            <p>لا توجد نتائج تحليل لهذا الحقل — قم بإجراء فحص تربة جديد</p>
          </div>
        ) : (
          <>
            {/* Summary Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'pH التربة', value: sample.pH.toFixed(1), sub: phInfo?.labelAr, color: phInfo?.color ?? '', icon: FlaskConical },
                { label: 'الملوحة (EC)', value: `${sample.ec} dS/m`, sub: ecInfo?.labelAr, color: ecInfo?.color ?? '', icon: Zap },
                { label: 'المادة العضوية', value: `${sample.organicMatter}%`, sub: sample.organicMatter < 1.5 ? 'منخفضة' : 'مقبولة', color: sample.organicMatter < 1.5 ? 'text-yellow-600' : 'text-green-600', icon: Leaf },
                { label: 'نسيج التربة', value: sample.textureAr, sub: sample.texture, color: 'text-gray-600 dark:text-gray-400', icon: Layers },
              ].map((stat) => (
                <div key={stat.label} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-9 h-9 rounded-lg bg-gray-50 dark:bg-gray-700 flex items-center justify-center">
                      <stat.icon className="w-4.5 h-4.5 text-gray-500" />
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{stat.label}</p>
                  </div>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{stat.value}</p>
                  {stat.sub && <p className={`text-xs font-medium mt-0.5 ${stat.color}`}>{stat.sub}</p>}
                </div>
              ))}
            </div>

            {/* Nutrient Health Summary Bar */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">ملخص حالة العناصر الغذائية</h3>
              <div className="flex gap-4 flex-wrap text-sm">
                {[
                  { label: 'مثالي', count: nutrientSummary.optimal, color: 'bg-green-500' },
                  { label: 'كافٍ', count: nutrientSummary.adequate, color: 'bg-blue-500' },
                  { label: 'منخفض', count: nutrientSummary.low, color: 'bg-yellow-500' },
                  { label: 'ناقص', count: nutrientSummary.deficient, color: 'bg-red-500' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${item.color}`} />
                    <span className="text-gray-600 dark:text-gray-400">{item.label}:</span>
                    <span className="font-semibold text-gray-900 dark:text-gray-100">{item.count}</span>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex h-3 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
                {nutrientSummary.optimal > 0 && <div className="bg-green-500" style={{ width: `${(nutrientSummary.optimal / nutrientSummary.total) * 100}%` }} />}
                {nutrientSummary.adequate > 0 && <div className="bg-blue-500" style={{ width: `${(nutrientSummary.adequate / nutrientSummary.total) * 100}%` }} />}
                {nutrientSummary.low > 0 && <div className="bg-yellow-500" style={{ width: `${(nutrientSummary.low / nutrientSummary.total) * 100}%` }} />}
                {nutrientSummary.deficient > 0 && <div className="bg-red-500" style={{ width: `${(nutrientSummary.deficient / nutrientSummary.total) * 100}%` }} />}
              </div>
            </div>

            {/* Nutrient Details */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Thermometer className="w-5 h-5 text-green-600" />
                  <h3 className="text-base font-bold text-gray-900 dark:text-gray-100">تفاصيل العناصر الغذائية</h3>
                </div>
                <span className="text-xs text-gray-400">العينة: {sample.id} | التاريخ: {sample.date} | العمق: {sample.depth}</span>
              </div>

              <div className="divide-y divide-gray-100 dark:divide-gray-700">
                {displayedNutrients.map((nutrient) => {
                  const statusColor = STATUS_COLORS[nutrient.status];
                  return (
                    <div key={nutrient.nameEn} className="px-5 py-4 flex flex-col sm:flex-row sm:items-center gap-3">
                      {/* Name & Status */}
                      <div className="sm:w-48 flex-shrink-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{nutrient.nameAr}</p>
                        <p className="text-xs text-gray-400">{nutrient.nameEn}</p>
                      </div>

                      {/* Value & Bar */}
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <span className="text-sm font-bold text-gray-900 dark:text-gray-100">
                            {nutrient.value} {nutrient.unit}
                          </span>
                          <span className="text-xs text-gray-400">
                            (المثالي: {nutrient.optimalMin}-{nutrient.optimalMax} {nutrient.unit})
                          </span>
                          {nutrient.trend === 'up' && <TrendingUp className="w-3.5 h-3.5 text-green-500" />}
                          {nutrient.trend === 'down' && <TrendingDown className="w-3.5 h-3.5 text-red-500" />}
                        </div>
                        <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${getNutrientBarColor(nutrient)}`} style={{ width: `${getNutrientBarWidth(nutrient)}%` }} />
                        </div>
                      </div>

                      {/* Status Badge */}
                      <div className="sm:w-28 flex-shrink-0">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusColor.bg} ${statusColor.text}`}>
                          <span className={`w-2 h-2 rounded-full ${statusColor.dot}`} />
                          {nutrient.statusAr}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {sample.nutrients.length > 5 && (
                <div className="px-5 py-3 border-t border-gray-100 dark:border-gray-700 text-center">
                  <button
                    type="button"
                    onClick={() => setShowAllNutrients(!showAllNutrients)}
                    className="inline-flex items-center gap-1.5 text-sm font-medium text-green-600 dark:text-green-400 hover:underline"
                  >
                    {showAllNutrients ? (
                      <><ChevronUp className="w-4 h-4" />عرض أقل</>
                    ) : (
                      <><ChevronDown className="w-4 h-4" />عرض جميع العناصر ({sample.nutrients.length})</>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* Recommendations */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-5">
              <div className="flex items-center gap-2 mb-4">
                <Info className="w-5 h-5 text-blue-500" />
                <h3 className="text-base font-bold text-gray-900 dark:text-gray-100">التوصيات</h3>
              </div>
              <ul className="space-y-3">
                {sample.recommendationsAr.map((rec, i) => {
                  const isWarning = rec.includes('نقص') || rec.includes('حاد') || rec.includes('مراقبة');
                  return (
                    <li key={i} className={`flex items-start gap-3 text-sm rounded-lg p-3 ${
                      isWarning
                        ? 'bg-amber-50 dark:bg-amber-900/15 border border-amber-100 dark:border-amber-800'
                        : 'bg-gray-50 dark:bg-gray-700/40 border border-gray-100 dark:border-gray-700'
                    }`}>
                      {isWarning ? (
                        <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                      ) : (
                        <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      )}
                      <span className="text-gray-700 dark:text-gray-300">{rec}</span>
                    </li>
                  );
                })}
              </ul>
            </div>

            {/* Footer Actions */}
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={() => alert('تصدير تقرير التحليل — PDF')}
                className="inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-medium bg-green-600 text-white hover:bg-green-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                تصدير PDF
              </button>
              <button
                type="button"
                onClick={() => alert('مقارنة مع تحليلات سابقة')}
                className="inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-medium bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <TrendingUp className="w-4 h-4" />
                مقارنة تاريخية
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
