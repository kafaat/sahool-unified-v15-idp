'use client';

/**
 * SAHOOL Task Card Component
 * مكون بطاقة المهمة
 */

import React from 'react';
import { Calendar, MapPin, Flag, Clock } from 'lucide-react';
import type { Task } from '../types';

interface TaskCardProps {
  task: Task;
  onClick?: () => void;
  draggable?: boolean;
}

const priorityColors: Record<string, string> = {
  urgent: 'bg-red-200 text-red-800 border-red-300',
  high: 'bg-red-100 text-red-700 border-red-200',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  low: 'bg-green-100 text-green-700 border-green-200',
};

const statusColors: Record<string, string> = {
  open: 'border-gray-200',
  pending: 'border-gray-200',
  in_progress: 'border-blue-300 bg-blue-50',
  completed: 'border-green-300 bg-green-50',
  cancelled: 'border-red-300 bg-red-50',
};

export const TaskCard: React.FC<TaskCardProps> = ({ task, onClick, draggable = false }) => {
  const isOverdue = task.due_date ? new Date(task.due_date) < new Date() && task.status !== 'completed' : false;

  return (
    <div
      onClick={onClick}
      draggable={draggable}
      className={`
        bg-white rounded-lg border-2 p-4 cursor-pointer
        hover:shadow-md transition-all
        ${statusColors[task.status]}
        ${draggable ? 'cursor-move' : ''}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-semibold text-gray-900 flex-1">
          {task.title}
        </h4>
        <div className={`px-2 py-1 rounded-full text-xs border ${priorityColors[task.priority]}`}>
          {task.priority === 'urgent' ? 'عاجلة' : task.priority === 'high' ? 'عالية' : task.priority === 'medium' ? 'متوسطة' : 'منخفضة'}
        </div>
      </div>

      {/* Description */}
      {task.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Meta Info */}
      <div className="space-y-2">
        {task.due_date && (
          <div className={`flex items-center gap-2 text-sm ${isOverdue ? 'text-red-600' : 'text-gray-500'}`}>
            <Calendar className="w-4 h-4" />
            <span>{new Date(task.due_date).toLocaleDateString('ar-EG')}</span>
            {isOverdue && (
              <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">متأخر</span>
            )}
          </div>
        )}

        {task.field_id && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <MapPin className="w-4 h-4" />
            <span>الحقل #{task.field_id}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskCard;
