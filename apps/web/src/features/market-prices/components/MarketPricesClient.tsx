'use client';

/**
 * SAHOOL Market Prices Client
 * أسعار السوق
 */

import React, { useState, useMemo } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Filter,
  BarChart3,
  Wheat,
  RefreshCw,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { useMarketPrices, useMarketPriceStats } from '../hooks/useMarketPrices';
import type { CropPriceRecord } from '../types';

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function MarketPricesClient() {
  const [cropFilter, setCropFilter] = useState<string>('all');

  const { data: prices, isLoading, isError, error, refetch } = useMarketPrices();
  const { data: stats } = useMarketPriceStats();

  const records = prices ?? [];

  const uniqueCrops = useMemo(
    () => Array.from(new Set(records.map((p) => p.cropTypeAr ?? p.cropType))),
    [records],
  );

  const filtered = useMemo(
    () =>
      cropFilter === 'all'
        ? records
        : records.filter((p) => (p.cropTypeAr ?? p.cropType) === cropFilter),
    [records, cropFilter],
  );

  const summaryStats = useMemo(() => {
    if (stats) {
      return {
        totalCrops: stats.totalCropsTracked,
        rising: stats.topGainers?.length ?? 0,
        falling: stats.topLosers?.length ?? 0,
        stable: stats.totalCropsTracked - (stats.topGainers?.length ?? 0) - (stats.topLosers?.length ?? 0),
      };
    }
    return {
      totalCrops: records.length,
      rising: 0,
      falling: 0,
      stable: records.length,
    };
  }, [stats, records]);

  // ── Loading State ──────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto" />
          <p className="text-gray-600 text-sm">جاري تحميل أسعار السوق...</p>
          <p className="text-gray-400 text-xs">Loading market prices...</p>
        </div>
      </div>
    );
  }

  // ── Error State ────────────────────────────────────────────────────
  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3 max-w-md">
          <AlertTriangle className="w-8 h-8 text-red-500 mx-auto" />
          <p className="text-gray-900 font-semibold">تعذر تحميل أسعار السوق</p>
          <p className="text-gray-500 text-sm">
            {error instanceof Error ? error.message : 'Failed to load market prices'}
          </p>
          <button
            onClick={() => refetch()}
            className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">أسعار السوق</h1>
            <p className="text-gray-600 mt-1">Market Prices</p>
          </div>
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-5 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            <RefreshCw className="w-5 h-5" />
            <span>تحديث الأسعار</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Wheat className="w-5 h-5 text-amber-600" />
            <p className="text-sm text-gray-600">إجمالي المحاصيل</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{summaryStats.totalCrops}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">أسعار مرتفعة</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{summaryStats.rising}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingDown className="w-5 h-5 text-red-600" />
            <p className="text-sm text-gray-600">أسعار منخفضة</p>
          </div>
          <p className="text-3xl font-bold text-red-600">{summaryStats.falling}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-5 h-5 text-gray-600" />
            <p className="text-sm text-gray-600">أسعار مستقرة</p>
          </div>
          <p className="text-3xl font-bold text-gray-600">{summaryStats.stable}</p>
        </div>
      </div>

      {/* Filter + Table */}
      <div className="bg-white rounded-xl border-2 border-gray-200">
        <div className="flex items-center gap-3 p-6 border-b border-gray-200 flex-wrap">
          <Filter className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-600">المحصول:</span>
          <button
            onClick={() => setCropFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${cropFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
          >
            الكل
          </button>
          {uniqueCrops.map(crop => (
            <button
              key={crop}
              onClick={() => setCropFilter(crop)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${cropFilter === crop ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              {crop}
            </button>
          ))}
        </div>

        <div className="p-6 overflow-x-auto">
          {filtered.length === 0 ? (
            <div className="text-center py-10 text-gray-500">
              <p className="text-sm">لا توجد أسعار متاحة حالياً</p>
              <p className="text-xs text-gray-400 mt-1">No prices available</p>
            </div>
          ) : (
            <table className="w-full text-right">
              <thead>
                <tr className="border-b border-gray-200 text-sm text-gray-500">
                  <th className="pb-3 pr-4 font-medium">المحصول</th>
                  <th className="pb-3 pr-4 font-medium">السعر</th>
                  <th className="pb-3 pr-4 font-medium">الجودة</th>
                  <th className="pb-3 pr-4 font-medium">نوع السوق</th>
                  <th className="pb-3 pr-4 font-medium">السوق</th>
                  <th className="pb-3 font-medium">التاريخ</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(item => (
                  <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 pr-4">
                      <p className="font-semibold text-gray-900">{item.cropTypeAr ?? item.cropType}</p>
                      <p className="text-xs text-gray-500">{item.cropType}</p>
                    </td>
                    <td className="py-4 pr-4">
                      <span className="font-bold text-gray-900">{item.priceValue}</span>
                      <span className="text-xs text-gray-500 mr-1">{item.currency}/{item.unit}</span>
                    </td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{item.quality ?? '-'}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{item.marketType ?? '-'}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{item.marketNameAr ?? item.marketName}</td>
                    <td className="py-4 text-sm text-gray-500">{item.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
