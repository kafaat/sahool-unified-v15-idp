'use client';

// Epidemic Monitoring Center - مركز رصد الأوبئة
// Advanced disease outbreak monitoring with heatmap visualization

import { useEffect, useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import { fetchDiagnoses, fetchDiagnosisStats } from '@/lib/api';
import { cn } from '@/lib/utils';
import type { DiagnosisRecord } from '@/types';
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
} from 'lucide-react';

// Yemen Governorates with coordinates
const GOVERNORATES = [
  { id: 'sanaa', name: 'صنعاء', lat: 15.3694, lng: 44.1910, color: '#ef4444' },
  { id: 'aden', name: 'عدن', lat: 12.7797, lng: 45.0187, color: '#f97316' },
  { id: 'taiz', name: 'تعز', lat: 13.5789, lng: 44.0219, color: '#eab308' },
  { id: 'ibb', name: 'إب', lat: 13.9759, lng: 44.1709, color: '#22c55e' },
  { id: 'hodeidah', name: 'الحديدة', lat: 14.7979, lng: 42.9540, color: '#3b82f6' },
  { id: 'hadramaut', name: 'حضرموت', lat: 15.9329, lng: 49.3929, color: '#8b5cf6' },
  { id: 'dhamar', name: 'ذمار', lat: 14.5426, lng: 44.4051, color: '#ec4899' },
  { id: 'marib', name: 'مأرب', lat: 15.4542, lng: 45.3269, color: '#06b6d4' },
  { id: 'hajjah', name: 'حجة', lat: 15.6917, lng: 43.6028, color: '#14b8a6' },
  { id: 'saadah', name: 'صعدة', lat: 16.9410, lng: 43.7640, color: '#f43f5e' },
  { id: 'shabwah', name: 'شبوة', lat: 14.5333, lng: 47.0167, color: '#a855f7' },
  { id: 'lahij', name: 'لحج', lat: 13.0578, lng: 44.8831, color: '#84cc16' },
];

interface EpidemicStats {
  total: number;
  pending: number;
  confirmed: number;
  treated: number;
  criticalCount: number;
  highCount: number;
  byDisease: Record<string, number>;
  byGovernorate: Record<string, number>;
}

