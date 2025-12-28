'use client';

/**
 * Dashboard Error Boundary
 * حد الخطأ للوحة التحكم
 */

import { useEffect } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Dashboard error:', error);
  }, [error]);

  return (
    <div className="min-h-full flex items-center justify-center p-6">
      <div className="max-w-lg w-full bg-white rounded-xl border-2 border-red-200 p-8 text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="w-8 h-8 text-red-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">حدث خطأ في لوحة التحكم</h1>
        <h2 className="text-lg text-gray-700 mb-4">Dashboard Error</h2>
        <p className="text-gray-600 mb-6">
          عذراً، حدث خطأ أثناء تحميل هذه الصفحة. يمكنك المحاولة مرة أخرى أو العودة إلى الصفحة الرئيسية.
        </p>
        {error.message && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-6 text-left">
            <p className="text-xs text-red-800 font-mono break-words">{error.message}</p>
          </div>
        )}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={reset}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors font-semibold"
          >
            <RefreshCw className="w-4 h-4" />
            <span>إعادة المحاولة</span>
          </button>
          <button
            onClick={() => router.push('/dashboard')}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
          >
            <Home className="w-4 h-4" />
            <span>الصفحة الرئيسية</span>
          </button>
        </div>
      </div>
    </div>
  );
}
