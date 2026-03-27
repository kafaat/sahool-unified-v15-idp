/**
 * Irrigation Loading Skeleton
 * هيكل تحميل صفحة الري الذكي
 *
 * Matches the irrigation page layout with stats, tab bar, and schedule cards.
 */

export default function IrrigationLoading() {
  return (
    <div
      className="p-6 space-y-6 animate-pulse"
      role="status"
      aria-label="جاري تحميل الري - Loading irrigation"
    >
      <span className="sr-only">جاري تحميل الري - Loading irrigation</span>
      {/* Header skeleton */}
      <div>
        <div className="h-8 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-4 w-72 bg-gray-200 dark:bg-gray-700 rounded mt-2" />
      </div>

      {/* Stats cards skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded" />
              <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
            </div>
            <div className="h-8 w-16 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
            <div className="h-3 w-10 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        ))}
      </div>

      {/* Tabs skeleton */}
      <div className="flex gap-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 w-fit">
        {Array.from({ length: 3 }).map((_, i) => (
          <div
            key={i}
            className={`h-10 w-32 rounded-md ${i === 0 ? 'bg-white dark:bg-gray-700 shadow-sm' : 'bg-transparent'}`}
          />
        ))}
      </div>

      {/* Refresh button */}
      <div className="flex justify-end">
        <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
      </div>

      {/* Schedule content - 3-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Schedule cards */}
        <div className="lg:col-span-2 space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-5"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 bg-gray-200 dark:bg-gray-700 rounded-lg" />
                  <div>
                    <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-1" />
                    <div className="h-3 w-48 bg-gray-200 dark:bg-gray-700 rounded" />
                  </div>
                </div>
                <div className="h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded-full" />
              </div>
              <div className="grid grid-cols-3 gap-4">
                {Array.from({ length: 3 }).map((_, j) => (
                  <div key={j} className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="h-6 w-16 bg-gray-200 dark:bg-gray-600 rounded mx-auto mb-1" />
                    <div className="h-3 w-10 bg-gray-200 dark:bg-gray-600 rounded mx-auto" />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
            <div className="h-5 w-20 bg-gray-200 dark:bg-gray-700 rounded mb-3" />
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-10 bg-gray-50 dark:bg-gray-700 rounded" />
              ))}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
            <div className="h-5 w-28 bg-gray-200 dark:bg-gray-700 rounded mb-3" />
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex justify-between">
                  <div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
                  <div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
