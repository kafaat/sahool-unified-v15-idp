'use client';

/**
 * Root Error Boundary
 * حد الخطأ الرئيسي
 */

import { useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="w-8 h-8 text-red-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">حدث خطأ</h1>
        <h2 className="text-lg text-gray-700 mb-4">Something went wrong</h2>
        <p className="text-gray-600 mb-6">
          عذراً، حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.
        </p>
        <p className="text-sm text-gray-500 mb-6">
          Sorry, an unexpected error occurred. Please try again.
        </p>
        {error.message && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-6 text-left">
            <p className="text-xs text-red-800 font-mono">{error.message}</p>
          </div>
        )}
        <button
          onClick={reset}
          className="w-full px-6 py-3 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors font-semibold"
        >
          إعادة المحاولة • Try Again
        </button>
      </div>
    </div>
  );
}
