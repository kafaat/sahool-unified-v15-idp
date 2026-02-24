/**
 * Reports Loading Skeleton
 * هيكل تحميل صفحة التقارير
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header with actions skeleton */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-8 bg-gray-200 rounded w-36 mb-2" />
          <div className="h-4 bg-gray-100 rounded w-56" />
        </div>
        <div className="flex gap-3">
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
          <div className="h-10 bg-gray-200 rounded-lg w-32" />
        </div>
      </div>

      {/* Filters skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="h-10 bg-gray-100 rounded-lg w-36" />
          <div className="h-10 bg-gray-100 rounded-lg w-32" />
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
        </div>
      </div>

      {/* Summary charts skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="h-5 bg-gray-200 rounded w-36 mb-4" />
          <div className="h-64 bg-gray-100 rounded" />
        </div>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="h-5 bg-gray-200 rounded w-32 mb-4" />
          <div className="h-64 bg-gray-100 rounded" />
        </div>
      </div>

      {/* Reports list skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <div className="h-5 bg-gray-200 rounded w-32" />
        </div>
        <div className="p-4 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-4 py-3 border-b border-gray-100 last:border-0"
            >
              <div className="h-8 w-8 bg-gray-100 rounded" />
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-48 mb-1" />
                <div className="h-3 bg-gray-100 rounded w-32" />
              </div>
              <div className="h-4 bg-gray-100 rounded w-20" />
              <div className="h-5 bg-gray-100 rounded-full w-16" />
              <div className="h-8 w-8 bg-gray-100 rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
