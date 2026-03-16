"use client";

/**
 * Enhanced Data Table Component
 * جدول البيانات المحسن مع الفرز والتصفية والتحديد المتعدد
 */

import React, { useState, useMemo, useCallback } from "react";
import { cn } from "@/lib/utils";
import {
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Check,
  Minus,
} from "lucide-react";

export type SortDirection = "asc" | "desc" | null;

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T, index: number) => React.ReactNode;
  sortable?: boolean;
  sortKey?: string;
  className?: string;
  headerClassName?: string;
  width?: string;
  align?: "left" | "center" | "right";
}

export interface EnhancedDataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  onRowClick?: (item: T) => void;
  onRowDoubleClick?: (item: T) => void;
  emptyMessage?: string;
  emptyMessageAr?: string;
  caption?: string;
  captionAr?: string;
  className?: string;
  isLoading?: boolean;
  // Pagination
  pagination?: boolean;
  pageSize?: number;
  pageSizeOptions?: number[];
  // Selection
  selectable?: boolean;
  selectedKeys?: Set<string>;
  onSelectionChange?: (selectedKeys: Set<string>) => void;
  // Sorting
  sortColumn?: string;
  sortDirection?: SortDirection;
  onSort?: (column: string, direction: SortDirection) => void;
  // Styling
  striped?: boolean;
  hoverable?: boolean;
  compact?: boolean;
  bordered?: boolean;
  stickyHeader?: boolean;
  maxHeight?: string;
}

