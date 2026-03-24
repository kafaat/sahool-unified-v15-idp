'use client';

import React, { useState, useMemo, useRef } from 'react';
import {
  Satellite,
  MapPin,
  Layers,
  TrendingUp,
  Download,
  AlertTriangle,
  Droplets,
} from 'lucide-react';
import { logger } from '@/lib/logger';
import { useSatelliteFields, useSatelliteStats } from '@/features/satellite';
import type { SatelliteField, IndexType } from '@/features/satellite';

const INDEX_CONFIG: Record<
  IndexType,
  {
    label: string;
    labelAr: string;
    unit: string;
    colorStops: Array<{ max: number; color: string; bgClass: string; label: string }>;
    description: string;
  }
> = {
  ndvi: {
    label: 'NDVI',
    labelAr: 'مؤشر الغطاء النباتي',
    unit: '',
    description: 'كثافة الغطاء النباتي',
    colorStops: [
      { max: 0.15, color: 'bg-red-500', bgClass: 'text-red-600', label: 'حرج' },
      { max: 0.3, color: 'bg-orange-500', bgClass: 'text-orange-600', label: 'ضعيف' },
      { max: 0.5, color: 'bg-yellow-500', bgClass: 'text-yellow-600', label: 'متوسط' },
      { max: 0.7, color: 'bg-green-400', bgClass: 'text-green-600', label: 'جيد' },
      { max: 1.0, color: 'bg-green-600', bgClass: 'text-green-700', label: 'ممتاز' },
    ],
  },
  ndwi: {
    label: 'NDWI',
    labelAr: 'مؤشر المياه',
    unit: '',
    description: 'محتوى الماء في الغطاء النباتي',
    colorStops: [
      { max: -0.1, color: 'bg-red-500', bgClass: 'text-red-600', label: 'جفاف شديد' },
      { max: 0.0, color: 'bg-orange-500', bgClass: 'text-orange-600', label: 'إجهاد مائي' },
      { max: 0.2, color: 'bg-yellow-500', bgClass: 'text-yellow-600', label: 'منخفض' },
      { max: 0.4, color: 'bg-blue-400', bgClass: 'text-blue-600', label: 'كافٍ' },
      { max: 1.0, color: 'bg-blue-600', bgClass: 'text-blue-700', label: 'ممتاز' },
    ],
  },
  evi: {
    label: 'EVI',
    labelAr: 'مؤشر الغطاء المحسن',
    unit: '',
    description: 'الغطاء النباتي مع تصحيح جوي',
    colorStops: [
      { max: 0.1, color: 'bg-red-500', bgClass: 'text-red-600', label: 'حرج' },
      { max: 0.25, color: 'bg-orange-500', bgClass: 'text-orange-600', label: 'ضعيف' },
      { max: 0.4, color: 'bg-yellow-500', bgClass: 'text-yellow-600', label: 'متوسط' },
      { max: 0.6, color: 'bg-green-400', bgClass: 'text-green-600', label: 'جيد' },
      { max: 1.0, color: 'bg-green-600', bgClass: 'text-green-700', label: 'ممتاز' },
    ],
  },
  savi: {
    label: 'SAVI',
    labelAr: 'مؤشر الغطاء المعدل للتربة',
    unit: '',
    description: 'الغطاء النباتي مع تصحيح التربة (مناسب للبيئة الجافة)',
    colorStops: [
      { max: 0.1, color: 'bg-red-500', bgClass: 'text-red-600', label: 'حرج' },
      { max: 0.25, color: 'bg-orange-500', bgClass: 'text-orange-600', label: 'ضعيف' },
      { max: 0.4, color: 'bg-yellow-500', bgClass: 'text-yellow-600', label: 'متوسط' },
      { max: 0.6, color: 'bg-green-400', bgClass: 'text-green-600', label: 'جيد' },
      { max: 1.0, color: 'bg-green-600', bgClass: 'text-green-700', label: 'ممتاز' },
    ],
  },
  ndre: {
    label: 'NDRE',
    labelAr: 'مؤشر الحافة الحمراء',
    unit: '',
    description: 'تركيز الكلوروفيل (مناسب للبن)',
    colorStops: [
      { max: 0.05, color: 'bg-red-500', bgClass: 'text-red-600', label: 'نقص شديد' },
      { max: 0.15, color: 'bg-orange-500', bgClass: 'text-orange-600', label: 'نقص' },
      { max: 0.3, color: 'bg-yellow-500', bgClass: 'text-yellow-600', label: 'متوسط' },
      { max: 0.5, color: 'bg-green-400', bgClass: 'text-green-600', label: 'جيد' },
      { max: 1.0, color: 'bg-green-600', bgClass: 'text-green-700', label: 'ممتاز' },
    ],
  },
  lai: {
    label: 'LAI',
    labelAr: 'مؤشر مساحة الأوراق',
    unit: 'm²/m²',
    description: 'نسبة مساحة الأوراق إلى مساحة الأرض',
    colorStops: [
      { max: 1.0, color: 'bg-red-500', bgClass: 'text-red-600', label: 'متناثر' },
      { max: 2.0, color: 'bg-orange-500', bgClass: 'text-orange-600', label: 'خفيف' },
      { max: 3.5, color: 'bg-yellow-500', bgClass: 'text-yellow-600', label: 'متوسط' },
      { max: 5.0, color: 'bg-green-400', bgClass: 'text-green-600', label: 'كثيف' },
      { max: 8.0, color: 'bg-green-600', bgClass: 'text-green-700', label: 'كثيف جداً' },
    ],
  },
};

