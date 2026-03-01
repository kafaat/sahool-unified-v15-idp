/**
 * Dashboard Loading Skeleton
 * هيكل تحميل لوحة التحكم الرئيسية
 */

export default function Loading() {
  return (
    <div className="space-y-6 animate-pulse" role="status" aria-label="جاري تحميل لوحة التحكم - Loading dashboard">
      <span className="sr-only">جاري تحميل لوحة التحكم - Loading dashboard</span>
      {/* Header skeleton */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="h-8 bg-gray-200 rounded w-48 mb-2" />
        <div className="h-4 bg-gray-100 rounded w-72" />
      </div>

      {/* Stat cards skeleton - 4 KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-xl border border-gray-100 shadow-sm p-6"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="h-4 bg-gray-200 rounded w-24" />
              <div className="h-10 w-10 bg-gray-100 rounded-lg" />
            </div>
            <div className="h-8 bg-gray-200 rounded w-20 mb-2" />
            <div className="h-3 bg-gray-100 rounded w-32" />
          </div>
        ))}
      </div>

      {/* Charts skeleton - 2 side-by-side charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Array.from({ length: 2 }).map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-xl border border-gray-100 shadow-sm p-6"
          >
            <div className="h-5 bg-gray-200 rounded w-40 mb-4" />
            <div className="h-64 bg-gray-100 rounded" />
          </div>
        ))}
      </div>

      {/* Activity list skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="h-5 bg-gray-200 rounded w-36 mb-4" />
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-4 py-3 border-b border-gray-100 last:border-0"
            >
              <div className="h-10 w-10 bg-gray-100 rounded-full" />
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-3 bg-gray-100 rounded w-1/2" />
              </div>
              <div className="h-4 bg-gray-100 rounded w-16" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
