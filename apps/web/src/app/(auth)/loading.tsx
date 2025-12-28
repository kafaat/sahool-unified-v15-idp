/**
 * Auth Loading State
 * حالة تحميل المصادقة
 */

export default function AuthLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8 animate-pulse">
        <div className="mx-auto w-16 h-16 bg-gray-200 rounded-full mb-6"></div>
        <div className="space-y-4">
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  );
}
