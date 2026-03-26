/**
 * Analytics Loading Skeleton
 * هيكل تحميل صفحة التحليلات
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-8 bg-gray-200 rounded w-56 mb-2" />
        <div className="h-4 bg-gray-100 rounded w-80" />
      </div>

      {/* Stat cards skeleton - 4 analytics KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-3">
              <div className="h-4 bg-gray-200 rounded w-20" />
              <div className="h-10 w-10 bg-gray-100 rounded-lg" />
            </div>
            <div className="h-8 bg-gray-200 rounded w-24 mb-2" />
            <div className="h-3 bg-gray-100 rounded w-28" />
          </div>
        ))}
      </div>

      {/* Main chart area skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="h-5 bg-gray-200 rounded w-44" />
          <div className="flex gap-2">
            <div className="h-8 bg-gray-100 rounded w-20" />
            <div className="h-8 bg-gray-100 rounded w-20" />
          </div>
        </div>
        <div className="h-80 bg-gray-100 rounded" />
      </div>

      {/* Two side-by-side charts */}
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
    </div>
  );
}
