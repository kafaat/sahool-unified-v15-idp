'use client';

/**
 * SAHOOL Fields List Component
 * مكون قائمة الحقول
 */

import React, { useState } from 'react';
import { Grid3x3, List, Map as MapIcon, Search, Plus } from 'lucide-react';
import { useFields } from '../hooks/useFields';
import { FieldCard } from './FieldCard';
import type { FieldViewMode, FieldFilters } from '../types';

interface FieldsListProps {
  onFieldClick?: (fieldId: string) => void;
  onCreateClick?: () => void;
}

export const FieldsList: React.FC<FieldsListProps> = ({ onFieldClick, onCreateClick }) => {
  const [viewMode, setViewMode] = useState<FieldViewMode['mode']>('grid');
  const [filters, setFilters] = useState<FieldFilters>({});
  const { data: fields, isLoading } = useFields(filters);

  const handleSearch = (search: string) => {
    setFilters(prev => ({ ...prev, search }));
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-10 w-64 bg-gray-200 rounded-lg animate-pulse" />
          <div className="h-10 w-32 bg-gray-200 rounded-lg animate-pulse" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={`skeleton-field-${i}`} className="h-48 bg-gray-200 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex-1 w-full sm:w-auto">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="ابحث عن حقل... | Search fields..."
              className="w-full pr-10 pl-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-lg" role="group" aria-label="تبديل طريقة العرض">
            <button
              onClick={() => setViewMode('grid')}
              aria-label="عرض شبكي"
              aria-pressed={viewMode === 'grid'}
              className={`p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${viewMode === 'grid' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
            >
              <Grid3x3 className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              aria-label="عرض قائمة"
              aria-pressed={viewMode === 'list'}
              className={`p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${viewMode === 'list' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
            >
              <List className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('map')}
              aria-label="عرض خريطة"
              aria-pressed={viewMode === 'map'}
              className={`p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${viewMode === 'map' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
            >
              <MapIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Create Button */}
          {onCreateClick && (
            <button
              onClick={onCreateClick}
              aria-label="إضافة حقل جديد"
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <Plus className="w-5 h-5" />
              <span>إضافة حقل</span>
            </button>
          )}
        </div>
      </div>

      {/* Fields Grid/List */}
      {!fields || fields.length === 0 ? (
        <div className="text-center py-16">
          <MapIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">لا توجد حقول</h3>
          <p className="text-gray-500 mb-6">ابدأ بإضافة حقلك الأول</p>
          {onCreateClick && (
            <button
              onClick={onCreateClick}
              aria-label="إضافة حقل جديد"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              إضافة حقل جديد
            </button>
          )}
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
          {fields.map((field) => (
            <FieldCard
              key={field.id}
              field={field}
              onClick={() => onFieldClick?.(field.id)}
            />
          ))}
        </div>
      )}

      {/* Results Count */}
      {fields && fields.length > 0 && (
        <div className="text-center text-sm text-gray-500">
          عرض {fields.length} حقل | Showing {fields.length} fields
        </div>
      )}
    </div>
  );
};

export default FieldsList;
