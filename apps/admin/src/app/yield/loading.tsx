/**
 * Yield Prediction Loading Skeleton
 * هيكل تحميل صفحة التنبؤ بالإنتاجية
 *
 * Matches the yield prediction page layout with form and results panels.
 */

export default function YieldLoading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-4 w-64 bg-gray-200 dark:bg-gray-700 rounded mt-2" />
      </div>

      {/* Two-column layout: form + results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form panel */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-100 dark:border-gray-700">
          <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-6" />
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i}>
                <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
                <div className="h-10 w-full bg-gray-100 dark:bg-gray-700 rounded-lg" />
              </div>
            ))}
            <div className="h-12 w-full bg-gray-200 dark:bg-gray-700 rounded-lg mt-6" />
          </div>
        </div>

        {/* Results panel */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-100 dark:border-gray-700">
          <div className="h-5 w-28 bg-gray-200 dark:bg-gray-700 rounded mb-6" />
          <div className="flex items-center justify-center h-64">
            <div className="text-center space-y-3">
              <div className="h-16 w-16 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto" />
              <div className="h-4 w-48 bg-gray-200 dark:bg-gray-700 rounded mx-auto" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
