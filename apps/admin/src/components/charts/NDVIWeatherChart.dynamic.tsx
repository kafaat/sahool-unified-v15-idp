'use client';

/**
 * Dynamic (lazy-loaded) NDVIWeatherChart wrapper
 * مغلف تحميل كسول لمخطط NDVI مع الطقس
 *
 * Defers loading of recharts (~120KB) until the component is needed.
 * Shows a loading skeleton while the chart library is being loaded.
 */

import dynamic from 'next/dynamic';

const NDVIWeatherChart = dynamic(() => import('./NDVIWeatherChart'), {
  ssr: false,
  loading: () => (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 animate-pulse">
      <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-2/5 mb-4" />
      <div className="h-[350px] bg-gray-100 dark:bg-gray-700/50 rounded flex items-center justify-center">
        <svg
          className="w-8 h-8 text-gray-300 dark:text-gray-600 animate-spin"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      </div>
    </div>
  ),
});

export default NDVIWeatherChart;
