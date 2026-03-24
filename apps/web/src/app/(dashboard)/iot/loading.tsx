/**
 * IoT Dashboard Loading Skeleton
 * هيكل تحميل صفحة إنترنت الأشياء
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-8 bg-gray-200 rounded w-48 mb-2" />
        <div className="h-4 bg-gray-100 rounded w-64" />
      </div>

      {/* Stat cards skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-100 p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 bg-gray-100 rounded-lg" />
              <div>
                <div className="h-7 bg-gray-200 rounded w-10 mb-1" />
                <div className="h-3 bg-gray-100 rounded w-20" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Real-time readings chart and device list */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="h-5 bg-gray-200 rounded w-40 mb-4" />
          <div className="h-64 bg-gray-100 rounded" />
        </div>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="h-5 bg-gray-200 rounded w-32 mb-4" />
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="h-8 w-8 bg-gray-200 rounded-full" />
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-28 mb-1" />
                  <div className="h-3 bg-gray-100 rounded w-20" />
                </div>
                <div className="h-5 bg-gray-100 rounded-full w-14" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="h-5 bg-gray-200 rounded w-28 mb-4" />
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
              <div className="h-8 w-8 bg-gray-200 rounded" />
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-1" />
                <div className="h-3 bg-gray-100 rounded w-1/2" />
              </div>
              <div className="h-6 bg-gray-100 rounded-full w-16" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
