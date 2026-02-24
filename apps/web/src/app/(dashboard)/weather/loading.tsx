/**
 * Weather Loading Skeleton
 * هيكل تحميل صفحة الطقس
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-8 bg-gray-200 rounded w-40 mb-2" />
        <div className="h-4 bg-gray-100 rounded w-72" />
      </div>

      {/* Current weather card skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-6">
          <div className="h-20 w-20 bg-gray-100 rounded-xl" />
          <div className="flex-1">
            <div className="h-10 bg-gray-200 rounded w-24 mb-2" />
            <div className="h-4 bg-gray-100 rounded w-40" />
          </div>
          <div className="grid grid-cols-3 gap-6">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="text-center">
                <div className="h-3 bg-gray-100 rounded w-16 mx-auto mb-2" />
                <div className="h-6 bg-gray-200 rounded w-12 mx-auto" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Forecast cards skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {Array.from({ length: 7 }).map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 text-center"
          >
            <div className="h-3 bg-gray-100 rounded w-12 mx-auto mb-3" />
            <div className="h-10 w-10 bg-gray-100 rounded-full mx-auto mb-3" />
            <div className="h-5 bg-gray-200 rounded w-16 mx-auto mb-1" />
            <div className="h-3 bg-gray-100 rounded w-10 mx-auto" />
          </div>
        ))}
      </div>

      {/* Weather charts skeleton */}
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
