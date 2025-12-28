/**
 * Root Loading State
 * حالة التحميل الرئيسية
 */

export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-sahool-green-200 border-t-sahool-green-600 rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-lg font-semibold text-gray-900 mb-1">جاري التحميل...</p>
        <p className="text-sm text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
