/**
 * Precision Agriculture Route Group Loading Skeleton
 * هيكل تحميل صفحات الزراعة الدقيقة
 *
 * Provides instant visual feedback during navigation to precision agriculture pages
 * (pivot, VRA, spray, GDD). Enables streaming via React Suspense.
 */

export default function PrecisionAgricultureLoading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-8 w-64 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-4 w-80 bg-gray-200 dark:bg-gray-700 rounded mt-2" />
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
            <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        ))}
      </div>

      {/* Action bar skeleton */}
      <div className="flex items-center justify-between">
        <div className="h-10 w-44 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
      </div>

      {/* Main content area - 3-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column - list items */}
        <div className="space-y-4">
          <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="h-5 w-40 bg-gray-200 dark:bg-gray-700 rounded" />
                <div className="h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded-full" />
              </div>
              <div className="h-40 bg-gray-100 dark:bg-gray-700 rounded-lg" />
              <div className="mt-3 grid grid-cols-2 gap-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
              </div>
            </div>
          ))}
        </div>

        {/* Right columns - detail panel */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="h-5 w-28 bg-gray-200 dark:bg-gray-700 rounded" />
              <div className="h-6 w-20 bg-gray-200 dark:bg-gray-700 rounded-full" />
            </div>
            <div className="flex gap-3 mb-6">
              <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
              <div className="h-10 w-28 bg-gray-200 dark:bg-gray-700 rounded-lg" />
              <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="h-6 w-8 bg-gray-200 dark:bg-gray-600 rounded mx-auto mb-1" />
                  <div className="h-3 w-14 bg-gray-200 dark:bg-gray-600 rounded mx-auto" />
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6">
            <div className="h-5 w-36 bg-gray-200 dark:bg-gray-700 rounded mb-4" />
            <div className="h-48 bg-gray-100 dark:bg-gray-700 rounded" />
          </div>
        </div>
      </div>
    </div>
  );
}
