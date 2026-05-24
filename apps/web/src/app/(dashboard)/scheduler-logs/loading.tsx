export default function Loading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-8 bg-gray-200 rounded w-64 mb-2" />
          <div className="h-4 bg-gray-100 rounded w-80" />
        </div>
        <div className="flex gap-3">
          <div className="h-9 bg-gray-100 rounded-lg w-28" />
          <div className="h-9 bg-gray-200 rounded-lg w-24" />
        </div>
      </div>

      {/* Stat tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white rounded-lg border p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-100 rounded-lg" />
              <div className="flex-1">
                <div className="h-3 bg-gray-200 rounded w-24 mb-2" />
                <div className="h-7 bg-gray-200 rounded w-16 mb-1" />
                <div className="h-2 bg-gray-100 rounded w-28" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border p-4 flex gap-3">
        <div className="h-9 bg-gray-100 rounded-lg w-36" />
        <div className="h-9 bg-gray-100 rounded-lg w-28" />
        <div className="h-9 bg-gray-100 rounded-lg flex-1" />
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b flex justify-between">
          <div className="h-5 bg-gray-200 rounded w-40" />
          <div className="h-5 bg-gray-100 rounded w-20" />
        </div>
        <div className="divide-y">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="flex gap-4 px-4 py-3">
              {Array.from({ length: 9 }).map((_, j) => (
                <div key={j} className="h-4 bg-gray-100 rounded flex-1" />
              ))}
            </div>
          ))}
        </div>
        {/* Pagination */}
        <div className="p-4 border-t flex justify-between">
          <div className="h-4 bg-gray-100 rounded w-32" />
          <div className="flex gap-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-8 bg-gray-100 rounded w-8" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
