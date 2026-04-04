'use client';

/**
 * Field Zone Management Page — VRI (Variable Rate Irrigation)
 * تقسيم الحقول — إدارة مناطق الحقل للري المتغير والزراعة الدقيقة
 *
 * Valley Irrigation-inspired zone management for precision agriculture.
 * Supports manual, NDVI-based, soil-based, and AI-auto zone strategies.
 */

import { useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import DataTable from '@/components/ui/DataTable';
import {
  Grid3X3,
  Leaf,
  BarChart3,
  Droplets,
  ChevronDown,
  ChevronUp,
  Download,
  Sprout,
  Wheat,
  MapPin,
  Layers,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ZoneProductivity = 'high' | 'medium' | 'low';
type ZoneStrategy = 'manual' | 'ndvi' | 'soil' | 'auto-ai';

interface ZoneCoordinate {
  lat: number;
  lng: number;
}

interface HistoricalNDVI {
  month: string;
  value: number;
}

interface FieldZone {
  id: string;
  name: string;
  nameAr: string;
  type: ZoneProductivity;
  typeAr: string;
  areaHa: number;
  ndvi: number;
  irrigationRate: number; // mm/hr
  fertilizerRate: number; // kg/ha
  seedRate: number; // kg/ha
  status: 'active' | 'scheduled' | 'completed';
  statusAr: string;
  boundary: ZoneCoordinate[];
  historicalNdvi: HistoricalNDVI[];
  recommendedActions: string[];
}

interface FieldOption {
  id: string;
  name: string;
  nameAr: string;
  crop: string;
  cropAr: string;
  areaHa: number;
}

// ---------------------------------------------------------------------------
// Mock Data
// ---------------------------------------------------------------------------

const FIELDS: FieldOption[] = [
  { id: 'FIELD-001', name: 'North Wheat Block', nameAr: 'حقل القمح الشمالي', crop: 'Wheat', cropAr: 'قمح', areaHa: 25.4 },
  { id: 'FIELD-002', name: 'South Barley Strip', nameAr: 'شريط الشعير الجنوبي', crop: 'Barley', cropAr: 'شعير', areaHa: 18.0 },
  { id: 'FIELD-003', name: 'East Date Palm Grove', nameAr: 'بستان النخيل الشرقي', crop: 'Date Palm', cropAr: 'نخيل', areaHa: 12.5 },
];

const MOCK_ZONES: Record<string, FieldZone[]> = {
  'FIELD-001': [
    {
      id: 'Z-001-A',
      name: 'Zone A — North-West',
      nameAr: 'المنطقة أ — الشمال الغربي',
      type: 'high',
      typeAr: 'إنتاجية عالية',
      areaHa: 6.2,
      ndvi: 0.78,
      irrigationRate: 12,
      fertilizerRate: 180,
      seedRate: 150,
      status: 'active',
      statusAr: 'نشط',
      boundary: [
        { lat: 24.7100, lng: 46.7000 },
        { lat: 24.7100, lng: 46.7200 },
        { lat: 24.7200, lng: 46.7200 },
        { lat: 24.7200, lng: 46.7000 },
      ],
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.45 },
        { month: 'نوفمبر', value: 0.58 },
        { month: 'ديسمبر', value: 0.68 },
        { month: 'يناير', value: 0.75 },
        { month: 'فبراير', value: 0.78 },
      ],
      recommendedActions: [
        'الاستمرار في جدول الري الحالي — كفاءة ممتازة',
        'تطبيق الجرعة الثانية من النيتروجين خلال أسبوع',
      ],
    },
    {
      id: 'Z-001-B',
      name: 'Zone B — North-East',
      nameAr: 'المنطقة ب — الشمال الشرقي',
      type: 'medium',
      typeAr: 'إنتاجية متوسطة',
      areaHa: 5.8,
      ndvi: 0.55,
      irrigationRate: 15,
      fertilizerRate: 200,
      seedRate: 160,
      status: 'active',
      statusAr: 'نشط',
      boundary: [
        { lat: 24.7100, lng: 46.7200 },
        { lat: 24.7100, lng: 46.7400 },
        { lat: 24.7200, lng: 46.7400 },
        { lat: 24.7200, lng: 46.7200 },
      ],
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.38 },
        { month: 'نوفمبر', value: 0.42 },
        { month: 'ديسمبر', value: 0.48 },
        { month: 'يناير', value: 0.52 },
        { month: 'فبراير', value: 0.55 },
      ],
      recommendedActions: [
        'زيادة معدل الري بنسبة 15% لتحسين رطوبة التربة',
        'فحص التربة للكشف عن نقص المغذيات',
        'مراقبة مؤشر NDVI أسبوعياً',
      ],
    },
    {
      id: 'Z-001-C',
      name: 'Zone C — Central',
      nameAr: 'المنطقة ج — الوسطى',
      type: 'high',
      typeAr: 'إنتاجية عالية',
      areaHa: 5.0,
      ndvi: 0.72,
      irrigationRate: 12,
      fertilizerRate: 175,
      seedRate: 150,
      status: 'completed',
      statusAr: 'مكتمل',
      boundary: [
        { lat: 24.7200, lng: 46.7100 },
        { lat: 24.7200, lng: 46.7300 },
        { lat: 24.7300, lng: 46.7300 },
        { lat: 24.7300, lng: 46.7100 },
      ],
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.50 },
        { month: 'نوفمبر', value: 0.60 },
        { month: 'ديسمبر', value: 0.65 },
        { month: 'يناير', value: 0.70 },
        { month: 'فبراير', value: 0.72 },
      ],
      recommendedActions: [
        'اكتملت دورة الري — الحالة ممتازة',
        'تجهيز الجدول الزمني للحصاد',
      ],
    },
    {
      id: 'Z-001-D',
      name: 'Zone D — South-West',
      nameAr: 'المنطقة د — الجنوب الغربي',
      type: 'low',
      typeAr: 'إنتاجية منخفضة',
      areaHa: 4.8,
      ndvi: 0.32,
      irrigationRate: 20,
      fertilizerRate: 240,
      seedRate: 180,
      status: 'active',
      statusAr: 'نشط',
      boundary: [
        { lat: 24.7300, lng: 46.7000 },
        { lat: 24.7300, lng: 46.7200 },
        { lat: 24.7400, lng: 46.7200 },
        { lat: 24.7400, lng: 46.7000 },
      ],
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.22 },
        { month: 'نوفمبر', value: 0.25 },
        { month: 'ديسمبر', value: 0.28 },
        { month: 'يناير', value: 0.30 },
        { month: 'فبراير', value: 0.32 },
      ],
      recommendedActions: [
        'تحليل التربة عاجل — اشتباه بملوحة مرتفعة',
        'زيادة الري بنسبة 40% مع رصد الصرف',
        'تطبيق سماد عضوي لتحسين بنية التربة',
        'النظر في تغيير الصنف للموسم القادم',
      ],
    },
    {
      id: 'Z-001-E',
      name: 'Zone E — South-East',
      nameAr: 'المنطقة هـ — الجنوب الشرقي',
      type: 'medium',
      typeAr: 'إنتاجية متوسطة',
      areaHa: 3.6,
      ndvi: 0.48,
      irrigationRate: 16,
      fertilizerRate: 210,
      seedRate: 165,
      status: 'scheduled',
      statusAr: 'مجدول',
      boundary: [
        { lat: 24.7300, lng: 46.7200 },
        { lat: 24.7300, lng: 46.7400 },
        { lat: 24.7400, lng: 46.7400 },
        { lat: 24.7400, lng: 46.7200 },
      ],
      historicalNdvi: [
        { month: 'أكتوبر', value: 0.30 },
        { month: 'نوفمبر', value: 0.35 },
        { month: 'ديسمبر', value: 0.40 },
        { month: 'يناير', value: 0.45 },
        { month: 'فبراير', value: 0.48 },
      ],
      recommendedActions: [
        'بدء دورة الري المجدولة خلال 48 ساعة',
        'تطبيق سماد الفوسفور قبل الري',
        'فحص مشاكل الصرف في الزاوية الجنوبية',
      ],
    },
  ],
};

