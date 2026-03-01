"use client";

import React, { useEffect, useState, useMemo, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { SkeletonCard } from "./ui/Skeleton";
import { logger } from "@/lib/logger";

// Constants for health thresholds
const HEALTH_THRESHOLDS = {
  GOOD: 70,
  MODERATE: 50,
} as const;

const HEALTH_COLORS = {
  GOOD: "#10b981",
  MODERATE: "#f59e0b",
  POOR: "#ef4444",
} as const;

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

// Memoized StatsCard component to prevent unnecessary re-renders
const StatsCard = React.memo<StatsCardProps>(function StatsCard({
  title,
  value,
  icon,
  subtitle,
  color = "text-gray-800",
  progress,
}) {
  // Memoize the progress bar color calculation
  const progressColor = useMemo(() => {
    if (progress === undefined) return undefined;
    if (progress >= HEALTH_THRESHOLDS.GOOD) return HEALTH_COLORS.GOOD;
    if (progress >= HEALTH_THRESHOLDS.MODERATE) return HEALTH_COLORS.MODERATE;
    return HEALTH_COLORS.POOR;
  }, [progress]);

  // Create accessible progress description
  const progressDescription = useMemo(() => {
    if (progress === undefined) return "";
    if (progress >= HEALTH_THRESHOLDS.GOOD) return "ممتاز";
    if (progress >= HEALTH_THRESHOLDS.MODERATE) return "جيد";
    return "يحتاج تحسين";
  }, [progress]);

  return (
    <article
      className="bg-white rounded-xl p-4 shadow-sm transition-transform hover:scale-[1.02] focus-within:ring-2 focus-within:ring-blue-500 focus-within:outline-none"
      role="article"
      aria-label={`${title}: ${value}${progress !== undefined ? `, ${progressDescription}` : ""}`}
         >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h3
            className="text-xs text-gray-500 font-medium"
            id={`stat-title-${title}`}
          >
            {title}
          </h3>
          <p
            className={`text-2xl font-bold ${color} mt-1`}
            aria-describedby={`stat-title-${title}`}
          >
            {value}
          </p>
        </div>
        <span className="text-3xl mr-3" role="img" aria-label={title}>
          {icon}
        </span>
      </div>
      {progress !== undefined && (
        <div className="mt-3">
          <div
            className="h-1.5 rounded-full overflow-hidden bg-gray-100"
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`${title}: ${progress}% - ${progressDescription}`}
          >
            <div
              className="h-full rounded-full transition-all duration-500 ease-out"
              style={{
                width: `${progress}%`,
                backgroundColor: progressColor,
              }}
            />
          </div>
          <span className="sr-only">{progressDescription}</span>
        </div>
      )}
      {subtitle && (
        <p className="text-xs mt-2 text-gray-600" role="note">
          {subtitle}
        </p>
      )}
    </article>
  );
});

interface StatsCardsProps {
  tenantId?: string;
}

export const StatsCards = React.memo<StatsCardsProps>(function StatsCards({
  tenantId,
}) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retrying, setRetrying] = useState(false);

  // Memoized fetch function
  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

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
            healthScore: Math.round(
              (ndviSummary.data?.averageHealth || 0) * 100,
            ),
            pendingTasks: 8,
            completedTasks: 4,
            activeAlerts: 3,
            temperature: weatherData?.data?.current?.temperature || 32,
            weatherCondition: weatherData?.data?.current?.description || "مشمس",
            waterUsage: 85,
            waterSaving: 15,
          });
          setError(null);
          return;
        }
      }

      // Fallback to demo data
      await new Promise((resolve) => setTimeout(resolve, 500));
      setStats({
        totalFields: 4,
        totalArea: 29.5,
        healthScore: 72,
        pendingTasks: 8,
        completedTasks: 4,
        activeAlerts: 3,
        temperature: 32,
        weatherCondition: "مشمس",
        waterUsage: 85,
        waterSaving: 15,
      });
      setError(null);
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? `خطأ في تحميل البيانات: ${err.message}`
          : "فشل تحميل الإحصائيات. يرجى المحاولة مرة أخرى.";
      setError(errorMessage);
      logger.error("Error fetching stats:", err);
    } finally {
      setLoading(false);
      setRetrying(false);
    }
  }, [tenantId]);

  // Handle retry with loading state
  const handleRetry = useCallback(() => {
    setRetrying(true);
    fetchStats();
  }, [fetchStats]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (loading) {
    return (
      <section
        className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4"
        aria-busy="true"
        aria-label="جاري تحميل الإحصائيات"
             >
        {[...Array(6)].map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </section>
    );
  }

  if (error) {
    return (
      <section
        className="bg-red-50 border border-red-200 rounded-xl p-6 text-center"
        role="alert"
        aria-live="assertive"
             >
        <div className="flex flex-col items-center gap-3">
          <span className="text-4xl" role="img" aria-label="خطأ">
            ⚠️
          </span>
          <p className="text-red-700 font-medium text-sm">{error}</p>
          <button
            type="button"
            onClick={handleRetry}
            disabled={retrying}
            className="mt-2 px-6 py-2.5 text-sm font-medium rounded-lg bg-red-500 text-white hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            aria-label="إعادة محاولة تحميل الإحصائيات"
          >
            {retrying ? (
              <span className="flex items-center gap-2">
                <svg
                  className="animate-spin h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                جاري إعادة المحاولة...
              </span>
            ) : (
              "🔄 إعادة المحاولة"
            )}
          </button>
        </div>
      </section>
    );
  }

  if (!stats) {
    return (
      <section
        className="bg-gray-50 border border-gray-200 rounded-xl p-6 text-center"
        role="status"
        aria-live="polite"
             >
        <p className="text-gray-500 text-sm">لا توجد بيانات متاحة</p>
      </section>
    );
  }

  return (
    <section
      className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4"
      role="region"
      aria-label="إحصائيات لوحة التحكم"
      aria-live="polite"
         >
      <StatsCard
        title="إجمالي الحقول"
        value={stats.totalFields}
        icon="🌱"
        subtitle={`المساحة: ${stats.totalArea.toFixed(1)} هكتار`}
      />

      <StatsCard
        title="صحة المحاصيل"
        value={`${stats.healthScore}%`}
        icon="💚"
        progress={stats.healthScore}
        color={
          stats.healthScore >= 70
            ? "text-emerald-600"
            : stats.healthScore >= 50
              ? "text-amber-600"
              : "text-red-600"
        }
      />

      <StatsCard
        title="المهام المعلقة"
        value={stats.pendingTasks}
        icon="📋"
        subtitle={`✓ ${stats.completedTasks} مهمة مكتملة اليوم`}
        color="text-blue-600"
      />

      <StatsCard
        title="التنبيهات النشطة"
        value={stats.activeAlerts}
        icon={stats.activeAlerts > 0 ? "🔔" : "✅"}
        subtitle={
          stats.activeAlerts > 0 ? "تحتاج إلى مراجعة" : "لا توجد تنبيهات"
        }
        color={stats.activeAlerts > 0 ? "text-red-600" : "text-emerald-600"}
      />

      <StatsCard
        title="حالة الطقس"
        value={`${stats.temperature}°س`}
        icon="☀️"
        subtitle={`صنعاء - ${stats.weatherCondition}`}
        color="text-cyan-600"
      />

      <StatsCard
        title="استهلاك المياه"
        value={`${stats.waterUsage}%`}
        icon="💧"
        subtitle={`↓ توفير ${stats.waterSaving}% من المياه`}
        color="text-blue-600"
      />
    </section>
  );
});

export default StatsCards;
