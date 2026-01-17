import Link from "next/link";

export const dynamic = "force-dynamic";
export const revalidate = 0;

/**
 * Custom 404 Page for SAHOOL Admin Dashboard
 * This is a static page that can be prerendered without ThemeProvider
 */
export default function NotFound() {
  return (
    <div
      className="min-h-screen flex items-center justify-center bg-gray-50"
      dir="rtl"
    >
      <div className="text-center px-4">
        <h1 className="text-9xl font-bold text-gray-200">404</h1>
        <h2 className="text-2xl font-semibold text-gray-800 mt-4">
          الصفحة غير موجودة
        </h2>
        <p className="text-gray-600 mt-2 mb-8">
          عذراً، الصفحة التي تبحث عنها غير موجودة أو تم نقلها.
        </p>
        <Link
          href="/dashboard"
          className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
        >
          <svg
            className="w-5 h-5 ml-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 19l-7-7m0 0l7-7m-7 7h18"
            />
          </svg>
          العودة إلى لوحة التحكم
        </Link>
      </div>
    </div>
  );
}
