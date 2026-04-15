'use client';

/**
 * Epidemic Monitoring Client Component
 * مكون مركز رصد الأوبئة — مراقبة انتشار الأمراض
 */

import React, { useState, useMemo } from 'react';
import {
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
} from 'lucide-react';
import { useEpidemics } from '../hooks/useEpidemic';
import type { Epidemic } from '../api';

// ---------------------------------------------------------------------------
// Static data (governorates are not served by the API)
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

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

interface GovStats {
  total: number;
  critical: number;
  high: number;
}

function buildGovStats(epidemics: Epidemic[]): Record<string, GovStats> {
  const result: Record<string, GovStats> = {};
  GOVERNORATES.forEach((g) => {
    result[g.id] = { total: 0, critical: 0, high: 0 };
  });
  epidemics.forEach((e) => {
    const govId = e.region?.toLowerCase() ?? '';
    if (result[govId]) {
      result[govId]!.total += 1;
      if (e.severity === 'critical') result[govId]!.critical += 1;
      if (e.severity === 'high') result[govId]!.high += 1;
    }
  });
  return result;
}

function buildTopDiseases(epidemics: Epidemic[]) {
  const counts: Record<string, { name: string; nameEn: string; count: number; trend: 'increasing' | 'stable' | 'decreasing' }> = {};
  epidemics.forEach((e) => {
    const key = e.diseaseType;
    if (!counts[key]) {
      counts[key] = { name: e.nameAr || e.name, nameEn: e.name, count: 0, trend: 'stable' };
    }
    counts[key]!.count += 1;
    if (e.spreadRate > 5) counts[key]!.trend = 'increasing';
    else if (e.spreadRate < 0) counts[key]!.trend = 'decreasing';
  });
  return Object.values(counts).sort((a, b) => b.count - a.count).slice(0, 5);
}

function buildRecentCases(epidemics: Epidemic[]) {
  return epidemics
    .filter((e) => e.severity === 'critical' || e.severity === 'high')
    .sort((a, b) => new Date(b.reportedAt).getTime() - new Date(a.reportedAt).getTime())
    .slice(0, 5)
    .map((e, i) => ({
      id: e.id || `c${i}`,
      disease: e.nameAr || e.name,
      governorate: e.region,
      severity: e.severity,
      // Confidence is not returned by the epidemics endpoint — display "--"
      // instead of fabricating a random value.
      confidence: null as number | null,
      date: e.reportedAt?.split('T')[0] ?? '',
      farm: '-',
    }));
}

const getAlertLevel = (stats: GovStats | undefined): string => {
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

// ---------------------------------------------------------------------------
// Loading / Error UI
// ---------------------------------------------------------------------------

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 animate-pulse">
            <div className="w-8 h-8 bg-gray-200 rounded-lg mb-2" />
            <div className="h-6 bg-gray-200 rounded w-1/2 mb-1" />
            <div className="h-3 bg-gray-200 rounded w-2/3" />
          </div>
        ))}
      </div>
    </div>
  );
}

function ErrorBanner({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
      <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
      <p className="text-red-700 font-medium mb-3">{message}</p>
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
      >
        <RefreshCw className="w-4 h-4" />
        إعادة المحاولة
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function EpidemicClient() {
  const [selectedGovernorate, setSelectedGovernorate] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month'>('week');

  // Fetch epidemics from API
  const {
    data: epidemics,
    isLoading,
    isError,
    refetch,
  } = useEpidemics();

  // Derive stats from API data
  const govStats = useMemo(() => buildGovStats(epidemics ?? []), [epidemics]);
  const topDiseases = useMemo(() => buildTopDiseases(epidemics ?? []), [epidemics]);
  const recentCases = useMemo(() => buildRecentCases(epidemics ?? []), [epidemics]);

  const summaryStats = useMemo(() => {
    const list = epidemics ?? [];
    return [
      { label: 'إجمالي الحالات', value: list.length, icon: Activity, color: 'text-blue-600', bg: 'bg-blue-100' },
      { label: 'حالات حرجة', value: list.filter((e) => e.severity === 'critical').length, icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-100' },
      { label: 'خطورة عالية', value: list.filter((e) => e.severity === 'high').length, icon: TrendingUp, color: 'text-orange-600', bg: 'bg-orange-100' },
      { label: 'قيد المراجعة', value: list.filter((e) => e.status === 'monitoring').length, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-100' },
      { label: 'تم العلاج', value: list.filter((e) => e.status === 'resolved' || e.status === 'contained').length, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
      { label: 'محافظات متأثرة', value: new Set(list.map((e) => e.region)).size, icon: MapPin, color: 'text-purple-600', bg: 'bg-purple-100' },
    ];
  }, [epidemics]);

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">مركز رصد الأوبئة</h1>
        <p className="text-sm text-gray-500 mt-1">
          المراقبة المتقدمة لانتشار الأمراض والآفات في اليمن
        </p>
      </div>

      {/* Loading */}
      {isLoading && <LoadingSkeleton />}

      {/* Error */}
      {isError && (
        <ErrorBanner
          message="فشل في تحميل بيانات الأوبئة. يرجى المحاولة مرة أخرى."
          onRetry={() => refetch()}
        />
      )}

      {/* Content */}
      {!isLoading && !isError && (
        <>
          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {summaryStats.map((s) => {
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
            <button
              onClick={() => refetch()}
              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
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
                  const stats = govStats[gov.id];
                  const alertLevel = getAlertLevel(stats);
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

              {topDiseases.length === 0 ? (
                <p className="text-gray-500 text-sm">لا توجد بيانات</p>
              ) : (
                <div className="space-y-4">
                  {topDiseases.map((disease, index) => {
                    const maxCount = topDiseases[0]?.count ?? 1;
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
              )}

              {/* Selected Governorate Details */}
              {selectedGovernorate && (
                <div className="mt-6 pt-6 border-t border-gray-100">
                  <h4 className="font-bold text-gray-900 mb-3">
                    {GOVERNORATES.find((g) => g.id === selectedGovernorate)?.name}
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">إجمالي الحالات:</span>
                      <span className="font-medium">{govStats[selectedGovernorate]?.total ?? 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">حالات حرجة:</span>
                      <span className="font-medium text-red-600">
                        {govStats[selectedGovernorate]?.critical ?? 0}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">خطورة عالية:</span>
                      <span className="font-medium text-orange-600">
                        {govStats[selectedGovernorate]?.high ?? 0}
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
              {recentCases.length === 0 ? (
                <div className="p-8 text-center text-gray-500">لا توجد حالات حرجة حالياً</div>
              ) : (
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
                    {recentCases.map((c) => (
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
                          {c.confidence != null ? (
                            <div className="flex items-center gap-2">
                              <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-green-500 rounded-full"
                                  style={{ width: `${c.confidence}%` }}
                                />
                              </div>
                              <span className="text-sm font-medium">{c.confidence}%</span>
                            </div>
                          ) : (
                            <span className="text-sm text-gray-400">--</span>
                          )}
                        </td>
                        <td className="p-4 text-gray-500">{c.date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
