'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { SkeletonCard } from './ui/Skeleton';

interface Stats {
  totalFields: number;
  totalArea: number;
  healthScore: number;
  pendingTasks: number;
  completedTasks: number;
  activeAlerts: number;
  temperature: number;
  weatherCondition: string;
  waterUsage: number;
  waterSaving: number;
}

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: string;
  subtitle?: string;
  color?: string;
  progress?: number;
}

function StatsCard({ title, value, icon, subtitle, color = 'text-gray-800', progress }: StatsCardProps) {
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm transition-transform hover:scale-[1.02]">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-gray-500">{title}</p>
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
      {progress !== undefined && (
        <div className="mt-2 h-1.5 rounded-full overflow-hidden bg-gray-100">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${progress}%`,
              backgroundColor: progress >= 70 ? '#10b981' : progress >= 50 ? '#f59e0b' : '#ef4444'
            }}
          />
        </div>
      )}
      {subtitle && (
        <p className="text-xs mt-2 text-gray-500">{subtitle}</p>
      )}
    </div>
  );
}

interface StatsCardsProps {
  tenantId?: string;
}

export function StatsCards({ tenantId }: StatsCardsProps) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);

        // Try to fetch from API
        if (tenantId) {
          const [ndviSummary, weatherData] = await Promise.all([
            apiClient.getNdviSummary(tenantId).catch(() => null),
            apiClient.getWeather(15.37, 44.19).catch(() => null), // Sanaa coordinates
          ]);

          if (ndviSummary?.success) {
            setStats({
              totalFields: ndviSummary.data?.totalFields || 0,
              totalArea: ndviSummary.data?.totalAreaHectares || 0,
              healthScore: Math.round((ndviSummary.data?.averageHealth || 0) * 100),
              pendingTasks: 8, // TODO: Fetch from task service
              completedTasks: 4,
              activeAlerts: 3,
              temperature: weatherData?.data?.current?.temperature || 32,
              weatherCondition: weatherData?.data?.current?.description || 'مشمس',
              waterUsage: 85,
              waterSaving: 15,
            });
            setError(null);
            return;
          }
        }

        // Fallback to demo data
        await new Promise(resolve => setTimeout(resolve, 500));
        setStats({
          totalFields: 4,
          totalArea: 29.5,
          healthScore: 72,
          pendingTasks: 8,
          completedTasks: 4,
          activeAlerts: 3,
          temperature: 32,
          weatherCondition: 'مشمس',
          waterUsage: 85,
          waterSaving: 15,
        });
        setError(null);
      } catch (err) {
        setError('فشل تحميل الإحصائيات');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [tenantId]);

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-xl p-4 text-center">
        <p className="text-red-500">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-2 px-4 py-2 text-sm rounded-lg bg-red-500 text-white hover:bg-red-600"
        >
          إعادة المحاولة
        </button>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <StatsCard
        title="الحقول"
        value={stats.totalFields}
        icon="🌱"
        subtitle={`${stats.totalArea} هكتار`}
      />

      <StatsCard
        title="صحة المحاصيل"
        value={`${stats.healthScore}%`}
        icon="💚"
        progress={stats.healthScore}
        color={stats.healthScore >= 70 ? 'text-emerald-600' : stats.healthScore >= 50 ? 'text-amber-600' : 'text-red-600'}
      />

      <StatsCard
        title="مهام معلقة"
        value={stats.pendingTasks}
        icon="📋"
        subtitle={`✓ ${stats.completedTasks} مكتملة اليوم`}
        color="text-blue-600"
      />

      <StatsCard
        title="تنبيهات نشطة"
        value={stats.activeAlerts}
        icon={stats.activeAlerts > 0 ? '🔔' : '✅'}
        subtitle={stats.activeAlerts > 0 ? 'تحتاج مراجعة' : 'لا توجد تنبيهات'}
        color={stats.activeAlerts > 0 ? 'text-red-600' : 'text-gray-500'}
      />

      <StatsCard
        title="الطقس اليوم"
        value={`${stats.temperature}°`}
        icon="☀️"
        subtitle={`صنعاء - ${stats.weatherCondition}`}
        color="text-cyan-600"
      />

      <StatsCard
        title="استهلاك المياه"
        value={`${stats.waterUsage}%`}
        icon="💧"
        subtitle={`↓ ${stats.waterSaving}% توفير`}
        color="text-blue-600"
      />
    </div>
  );
}

export default StatsCards;
