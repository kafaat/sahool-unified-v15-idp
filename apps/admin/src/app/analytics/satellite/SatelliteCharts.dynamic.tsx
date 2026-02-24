import dynamic from "next/dynamic";

export const NDVITrendChart = dynamic(
  () =>
    import("./SatelliteCharts").then((mod) => ({
      default: mod.NDVITrendChart,
    })),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full bg-gray-100 animate-pulse rounded-lg flex items-center justify-center">
        <p className="text-gray-500 text-sm">جاري تحميل المخطط...</p>
      </div>
    ),
  },
);
