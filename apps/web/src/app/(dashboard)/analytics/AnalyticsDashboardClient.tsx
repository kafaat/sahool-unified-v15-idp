"use client";

import dynamic from "next/dynamic";

const AnalyticsDashboard = dynamic(
  () =>
    import("@/features/analytics").then((mod) => ({
      default: mod.AnalyticsDashboard,
    })),
  {
    ssr: false,
    loading: () => (
      <div
        className="min-h-screen bg-gray-50 flex items-center justify-center"
        dir="rtl"
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
          <p className="text-gray-500 mt-4">جاري تحميل لوحة التحليلات...</p>
        </div>
      </div>
    ),
  },
);

export default AnalyticsDashboard;
