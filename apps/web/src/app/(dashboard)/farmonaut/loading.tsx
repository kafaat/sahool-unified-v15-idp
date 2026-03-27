/**
 * Farmonaut Satellite Monitoring - Loading Skeleton
 * هيكل تحميل مراقبة الأقمار الصناعية فارمونوت
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-8 bg-gray-200 rounded w-56 mb-2" />
          <div className="h-4 bg-gray-100 rounded w-72" />
        </div>
        <div className="flex gap-3">
          <div className="h-10 bg-gray-100 rounded-lg w-40" />
          <div className="h-10 bg-gray-200 rounded-lg w-28" />
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white rounded-lg border p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-100 rounded-lg" />
              <div className="flex-1">
                <div className="h-3 bg-gray-200 rounded w-20 mb-2" />
                <div className="h-6 bg-gray-200 rounded w-16 mb-1" />
                <div className="h-2 bg-gray-100 rounded w-24" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Map Control + Map */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border p-4 space-y-3">
          <div className="h-5 bg-gray-200 rounded w-28" />
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-8 bg-gray-100 rounded" />
          ))}
        </div>
        <div className="lg:col-span-3 bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b">
            <div className="h-5 bg-gray-200 rounded w-40" />
          </div>
          <div className="aspect-[16/9] bg-gray-100" />
          <div className="p-3 flex gap-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center gap-1">
                <div className="w-3 h-3 bg-gray-200 rounded-full" />
                <div className="h-3 bg-gray-100 rounded w-12" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 9-Direction Grid */}
      <div className="bg-white rounded-lg border p-6">
        <div className="h-5 bg-gray-200 rounded w-44 mb-4" />
        <div className="grid grid-cols-3 gap-2 max-w-md mx-auto">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="h-20 bg-gray-100 rounded-lg" />
          ))}
        </div>
      </div>

      {/* Time Series + Weather */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-4">
          <div className="h-5 bg-gray-200 rounded w-36 mb-4" />
          <div className="h-40 bg-gray-100 rounded" />
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="h-5 bg-gray-200 rounded w-36 mb-4" />
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-12 bg-gray-100 rounded" />
            ))}
          </div>
        </div>
      </div>

      {/* Field Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b">
          <div className="h-5 bg-gray-200 rounded w-28" />
        </div>
        <div className="p-4 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex gap-4 py-3 border-b border-gray-100 last:border-0">
              {Array.from({ length: 8 }).map((_, j) => (
                <div key={j} className="h-4 bg-gray-100 rounded flex-1" />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
