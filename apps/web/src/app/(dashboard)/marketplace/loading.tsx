/**
 * Marketplace Loading Skeleton
 * هيكل تحميل صفحة السوق
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header with search skeleton */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-8 bg-gray-200 rounded w-36 mb-2" />
          <div className="h-4 bg-gray-100 rounded w-56" />
        </div>
        <div className="h-10 bg-gray-200 rounded-lg w-32" />
      </div>

      {/* Search and filters skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px] h-10 bg-gray-100 rounded-lg" />
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
          <div className="h-10 bg-gray-100 rounded-lg w-28" />
        </div>
      </div>

      {/* Product cards grid skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
          >
            <div className="h-48 bg-gray-100" />
            <div className="p-4">
              <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
              <div className="h-3 bg-gray-100 rounded w-1/2 mb-3" />
              <div className="flex items-center justify-between">
                <div className="h-6 bg-gray-200 rounded w-20" />
                <div className="h-4 bg-gray-100 rounded w-16" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
