"use client";

/**
 * SAHOOL Tasks Board Component (Kanban)
 * مكون لوحة المهام (كانبان)
 */

import React, { useMemo, useState } from "react";
import { useTasks, useUpdateTaskStatus } from "../hooks/useTasks";
import { TaskCard } from "./TaskCard";
import type { TaskBoardColumn, TaskStatus } from "../types";

interface TasksBoardProps {
  onTaskClick?: (taskId: string) => void;
}

const columns: TaskBoardColumn[] = [
  {
    id: "open",
    title: "Open",
    title_ar: "جديدة",
    tasks: [],
    color: "bg-gray-50 border-gray-200 dark:bg-gray-800 dark:border-gray-700",
  },
  {
    id: "in_progress",
    title: "In Progress",
    title_ar: "قيد التنفيذ",
    tasks: [],
    color: "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800",
  },
  {
    id: "completed",
    title: "Completed",
    title_ar: "مكتملة",
    tasks: [],
    color: "bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800",
  },
];

export const TasksBoard: React.FC<TasksBoardProps> = ({ onTaskClick }) => {
  const { data: tasks, isLoading, error } = useTasks();
  const updateStatus = useUpdateTaskStatus();

  // State for drag-drop visual feedback
  const [draggedTaskId, setDraggedTaskId] = useState<string | null>(null);
  const [dropTargetColumn, setDropTargetColumn] = useState<TaskStatus | null>(
    null,
  );

  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    e.dataTransfer.setData("taskId", taskId);
    e.dataTransfer.effectAllowed = "move";
    setDraggedTaskId(taskId);

    // Add ARIA attribute for accessibility
    const target = e.currentTarget as HTMLElement;
    target.setAttribute("aria-grabbed", "true");
  };

  const handleDragEnd = (e: React.DragEvent) => {
    setDraggedTaskId(null);
    setDropTargetColumn(null);

    // Reset ARIA attribute
    const target = e.currentTarget as HTMLElement;
    target.setAttribute("aria-grabbed", "false");
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  };

  const handleDragEnter = (status: TaskStatus) => {
    setDropTargetColumn(status);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    // Only clear if we're leaving the column entirely
    const relatedTarget = e.relatedTarget as HTMLElement;
    if (
      !relatedTarget ||
      !(e.currentTarget as HTMLElement).contains(relatedTarget)
    ) {
      setDropTargetColumn(null);
    }
  };

  const handleDrop = async (e: React.DragEvent, status: TaskStatus) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData("taskId");
    if (taskId) {
      await updateStatus.mutateAsync({ id: taskId, status });
    }
    setDraggedTaskId(null);
    setDropTargetColumn(null);
  };

  // Performance optimization: Memoize grouped tasks
  const boardColumns = useMemo(() => {
    if (!tasks) return columns.map((col) => ({ ...col, tasks: [] }));

    return columns.map((column) => ({
      ...column,
      tasks: tasks.filter((t) => t.status === column.id),
    }));
  }, [tasks]);

  // Improved loading state
  if (isLoading) {
    return (
      <div
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
        role="status"
        aria-label="Loading tasks board"
        aria-live="polite"
      >
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-4 min-h-[500px]"
          >
            {/* Column header skeleton */}
            <div className="mb-4 space-y-2">
              <div className="h-6 w-24 bg-gray-300 dark:bg-gray-600 rounded animate-pulse" />
              <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            </div>
            {/* Task cards skeleton */}
            <div className="space-y-3">
              {[...Array(3)].map((_, j) => (
                <div
                  key={j}
                  className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"
                  style={{ animationDelay: `${j * 100}ms` }}
                />
              ))}
            </div>
          </div>
        ))}
        <span className="sr-only">جاري تحميل لوحة المهام...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div
        className="flex flex-col items-center justify-center min-h-[500px] bg-red-50 dark:bg-red-900/20 rounded-xl border-2 border-red-200 dark:border-red-800 p-8"
        role="alert"
        aria-live="assertive"
      >
        <svg
          className="w-16 h-16 text-red-400 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <h3 className="text-lg font-semibold text-red-900 dark:text-red-200 mb-2">
          خطأ في تحميل المهام
        </h3>
        <p className="text-red-700 dark:text-red-300 text-center">Error loading tasks</p>
        <p className="text-sm text-red-600 dark:text-red-400 mt-2">
          {error.message || "An unknown error occurred"}
        </p>
      </div>
    );
  }

  // Empty state (no tasks at all)
  const totalTasks = boardColumns.reduce(
    (sum, col) => sum + col.tasks.length,
    0,
  );
  if (totalTasks === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center min-h-[500px] bg-gray-50 dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-8"
        role="status"
        aria-label="No tasks available"
      >
        <svg
          className="w-20 h-20 text-gray-300 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
        <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
          لا توجد مهام حتى الآن
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-center max-w-md">
          No tasks yet. Create your first task to get started!
        </p>
      </div>
    );
  }

  return (
    <div
      className="grid grid-cols-1 md:grid-cols-3 gap-6"
      role="region"
      aria-label="Tasks kanban board"
      dir="auto"
    >
      {boardColumns.map((column) => {
        const isDropTarget = dropTargetColumn === column.id;
        const hasTasksBeingDragged = draggedTaskId !== null;

        return (
          <div
            key={column.id}
            onDragOver={handleDragOver}
            onDragEnter={() => handleDragEnter(column.id)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, column.id)}
            className={`
              rounded-xl border-2 p-4 min-h-[500px] transition-all duration-200
              ${column.color}
              ${isDropTarget ? "ring-4 ring-blue-300 ring-opacity-50 scale-[1.02] shadow-lg" : ""}
              ${hasTasksBeingDragged && !isDropTarget ? "opacity-75" : ""}
            `}
            role="region"
            aria-label={`${column.title_ar} column with ${column.tasks.length} tasks`}
            aria-dropeffect="move"
          >
            {/* Column Header */}
            <div className="mb-4">
              <h3
                className="text-lg font-bold text-gray-900 dark:text-white"
                               lang="ar"
              >
                {column.title_ar}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400" dir="ltr" lang="en">
                {column.title}
              </p>
              <div className="mt-2 text-sm font-medium text-gray-600 dark:text-gray-400">
                <span lang="ar">
                  {column.tasks.length}{" "}
                  {column.tasks.length === 1 ? "مهمة" : "مهام"}
                </span>
              </div>
            </div>

            {/* Drop zone indicator - only rendered when active to avoid screen reader announcements */}
            {isDropTarget && (
              <div
                className="mb-3 p-3 border-2 border-dashed rounded-lg text-center transition-all duration-300 overflow-hidden max-h-24 opacity-100 border-blue-400 bg-blue-100 scale-100"
                role="status"
                aria-live="polite"
              >
                <p className="text-sm font-medium text-blue-700">
                  أفلت المهمة هنا
                </p>
                <p className="text-xs text-blue-600" dir="ltr">
                  Drop task here
                </p>
              </div>
            )}

            {/* Tasks */}
            <div className="space-y-3">
              {column.tasks.length === 0 ? (
                <div
                  className="text-center py-12 text-gray-400 dark:text-gray-500 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg"
                  role="status"
                  aria-label={`No tasks in ${column.title}`}
                >
                  <svg
                    className="w-12 h-12 mx-auto mb-3 text-gray-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                    />
                  </svg>
                  <p className="text-sm font-medium">
                    لا توجد مهام
                  </p>
                  <p className="text-xs mt-1" dir="ltr">
                    No tasks
                  </p>
                </div>
              ) : (
                column.tasks.map((task) => {
                  const isBeingDragged = draggedTaskId === task.id;

                  return (
                    <div
                      key={task.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, task.id)}
                      onDragEnd={handleDragEnd}
                      className={`
                        transition-all duration-300 ease-out cursor-grab active:cursor-grabbing
                        ${isBeingDragged ? "opacity-30 scale-90 rotate-2 shadow-none" : "opacity-100 scale-100 rotate-0 hover:shadow-md"}
                        ${!isBeingDragged && hasTasksBeingDragged ? "hover:scale-[1.02] hover:-translate-y-0.5" : "hover:-translate-y-0.5"}
                      `}
                      role="button"
                      aria-grabbed={isBeingDragged}
                      aria-label={`Task: ${task.title || "Untitled task"}. Draggable.`}
                      tabIndex={0}
                    >
                      <TaskCard
                        task={task}
                        onClick={() => onTaskClick?.(task.id)}
                        draggable
                      />
                    </div>
                  );
                })
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default TasksBoard;
