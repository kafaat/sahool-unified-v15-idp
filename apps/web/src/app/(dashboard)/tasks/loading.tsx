/**
 * Tasks Loading Skeleton
 * هيكل تحميل صفحة المهام
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header with action button skeleton */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-8 bg-gray-200 rounded w-36 mb-2" />
          <div className="h-4 bg-gray-100 rounded w-36" />
        </div>
        <div className="flex gap-3">
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
          <div className="h-10 bg-gray-200 rounded-lg w-28" />
        </div>
      </div>

      {/* Stat cards skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-100 p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 bg-gray-100 rounded-lg" />
              <div>
                <div className="h-7 bg-gray-200 rounded w-10 mb-1" />
                <div className="h-3 bg-gray-100 rounded w-16" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Filters skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px] h-10 bg-gray-100 rounded-lg" />
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
          <div className="h-10 bg-gray-100 rounded-lg w-10" />
        </div>
      </div>

      {/* Tasks table skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden p-4 space-y-0">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="flex items-center gap-4 py-4 border-b border-gray-100 last:border-0"
          >
            <div className="h-5 w-5 bg-gray-100 rounded" />
            <div className="flex-1">
              <div className="h-4 bg-gray-200 rounded w-48 mb-1" />
              <div className="h-3 bg-gray-100 rounded w-32" />
            </div>
            <div className="h-5 bg-gray-100 rounded-full w-14" />
            <div className="h-5 bg-gray-100 rounded-full w-16" />
            <div className="h-4 bg-gray-100 rounded w-20" />
            <div className="flex gap-1">
              <div className="h-8 w-8 bg-gray-100 rounded" />
              <div className="h-8 w-8 bg-gray-100 rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
