'use client';

/**
 * SAHOOL Dashboard Home Page Client Component
 * الصفحة الرئيسية للوحة التحكم
 */

import React, { Suspense } from 'react';
import { useAuth } from '@/stores/auth.store';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import {
  DashboardStats,
  RecentActivity,
  WeatherWidget,
  TasksSummary,
  QuickActions,
} from '@/features/home';

// Fallback components for error states
const StatsFallback = () => (
  <div className="bg-red-50 rounded-xl p-6 text-center border-2 border-red-200">
    <span className="text-4xl">📊</span>
    <p className="text-red-600 mt-2">فشل تحميل الإحصائيات</p>
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
    <span className="text-2xl">📋</span>
    <p className="text-yellow-700 text-sm mt-1">فشل تحميل النشاطات</p>
  </div>
);

const WeatherFallback = () => (
  <div className="bg-blue-50 rounded-xl p-4 text-center">
    <span className="text-2xl">🌤️</span>
    <p className="text-blue-700 text-sm mt-1">فشل تحميل الطقس</p>
  </div>
);

const LoadingSkeleton = () => (
  <div className="animate-pulse space-y-4">
    <div className="h-20 bg-gray-200 rounded-xl" />
    <div className="h-20 bg-gray-200 rounded-xl" />
  </div>
);

export default function DashboardClient() {
  const { user } = useAuth();

  return (
    <div className="space-y-6" role="main" aria-label="لوحة التحكم الرئيسية">
      {/* Welcome Section */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h1 className="text-3xl font-bold text-gray-900">
          مرحباً، {user?.name_ar || user?.name || 'المستخدم'}
        </h1>
        <p className="text-gray-600 mt-1">
          Welcome back to SAHOOL Agricultural Management Platform
        </p>
      </div>

      {/* Dashboard Stats - Protected with ErrorBoundary */}
      <ErrorBoundary fallback={<StatsFallback />}>
        <Suspense fallback={<LoadingSkeleton />}>
          <DashboardStats />
        </Suspense>
      </ErrorBoundary>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Activity - Protected with ErrorBoundary */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">النشاط الأخير</h2>
            <p className="text-sm text-gray-600 mb-4">Recent Activity</p>
            <ErrorBoundary fallback={<ActivityFallback />}>
              <RecentActivity />
            </ErrorBoundary>
          </div>

          {/* Quick Actions - Protected with ErrorBoundary */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">إجراءات سريعة</h2>
            <p className="text-sm text-gray-600 mb-4">Quick Actions</p>
            <ErrorBoundary fallback={<div className="text-gray-500 text-center py-4">فشل تحميل الإجراءات</div>}>
              <QuickActions />
            </ErrorBoundary>
          </div>
        </div>

        {/* Right Column - 1/3 width */}
        <div className="space-y-6">
          {/* Weather Widget - Protected with ErrorBoundary */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">الطقس</h2>
            <p className="text-sm text-gray-600 mb-4">Weather</p>
            <ErrorBoundary fallback={<WeatherFallback />}>
              <WeatherWidget />
            </ErrorBoundary>
          </div>

          {/* Tasks Summary - Protected with ErrorBoundary */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">المهام القادمة</h2>
            <p className="text-sm text-gray-600 mb-4">Upcoming Tasks</p>
            <ErrorBoundary fallback={<div className="text-gray-500 text-center py-4">فشل تحميل المهام</div>}>
              <TasksSummary />
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </div>
  );
}
