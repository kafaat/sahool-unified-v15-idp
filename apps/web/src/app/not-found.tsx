import Link from 'next/link';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

/**
 * Custom 404 Page for SAHOOL Web Dashboard
 * صفحة 404 مخصصة للوحة التحكم الرئيسية
 *
 * Bilingual (Arabic + English) with proper accessibility
 */
export default function NotFound() {
  return (
    <div
      className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900"
      role="main"
      aria-labelledby="not-found-title"
    >
      <div className="text-center px-4">
        <h1 className="text-9xl font-bold text-gray-200 dark:text-gray-700" aria-hidden="true">
          404
        </h1>
        <h2 id="not-found-title" className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mt-4">
          <div>الصفحة غير موجودة</div>
          <div className="text-base text-gray-500 dark:text-gray-400 mt-1">Page Not Found</div>
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mt-2 mb-8">
          <span className="block">عذراً، الصفحة التي تبحث عنها غير موجودة أو تم نقلها.</span>
          <span className="block text-sm text-gray-500 dark:text-gray-500 mt-1">
            Sorry, the page you&apos;re looking for doesn&apos;t exist or has been moved.
          </span>
        </p>
        <Link
          href="/"
          className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          aria-label="العودة إلى الصفحة الرئيسية - Go back to home page"
        >
          <svg
            className="w-5 h-5 me-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 19l-7-7m0 0l7-7m-7 7h18"
            />
          </svg>
          <span>العودة إلى الصفحة الرئيسية</span>
          <span className="mx-1">•</span>
          <span className="text-sm">Go Home</span>
        </Link>
      </div>
    </div>
  );
}
