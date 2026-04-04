'use client';

/**
 * Terrain Analysis Client Component
 * مكون تحليل التضاريس
 */

import React, { useState } from 'react';
import {
  Mountain,
  CheckCircle,
  Clock,
  Upload,
  MapPin,
  TrendingUp,
  Droplets,
  ArrowUpDown,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types & Data
// ---------------------------------------------------------------------------

const STATS = [
  { label: 'تحليلات مكتملة', value: 256, icon: CheckCircle, color: 'green' },
  { label: 'قيد الانتظار', value: 14, icon: Clock, color: 'yellow' },
  { label: 'رفع DEM', value: 89, icon: Upload, color: 'blue' },
  { label: 'إجمالي المساحة', value: '4,320 هـ', icon: MapPin, color: 'purple' },
];

const TABS = [
  { id: 'analyses', label: 'التحليلات', icon: Mountain },
  { id: 'slope', label: 'الانحدار', icon: TrendingUp },
  { id: 'leveling', label: 'التسوية', icon: ArrowUpDown },
  { id: 'hydrology', label: 'الهيدرولوجيا', icon: Droplets },
] as const;

type TabId = (typeof TABS)[number]['id'];

const ANALYSES = [
  { id: 'a1', field: 'حقل القمح الشمالي', date: '2026-04-02', type: 'DEM + انحدار', resolution: '1 م', area: 5.2, status: 'completed', avgSlope: 2.3 },
  { id: 'a2', field: 'بستان النخيل', date: '2026-04-01', type: 'تسوية', resolution: '0.5 م', area: 8.5, status: 'completed', avgSlope: 1.8 },
  { id: 'a3', field: 'حقل الطماطم', date: '2026-03-31', type: 'هيدرولوجيا', resolution: '2 م', area: 3.0, status: 'processing', avgSlope: 4.1 },
  { id: 'a4', field: 'حقل الذرة الرفيعة', date: '2026-03-30', type: 'DEM كامل', resolution: '1 م', area: 6.7, status: 'completed', avgSlope: 3.5 },
  { id: 'a5', field: 'حقل البصل', date: '2026-03-29', type: 'انحدار + اتجاه', resolution: '1 م', area: 2.1, status: 'pending', avgSlope: 0 },
];

const SLOPE_DATA = [
  { range: '0-2%', label: 'مستوٍ', area: 1250, pct: 29, color: 'bg-green-500', recommendation: 'مناسب لجميع المحاصيل - ري بالغمر ممكن' },
  { range: '2-5%', label: 'انحدار خفيف', area: 1680, pct: 39, color: 'bg-yellow-500', recommendation: 'ري بالتنقيط مفضل - زراعة خطوط كنتورية' },
  { range: '5-10%', label: 'انحدار متوسط', area: 890, pct: 21, color: 'bg-orange-500', recommendation: 'مصاطب ضرورية - محاصيل شجرية مفضلة' },
  { range: '10%+', label: 'انحدار حاد', area: 500, pct: 11, color: 'bg-red-500', recommendation: 'حفظ تربة ضروري - أشجار فقط' },
];

const LEVELING_PLANS = [
  { id: 'l1', field: 'حقل القمح', cutVol: 1200, fillVol: 1180, cost: 4500, savings: 12000, status: 'approved' },
  { id: 'l2', field: 'حقل الطماطم', cutVol: 650, fillVol: 630, cost: 2800, savings: 7500, status: 'pending' },
  { id: 'l3', field: 'حقل البصل', cutVol: 300, fillVol: 290, cost: 1500, savings: 4200, status: 'draft' },
];

const STATUS_STYLES: Record<string, string> = {
  completed: 'bg-green-100 text-green-700',
  processing: 'bg-blue-100 text-blue-700',
  pending: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-green-100 text-green-700',
  draft: 'bg-gray-100 text-gray-700',
};

const STATUS_LABELS: Record<string, string> = {
  completed: 'مكتمل',
  processing: 'قيد المعالجة',
  pending: 'في الانتظار',
  approved: 'معتمد',
  draft: 'مسودة',
};

const STAT_COLORS: Record<string, { bg: string; icon: string }> = {
  green: { bg: 'bg-green-100', icon: 'text-green-600' },
  yellow: { bg: 'bg-yellow-100', icon: 'text-yellow-600' },
  blue: { bg: 'bg-blue-100', icon: 'text-blue-600' },
  purple: { bg: 'bg-purple-100', icon: 'text-purple-600' },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function TerrainClient() {
  const [activeTab, setActiveTab] = useState<TabId>('analyses');

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">تحليل التضاريس</h1>
        <p className="text-sm text-gray-500 mt-1">
          معالجة نموذج الارتفاع الرقمي وتحليل الانحدار وتحسين التسوية
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {STATS.map((s) => {
          const Icon = s.icon;
          const colors = (STAT_COLORS[s.color] ?? STAT_COLORS.blue)!;
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

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-green-700 shadow-sm font-medium'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Analyses Tab */}
      {activeTab === 'analyses' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-right p-4 font-medium text-gray-600">الحقل</th>
                <th className="text-right p-4 font-medium text-gray-600">النوع</th>
                <th className="text-right p-4 font-medium text-gray-600">الدقة</th>
                <th className="text-right p-4 font-medium text-gray-600">المساحة</th>
                <th className="text-right p-4 font-medium text-gray-600">التاريخ</th>
                <th className="text-right p-4 font-medium text-gray-600">الحالة</th>
              </tr>
            </thead>
            <tbody>
              {ANALYSES.map((a) => (
                <tr key={a.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="p-4 font-medium text-gray-900">{a.field}</td>
                  <td className="p-4 text-gray-600">{a.type}</td>
                  <td className="p-4 text-gray-600">{a.resolution}</td>
                  <td className="p-4 text-gray-600">{a.area} هـ</td>
                  <td className="p-4 text-gray-600">{a.date}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_STYLES[a.status] ?? ''}`}>
                      {STATUS_LABELS[a.status] ?? a.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Slope Tab */}
      {activeTab === 'slope' && (
        <div className="space-y-4">
          {SLOPE_DATA.map((s) => (
            <div key={s.range} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded-full ${s.color}`} />
                  <div>
                    <span className="font-bold text-gray-900">{s.label}</span>
                    <span className="text-sm text-gray-500 mr-2">({s.range})</span>
                  </div>
                </div>
                <div className="text-left">
                  <span className="text-lg font-bold text-gray-900">{s.area.toLocaleString('ar-SA')} هـ</span>
                  <span className="text-sm text-gray-500 mr-2">({s.pct}%)</span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div className={`h-2 rounded-full ${s.color}`} style={{ width: `${s.pct}%` }} />
              </div>
              <p className="text-sm text-gray-600">
                <TrendingUp className="w-3 h-3 inline ml-1" />
                {s.recommendation}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Leveling Tab */}
      {activeTab === 'leveling' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-right p-4 font-medium text-gray-600">الحقل</th>
                <th className="text-right p-4 font-medium text-gray-600">حجم القطع (م3)</th>
                <th className="text-right p-4 font-medium text-gray-600">حجم الردم (م3)</th>
                <th className="text-right p-4 font-medium text-gray-600">التكلفة (ريال)</th>
                <th className="text-right p-4 font-medium text-gray-600">التوفير المتوقع</th>
                <th className="text-right p-4 font-medium text-gray-600">الحالة</th>
              </tr>
            </thead>
            <tbody>
              {LEVELING_PLANS.map((l) => (
                <tr key={l.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="p-4 font-medium text-gray-900">{l.field}</td>
                  <td className="p-4 text-gray-600">{l.cutVol.toLocaleString('ar-SA')}</td>
                  <td className="p-4 text-gray-600">{l.fillVol.toLocaleString('ar-SA')}</td>
                  <td className="p-4 text-gray-600">{l.cost.toLocaleString('ar-SA')}</td>
                  <td className="p-4 text-green-600 font-medium">{l.savings.toLocaleString('ar-SA')}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_STYLES[l.status] ?? ''}`}>
                      {STATUS_LABELS[l.status] ?? l.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Hydrology Tab */}
      {activeTab === 'hydrology' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
          <Droplets className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            تحليل الهيدرولوجيا والصرف
          </h3>
          <p className="text-gray-500 text-sm mb-4">
            تحليل مجاري المياه وأحواض التجميع وتراكم التدفق سيتم عرضها هنا
          </p>
          <p className="text-xs text-gray-400">
            Drainage analysis, watershed delineation, and flow accumulation will be displayed here
          </p>
        </div>
      )}
    </div>
  );
}
