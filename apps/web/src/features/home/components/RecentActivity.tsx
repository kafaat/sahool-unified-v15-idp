"use client";

/**
 * SAHOOL Recent Activity Component
 * مكون النشاط الأخير
 *
 * Performance optimizations:
 * - React.memo prevents re-renders when props don't change
 * - useMemo memoizes computed values
 */

import React, { useMemo } from "react";
import { Activity, Clock } from "lucide-react";
import { useDashboardData } from "../hooks/useDashboardData";

interface ActivityItem {
  id: string;
  type: "task" | "alert" | "field" | "weather";
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  timestamp: string;
}

const activityIcons: Record<string, { icon: React.ReactNode; color: string }> =
  {
    task: {
      icon: <Activity className="w-4 h-4" />,
      color: "bg-blue-100 text-blue-600",
    },
    alert: {
      icon: <Activity className="w-4 h-4" />,
      color: "bg-red-100 text-red-600",
    },
    field: {
      icon: <Activity className="w-4 h-4" />,
      color: "bg-green-100 text-green-600",
    },
    weather: {
      icon: <Activity className="w-4 h-4" />,
      color: "bg-cyan-100 text-cyan-600",
    },
  };

// Memoized activity item component to prevent unnecessary re-renders in lists
const ActivityItemComponent = React.memo<{ activity: ActivityItem }>(
  function ActivityItemComponent({ activity }) {
    const iconConfig = activityIcons[activity.type] || activityIcons.task;

    // Memoize formatted date to prevent recalculation
    const formattedDate = useMemo(
      () => new Date(activity.timestamp).toLocaleString("ar-EG"),
      [activity.timestamp]
    );

    return (
      <div className="flex items-start gap-4 p-4 hover:bg-gray-50 rounded-lg transition-colors">
        <div className={`p-2 rounded-lg ${iconConfig!.color} flex-shrink-0`}>
          {iconConfig!.icon}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900">{activity.titleAr}</p>
          <p className="text-sm text-gray-500 truncate">
            {activity.descriptionAr}
          </p>
          <div className="flex items-center gap-1 mt-1 text-xs text-gray-400">
            <Clock className="w-3 h-3" />
            <span>{formattedDate}</span>
          </div>
        </div>
      </div>
    );
  }
);

// Memoized RecentActivity component
export const RecentActivity = React.memo(function RecentActivity() {
  const { data, isLoading } = useDashboardData();

  // Memoize activities list
  const activities: ActivityItem[] = useMemo(
    () => data?.recentActivity || [],
    [data?.recentActivity]
  );

  // Memoize visible activities (limit to 10)
  const visibleActivities = useMemo(
    () => activities.slice(0, 10),
    [activities]
  );

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">النشاط الأخير</h3>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-20 bg-gray-100 rounded-lg animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">النشاط الأخير</h3>
        <span className="text-sm text-gray-500">Recent Activity</span>
      </div>

      {activities.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Activity className="w-12 h-12 mx-auto mb-2 opacity-20" />
          <p>لا يوجد نشاط حديث</p>
          <p className="text-sm">No recent activity</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {visibleActivities.map((activity) => (
            <ActivityItemComponent key={activity.id} activity={activity} />
          ))}
        </div>
      )}
    </div>
  );
});

RecentActivity.displayName = "RecentActivity";

export default RecentActivity;
