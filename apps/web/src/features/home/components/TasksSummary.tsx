'use client';

/**
 * SAHOOL Tasks Summary Component
 * مكون ملخص المهام
 */

import React from 'react';
import { CheckCircle2, Clock, Calendar, ArrowLeft } from 'lucide-react';
import { useDashboardData } from '../hooks/useDashboardData';
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
  high: 'bg-red-100 text-red-700 border-red-200',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  low: 'bg-green-100 text-green-700 border-green-200',
};

const TaskItem: React.FC<TaskItemProps> = ({ titleAr, dueDate, priority, status }) => {
  const isOverdue = new Date(dueDate) < new Date() && status !== 'completed';

  return (
    <div className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
      <div className={`mt-1 ${status === 'completed' ? 'text-green-500' : 'text-gray-300'}`}>
        <CheckCircle2 className="w-5 h-5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 truncate">{titleAr}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className={`text-xs px-2 py-1 rounded-full border ${priorityColors[priority]}`}>
            {priority === 'high' ? 'عالية' : priority === 'medium' ? 'متوسطة' : 'منخفضة'}
          </span>
          <div className={`flex items-center gap-1 text-xs ${isOverdue ? 'text-red-600' : 'text-gray-500'}`}>
            <Calendar className="w-3 h-3" />
            <span>{new Date(dueDate).toLocaleDateString('ar-EG')}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export const TasksSummary: React.FC = () => {
  const { data, isLoading } = useDashboardData();

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">المهام القادمة</h3>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const tasks = data?.upcomingTasks || [];

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">المهام القادمة</h3>
        <span className="text-sm text-gray-500">Upcoming Tasks</span>
      </div>

      {tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-2 opacity-20" />
          <p>لا توجد مهام قادمة</p>
          <p className="text-sm">No upcoming tasks</p>
        </div>
      ) : (
        <>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {tasks.slice(0, 8).map((task: TaskItemProps) => (
              <TaskItem key={task.id} {...task} />
            ))}
          </div>

          {tasks.length > 0 && (
            <Link
              href="/tasks"
              className="mt-4 flex items-center justify-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              <span>عرض جميع المهام</span>
              <ArrowLeft className="w-4 h-4" />
            </Link>
          )}
        </>
      )}
    </div>
  );
};

export default TasksSummary;
