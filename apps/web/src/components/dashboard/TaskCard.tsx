'use client';

import type { Task } from '@/lib/api/types';

interface TaskCardProps {
  task: Task;
  onComplete?: (taskId: string) => void;
  onSelect?: (taskId: string) => void;
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'معلقة',
  in_progress: 'قيد التنفيذ',
  completed: 'مكتملة',
  cancelled: 'ملغاة',
};

const PRIORITY_LABELS: Record<string, string> = {
  low: 'منخفضة',
  medium: 'متوسطة',
  high: 'عالية',
};

const PRIORITY_ICONS: Record<string, string> = {
  low: '🔵',
  medium: '🟡',
  high: '🔴',
};

export function TaskCard({ task, onComplete, onSelect }: TaskCardProps) {
  const isCompleted = task.status === 'completed' || task.status === 'cancelled';
  const dueDate = task.dueDate ? new Date(task.dueDate) : null;
  const isOverdue = dueDate && dueDate < new Date() && !isCompleted;

  return (
    <div
      onClick={() => onSelect?.(task.id)}
      className={`
        p-3 rounded-lg border transition-all cursor-pointer
        ${isCompleted ? 'bg-gray-50 opacity-60' : 'bg-white hover:shadow-md'}
        ${task.priority === 'high' ? 'border-r-4 border-r-red-400' : ''}
        ${task.priority === 'medium' ? 'border-r-4 border-r-yellow-400' : ''}
        ${task.priority === 'low' ? 'border-r-4 border-r-blue-400' : ''}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">{PRIORITY_ICONS[task.priority]}</span>
          <h4 className={`font-medium text-sm ${isCompleted ? 'line-through text-gray-400' : 'text-gray-800'}`}>
            {task.title}
          </h4>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          task.status === 'completed' ? 'bg-green-100 text-green-700' :
          task.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
          task.status === 'cancelled' ? 'bg-gray-100 text-gray-500' :
          'bg-amber-100 text-amber-700'
        }`}>
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
            <span className={`flex items-center gap-1 ${isOverdue ? 'text-red-500' : ''}`}>
              📅
              {dueDate.toLocaleDateString('ar-YE', {
                month: 'short',
                day: 'numeric',
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
            <span className="flex items-center gap-1">
              🌱 {task.fieldName}
            </span>
          )}
        </div>

        {/* Complete button */}
        {!isCompleted && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onComplete?.(task.id);
            }}
            className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 transition-colors"
          >
            ✓ إنهاء
          </button>
        )}
      </div>
    </div>
  );
}

export default TaskCard;
