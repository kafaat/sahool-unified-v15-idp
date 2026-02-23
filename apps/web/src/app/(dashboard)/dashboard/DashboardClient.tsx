"use client";

/**
 * SAHOOL Dashboard Home Page Client Component
 * الصفحة الرئيسية للوحة التحكم
 *
 * Uses Suspense boundaries for progressive loading - the page shell renders
 * immediately while each data-dependent section loads independently.
 */

import React, { Suspense } from "react";
import { useAuth } from "@/stores/auth.store";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import {
  DashboardStats,
  RecentActivity,
  WeatherWidget,
  TasksSummary,
  QuickActions,
} from "@/features/home";

// ═══════════════════════════════════════════════════════════════════════════
// Loading Skeletons - lightweight placeholders for progressive rendering
// ═══════════════════════════════════════════════════════════════════════════

const StatsLoadingSkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    {[0, 1, 2, 3].map((i) => (
      <div
        key={i}
        className="bg-white rounded-xl border-2 border-gray-200 p-6 animate-pulse"
      >
        <div className="flex items-start justify-between">
          <div className="h-12 w-12 bg-gray-200 rounded-lg" />
          <div className="h-4 w-10 bg-gray-200 rounded" />
        </div>
        <div className="mt-4 space-y-2">
          <div className="h-3 w-24 bg-gray-200 rounded" />
          <div className="h-3 w-16 bg-gray-100 rounded" />
          <div className="h-8 w-20 bg-gray-200 rounded mt-2" />
        </div>
      </div>
    ))}
  </div>
);

const ActivityLoadingSkeleton = () => (
  <div className="space-y-3">
    {[0, 1, 2, 3, 4].map((i) => (
      <div key={i} className="flex items-start gap-4 p-4 animate-pulse">
        <div className="h-10 w-10 bg-gray-200 rounded-lg flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-4 w-3/4 bg-gray-200 rounded" />
          <div className="h-3 w-1/2 bg-gray-100 rounded" />
          <div className="h-3 w-24 bg-gray-100 rounded" />
        </div>
      </div>
    ))}
  </div>
);

const QuickActionsLoadingSkeleton = () => (
  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
    {[0, 1, 2, 3, 4, 5].map((i) => (
      <div
        key={i}
        className="flex flex-col items-center justify-center p-6 rounded-xl border-2 border-gray-200 animate-pulse"
      >
        <div className="h-12 w-12 bg-gray-200 rounded-full mb-3" />
        <div className="h-4 w-16 bg-gray-200 rounded" />
        <div className="h-3 w-12 bg-gray-100 rounded mt-1" />
      </div>
    ))}
  </div>
);

const WeatherLoadingSkeleton = () => (
  <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-200 p-6 animate-pulse">
    <div className="flex items-center justify-between mb-4">
      <div className="h-5 w-24 bg-blue-200 rounded" />
      <div className="h-3 w-20 bg-blue-100 rounded" />
    </div>
    <div className="flex items-center gap-4 mb-6">
      <div className="h-12 w-12 bg-blue-200 rounded-lg" />
      <div className="space-y-2">
        <div className="h-10 w-20 bg-blue-200 rounded" />
        <div className="h-3 w-16 bg-blue-100 rounded" />
      </div>
    </div>
    <div className="grid grid-cols-2 gap-4">
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 bg-blue-200 rounded" />
        <div className="space-y-1">
          <div className="h-3 w-12 bg-blue-100 rounded" />
          <div className="h-4 w-10 bg-blue-200 rounded" />
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 bg-blue-200 rounded" />
        <div className="space-y-1">
          <div className="h-3 w-12 bg-blue-100 rounded" />
          <div className="h-4 w-16 bg-blue-200 rounded" />
        </div>
      </div>
    </div>
  </div>
);

const TasksLoadingSkeleton = () => (
  <div className="space-y-3">
    {[0, 1, 2, 3].map((i) => (
      <div key={i} className="flex items-start gap-3 p-3 animate-pulse">
        <div className="h-5 w-5 bg-gray-200 rounded-full mt-1 flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-4 w-3/4 bg-gray-200 rounded" />
          <div className="flex items-center gap-2">
            <div className="h-5 w-14 bg-gray-200 rounded-full" />
            <div className="h-3 w-20 bg-gray-100 rounded" />
          </div>
        </div>
      </div>
    ))}
  </div>
);

