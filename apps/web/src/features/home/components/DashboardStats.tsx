"use client";

/**
 * SAHOOL Dashboard Stats Component
 * مكون إحصائيات لوحة التحكم
 */

import React, { useEffect, useState, useRef } from "react";
import { BarChart3, Droplets, MapPin, AlertTriangle, RefreshCw } from "lucide-react";
import { useStats } from "../hooks/useStats";
import { useWeather } from "../hooks/useWeather";

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  labelAr: string;
  value: string | number;
  trend?: number;
  color: string;
  index: number;
}

/**
 * Animated counter hook for smooth number transitions
 */
function useAnimatedValue(target: number, duration = 600): number {
  const [current, setCurrent] = useState(0);
  const prevRef = useRef(0);

  useEffect(() => {
    const start = prevRef.current;
    const diff = target - start;
    if (diff === 0) return;

    const startTime = performance.now();
    let rafId: number;

    const animate = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = Math.round(start + diff * eased);
      setCurrent(value);

      if (progress < 1) {
        rafId = requestAnimationFrame(animate);
      } else {
        prevRef.current = target;
      }
    };

    rafId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafId);
  }, [target, duration]);

  return current;
}

const StatCard: React.FC<StatCardProps> = ({
  icon,
  label,
  labelAr,
  value,
  trend,
  color,
  index,
}) => {
  const numericValue = typeof value === "number" ? value : null;
  const animatedValue = useAnimatedValue(numericValue ?? 0);
  const displayValue = numericValue !== null ? animatedValue : value;

  return (
    <div
      className={`p-6 rounded-xl border-2 ${color} bg-white hover:shadow-lg hover:-translate-y-1 transition-all duration-300 animate-slide-in-up cursor-default group`}
      style={{ animationDelay: `${index * 100}ms`, animationFillMode: "both" }}
    >
      <div className="flex items-start justify-between">
        <div className={`p-3 rounded-lg ${color} bg-opacity-10 group-hover:scale-110 transition-transform duration-200`}>
          {icon}
        </div>
        {trend !== undefined && (
          <div
            className={`flex items-center gap-1 text-sm font-medium px-2 py-1 rounded-full ${
              trend >= 0
                ? "text-green-700 bg-green-50"
                : "text-red-700 bg-red-50"
            }`}
          >
            <span className={trend >= 0 ? "rotate-0" : "rotate-180"}>&#9650;</span>
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-sm text-gray-600">{labelAr}</p>
        <p className="text-xs text-gray-400">{label}</p>
        <p className="text-3xl font-bold text-gray-900 mt-2 tabular-nums">
          {displayValue}
        </p>
      </div>
    </div>
  );
};

export const DashboardStats: React.FC = () => {
  const { data: statsData, isLoading: statsLoading, refetch: refetchStats } = useStats();
  const { data: weatherData, isLoading: weatherLoading, refetch: refetchWeather } = useWeather();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const isLoading = statsLoading || weatherLoading;

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await Promise.all([refetchStats(), refetchWeather()]);
    setIsRefreshing(false);
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-40 bg-gray-100 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  const stats = [
    {
      icon: <MapPin className="w-6 h-6 text-blue-600" />,
      label: "Total Fields",
      labelAr: "إجمالي الحقول",
      value: statsData?.totalFields || 0,
      trend: 5,
      color: "border-blue-200",
    },
    {
      icon: <BarChart3 className="w-6 h-6 text-green-600" />,
      label: "Active Tasks",
      labelAr: "المهام النشطة",
      value: statsData?.activeTasks || 0,
      trend: -2,
      color: "border-green-200",
    },
    {
      icon: <AlertTriangle className="w-6 h-6 text-orange-600" />,
      label: "Alerts",
      labelAr: "التنبيهات",
      value: statsData?.activeAlerts || 0,
      color: "border-orange-200",
    },
    {
      icon: <Droplets className="w-6 h-6 text-cyan-600" />,
      label: "Avg Humidity",
      labelAr: "متوسط الرطوبة",
      value: weatherData?.humidity ? `${weatherData.humidity}%` : "N/A",
      color: "border-cyan-200",
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-end">
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          aria-label="تحديث الإحصائيات"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
          <span className="text-xs">تحديث</span>
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatCard key={index} index={index} {...stat} />
        ))}
      </div>
    </div>
  );
};

export default DashboardStats;
