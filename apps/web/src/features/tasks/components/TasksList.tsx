"use client";

/**
 * SAHOOL Tasks List Component
 * مكون قائمة المهام
 */

import React from "react";
import { CheckCircle2, Clock, XCircle } from "lucide-react";
import { useTasks } from "../hooks/useTasks";
import { TaskCard } from "./TaskCard";
import type { TaskFilters } from "../types";

interface TasksListProps {
  filters?: TaskFilters;
  onTaskClick?: (taskId: string) => void;
}

export const TasksList: React.FC<TasksListProps> = ({
  filters,
  onTaskClick,
}) => {
  const { data: tasks, isLoading } = useTasks(filters);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-32 bg-gray-200 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div className="text-center py-16 bg-white rounded-xl border-2 border-gray-200">
        <Clock className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          لا توجد مهام
        </h3>
        <p className="text-gray-500">لا توجد مهام تطابق المعايير المحددة</p>
      </div>
    );
  }

  // Group tasks by status
  const groupedTasks = {
    open: tasks.filter((t) => t.status === "open" || t.status === "pending"),
    in_progress: tasks.filter((t) => t.status === "in_progress"),
    completed: tasks.filter((t) => t.status === "completed"),
    cancelled: tasks.filter((t) => t.status === "cancelled"),
  };

  return (
    <div className="space-y-6">
      {/* Pending Tasks */}
      {groupedTasks.open.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              قيد الانتظار ({groupedTasks.open.length})
            </h3>
          </div>
          <div className="space-y-3">
            {groupedTasks.open.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onClick={() => onTaskClick?.(task.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* In Progress Tasks */}
      {groupedTasks.in_progress.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              قيد التنفيذ ({groupedTasks.in_progress.length})
            </h3>
          </div>
          <div className="space-y-3">
            {groupedTasks.in_progress.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onClick={() => onTaskClick?.(task.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed Tasks */}
      {groupedTasks.completed.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              مكتملة ({groupedTasks.completed.length})
            </h3>
          </div>
          <div className="space-y-3">
            {groupedTasks.completed.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onClick={() => onTaskClick?.(task.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Cancelled Tasks */}
      {groupedTasks.cancelled.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <XCircle className="w-5 h-5 text-red-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              ملغاة ({groupedTasks.cancelled.length})
            </h3>
          </div>
          <div className="space-y-3">
            {groupedTasks.cancelled.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onClick={() => onTaskClick?.(task.id)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TasksList;
