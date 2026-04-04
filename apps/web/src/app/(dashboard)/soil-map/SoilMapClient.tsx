'use client';

/**
 * Soil Map Client Component
 * مكون خريطة التربة
 */

import React, { useState } from 'react';
import {
  Map,
  Layers,
  FlaskConical,
  Droplets,
  Mountain,
  Thermometer,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types & Data
// ---------------------------------------------------------------------------

interface AgroZone {
  id: string;
  nameAr: string;
  nameEn: string;
  regionAr: string;
  climateAr: string;
  soilTypeAr: string;
  altitude: string;
  rainfall: string;
  temperature: string;
  cropsAr: string[];
  areaKm2: number;
  fieldCount: number;
  color: string;
  bgColor: string;
}

const AGRO_ZONES: AgroZone[] = [
  {
    id: 'coastal', nameAr: 'السهل الساحلي (تهامة)', nameEn: 'Coastal Plain',
    regionAr: 'تهامة', climateAr: 'حار رطب', soilTypeAr: 'رملية - طمية',
    altitude: '0 - 200 م', rainfall: '50 - 200 مم', temperature: '25 - 40 درجة مئوية',
    cropsAr: ['نخيل', 'ذرة رفيعة', 'سمسم', 'قطن', 'موز'],
    areaKm2: 25000, fieldCount: 1200, color: '#f59e0b', bgColor: 'bg-amber-50',
  },
  {
    id: 'western_highlands', nameAr: 'المرتفعات الغربية', nameEn: 'Western Highlands',
    regionAr: 'إب - تعز', climateAr: 'معتدل رطب', soilTypeAr: 'طينية بركانية خصبة',
    altitude: '1000 - 3000 م', rainfall: '400 - 1000 مم', temperature: '15 - 25 درجة مئوية',
    cropsAr: ['بن يمني', 'قات', 'قمح', 'شعير', 'خضروات'],
    areaKm2: 35000, fieldCount: 3500, color: '#22c55e', bgColor: 'bg-green-50',
  },
  {
    id: 'eastern_plateau', nameAr: 'الهضبة الشرقية', nameEn: 'Eastern Plateau',
    regionAr: 'مأرب - حضرموت', climateAr: 'جاف حار', soilTypeAr: 'رملية - صحراوية',
    altitude: '500 - 1500 م', rainfall: '50 - 100 مم', temperature: '20 - 38 درجة مئوية',
    cropsAr: ['نخيل التمر', 'ذرة', 'بطيخ'],
    areaKm2: 120000, fieldCount: 800, color: '#ef4444', bgColor: 'bg-red-50',
  },
  {
    id: 'central_highlands', nameAr: 'المرتفعات الوسطى', nameEn: 'Central Highlands',
    regionAr: 'صنعاء - ذمار', climateAr: 'معتدل جاف', soilTypeAr: 'طينية جيرية',
    altitude: '1800 - 2800 م', rainfall: '200 - 500 مم', temperature: '12 - 22 درجة مئوية',
    cropsAr: ['قمح', 'شعير', 'عنب', 'رمان', 'لوز'],
    areaKm2: 28000, fieldCount: 2800, color: '#3b82f6', bgColor: 'bg-blue-50',
  },
  {
    id: 'wadis', nameAr: 'الأودية والمجاري المائية', nameEn: 'Wadis',
    regionAr: 'وادي حضرموت - وادي بنا', climateAr: 'حار شبه جاف', soilTypeAr: 'طمية غنية - رسوبية',
    altitude: '200 - 800 م', rainfall: '100 - 300 مم', temperature: '22 - 35 درجة مئوية',
    cropsAr: ['نخيل', 'حمضيات', 'خضروات', 'بصل', 'ثوم'],
    areaKm2: 15000, fieldCount: 1500, color: '#8b5cf6', bgColor: 'bg-purple-50',
  },
];

const SOIL_TESTS = [
  { test: 'الأس الهيدروجيني (pH)', importance: 'يؤثر على امتصاص العناصر', frequency: 'سنوياً' },
  { test: 'الملوحة (EC)', importance: 'تحديد ملاءمة المحاصيل', frequency: 'موسمياً' },
  { test: 'المادة العضوية', importance: 'خصوبة التربة والاحتفاظ بالماء', frequency: 'سنوياً' },
  { test: 'النيتروجين (N)', importance: 'عنصر أساسي للنمو الخضري', frequency: 'قبل كل موسم' },
  { test: 'الفوسفور (P)', importance: 'نمو الجذور والإزهار', frequency: 'سنوياً' },
  { test: 'البوتاسيوم (K)', importance: 'جودة الثمار ومقاومة الأمراض', frequency: 'سنوياً' },
];

const STATS = [
  { label: 'إجمالي المناطق', value: '5', icon: Map, color: 'blue' },
  { label: 'إجمالي الحقول', value: '9,800', icon: Layers, color: 'green' },
  { label: 'تحليلات التربة', value: '1,240', icon: FlaskConical, color: 'purple' },
  { label: 'المساحة الكلية', value: '223,000 كم\u00B2', icon: Mountain, color: 'amber' },
];

const STAT_COLORS: Record<string, { bg: string; icon: string }> = {
  blue: { bg: 'bg-blue-100', icon: 'text-blue-600' },
  green: { bg: 'bg-green-100', icon: 'text-green-600' },
  purple: { bg: 'bg-purple-100', icon: 'text-purple-600' },
  amber: { bg: 'bg-amber-100', icon: 'text-amber-600' },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SoilMapClient() {
  const [expandedZone, setExpandedZone] = useState<string | null>(null);

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">خريطة التربة اليمنية</h1>
        <p className="text-sm text-gray-500 mt-1">
          المناطق الزراعية البيئية وأنواع التربة والمحاصيل المناسبة
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {STATS.map((s) => {
          const Icon = s.icon;
          const colors = STAT_COLORS[s.color] ?? STAT_COLORS.blue;
          return (
            <div key={s.label} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 ${colors.bg} rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${colors.icon}`} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{s.value}</p>
                  <p className="text-sm text-gray-500">{s.label}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Agro-Ecological Zones */}
      <div>
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5 text-green-600" />
          المناطق الزراعية البيئية
        </h2>
        <div className="space-y-3">
          {AGRO_ZONES.map((zone) => {
            const isExpanded = expandedZone === zone.id;
            return (
              <div key={zone.id} className={`bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden`}>
                <button
                  onClick={() => setExpandedZone(isExpanded ? null : zone.id)}
                  className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div
                      className="w-4 h-4 rounded-full flex-shrink-0"
                      style={{ backgroundColor: zone.color }}
                    />
                    <div className="text-right">
                      <p className="font-bold text-gray-900">{zone.nameAr}</p>
                      <p className="text-sm text-gray-500">{zone.regionAr} - {zone.climateAr}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-500">{zone.fieldCount} حقل</span>
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                  </div>
                </button>

                {isExpanded && (
                  <div className={`p-6 border-t ${zone.bgColor}`}>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="flex items-center gap-2 text-sm">
                        <Mountain className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-600">الارتفاع:</span>
                        <span className="font-medium">{zone.altitude}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Droplets className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-600">الأمطار:</span>
                        <span className="font-medium">{zone.rainfall}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Thermometer className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-600">الحرارة:</span>
                        <span className="font-medium">{zone.temperature}</span>
                      </div>
                    </div>
                    <div className="mb-3">
                      <p className="text-sm text-gray-600 mb-1">نوع التربة:</p>
                      <p className="font-medium text-gray-900">{zone.soilTypeAr}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-2">المحاصيل المناسبة:</p>
                      <div className="flex flex-wrap gap-2">
                        {zone.cropsAr.map((crop) => (
                          <span key={crop} className="px-3 py-1 bg-white rounded-full text-sm font-medium text-gray-700 border">
                            {crop}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="mt-3 text-sm text-gray-500">
                      المساحة: {zone.areaKm2.toLocaleString('ar-SA')} كم\u00B2
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Soil Tests Reference */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <FlaskConical className="w-5 h-5 text-purple-600" />
          تحليلات التربة الأساسية
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-right p-3 font-medium text-gray-600">التحليل</th>
                <th className="text-right p-3 font-medium text-gray-600">الأهمية</th>
                <th className="text-right p-3 font-medium text-gray-600">التكرار</th>
              </tr>
            </thead>
            <tbody>
              {SOIL_TESTS.map((t) => (
                <tr key={t.test} className="border-t hover:bg-gray-50">
                  <td className="p-3 font-medium text-gray-900">{t.test}</td>
                  <td className="p-3 text-gray-600">{t.importance}</td>
                  <td className="p-3">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                      {t.frequency}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
