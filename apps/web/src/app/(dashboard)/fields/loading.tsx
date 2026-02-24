/**
 * Fields Loading Skeleton
 * هيكل تحميل صفحة الحقول
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header with action button skeleton */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-8 bg-gray-200 rounded w-44 mb-2" />
          <div className="h-4 bg-gray-100 rounded w-64" />
        </div>
        <div className="h-10 bg-gray-200 rounded-lg w-32" />
      </div>

      {/* Map placeholder skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="h-[400px] bg-gray-100 flex items-center justify-center">
          <div className="text-center">
            <div className="h-12 w-12 bg-gray-200 rounded-full mx-auto mb-3" />
            <div className="h-4 bg-gray-200 rounded w-32 mx-auto" />
          </div>
        </div>
      </div>

      {/* Search and filters skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1 h-10 bg-gray-100 rounded-lg" />
          <div className="h-10 bg-gray-100 rounded-lg w-32" />
          <div className="h-10 bg-gray-100 rounded-lg w-32" />
        </div>
      </div>

      {/* Fields list skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-xl border border-gray-100 shadow-sm p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="h-5 bg-gray-200 rounded w-32" />
              <div className="h-6 bg-gray-100 rounded-full w-16" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <div className="h-4 bg-gray-100 rounded w-20" />
                <div className="h-4 bg-gray-200 rounded w-16" />
              </div>
              <div className="flex justify-between">
                <div className="h-4 bg-gray-100 rounded w-24" />
                <div className="h-4 bg-gray-200 rounded w-12" />
              </div>
              <div className="h-2 bg-gray-100 rounded-full w-full" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