function EnhancedDataTableInner<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  onRowDoubleClick,
  emptyMessage = "No data available",
  emptyMessageAr = "لا توجد بيانات",
  caption,
  captionAr,
  className = "",
  isLoading = false,
  pagination = true,
  pageSize: initialPageSize = 10,
  pageSizeOptions = [5, 10, 25, 50, 100],
  selectable = false,
  selectedKeys: controlledSelectedKeys,
  onSelectionChange,
  sortColumn: controlledSortColumn,
  sortDirection: controlledSortDirection,
  onSort,
  striped = true,
  hoverable = true,
  compact = false,
  bordered = false,
  stickyHeader = false,
  maxHeight,
}: EnhancedDataTableProps<T>) {
  // Internal state for uncontrolled mode
  const [internalSelectedKeys, setInternalSelectedKeys] = useState<Set<string>>(
    new Set()
  );
  const [internalSortColumn, setInternalSortColumn] = useState<string | null>(
    null
  );
  const [internalSortDirection, setInternalSortDirection] =
    useState<SortDirection>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);

  // Determine if controlled or uncontrolled
  const selectedKeys = controlledSelectedKeys ?? internalSelectedKeys;
  const sortColumn = controlledSortColumn ?? internalSortColumn;
  const sortDirection = controlledSortDirection ?? internalSortDirection;

  const handleSelectionChange = useCallback(
    (keys: Set<string>) => {
      if (onSelectionChange) {
        onSelectionChange(keys);
      } else {
        setInternalSelectedKeys(keys);
      }
    },
    [onSelectionChange]
  );

  const handleSort = useCallback(
    (column: string) => {
      let newDirection: SortDirection = "asc";
      if (sortColumn === column) {
        if (sortDirection === "asc") newDirection = "desc";
        else if (sortDirection === "desc") newDirection = null;
      }

      if (onSort) {
        onSort(column, newDirection);
      } else {
        setInternalSortColumn(newDirection ? column : null);
        setInternalSortDirection(newDirection);
      }
    },
    [sortColumn, sortDirection, onSort]
  );

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortColumn || !sortDirection) return data;

    return [...data].sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[sortColumn];
      const bVal = (b as Record<string, unknown>)[sortColumn];

      if (aVal === bVal) return 0;
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;

      const comparison =
        typeof aVal === "string" && typeof bVal === "string"
          ? aVal.localeCompare(bVal, "ar")
          : aVal < bVal
            ? -1
            : 1;

      return sortDirection === "asc" ? comparison : -comparison;
    });
  }, [data, sortColumn, sortDirection]);

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;
    const start = (currentPage - 1) * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, pagination, currentPage, pageSize]);

  const totalPages = Math.ceil(sortedData.length / pageSize);

  // Selection handlers
  const handleSelectAll = useCallback(() => {
    const pageKeys = new Set(paginatedData.map(keyExtractor));
    const allSelected = paginatedData.every((item) =>
      selectedKeys.has(keyExtractor(item))
    );

    if (allSelected) {
      // Deselect all on current page
      const newSelection = new Set(selectedKeys);
      pageKeys.forEach((key) => newSelection.delete(key));
      handleSelectionChange(newSelection);
    } else {
      // Select all on current page
      const newSelection = new Set(selectedKeys);
      pageKeys.forEach((key) => newSelection.add(key));
      handleSelectionChange(newSelection);
    }
  }, [paginatedData, selectedKeys, keyExtractor, handleSelectionChange]);

  const handleSelectRow = useCallback(
    (key: string) => {
      const newSelection = new Set(selectedKeys);
      if (newSelection.has(key)) {
        newSelection.delete(key);
      } else {
        newSelection.add(key);
      }
      handleSelectionChange(newSelection);
    },
    [selectedKeys, handleSelectionChange]
  );

  const isAllSelected =
    paginatedData.length > 0 &&
    paginatedData.every((item) => selectedKeys.has(keyExtractor(item)));
  const isSomeSelected =
    paginatedData.some((item) => selectedKeys.has(keyExtractor(item))) &&
    !isAllSelected;

  // Render sort icon
  const renderSortIcon = (column: Column<T>) => {
    if (!column.sortable) return null;
    const colKey = column.sortKey || column.key;
    const isActive = sortColumn === colKey;

    return (
      <span className="inline-flex mr-1">
        {isActive && sortDirection === "asc" ? (
          <ChevronUp className="w-4 h-4 text-sahool-600" />
        ) : isActive && sortDirection === "desc" ? (
          <ChevronDown className="w-4 h-4 text-sahool-600" />
        ) : (
          <ChevronsUpDown className="w-4 h-4 text-gray-400" />
        )}
      </span>
    );
  };

  // Loading skeleton
  if (isLoading) {
    return (
      <div
        className={cn(
          "bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden",
          className
        )}
      >
        <div className="animate-pulse">
          <div className="h-12 bg-gray-100 dark:bg-gray-700"></div>
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="h-14 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800"
            ></div>
          ))}
        </div>
      </div>
    );
  }

  // Empty state
  if (data.length === 0) {
    return (
      <div
        className={cn(
          "bg-white dark:bg-gray-800 rounded-xl shadow-sm p-12 text-center",
          className
        )}
      >
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
          <svg
            className="w-8 h-8 text-gray-400 dark:text-gray-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
        </div>
        <p className="text-gray-500 dark:text-gray-400 text-lg">{emptyMessageAr}</p>
        <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden",
        bordered && "border border-gray-200 dark:border-gray-700",
        className
      )}
    >
      <div
        className={cn("overflow-x-auto", maxHeight && "overflow-y-auto")}
        style={{ maxHeight }}
      >
        <table className="w-full">
          {(captionAr || caption) && (
            <caption className="sr-only">{captionAr || caption}</caption>
          )}
          <thead
            className={cn(
              "bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700",
              stickyHeader && "sticky top-0 z-10"
            )}
          >
            <tr>
              {selectable && (
                <th className="w-12 px-4 py-3" scope="col">
                  <button
                    onClick={handleSelectAll}
                    className={cn(
                      "w-5 h-5 rounded border-2 flex items-center justify-center transition-colors",
                      isAllSelected
                        ? "bg-sahool-600 border-sahool-600 text-white"
                        : isSomeSelected
                          ? "bg-sahool-100 border-sahool-600"
                          : "border-gray-300 dark:border-gray-600 hover:border-sahool-500"
                    )}
                    aria-label="تحديد الكل"
                  >
                    {isAllSelected && <Check className="w-3 h-3" />}
                    {isSomeSelected && <Minus className="w-3 h-3 text-sahool-600" />}
                  </button>
                </th>
              )}
              {columns.map((col) => {
                const colKey = col.sortKey || col.key;
                const isActiveSortCol = sortColumn === colKey;
                const ariaSortValue = isActiveSortCol && sortDirection === "asc"
                  ? "ascending" as const
                  : isActiveSortCol && sortDirection === "desc"
                    ? "descending" as const
                    : undefined;

                return (
                <th
                  key={col.key}
                  scope="col"
                  className={cn(
                    "text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider",
                    compact ? "px-4 py-2" : "px-6 py-3",
                    col.align === "center" && "text-center",
                    col.align === "left" && "text-left",
                    col.align === "right" || !col.align ? "text-right" : "",
                    col.sortable && "cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-800",
                    col.headerClassName
                  )}
                  style={{ width: col.width }}
                  onClick={() =>
                    col.sortable && handleSort(colKey)
                  }
                  aria-sort={ariaSortValue}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.header}
                    {renderSortIcon(col)}
                  </span>
                </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {paginatedData.map((item, index) => {
              const key = keyExtractor(item);
              const isSelected = selectedKeys.has(key);

              return (
                <tr
                  key={key}
                  onClick={() => onRowClick?.(item)}
                  onDoubleClick={() => onRowDoubleClick?.(item)}
                  onKeyDown={(e) => {
                    if (onRowClick && (e.key === "Enter" || e.key === " ")) {
                      e.preventDefault();
                      onRowClick(item);
                    }
                  }}
                  tabIndex={onRowClick ? 0 : undefined}
                  role={onRowClick ? "button" : undefined}
                  className={cn(
                    "transition-colors focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:ring-inset",
                    onRowClick && "cursor-pointer",
                    hoverable && "hover:bg-gray-50 dark:hover:bg-gray-700/50",
                    striped && index % 2 === 1 && "bg-gray-50/50 dark:bg-gray-800/50",
                    isSelected && "bg-sahool-50 dark:bg-sahool-900/30"
                  )}
                >
                  {selectable && (
                    <td className="w-12 px-4 py-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectRow(key);
                        }}
                        className={cn(
                          "w-5 h-5 rounded border-2 flex items-center justify-center transition-colors",
                          isSelected
                            ? "bg-sahool-600 border-sahool-600 text-white"
                            : "border-gray-300 dark:border-gray-600 hover:border-sahool-500"
                        )}
                        aria-label={isSelected ? "إلغاء التحديد" : "تحديد"}
                      >
                        {isSelected && <Check className="w-3 h-3" />}
                      </button>
                    </td>
                  )}
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={cn(
                        "text-sm text-gray-900 dark:text-gray-100",
                        compact ? "px-4 py-2" : "px-6 py-4",
                        col.align === "center" && "text-center",
                        col.align === "left" && "text-left",
                        col.className
                      )}
                    >
                      {col.render
                        ? col.render(item, index)
                        : String(
                            (item as Record<string, unknown>)[col.key] ?? ""
                          )}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 0 && (
        <div className="px-6 py-4 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              عرض{" "}
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {(currentPage - 1) * pageSize + 1}
              </span>{" "}
              -{" "}
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {Math.min(currentPage * pageSize, sortedData.length)}
              </span>{" "}
              من{" "}
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {sortedData.length}
              </span>{" "}
              نتيجة
            </span>

            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2 py-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              aria-label="عدد الصفوف في كل صفحة"
            >
              {pageSizeOptions.map((size) => (
                <option key={size} value={size}>
                  {size} صف
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="الصفحة الأولى"
            >
              <ChevronsRight className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="الصفحة السابقة"
            >
              <ChevronRight className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>

            <span className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400">
              صفحة{" "}
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {currentPage}
              </span>{" "}
              من{" "}
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {totalPages}
              </span>
            </span>

            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="الصفحة التالية"
            >
              <ChevronLeft className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="الصفحة الأخيرة"
            >
              <ChevronsLeft className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// Memoize to prevent unnecessary re-renders when parent state changes
const EnhancedDataTable = React.memo(EnhancedDataTableInner) as typeof EnhancedDataTableInner;
export default EnhancedDataTable;
