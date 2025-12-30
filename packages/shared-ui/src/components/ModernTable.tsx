'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernTable Component - جدول حديث
// Advanced data table with sorting, filtering, and pagination
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ReactNode, useState, useMemo } from 'react';
import {
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
  ChevronLeft,
  ChevronRight,
  Search,
} from 'lucide-react';

export interface Column<T> {
  key: string;
  header: string | ReactNode;
  accessor: (row: T) => ReactNode;
  sortable?: boolean;
  filterable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

export interface ModernTableProps<T> {
  data: T[];
  columns: Column<T>[];
  pagination?: boolean;
  pageSize?: number;
  searchable?: boolean;
  searchPlaceholder?: string;
  striped?: boolean;
  hoverable?: boolean;
  bordered?: boolean;
  compact?: boolean;
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
  onRowClick?: (row: T, index: number) => void;
}

type SortDirection = 'asc' | 'desc' | null;

export function ModernTable<T>({
  data,
  columns,
  pagination = true,
  pageSize = 10,
  searchable = true,
  searchPlaceholder = 'Search...',
  striped = true,
  hoverable = true,
  bordered = false,
  compact = false,
  loading = false,
  emptyMessage = 'No data available',
  className = '',
  onRowClick,
}: ModernTableProps<T>) {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm || !searchable) return data;

