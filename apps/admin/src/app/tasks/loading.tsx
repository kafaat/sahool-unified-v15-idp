/**
 * Tasks Management Loading Skeleton
 * هيكل تحميل صفحة إدارة المهام
 *
 * Matches the tasks page layout with stats, filter bar, and data table.
 */

export default function TasksLoading() {
  return (
    <div
      className="p-6 space-y-6 animate-pulse"
      role="status"
      aria-label="جاري تحميل المهام - Loading tasks"
    >
      <span className="sr-only">جاري تحميل المهام - Loading tasks</span>
      {/* Header skeleton */}
      <div>
        <div className="h-8 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-4 w-28 bg-gray-200 dark:bg-gray-700 rounded mt-2" />
      </div>

      {/* Stats cards skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
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
          <div className="h-10 w-28 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          <div className="h-10 w-28 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          <div className="h-10 w-28 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          <div className="h-10 w-28 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        </div>
      </div>

      {/* Table skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="p-4 border-b border-gray-100 dark:border-gray-700 last:border-0">
            <div className="h-14 bg-gray-100 dark:bg-gray-700 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
