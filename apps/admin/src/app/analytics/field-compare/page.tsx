'use client';

// Advanced Field Analysis - Side-by-Side Comparison
// تحليل الحقول المتقدم - مقارنة جنبًا إلى جنب

import { useEffect, useState, useCallback } from 'react';
import Header from '@/components/layout/Header';
import { adminApiClient as apiClient } from '@/lib/api';
import { API_PATHS } from '@/config/api';
import {
  ArrowLeftRight,
  Leaf,
  Droplets,
  Thermometer,
  BarChart3,
  RefreshCw,
  Layers,
  Zap,
  Sun,
  CloudRain,
} from 'lucide-react';
import { logger } from '../../../lib/logger';

// ═══════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════

interface FieldMetrics {
  id: string;
  name: string;
  farmName: string;
  area: number;
  cropType: string;
  cropStage: string;
  soilType: string;
  irrigationType: string;
  governorate: string;
  plantingDate: string;
  ndvi: number;
  ndviTrend: 'up' | 'down' | 'stable';
  lai: number;
  soilMoisture: number;
  soilMoistureTarget: number;
  temperature: number;
  humidity: number;
  rainfall7d: number;
  etActual: number;
  etReference: number;
  yieldEstimate: number;
  yieldTarget: number;
  nitrogenLevel: number;
  phosphorusLevel: number;
  potassiumLevel: number;
  ph: number;
  ec: number;
  organicMatter: number;
  fertilizerApplied: number;
  irrigationApplied: number;
  diseaseRisk: 'low' | 'medium' | 'high';
  pestPressure: 'low' | 'medium' | 'high';
  overallHealth: 'excellent' | 'good' | 'fair' | 'poor';
}

// ═══════════════════════════════════════════════════════════════
// Mock Data
// ═══════════════════════════════════════════════════════════════

const MOCK_FIELDS: FieldMetrics[] = [
  {
    id: 'FLD-001',
    name: 'حقل القمح الشمالي',
    farmName: 'مزرعة الوادي',
    area: 5.2,
    cropType: 'قمح',
    cropStage: 'التفريع',
    soilType: 'طيني',
    irrigationType: 'محوري',
    governorate: 'صنعاء',
    plantingDate: '2025-11-15',
    ndvi: 0.72,
    ndviTrend: 'up',
    lai: 3.8,
    soilMoisture: 45,
    soilMoistureTarget: 50,
    temperature: 18,
    humidity: 62,
    rainfall7d: 12,
    etActual: 4.2,
    etReference: 5.0,
    yieldEstimate: 4.8,
    yieldTarget: 5.5,
    nitrogenLevel: 28,
    phosphorusLevel: 22,
    potassiumLevel: 180,
    ph: 7.2,
    ec: 1.8,
    organicMatter: 2.5,
    fertilizerApplied: 120,
    irrigationApplied: 3200,
    diseaseRisk: 'low',
    pestPressure: 'low',
    overallHealth: 'good',
  },
  {
    id: 'FLD-003',
    name: 'حقل القمح الشرقي',
    farmName: 'مزرعة الوادي',
    area: 8.5,
    cropType: 'قمح',
    cropStage: 'التفريع',
    soilType: 'طيني رملي',
    irrigationType: 'تنقيط',
    governorate: 'صنعاء',
    plantingDate: '2025-11-20',
    ndvi: 0.58,
    ndviTrend: 'down',
    lai: 2.9,
    soilMoisture: 35,
    soilMoistureTarget: 48,
    temperature: 19,
    humidity: 58,
    rainfall7d: 8,
    etActual: 3.8,
    etReference: 5.0,
    yieldEstimate: 3.5,
    yieldTarget: 5.0,
    nitrogenLevel: 15,
    phosphorusLevel: 18,
    potassiumLevel: 140,
    ph: 7.5,
    ec: 2.4,
    organicMatter: 1.8,
    fertilizerApplied: 85,
    irrigationApplied: 2800,
    diseaseRisk: 'medium',
    pestPressure: 'medium',
    overallHealth: 'fair',
  },
  {
    id: 'FLD-007',
    name: 'حقل الطماطم',
    farmName: 'مزرعة السهل',
    area: 3.2,
    cropType: 'طماطم',
    cropStage: 'الإزهار',
    soilType: 'طيني',
    irrigationType: 'تنقيط',
    governorate: 'إب',
    plantingDate: '2026-01-10',
    ndvi: 0.68,
    ndviTrend: 'stable',
    lai: 4.2,
    soilMoisture: 52,
    soilMoistureTarget: 55,
    temperature: 22,
    humidity: 70,
    rainfall7d: 5,
    etActual: 5.5,
    etReference: 6.0,
    yieldEstimate: 42,
    yieldTarget: 50,
    nitrogenLevel: 32,
    phosphorusLevel: 28,
    potassiumLevel: 200,
    ph: 6.8,
    ec: 1.5,
    organicMatter: 3.2,
    fertilizerApplied: 180,
    irrigationApplied: 4500,
    diseaseRisk: 'medium',
    pestPressure: 'high',
    overallHealth: 'good',
  },
  {
    id: 'FLD-012',
    name: 'حقل الشعير',
    farmName: 'مزرعة الجبل',
    area: 6.0,
    cropType: 'شعير',
    cropStage: 'السنبلة',
    soilType: 'رملي',
    irrigationType: 'محوري',
    governorate: 'تعز',
    plantingDate: '2025-11-05',
    ndvi: 0.65,
    ndviTrend: 'stable',
    lai: 3.5,
    soilMoisture: 40,
    soilMoistureTarget: 42,
    temperature: 20,
    humidity: 55,
    rainfall7d: 15,
    etActual: 4.0,
    etReference: 4.8,
    yieldEstimate: 3.8,
    yieldTarget: 4.2,
    nitrogenLevel: 25,
    phosphorusLevel: 20,
    potassiumLevel: 160,
    ph: 7.8,
    ec: 2.1,
    organicMatter: 1.5,
    fertilizerApplied: 95,
    irrigationApplied: 2600,
    diseaseRisk: 'low',
    pestPressure: 'low',
    overallHealth: 'good',
  },
];

