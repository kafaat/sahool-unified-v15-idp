/**
 * Global Loading Skeleton
 * هيكل التحميل العام
 *
 * Shown during navigation/data loading (Next.js 13+ convention).
 */

export default function Loading() {
  return (
    <div
      className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900"
      role="status"
      aria-label="Loading"
    >
      <div className="text-center space-y-4">
        <div
          className="w-12 h-12 border-4 border-green-200 border-t-green-600 rounded-full animate-spin mx-auto"
          aria-hidden="true"
        />
        <p className="text-sm text-gray-500 dark:text-gray-400">جاري التحميل... / Loading...</p>
      </div>
    </div>
  );
}
