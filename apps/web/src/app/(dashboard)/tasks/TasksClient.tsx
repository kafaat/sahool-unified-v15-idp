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
import type { TaskFilters as TaskFiltersType } from '@/features/tasks/types';
import { ErrorTracking } from '@/lib/monitoring/error-tracking';

export default function TasksClient() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<TaskFiltersType>({});
  const [, setSelectedTaskId] = useState<string | null>(null);

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

  const handleSubmit = async (data: any) => {
    try {
      ErrorTracking.addBreadcrumb({
        type: 'click',
        category: 'ui',
        message: 'Creating task',
        data: { taskTitle: data?.title },
      });
      // TODO: Implement actual task creation
      // For now, just close the modal
      setShowCreateModal(false);
    } catch (error) {
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
              data-testid="toggle-filters-button"
            >
              <Filter className="w-5 h-5" />
              <span className="font-medium">فلتر</span>
            </button>
            <button
              onClick={handleCreateClick}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
              data-testid="add-task-button"
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
        />
      </Modal>
    </div>
  );
}
