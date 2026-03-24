/**
 * Crop Health Loading Skeleton
 * هيكل تحميل صفحة صحة المحصول
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-8 bg-gray-200 rounded w-56 mb-2" />
        <div className="h-4 bg-gray-100 rounded w-80" />
      </div>

      {/* Stat cards skeleton - 4 health KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-3">
              <div className="h-4 bg-gray-200 rounded w-24" />
              <div className="h-10 w-10 bg-gray-100 rounded-lg" />
            </div>
            <div className="h-8 bg-gray-200 rounded w-16 mb-2" />
            <div className="h-3 bg-gray-100 rounded w-28" />
          </div>
        ))}
      </div>

      {/* Health overview and diagnosis cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Health status chart skeleton */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="h-5 bg-gray-200 rounded w-40 mb-4" />
          <div className="h-64 bg-gray-100 rounded" />
        </div>

        {/* Recent diagnoses skeleton */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="h-5 bg-gray-200 rounded w-36 mb-4" />
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="h-12 w-12 bg-gray-200 rounded-lg flex-shrink-0" />
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-gray-100 rounded w-1/2 mb-1" />
                  <div className="h-3 bg-gray-100 rounded w-2/3" />
                </div>
                <div className="h-6 bg-gray-100 rounded-full w-16" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Disease/pest alerts table skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <div className="h-5 bg-gray-200 rounded w-40" />
          <div className="h-8 bg-gray-100 rounded w-28" />
        </div>
        <div className="p-4 space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-4 py-3 border-b border-gray-100 last:border-0"
            >
              <div className="h-8 w-8 bg-gray-200 rounded" />
              <div className="h-4 flex-1 bg-gray-100 rounded" />
              <div className="h-4 w-20 bg-gray-200 rounded" />
              <div className="h-6 w-16 bg-gray-100 rounded-full" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
