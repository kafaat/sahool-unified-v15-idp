"use client";

// Data Table Component
// جدول البيانات

import { memo, useCallback, useMemo } from "react";
import { cn } from "@/lib/utils";

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

// Memoized loading skeleton row component
const LoadingRow = memo(function LoadingRow({ index }: { index: number }) {
  return (
    <div
      key={index}
      className="h-16 border-t border-gray-100 bg-gray-50"
    ></div>
  );
});

// Memoized table row component to prevent unnecessary re-renders
const TableRow = memo(function TableRow<T>({
  item,
  columns,
  itemKey,
  onRowClick,
  isClickable,
}: {
  item: T;
  columns: Column<T>[];
  itemKey: string;
  onRowClick?: (item: T) => void;
  isClickable: boolean;
}) {
  const handleClick = useCallback(() => {
    onRowClick?.(item);
  }, [item, onRowClick]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (onRowClick && (e.key === "Enter" || e.key === " ")) {
        e.preventDefault();
        onRowClick(item);
      }
    },
    [item, onRowClick]
  );

  return (
    <tr
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={isClickable ? 0 : undefined}
      role={isClickable ? "button" : undefined}
      aria-label={isClickable ? "اضغط للتفاصيل" : undefined}
      className={cn(
        "hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-inset",
        isClickable && "cursor-pointer",
      )}
    >
      {columns.map((col) => (
        <td
          key={col.key}
          className={cn("px-6 py-4 text-sm", col.className)}
        >
          {col.render
            ? col.render(item)
            : String(
                (item as Record<string, unknown>)[col.key] ?? "",
              )}
        </td>
      ))}
    </tr>
  );
}) as <T>(props: {
  item: T;
  columns: Column<T>[];
  itemKey: string;
  onRowClick?: (item: T) => void;
  isClickable: boolean;
}) => React.ReactElement;

function DataTable<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  emptyMessage = "لا توجد بيانات",
  className = "",
  isLoading = false,
}: DataTableProps<T>) {
  // Memoize whether rows are clickable
  const isClickable = useMemo(() => !!onRowClick, [onRowClick]);

  // Memoize loading skeleton indices
  const loadingIndices = useMemo(() => Array.from({ length: 5 }, (_, i) => i), []);

  if (isLoading) {
    return (
      <div
        className={cn(
          "bg-white rounded-xl shadow-sm overflow-hidden",
          className,
        )}
      >
        <div className="animate-pulse">
          <div className="h-12 bg-gray-100"></div>
          {loadingIndices.map((i) => (
            <LoadingRow key={i} index={i} />
          ))}
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div
        className={cn(
          "bg-white rounded-xl shadow-sm p-8 text-center",
          className,
        )}
      >
        <p className="text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div
      className={cn("bg-white rounded-xl shadow-sm overflow-hidden", className)}
    >
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    "px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider",
                    col.className,
                  )}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map((item) => {
              const itemKey = keyExtractor(item);
              return (
                <TableRow
                  key={itemKey}
                  item={item}
                  columns={columns}
                  itemKey={itemKey}
                  onRowClick={onRowClick}
                  isClickable={isClickable}
                />
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Memoized export to prevent unnecessary re-renders
export default memo(DataTable) as typeof DataTable;
