"use client";

/**
 * Global Error Page
 * صفحة الأخطاء العامة
 *
 * Catches unhandled errors at the page level (Next.js 13+ convention).
 */

import { useEffect } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to monitoring (Sentry is configured via sentry.client.config.ts)
    if (typeof window !== "undefined" && (window as any).__SENTRY__) {
      import(/* webpackIgnore: true */ "@sentry/nextjs").then((Sentry) => {
        Sentry.captureException(error);
      });
    }
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="mx-auto w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
          <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
        </div>

        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            حدث خطأ غير متوقع
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            An unexpected error occurred
          </p>
          {error.digest && (
            <p className="text-xs text-gray-400 dark:text-gray-500 font-mono">
              Error ID: {error.digest}
            </p>
          )}
        </div>

        <button
          onClick={reset}
          className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
        >
          <RefreshCw className="w-4 h-4" />
          إعادة المحاولة / Retry
        </button>
      </div>
    </div>
  );
}
