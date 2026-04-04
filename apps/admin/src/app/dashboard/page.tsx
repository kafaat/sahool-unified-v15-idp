'use client';

// Sahool Admin Dashboard - Main Page
// الصفحة الرئيسية للوحة تحكم سهول - غرفة العمليات المركزية

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import AlertBadge from '@/components/ui/AlertBadge';
import {
  fetchDashboardStats,
  fetchFarms,
  fetchDiagnoses,
  fetchYieldTrends,
  fetchCropDistribution,
  fetchWeeklyActivity,
  fetchPlatformMetrics,
} from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { t } from '@/lib/i18n';
import type { DashboardStats, Farm, DiagnosisRecord } from '@/types';
import type { BaseFarmData } from '@/components/maps/FarmsMap';
import {
  MapPin,
  Leaf,
  Bug,
  AlertTriangle,
  TrendingUp,
  Activity,
  Eye,
  Users,
  DollarSign,
  Droplets,
  Sun,
  Wifi,
  WifiOff,
} from 'lucide-react';
import Link from 'next/link';
import { useWebSocket, useWebSocketEvent } from '@/hooks/useWebSocket';
import { useRealTimeAlerts } from '@/hooks/useRealTimeAlerts';
import type { SensorMessage, DiagnosisMessage } from '@/hooks/useWebSocket';
import ExpertView from '@/components/fields/ExpertView';
import { logger } from '../../lib/logger';
import {
  YieldTrendChart,
  WeeklyActivityChart,
  CropDistributionChart,
} from './DashboardCharts.dynamic';

// Dynamic import for CrossFarmDashboard (no SSR)
const CrossFarmDashboard = dynamic(
  () => import('@/components/dashboard/CrossFarmDashboard'),
  {
    ssr: false,
    loading: () => (
      <div className="h-64 bg-gray-100 dark:bg-gray-700 animate-pulse rounded-xl flex items-center justify-center">
        <p className="text-gray-500 dark:text-gray-400">جاري تحميل لوحة المقارنة...</p>
      </div>
    ),
  }
);

