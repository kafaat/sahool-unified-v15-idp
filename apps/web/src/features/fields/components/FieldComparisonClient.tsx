'use client';

/**
 * Field Comparison Client Component
 * مقارنة الحقول — مقارنة جنبًا إلى جنب
 *
 * Side-by-side field comparison using NDVI, LAI, soil moisture,
 * weather, and yield metrics with winner determination.
 */

import { useState, useMemo } from 'react';
import {
  Trophy,
  ArrowRight,
  TrendingUp,
  Scale,
  Leaf,
  Droplets,
  Thermometer,
  BarChart3,
  Wind,
  CloudRain,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface FieldData {
  id: string;
  nameAr: string;
  nameEn: string;
  cropAr: string;
  areaHa: number;
  ndvi: number;
  lai: number;
  soilMoisture: number;
  yieldTonHa: number;
  tempC: number;
  rainfall: number;
  windSpeed: number;
  healthStatus: 'healthy' | 'moderate' | 'stressed' | 'critical';
  healthStatusAr: string;
}

type MetricKey = 'ndvi' | 'lai' | 'soilMoisture' | 'yieldTonHa' | 'tempC' | 'rainfall' | 'windSpeed';

interface ComparisonMetric {
  key: MetricKey;
  labelAr: string;
  labelEn: string;
  unit: string;
  higherIsBetter: boolean;
  icon: React.ElementType;
}

// ---------------------------------------------------------------------------
// Mock Data
// ---------------------------------------------------------------------------

const MOCK_FIELDS: FieldData[] = [
  {
    id: 'FIELD-001', nameAr: 'حقل القمح الشمالي', nameEn: 'North Wheat Block',
    cropAr: 'قمح', areaHa: 5.2, ndvi: 0.72, lai: 3.1, soilMoisture: 45,
    yieldTonHa: 4.8, tempC: 22, rainfall: 35, windSpeed: 12,
    healthStatus: 'healthy', healthStatusAr: 'صحي',
  },
  {
    id: 'FIELD-002', nameAr: 'شريط الشعير الجنوبي', nameEn: 'South Barley Strip',
    cropAr: 'شعير', areaHa: 8.0, ndvi: 0.58, lai: 2.2, soilMoisture: 38,
    yieldTonHa: 3.5, tempC: 24, rainfall: 28, windSpeed: 15,
    healthStatus: 'stressed', healthStatusAr: 'مجهد',
  },
  {
    id: 'FIELD-003', nameAr: 'دفيئة الطماطم الشرقية', nameEn: 'East Tomato Greenhouse',
    cropAr: 'طماطم', areaHa: 1.5, ndvi: 0.81, lai: 4.0, soilMoisture: 60,
    yieldTonHa: 45.0, tempC: 26, rainfall: 0, windSpeed: 5,
    healthStatus: 'healthy', healthStatusAr: 'صحي',
  },
  {
    id: 'FIELD-004', nameAr: 'بستان النخيل الغربي', nameEn: 'West Date Palm Grove',
    cropAr: 'نخيل', areaHa: 12.3, ndvi: 0.65, lai: 2.8, soilMoisture: 32,
    yieldTonHa: 8.2, tempC: 30, rainfall: 12, windSpeed: 18,
    healthStatus: 'moderate', healthStatusAr: 'معتدل',
  },
  {
    id: 'FIELD-005', nameAr: 'حقل البرسيم المركزي', nameEn: 'Central Alfalfa Field',
    cropAr: 'برسيم', areaHa: 6.7, ndvi: 0.44, lai: 1.9, soilMoisture: 28,
    yieldTonHa: 12.0, tempC: 28, rainfall: 8, windSpeed: 20,
    healthStatus: 'stressed', healthStatusAr: 'مجهد',
  },
];

const METRICS: ComparisonMetric[] = [
  { key: 'ndvi', labelAr: 'مؤشر الغطاء النباتي', labelEn: 'NDVI', unit: '', higherIsBetter: true, icon: Leaf },
  { key: 'lai', labelAr: 'مؤشر مساحة الورقة', labelEn: 'LAI', unit: '', higherIsBetter: true, icon: Leaf },
  { key: 'soilMoisture', labelAr: 'رطوبة التربة', labelEn: 'Soil Moisture', unit: '%', higherIsBetter: true, icon: Droplets },
  { key: 'yieldTonHa', labelAr: 'الإنتاجية', labelEn: 'Yield', unit: 'طن/هـ', higherIsBetter: true, icon: BarChart3 },
  { key: 'tempC', labelAr: 'درجة الحرارة', labelEn: 'Temperature', unit: '°C', higherIsBetter: false, icon: Thermometer },
  { key: 'rainfall', labelAr: 'هطول الأمطار', labelEn: 'Rainfall', unit: 'مم', higherIsBetter: true, icon: CloudRain },
  { key: 'windSpeed', labelAr: 'سرعة الرياح', labelEn: 'Wind Speed', unit: 'كم/س', higherIsBetter: false, icon: Wind },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const HEALTH_COLORS: Record<FieldData['healthStatus'], string> = {
  healthy: 'text-green-600', moderate: 'text-yellow-600', stressed: 'text-orange-500', critical: 'text-red-600',
};

const HEALTH_DOT: Record<FieldData['healthStatus'], string> = {
  healthy: 'bg-green-500', moderate: 'bg-yellow-500', stressed: 'bg-orange-500', critical: 'bg-red-500',
};

type Winner = 'A' | 'B' | 'tie';

function getWinner(metric: ComparisonMetric, a: number, b: number): Winner {
  if (a === b) return 'tie';
  if (metric.higherIsBetter) return a > b ? 'A' : 'B';
  return a < b ? 'A' : 'B';
}

function formatVal(key: MetricKey, value: number, unit: string): string {
  if (key === 'ndvi' || key === 'lai') return value.toFixed(2);
  if (key === 'soilMoisture') return `${value}${unit}`;
  return `${value} ${unit}`.trim();
}

function computeDiff(key: MetricKey, a: number, b: number): string {
  const diff = a - b;
  const prefix = diff > 0 ? '+' : '';
  if (key === 'ndvi' || key === 'lai') return `${prefix}${diff.toFixed(2)}`;
  return `${prefix}${diff}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function FieldComparisonClient() {
  const [fieldAId, setFieldAId] = useState(MOCK_FIELDS[0].id);
  const [fieldBId, setFieldBId] = useState(MOCK_FIELDS[1].id);

  const fieldA = useMemo(() => MOCK_FIELDS.find((f) => f.id === fieldAId) ?? MOCK_FIELDS[0], [fieldAId]);
  const fieldB = useMemo(() => MOCK_FIELDS.find((f) => f.id === fieldBId) ?? MOCK_FIELDS[1], [fieldBId]);

  const results = useMemo(() => {
    return METRICS.map((metric) => {
      const valA = fieldA[metric.key];
      const valB = fieldB[metric.key];
      return { metric, valA, valB, winner: getWinner(metric, valA, valB), diff: computeDiff(metric.key, valA, valB) };
    });
  }, [fieldA, fieldB]);

  const aWins = results.filter((r) => r.winner === 'A').length;
  const bWins = results.filter((r) => r.winner === 'B').length;
  const overallWinner = aWins > bWins ? 'A' : bWins > aWins ? 'B' : null;

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-5">
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">مقارنة الحقول</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Field Comparison — مقارنة جنبًا إلى جنب للمؤشرات الزراعية
        </p>
      </div>

      <main className="p-6 space-y-6 max-w-6xl mx-auto">
        {/* Field Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">اختر الحقل أ</label>
            <select
              value={fieldAId}
              onChange={(e) => setFieldAId(e.target.value)}
              className="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {MOCK_FIELDS.map((f) => (
                <option key={f.id} value={f.id} disabled={f.id === fieldBId}>
                  {f.nameAr} ({f.id})
                </option>
              ))}
            </select>
          </div>

          <div className="hidden md:flex items-center justify-center pb-1">
            <div className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
              <Scale className="w-5 h-5 text-gray-400" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">اختر الحقل ب</label>
            <select
              value={fieldBId}
              onChange={(e) => setFieldBId(e.target.value)}
              className="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {MOCK_FIELDS.map((f) => (
                <option key={f.id} value={f.id} disabled={f.id === fieldAId}>
                  {f.nameAr} ({f.id})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Field Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[{ field: fieldA, side: 'A' as const }, { field: fieldB, side: 'B' as const }].map(({ field, side }) => {
            const borderColor = side === 'A' ? 'border-green-500' : 'border-blue-500';
            const badgeColor = side === 'A' ? 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300' : 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300';

            return (
              <div key={field.id} className={`bg-white dark:bg-gray-800 rounded-xl border-2 ${borderColor} p-5`}>
                <div className="flex items-center justify-between mb-3">
                  <span className={`text-xs font-bold px-2 py-1 rounded-lg ${badgeColor}`}>
                    {side === 'A' ? 'حقل أ' : 'حقل ب'}
                  </span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">{field.id}</span>
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-1">{field.nameAr}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{field.nameEn}</p>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">المحصول</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">{field.cropAr}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">المساحة</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">{field.areaHa} هكتار</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">NDVI</span>
                    <span className="font-bold text-gray-900 dark:text-gray-100">{field.ndvi.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500 dark:text-gray-400">الحالة الصحية</span>
                    <span className={`flex items-center gap-1.5 font-medium ${HEALTH_COLORS[field.healthStatus]}`}>
                      {field.healthStatusAr}
                      <span className={`inline-block w-2.5 h-2.5 rounded-full ${HEALTH_DOT[field.healthStatus]}`} />
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Comparison Table */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-700 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <h2 className="text-base font-bold text-gray-900 dark:text-gray-100">جدول المقارنة</h2>
            <span className="text-sm text-gray-400 dark:text-gray-500 mr-1">Comparison Metrics</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400">
                  <th className="px-5 py-3 text-right font-medium">المؤشر</th>
                  <th className="px-5 py-3 text-center font-medium">حقل أ</th>
                  <th className="px-5 py-3 text-center font-medium">حقل ب</th>
                  <th className="px-5 py-3 text-center font-medium">الفرق</th>
                  <th className="px-5 py-3 text-center font-medium">الأفضل</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                {results.map(({ metric, valA, valB, winner, diff }) => {
                  const MetricIcon = metric.icon;
                  return (
                    <tr key={metric.key} className="hover:bg-gray-50 dark:hover:bg-gray-900/30 transition-colors">
                      <td className="px-5 py-3.5 flex items-center gap-2">
                        <MetricIcon className="w-4 h-4 text-gray-400" />
                        <span className="font-medium text-gray-900 dark:text-gray-100">{metric.labelAr}</span>
                        <span className="text-gray-400 text-xs">({metric.labelEn})</span>
                      </td>
                      <td className={`px-5 py-3.5 text-center font-mono ${winner === 'A' ? 'font-bold text-green-700 dark:text-green-400' : 'text-gray-700 dark:text-gray-300'}`}>
                        {formatVal(metric.key, valA, metric.unit)}
                      </td>
                      <td className={`px-5 py-3.5 text-center font-mono ${winner === 'B' ? 'font-bold text-green-700 dark:text-green-400' : 'text-gray-700 dark:text-gray-300'}`}>
                        {formatVal(metric.key, valB, metric.unit)}
                      </td>
                      <td className="px-5 py-3.5 text-center font-mono text-gray-500 dark:text-gray-400">{diff}</td>
                      <td className="px-5 py-3.5 text-center">
                        {winner === 'tie' ? (
                          <span className="text-gray-400 text-xs">تعادل</span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-green-600 dark:text-green-400 text-xs font-medium">
                            <ArrowRight className={`w-3.5 h-3.5 ${winner === 'B' ? 'rotate-180' : ''}`} />
                            {winner === 'A' ? 'حقل أ' : 'حقل ب'}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Overall Winner */}
        <div className={`rounded-xl p-5 flex flex-col sm:flex-row items-center gap-4 ${
          overallWinner
            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
            : 'bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
        }`}>
          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
            overallWinner ? 'bg-green-100 dark:bg-green-900/40' : 'bg-gray-200 dark:bg-gray-700'
          }`}>
            <Trophy className={`w-6 h-6 ${overallWinner ? 'text-green-600 dark:text-green-400' : 'text-gray-400'}`} />
          </div>
          <div className="text-center sm:text-right flex-1">
            {overallWinner ? (
              <>
                <p className="text-lg font-bold text-green-800 dark:text-green-300">
                  الأفضل أداءً: {overallWinner === 'A' ? fieldA.nameAr : fieldB.nameAr}
                </p>
                <p className="text-sm text-green-600 dark:text-green-400 mt-0.5">
                  تفوق في {overallWinner === 'A' ? aWins : bWins} مؤشرات مقابل {overallWinner === 'A' ? bWins : aWins} مؤشرات
                </p>
              </>
            ) : (
              <>
                <p className="text-lg font-bold text-gray-700 dark:text-gray-300">تعادل بين الحقلين</p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                  كلا الحقلين متساويان في عدد المؤشرات ({aWins} مقابل {bWins})
                </p>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
