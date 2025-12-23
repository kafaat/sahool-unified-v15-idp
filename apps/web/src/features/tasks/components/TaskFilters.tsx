'use client';

/**
 * SAHOOL Task Filters Component
 * مكون تصفية المهام
 */

import React from 'react';
import { Filter, X } from 'lucide-react';
import type { TaskFilters, Priority, TaskStatus } from '../types';

interface TaskFiltersProps {
  filters: TaskFilters;
  onChange: (filters: TaskFilters) => void;
  onReset?: () => void;
}

export const TaskFiltersComponent: React.FC<TaskFiltersProps> = ({
  filters,
  onChange,
  onReset,
}) => {
  const handleChange = (key: keyof TaskFilters, value: any) => {
    onChange({ ...filters, [key]: value || undefined });
  };

  const hasActiveFilters = Object.values(filters).some(v => v);

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">التصفية</h3>
        </div>
        {hasActiveFilters && onReset && (
          <button
            onClick={onReset}
            className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
          >
            <X className="w-4 h-4" />
            <span>إزالة الفلاتر</span>
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            البحث
          </label>
          <input
            type="text"
            value={filters.search || ''}
            onChange={(e) => handleChange('search', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="ابحث في المهام..."
          />
        </div>

        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الحالة
          </label>
          <select
            value={filters.status || ''}
            onChange={(e) => handleChange('status', e.target.value as TaskStatus)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value="">الكل</option>
            <option value="pending">قيد الانتظار</option>
            <option value="in_progress">قيد التنفيذ</option>
            <option value="completed">مكتملة</option>
            <option value="cancelled">ملغاة</option>
          </select>
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الأولوية
          </label>
          <select
            value={filters.priority || ''}
            onChange={(e) => handleChange('priority', e.target.value as Priority)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value="">الكل</option>
            <option value="low">منخفضة</option>
            <option value="medium">متوسطة</option>
            <option value="high">عالية</option>
          </select>
        </div>

        {/* Field ID */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الحقل
          </label>
          <input
            type="text"
            value={filters.fieldId || ''}
            onChange={(e) => handleChange('fieldId', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="معرّف الحقل"
          />
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            من تاريخ
          </label>
          <input
            type="date"
            value={filters.dueDateFrom || ''}
            onChange={(e) => handleChange('dueDateFrom', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            إلى تاريخ
          </label>
          <input
            type="date"
            value={filters.dueDateTo || ''}
            onChange={(e) => handleChange('dueDateTo', e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>
    </div>
  );
};

export default TaskFiltersComponent;
