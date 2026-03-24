"use client";

import React, { useMemo, useCallback } from "react";
import type { Task } from "@/lib/api/types";

interface TaskCardProps {
  task: Task;
  onComplete?: (taskId: string) => void;
  onSelect?: (taskId: string) => void;
}

const STATUS_LABELS: Record<string, string> = {
  pending: "معلقة",
  in_progress: "قيد التنفيذ",
  completed: "مكتملة",
  cancelled: "ملغاة",
};

const PRIORITY_LABELS: Record<string, string> = {
  low: "منخفضة",
  medium: "متوسطة",
  high: "عالية",
  urgent: "عاجلة",
};

const PRIORITY_ICONS: Record<string, string> = {
  low: "🔵",
  medium: "🟡",
  high: "🔴",
  urgent: "🚨",
};

// Memoized TaskCard component
const TaskCard = React.memo<TaskCardProps>(function TaskCard({
  task,
  onComplete,
  onSelect,
}) {
  // Memoized derived values
  const isCompleted = useMemo(
    () => task.status === "completed" || task.status === "cancelled",
    [task.status],
  );

  const dueDate = useMemo(
    () => (task.due_date ? new Date(task.due_date) : null),
    [task.due_date],
  );

  const isOverdue = useMemo(
    () => dueDate && dueDate < new Date() && !isCompleted,
    [dueDate, isCompleted],
  );

  // Memoized handlers
  const handleClick = useCallback(() => {
    onSelect?.(task.id);
  }, [task.id, onSelect]);

  const handleComplete = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onComplete?.(task.id);
    },
    [task.id, onComplete],
  );

  // Memoized class names
  const cardClassName = useMemo(() => {
    const baseClasses =
      "p-3 rounded-lg border transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-emerald-500";
    const stateClasses = isCompleted
      ? "bg-gray-50 opacity-60"
      : "bg-white hover:shadow-md";
    const priorityClasses =
      {
        high: "border-e-4 border-e-red-400",
        medium: "border-e-4 border-e-yellow-400",
        low: "border-e-4 border-e-blue-400",
        urgent: "border-e-4 border-e-purple-500",
      }[task.priority] || "";

    return `${baseClasses} ${stateClasses} ${priorityClasses}`;
  }, [isCompleted, task.priority]);

  return (
    <div
      onClick={handleClick}
      onKeyDown={(e) => e.key === "Enter" && handleClick()}
      tabIndex={0}
      role="button"
      aria-label={`مهمة: ${task.title} - الحالة: ${STATUS_LABELS[task.status]} - الأولوية: ${PRIORITY_LABELS[task.priority]}`}
      className={cardClassName}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">{PRIORITY_ICONS[task.priority]}</span>
          <h4
            className={`font-medium text-sm ${isCompleted ? "line-through text-gray-400" : "text-gray-800"}`}
          >
            {task.title}
          </h4>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${
            task.status === "completed"
              ? "bg-green-100 text-green-700"
              : task.status === "in_progress"
                ? "bg-blue-100 text-blue-700"
                : task.status === "cancelled"
                  ? "bg-gray-100 text-gray-500"
                  : "bg-amber-100 text-amber-700"
          }`}
        >
          {STATUS_LABELS[task.status]}
        </span>
      </div>

      {/* Description */}
      {task.description && (
        <p className="text-xs text-gray-500 mt-2 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Meta */}
      <div className="flex items-center justify-between mt-3 text-xs text-gray-400">
        <div className="flex items-center gap-3">
          {/* Due date */}
          {dueDate && (
            <span
              className={`flex items-center gap-1 ${isOverdue ? "text-red-500" : ""}`}
            >
              📅
              {dueDate.toLocaleDateString("ar-YE", {
                month: "short",
                day: "numeric",
              })}
              {isOverdue && <span className="text-red-500">متأخرة</span>}
            </span>
          )}

          {/* Assigned to */}
          {task.assigneeName && (
            <span className="flex items-center gap-1">
              👤 {task.assigneeName}
            </span>
          )}

          {/* Field */}
          {task.fieldName && (
            <span className="flex items-center gap-1">🌱 {task.fieldName}</span>
          )}
        </div>

        {/* Complete button */}
        {!isCompleted && (
          <button
            onClick={handleComplete}
            aria-label={`إنهاء مهمة: ${task.title}`}
            className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            ✓ إنهاء
          </button>
        )}
      </div>
    </div>
  );
});

export { TaskCard };
export default TaskCard;
