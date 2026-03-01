/**
 * Copilot Management Loading Skeleton
 * هيكل تحميل صفحة المساعد الذكي
 *
 * Matches the copilot page layout with tabs and dashboard content.
 */

export default function CopilotLoading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-8 w-56 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-4 w-72 bg-gray-200 dark:bg-gray-700 rounded mt-2" />
      </div>

      {/* Tabs skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div className="flex border-b border-gray-100 dark:border-gray-700">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className={`px-5 py-3 ${i === 0 ? "border-b-2 border-gray-300" : ""}`}
            >
              <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
            </div>
          ))}
        </div>
      </div>

      {/* Dashboard stats skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-100 dark:border-gray-700"
          >
            <div className="mb-3">
              <div className="h-9 w-9 bg-gray-200 dark:bg-gray-700 rounded-lg" />
            </div>
            <div className="h-7 w-12 bg-gray-200 dark:bg-gray-700 rounded mb-1" />
            <div className="h-3 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        ))}
      </div>

      {/* Quick actions skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-100 dark:border-gray-700">
        <div className="h-5 w-40 bg-gray-200 dark:bg-gray-700 rounded mb-4" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl"
            >
              <div className="h-9 w-9 bg-gray-200 dark:bg-gray-600 rounded-lg" />
              <div className="flex-1">
                <div className="h-4 w-36 bg-gray-200 dark:bg-gray-600 rounded mb-1" />
                <div className="h-3 w-28 bg-gray-200 dark:bg-gray-600 rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Service status skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-100 dark:border-gray-700">
        <div className="h-5 w-36 bg-gray-200 dark:bg-gray-700 rounded mb-4" />
        <div className="flex items-center gap-3">
          <div className="h-3 w-3 bg-gray-200 dark:bg-gray-700 rounded-full" />
          <div className="h-4 w-40 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
      </div>
    </div>
  );
}
