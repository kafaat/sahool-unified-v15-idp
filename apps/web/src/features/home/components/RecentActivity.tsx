'use client';

/**
 * SAHOOL Recent Activity Component
 * مكون النشاط الأخير
 */

import React from 'react';
import { Activity, Clock, ClipboardList, AlertTriangle, Sprout, CloudSun } from 'lucide-react';
import Link from 'next/link';
import { useRecentActivity } from '../hooks/useRecentActivity';

interface ActivityItem {
  id: string;
  type: 'task' | 'alert' | 'field' | 'weather';
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  timestamp: string;
}

const activityConfig: Record<
  string,
  { icon: React.ReactNode; color: string; darkColor: string; href: string }
> = {
  task: {
    icon: <ClipboardList className="w-4 h-4" />,
    color: 'bg-blue-100 text-blue-600',
    darkColor: 'dark:bg-blue-900/40 dark:text-blue-400',
    href: '/tasks',
  },
  alert: {
    icon: <AlertTriangle className="w-4 h-4" />,
    color: 'bg-red-100 text-red-600',
    darkColor: 'dark:bg-red-900/40 dark:text-red-400',
    href: '/alerts',
  },
  field: {
    icon: <Sprout className="w-4 h-4" />,
    color: 'bg-green-100 text-green-600',
    darkColor: 'dark:bg-green-900/40 dark:text-green-400',
    href: '/fields',
  },
  weather: {
    icon: <CloudSun className="w-4 h-4" />,
    color: 'bg-cyan-100 text-cyan-600',
    darkColor: 'dark:bg-cyan-900/40 dark:text-cyan-400',
    href: '/weather',
  },
};

const ActivityItemComponent: React.FC<{
  activity: ActivityItem;
  index: number;
}> = ({ activity, index }) => {
  const config = activityConfig[activity.type] || activityConfig.task;

  return (
    <Link
      // nosemgrep: react-href-var -- href is sourced from hardcoded `activityConfig` object, not user input
      href={config!.href}
      className="flex items-start gap-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-colors group cursor-pointer animate-slide-in-up"
      style={{
        animationDelay: `${index * 50}ms`,
        animationFillMode: 'both',
      }}
    >
      <div
        className={`p-2 rounded-lg ${config!.color} ${config!.darkColor} flex-shrink-0 transition-transform group-hover:scale-110`}
      >
        {config!.icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
          {activity.titleAr}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
          {activity.descriptionAr}
        </p>
        <div className="flex items-center gap-1 mt-1 text-xs text-gray-400 dark:text-gray-500">
          <Clock className="w-3 h-3" />
          <span>{new Date(activity.timestamp).toLocaleString('ar-EG')}</span>
        </div>
      </div>
      <div className="opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 dark:text-gray-500 self-center">
        <svg
          className="w-4 h-4 rtl:rotate-180"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </Link>
  );
};

export const RecentActivity: React.FC = () => {
  const { data: activityData, isLoading } = useRecentActivity({ limit: 10 });

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-6 transition-colors">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">النشاط الأخير</h3>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const activities: ActivityItem[] = activityData || [];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-6 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">النشاط الأخير</h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">Recent Activity</span>
      </div>

      {activities.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <Activity className="w-12 h-12 mx-auto mb-2 opacity-20" />
          <p>لا يوجد نشاط حديث</p>
          <p className="text-sm">No recent activity</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {activities.slice(0, 10).map((activity, index) => (
            <ActivityItemComponent key={activity.id} activity={activity} index={index} />
          ))}
        </div>
      )}
    </div>
  );
};

export default RecentActivity;
