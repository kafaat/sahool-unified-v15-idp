/**
 * Profitability Analytics Loading Skeleton
 * هيكل تحميل تحليل الربحية
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header with period selector skeleton */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-8 bg-gray-200 rounded w-44 mb-2" />
          <div className="h-4 bg-gray-100 rounded w-72" />
        </div>
        <div className="h-10 bg-gray-100 rounded-lg w-28" />
      </div>

      {/* Stat cards skeleton - 5 financial KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-xl border border-gray-100 shadow-sm p-6"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="h-4 bg-gray-200 rounded w-24" />
              <div className="h-10 w-10 bg-gray-100 rounded-lg" />
            </div>
            <div className="h-8 bg-gray-200 rounded w-20 mb-2" />
            <div className="h-3 bg-gray-100 rounded w-28" />
          </div>
        ))}
      </div>

      {/* Monthly trend chart skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="h-5 bg-gray-200 rounded w-48 mb-4" />
        <div className="h-80 bg-gray-100 rounded" />
      </div>

      {/* Two side-by-side charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="h-5 bg-gray-200 rounded w-40 mb-4" />
          <div className="h-80 bg-gray-100 rounded" />
        </div>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="h-5 bg-gray-200 rounded w-32 mb-4" />
          <div className="h-80 bg-gray-100 rounded" />
        </div>
      </div>

      {/* Crop details table skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <div className="h-5 bg-gray-200 rounded w-48" />
        </div>
        <div className="p-4 space-y-3">
          {/* Table header */}
          <div className="flex gap-4 pb-3 border-b border-gray-200">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="h-3 bg-gray-200 rounded flex-1" />
            ))}
          </div>
          {/* Table rows */}
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="flex gap-4 py-3 border-b border-gray-100 last:border-0"
            >
              {Array.from({ length: 7 }).map((_, j) => (
                <div key={j} className="h-4 bg-gray-100 rounded flex-1" />
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Season summary skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="h-5 bg-gray-200 rounded w-28 mb-4" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="border border-gray-100 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="h-4 bg-gray-200 rounded w-16" />
                <div className="h-5 w-5 bg-gray-100 rounded" />
              </div>
              <div className="space-y-2">
                {Array.from({ length: 4 }).map((_, j) => (
                  <div key={j} className="flex justify-between">
                    <div className="h-3 bg-gray-100 rounded w-16" />
                    <div className="h-3 bg-gray-200 rounded w-12" />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
