'use client';

/**
 * SAHOOL Tasks Page Client Component
 * صفحة المهام
 */

import React, { useState } from 'react';
import { TasksList } from '@/features/tasks';
import { TaskForm } from '@/features/tasks/components/TaskForm';
import { TaskFiltersComponent as TaskFilters } from '@/features/tasks/components/TaskFilters';
import { Modal } from '@/components/ui/modal';
import { Plus, Filter } from 'lucide-react';
import type { TaskFilters as TaskFiltersType, TaskFormData } from '@/features/tasks/types';
import { ErrorTracking } from '@/lib/monitoring/error-tracking';
import { useCreateTask } from '@/features/tasks/hooks/useTasks';
import { useToast } from '@/components/ui/toast';

export default function TasksClient() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<TaskFiltersType>({});
  const [, setSelectedTaskId] = useState<string | null>(null);

  // Task creation mutation
  const createTaskMutation = useCreateTask();
  const { showToast } = useToast();

  const handleTaskClick = (taskId: string) => {
    setSelectedTaskId(taskId);
    ErrorTracking.addBreadcrumb({
      type: 'click',
      category: 'ui',
      message: 'Task clicked',
      data: { taskId },
    });
  };

  const handleCreateClick = () => {
    setShowCreateModal(true);
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
  };

  const handleFiltersChange = (newFilters: TaskFiltersType) => {
    setFilters(newFilters);
  };

  const handleSubmit = async (data: TaskFormData) => {
    try {
      ErrorTracking.addBreadcrumb({
        type: 'click',
        category: 'ui',
        message: 'Creating task',
        data: { taskTitle: data?.title },
      });

      // Create the task using the mutation
      await createTaskMutation.mutateAsync(data);

      // Show success message
      showToast({
        type: 'success',
        messageAr: 'تم إنشاء المهمة بنجاح',
        message: 'Task created successfully',
      });

      // Close the modal
      setShowCreateModal(false);
    } catch (error) {
      // Show error message
      showToast({
        type: 'error',
        messageAr: 'فشل في إنشاء المهمة',
        message: error instanceof Error ? error.message : 'Failed to create task',
      });

      ErrorTracking.captureError(
        error instanceof Error ? error : new Error('Failed to create task'),
        undefined,
        { data }
      );
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">المهام</h1>
            <p className="text-gray-600">Tasks Management</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-4 py-3 border-2 rounded-lg transition-colors ${
                showFilters
                  ? 'border-blue-600 bg-blue-50 text-blue-600'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              <Filter className="w-5 h-5" />
              <span className="font-medium">فلتر</span>
            </button>
            <button
              onClick={handleCreateClick}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
            >
              <Plus className="w-5 h-5" />
              <span className="font-medium">إضافة مهمة جديدة</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filters Section */}
      {showFilters && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <TaskFilters
            filters={filters}
            onChange={handleFiltersChange}
          />
        </div>
      )}

      {/* Tasks List */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <TasksList
          filters={filters}
          onTaskClick={handleTaskClick}
        />
      </div>

      {/* Create Task Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={handleCloseModal}
        titleAr="إضافة مهمة جديدة"
        title="Create New Task"
      >
        <TaskForm
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isSubmitting={createTaskMutation.isPending}
        />
      </Modal>
    </div>
  );
}
