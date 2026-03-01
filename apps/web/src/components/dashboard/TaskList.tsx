"use client";

import React, { useEffect, useState, useMemo, useCallback } from "react";
import { apiClient } from "@/lib/api";
import type { Task } from "@/lib/api/types";
import { TaskCard } from "./TaskCard";
import { SkeletonTaskItem } from "./ui/Skeleton";
import { logger } from "@/lib/logger";

interface TaskListProps {
  tenantId?: string;
  fieldId?: string | null;
  limit?: number;
}

export function TaskList({ tenantId, fieldId, limit = 10 }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<"all" | "pending" | "completed">("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTasks = async () => {
      setLoading(true);
      try {
        const response = await apiClient.getTasks({
          tenantId,
          fieldId: fieldId || undefined,
          limit,
          offset: 0,
        });

        if (response.success && response.data) {
          setTasks(response.data);
        }
      } catch (error) {
        logger.error("Failed to fetch tasks:", error);
        // Fallback to demo data
        setTasks([
          {
            id: "task_001",
            title: "ري الطماطم - الصباح",
            description: "ري الحقل الشمالي لمدة 30 دقيقة",
            field_id: "field_001",
            fieldName: "حقل الطماطم",
            status: "pending",
            priority: "high",
            taskType: "irrigation",
            due_date: new Date().toISOString(),
            assigneeName: "أحمد",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: "task_002",
            title: "رش مبيدات وقائية",
            description: "رش مبيد فطري للوقاية من البياض الدقيقي",
            field_id: "field_001",
            fieldName: "حقل الطماطم",
            status: "in_progress",
            priority: "medium",
            taskType: "pesticide",
            due_date: new Date(Date.now() + 86400000).toISOString(),
            assigneeName: "محمد",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: "task_003",
            title: "فحص مرض صدأ البن",
            description: "فحص ميداني للكشف عن علامات مرض صدأ الأوراق",
            field_id: "field_002",
            fieldName: "حقل البن",
            status: "pending",
            priority: "high",
            taskType: "inspection",
            due_date: new Date().toISOString(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: "task_004",
            title: "حصاد الموز الناضج",
            description: "جمع العناقيد الناضجة من الصف 1-5",
            field_id: "field_004",
            fieldName: "حقل الموز",
            status: "completed",
            priority: "medium",
            taskType: "harvest",
            completed_at: new Date().toISOString(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [tenantId, fieldId, limit]);

  // Memoized handleComplete with useCallback
  const handleComplete = useCallback(async (taskId: string) => {
    // Update local state optimistically
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId
          ? {
              ...t,
              status: "completed" as const,
              completed_at: new Date().toISOString(),
            }
          : t,
      ),
    );

    try {
      await apiClient.updateTask(taskId, { status: "completed" });
    } catch {
      // Revert on failure - log to error tracking instead of console
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId
            ? { ...t, status: "pending" as const, completed_at: undefined }
            : t,
        ),
      );
    }
  }, []);

  // Memoized filtered tasks to prevent recalculation on every render
  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      if (filter === "pending")
        return task.status === "pending" || task.status === "in_progress";
      if (filter === "completed") return task.status === "completed";
      return true;
    });
  }, [tasks, filter]);

  // Memoized counts
  const { pendingCount, completedCount } = useMemo(
    () => ({
      pendingCount: tasks.filter(
        (t) => t.status === "pending" || t.status === "in_progress",
      ).length,
      completedCount: tasks.filter((t) => t.status === "completed").length,
    }),
    [tasks],
  );

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <SkeletonTaskItem key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3" role="region" aria-label="قائمة المهام">
      {/* Filter tabs */}
      <div className="flex gap-2 mb-4" role="tablist" aria-label="تصفية المهام">
        <button
          type="button"
          onClick={() => setFilter("all")}
          role="tab"
          aria-selected={filter === "all"}
          aria-controls="task-list"
          className={`text-xs px-3 py-1 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1 ${
            filter === "all"
              ? "bg-emerald-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          الكل ({tasks.length})
        </button>
        <button
          type="button"
          onClick={() => setFilter("pending")}
          role="tab"
          aria-selected={filter === "pending"}
          aria-controls="task-list"
          className={`text-xs px-3 py-1 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1 ${
            filter === "pending"
              ? "bg-emerald-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          معلقة ({pendingCount})
        </button>
        <button
          type="button"
          onClick={() => setFilter("completed")}
          role="tab"
          aria-selected={filter === "completed"}
          aria-controls="task-list"
          className={`text-xs px-3 py-1 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1 ${
            filter === "completed"
              ? "bg-emerald-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          مكتملة ({completedCount})
        </button>
      </div>

      {/* Task cards */}
      <div id="task-list" role="tabpanel" aria-label="قائمة المهام المعروضة">
        {filteredTasks.length === 0 ? (
          <div
            className="text-center py-8 text-gray-400"
            role="status"
            aria-label="لا توجد مهام"
          >
            <span className="text-4xl" role="img" aria-hidden="true">
              📋
            </span>
            <p className="mt-2">لا توجد مهام</p>
          </div>
        ) : (
          <ul className="space-y-2" role="list" aria-label="المهام">
            {filteredTasks.map((task) => (
              <li key={task.id}>
                <TaskCard task={task} onComplete={handleComplete} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

// Memoized export
export default React.memo(TaskList);
