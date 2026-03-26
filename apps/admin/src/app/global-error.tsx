'use client';

/**
 * Global Error Boundary (Root Layout Level)
 * حدود الخطأ العامة على مستوى التخطيط الجذري
 *
 * Catches errors in the root layout itself (Next.js 13+).
 * Must include its own <html> and <body> tags.
 */

import { getDirection, getLocale } from '@/lib/i18n';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const locale = getLocale();
  const direction = getDirection(locale);

  return (
    <html lang={locale} dir={direction}>
      <body className="bg-gray-50 text-gray-900">
        <div className="flex min-h-screen items-center justify-center p-4">
          <div className="max-w-md w-full text-center space-y-6">
            <div className="text-6xl">⚠️</div>

            <div className="space-y-2">
              <h1 className="text-2xl font-bold">خطأ حرج في النظام</h1>
              <p className="text-gray-600">
                A critical system error occurred. Please refresh the page.
              </p>
              {error.digest && <p className="text-xs text-gray-400 font-mono">{error.digest}</p>}
            </div>

            <button
              onClick={reset}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
            >
              تحديث الصفحة / Refresh
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
