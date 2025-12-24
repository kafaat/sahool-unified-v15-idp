'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import type { Task } from '@/lib/api/types';
import { TaskCard } from './TaskCard';
import { SkeletonTaskItem } from './ui/Skeleton';

interface TaskListProps {
  tenantId?: string;
  fieldId?: string | null;
  limit?: number;
}

export function TaskList({ tenantId, fieldId, limit = 10 }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');
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
        console.error('Failed to fetch tasks:', error);
        // Fallback to demo data
        setTasks([
          {
            id: 'task_001',
            title: 'ري الطماطم - الصباح',
            description: 'ري الحقل الشمالي لمدة 30 دقيقة',
            field_id: 'field_001',
            fieldName: 'حقل الطماطم',
            status: 'pending',
            priority: 'high',
            taskType: 'irrigation',
            due_date: new Date().toISOString(),
            assigneeName: 'أحمد',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 'task_002',
            title: 'رش مبيدات وقائية',
            description: 'رش مبيد فطري للوقاية من البياض الدقيقي',
            field_id: 'field_001',
            fieldName: 'حقل الطماطم',
            status: 'in_progress',
            priority: 'medium',
            taskType: 'pesticide',
            due_date: new Date(Date.now() + 86400000).toISOString(),
            assigneeName: 'محمد',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 'task_003',
            title: 'فحص مرض صدأ البن',
            description: 'فحص ميداني للكشف عن علامات مرض صدأ الأوراق',
            field_id: 'field_002',
            fieldName: 'حقل البن',
            status: 'pending',
            priority: 'high',
            taskType: 'inspection',
            due_date: new Date().toISOString(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 'task_004',
            title: 'حصاد الموز الناضج',
            description: 'جمع العناقيد الناضجة من الصف 1-5',
            field_id: 'field_004',
            fieldName: 'حقل الموز',
            status: 'completed',
            priority: 'medium',
            taskType: 'harvest',
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

  const handleComplete = async (taskId: string) => {
    // Update local state optimistically
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId ? { ...t, status: 'completed' as const, completed_at: new Date().toISOString() } : t
      )
    );

    try {
      await apiClient.updateTask(taskId, { status: 'completed' });
    } catch (error) {
      // Revert on failure
      console.error('Failed to complete task:', error);
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId ? { ...t, status: 'pending' as const, completed_at: undefined } : t
        )
      );
    }
  };

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'pending') return task.status === 'pending' || task.status === 'in_progress';
    if (filter === 'completed') return task.status === 'completed';
    return true;
  });

  const pendingCount = tasks.filter((t) => t.status === 'pending' || t.status === 'in_progress').length;
  const completedCount = tasks.filter((t) => t.status === 'completed').length;

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
    <div className="space-y-3">
      {/* Filter tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setFilter('all')}
          className={`text-xs px-3 py-1 rounded-full transition-colors ${
            filter === 'all'
              ? 'bg-emerald-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          الكل ({tasks.length})
        </button>
        <button
          onClick={() => setFilter('pending')}
          className={`text-xs px-3 py-1 rounded-full transition-colors ${
            filter === 'pending'
              ? 'bg-emerald-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          معلقة ({pendingCount})
        </button>
        <button
          onClick={() => setFilter('completed')}
          className={`text-xs px-3 py-1 rounded-full transition-colors ${
            filter === 'completed'
              ? 'bg-emerald-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          مكتملة ({completedCount})
        </button>
      </div>

      {/* Task cards */}
      {filteredTasks.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <span className="text-4xl">📋</span>
          <p className="mt-2">لا توجد مهام</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filteredTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onComplete={handleComplete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default TaskList;
