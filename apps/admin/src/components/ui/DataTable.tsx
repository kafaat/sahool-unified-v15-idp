'use client';

// Data Table Component
// جدول البيانات

import React, { useCallback } from 'react';
import { cn } from '@/lib/utils';

interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
  className?: string;
  isLoading?: boolean;
}

function DataTableInner<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  emptyMessage = 'لا توجد بيانات',
  className = '',
  isLoading = false,
}: DataTableProps<T>) {
  const handleRowKeyDown = useCallback(
    (e: React.KeyboardEvent, item: T) => {
      if (onRowClick && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        onRowClick(item);
      }
    },
    [onRowClick]
  );

  if (isLoading) {
    return (
      <div
        className={cn('bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden', className)}
      >
        <div className="animate-pulse">
          <div className="h-12 bg-gray-100 dark:bg-gray-700"></div>
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="h-16 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800"
            ></div>
          ))}
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div
        className={cn('bg-white dark:bg-gray-800 rounded-xl shadow-sm p-8 text-center', className)}
        role="status"
        aria-live="polite"
      >
        <p className="text-gray-500 dark:text-gray-400">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div
      className={cn('bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden', className)}
    >
      <div className="overflow-x-auto">
        <table className="w-full" role="table">
          <thead className="bg-gray-50 dark:bg-gray-900 border-b border-gray-100 dark:border-gray-700">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  scope="col"
                  className={cn(
                    'px-6 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider',
                    col.className
                  )}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {data.map((item) => (
              <tr
                key={keyExtractor(item)}
                onClick={() => onRowClick?.(item)}
                onKeyDown={(e) => handleRowKeyDown(e, item)}
                tabIndex={onRowClick ? 0 : undefined}
                role={onRowClick ? 'button' : undefined}
                aria-label={onRowClick ? 'اضغط للتفاصيل' : undefined}
                className={cn(
                  'hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-inset',
                  onRowClick && 'cursor-pointer'
                )}
              >
                {columns.map((col) => (
                  <td key={col.key} className={cn('px-6 py-4 text-sm', col.className)}>
                    {col.render
                      ? col.render(item)
                      : String((item as Record<string, unknown>)[col.key] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Memoize to prevent unnecessary re-renders when parent state changes
const DataTable = React.memo(DataTableInner) as typeof DataTableInner;
export default DataTable;
