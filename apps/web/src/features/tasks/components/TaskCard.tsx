"use client";

/**
 * SAHOOL Task Card Component
 * مكون بطاقة المهمة
 */

import React from "react";
import {
  Calendar,
  MapPin,
  Flag,
  Clock,
  CheckCircle2,
  XCircle,
  Circle,
  AlertCircle,
} from "lucide-react";
import type { Task } from "../types";

interface TaskCardProps {
  task: Task;
  onClick?: () => void;
  draggable?: boolean;
}

const priorityConfig: Record<
  string,
  { colors: string; label: string; labelAr: string; icon: React.ReactNode }
> = {
  urgent: {
    colors:
      "bg-red-200 text-red-800 border-red-300 dark:bg-red-900 dark:text-red-100",
    label: "Urgent",
    labelAr: "عاجلة",
    icon: <Flag className="w-3 h-3" aria-hidden="true" />,
  },
  high: {
    colors:
      "bg-red-100 text-red-700 border-red-200 dark:bg-red-800 dark:text-red-100",
    label: "High",
    labelAr: "عالية",
    icon: <Flag className="w-3 h-3" aria-hidden="true" />,
  },
  medium: {
    colors:
      "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-800 dark:text-yellow-100",
    label: "Medium",
    labelAr: "متوسطة",
    icon: <Flag className="w-3 h-3" aria-hidden="true" />,
  },
  low: {
    colors:
      "bg-green-100 text-green-700 border-green-200 dark:bg-green-800 dark:text-green-100",
    label: "Low",
    labelAr: "منخفضة",
    icon: <Flag className="w-3 h-3" aria-hidden="true" />,
  },
};

const statusConfig: Record<
  string,
  { colors: string; label: string; labelAr: string; icon: React.ReactNode }
> = {
  open: {
    colors: "border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700",
    label: "Open",
    labelAr: "مفتوحة",
    icon: <Circle className="w-4 h-4 text-gray-400" aria-hidden="true" />,
  },
  pending: {
    colors: "border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700",
    label: "Pending",
    labelAr: "قيد الانتظار",
    icon: <Clock className="w-4 h-4 text-gray-400" aria-hidden="true" />,
  },
  in_progress: {
    colors:
      "border-blue-300 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-700",
    label: "In Progress",
    labelAr: "قيد التنفيذ",
    icon: <AlertCircle className="w-4 h-4 text-blue-600" aria-hidden="true" />,
  },
  completed: {
    colors:
      "border-green-300 bg-green-50 dark:bg-green-900/20 dark:border-green-700",
    label: "Completed",
    labelAr: "مكتملة",
    icon: (
      <CheckCircle2 className="w-4 h-4 text-green-600" aria-hidden="true" />
    ),
  },
  cancelled: {
    colors: "border-red-300 bg-red-50 dark:bg-red-900/20 dark:border-red-700",
    label: "Cancelled",
    labelAr: "ملغية",
    icon: <XCircle className="w-4 h-4 text-red-600" aria-hidden="true" />,
  },
};

export const TaskCard: React.FC<TaskCardProps> = React.memo(
  ({ task, onClick, draggable = false }) => {
    // Memoize computed values for performance
    const isOverdue = React.useMemo(() => {
      return task.due_date
        ? new Date(task.due_date) < new Date() && task.status !== "completed"
        : false;
    }, [task.due_date, task.status]);

    const priorityInfo = React.useMemo(() => {
      return priorityConfig[task.priority] || priorityConfig.low;
    }, [task.priority]);

    const statusInfo = React.useMemo(() => {
      return statusConfig[task.status] || statusConfig.open;
    }, [task.status]);

    const formattedDueDate = React.useMemo(() => {
      return task.due_date
        ? new Date(task.due_date).toLocaleDateString("ar-EG")
        : null;
    }, [task.due_date]);

    // Keyboard navigation handler
    const handleKeyDown = React.useCallback(
      (event: React.KeyboardEvent<HTMLDivElement>) => {
        if (onClick && (event.key === "Enter" || event.key === " ")) {
          event.preventDefault();
          onClick();
        }
      },
      [onClick],
    );

    // Generate accessible label
    const ariaLabel = React.useMemo(() => {
      const parts = [
        `Task: ${task.title}`,
        `Status: ${statusInfo!.labelAr}`,
        `Priority: ${priorityInfo!.labelAr}`,
      ];

      if (task.due_date) {
        parts.push(`Due date: ${formattedDueDate}`);
        if (isOverdue) {
          parts.push("Overdue");
        }
      }

      if (task.field_id) {
        parts.push(`Field: ${task.field_id}`);
      }

      return parts.join(", ");
    }, [
      task.title,
      task.due_date,
      task.field_id,
      statusInfo!.labelAr,
      priorityInfo!.labelAr,
      formattedDueDate,
      isOverdue,
    ]);

    return (
      <div
        role={onClick ? "button" : undefined}
        tabIndex={onClick ? 0 : undefined}
        onClick={onClick}
        onKeyDown={handleKeyDown}
        draggable={draggable}
        dir="rtl"
        aria-label={ariaLabel}
        aria-live="polite"
        className={`
        rounded-lg border-2 p-4 transition-all duration-200
        ${statusInfo!.colors}
        ${onClick ? "cursor-pointer" : ""}
        ${draggable ? "cursor-move" : ""}
        ${onClick ? "hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]" : ""}
        ${onClick ? "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" : ""}
        ${onClick ? "focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2" : ""}
      `}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-3 gap-2">
          <div className="flex items-center gap-2 flex-1">
            <h4 className="font-semibold text-gray-900 dark:text-gray-100">
              {task.title}
            </h4>
          </div>
          <div
            className={`px-2 py-1 rounded-full text-xs border flex items-center gap-1 shrink-0 ${priorityInfo!.colors}`}
            aria-label={`Priority: ${priorityInfo!.labelAr}`}
            role="status"
          >
            {priorityInfo!.icon}
            <span>{priorityInfo!.labelAr}</span>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-2 mb-3">
          <div
            className="flex items-center gap-1.5 text-xs font-medium"
            aria-label={`Status: ${statusInfo!.labelAr}`}
            role="status"
          >
            {statusInfo!.icon}
            <span className="text-gray-700 dark:text-gray-300">
              {statusInfo!.labelAr}
            </span>
          </div>
        </div>

        {/* Description */}
        {task.description && (
          <p
            className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2"
            aria-label={`Description: ${task.description}`}
          >
            {task.description}
          </p>
        )}

        {/* Meta Info */}
        <div className="space-y-2">
          {task.due_date && (
            <div
              className={`flex items-center gap-2 text-sm ${isOverdue ? "text-red-600 dark:text-red-400" : "text-gray-500 dark:text-gray-400"}`}
              aria-label={`Due date: ${formattedDueDate}${isOverdue ? " (Overdue)" : ""}`}
            >
              <Calendar className="w-4 h-4" aria-hidden="true" />
              <span>{formattedDueDate}</span>
              {isOverdue && (
                <span
                  className="text-xs bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100 px-2 py-0.5 rounded font-medium"
                  role="alert"
                  aria-label="This task is overdue"
                >
                  متأخر
                </span>
              )}
            </div>
          )}

          {task.field_id && (
            <div
              className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400"
              aria-label={`Field: ${task.field_id}`}
            >
              <MapPin className="w-4 h-4" aria-hidden="true" />
              <span>الحقل #{task.field_id}</span>
            </div>
          )}
        </div>
      </div>
    );
  },
);

TaskCard.displayName = "TaskCard";

export default TaskCard;
