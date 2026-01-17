"use client";

/**
 * SAHOOL Action Recommendation Card Component
 * مكون بطاقة توصية العمل
 *
 * Displays individual action recommendations with one-click task creation
 */

import React, { useState } from "react";
import {
  Sprout,
  Droplet,
  FlaskConical,
  AlertCircle,
  CheckCircle2,
  Clock,
  TrendingUp,
  Plus,
  Loader2,
} from "lucide-react";
import type {
  ActionRecommendation as ActionRecommendationType,
  ActionType,
} from "../types/action-windows";
import { WeatherConditions } from "./WeatherConditions";

interface ActionRecommendationProps {
  recommendation: ActionRecommendationType;
  onCreateTask?: (recommendation: ActionRecommendationType) => Promise<void>;
  showWeather?: boolean;
  compact?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

const getActionIcon = (actionType: ActionType) => {
  const iconClass = "w-5 h-5";

  switch (actionType) {
    case "spray":
      return <Sprout className={iconClass} aria-hidden="true" />;
    case "irrigate":
      return <Droplet className={iconClass} aria-hidden="true" />;
    case "fertilize":
      return <FlaskConical className={iconClass} aria-hidden="true" />;
    case "plant":
      return <Sprout className={iconClass} aria-hidden="true" />;
    case "harvest":
      return <CheckCircle2 className={iconClass} aria-hidden="true" />;
    default:
      return <AlertCircle className={iconClass} aria-hidden="true" />;
  }
};

const getActionLabel = (actionType: ActionType): { en: string; ar: string } => {
  switch (actionType) {
    case "spray":
      return { en: "Spray", ar: "رش" };
    case "irrigate":
      return { en: "Irrigate", ar: "ري" };
    case "fertilize":
      return { en: "Fertilize", ar: "تسميد" };
    case "plant":
      return { en: "Plant", ar: "زراعة" };
    case "harvest":
      return { en: "Harvest", ar: "حصاد" };
    default:
      return { en: "Action", ar: "عمل" };
  }
};

const getPriorityColor = (priority: ActionRecommendationType["priority"]) => {
  switch (priority) {
    case "urgent":
      return "bg-red-100 text-red-800 border-red-300";
    case "high":
      return "bg-orange-100 text-orange-800 border-orange-300";
    case "medium":
      return "bg-yellow-100 text-yellow-800 border-yellow-300";
    case "low":
      return "bg-blue-100 text-blue-800 border-blue-300";
    default:
      return "bg-gray-100 text-gray-800 border-gray-300";
  }
};

const getPriorityLabel = (
  priority: ActionRecommendationType["priority"],
): { en: string; ar: string } => {
  switch (priority) {
    case "urgent":
      return { en: "Urgent", ar: "عاجل" };
    case "high":
      return { en: "High", ar: "عالي" };
    case "medium":
      return { en: "Medium", ar: "متوسط" };
    case "low":
      return { en: "Low", ar: "منخفض" };
    default:
      return { en: "Normal", ar: "عادي" };
  }
};

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString("ar-EG", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────

export const ActionRecommendation = React.memo<ActionRecommendationProps>(
  ({ recommendation, onCreateTask, showWeather = false, compact = false }) => {
    const [isCreatingTask, setIsCreatingTask] = useState(false);
    const [taskCreated, setTaskCreated] = useState(false);

    const actionLabel = getActionLabel(recommendation.actionType);
    const priorityLabel = getPriorityLabel(recommendation.priority);

    const handleCreateTask = async () => {
      if (!onCreateTask || isCreatingTask || taskCreated) return;

      setIsCreatingTask(true);
      try {
        await onCreateTask(recommendation);
        setTaskCreated(true);
      } catch (error) {
        console.error("Failed to create task:", error);
      } finally {
        setIsCreatingTask(false);
      }
    };

    if (compact) {
      return (
        <div
          className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
          role="article"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3 flex-1">
              <div
                className={`p-2 rounded-lg ${getPriorityColor(recommendation.priority).replace("text-", "bg-").replace("-800", "-100")}`}
              >
                {getActionIcon(recommendation.actionType)}
              </div>

              <div className="flex-1" dir="rtl">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-gray-900">
                    {recommendation.titleAr}
                  </h3>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs border ${getPriorityColor(recommendation.priority)}`}
                  >
                    {priorityLabel.ar}
                  </span>
                </div>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {recommendation.descriptionAr}
                </p>
                <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                  <Clock className="w-3 h-3" aria-hidden="true" />
                  <span>{formatDateTime(recommendation.window.startTime)}</span>
                </div>
              </div>
            </div>

            {onCreateTask && (
              <button
                onClick={handleCreateTask}
                disabled={isCreatingTask || taskCreated}
                className={`
                px-4 py-2 rounded-lg font-medium text-sm transition-colors whitespace-nowrap
                ${
                  taskCreated
                    ? "bg-green-100 text-green-700 border border-green-300 cursor-not-allowed"
                    : "bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800"
                }
              `}
                aria-label={taskCreated ? "تم إنشاء المهمة" : "إنشاء مهمة"}
              >
                {isCreatingTask ? (
                  <Loader2
                    className="w-4 h-4 animate-spin"
                    aria-hidden="true"
                  />
                ) : taskCreated ? (
                  <CheckCircle2 className="w-4 h-4" aria-hidden="true" />
                ) : (
                  <Plus className="w-4 h-4" aria-hidden="true" />
                )}
              </button>
            )}
          </div>
        </div>
      );
    }

    return (
      <div
        className="bg-white rounded-xl border-2 border-gray-200 p-6 hover:shadow-lg transition-shadow"
        role="article"
        aria-labelledby={`recommendation-title-${recommendation.id}`}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-3">
            <div
              className={`p-3 rounded-xl ${getPriorityColor(recommendation.priority).replace("text-", "bg-").replace("-800", "-100")}`}
            >
              {getActionIcon(recommendation.actionType)}
            </div>

            <div dir="rtl">
              <div className="flex items-center gap-2 mb-1">
                <h3
                  id={`recommendation-title-${recommendation.id}`}
                  className="text-xl font-bold text-gray-900"
                >
                  {recommendation.titleAr}
                </h3>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(recommendation.priority)}`}
                >
                  {priorityLabel.ar}
                </span>
              </div>
              <p className="text-sm text-gray-500">{actionLabel.ar}</p>
            </div>
          </div>

          {/* Confidence Score */}
          <div className="text-right">
            <div className="flex items-center gap-1">
              <TrendingUp
                className="w-4 h-4 text-green-600"
                aria-hidden="true"
              />
              <span className="text-2xl font-bold text-green-600">
                {Math.round(recommendation.confidence)}%
              </span>
            </div>
            <p className="text-xs text-gray-500" dir="rtl">
              الثقة
            </p>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-700 mb-4" dir="rtl">
          {recommendation.descriptionAr}
        </p>

        {/* Window Information */}
        <div
          className="bg-blue-50 rounded-lg border border-blue-200 p-4 mb-4"
          dir="rtl"
        >
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-blue-600" aria-hidden="true" />
            <span className="font-semibold text-blue-900">
              النافذة الموصى بها
            </span>
            {recommendation.window.optimal && (
              <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs border border-green-300">
                مثالي
              </span>
            )}
          </div>
          <div className="space-y-1 text-sm text-blue-800">
            <p>
              <span className="font-medium">البداية:</span>{" "}
              {formatDateTime(recommendation.window.startTime)}
            </p>
            <p>
              <span className="font-medium">النهاية:</span>{" "}
              {formatDateTime(recommendation.window.endTime)}
            </p>
          </div>
        </div>

        {/* Reason */}
        <div className="mb-4">
          <h4 className="font-semibold text-gray-900 mb-2" dir="rtl">
            السبب
          </h4>
          <p className="text-sm text-gray-700" dir="rtl">
            {recommendation.reasonAr}
          </p>
        </div>

        {/* Benefits */}
        {recommendation.benefitsAr && recommendation.benefitsAr.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold text-gray-900 mb-2" dir="rtl">
              الفوائد
            </h4>
            <ul className="space-y-1">
              {recommendation.benefitsAr.map((benefit, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 text-sm text-gray-700"
                  dir="rtl"
                >
                  <CheckCircle2
                    className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0"
                    aria-hidden="true"
                  />
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Warnings */}
        {recommendation.warningsAr && recommendation.warningsAr.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold text-gray-900 mb-2" dir="rtl">
              تحذيرات
            </h4>
            <ul className="space-y-1">
              {recommendation.warningsAr.map((warning, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 text-sm text-orange-700"
                  dir="rtl"
                >
                  <AlertCircle
                    className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0"
                    aria-hidden="true"
                  />
                  <span>{warning}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Weather Conditions */}
        {showWeather && (
          <div className="mb-4">
            <h4 className="font-semibold text-gray-900 mb-3" dir="rtl">
              الظروف الجوية
            </h4>
            <WeatherConditions conditions={recommendation.conditions} compact />
          </div>
        )}

        {/* Action Button */}
        {onCreateTask && (
          <button
            onClick={handleCreateTask}
            disabled={isCreatingTask || taskCreated}
            className={`
            w-full px-6 py-3 rounded-lg font-semibold transition-all duration-200
            flex items-center justify-center gap-2
            ${
              taskCreated
                ? "bg-green-100 text-green-700 border-2 border-green-300 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 hover:shadow-lg"
            }
          `}
            aria-label={
              taskCreated
                ? "تم إنشاء المهمة بنجاح"
                : "إنشاء مهمة من هذه التوصية"
            }
          >
            {isCreatingTask ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
                <span dir="rtl">جاري الإنشاء...</span>
              </>
            ) : taskCreated ? (
              <>
                <CheckCircle2 className="w-5 h-5" aria-hidden="true" />
                <span dir="rtl">تم إنشاء المهمة</span>
              </>
            ) : (
              <>
                <Plus className="w-5 h-5" aria-hidden="true" />
                <span dir="rtl">إنشاء مهمة</span>
              </>
            )}
          </button>
        )}

        {/* Footer */}
        <div
          className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500"
          dir="rtl"
        >
          <span>ينتهي في: {formatDateTime(recommendation.expiresAt)}</span>
          {recommendation.fieldNameAr && (
            <span>الحقل: {recommendation.fieldNameAr}</span>
          )}
        </div>
      </div>
    );
  },
);

ActionRecommendation.displayName = "ActionRecommendation";

export default ActionRecommendation;
