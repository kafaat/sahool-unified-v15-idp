/**
 * VRA Management Loading Skeleton
 * هيكل تحميل صفحة التطبيق المتغير
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-8 bg-gray-200 rounded w-64 mb-2" />
        <div className="h-4 bg-gray-100 rounded w-80" />
      </div>

      {/* Stat cards skeleton - 4 VRA KPIs */}
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
            <div className="h-8 bg-gray-200 rounded w-12 mb-2" />
            <div className="h-3 bg-gray-100 rounded w-28" />
          </div>
        ))}
      </div>

      {/* Filters bar skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="h-5 w-5 bg-gray-100 rounded" />
            <div className="h-4 bg-gray-200 rounded w-12" />
          </div>
          <div className="h-10 bg-gray-100 rounded-lg w-32" />
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
          <div className="ml-auto h-10 bg-gray-200 rounded-lg w-32" />
        </div>
      </div>

      {/* Prescriptions table skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-4 space-y-0">
          {/* Table header */}
          <div className="flex items-center gap-4 py-3 border-b border-gray-200">
            <div className="h-3 bg-gray-200 rounded flex-1" />
            <div className="h-3 bg-gray-200 rounded w-12" />
            <div className="h-3 bg-gray-200 rounded w-16" />
            <div className="h-3 bg-gray-200 rounded w-12" />
            <div className="h-3 bg-gray-200 rounded w-16" />
            <div className="h-3 bg-gray-200 rounded w-16" />
            <div className="h-3 bg-gray-200 rounded w-20" />
            <div className="h-3 bg-gray-200 rounded w-16" />
          </div>
          {/* Table rows */}
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-4 py-4 border-b border-gray-100 last:border-0"
            >
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-28 mb-1" />
                <div className="h-3 bg-gray-100 rounded w-20" />
              </div>
              <div className="h-4 bg-gray-100 rounded w-10" />
              <div className="h-4 bg-gray-100 rounded w-16" />
              <div className="h-4 bg-gray-100 rounded w-8" />
              <div className="h-4 bg-gray-100 rounded w-16" />
              <div className="h-5 bg-gray-100 rounded-full w-16" />
              <div className="h-4 bg-gray-100 rounded w-20" />
              <div className="flex gap-1">
                <div className="h-7 w-7 bg-gray-100 rounded" />
                <div className="h-7 w-7 bg-gray-100 rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
