"use client";

/**
 * SAHOOL Window Timeline Component
 * مكون الجدول الزمني للنوافذ
 *
 * Visual timeline showing optimal action windows over time
 */

import React, { useState, useMemo } from "react";
import { Calendar, Clock, TrendingUp } from "lucide-react";
import type {
  Timeline,
  TimelineBlock,
  WindowStatus,
} from "../types/action-windows";

interface WindowTimelineProps {
  timeline: Timeline | TimelineBlock[];
  onBlockClick?: (block: TimelineBlock) => void;
  showDetails?: boolean;
  height?: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

const getStatusColor = (status: WindowStatus): string => {
  switch (status) {
    case "optimal":
      return "bg-green-500 hover:bg-green-600 border-green-600";
    case "marginal":
      return "bg-yellow-500 hover:bg-yellow-600 border-yellow-600";
    case "avoid":
      return "bg-red-500 hover:bg-red-600 border-red-600";
    default:
      return "bg-gray-500 hover:bg-gray-600 border-gray-600";
  }
};

const getStatusLabel = (status: WindowStatus): { en: string; ar: string } => {
  switch (status) {
    case "optimal":
      return { en: "Optimal", ar: "مثالي" };
    case "marginal":
      return { en: "Marginal", ar: "هامشي" };
    case "avoid":
      return { en: "Avoid", ar: "تجنب" };
    default:
      return { en: "Unknown", ar: "غير معروف" };
  }
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString("ar-EG", { month: "short", day: "numeric" });
};

const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleTimeString("ar-EG", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────

export const WindowTimeline = React.memo<WindowTimelineProps>(
  ({ timeline, onBlockClick, showDetails = true, height = 200 }) => {
    const [selectedBlock, setSelectedBlock] = useState<TimelineBlock | null>(
      null,
    );

    // Extract blocks and summary
    const { blocks, summary } = useMemo(() => {
      if (Array.isArray(timeline)) {
        // If timeline is just an array of blocks
        return {
          blocks: timeline,
          summary: {
            totalWindows: timeline.length,
            optimalWindows: timeline.filter((b) => b.status === "optimal")
              .length,
            marginalWindows: timeline.filter((b) => b.status === "marginal")
              .length,
            avoidWindows: timeline.filter((b) => b.status === "avoid").length,
            bestWindowIndex: timeline.findIndex((b) => b.status === "optimal"),
          },
        };
      } else {
        return {
          blocks: timeline.blocks,
          summary: timeline.summary,
        };
      }
    }, [timeline]);

    const handleBlockClick = (block: TimelineBlock) => {
      setSelectedBlock(block);
      onBlockClick?.(block);
    };

    const handleBlockKeyPress = (
      event: React.KeyboardEvent,
      block: TimelineBlock,
    ) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        handleBlockClick(block);
      }
    };

    if (blocks.length === 0) {
      return (
        <div
          className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-8 text-center"
          role="status"
        >
          <Calendar
            className="w-12 h-12 mx-auto mb-3 text-gray-400"
            aria-hidden="true"
          />
          <p className="text-gray-600" dir="rtl">
            لا توجد نوافذ متاحة
          </p>
          <p className="text-sm text-gray-500 mt-1" dir="ltr">
            No windows available
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {/* Summary Stats */}
        {showDetails && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-white rounded-lg border border-gray-200 p-3">
              <p className="text-xs text-gray-600 mb-1" dir="rtl">
                إجمالي النوافذ
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {summary.totalWindows}
              </p>
            </div>

            <div className="bg-green-50 rounded-lg border border-green-200 p-3">
              <p className="text-xs text-green-700 mb-1" dir="rtl">
                مثالي
              </p>
              <p className="text-2xl font-bold text-green-700">
                {summary.optimalWindows}
              </p>
            </div>

            <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-3">
              <p className="text-xs text-yellow-700 mb-1" dir="rtl">
                هامشي
              </p>
              <p className="text-2xl font-bold text-yellow-700">
                {summary.marginalWindows}
              </p>
            </div>

            <div className="bg-red-50 rounded-lg border border-red-200 p-3">
              <p className="text-xs text-red-700 mb-1" dir="rtl">
                تجنب
              </p>
              <p className="text-2xl font-bold text-red-700">
                {summary.avoidWindows}
              </p>
            </div>
          </div>
        )}

        {/* Timeline Visualization */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3
            className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2"
            dir="rtl"
          >
            <TrendingUp className="w-4 h-4" aria-hidden="true" />
            الجدول الزمني للنوافذ
          </h3>

          <div
            className="relative space-y-2"
            style={{ minHeight: `${height}px` }}
            role="list"
            aria-label="Window timeline blocks"
          >
            {blocks.map((block) => {
              const statusLabel = getStatusLabel(block.status);
              const isSelected = selectedBlock?.id === block.id;

              return (
                <div
                  key={block.id}
                  role="listitem"
                  tabIndex={block.actionable ? 0 : -1}
                  onClick={() => block.actionable && handleBlockClick(block)}
                  onKeyPress={(e) =>
                    block.actionable && handleBlockKeyPress(e, block)
                  }
                  className={`
                  relative rounded-lg border-2 p-3 transition-all duration-200
                  ${getStatusColor(block.status)}
                  ${block.actionable ? "cursor-pointer" : "opacity-50 cursor-not-allowed"}
                  ${isSelected ? "ring-4 ring-blue-300 scale-105" : ""}
                  text-white
                `}
                  aria-label={`${statusLabel.ar}: ${block.labelAr} من ${formatTime(block.startTime)} إلى ${formatTime(block.endTime)}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1" dir="rtl">
                      <div className="flex items-center gap-2 mb-1">
                        <Clock className="w-4 h-4" aria-hidden="true" />
                        <span className="font-semibold text-sm">
                          {formatDate(block.startTime)} -{" "}
                          {formatTime(block.startTime)}
                        </span>
                      </div>
                      <p className="text-sm opacity-90">{block.labelAr}</p>
                    </div>

                    <div className="text-right">
                      <p className="text-2xl font-bold">
                        {Math.round(block.score)}
                      </p>
                      <p className="text-xs opacity-75">{statusLabel.ar}</p>
                    </div>
                  </div>

                  {/* Expand details on hover/select */}
                  {(isSelected || showDetails) && (
                    <div className="mt-3 pt-3 border-t border-white/20">
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="opacity-75">الحرارة:</span>{" "}
                          <span className="font-medium">
                            {Math.round(block.details.temperature)}°C
                          </span>
                        </div>
                        <div>
                          <span className="opacity-75">الرياح:</span>{" "}
                          <span className="font-medium">
                            {block.details.windSpeed} km/h
                          </span>
                        </div>
                        <div>
                          <span className="opacity-75">الرطوبة:</span>{" "}
                          <span className="font-medium">
                            {Math.round(block.details.humidity)}%
                          </span>
                        </div>
                        <div>
                          <span className="opacity-75">المطر:</span>{" "}
                          <span className="font-medium">
                            {Math.round(block.details.rainProbability)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Block Details */}
        {selectedBlock && (
          <div
            className="bg-blue-50 rounded-lg border border-blue-200 p-4"
            dir="rtl"
          >
            <h4 className="font-semibold text-blue-900 mb-2">
              تفاصيل النافذة المحددة
            </h4>
            <div className="space-y-2 text-sm text-blue-800">
              <p>
                <span className="font-medium">الوقت:</span>{" "}
                {formatTime(selectedBlock.startTime)} -{" "}
                {formatTime(selectedBlock.endTime)}
              </p>
              <p>
                <span className="font-medium">الحالة:</span>{" "}
                {selectedBlock.labelAr}
              </p>
              <p>
                <span className="font-medium">النتيجة:</span>{" "}
                {Math.round(selectedBlock.score)}/100
              </p>
              {selectedBlock.actionable && (
                <button
                  className="mt-3 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  onClick={() => {
                    // Handle task creation
                    console.log("Create task for window:", selectedBlock);
                  }}
                >
                  إنشاء مهمة
                </button>
              )}
            </div>
          </div>
        )}

        {/* Legend */}
        <div
          className="flex items-center justify-center gap-6 text-sm"
          dir="rtl"
        >
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span className="text-gray-700">مثالي</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-500 rounded"></div>
            <span className="text-gray-700">هامشي</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded"></div>
            <span className="text-gray-700">تجنب</span>
          </div>
        </div>
      </div>
    );
  },
);

WindowTimeline.displayName = "WindowTimeline";

export default WindowTimeline;
