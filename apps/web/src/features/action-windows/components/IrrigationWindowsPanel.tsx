"use client";

/**
 * SAHOOL Irrigation Windows Panel Component
 * مكون لوحة نوافذ الري
 *
 * Displays irrigation recommendations based on soil moisture and weather conditions
 */

import React, { useState, useMemo } from "react";
import {
  Droplets,
  TrendingDown,
  Calendar,
  AlertCircle,
  RefreshCw,
  Plus,
  Droplet,
  Thermometer,
  Wind,
  Clock,
} from "lucide-react";
import { useIrrigationWindows } from "../hooks/useActionWindows";
import { useCreateTask } from "@/features/tasks/hooks/useTasks";
import type { IrrigationWindow } from "../types/action-windows";
import type { TaskFormData } from "@/features/tasks/types";
import { WindowTimeline } from "./WindowTimeline";

interface IrrigationWindowsPanelProps {
  fieldId: string;
  days?: number;
  onCreateTask?: (window: IrrigationWindow) => void;
  showTimeline?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString("ar-EG", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString("ar-EG", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
};

const getPriorityBadge = (priority: IrrigationWindow["priority"]) => {
  switch (priority) {
    case "urgent":
      return (
        <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium border border-red-300">
          عاجل
        </span>
      );
    case "high":
      return (
        <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium border border-orange-300">
          عالي
        </span>
      );
    case "medium":
      return (
        <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium border border-yellow-300">
          متوسط
        </span>
      );
    case "low":
      return (
        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium border border-green-300">
          منخفض
        </span>
      );
  }
};

const getSoilMoistureStatusBadge = (
  status: IrrigationWindow["soilMoisture"]["status"],
) => {
  switch (status) {
    case "critical":
      return (
        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium">
          حرج
        </span>
      );
    case "low":
      return (
        <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs font-medium">
          منخفض
        </span>
      );
    case "optimal":
      return (
        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
          مثالي
        </span>
      );
    case "high":
      return (
        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
          عالي
        </span>
      );
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────

export const IrrigationWindowsPanel = React.memo<IrrigationWindowsPanelProps>(
  ({ fieldId, days = 7, onCreateTask, showTimeline = true }) => {
    const [selectedWindow, setSelectedWindow] =
      useState<IrrigationWindow | null>(null);
    const {
      data: windows,
      isLoading,
      error,
      refetch,
      isRefetching,
    } = useIrrigationWindows({
      fieldId,
      days,
    });

    const createTaskMutation = useCreateTask();

    // Filter to show urgent and high priority windows first
    const prioritizedWindows = useMemo(() => {
      if (!windows) return [];
      return [...windows].sort((a, b) => {
        const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
        return priorityOrder[a.priority] - priorityOrder[b.priority];
      });
    }, [windows]);

    // Convert windows to timeline blocks
    const timelineBlocks = useMemo(() => {
      if (!windows) return [];

      return windows.map((window) => ({
        id: window.id,
        startTime: window.startTime,
        endTime: window.endTime,
        status: window.status,
        score:
          window.priority === "urgent"
            ? 100
            : window.priority === "high"
              ? 80
              : window.priority === "medium"
                ? 60
                : 40,
        label: `Irrigation - ${window.duration}h`,
        labelAr: `ري - ${window.duration}س`,
        details: {
          temperature: window.weather.temperature,
          windSpeed: window.weather.windSpeed,
          humidity: window.weather.humidity,
          rainProbability: window.weather.rainProbability,
        },
        actionable: true,
      }));
    }, [windows]);

    const handleCreateTask = async (window: IrrigationWindow) => {
      if (onCreateTask) {
        onCreateTask(window);
        setSelectedWindow(null);
        return;
      }

      // Default task creation
      const taskData: TaskFormData = {
        title: `Irrigation - ${window.waterAmount}mm`,
        title_ar: `ري - ${window.waterAmount}ملم`,
        description: `${window.reason}\n\nSoil Moisture: ${window.soilMoisture.current.toFixed(1)}% (Target: ${window.soilMoisture.target.toFixed(1)}%)\nWater Amount: ${window.waterAmount}mm\nDuration: ${window.duration} hours`,
        description_ar: `${window.reasonAr}\n\nرطوبة التربة: ${window.soilMoisture.current.toFixed(1)}% (المستهدف: ${window.soilMoisture.target.toFixed(1)}%)\nكمية الماء: ${window.waterAmount}ملم\nالمدة: ${window.duration} ساعة`,
        due_date: window.startTime,
        priority:
          window.priority === "urgent" || window.priority === "high"
            ? "high"
            : "medium",
        field_id: fieldId,
        status: "open",
      };

      try {
        await createTaskMutation.mutateAsync(taskData);
        setSelectedWindow(null);
        // Optionally show success toast
      } catch (error) {
        // Optionally show error toast
        console.error("Failed to create irrigation task:", error);
      }
    };

    // Loading State
    if (isLoading) {
      return (
        <div
          className="bg-white rounded-xl border border-gray-200 p-8"
          role="status"
          aria-live="polite"
        >
          <div className="flex flex-col items-center justify-center space-y-4">
            <RefreshCw
              className="w-12 h-12 text-blue-600 animate-spin"
              aria-hidden="true"
            />
            <p className="text-gray-600" dir="rtl">
              جاري تحميل نوافذ الري...
            </p>
          </div>
        </div>
      );
    }

    // Error State
    if (error) {
      return (
        <div
          className="bg-white rounded-xl border border-red-200 p-8"
          role="alert"
        >
          <div className="flex flex-col items-center justify-center space-y-4">
            <AlertCircle
              className="w-12 h-12 text-red-500"
              aria-hidden="true"
            />
            <div className="text-center">
              <p className="text-red-700 font-medium mb-2" dir="rtl">
                حدث خطأ أثناء تحميل نوافذ الري
              </p>
              <p className="text-sm text-red-600 mb-4" dir="ltr">
                {error.message}
              </p>
              <button
                onClick={() => refetch()}
                disabled={isRefetching}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <RefreshCw
                  className={`w-4 h-4 inline mr-2 ${isRefetching ? "animate-spin" : ""}`}
                  aria-hidden="true"
                />
                <span dir="rtl">إعادة المحاولة</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    // No Windows Available
    if (!windows || windows.length === 0) {
      return (
        <div
          className="bg-white rounded-xl border border-gray-200 p-8"
          role="status"
        >
          <div className="flex flex-col items-center justify-center space-y-4">
            <Droplets className="w-12 h-12 text-gray-400" aria-hidden="true" />
            <div className="text-center">
              <p className="text-gray-700 font-medium mb-2" dir="rtl">
                لا توجد نوافذ ري متاحة
              </p>
              <p className="text-sm text-gray-500" dir="rtl">
                تحقق من بيانات رطوبة التربة أو توقعات الطقس
              </p>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl border border-blue-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3" dir="rtl">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Droplets
                  className="w-6 h-6 text-blue-700"
                  aria-hidden="true"
                />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">نوافذ الري</h2>
                <p className="text-sm text-gray-600">
                  توصيات الري لـ {days} أيام
                </p>
              </div>
            </div>

            <button
              onClick={() => refetch()}
              disabled={isRefetching}
              className="p-2 text-blue-700 hover:bg-blue-100 rounded-lg transition-colors"
              aria-label="تحديث نوافذ الري"
            >
              <RefreshCw
                className={`w-5 h-5 ${isRefetching ? "animate-spin" : ""}`}
                aria-hidden="true"
              />
            </button>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-3 border border-blue-200">
              <p className="text-sm text-gray-600 mb-1" dir="rtl">
                إجمالي النوافذ
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {windows.length}
              </p>
            </div>
            <div className="bg-red-50 rounded-lg p-3 border border-red-300">
              <p className="text-sm text-red-700 mb-1" dir="rtl">
                عاجل
              </p>
              <p className="text-2xl font-bold text-red-700">
                {windows.filter((w) => w.priority === "urgent").length}
              </p>
            </div>
            <div className="bg-orange-50 rounded-lg p-3 border border-orange-300">
              <p className="text-sm text-orange-700 mb-1" dir="rtl">
                عالي
              </p>
              <p className="text-2xl font-bold text-orange-700">
                {windows.filter((w) => w.priority === "high").length}
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-3 border border-green-300">
              <p className="text-sm text-green-700 mb-1" dir="rtl">
                متوسط/منخفض
              </p>
              <p className="text-2xl font-bold text-green-700">
                {
                  windows.filter(
                    (w) => w.priority === "medium" || w.priority === "low",
                  ).length
                }
              </p>
            </div>
          </div>
        </div>

        {/* Timeline View */}
        {showTimeline && timelineBlocks.length > 0 && (
          <WindowTimeline
            timeline={timelineBlocks}
            onBlockClick={(block) => {
              const window = windows.find((w) => w.id === block.id);
              if (window) setSelectedWindow(window);
            }}
          />
        )}

        {/* Window Cards List */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900" dir="rtl">
            توصيات الري ({prioritizedWindows.length})
          </h3>

          {prioritizedWindows.map((window) => (
            <div
              key={window.id}
              className={`
              bg-white rounded-lg border-2 p-5 transition-all
              ${selectedWindow?.id === window.id ? "border-blue-500 shadow-lg" : "border-gray-200 hover:border-gray-300"}
            `}
              role="article"
            >
              {/* Window Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1" dir="rtl">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar
                      className="w-5 h-5 text-gray-500"
                      aria-hidden="true"
                    />
                    <span className="font-semibold text-gray-900">
                      {formatDate(window.date)}
                    </span>
                    {getPriorityBadge(window.priority)}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {formatDateTime(window.startTime)} -{" "}
                    {formatDateTime(window.endTime)}
                  </p>
                  <p className="text-sm text-gray-700 font-medium" dir="rtl">
                    كمية الماء: {window.waterAmount} ملم | المدة:{" "}
                    {window.duration} ساعة
                  </p>
                </div>

                {(window.priority === "urgent" ||
                  window.priority === "high") && (
                  <button
                    onClick={() => handleCreateTask(window)}
                    disabled={createTaskMutation.isPending}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2 disabled:opacity-50"
                    aria-label="إنشاء مهمة ري"
                  >
                    <Plus className="w-4 h-4" aria-hidden="true" />
                    <span dir="rtl">إنشاء مهمة</span>
                  </button>
                )}
              </div>

              {/* Soil Moisture Status */}
              <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 mb-4">
                <div
                  className="flex items-center justify-between mb-3"
                  dir="rtl"
                >
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <TrendingDown className="w-4 h-4" aria-hidden="true" />
                    حالة رطوبة التربة
                  </h4>
                  {getSoilMoistureStatusBadge(window.soilMoisture.status)}
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-gray-600 mb-1" dir="rtl">
                      الحالي
                    </p>
                    <p className="text-lg font-bold text-gray-900">
                      {window.soilMoisture.current.toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 mb-1" dir="rtl">
                      المستهدف
                    </p>
                    <p className="text-lg font-bold text-blue-600">
                      {window.soilMoisture.target.toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 mb-1" dir="rtl">
                      العجز
                    </p>
                    <p className="text-lg font-bold text-red-600">
                      {window.soilMoisture.deficit.toFixed(1)} ملم
                    </p>
                  </div>
                </div>

                {/* Moisture Progress Bar */}
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${
                        window.soilMoisture.status === "critical"
                          ? "bg-red-500"
                          : window.soilMoisture.status === "low"
                            ? "bg-orange-500"
                            : window.soilMoisture.status === "optimal"
                              ? "bg-green-500"
                              : "bg-blue-500"
                      }`}
                      style={{
                        width: `${(window.soilMoisture.current / window.soilMoisture.target) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* ET Data */}
              <div className="bg-blue-50 rounded-lg border border-blue-200 p-3 mb-4">
                <h4
                  className="font-medium text-blue-900 mb-2 text-sm"
                  dir="rtl"
                >
                  معدل التبخر والنتح (ET)
                </h4>
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div>
                    <p className="text-xs text-blue-700 mb-1" dir="rtl">
                      ET₀
                    </p>
                    <p className="font-semibold text-blue-900">
                      {window.et.et0.toFixed(2)} ملم/يوم
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-blue-700 mb-1" dir="rtl">
                      ETc
                    </p>
                    <p className="font-semibold text-blue-900">
                      {window.et.etc.toFixed(2)} ملم/يوم
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-blue-700 mb-1" dir="rtl">
                      Kc
                    </p>
                    <p className="font-semibold text-blue-900">
                      {window.et.kc.toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Weather Conditions */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="p-3 rounded-lg border bg-gray-50 border-gray-200">
                  <div className="flex items-center gap-2 mb-1">
                    <Thermometer
                      className="w-4 h-4 text-gray-600"
                      aria-hidden="true"
                    />
                    <span className="text-xs font-medium text-gray-700">
                      الحرارة
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {Math.round(window.weather.temperature)}°C
                  </p>
                </div>

                <div className="p-3 rounded-lg border bg-gray-50 border-gray-200">
                  <div className="flex items-center gap-2 mb-1">
                    <Wind
                      className="w-4 h-4 text-gray-600"
                      aria-hidden="true"
                    />
                    <span className="text-xs font-medium text-gray-700">
                      الرياح
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {window.weather.windSpeed} km/h
                  </p>
                </div>

                <div className="p-3 rounded-lg border bg-gray-50 border-gray-200">
                  <div className="flex items-center gap-2 mb-1">
                    <Droplet
                      className="w-4 h-4 text-gray-600"
                      aria-hidden="true"
                    />
                    <span className="text-xs font-medium text-gray-700">
                      الرطوبة
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {Math.round(window.weather.humidity)}%
                  </p>
                </div>

                <div className="p-3 rounded-lg border bg-gray-50 border-gray-200">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock
                      className="w-4 h-4 text-gray-600"
                      aria-hidden="true"
                    />
                    <span className="text-xs font-medium text-gray-700">
                      المطر
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {Math.round(window.weather.rainProbability)}%
                  </p>
                </div>
              </div>

              {/* Reason */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                <h4
                  className="font-medium text-yellow-900 mb-2 text-sm"
                  dir="rtl"
                >
                  السبب:
                </h4>
                <p className="text-sm text-yellow-800" dir="rtl">
                  {window.reasonAr}
                </p>
              </div>

              {/* Recommendations */}
              {window.recommendationsAr.length > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <h4
                    className="font-medium text-green-900 mb-2 text-sm"
                    dir="rtl"
                  >
                    توصيات:
                  </h4>
                  <ul className="space-y-1">
                    {window.recommendationsAr.map((rec, idx) => (
                      <li
                        key={idx}
                        className="text-sm text-green-800"
                        dir="rtl"
                      >
                        • {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  },
);

IrrigationWindowsPanel.displayName = "IrrigationWindowsPanel";

export default IrrigationWindowsPanel;