export default function EpidemicCenterPage() {
  const [diagnoses, setDiagnoses] = useState<DiagnosisRecord[]>([]);
  const [stats, setStats] = useState<EpidemicStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedGovernorate, setSelectedGovernorate] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month'>('week');

  useEffect(() => {
    loadData();
  }, [timeRange]);

  async function loadData() {
    setIsLoading(true);
    try {
      const [diagnosesData, statsData] = await Promise.all([
        fetchDiagnoses({ limit: 100 }),
        fetchDiagnosisStats(),
      ]);
      setDiagnoses(diagnosesData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load epidemic data:', error);
    } finally {
      setIsLoading(false);
    }
  }

  // Calculate governorate statistics
  const governorateStats = useMemo(() => {
    const statsMap: Record<string, { total: number; critical: number; high: number }> = {};

    GOVERNORATES.forEach(gov => {
      statsMap[gov.id] = { total: 0, critical: 0, high: 0 };
    });

    diagnoses.forEach(d => {
      // Try to match governorate from diagnosis
      const govName = (d as any).governorate?.toLowerCase() || '';
      const gov = GOVERNORATES.find(g =>
        g.id === govName || g.name.includes(govName)
      );

      if (gov) {
        statsMap[gov.id].total++;
        if (d.severity === 'critical') statsMap[gov.id].critical++;
        if (d.severity === 'high') statsMap[gov.id].high++;
      }
    });

    return statsMap;
  }, [diagnoses]);

  // Top diseases
  const topDiseases = useMemo(() => {
    if (!stats?.byDisease) return [];
    return Object.entries(stats.byDisease)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5);
  }, [stats]);

  // Alert level calculation
  const getAlertLevel = (govId: string) => {
    const govStats = governorateStats[govId];
    if (!govStats) return 'safe';
    if (govStats.critical > 0) return 'critical';
    if (govStats.high > 2) return 'high';
    if (govStats.total > 5) return 'medium';
    return 'safe';
  };

  const alertColors = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-yellow-500',
    safe: 'bg-green-500',
  };

  return (
    <div className="p-6">
      <Header
        title="مركز رصد الأوبئة"
        subtitle="المراقبة المتقدمة لانتشار الأمراض في اليمن"
      />

      {/* Quick Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.total || 0}</p>
              <p className="text-xs text-gray-500">إجمالي الحالات</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{stats?.criticalCount || 0}</p>
              <p className="text-xs text-gray-500">حالات حرجة</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-600">{stats?.highCount || 0}</p>
              <p className="text-xs text-gray-500">خطورة عالية</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-100 rounded-lg">
              <Bug className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-600">{stats?.pending || 0}</p>
              <p className="text-xs text-gray-500">قيد المراجعة</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingDown className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{stats?.treated || 0}</p>
              <p className="text-xs text-gray-500">تم العلاج</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <MapPin className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">
                {Object.values(governorateStats).filter(g => g.total > 0).length}
              </p>
              <p className="text-xs text-gray-500">محافظات متأثرة</p>
            </div>
          </div>
        </div>
      </div>

      {/* Time Range Filter */}
      <div className="mt-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-600">الفترة الزمنية:</span>
          <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
            {[
              { key: 'day', label: 'اليوم' },
              { key: 'week', label: 'الأسبوع' },
              { key: 'month', label: 'الشهر' },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setTimeRange(key as any)}
                className={cn(
                  'px-3 py-1 text-sm rounded-md transition-colors',
                  timeRange === key
                    ? 'bg-white text-sahool-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          تحديث
        </button>
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Governorates Map (Simplified) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-sahool-600" />
            خريطة انتشار الأمراض
          </h3>

          {/* Simplified Governorate Grid */}
          <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
            {GOVERNORATES.map(gov => {
              const govStats = governorateStats[gov.id];
              const alertLevel = getAlertLevel(gov.id);
              const isSelected = selectedGovernorate === gov.id;

              return (
                <button
                  key={gov.id}
                  onClick={() => setSelectedGovernorate(isSelected ? null : gov.id)}
                  className={cn(
                    'relative p-4 rounded-xl border-2 transition-all text-right',
                    isSelected
                      ? 'border-sahool-500 bg-sahool-50'
                      : 'border-gray-100 hover:border-gray-200 bg-white'
                  )}
                >
                  {/* Alert Indicator */}
                  <div className={cn(
                    'absolute top-2 left-2 w-3 h-3 rounded-full',
                    alertColors[alertLevel]
                  )} />

                  <p className="font-bold text-gray-900">{gov.name}</p>
                  <p className="text-2xl font-bold mt-1" style={{ color: gov.color }}>
                    {govStats?.total || 0}
                  </p>
                  <p className="text-xs text-gray-500">حالة</p>

                  {govStats?.critical > 0 && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-red-600">
                      <AlertTriangle className="w-3 h-3" />
                      {govStats.critical} حرج
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
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-sahool-600" />
            أكثر الأمراض انتشاراً
          </h3>

          <div className="space-y-4">
            {topDiseases.length > 0 ? (
              topDiseases.map(([disease, count], index) => {
                const maxCount = topDiseases[0][1];
                const percentage = (count / maxCount) * 100;

                return (
                  <div key={disease}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">{disease}</span>
                      <span className="text-sm text-gray-500">{count}</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={cn(
                          'h-full rounded-full transition-all',
                          index === 0 ? 'bg-red-500' :
                          index === 1 ? 'bg-orange-500' :
                          index === 2 ? 'bg-yellow-500' :
                          'bg-blue-500'
                        )}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Bug className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>لا توجد بيانات</p>
              </div>
            )}
          </div>

          {/* Selected Governorate Details */}
          {selectedGovernorate && (
            <div className="mt-6 pt-6 border-t border-gray-100">
              <h4 className="font-bold text-gray-900 mb-3">
                {GOVERNORATES.find(g => g.id === selectedGovernorate)?.name}
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">إجمالي الحالات:</span>
                  <span className="font-medium">{governorateStats[selectedGovernorate]?.total || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">حالات حرجة:</span>
                  <span className="font-medium text-red-600">{governorateStats[selectedGovernorate]?.critical || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">خطورة عالية:</span>
                  <span className="font-medium text-orange-600">{governorateStats[selectedGovernorate]?.high || 0}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Critical Cases */}
      <div className="mt-6 bg-white rounded-xl border border-gray-100 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          الحالات الحرجة الأخيرة
        </h3>

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-16 bg-gray-100 animate-pulse rounded-lg" />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {diagnoses
              .filter(d => d.severity === 'critical' || d.severity === 'high')
              .slice(0, 5)
              .map(diagnosis => (
                <div
                  key={diagnosis.id}
                  className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className={cn(
                    'w-3 h-3 rounded-full',
                    diagnosis.severity === 'critical' ? 'bg-red-500' : 'bg-orange-500'
                  )} />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{diagnosis.diseaseNameAr}</p>
                    <p className="text-sm text-gray-500">{diagnosis.farmName}</p>
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-medium">{diagnosis.confidence.toFixed(0)}%</p>
                    <p className="text-xs text-gray-500">دقة</p>
                  </div>
                </div>
              ))}

            {diagnoses.filter(d => d.severity === 'critical' || d.severity === 'high').length === 0 && (
              <div className="text-center py-8 text-gray-400">
                <AlertTriangle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>لا توجد حالات حرجة حالياً</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
