/**
 * Soil Map Loading Skeleton
 * هيكل تحميل صفحة soil-map
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse" role="status" aria-label="جاري التحميل - Loading">
      <span className="sr-only">جاري التحميل - Loading</span>

      {/* Header skeleton */}
      <div>
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-56 mb-2" />
        <div className="h-4 bg-gray-100 dark:bg-gray-800 rounded w-80" />
      </div>

      {/* Stat cards skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm p-6">
            <div className="flex items-center justify-between mb-3">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24" />
              <div className="h-10 w-10 bg-gray-100 dark:bg-gray-700 rounded-lg" />
            </div>
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-2" />
            <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded w-28" />
          </div>
        ))}
      </div>

      {/* Content skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm p-6">
        <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-40 mb-4" />
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 py-3 border-b border-gray-100 dark:border-gray-700 last:border-0">
              <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded" />
              <div className="h-4 flex-1 bg-gray-100 dark:bg-gray-800 rounded" />
              <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