// Dynamic import for map (no SSR) with error handling
const FarmsMap = dynamic(
  () =>
    import('@/components/maps/FarmsMap').catch((err) => {
      logger.error('Failed to load FarmsMap:', err);
      // Return a fallback component on error
      return {
        default: () => (
          <div className="h-[400px] bg-red-50 rounded-xl flex items-center justify-center">
            <p className="text-red-600">فشل تحميل الخريطة. يرجى تحديث الصفحة.</p>
          </div>
        ),
      };
    }),
  {
    ssr: false,
    loading: () => (
      <div className="h-[400px] bg-gray-100 dark:bg-gray-700 animate-pulse rounded-xl flex items-center justify-center">
        <p className="text-gray-500 dark:text-gray-400">جاري تحميل الخريطة...</p>
      </div>
    ),
  }
);

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [recentDiagnoses, setRecentDiagnoses] = useState<DiagnosisRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedFarm, setSelectedFarm] = useState<Farm | null>(null);
  const [yieldTrendData, setYieldTrendData] = useState<
    Array<{ month: string; yield: number; forecast: number }>
  >([]);
  const [cropDistributionData, setCropDistributionData] = useState<
    Array<{ name: string; value: number }>
  >([]);
  const [weeklyActivityData, setWeeklyActivityData] = useState<
    Array<{ day: string; diagnoses: number; irrigations: number; alerts: number }>
  >([]);
  const [platformMetrics, setPlatformMetrics] = useState<{
    activeFarmers: number;
    dailySales: number;
    irrigationOps: number;
    avgTemperature: number;
    monthlyGrowthRate: number;
  } | null>(null);

  // WebSocket integration for real-time updates
  const { isConnected } = useWebSocket({ autoConnect: true });
  const { unreadCount, criticalAlerts } = useRealTimeAlerts({
    enableNotifications: true,
    minSeverity: 'medium',
  });

  // Load initial data with individual error handling using Promise.allSettled
  useEffect(() => {
    async function loadData() {
      try {
        const results = await Promise.allSettled([
          fetchDashboardStats(),
          fetchFarms(),
          fetchDiagnoses({ limit: 5 }),
          fetchYieldTrends('30d'),
          fetchCropDistribution(),
          fetchWeeklyActivity(),
          fetchPlatformMetrics(),
        ]);

        let failedCount = 0;

        // Handle stats result
        if (results[0].status === 'fulfilled') {
          setStats(results[0].value);
        } else {
          logger.error('Failed to load dashboard stats:', results[0].reason);
          failedCount++;
        }

        // Handle farms result
        if (results[1].status === 'fulfilled') {
          setFarms(results[1].value);
        } else {
          logger.error('Failed to load farms:', results[1].reason);
          failedCount++;
        }

        // Handle diagnoses result
        if (results[2].status === 'fulfilled') {
          setRecentDiagnoses(results[2].value.slice(0, 5));
        } else {
          logger.error('Failed to load diagnoses:', results[2].reason);
          failedCount++;
        }

        // Handle yield trends
        if (results[3].status === 'fulfilled') {
          setYieldTrendData(results[3].value);
        } else {
          logger.error('Failed to load yield trends:', results[3].reason);
        }

        // Handle crop distribution
        if (results[4].status === 'fulfilled') {
          setCropDistributionData(results[4].value);
        } else {
          logger.error('Failed to load crop distribution:', results[4].reason);
        }

        // Handle weekly activity
        if (results[5].status === 'fulfilled') {
          setWeeklyActivityData(results[5].value);
        } else {
          logger.error('Failed to load weekly activity:', results[5].reason);
        }

        // Handle platform metrics
        if (results[6].status === 'fulfilled') {
          setPlatformMetrics(results[6].value);
        } else {
          logger.error('Failed to load platform metrics:', results[6].reason);
        }

        // Show error if core requests failed
        if (failedCount === 3) {
          setLoadError('فشل تحميل بيانات لوحة التحكم. يرجى التحقق من الاتصال.');
        } else if (failedCount > 0) {
          logger.warn(`${failedCount} of 3 dashboard data requests failed`);
        }
      } catch (error) {
        logger.error('Failed to load dashboard data:', error);
        setLoadError('حدث خطأ غير متوقع. يرجى تحديث الصفحة.');
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  // Real-time diagnosis updates via WebSocket
  useWebSocketEvent<DiagnosisMessage>('diagnosis', (diagnosis) => {
    // Update weekly diagnoses count
    setStats((prev) =>
      prev ? { ...prev, weeklyDiagnoses: (prev.weeklyDiagnoses || 0) + 1 } : prev
    );

    // Add to recent diagnoses
    setRecentDiagnoses((prev) => {
      const newDiagnosis: DiagnosisRecord = {
        id: diagnosis.id,
        farmId: diagnosis.farmId,
        farmName: diagnosis.farmName,
        diseaseNameAr: diagnosis.diseaseNameAr,
        diseaseName: '',
        diseaseId: '',
        imageUrl: '/api/placeholder/400/300',
        thumbnailUrl: undefined,
        cropType: '',
        confidence: diagnosis.confidence,
        severity: diagnosis.severity,
        status: 'pending',
        location: { lat: 0, lng: 0 },
        diagnosedAt: diagnosis.timestamp,
        createdBy: '',
      };

      return [newDiagnosis, ...prev].slice(0, 5);
    });
  });

  // Real-time sensor updates via WebSocket
  useWebSocketEvent<SensorMessage>('sensor', (sensor) => {
    // Log sensor readings - can be extended to show live sensor data
    logger.debug('New sensor reading:', sensor);
  });

  // Update critical alerts count from real-time data
  // Uses functional update to safely handle null stats state
  useEffect(() => {
    setStats((prev) => {
      // If stats is null or critical alerts count is unchanged, no update needed
      if (!prev) return prev;
      if (prev.criticalAlerts === criticalAlerts.length) return prev;
      return { ...prev, criticalAlerts: criticalAlerts.length };
    });
  }, [criticalAlerts.length]);

  // Accept any farm-like object that has at least the base properties
  const handleFarmClick = (farm: BaseFarmData) => {
    setSelectedFarm(farm as Farm);
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <Header title={t('dashboard.title')} subtitle={t('dashboard.overview')} />
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 animate-pulse rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  // Show error message if data loading completely failed
  if (loadError && !stats && farms.length === 0) {
    return (
      <div className="p-6">
        <Header title={t('dashboard.title')} subtitle={t('dashboard.overview')} />
        <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-700 font-medium">{loadError}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            إعادة تحميل الصفحة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between">
        <Header title={t('dashboard.title')} subtitle={t('dashboard.overview')} />

        {/* WebSocket Connection Status */}
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600">
          {isConnected ? (
            <>
              <Wifi className="w-4 h-4 text-green-500" />
              <span className="text-sm text-gray-700 dark:text-gray-300">متصل</span>
              {unreadCount > 0 && (
                <span className="ml-2 px-2 py-0.5 text-xs font-semibold text-white bg-red-500 rounded-full">
                  {unreadCount}
                </span>
              )}
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-gray-400 dark:text-gray-500" />
              <span className="text-sm text-gray-500 dark:text-gray-400">غير متصل</span>
            </>
          )}
        </div>
      </div>

      {/* Real-time Status Indicators */}
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <span className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">
          {isConnected ? (
            <><span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" /> الخدمات: متصلة</>
          ) : (
            <><span className="w-2 h-2 rounded-full bg-red-500" /> الخدمات: غير متصلة</>
          )}
        </span>
        <span className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">
          🛰️ آخر صورة: {farms.length > 0 ? formatDate(farms?.[0]?.lastUpdated) : '—'}
        </span>
        <span className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">
          ☁️ الطقس: {platformMetrics?.avgTemperature ? `${platformMetrics.avgTemperature}°` : '—'}
        </span>
      </div>

      {/* Quick Actions Bar */}
      <div className="mt-4 flex flex-wrap gap-2">
        <Link href="/farms" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-full bg-green-50 dark:bg-green-950/40 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800 hover:bg-green-100 dark:hover:bg-green-900/50 transition-colors">
          🌿 إنشاء حقل
        </Link>
        <Link href="/irrigation" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-full bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors">
          💧 جدولة ري
        </Link>
        <Link href="/epidemic" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-full bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-400 border border-purple-200 dark:border-purple-800 hover:bg-purple-100 dark:hover:bg-purple-900/50 transition-colors">
          🔬 تشخيص مرض
        </Link>
        <Link href="/analytics/satellite" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors">
          📊 تقارير
        </Link>
        <Link href="/alerts" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-full bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800 hover:bg-amber-100 dark:hover:bg-amber-900/50 transition-colors">
          ⚠️ التنبيهات
        </Link>
        <Link href="/tasks" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100 dark:hover:bg-emerald-900/50 transition-colors">
          ✅ المهام
        </Link>
      </div>

      {/* Statistics Cards */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title={t('dashboard.stats.farms')}
          value={stats?.totalFarms || 0}
          icon={MapPin}
          iconColor="text-blue-600"
        />
        <StatCard
          title={t('dashboard.stats.area')}
          value={stats?.totalArea?.toFixed(1) || '0'}
          suffix={t('units.hectare')}
          icon={Leaf}
          iconColor="text-green-600"
        />
        <StatCard
          title={t('dashboard.stats.diagnoses')}
          value={stats?.weeklyDiagnoses || 0}
          icon={Bug}
          iconColor="text-purple-600"
        />
        <StatCard
          title={t('dashboard.stats.alerts')}
          value={stats?.criticalAlerts || 0}
          icon={AlertTriangle}
          iconColor="text-red-600"
        />
      </div>

      {/* Second Row - More Stats */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title={t('dashboard.stats.health')}
          value={`${stats?.avgHealthScore?.toFixed(1) || '0'}%`}
          icon={Activity}
          iconColor="text-emerald-600"
        />
        <StatCard
          title={t('dashboard.stats.reviews')}
          value={stats?.pendingReviews || 0}
          icon={Eye}
          iconColor="text-amber-600"
        />
        <StatCard
          title={t('dashboard.stats.activeFarms')}
          value={stats?.activeFarms || 0}
          icon={TrendingUp}
          iconColor="text-cyan-600"
        />
      </div>

      {/* Charts Row */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Yield Trend Chart */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900 dark:text-gray-100">
              {t('dashboard.charts.yield')}
            </h3>
            <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
              آخر 6 أشهر
            </span>
          </div>
          <div className="h-64">
            <YieldTrendChart data={yieldTrendData} />
          </div>
        </div>

        {/* Weekly Activity Chart */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900 dark:text-gray-100">
              {t('dashboard.charts.activity')}
            </h3>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full bg-sahool-600"></span>
                تشخيصات
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                ري
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full bg-red-500"></span>
                تنبيهات
              </span>
            </div>
          </div>
          <div className="h-64">
            <WeeklyActivityChart data={weeklyActivityData} />
          </div>
        </div>
      </div>

      {/* Third Row - Crop Distribution and Quick Stats */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Crop Distribution Pie Chart */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">
            {t('dashboard.charts.crops')}
          </h3>
          <div className="h-48">
            <CropDistributionChart data={cropDistributionData} />
          </div>
        </div>

        {/* Quick Performance Metrics */}
        <div className="lg:col-span-2 bg-gradient-to-br from-sahool-600 to-sahool-700 p-6 rounded-xl shadow-sm text-white">
          <h3 className="font-bold mb-4">أداء المنصة اليوم</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
              <Users className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-2xl font-bold">
                {platformMetrics?.activeFarmers?.toLocaleString() || '—'}
              </p>
              <p className="text-xs opacity-80">مزارع نشط</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
              <DollarSign className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-2xl font-bold">
                {platformMetrics?.dailySales
                  ? `$${(platformMetrics.dailySales / 1000).toFixed(0)}K`
                  : '—'}
              </p>
              <p className="text-xs opacity-80">مبيعات اليوم</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
              <Droplets className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-2xl font-bold">
                {platformMetrics?.irrigationOps?.toLocaleString() || '—'}
              </p>
              <p className="text-xs opacity-80">عملية ري</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
              <Sun className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-2xl font-bold">
                {platformMetrics?.avgTemperature ? `${platformMetrics.avgTemperature}°` : '—'}
              </p>
              <p className="text-xs opacity-80">متوسط الحرارة</p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-white/20">
            <div className="flex items-center justify-between text-sm">
              <span className="opacity-80">نسبة النمو الشهري</span>
              <span className="font-bold text-green-300">
                {platformMetrics?.monthlyGrowthRate
                  ? `+${platformMetrics.monthlyGrowthRate}%`
                  : '—'}
              </span>
            </div>
            <div className="mt-2 h-2 bg-white/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-400 rounded-full"
                style={{ width: `${Math.min(platformMetrics?.monthlyGrowthRate || 0, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Map and Recent Activity */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Farms Map */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
            <h2 className="font-bold text-gray-900 dark:text-gray-100">خريطة المزارع</h2>
            <Link
              href="/farms"
              className="text-sm text-sahool-600 hover:text-sahool-700 font-medium"
            >
              عرض الكل ←
            </Link>
          </div>
          <div className="h-[400px]">
            <FarmsMap
              farms={farms}
              onFarmClick={handleFarmClick}
              selectedFarmId={selectedFarm?.id}
              showHealthOverlay={true}
              className="h-full"
            />
          </div>
        </div>

        {/* Recent Diagnoses */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
            <h2 className="font-bold text-gray-900 dark:text-gray-100">أحدث التشخيصات</h2>
            <Link
              href="/diseases"
              className="text-sm text-sahool-600 hover:text-sahool-700 font-medium"
            >
              عرض الكل ←
            </Link>
          </div>
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {recentDiagnoses.length === 0 ? (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                لا توجد تشخيصات حديثة
              </div>
            ) : (
              recentDiagnoses.map((diagnosis) => (
                <div
                  key={diagnosis.id}
                  className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
                      <Bug className="w-6 h-6 text-gray-400 dark:text-gray-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 dark:text-gray-100 truncate">
                        {diagnosis.diseaseNameAr}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                        {diagnosis.farmName}
                      </p>
                      <div className="mt-1 flex items-center gap-2">
                        <AlertBadge severity={diagnosis.severity} />
                        <span className="text-xs text-gray-400 dark:text-gray-500">
                          {formatDate(diagnosis.diagnosedAt)}
                        </span>
                      </div>
                    </div>
                    <div className="text-left">
                      <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
                        {diagnosis.confidence.toFixed(0)}%
                      </span>
                      <p className="text-xs text-gray-500 dark:text-gray-400">دقة</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Cross-Farm Dashboard — لوحة مقارنة المزارع */}
      <div className="mt-8">
        <CrossFarmDashboard
          fields={farms.map((farm) => ({
            id: farm.id,
            name: farm.name,
            nameAr: farm.nameAr || farm.name,
            cropType: farm.crops?.[0] || '—',
            areaHa: farm.area,
            ndvi: 0,
            healthScore: farm.healthScore,
            diseaseRisk: farm.healthScore >= 70 ? 'low' as const : farm.healthScore >= 40 ? 'medium' as const : 'high' as const,
          }))}
          onFieldClick={(fieldId) => {
            const farm = farms.find((f) => f.id === fieldId);
            if (farm) setSelectedFarm(farm);
          }}
        />
      </div>

      {/* Expert View — نظرة خبير */}
      {(selectedFarm || farms.length > 0) && (
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-gray-900 dark:text-gray-100">
              نظرة خبير — {selectedFarm?.nameAr || farms[0]?.nameAr || farms[0]?.name}
            </h2>
          </div>
          <ExpertView
            fieldId={selectedFarm?.id || farms[0]?.id}
            cropType={selectedFarm?.crops?.[0] || farms[0]?.crops?.[0] || '—'}
            temperature={platformMetrics?.avgTemperature}
            soilMoisture={undefined}
            diseaseRisk={
              (selectedFarm?.healthScore ?? farms[0]?.healthScore ?? 70) >= 70
                ? 'low'
                : (selectedFarm?.healthScore ?? farms[0]?.healthScore ?? 70) >= 40
                  ? 'medium'
                  : 'high'
            }
          />
        </div>
      )}

      {/* Selected Farm Detail (if any) */}
      {selectedFarm && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-lg text-gray-900 dark:text-gray-100">
              {selectedFarm.nameAr}
            </h2>
            <button
              onClick={() => setSelectedFarm(null)}
              className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">المحافظة</p>
              <p className="font-medium dark:text-gray-200">{selectedFarm.governorate}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">المساحة</p>
              <p className="font-medium dark:text-gray-200">{selectedFarm.area.toFixed(1)} هكتار</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">المحاصيل</p>
              <p className="font-medium dark:text-gray-200">{selectedFarm.crops.join(', ')}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">مستوى الصحة</p>
              <p className="font-bold text-sahool-600">{selectedFarm.healthScore}%</p>
            </div>
          </div>
          <div className="mt-4 flex gap-3">
            <Link
              href={`/farms/${selectedFarm.id}`}
              className="px-4 py-2 bg-sahool-600 text-white rounded-lg text-sm font-medium hover:bg-sahool-700 transition-colors"
            >
              عرض التفاصيل
            </Link>
            <Link
              href={`/diseases?farmId=${selectedFarm.id}`}
              className="px-4 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              عرض التشخيصات
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
