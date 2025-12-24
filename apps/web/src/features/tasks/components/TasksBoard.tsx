'use client';

/**
 * SAHOOL Tasks Board Component (Kanban)
 * مكون لوحة المهام (كانبان)
 */

import React from 'react';
import { useTasks, useUpdateTaskStatus } from '../hooks/useTasks';
import { TaskCard } from './TaskCard';
import type { TaskBoardColumn, TaskStatus } from '../types';

interface TasksBoardProps {
  onTaskClick?: (taskId: string) => void;
}

const columns: TaskBoardColumn[] = [
  {
    id: 'pending',
    title: 'Pending',
    titleAr: 'قيد الانتظار',
    tasks: [],
    color: 'bg-gray-50 border-gray-200',
  },
  {
    id: 'in_progress',
    title: 'In Progress',
    titleAr: 'قيد التنفيذ',
    tasks: [],
    color: 'bg-blue-50 border-blue-200',
  },
  {
    id: 'completed',
    title: 'Completed',
    titleAr: 'مكتملة',
    tasks: [],
    color: 'bg-green-50 border-green-200',
  },
];

export const TasksBoard: React.FC<TasksBoardProps> = ({ onTaskClick }) => {
  const { data: tasks, isLoading } = useTasks();
  const updateStatus = useUpdateTaskStatus();

  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    e.dataTransfer.setData('taskId', taskId);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = async (e: React.DragEvent, status: TaskStatus) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('taskId');
    if (taskId) {
      await updateStatus.mutateAsync({ id: taskId, status });
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-96 bg-gray-200 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  // Group tasks by status
  const boardColumns = columns.map(column => ({
    ...column,
    tasks: tasks?.filter(t => t.status === column.id) || [],
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {boardColumns.map((column) => (
        <div
          key={column.id}
          onDragOver={handleDragOver}
          onDrop={(e) => handleDrop(e, column.id)}
          className={`rounded-xl border-2 ${column.color} p-4 min-h-[500px]`}
        >
          {/* Column Header */}
          <div className="mb-4">
            <h3 className="text-lg font-bold text-gray-900">{column.titleAr}</h3>
            <p className="text-sm text-gray-500">{column.title}</p>
            <div className="mt-2 text-sm text-gray-600">
              {column.tasks.length} {column.tasks.length === 1 ? 'مهمة' : 'مهام'}
            </div>
          </div>

          {/* Tasks */}
          <div className="space-y-3">
            {column.tasks.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p className="text-sm">لا توجد مهام</p>
              </div>
            ) : (
              column.tasks.map((task) => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, task.id)}
                >
                  <TaskCard
                    task={task}
                    onClick={() => onTaskClick?.(task.id)}
                    draggable
                  />
                </div>
              ))
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default TasksBoard;
