/**
 * Satellite Analytics Loading Skeleton
 * هيكل تحميل تحليلات الأقمار الصناعية
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header with controls skeleton */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-8 bg-gray-200 rounded w-64 mb-2" />
          <div className="h-4 bg-gray-100 rounded w-80" />
        </div>
        <div className="flex items-center gap-3">
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
          <div className="h-10 bg-gray-200 rounded-lg w-32" />
        </div>
      </div>

      {/* Stat cards skeleton */}
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

      {/* Satellite map skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <div className="h-5 bg-gray-200 rounded w-48" />
          <div className="h-4 bg-gray-100 rounded w-36" />
        </div>
        <div className="h-[500px] bg-gray-100" />
      </div>

      {/* NDVI trend chart + field details skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="h-5 bg-gray-200 rounded w-28" />
            <div className="h-9 bg-gray-100 rounded-lg w-48" />
          </div>
          <div className="h-80 bg-gray-100 rounded" />
        </div>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="h-5 bg-gray-200 rounded w-28 mb-4" />
          <div className="space-y-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="border-t border-gray-100 pt-4 first:border-0 first:pt-0">
                <div className="h-3 bg-gray-100 rounded w-20 mb-2" />
                <div className="h-5 bg-gray-200 rounded w-32" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Fields table skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <div className="h-5 bg-gray-200 rounded w-28" />
        </div>
        <div className="p-4 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex gap-4 py-3 border-b border-gray-100 last:border-0">
              <div className="h-4 bg-gray-100 rounded flex-1" />
              <div className="h-4 bg-gray-100 rounded w-16" />
              <div className="h-4 bg-gray-200 rounded w-12" />
              <div className="h-4 bg-gray-100 rounded w-12" />
              <div className="h-4 bg-gray-100 rounded w-16" />
              <div className="h-4 bg-gray-100 rounded w-20" />
              <div className="h-4 bg-gray-100 rounded w-8" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
