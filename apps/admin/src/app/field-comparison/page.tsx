'use client';

/**
 * Field Comparison Page
 * مقارنة الحقول - مقارنة جنبًا إلى جنب باستخدام FieldComparator
 *
 * Compares two fields side-by-side using metrics from FieldComparator
 * (fieldview_features.py) including NDVI, LAI, area, and soil moisture.
 */

import { useState, useMemo, useEffect } from 'react';
import Header from '@/components/layout/Header';
import { Trophy, ArrowRight, TrendingUp, Scale } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { FIELD_ENDPOINTS } from '@sahool/shared-types/contracts';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface FieldData {
  id: string;
  name: string;
  nameAr: string;
  crop: string;
  cropAr: string;
  areaHa: number;
  ndvi: number;
  lai: number;
  soilMoisture: number;
  healthStatus: 'healthy' | 'moderate' | 'stressed' | 'critical';
  healthStatusAr: string;
}

type MetricKey = 'ndvi' | 'lai' | 'areaHa' | 'soilMoisture';

interface ComparisonMetric {
  key: MetricKey;
  labelAr: string;
  labelEn: string;
  unit: string;
  higherIsBetter: boolean;
}

// ---------------------------------------------------------------------------
// Mock Data (FieldComparator output simulation)
// ---------------------------------------------------------------------------

const MOCK_FIELDS: FieldData[] = [
  {
    id: 'FIELD-001',
    name: 'North Wheat Block',
    nameAr: 'حقل القمح الشمالي',
    crop: 'Wheat',
    cropAr: 'قمح',
    areaHa: 5.2,
    ndvi: 0.72,
    lai: 3.1,
    soilMoisture: 45,
    healthStatus: 'healthy',
    healthStatusAr: 'صحي',
  },
  {
    id: 'FIELD-002',
    name: 'South Barley Strip',
    nameAr: 'شريط الشعير الجنوبي',
    crop: 'Barley',
    cropAr: 'شعير',
    areaHa: 8.0,
    ndvi: 0.58,
    lai: 2.2,
    soilMoisture: 38,
    healthStatus: 'stressed',
    healthStatusAr: 'مجهد',
  },
  {
    id: 'FIELD-003',
    name: 'East Tomato Greenhouse',
    nameAr: 'دفيئة الطماطم الشرقية',
    crop: 'Tomato',
    cropAr: 'طماطم',
    areaHa: 1.5,
    ndvi: 0.81,
    lai: 4.0,
    soilMoisture: 60,
    healthStatus: 'healthy',
    healthStatusAr: 'صحي',
  },
  {
    id: 'FIELD-004',
    name: 'West Date Palm Grove',
    nameAr: 'بستان النخيل الغربي',
    crop: 'Date Palm',
    cropAr: 'نخيل',
    areaHa: 12.3,
    ndvi: 0.65,
    lai: 2.8,
    soilMoisture: 32,
    healthStatus: 'moderate',
    healthStatusAr: 'معتدل',
  },
  {
    id: 'FIELD-005',
    name: 'Central Alfalfa Field',
    nameAr: 'حقل البرسيم المركزي',
    crop: 'Alfalfa',
    cropAr: 'برسيم',
    areaHa: 6.7,
    ndvi: 0.44,
    lai: 1.9,
    soilMoisture: 28,
    healthStatus: 'stressed',
    healthStatusAr: 'مجهد',
  },
];

