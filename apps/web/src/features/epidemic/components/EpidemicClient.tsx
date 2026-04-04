'use client';

/**
 * Epidemic Monitoring Client Component
 * مكون مركز رصد الأوبئة — مراقبة انتشار الأمراض
 */

import React, { useState, useMemo } from 'react';
import {
  Bug,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  MapPin,
  Activity,
  BarChart3,
  RefreshCw,
  Filter,
  CheckCircle,
  Clock,
  Shield,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------

const GOVERNORATES = [
  { id: 'sanaa', name: 'صنعاء', color: '#ef4444' },
  { id: 'aden', name: 'عدن', color: '#f97316' },
  { id: 'taiz', name: 'تعز', color: '#eab308' },
  { id: 'ibb', name: 'إب', color: '#22c55e' },
  { id: 'hodeidah', name: 'الحديدة', color: '#3b82f6' },
  { id: 'hadramaut', name: 'حضرموت', color: '#8b5cf6' },
  { id: 'dhamar', name: 'ذمار', color: '#ec4899' },
  { id: 'marib', name: 'مأرب', color: '#06b6d4' },
  { id: 'hajjah', name: 'حجة', color: '#14b8a6' },
  { id: 'saadah', name: 'صعدة', color: '#f43f5e' },
  { id: 'shabwah', name: 'شبوة', color: '#a855f7' },
  { id: 'lahij', name: 'لحج', color: '#84cc16' },
];

interface GovStats {
  total: number;
  critical: number;
  high: number;
}

const GOV_STATS: Record<string, GovStats> = {
  sanaa: { total: 45, critical: 3, high: 8 },
  aden: { total: 22, critical: 1, high: 4 },
  taiz: { total: 38, critical: 2, high: 6 },
  ibb: { total: 15, critical: 0, high: 2 },
  hodeidah: { total: 52, critical: 5, high: 10 },
  hadramaut: { total: 8, critical: 0, high: 1 },
  dhamar: { total: 18, critical: 1, high: 3 },
  marib: { total: 12, critical: 0, high: 2 },
  hajjah: { total: 30, critical: 2, high: 5 },
  saadah: { total: 25, critical: 1, high: 4 },
  shabwah: { total: 6, critical: 0, high: 0 },
  lahij: { total: 14, critical: 0, high: 2 },
};

const TOP_DISEASES = [
  { name: 'صدأ القمح', nameEn: 'Wheat Rust', count: 78, trend: 'increasing' as const },
  { name: 'اللفحة المتأخرة', nameEn: 'Late Blight', count: 52, trend: 'stable' as const },
  { name: 'البياض الدقيقي', nameEn: 'Powdery Mildew', count: 41, trend: 'decreasing' as const },
  { name: 'تبقع الأوراق', nameEn: 'Leaf Spot', count: 35, trend: 'increasing' as const },
  { name: 'الفيوزاريوم', nameEn: 'Fusarium Wilt', count: 28, trend: 'stable' as const },
];

const RECENT_CASES = [
  { id: 'c1', disease: 'صدأ القمح', governorate: 'الحديدة', severity: 'critical', confidence: 92, date: '2026-04-03', farm: 'مزرعة الأمل' },
  { id: 'c2', disease: 'اللفحة المتأخرة', governorate: 'تعز', severity: 'critical', confidence: 88, date: '2026-04-03', farm: 'مزرعة السلام' },
  { id: 'c3', disease: 'دودة الحشد', governorate: 'صنعاء', severity: 'high', confidence: 95, date: '2026-04-02', farm: 'مزرعة الوادي' },
  { id: 'c4', disease: 'سوسة النخيل', governorate: 'حضرموت', severity: 'critical', confidence: 97, date: '2026-04-02', farm: 'مزرعة النخيل' },
  { id: 'c5', disease: 'البياض الدقيقي', governorate: 'إب', severity: 'high', confidence: 85, date: '2026-04-01', farm: 'مزرعة الخضراء' },
];

const STATS_DATA = [
  { label: 'إجمالي الحالات', value: 285, icon: Activity, color: 'text-blue-600', bg: 'bg-blue-100' },
  { label: 'حالات حرجة', value: 15, icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-100' },
  { label: 'خطورة عالية', value: 47, icon: TrendingUp, color: 'text-orange-600', bg: 'bg-orange-100' },
  { label: 'قيد المراجعة', value: 32, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-100' },
  { label: 'تم العلاج', value: 198, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
  { label: 'محافظات متأثرة', value: 11, icon: MapPin, color: 'text-purple-600', bg: 'bg-purple-100' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const getAlertLevel = (govId: string): string => {
  const stats = GOV_STATS[govId];
  if (!stats) return 'safe';
  if (stats.critical > 0) return 'critical';
  if (stats.high > 2) return 'high';
  if (stats.total > 5) return 'medium';
  return 'safe';
};

const ALERT_COLORS: Record<string, string> = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  safe: 'bg-green-500',
};

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function EpidemicClient() {
  const [selectedGovernorate, setSelectedGovernorate] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month'>('week');

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">مركز رصد الأوبئة</h1>
        <p className="text-sm text-gray-500 mt-1">
          المراقبة المتقدمة لانتشار الأمراض والآفات في اليمن
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {STATS_DATA.map((s) => {
          const Icon = s.icon;
          return (
            <div key={s.label} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-2 mb-1">
                <div className={`w-8 h-8 ${s.bg} rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-4 h-4 ${s.color}`} />
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">{s.value}</p>
              <p className="text-xs text-gray-500">{s.label}</p>
            </div>
          );
        })}
      </div>

      {/* Time Range Filter */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-600">الفترة الزمنية:</span>
          <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
            {[
              { key: 'day' as const, label: 'اليوم' },
              { key: 'week' as const, label: 'الأسبوع' },
              { key: 'month' as const, label: 'الشهر' },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setTimeRange(key)}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  timeRange === key
                    ? 'bg-white text-green-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <RefreshCw className="w-4 h-4" />
          تحديث
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Governorates Grid */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-green-600" />
            خريطة انتشار الأمراض
          </h3>

          <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
            {GOVERNORATES.map((gov) => {
              const stats = GOV_STATS[gov.id];
              const alertLevel = getAlertLevel(gov.id);
              const isSelected = selectedGovernorate === gov.id;

              return (
                <button
                  key={gov.id}
                  onClick={() =>
                    setSelectedGovernorate(isSelected ? null : gov.id)
                  }
                  className={`relative p-4 rounded-xl border-2 transition-all text-right ${
                    isSelected
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-100 hover:border-gray-200 bg-white'
                  }`}
                >
                  <div
                    className={`absolute top-2 left-2 w-3 h-3 rounded-full ${ALERT_COLORS[alertLevel] ?? 'bg-green-500'}`}
                  />
                  <p className="font-bold text-gray-900">{gov.name}</p>
                  <p className="text-2xl font-bold mt-1" style={{ color: gov.color }}>
                    {stats?.total ?? 0}
                  </p>
                  <p className="text-xs text-gray-500">حالة</p>
                  {(stats?.critical ?? 0) > 0 && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-red-600">
                      <AlertTriangle className="w-3 h-3" />
                      {stats?.critical ?? 0} حرج
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Legend */}
          <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span>حرج</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-orange-500" />
              <span>مرتفع</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <span>متوسط</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span>آمن</span>
            </div>
          </div>
        </div>

        {/* Top Diseases Sidebar */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-green-600" />
            أكثر الأمراض انتشاراً
          </h3>

          <div className="space-y-4">
            {TOP_DISEASES.map((disease, index) => {
              const maxCount = TOP_DISEASES[0]?.count ?? 1;
              const percentage = (disease.count / maxCount) * 100;
              return (
                <div key={disease.name}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-700">{disease.name}</span>
                      {disease.trend === 'increasing' ? (
                        <TrendingUp className="w-3 h-3 text-red-500" />
                      ) : disease.trend === 'decreasing' ? (
                        <TrendingDown className="w-3 h-3 text-green-500" />
                      ) : null}
                    </div>
                    <span className="text-sm text-gray-500">{disease.count}</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        index === 0
                          ? 'bg-red-500'
                          : index === 1
                            ? 'bg-orange-500'
                            : index === 2
                              ? 'bg-yellow-500'
                              : 'bg-blue-500'
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Selected Governorate Details */}
          {selectedGovernorate && (
            <div className="mt-6 pt-6 border-t border-gray-100">
              <h4 className="font-bold text-gray-900 mb-3">
                {GOVERNORATES.find((g) => g.id === selectedGovernorate)?.name}
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">إجمالي الحالات:</span>
                  <span className="font-medium">{GOV_STATS[selectedGovernorate]?.total ?? 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">حالات حرجة:</span>
                  <span className="font-medium text-red-600">
                    {GOV_STATS[selectedGovernorate]?.critical ?? 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">خطورة عالية:</span>
                  <span className="font-medium text-orange-600">
                    {GOV_STATS[selectedGovernorate]?.high ?? 0}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Critical Cases */}
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          الحالات الحرجة الأخيرة
        </h3>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-right p-4 font-medium text-gray-600">الحالة</th>
                <th className="text-right p-4 font-medium text-gray-600">المرض</th>
                <th className="text-right p-4 font-medium text-gray-600">المحافظة</th>
                <th className="text-right p-4 font-medium text-gray-600">المزرعة</th>
                <th className="text-right p-4 font-medium text-gray-600">دقة التشخيص</th>
                <th className="text-right p-4 font-medium text-gray-600">التاريخ</th>
              </tr>
            </thead>
            <tbody>
              {RECENT_CASES.map((c) => (
                <tr key={c.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          c.severity === 'critical' ? 'bg-red-500' : 'bg-orange-500'
                        }`}
                      />
                      <span className="font-medium">
                        {c.severity === 'critical' ? 'حرج' : 'عالي'}
                      </span>
                    </div>
                  </td>
                  <td className="p-4 font-medium text-gray-900">{c.disease}</td>
                  <td className="p-4 text-gray-600">{c.governorate}</td>
                  <td className="p-4 text-gray-600">{c.farm}</td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500 rounded-full"
                          style={{ width: `${c.confidence}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{c.confidence}%</span>
                    </div>
                  </td>
                  <td className="p-4 text-gray-500">{c.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
