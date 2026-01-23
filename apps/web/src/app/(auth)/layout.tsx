"use client";

import { ErrorBoundary } from "@/components/common/ErrorBoundary";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sahool-green-50 via-white to-sahool-brown-50">
      <ErrorBoundary
        fallback={
          <div className="min-h-screen flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center" dir="rtl">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">حدث خطأ غير متوقع</h2>
              <p className="text-gray-600 mb-6">نعتذر عن الإزعاج. يرجى المحاولة مرة أخرى.</p>
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                تحديث الصفحة
              </button>
            </div>
          </div>
        }
      >
        {children}
      </ErrorBoundary>
    </div>
  );
}