const COMPARISON_METRICS: ComparisonMetric[] = [
  { key: 'ndvi', labelAr: 'مؤشر الغطاء النباتي', labelEn: 'NDVI', unit: '', higherIsBetter: true },
  { key: 'lai', labelAr: 'مؤشر مساحة الورقة', labelEn: 'LAI', unit: '', higherIsBetter: true },
  { key: 'areaHa', labelAr: 'المساحة', labelEn: 'Area', unit: 'ha', higherIsBetter: false },
  { key: 'soilMoisture', labelAr: 'رطوبة التربة', labelEn: 'Soil Moisture', unit: '%', higherIsBetter: true },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const HEALTH_COLORS: Record<FieldData['healthStatus'], string> = {
  healthy: 'text-green-600',
  moderate: 'text-yellow-600',
  stressed: 'text-orange-500',
  critical: 'text-red-600',
};

const HEALTH_DOT: Record<FieldData['healthStatus'], string> = {
  healthy: 'bg-green-500',
  moderate: 'bg-yellow-500',
  stressed: 'bg-orange-500',
  critical: 'bg-red-500',
};

function formatMetricValue(key: MetricKey, value: number, unit: string): string {
  if (key === 'areaHa') return `${value.toFixed(1)} ${unit}`;
  if (key === 'soilMoisture') return `${value}${unit}`;
  return value.toFixed(2);
}

function computeDiff(key: MetricKey, a: number, b: number): string {
  const diff = a - b;
  const prefix = diff > 0 ? '+' : '';
  if (key === 'areaHa') return `${prefix}${diff.toFixed(1)}`;
  if (key === 'soilMoisture') return `${prefix}${diff}%`;
  return `${prefix}${diff.toFixed(2)}`;
}

type Winner = 'A' | 'B' | 'neutral';

function getWinner(metric: ComparisonMetric, a: number, b: number): Winner {
  if (!metric.higherIsBetter) return 'neutral';
  if (a > b) return 'A';
  if (b > a) return 'B';
  return 'neutral';
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function FieldSelector({
  label,
  selectedId,
  excludeId,
  onChange,
  fields,
}: {
  label: string;
  selectedId: string;
  excludeId: string;
  onChange: (id: string) => void;
  fields: FieldData[];
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</label>
      <select
        value={selectedId}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-sahool-500"
      >
        {fields.map((f) => (
          <option key={f.id} value={f.id} disabled={f.id === excludeId}>
            {f.nameAr} ({f.id})
          </option>
        ))}
      </select>
    </div>
  );
}

function FieldCard({ field, side }: { field: FieldData; side: 'A' | 'B' }) {
  const borderColor = side === 'A' ? 'border-sahool-500' : 'border-blue-500';
  const badgeColor = side === 'A' ? 'bg-sahool-100 text-sahool-700 dark:bg-sahool-900/50 dark:text-sahool-300' : 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300';

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl border-2 ${borderColor} p-5`}>
      <div className="flex items-center justify-between mb-3">
        <span className={`text-xs font-bold px-2 py-1 rounded-lg ${badgeColor}`}>
          {side === 'A' ? 'حقل أ' : 'حقل ب'}
        </span>
        <span className="text-xs text-gray-400 dark:text-gray-500">{field.id}</span>
      </div>

      <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-1">{field.nameAr}</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{field.name}</p>

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
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function FieldComparisonPage() {
  const [fieldOptions, setFieldOptions] = useState<FieldData[]>(MOCK_FIELDS);
  const [isLoadingFields, setIsLoadingFields] = useState(true);
  const [fieldAId, setFieldAId] = useState(MOCK_FIELDS[0]?.id ?? '');
  const [fieldBId, setFieldBId] = useState(MOCK_FIELDS[1]?.id ?? '');

  useEffect(() => {
    apiClient.get(FIELD_ENDPOINTS.LIST).then((result) => {
      if (result.success && result.data) {
        const items = Array.isArray(result.data) ? result.data : [];
        const mapped = (items as Array<Record<string, unknown>>).map((f): FieldData => ({
          id: String(f.id ?? f.field_id ?? ''),
          name: String(f.name ?? f.name_en ?? ''),
          nameAr: String(f.name_ar ?? f.nameAr ?? f.name ?? ''),
          crop: String(f.crop ?? f.crop_type ?? ''),
          cropAr: String(f.crop_ar ?? f.cropAr ?? f.crop ?? ''),
          areaHa: Number(f.area_ha ?? f.areaHa ?? 0),
          ndvi: Number(f.ndvi ?? 0),
          lai: Number(f.lai ?? 0),
          soilMoisture: Number(f.soil_moisture ?? f.soilMoisture ?? 0),
          healthStatus: (f.health_status ?? f.healthStatus ?? 'moderate') as FieldData['healthStatus'],
          healthStatusAr: String(f.health_status_ar ?? f.healthStatusAr ?? 'معتدل'),
        })).filter((f) => f.id);
        if (mapped.length > 0) {
          setFieldOptions(mapped);
          setFieldAId(mapped[0]?.id ?? MOCK_FIELDS[0]?.id ?? '');
          setFieldBId(mapped[1]?.id ?? MOCK_FIELDS[1]?.id ?? '');
        }
      }
    }).catch(() => {/* keep MOCK_FIELDS */}).finally(() => setIsLoadingFields(false));
  }, []);

  const fieldA = useMemo(() => fieldOptions.find((f) => f.id === fieldAId) ?? fieldOptions[0]!, [fieldAId, fieldOptions]);
  const fieldB = useMemo(() => fieldOptions.find((f) => f.id === fieldBId) ?? fieldOptions[1]!, [fieldBId, fieldOptions]);

  // Compute winners per metric
  const results = useMemo(() => {
    return COMPARISON_METRICS.map((metric) => {
      const valA = fieldA[metric.key];
      const valB = fieldB[metric.key];
      const winner = getWinner(metric, valA, valB);
      return { metric, valA, valB, winner, diff: computeDiff(metric.key, valA, valB) };
    });
  }, [fieldA, fieldB]);

  const aWins = results.filter((r) => r.winner === 'A').length;
  const bWins = results.filter((r) => r.winner === 'B').length;
  const overallWinner = aWins > bWins ? fieldA : bWins > aWins ? fieldB : null;
  const overallWinnerSide = aWins > bWins ? 'A' : bWins > aWins ? 'B' : null;

  return (
    <div className="p-6" dir="rtl">
      <Header title="مقارنة الحقول" subtitle="Field Comparison" />

      {isLoadingFields && (
        <p className="mt-2 text-sm text-gray-400 dark:text-gray-500">جارٍ تحميل الحقول...</p>
      )}

      {/* Field Selectors */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 items-end mb-6">
        <FieldSelector
          label="اختر الحقل أ"
          selectedId={fieldAId}
          excludeId={fieldBId}
          onChange={setFieldAId}
          fields={fieldOptions}
        />

        <div className="hidden md:flex items-center justify-center pb-1">
          <div className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <Scale className="w-5 h-5 text-gray-400" />
          </div>
        </div>

        <FieldSelector
          label="اختر الحقل ب"
          selectedId={fieldBId}
          excludeId={fieldAId}
          onChange={setFieldBId}
          fields={fieldOptions}
        />
      </div>

      {/* Field Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <FieldCard field={fieldA} side="A" />
        <FieldCard field={fieldB} side="B" />
      </div>

      {/* Comparison Metrics Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden mb-6">
        <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-700 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-sahool-600" />
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
              {results.map(({ metric, valA, valB, winner, diff }) => (
                <tr key={metric.key} className="hover:bg-gray-50 dark:hover:bg-gray-900/30 transition-colors">
                  <td className="px-5 py-3.5">
                    <span className="font-medium text-gray-900 dark:text-gray-100">{metric.labelAr}</span>
                    <span className="text-gray-400 dark:text-gray-500 text-xs mr-2">({metric.labelEn})</span>
                  </td>
                  <td className={`px-5 py-3.5 text-center font-mono ${winner === 'A' ? 'font-bold text-green-700 dark:text-green-400' : 'text-gray-700 dark:text-gray-300'}`}>
                    {formatMetricValue(metric.key, valA, metric.unit)}
                  </td>
                  <td className={`px-5 py-3.5 text-center font-mono ${winner === 'B' ? 'font-bold text-green-700 dark:text-green-400' : 'text-gray-700 dark:text-gray-300'}`}>
                    {formatMetricValue(metric.key, valB, metric.unit)}
                  </td>
                  <td className="px-5 py-3.5 text-center font-mono text-gray-500 dark:text-gray-400">
                    {diff}
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    {winner === 'neutral' ? (
                      <span className="inline-flex items-center gap-1 text-gray-400 dark:text-gray-500 text-xs">
                        <span className="w-2 h-2 bg-gray-300 dark:bg-gray-600 rounded-full" />
                        محايد
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-green-600 dark:text-green-400 text-xs font-medium">
                        <ArrowRight className={`w-3.5 h-3.5 ${winner === 'B' ? 'rotate-180' : ''}`} />
                        {winner === 'A' ? 'حقل أ' : 'حقل ب'}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Overall Winner Banner */}
      <div
        className={`rounded-xl p-5 flex flex-col sm:flex-row items-center gap-4 ${
          overallWinner
            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
            : 'bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
        }`}
      >
        <div
          className={`w-12 h-12 rounded-full flex items-center justify-center ${
            overallWinner
              ? 'bg-green-100 dark:bg-green-900/40'
              : 'bg-gray-200 dark:bg-gray-700'
          }`}
        >
          <Trophy
            className={`w-6 h-6 ${
              overallWinner ? 'text-green-600 dark:text-green-400' : 'text-gray-400 dark:text-gray-500'
            }`}
          />
        </div>

        <div className="text-center sm:text-right flex-1">
          {overallWinner ? (
            <>
              <p className="text-lg font-bold text-green-800 dark:text-green-300">
                الأفضل أداءً: {overallWinner.nameAr}
              </p>
              <p className="text-sm text-green-600 dark:text-green-400 mt-0.5">
                تفوق في {overallWinnerSide === 'A' ? aWins : bWins} مؤشرات مقابل{' '}
                {overallWinnerSide === 'A' ? bWins : aWins} مؤشرات
              </p>
              <p className="text-xs text-green-500 dark:text-green-500 mt-1">
                Best Performer: {overallWinner.name} ({overallWinnerSide === 'A' ? aWins : bWins} vs{' '}
                {overallWinnerSide === 'A' ? bWins : aWins} metrics)
              </p>
            </>
          ) : (
            <>
              <p className="text-lg font-bold text-gray-700 dark:text-gray-300">تعادل بين الحقلين</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                كلا الحقلين متساويان في عدد المؤشرات ({aWins} مقابل {bWins})
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                Tie: Both fields are equal in performance metrics
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
