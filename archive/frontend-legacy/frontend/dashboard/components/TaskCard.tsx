'use client'

import { Task } from '@/lib/api'

interface TaskCardProps {
  task: Task
  onComplete?: (taskId: string) => void
  onSelect?: (taskId: string) => void
}

const STATUS_LABELS: Record<string, string> = {
  open: 'مفتوحة',
  in_progress: 'قيد التنفيذ',
  done: 'مكتملة',
  canceled: 'ملغاة',
}

const PRIORITY_LABELS: Record<string, string> = {
  low: 'منخفضة',
  medium: 'متوسطة',
  high: 'عالية',
  urgent: 'عاجلة',
}

const PRIORITY_ICONS: Record<string, string> = {
  low: '🔵',
  medium: '🟡',
  high: '🟠',
  urgent: '🔴',
}

export function TaskCard({ task, onComplete, onSelect }: TaskCardProps) {
  const isCompleted = task.status === 'done' || task.status === 'canceled'
  const dueDate = task.due_date ? new Date(task.due_date) : null
  const isOverdue = dueDate && dueDate < new Date() && !isCompleted

  return (
    <div
      onClick={() => onSelect?.(task.id)}
      className={`
        p-3 rounded-lg border transition-all cursor-pointer
        ${isCompleted ? 'bg-gray-50 opacity-60' : 'bg-white hover:shadow-md'}
        priority-${task.priority}
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
        <span className={`text-xs px-2 py-0.5 rounded-full status-${task.status}`}>
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
          {task.assigned_to && (
            <span className="flex items-center gap-1">
              👤 {task.assigned_to}
            </span>
          )}
        </div>

        {/* Complete button */}
        {!isCompleted && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onComplete?.(task.id)
            }}
            className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 transition-colors"
          >
            ✓ إنهاء
          </button>
        )}
      </div>

      {/* Evidence indicator */}
      {task.evidence_photos && task.evidence_photos.length > 0 && (
        <div className="mt-2 flex items-center gap-1 text-xs text-gray-400">
          <span>📷</span>
          <span>{task.evidence_photos.length} صور</span>
        </div>
      )}
    </div>
  )
}
