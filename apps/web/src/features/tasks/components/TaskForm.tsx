'use client';

/**
 * SAHOOL Task Form Component
 * مكون نموذج المهمة
 */

import React, { useState } from 'react';
import { Save, X } from 'lucide-react';
import type { Task, TaskFormData, Priority, TaskStatus } from '../types';

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: TaskFormData) => void | Promise<void>;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  task,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: task?.title || '',
    title_ar: task?.title || '', // Use title as fallback
    description: task?.description || '',
    description_ar: task?.description || '', // Use description as fallback
    due_date: task?.due_date ? (task.due_date.split('T')[0] ?? '') : '',
    priority: task?.priority || 'medium',
    status: task?.status || 'open',
    field_id: task?.field_id || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  const handleChange = (field: keyof TaskFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="task-form">
      <h2 className="text-2xl font-bold text-gray-900 mb-6" data-testid="task-form-title">
        {task ? 'تعديل المهمة' : 'إضافة مهمة جديدة'}
      </h2>

      <div className="space-y-6">
        {/* Title (Arabic) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            العنوان (بالعربية) *
          </label>
          <input
            type="text"
            required
            value={formData.title_ar}
            onChange={(e) => handleChange('title_ar', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="أدخل عنوان المهمة"
            data-testid="task-title-ar-input"
          />
        </div>

        {/* Title (English) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Title (English) *
          </label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => handleChange('title', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="Enter task title"
            dir="ltr"
            data-testid="task-title-input"
          />
        </div>

        {/* Due Date & Priority Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              تاريخ الاستحقاق *
            </label>
            <input
              type="date"
              required
              value={formData.due_date}
              onChange={(e) => handleChange('due_date', e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
              data-testid="task-due-date-input"
            />
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              الأولوية *
            </label>
            <select
              required
              value={formData.priority}
              onChange={(e) => handleChange('priority', e.target.value as Priority)}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
              data-testid="task-priority-select"
            >
              <option value="low">منخفضة - Low</option>
              <option value="medium">متوسطة - Medium</option>
              <option value="high">عالية - High</option>
            </select>
          </div>
        </div>

        {/* Status & Field Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              الحالة
            </label>
            <select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value as TaskStatus)}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
              data-testid="task-status-select"
            >
              <option value="open">جديدة - Open</option>
              <option value="in_progress">قيد التنفيذ - In Progress</option>
              <option value="completed">مكتملة - Completed</option>
              <option value="cancelled">ملغاة - Cancelled</option>
            </select>
          </div>

          {/* Field ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              الحقل (اختياري)
            </label>
            <input
              type="text"
              value={formData.field_id}
              onChange={(e) => handleChange('field_id', e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="معرّف الحقل"
              data-testid="task-field-id-input"
            />
          </div>
        </div>

        {/* Description (Arabic) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الوصف (بالعربية)
          </label>
          <textarea
            value={formData.description_ar}
            onChange={(e) => handleChange('description_ar', e.target.value)}
            rows={4}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="وصف المهمة"
            data-testid="task-description-ar-input"
          />
        </div>

        {/* Description (English) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description (English)
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={4}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="Task description"
            dir="ltr"
            data-testid="task-description-input"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 mt-8 pt-6 border-t-2 border-gray-200">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex items-center gap-2 px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isSubmitting}
            data-testid="task-form-cancel-button"
          >
            <X className="w-4 h-4" />
            <span>إلغاء</span>
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="task-form-submit-button"
        >
          <Save className="w-4 h-4" />
          <span>{isSubmitting ? 'جاري الحفظ...' : 'حفظ'}</span>
        </button>
      </div>
    </form>
  );
};

export default TaskForm;
