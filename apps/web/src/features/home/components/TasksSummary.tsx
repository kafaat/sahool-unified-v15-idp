'use client';

/**
 * SAHOOL Tasks Summary Component
 * مكون ملخص المهام
 */

import React, { useState, useCallback, useEffect } from 'react';
import { CheckCircle2, Clock, Calendar, ArrowLeft } from 'lucide-react';
import { useUpcomingTasks } from '../hooks/useUpcomingTasks';
import { useCompleteTask, useUpdateTaskStatus } from '@/features/tasks/hooks/useTasks';
import Link from 'next/link';

interface TaskItemProps {
  id: string;
  title: string;
  titleAr: string;
  dueDate: string;
  priority: 'high' | 'medium' | 'low';
  status: string;
}

const priorityColors = {
  high: 'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800',
  medium:
    'bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800',
  low: 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
};

const TaskItem: React.FC<
  TaskItemProps & { onToggleComplete: (id: string) => void; index: number }
> = ({ id, titleAr, dueDate, priority, status, onToggleComplete, index }) => {
  const isOverdue = new Date(dueDate) < new Date() && status !== 'completed';
  const isCompleted = status === 'completed';

  return (
    <div
      className="flex items-start gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-all group animate-slide-in-up"
      style={{
        animationDelay: `${index * 60}ms`,
        animationFillMode: 'both',
      }}
    >
      <button
        onClick={() => onToggleComplete(id)}
        className={`mt-0.5 flex-shrink-0 transition-all ${
          isCompleted
            ? 'text-green-500 dark:text-green-400 scale-110'
            : 'text-gray-300 dark:text-gray-600 hover:text-green-400 dark:hover:text-green-500 hover:scale-110'
        }`}
        aria-label={isCompleted ? 'إلغاء إكمال المهمة' : 'إكمال المهمة'}
      >
        <CheckCircle2 className="w-5 h-5" />
      </button>
      <div className="flex-1 min-w-0">
        <p
          className={`font-medium truncate transition-all ${
            isCompleted
              ? 'line-through text-gray-400 dark:text-gray-500'
              : 'text-gray-900 dark:text-white'
          }`}
        >
          {titleAr}
        </p>
        <div className="flex items-center gap-2 mt-1">
          <span className={`text-xs px-2 py-1 rounded-full border ${priorityColors[priority]}`}>
            {priority === 'high' ? 'عالية' : priority === 'medium' ? 'متوسطة' : 'منخفضة'}
          </span>
          <div
            className={`flex items-center gap-1 text-xs ${
              isOverdue ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            <Calendar className="w-3 h-3" />
            <span>{new Date(dueDate).toLocaleDateString('ar-EG')}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * NOTE (testing): This component uses useUpcomingTasks (react-query) internally.
 * Tests must wrap it in a QueryClientProvider with a dedicated QueryClient instance.
 */
export const TasksSummary: React.FC = () => {
  const { data: tasksData, isLoading } = useUpcomingTasks({ limit: 8 });
  const [completedIds, setCompletedIds] = useState<Set<string>>(new Set());
  const [pendingIds, setPendingIds] = useState<Set<string>>(new Set());
  const completeTask = useCompleteTask();
  const updateTaskStatus = useUpdateTaskStatus();

  // Initialize completedIds from tasks that are already completed in API data
  useEffect(() => {
    const alreadyCompleted = new Set(
      (tasksData ?? []).filter((t: TaskItemProps) => t.status === 'completed').map((t: TaskItemProps) => t.id)
    );
    setCompletedIds(alreadyCompleted);
  }, [tasksData]);

  const handleToggleComplete = useCallback((id: string) => {
    if (pendingIds.has(id)) return; // Prevent double-clicks while API call in-flight

    const isCurrentlyCompleted = completedIds.has(id);

    // Optimistic local update
    setCompletedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });

    // Call the real API
    setPendingIds((prev) => new Set(prev).add(id));

    if (isCurrentlyCompleted) {
      // Revert to pending status
      updateTaskStatus.mutate(
        { id, status: 'pending' },
        {
          onError: () => {
            // Revert optimistic update on failure
            setCompletedIds((prev) => {
              const next = new Set(prev);
              next.add(id);
              return next;
            });
          },
          onSettled: () => {
            setPendingIds((prev) => {
              const next = new Set(prev);
              next.delete(id);
              return next;
            });
          },
        }
      );
    } else {
      // Mark as completed
      completeTask.mutate(
        { id },
        {
          onError: () => {
            // Revert optimistic update on failure
            setCompletedIds((prev) => {
              const next = new Set(prev);
              next.delete(id);
              return next;
            });
          },
          onSettled: () => {
            setPendingIds((prev) => {
              const next = new Set(prev);
              next.delete(id);
              return next;
            });
          },
        }
      );
    }
  }, [completedIds, pendingIds, completeTask, updateTaskStatus]);

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-6 transition-colors">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">المهام القادمة</h3>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const tasks = tasksData || [];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-6 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">المهام القادمة</h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">Upcoming Tasks</span>
      </div>

      {tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <Clock className="w-12 h-12 mx-auto mb-2 opacity-20" />
          <p>لا توجد مهام قادمة</p>
          <p className="text-sm">No upcoming tasks</p>
        </div>
      ) : (
        <>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {tasks.slice(0, 8).map((task: TaskItemProps, index: number) => (
              <TaskItem
                key={task.id}
                {...task}
                status={completedIds.has(task.id) ? 'completed' : task.status}
                onToggleComplete={handleToggleComplete}
                index={index}
              />
            ))}
          </div>

          {tasks.length > 0 && (
            <Link
              href="/tasks"
              className="mt-4 flex items-center justify-center gap-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm font-medium group"
            >
              <span>عرض جميع المهام</span>
              <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1 rtl:group-hover:translate-x-1" />
            </Link>
          )}
        </>
      )}
    </div>
  );
};

export default TasksSummary;
