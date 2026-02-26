/**
 * Settings Loading Skeleton
 * هيكل تحميل صفحة الإعدادات
 */

export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-8 bg-gray-200 rounded w-32 mb-2" />
        <div className="h-4 bg-gray-100 rounded w-56" />
      </div>

      {/* Tab navigation skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-1">
        <div className="flex gap-1">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className={`flex-1 h-12 rounded-lg ${i === 0 ? "bg-gray-200" : "bg-gray-50"}`}
            />
          ))}
        </div>
      </div>

      {/* Profile form section skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="h-9 w-9 bg-gray-100 rounded-lg" />
          <div className="h-5 bg-gray-200 rounded w-36" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i}>
              <div className="h-4 bg-gray-100 rounded w-28 mb-2" />
              <div className="h-10 bg-gray-50 border border-gray-200 rounded-lg" />
            </div>
          ))}
          <div className="md:col-span-2">
            <div className="h-4 bg-gray-100 rounded w-20 mb-2" />
            <div className="h-10 bg-gray-50 border border-gray-200 rounded-lg" />
          </div>
        </div>
        <div className="mt-6 flex justify-end">
          <div className="h-10 bg-gray-200 rounded-lg w-36" />
        </div>
      </div>

      {/* Password section skeleton */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="h-9 w-9 bg-red-50 rounded-lg" />
          <div className="h-5 bg-gray-200 rounded w-40" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i}>
              <div className="h-4 bg-gray-100 rounded w-32 mb-2" />
              <div className="h-10 bg-gray-50 border border-gray-200 rounded-lg" />
            </div>
          ))}
        </div>
        <div className="mt-6 flex justify-end">
          <div className="h-10 bg-gray-200 rounded-lg w-40" />
        </div>
      </div>
    </div>
  );
}