const ZONE_STRATEGIES: { value: ZoneStrategy; labelAr: string; labelEn: string }[] = [
  { value: 'manual', labelAr: 'يدوي', labelEn: 'Manual' },
  { value: 'ndvi', labelAr: 'بناءً على NDVI', labelEn: 'NDVI-based' },
  { value: 'soil', labelAr: 'بناءً على التربة', labelEn: 'Soil-based' },
  { value: 'auto-ai', labelAr: 'ذكاء اصطناعي تلقائي', labelEn: 'Auto AI' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const ZONE_COLOR_MAP: Record<ZoneProductivity, { bg: string; text: string; dot: string }> = {
  high: { bg: 'bg-green-50 dark:bg-green-900/20', text: 'text-green-700 dark:text-green-400', dot: 'bg-green-500' },
  medium: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', text: 'text-yellow-700 dark:text-yellow-400', dot: 'bg-yellow-500' },
  low: { bg: 'bg-red-50 dark:bg-red-900/20', text: 'text-red-700 dark:text-red-400', dot: 'bg-red-500' },
};

const STATUS_STYLES: Record<string, string> = {
  active: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  scheduled: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
  completed: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
};

function computeHeterogeneity(zones: FieldZone[]): number {
  if (zones.length < 2) return 0;
  const values = zones.map((z) => z.ndvi);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((sum, v) => sum + (v - mean) ** 2, 0) / values.length;
  const cv = (Math.sqrt(variance) / mean) * 100;
  return Math.round(cv);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function FieldZonesPage() {
  const [selectedFieldId, setSelectedFieldId] = useState<string>(FIELDS[0].id);
  const [strategy, setStrategy] = useState<ZoneStrategy>('ndvi');
  const [expandedZoneId, setExpandedZoneId] = useState<string | null>(null);

  const _selectedField = useMemo(
    () => FIELDS.find((f) => f.id === selectedFieldId) ?? FIELDS[0],
    [selectedFieldId],
  );

  const zones = useMemo(() => MOCK_ZONES[selectedFieldId] ?? [], [selectedFieldId]);

  const avgNdvi = useMemo(() => {
    if (zones.length === 0) return 0;
    return zones.reduce((sum, z) => sum + z.ndvi, 0) / zones.length;
  }, [zones]);

  const heterogeneity = useMemo(() => computeHeterogeneity(zones), [zones]);

  const vraRecommended = useMemo(
    () => (heterogeneity > 20 ? zones.length : 0),
    [heterogeneity, zones.length],
  );

  const totalArea = useMemo(() => zones.reduce((s, z) => s + z.areaHa, 0), [zones]);

  const estimatedSavings = useMemo(() => {
    if (heterogeneity <= 10) return 0;
    return Math.round(totalArea * heterogeneity * 2.5);
  }, [heterogeneity, totalArea]);

  // Table columns
  const columns = useMemo(
    () => [
      {
        key: 'id',
        header: 'رمز المنطقة',
        render: (z: FieldZone) => (
          <span className="font-mono text-xs text-gray-600 dark:text-gray-300">{z.id}</span>
        ),
      },
      {
        key: 'type',
        header: 'النوع',
        render: (z: FieldZone) => {
          const color = ZONE_COLOR_MAP[z.type];
          return (
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${color.bg} ${color.text}`}>
              <span className={`w-2 h-2 rounded-full ${color.dot}`} />
              {z.typeAr}
            </span>
          );
        },
      },
      {
        key: 'areaHa',
        header: 'المساحة (هـ)',
        render: (z: FieldZone) => (
          <span className="text-gray-900 dark:text-gray-100">{z.areaHa.toFixed(1)}</span>
        ),
      },
      {
        key: 'ndvi',
        header: 'NDVI',
        render: (z: FieldZone) => {
          const color = z.ndvi >= 0.6 ? 'text-green-600' : z.ndvi >= 0.4 ? 'text-yellow-600' : 'text-red-600';
          return <span className={`font-semibold ${color}`}>{z.ndvi.toFixed(2)}</span>;
        },
      },
      {
        key: 'irrigationRate',
        header: 'معدل الري (مم/س)',
        render: (z: FieldZone) => (
          <div className="flex items-center gap-1.5">
            <Droplets className="w-3.5 h-3.5 text-blue-500" />
            <span className="text-gray-900 dark:text-gray-100">{z.irrigationRate}</span>
          </div>
        ),
      },
      {
        key: 'fertilizerRate',
        header: 'معدل السماد (كجم/هـ)',
        render: (z: FieldZone) => (
          <div className="flex items-center gap-1.5">
            <Sprout className="w-3.5 h-3.5 text-emerald-500" />
            <span className="text-gray-900 dark:text-gray-100">{z.fertilizerRate}</span>
          </div>
        ),
      },
      {
        key: 'seedRate',
        header: 'معدل البذور (كجم/هـ)',
        render: (z: FieldZone) => (
          <div className="flex items-center gap-1.5">
            <Wheat className="w-3.5 h-3.5 text-amber-600" />
            <span className="text-gray-900 dark:text-gray-100">{z.seedRate}</span>
          </div>
        ),
      },
      {
        key: 'status',
        header: 'الحالة',
        render: (z: FieldZone) => (
          <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_STYLES[z.status]}`}>
            {z.statusAr}
          </span>
        ),
      },
      {
        key: 'expand',
        header: '',
        render: (z: FieldZone) => (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setExpandedZoneId((prev) => (prev === z.id ? null : z.id));
            }}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label={expandedZoneId === z.id ? 'طي التفاصيل' : 'عرض التفاصيل'}
          >
            {expandedZoneId === z.id ? (
              <ChevronUp className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            )}
          </button>
        ),
        className: 'w-10',
      },
    ],
    [expandedZoneId],
  );

  const handleExport = (format: 'geojson' | 'shapefile') => {
    alert(`تصدير ${format === 'geojson' ? 'GeoJSON' : 'Shapefile'} — ${zones.length} مناطق`);
  };

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header
        title="تقسيم الحقول — Field Zone Management"
        subtitle="إدارة مناطق الري المتغير والزراعة الدقيقة — Valley VRI"
      />

      <main className="p-6 space-y-6 max-w-7xl mx-auto">
        {/* ---- Stats Row ---- */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="إجمالي المناطق"
            value={zones.length}
            icon={Grid3X3}
            iconColor="text-indigo-600"
          />
          <StatCard
            title="متوسط NDVI"
            value={avgNdvi.toFixed(2)}
            icon={Leaf}
            iconColor="text-green-600"
            trend={avgNdvi >= 0.6 ? { value: 5, isPositive: true } : { value: 8, isPositive: false }}
          />
          <StatCard
            title="تباين الحقل (CV%)"
            value={`${heterogeneity}%`}
            icon={BarChart3}
            iconColor="text-orange-600"
          />
          <StatCard
            title="حقول موصى بـ VRA"
            value={vraRecommended}
            icon={Layers}
            iconColor="text-purple-600"
            suffix={vraRecommended > 0 ? 'منطقة' : ''}
          />
        </div>

        {/* ---- Selectors Row ---- */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Field Selector */}
            <div className="flex-1">
              <label htmlFor="field-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                <MapPin className="w-4 h-4 inline-block ml-1" />
                الحقل
              </label>
              <select
                id="field-select"
                value={selectedFieldId}
                onChange={(e) => {
                  setSelectedFieldId(e.target.value);
                  setExpandedZoneId(null);
                }}
                className="w-full rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500"
              >
                {FIELDS.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.nameAr} — {f.cropAr} ({f.areaHa} هـ)
                  </option>
                ))}
              </select>
            </div>

            {/* Zone Strategy Selector */}
            <div className="flex-1">
              <label htmlFor="strategy-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
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
                        ? 'bg-sahool-600 text-white shadow-sm'
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

        {/* ---- Zone Table ---- */}
        <div>
          <DataTable
            columns={columns}
            data={zones}
            keyExtractor={(z) => z.id}
            onRowClick={(z) => setExpandedZoneId((prev) => (prev === z.id ? null : z.id))}
            emptyMessage="لا توجد مناطق لهذا الحقل — اختر حقلاً آخر أو أنشئ تقسيماً جديداً"
          />

          {/* Expanded Zone Detail */}
          {expandedZoneId && (() => {
            const zone = zones.find((z) => z.id === expandedZoneId);
            if (!zone) return null;
            const color = ZONE_COLOR_MAP[zone.type];

            return (
              <div className={`mt-1 rounded-b-xl border border-t-0 border-gray-100 dark:border-gray-700 ${color.bg} p-5 space-y-4 transition-all`}>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Boundary Coordinates */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      إحداثيات الحدود
                    </h4>
                    <ul className="space-y-1">
                      {zone.boundary.map((coord, i) => (
                        <li key={i} className="text-xs font-mono text-gray-600 dark:text-gray-400">
                          [{coord.lat.toFixed(4)}, {coord.lng.toFixed(4)}]
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Historical NDVI Trend */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      اتجاه NDVI التاريخي
                    </h4>
                    <div className="flex items-end gap-2 h-20">
                      {zone.historicalNdvi.map((point, i) => {
                        const heightPct = Math.max(10, point.value * 100);
                        const barColor =
                          point.value >= 0.6 ? 'bg-green-500' : point.value >= 0.4 ? 'bg-yellow-500' : 'bg-red-500';
                        return (
                          <div key={i} className="flex flex-col items-center flex-1 gap-1">
                            <span className="text-[10px] text-gray-500 dark:text-gray-400">
                              {point.value.toFixed(2)}
                            </span>
                            <div
                              className={`w-full rounded-t ${barColor} transition-all`}
                              style={{ height: `${heightPct}%` }}
                            />
                            <span className="text-[9px] text-gray-400 dark:text-gray-500 truncate w-full text-center">
                              {point.month}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Recommended Actions */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      الإجراءات الموصى بها
                    </h4>
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
            );
          })()}
        </div>

        {/* ---- Summary Footer ---- */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex flex-wrap gap-6 text-sm">
              <div>
                <span className="text-gray-500 dark:text-gray-400">إجمالي المساحة: </span>
                <span className="font-semibold text-gray-900 dark:text-gray-100">{totalArea.toFixed(1)} هـ</span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">التوفير المقدر (VRI): </span>
                <span className="font-semibold text-green-600">
                  {estimatedSavings > 0 ? `${estimatedSavings} ريال/موسم` : 'غير متاح'}
                </span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">حالة VRI: </span>
                <span
                  className={`font-semibold ${
                    heterogeneity > 20
                      ? 'text-green-600'
                      : heterogeneity > 10
                        ? 'text-yellow-600'
                        : 'text-gray-500 dark:text-gray-400'
                  }`}
                >
                  {heterogeneity > 20 ? 'موصى بشدة' : heterogeneity > 10 ? 'اختياري' : 'غير ضروري'}
                </span>
              </div>
            </div>

            {/* Export Buttons */}
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => handleExport('geojson')}
                className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-sahool-600 text-white hover:bg-sahool-700 transition-colors shadow-sm"
              >
                <Download className="w-4 h-4" />
                GeoJSON
              </button>
              <button
                type="button"
                onClick={() => handleExport('shapefile')}
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