    return data.filter((row) => {
      return columns.some((column) => {
        if (!column.filterable) return false;
        const value = column.accessor(row);
        if (typeof value === 'string' || typeof value === 'number') {
          return String(value).toLowerCase().includes(searchTerm.toLowerCase());
        }
        return false;
      });
    });
  }, [data, searchTerm, searchable, columns]);

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortColumn || !sortDirection) return filteredData;

    const column = columns.find((col) => col.key === sortColumn);
    if (!column) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aValue = column.accessor(a);
      const bValue = column.accessor(b);

      const aStr = String(aValue);
      const bStr = String(bValue);

      if (sortDirection === 'asc') {
        return aStr.localeCompare(bStr);
      } else {
        return bStr.localeCompare(aStr);
      }
    });
  }, [filteredData, sortColumn, sortDirection, columns]);

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;

    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return sortedData.slice(startIndex, endIndex);
  }, [sortedData, currentPage, pageSize, pagination]);

  const totalPages = Math.ceil(sortedData.length / pageSize);

  // Handle sorting
  const handleSort = (columnKey: string) => {
    const column = columns.find((col) => col.key === columnKey);
    if (!column || !column.sortable) return;

    if (sortColumn === columnKey) {
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortDirection(null);
        setSortColumn(null);
      }
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  // Render sort icon
  const renderSortIcon = (columnKey: string) => {
    if (sortColumn !== columnKey) {
      return <ChevronsUpDown className="w-4 h-4 opacity-30" aria-hidden="true" />;
    }
    if (sortDirection === 'asc') {
      return <ChevronUp className="w-4 h-4" aria-label="Sorted ascending" />;
    }
    return <ChevronDown className="w-4 h-4" aria-label="Sorted descending" />;
  };

  const alignClasses = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
  };

  return (
    <div className={cn('w-full space-y-4', className)}>
      {/* Search Input */}
      {searchable && (
        <div className="relative max-w-md">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500"
            aria-hidden="true"
          />
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className={cn(
              'w-full pl-10 pr-4 py-2.5 rounded-xl',
              'bg-white dark:bg-gray-800',
              'border border-gray-200 dark:border-gray-700',
              'text-gray-900 dark:text-gray-100',
              'placeholder:text-gray-400 dark:placeholder:text-gray-500',
              'focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:border-transparent',
              'transition-all duration-200'
            )}
            aria-label="Search table"
          />
        </div>
      )}

      {/* Table Container */}
      <div className="relative overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700">
        <table className="w-full text-sm">
          {/* Table Header */}
          <thead
            className={cn(
              'bg-gray-50 dark:bg-gray-800/50',
              'border-b border-gray-200 dark:border-gray-700'
            )}
          >
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  style={{ width: column.width }}
                  className={cn(
                    compact ? 'px-4 py-3' : 'px-6 py-4',
                    'font-semibold text-gray-900 dark:text-gray-100',
                    alignClasses[column.align || 'left'],
                    column.sortable && 'cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-800',
                    'transition-colors duration-150'
                  )}
                  onClick={() => column.sortable && handleSort(column.key)}
                  role={column.sortable ? 'button' : undefined}
                  aria-sort={
                    sortColumn === column.key
                      ? sortDirection === 'asc'
                        ? 'ascending'
                        : 'descending'
                      : undefined
                  }
                >
                  <div className="flex items-center gap-2 justify-between">
                    <span>{column.header}</span>
                    {column.sortable && renderSortIcon(column.key)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>

          {/* Table Body */}
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-12 text-center">
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-5 h-5 border-2 border-sahool-600 border-t-transparent rounded-full animate-spin" />
                    <span className="text-gray-600 dark:text-gray-400">Loading...</span>
                  </div>
                </td>
              </tr>
            ) : paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-12 text-center">
                  <span className="text-gray-500 dark:text-gray-400">{emptyMessage}</span>
                </td>
              </tr>
            ) : (
              paginatedData.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className={cn(
                    'bg-white dark:bg-gray-900',
                    striped && rowIndex % 2 === 1 && 'bg-gray-50 dark:bg-gray-800/30',
                    hoverable && 'hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors duration-150',
                    onRowClick && 'cursor-pointer'
                  )}
                  onClick={() => onRowClick && onRowClick(row, rowIndex)}
                  role={onRowClick ? 'button' : undefined}
                  tabIndex={onRowClick ? 0 : undefined}
                  onKeyDown={(e) => {
                    if (onRowClick && (e.key === 'Enter' || e.key === ' ')) {
                      e.preventDefault();
                      onRowClick(row, rowIndex);
                    }
                  }}
                >
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={cn(
                        compact ? 'px-4 py-3' : 'px-6 py-4',
                        'text-gray-700 dark:text-gray-300',
                        alignClasses[column.align || 'left']
                      )}
                    >
                      {column.accessor(row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Showing {(currentPage - 1) * pageSize + 1} to{' '}
            {Math.min(currentPage * pageSize, sortedData.length)} of {sortedData.length} results
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className={cn(
                'p-2 rounded-lg',
                'border border-gray-200 dark:border-gray-700',
                'hover:bg-gray-50 dark:hover:bg-gray-800',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'transition-colors duration-150'
              )}
              aria-label="Previous page"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter((page) => {
                  return (
                    page === 1 ||
                    page === totalPages ||
                    Math.abs(page - currentPage) <= 1
                  );
                })
                .map((page, index, array) => {
                  const showEllipsis = index > 0 && page - array[index - 1] > 1;
                  return (
                    <div key={page} className="flex items-center gap-1">
                      {showEllipsis && (
                        <span className="px-2 text-gray-400">...</span>
                      )}
                      <button
                        onClick={() => setCurrentPage(page)}
                        className={cn(
                          'min-w-[2.5rem] px-3 py-2 rounded-lg text-sm font-medium',
                          'transition-colors duration-150',
                          page === currentPage
                            ? 'bg-sahool-600 text-white'
                            : 'hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                        )}
                        aria-label={`Page ${page}`}
                        aria-current={page === currentPage ? 'page' : undefined}
                      >
                        {page}
                      </button>
                    </div>
                  );
                })}
            </div>

            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className={cn(
                'p-2 rounded-lg',
                'border border-gray-200 dark:border-gray-700',
                'hover:bg-gray-50 dark:hover:bg-gray-800',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'transition-colors duration-150'
              )}
              aria-label="Next page"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

ModernTable.displayName = 'ModernTable';
