/**
 * Equipment List Component
 * مكون قائمة المعدات
 */

'use client';

import { useState } from 'react';
import { useEquipment } from '../hooks/useEquipment';
import { EquipmentCard } from './EquipmentCard';
import type { EquipmentFilters, EquipmentType, EquipmentStatus } from '../types';
import { Search, Filter, Loader2 } from 'lucide-react';

interface EquipmentListProps {
  onFieldClick?: (equipmentId: string) => void;
  onCreateClick?: () => void;
}

export function EquipmentList({ onFieldClick }: EquipmentListProps) {
  const [filters, setFilters] = useState<EquipmentFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const { data: equipment, isLoading, error } = useEquipment(filters);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters({ ...filters, search: searchTerm });
  };

  const handleTypeFilter = (type: EquipmentType | undefined) => {
    setFilters({ ...filters, type });
  };

  const handleStatusFilter = (status: EquipmentStatus | undefined) => {
    setFilters({ ...filters, status });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12" data-testid="equipment-list-loading">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <span className="mr-3 text-gray-600">جاري التحميل...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800" data-testid="equipment-list-error">
        حدث خطأ أثناء تحميل المعدات
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="equipment-list-container">
      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow p-4 space-y-4" data-testid="equipment-filters">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="ابحث عن المعدات..."
              data-testid="equipment-search-input"
              className="w-full pr-10 pl-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          </div>
          <button
            type="submit"
            data-testid="equipment-search-button"
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            بحث
          </button>
        </form>

        <div className="flex flex-wrap gap-2" data-testid="equipment-type-filters">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">النوع:</span>
          </div>
          <button
            onClick={() => handleTypeFilter(undefined)}
            data-testid="filter-type-all"
            className={`px-3 py-1 rounded-full text-sm ${
              !filters.type
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            الكل
          </button>
          <button
            onClick={() => handleTypeFilter('tractor')}
            data-testid="filter-type-tractor"
            className={`px-3 py-1 rounded-full text-sm ${
              filters.type === 'tractor'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            جرار
          </button>
          <button
            onClick={() => handleTypeFilter('harvester')}
            data-testid="filter-type-harvester"
            className={`px-3 py-1 rounded-full text-sm ${
              filters.type === 'harvester'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            حصادة
          </button>
          <button
            onClick={() => handleTypeFilter('irrigation_system')}
            data-testid="filter-type-irrigation"
            className={`px-3 py-1 rounded-full text-sm ${
              filters.type === 'irrigation_system'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            نظام ري
          </button>
        </div>

        <div className="flex flex-wrap gap-2" data-testid="equipment-status-filters">
          <span className="text-sm text-gray-600">الحالة:</span>
          <button
            onClick={() => handleStatusFilter(undefined)}
            data-testid="filter-status-all"
            className={`px-3 py-1 rounded-full text-sm ${
              !filters.status
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            الكل
          </button>
          <button
            onClick={() => handleStatusFilter('active')}
            data-testid="filter-status-active"
            className={`px-3 py-1 rounded-full text-sm ${
              filters.status === 'active'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            نشط
          </button>
          <button
            onClick={() => handleStatusFilter('maintenance')}
            data-testid="filter-status-maintenance"
            className={`px-3 py-1 rounded-full text-sm ${
              filters.status === 'maintenance'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            صيانة
          </button>
        </div>
      </div>

      {/* Equipment Grid */}
      {equipment && equipment.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="equipment-grid">
          {equipment.map((item) => (
            <div key={item.id} onClick={() => onFieldClick?.(item.id)}>
              <EquipmentCard equipment={item} />
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow" data-testid="equipment-empty-state">
          <p className="text-gray-500">لا توجد معدات</p>
        </div>
      )}
    </div>
  );
}
