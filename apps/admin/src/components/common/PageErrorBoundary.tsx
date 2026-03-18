/**
 * SAHOOL Admin - Page-level Error Boundary
 * حدود الخطأ على مستوى الصفحة
 *
 * Lightweight wrapper around ErrorBoundary for page-level usage.
 * Provides a consistent error UI with page name context.
 */

"use client";

import { ReactNode } from "react";
import { ErrorBoundary } from "./ErrorBoundary";

interface PageErrorBoundaryProps {
  children: ReactNode;
  /** Page name for error tracking context */
  pageName?: string;
  /** Arabic page name */
  pageNameAr?: string;
}

/**
 * Page-level error boundary with bilingual fallback UI
 *
 * @example
 * ```tsx
 * <PageErrorBoundary pageName="Dashboard" pageNameAr="لوحة التحكم">
 *   <DashboardContent />
 * </PageErrorBoundary>
 * ```
 */
export function PageErrorBoundary({
  children,
  pageName = "Page",
  pageNameAr = "الصفحة",
}: PageErrorBoundaryProps) {
  return (
    <ErrorBoundary
      componentName={pageName}
      fallback={
        <div className="min-h-[400px] flex items-center justify-center p-8">
          <div className="bg-white rounded-xl shadow-lg p-8 max-w-lg w-full text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-8 h-8 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>

            <h2 className="text-xl font-bold text-gray-800 mb-2">
              خطأ في {pageNameAr}
            </h2>
            <p className="text-gray-500 mb-1">
              حدث خطأ غير متوقع أثناء تحميل هذه الصفحة
            </p>
            <p className="text-gray-400 text-sm mb-6">
              An unexpected error occurred while loading {pageName}
            </p>

            <div className="flex gap-3 justify-center">
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                إعادة تحميل الصفحة
              </button>
              <button
                type="button"
                onClick={() => window.history.back()}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                العودة
              </button>
            </div>
          </div>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
}

export default PageErrorBoundary;
