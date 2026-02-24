/**
 * Reusable table page loading skeleton for admin feature routes.
 * هيكل تحميل مشترك لصفحات الجداول في لوحة التحكم
 *
 * Provides consistent loading UI for pages that follow the
 * Header -> Stats -> Filters -> DataTable layout pattern.
 */

interface TablePageSkeletonProps {
  /** Number of stat cards to show (default: 4) */
  statCards?: number;
  /** Number of filter inputs to show (default: 3) */
  filterInputs?: number;
  /** Number of table rows to show (default: 6) */
  tableRows?: number;
  /** Whether to show an "add" button in the filter bar */
  showAddButton?: boolean;
}

export default function TablePageSkeleton({
  statCards = 4,
  filterInputs = 3,
  tableRows = 6,
  showAddButton = false,
}: TablePageSkeletonProps) {
  return (
    <div className="p-6 space-y-6 animate-pulse" dir="rtl">
      {/* Header skeleton */}
      <div>
        <div className="h-8 w-40 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded mt-2" />
      </div>

      {/* Stats cards skeleton */}
      <div
        className="grid gap-4"
        style={{
          gridTemplateColumns: `repeat(${Math.min(statCards, 4)}, minmax(0, 1fr))`,
        }}
      >
        {Array.from({ length: statCards }).map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg flex-shrink-0" />
              <div>
                <div className="h-7 w-10 bg-gray-200 dark:bg-gray-700 rounded mb-1" />
                <div className="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Filter bar skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px] h-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          {Array.from({ length: filterInputs }).map((_, i) => (
            <div
              key={i}
              className="h-10 w-28 bg-gray-200 dark:bg-gray-700 rounded-lg"
            />
          ))}
          <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          {showAddButton && (
            <div className="h-10 w-28 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          )}
        </div>
      </div>

      {/* Table skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        {Array.from({ length: tableRows }).map((_, i) => (
          <div
            key={i}
            className="p-4 border-b border-gray-100 dark:border-gray-700 last:border-0"
          >
            <div className="h-12 bg-gray-100 dark:bg-gray-700 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