// ═══════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════

function getRiskColor(risk: string): string {
  const colors: Record<string, string> = {
    low: 'text-green-600 dark:text-green-400',
    medium: 'text-yellow-600 dark:text-yellow-400',
    high: 'text-red-600 dark:text-red-400',
  };
  return colors[risk] ?? 'text-gray-600';
}

function getRiskLabel(risk: string): string {
  const labels: Record<string, string> = { low: 'منخفض', medium: 'متوسط', high: 'مرتفع' };
  return labels[risk] ?? risk;
}

function getHealthColor(health: FieldMetrics['overallHealth']): string {
  const colors = {
    excellent: 'text-emerald-600',
    good: 'text-green-600',
    fair: 'text-yellow-600',
    poor: 'text-red-600',
  };
  return colors[health];
}

function getHealthLabel(health: FieldMetrics['overallHealth']): string {
  const labels = { excellent: 'ممتاز', good: 'جيد', fair: 'مقبول', poor: 'ضعيف' };
  return labels[health];
}

function compareValue(a: number, b: number): { diff: number; better: 'a' | 'b' | 'equal' } {
  const diff = a - b;
  if (Math.abs(diff) < 0.01) return { diff: 0, better: 'equal' };
  return { diff, better: diff > 0 ? 'a' : 'b' };
}

// ═══════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════