const indexTypes = Object.entries(INDEX_CONFIG).map(([value, config]) => ({
  value: value as IndexType,
  label: config.label,
  labelAr: config.labelAr,
}));

export default function SatelliteClient() {
  const [selectedIndex, setSelectedIndex] = useState<IndexType>('ndvi');
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const warnedIndicesRef = useRef(new Set<string>());

  // Fetch data using React Query hooks
  const { data: fields = [], isLoading, error } = useSatelliteFields();
  const { data: stats } = useSatelliteStats();

  const getHealthColor = (status: SatelliteField['healthStatus']) => {
    const colors: Record<SatelliteField['healthStatus'], string> = {
      excellent: 'text-green-700 bg-green-100',
      good: 'text-green-600 bg-green-50',
      moderate: 'text-yellow-600 bg-yellow-100',
      poor: 'text-orange-600 bg-orange-100',
      critical: 'text-red-600 bg-red-100',
    };
    return colors[status];
  };

  const getHealthLabel = (status: SatelliteField['healthStatus']) => {
    const labels: Record<SatelliteField['healthStatus'], string> = {
      excellent: 'ممتاز',
      good: 'جيد',
      moderate: 'متوسط',
      poor: 'ضعيف',
      critical: 'حرج',
    };
    return labels[status];
  };

  // Get the value of the currently selected index for a field
  const getIndexValue = (field: SatelliteField): number => {
    if (selectedIndex === 'ndvi') return field.indices.ndvi;
    const value = field.indices[selectedIndex];
    if (value == null) {
      const key = `${selectedIndex}:${field.id}`;
      if (process.env.NODE_ENV !== 'production' && !warnedIndicesRef.current.has(key)) {
        warnedIndicesRef.current.add(key);
        logger.warn(
          `[SatelliteClient] Index "${selectedIndex}" not available for field ${field.id}, falling back to NDVI`
        );
      }
      return field.indices.ndvi;
    }
    return value;
  };

  // Get color/label for a value based on the active index config
  const getIndexColor = (value: number): { bgClass: string; barColor: string; label: string } => {
    const config = INDEX_CONFIG[selectedIndex];
    for (const stop of config.colorStops) {
      if (value <= stop.max) {
        return { bgClass: stop.bgClass, barColor: stop.color, label: stop.label };
      }
    }
    const last = config.colorStops[config.colorStops.length - 1]!;
    return { bgClass: last.bgClass, barColor: last.color, label: last.label };
  };

  // Normalize a value to 0-100% for the progress bar based on index range
  const getBarWidth = (value: number): number => {
    if (selectedIndex === 'lai') return Math.min((value / 8) * 100, 100);
    return Math.max(Math.min(((value + 1) / 2) * 100, 100), 0); // normalized [-1, 1] → [0, 100]
  };

  const activeConfig = INDEX_CONFIG[selectedIndex];

  const avgIndex = useMemo(() => {
    if (fields.length === 0) return '0.00';
    const values = fields.map((f) => getIndexValue(f));
    return (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fields, selectedIndex]);

  const totalArea = useMemo(() => {
    return fields.reduce((acc, f) => acc + f.area, 0).toFixed(1);
  }, [fields]);

  // Detect water stress alerts from NDWI
  const waterStressFields = useMemo(() => {
    return fields.filter((f) => (f.indices.ndwi ?? 0) < 0);
  }, [fields]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات الأقمار الصناعية</p>
          <p className="text-gray-500 text-sm">Failed to load satellite data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تحليل الأقمار الصناعية</h1>
          <p className="text-gray-500 mt-1">Satellite Imagery & Vegetation Analysis</p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedIndex}
            onChange={(e) => setSelectedIndex(e.target.value as IndexType)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          >
            {indexTypes.map((idx) => (
              <option key={idx.value} value={idx.value}>
                {idx.labelAr} ({idx.label})
              </option>
            ))}
          </select>
          <button className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors">
            <Download className="w-4 h-4" />
            <span>تصدير</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Satellite className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">آخر التقاط</div>
              <div className="text-lg font-bold text-gray-900">
                {stats?.lastCapture ?? '2026-01-24'}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متوسط {activeConfig.label}</div>
              <div className="text-lg font-bold text-green-600">
                {selectedIndex === 'ndvi' ? (stats?.averageNdvi?.toFixed(2) ?? avgIndex) : avgIndex}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <MapPin className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">الحقول المراقبة</div>
              <div className="text-lg font-bold text-purple-600">
                {stats?.totalFields ?? fields.length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
              <Layers className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">المساحة الكلية</div>
              <div className="text-lg font-bold text-amber-600">
                {stats?.totalArea?.toFixed(1) ?? totalArea} هـ
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Placeholder */}
        <div className="lg:col-span-2 bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">خريطة الأقمار الصناعية</h2>
          </div>
          <div className="aspect-video bg-gradient-to-br from-green-200 via-green-300 to-green-400 flex items-center justify-center">
            <div className="text-center">
              <Satellite className="w-16 h-16 text-green-700 mx-auto mb-4" />
              <p className="text-green-800 font-medium">خريطة تفاعلية للأقمار الصناعية</p>
              <p className="text-green-700 text-sm">Sentinel-2 / Landsat-8</p>
            </div>
          </div>
          <div className="p-4 flex justify-between items-center text-sm">
            <span className="text-gray-500">
              المصدر: Sentinel-2 L2A | {activeConfig.description}
            </span>
            <div className="flex gap-3 flex-wrap">
              {activeConfig.colorStops.map((stop) => (
                <div key={stop.max} className="flex items-center gap-1.5">
                  <div className={`w-3 h-3 rounded-full ${stop.color}`} />
                  <span>{stop.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Fields List */}
        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">الحقول</h2>
          </div>
          <div className="divide-y max-h-[500px] overflow-y-auto">
            {fields.length === 0 ? (
              <div className="p-4 text-center text-gray-500">لا توجد حقول مراقبة</div>
            ) : (
              fields.map((field) => (
                <div
                  key={field.id}
                  className={`p-4 cursor-pointer transition-colors ${
                    selectedField === field.id ? 'bg-sahool-green-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedField(field.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-medium text-gray-900">{field.fieldNameAr}</h3>
                      <p className="text-sm text-gray-500">{field.fieldName}</p>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getHealthColor(field.healthStatus)}`}
                    >
                      {getHealthLabel(field.healthStatus)}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500">{activeConfig.label}:</span>
                      <span
                        className={`font-medium mr-1 ${getIndexColor(getIndexValue(field)).bgClass}`}
                      >
                        {getIndexValue(field).toFixed(2)}
                      </span>
                      {selectedIndex === 'ndvi' && (
                        <span
                          className={
                            field.indices.ndviChange >= 0 ? 'text-green-600' : 'text-red-600'
                          }
                        >
                          ({field.indices.ndviChange >= 0 ? '+' : ''}
                          {field.indices.ndviChange.toFixed(2)})
                        </span>
                      )}
                    </div>
                    <div className="text-gray-500">{field.area} هكتار</div>
                  </div>

                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getIndexColor(getIndexValue(field)).barColor}`}
                        style={{ width: `${getBarWidth(getIndexValue(field))}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Water Stress Alerts (NDWI-based) */}
      {waterStressFields.length > 0 && (
        <div className="bg-white rounded-lg border border-orange-200 overflow-hidden">
          <div className="p-4 border-b bg-orange-50 flex items-center gap-2">
            <Droplets className="w-5 h-5 text-orange-600" />
            <h2 className="font-semibold text-orange-800">تنبيهات الإجهاد المائي (NDWI)</h2>
            <span className="px-2 py-0.5 bg-orange-200 text-orange-800 text-xs font-medium rounded-full">
              {waterStressFields.length}
            </span>
          </div>
          <div className="divide-y divide-orange-100">
            {waterStressFields.map((field) => (
              <div
                key={field.id}
                className="p-3 flex items-center justify-between hover:bg-orange-50/50 cursor-pointer"
                onClick={() => setSelectedField(field.id)}
              >
                <div>
                  <h3 className="font-medium text-gray-900 text-sm">{field.fieldNameAr}</h3>
                  <p className="text-xs text-gray-500">
                    {field.fieldName} — {field.area} هكتار
                  </p>
                </div>
                <div className="text-left">
                  <span className="text-sm font-bold text-orange-600">
                    NDWI: {(field.indices.ndwi ?? 0).toFixed(2)}
                  </span>
                  <p className="text-xs text-orange-500">إجهاد مائي — يُنصح بزيادة الري</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
