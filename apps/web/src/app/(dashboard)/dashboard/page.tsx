'use client';

/**
 * SAHOOL Dashboard Home Page
 * الصفحة الرئيسية للوحة التحكم
 */

import React from 'react';
import { useAuth } from '@/stores/auth.store';
import {
  DashboardStats,
  RecentActivity,
  WeatherWidget,
  TasksSummary,
  QuickActions,
} from '@/features/home';

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h1 className="text-3xl font-bold text-gray-900">
          مرحباً، {user?.name_ar || user?.name}
        </h1>
        <p className="text-gray-600 mt-1">
          Welcome back to SAHOOL Agricultural Management Platform
        </p>
      </div>

      {/* Dashboard Stats */}
      <DashboardStats />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Activity */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">النشاط الأخير</h2>
            <p className="text-sm text-gray-600 mb-4">Recent Activity</p>
            <RecentActivity />
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">إجراءات سريعة</h2>
            <p className="text-sm text-gray-600 mb-4">Quick Actions</p>
            <QuickActions />
          </div>
        </div>

        {/* Right Column - 1/3 width */}
        <div className="space-y-6">
          {/* Weather Widget */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">الطقس</h2>
            <p className="text-sm text-gray-600 mb-4">Weather</p>
            <WeatherWidget />
          </div>

          {/* Tasks Summary */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">المهام القادمة</h2>
            <p className="text-sm text-gray-600 mb-4">Upcoming Tasks</p>
            <TasksSummary />
          </div>
        </div>
      </div>
    </div>
  );
}