// ═══════════════════════════════════════════════════════════════════════════
// Error Fallback components
// ═══════════════════════════════════════════════════════════════════════════

const StatsFallback = () => (
  <div className="bg-red-50 rounded-xl p-6 text-center border-2 border-red-200">
    <p className="text-red-600 mt-2">فشل تحميل الإحصائيات</p>
    <p className="text-red-400 text-sm">Failed to load statistics</p>
    <button
      onClick={() => window.location.reload()}
      className="mt-3 px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200"
    >
      إعادة المحاولة
    </button>
  </div>
);

const ActivityFallback = () => (
  <div className="bg-yellow-50 rounded-xl p-4 text-center">
    <p className="text-yellow-700 text-sm mt-1">فشل تحميل النشاطات</p>
  </div>
);

const WeatherFallback = () => (
  <div className="bg-blue-50 rounded-xl p-4 text-center">
    <p className="text-blue-700 text-sm mt-1">فشل تحميل الطقس</p>
  </div>
);

const TasksFallback = () => (
  <div className="text-gray-500 text-center py-4">فشل تحميل المهام</div>
);

const QuickActionsFallback = () => (
  <div className="text-gray-500 text-center py-4">فشل تحميل الإجراءات</div>
);

// ═══════════════════════════════════════════════════════════════════════════
// Main Dashboard Component
// ═══════════════════════════════════════════════════════════════════════════

export default function DashboardClient() {
  const { user } = useAuth();

  return (
    <div className="space-y-6" role="main" aria-label="لوحة التحكم الرئيسية">
      {/* Welcome Section - renders immediately (no data dependency) */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h1 className="text-3xl font-bold text-gray-900">
          مرحباً، {user?.name_ar || user?.name || "المستخدم"}
        </h1>
        <p className="text-gray-600 mt-1">
          Welcome back to SAHOOL Agricultural Management Platform
        </p>
      </div>

      {/* Dashboard Stats - independent data fetch via useStats + useWeather */}
      <ErrorBoundary fallback={<StatsFallback />}>
        <Suspense fallback={<StatsLoadingSkeleton />}>
          <DashboardStats />
        </Suspense>
      </ErrorBoundary>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Activity - independent data fetch via useRecentActivity */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              النشاط الأخير
            </h2>
            <p className="text-sm text-gray-600 mb-4">Recent Activity</p>
            <ErrorBoundary fallback={<ActivityFallback />}>
              <Suspense fallback={<ActivityLoadingSkeleton />}>
                <RecentActivity />
              </Suspense>
            </ErrorBoundary>
          </div>

          {/* Quick Actions - static content, no data fetch needed */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              إجراءات سريعة
            </h2>
            <p className="text-sm text-gray-600 mb-4">Quick Actions</p>
            <ErrorBoundary fallback={<QuickActionsFallback />}>
              <Suspense fallback={<QuickActionsLoadingSkeleton />}>
                <QuickActions />
              </Suspense>
            </ErrorBoundary>
          </div>
        </div>

        {/* Right Column - 1/3 width */}
        <div className="space-y-6">
          {/* Weather Widget - independent data fetch via useWeather */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">الطقس</h2>
            <p className="text-sm text-gray-600 mb-4">Weather</p>
            <ErrorBoundary fallback={<WeatherFallback />}>
              <Suspense fallback={<WeatherLoadingSkeleton />}>
                <WeatherWidget />
              </Suspense>
            </ErrorBoundary>
          </div>

          {/* Tasks Summary - independent data fetch via useUpcomingTasks */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              المهام القادمة
            </h2>
            <p className="text-sm text-gray-600 mb-4">Upcoming Tasks</p>
            <ErrorBoundary fallback={<TasksFallback />}>
              <Suspense fallback={<TasksLoadingSkeleton />}>
                <TasksSummary />
              </Suspense>
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </div>
  );
}