export default function FieldComparePage() {
  const [fields, setFields] = useState<FieldMetrics[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fieldAId, setFieldAId] = useState<string>('');
  const [fieldBId, setFieldBId] = useState<string>('');

  const loadFields = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await apiClient.get<FieldMetrics[]>(API_PATHS.fields.list);
      if (result.success && result.data) {
        const data = Array.isArray(result.data) ? result.data : [];
        setFields(data.length > 0 ? data : MOCK_FIELDS);
      } else {
        throw new Error(result.error || 'Failed to fetch fields');
      }
    } catch {
      logger.info('Using mock field data for comparison');
      setFields(MOCK_FIELDS);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFields();
  }, [loadFields]);

  useEffect(() => {
    if (fields.length >= 2 && !fieldAId && !fieldBId) {
      setFieldAId(fields[0]!.id);
      setFieldBId(fields[1]!.id);
    }
  }, [fields, fieldAId, fieldBId]);

  const fieldA = fields.find((f) => f.id === fieldAId);
  const fieldB = fields.find((f) => f.id === fieldBId);

  function swapFields() {
    setFieldAId(fieldBId);
    setFieldBId(fieldAId);
  }

  // Comparison row component
  function ComparisonRow({
    label,
    icon,
    valueA,
    valueB,
    unit = '',
    higherIsBetter = true,
    format,
  }: {
    label: string;
    icon?: React.ReactNode;
    valueA: number | string;
    valueB: number | string;
    unit?: string;
    higherIsBetter?: boolean;
    format?: (v: number | string) => string;
  }) {
    const numA = typeof valueA === 'number' ? valueA : 0;
    const numB = typeof valueB === 'number' ? valueB : 0;
    const isNumeric = typeof valueA === 'number' && typeof valueB === 'number';
    const comparison = isNumeric ? compareValue(numA, numB) : { diff: 0, better: 'equal' as const };

    const getHighlight = (side: 'a' | 'b') => {
      if (!isNumeric || comparison.better === 'equal') return '';
      const isBetter = higherIsBetter ? comparison.better === side : comparison.better !== side;
      return isBetter
        ? 'bg-emerald-50 dark:bg-emerald-900/10 font-semibold text-emerald-700 dark:text-emerald-400'
        : '';
    };

    const displayA = format ? format(valueA) : `${valueA}${unit ? ` ${unit}` : ''}`;
    const displayB = format ? format(valueB) : `${valueB}${unit ? ` ${unit}` : ''}`;

    return (
      <tr className="border-b border-gray-100 dark:border-gray-800">
        <td className={`px-4 py-3 text-center ${getHighlight('a')}`}>{displayA}</td>
        <td className="px-4 py-3 text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            {icon}
            <span>{label}</span>
          </div>
        </td>
        <td className={`px-4 py-3 text-center ${getHighlight('b')}`}>{displayB}</td>
      </tr>
    );
  }

  // Status comparison row
  function StatusRow({
    label,
    icon,
    valueA,
    valueB,
    colorFn,
    labelFn,
  }: {
    label: string;
    icon?: React.ReactNode;
    valueA: string;
    valueB: string;
    colorFn: (v: string) => string;
    labelFn: (v: string) => string;
  }) {
    return (
      <tr className="border-b border-gray-100 dark:border-gray-800">
        <td className="px-4 py-3 text-center">
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${colorFn(valueA)} ${
              valueA === 'low'
                ? 'bg-green-100 dark:bg-green-900/30'
                : valueA === 'medium'
                  ? 'bg-yellow-100 dark:bg-yellow-900/30'
                  : 'bg-red-100 dark:bg-red-900/30'
            }`}
          >
            {labelFn(valueA)}
          </span>
        </td>
        <td className="px-4 py-3 text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            {icon}
            <span>{label}</span>
          </div>
        </td>
        <td className="px-4 py-3 text-center">
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${colorFn(valueB)} ${
              valueB === 'low'
                ? 'bg-green-100 dark:bg-green-900/30'
                : valueB === 'medium'
                  ? 'bg-yellow-100 dark:bg-yellow-900/30'
                  : 'bg-red-100 dark:bg-red-900/30'
            }`}
          >
            {labelFn(valueB)}
          </span>
        </td>
      </tr>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header
        title="مقارنة الحقول المتقدمة"
        subtitle="مقارنة جنبًا إلى جنب بين حقلين لتحديد الفروقات والفرص"
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Field Selectors */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5">
          <div className="flex flex-col md:flex-row items-center gap-4">
            {/* Field A Selector */}
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                الحقل الأول
              </label>
              <select
                value={fieldAId}
                onChange={(e) => setFieldAId(e.target.value)}
                className="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                {fields.map((f) => (
                  <option key={f.id} value={f.id} disabled={f.id === fieldBId}>
                    {f.name} — {f.farmName} ({f.cropType})
                  </option>
                ))}
              </select>
            </div>

            {/* Swap Button */}
            <button
              onClick={swapFields}
              className="mt-6 md:mt-0 p-3 rounded-full border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              title="تبديل الحقول"
            >
              <ArrowLeftRight className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>

            {/* Field B Selector */}
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                الحقل الثاني
              </label>
              <select
                value={fieldBId}
                onChange={(e) => setFieldBId(e.target.value)}
                className="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                {fields.map((f) => (
                  <option key={f.id} value={f.id} disabled={f.id === fieldAId}>
                    {f.name} — {f.farmName} ({f.cropType})
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={loadFields}
              className="mt-6 md:mt-0 p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              title="تحديث البيانات"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600" />
          </div>
        ) : !fieldA || !fieldB ? (
          <div className="text-center py-16 text-gray-500 dark:text-gray-400">
            <ArrowLeftRight className="w-12 h-12 mx-auto mb-3 opacity-40" />
            <p>اختر حقلين للمقارنة</p>
          </div>
        ) : (
          <>
            {/* Field Header Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[fieldA, fieldB].map((field) => (
                <div
                  key={field.id}
                  className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {field.name}
                    </h3>
                    <span
                      className={`text-sm font-semibold ${getHealthColor(field.overallHealth)}`}
                    >
                      {getHealthLabel(field.overallHealth)}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span>المزرعة: {field.farmName}</span>
                    <span>المحصول: {field.cropType}</span>
                    <span>المرحلة: {field.cropStage}</span>
                    <span>المساحة: {field.area} هـ</span>
                    <span>نوع التربة: {field.soilType}</span>
                    <span>الري: {field.irrigationType}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Comparison Table */}
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-gray-200 dark:border-gray-800">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  مقارنة المؤشرات
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-4 py-3 text-center font-medium text-gray-600 dark:text-gray-400 w-1/3">
                        {fieldA.name}
                      </th>
                      <th className="px-4 py-3 text-center font-medium text-gray-600 dark:text-gray-400 w-1/3">
                        المؤشر
                      </th>
                      <th className="px-4 py-3 text-center font-medium text-gray-600 dark:text-gray-400 w-1/3">
                        {fieldB.name}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* Vegetation Section */}
                    <tr className="bg-emerald-50/50 dark:bg-emerald-900/5">
                      <td
                        colSpan={3}
                        className="px-4 py-2 text-xs font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider"
                      >
                        مؤشرات الغطاء النباتي
                      </td>
                    </tr>
                    <ComparisonRow
                      label="NDVI"
                      icon={<Leaf className="w-4 h-4" />}
                      valueA={fieldA.ndvi}
                      valueB={fieldB.ndvi}
                    />
                    <ComparisonRow
                      label="LAI"
                      icon={<Layers className="w-4 h-4" />}
                      valueA={fieldA.lai}
                      valueB={fieldB.lai}
                    />

                    {/* Soil Section */}
                    <tr className="bg-amber-50/50 dark:bg-amber-900/5">
                      <td
                        colSpan={3}
                        className="px-4 py-2 text-xs font-semibold text-amber-700 dark:text-amber-400 uppercase tracking-wider"
                      >
                        التربة والمغذيات
                      </td>
                    </tr>
                    <ComparisonRow
                      label="رطوبة التربة"
                      icon={<Droplets className="w-4 h-4" />}
                      valueA={fieldA.soilMoisture}
                      valueB={fieldB.soilMoisture}
                      unit="%"
                    />
                    <ComparisonRow
                      label="النيتروجين"
                      valueA={fieldA.nitrogenLevel}
                      valueB={fieldB.nitrogenLevel}
                      unit="ppm"
                    />
                    <ComparisonRow
                      label="الفوسفور"
                      valueA={fieldA.phosphorusLevel}
                      valueB={fieldB.phosphorusLevel}
                      unit="ppm"
                    />
                    <ComparisonRow
                      label="البوتاسيوم"
                      valueA={fieldA.potassiumLevel}
                      valueB={fieldB.potassiumLevel}
                      unit="ppm"
                    />
                    <ComparisonRow
                      label="pH"
                      valueA={fieldA.ph}
                      valueB={fieldB.ph}
                      higherIsBetter={false}
                    />
                    <ComparisonRow
                      label="EC"
                      valueA={fieldA.ec}
                      valueB={fieldB.ec}
                      unit="dS/m"
                      higherIsBetter={false}
                    />
                    <ComparisonRow
                      label="المادة العضوية"
                      valueA={fieldA.organicMatter}
                      valueB={fieldB.organicMatter}
                      unit="%"
                    />

                    {/* Climate Section */}
                    <tr className="bg-blue-50/50 dark:bg-blue-900/5">
                      <td
                        colSpan={3}
                        className="px-4 py-2 text-xs font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wider"
                      >
                        المناخ والري
                      </td>
                    </tr>
                    <ComparisonRow
                      label="درجة الحرارة"
                      icon={<Thermometer className="w-4 h-4" />}
                      valueA={fieldA.temperature}
                      valueB={fieldB.temperature}
                      unit="°م"
                      higherIsBetter={false}
                    />
                    <ComparisonRow
                      label="الرطوبة"
                      icon={<Sun className="w-4 h-4" />}
                      valueA={fieldA.humidity}
                      valueB={fieldB.humidity}
                      unit="%"
                    />
                    <ComparisonRow
                      label="هطول 7 أيام"
                      icon={<CloudRain className="w-4 h-4" />}
                      valueA={fieldA.rainfall7d}
                      valueB={fieldB.rainfall7d}
                      unit="مم"
                    />
                    <ComparisonRow
                      label="ET الفعلي"
                      valueA={fieldA.etActual}
                      valueB={fieldB.etActual}
                      unit="مم/يوم"
                    />
                    <ComparisonRow
                      label="الري المطبق"
                      valueA={fieldA.irrigationApplied}
                      valueB={fieldB.irrigationApplied}
                      unit="م³"
                    />

                    {/* Yield Section */}
                    <tr className="bg-purple-50/50 dark:bg-purple-900/5">
                      <td
                        colSpan={3}
                        className="px-4 py-2 text-xs font-semibold text-purple-700 dark:text-purple-400 uppercase tracking-wider"
                      >
                        الإنتاجية والتكلفة
                      </td>
                    </tr>
                    <ComparisonRow
                      label="الغلة المتوقعة"
                      icon={<BarChart3 className="w-4 h-4" />}
                      valueA={fieldA.yieldEstimate}
                      valueB={fieldB.yieldEstimate}
                      unit="طن/هـ"
                    />
                    <ComparisonRow
                      label="الغلة المستهدفة"
                      valueA={fieldA.yieldTarget}
                      valueB={fieldB.yieldTarget}
                      unit="طن/هـ"
                    />
                    <ComparisonRow
                      label="نسبة التحقيق"
                      valueA={Number(
                        ((fieldA.yieldEstimate / (fieldA.yieldTarget || 1)) * 100).toFixed(1)
                      )}
                      valueB={Number(
                        ((fieldB.yieldEstimate / (fieldB.yieldTarget || 1)) * 100).toFixed(1)
                      )}
                      unit="%"
                    />
                    <ComparisonRow
                      label="السماد المطبق"
                      icon={<Zap className="w-4 h-4" />}
                      valueA={fieldA.fertilizerApplied}
                      valueB={fieldB.fertilizerApplied}
                      unit="كجم/هـ"
                    />

                    {/* Risk Section */}
                    <tr className="bg-red-50/50 dark:bg-red-900/5">
                      <td
                        colSpan={3}
                        className="px-4 py-2 text-xs font-semibold text-red-700 dark:text-red-400 uppercase tracking-wider"
                      >
                        المخاطر
                      </td>
                    </tr>
                    <StatusRow
                      label="خطر الأمراض"
                      valueA={fieldA.diseaseRisk}
                      valueB={fieldB.diseaseRisk}
                      colorFn={getRiskColor}
                      labelFn={getRiskLabel}
                    />
                    <StatusRow
                      label="ضغط الآفات"
                      valueA={fieldA.pestPressure}
                      valueB={fieldB.pestPressure}
                      colorFn={getRiskColor}
                      labelFn={getRiskLabel}
                    />
                  </tbody>
                </table>
              </div>
            </div>

            {/* Key Insights */}
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                الملاحظات الرئيسية
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* NDVI Difference */}
                {Math.abs(fieldA.ndvi - fieldB.ndvi) > 0.05 && (
                  <div className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <Leaf className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                    <div className="text-sm">
                      <p className="font-medium text-gray-900 dark:text-gray-100">فرق NDVI ملحوظ</p>
                      <p className="text-gray-500 dark:text-gray-400">
                        {fieldA.ndvi > fieldB.ndvi ? fieldA.name : fieldB.name} يتفوق بـ{' '}
                        {Math.abs(fieldA.ndvi - fieldB.ndvi).toFixed(2)} نقطة في مؤشر الغطاء النباتي
                      </p>
                    </div>
                  </div>
                )}

                {/* Soil Moisture */}
                {Math.abs(fieldA.soilMoisture - fieldB.soilMoisture) > 5 && (
                  <div className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <Droplets className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                    <div className="text-sm">
                      <p className="font-medium text-gray-900 dark:text-gray-100">
                        فارق رطوبة التربة
                      </p>
                      <p className="text-gray-500 dark:text-gray-400">
                        فرق {Math.abs(fieldA.soilMoisture - fieldB.soilMoisture)}% في رطوبة التربة —
                        تحقق من كفاءة الري
                      </p>
                    </div>
                  </div>
                )}

                {/* Nitrogen */}
                {Math.abs(fieldA.nitrogenLevel - fieldB.nitrogenLevel) > 5 && (
                  <div className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <Zap className="w-5 h-5 text-orange-600 shrink-0 mt-0.5" />
                    <div className="text-sm">
                      <p className="font-medium text-gray-900 dark:text-gray-100">
                        فرق مستوى النيتروجين
                      </p>
                      <p className="text-gray-500 dark:text-gray-400">
                        {fieldA.nitrogenLevel < fieldB.nitrogenLevel ? fieldA.name : fieldB.name}{' '}
                        يحتاج تسميد نيتروجيني إضافي
                      </p>
                    </div>
                  </div>
                )}

                {/* Yield Gap */}
                {(() => {
                  const achieveA = (fieldA.yieldEstimate / (fieldA.yieldTarget || 1)) * 100;
                  const achieveB = (fieldB.yieldEstimate / (fieldB.yieldTarget || 1)) * 100;
                  return Math.abs(achieveA - achieveB) > 5 ? (
                    <div className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <BarChart3 className="w-5 h-5 text-purple-600 shrink-0 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium text-gray-900 dark:text-gray-100">
                          فجوة الإنتاجية
                        </p>
                        <p className="text-gray-500 dark:text-gray-400">
                          {achieveA > achieveB ? fieldA.name : fieldB.name} أقرب للهدف بنسبة{' '}
                          {Math.abs(achieveA - achieveB).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  ) : null;
                })()}

                {/* EC Salinity */}
                {(fieldA.ec > 2.0 || fieldB.ec > 2.0) && (
                  <div className="flex items-start gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/10 rounded-lg">
                    <Thermometer className="w-5 h-5 text-yellow-600 shrink-0 mt-0.5" />
                    <div className="text-sm">
                      <p className="font-medium text-gray-900 dark:text-gray-100">تحذير ملوحة</p>
                      <p className="text-gray-500 dark:text-gray-400">
                        {fieldA.ec > 2.0 && fieldB.ec > 2.0
                          ? 'كلا الحقلين يعاني من ارتفاع الملوحة'
                          : `${fieldA.ec > 2.0 ? fieldA.name : fieldB.name} يعاني من ارتفاع EC (${Math.max(fieldA.ec, fieldB.ec)} dS/m)`}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
