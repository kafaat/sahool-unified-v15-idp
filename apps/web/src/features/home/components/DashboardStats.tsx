"use client";

/**
 * SAHOOL Dashboard Stats Component
 * مكون إحصائيات لوحة التحكم
 */

import React from "react";
import { BarChart3, Droplets, MapPin, AlertTriangle } from "lucide-react";
import { useDashboardData } from "../hooks/useDashboardData";

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  labelAr: string;
  value: string | number;
  trend?: number;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({
  icon,
  label,
  labelAr,
  value,
  trend,
  color,
}) => {
  return (
    <div
      className={`p-6 rounded-xl border-2 ${color} bg-white hover:shadow-lg transition-shadow`}
    >
      <div className="flex items-start justify-between">
        <div className={`p-3 rounded-lg ${color} bg-opacity-10`}>{icon}</div>
        {trend !== undefined && (
          <div
            className={`text-sm font-medium ${trend >= 0 ? "text-green-600" : "text-red-600"}`}
          >
            {trend >= 0 ? "+" : ""}
            {trend}%
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-sm text-gray-600">{labelAr}</p>
        <p className="text-xs text-gray-400">{label}</p>
        <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
      </div>
    </div>
  );
};

export const DashboardStats: React.FC = () => {
  const { data, isLoading } = useDashboardData();

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
      value: data?.stats?.totalFields || 0,
      trend: 5,
      color: "border-blue-200",
    },
    {
      icon: <BarChart3 className="w-6 h-6 text-green-600" />,
      label: "Active Tasks",
      labelAr: "المهام النشطة",
      value: data?.stats?.activeTasks || 0,
      trend: -2,
      color: "border-green-200",
    },
    {
      icon: <AlertTriangle className="w-6 h-6 text-orange-600" />,
      label: "Alerts",
      labelAr: "التنبيهات",
      value: data?.stats?.activeAlerts || 0,
      color: "border-orange-200",
    },
    {
      icon: <Droplets className="w-6 h-6 text-cyan-600" />,
      label: "Avg Humidity",
      labelAr: "متوسط الرطوبة",
      value: data?.weather?.humidity ? `${data.weather.humidity}%` : "N/A",
      color: "border-cyan-200",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </div>
  );
};

export default DashboardStats;
