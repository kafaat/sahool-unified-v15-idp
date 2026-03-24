'use client';

// Profitability Analytics
// تحليل الربحية

import { useEffect, useState, useCallback } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import { fetchProfitabilityData } from '@/lib/api/analytics';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Wheat,
  Calendar,
  Target,
  PieChart as PieChartIcon,
} from 'lucide-react';
import { logger } from '../../../lib/logger';
import {
  DynamicMonthlyTrendChart,
  DynamicCropProfitabilityChart,
  DynamicCostBreakdownChart,
} from './ProfitabilityCharts.dynamic';

interface ProfitabilityData {
  summary: {
    totalRevenue: number;
    totalCosts: number;
    netProfit: number;
    profitMargin: number;
    roi: number;
  };
  byCrop: Array<{
    crop: string;
    cropAr: string;
    revenue: number;
    costs: number;
    profit: number;
    margin: number;
    area: number;
  }>;
  byMonth: Array<{
    month: string;
    revenue: number;
    costs: number;
    profit: number;
  }>;
  costBreakdown: Array<{
    category: string;
    categoryAr: string;
    amount: number;
    percentage: number;
  }>;
  seasons: Array<{
    season: string;
    seasonAr: string;
    revenue: number;
    costs: number;
    profit: number;
    crops: number;
  }>;
}

export default function ProfitabilityPage() {
  const [data, setData] = useState<ProfitabilityData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'month' | 'quarter' | 'year'>('month');

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const profitData = await fetchProfitabilityData({
        period: selectedPeriod,
      });
      setData(profitData);
    } catch (error) {
      logger.error('Failed to load profitability data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedPeriod]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (isLoading || !data) {
    return (
      <div className="p-6">
        <Header
          title="تحليل الربحية"
          subtitle="Profitability Analytics - تحليل شامل للإيرادات والتكاليف"
        />
        <div className="mt-6 flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-sahool-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between">
        <Header
          title="تحليل الربحية"
          subtitle="Profitability Analytics - تحليل شامل للإيرادات والتكاليف"
        />
        <select
          value={selectedPeriod}
          onChange={(e) => setSelectedPeriod(e.target.value as 'month' | 'quarter' | 'year')}
          className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500"
        >
          <option value="month">شهري</option>
          <option value="quarter">ربع سنوي</option>
          <option value="year">سنوي</option>
        </select>
      </div>

      {/* Summary Statistics */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatCard
          title="إجمالي الإيرادات"
          value={`$${(data.summary.totalRevenue / 1000).toFixed(1)}K`}
          icon={DollarSign}
          iconColor="text-green-600"
        />
        <StatCard
          title="إجمالي التكاليف"
          value={`$${(data.summary.totalCosts / 1000).toFixed(1)}K`}
          icon={TrendingDown}
          iconColor="text-red-600"
        />
        <StatCard
          title="صافي الربح"
          value={`$${(data.summary.netProfit / 1000).toFixed(1)}K`}
          icon={TrendingUp}
          iconColor="text-blue-600"
        />
        <StatCard
          title="هامش الربح"
          value={`${data.summary.profitMargin.toFixed(1)}%`}
          icon={Target}
          iconColor="text-purple-600"
        />
        <StatCard
          title="عائد الاستثمار"
          value={`${data.summary.roi.toFixed(1)}%`}
          icon={PieChartIcon}
          iconColor="text-yellow-600"
        />
      </div>

      {/* Monthly Trend */}
      <div className="mt-6 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
        <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">اتجاه الربحية الشهري</h3>
        <div className="h-80">
          <DynamicMonthlyTrendChart data={data.byMonth} />
        </div>
      </div>

      {/* Crop Profitability and Cost Breakdown */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Crop Profitability Comparison */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">مقارنة ربحية المحاصيل</h3>
          <div className="h-80">
            <DynamicCropProfitabilityChart data={data.byCrop} />
          </div>
        </div>

        {/* Cost Breakdown */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">توزيع التكاليف</h3>
          <div className="h-80">
            <DynamicCostBreakdownChart data={data.costBreakdown} />
          </div>
        </div>
      </div>

      {/* Crop Details Table */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-100 dark:border-gray-700">
          <h3 className="font-bold text-gray-900 dark:text-gray-100">تفاصيل الربحية حسب المحصول</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-950 border-b border-gray-100 dark:border-gray-700">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  المحصول
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  المساحة
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  الإيرادات
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  التكاليف
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  الربح
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  هامش الربح
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  الربح/هكتار
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {data.byCrop.map((crop) => (
                <tr
                  key={crop.crop}
                  className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Wheat className="w-5 h-5 text-sahool-600" />
                      <span className="font-medium text-gray-900 dark:text-gray-100">
                        {crop.cropAr}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                    {crop.area.toFixed(1)} هكتار
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-green-600">
                    ${crop.revenue.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-red-600">
                    ${crop.costs.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm font-bold text-blue-600">
                    ${crop.profit.toFixed(2)}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`text-sm font-medium ${crop.margin >= 20 ? 'text-green-600' : crop.margin >= 10 ? 'text-yellow-600' : 'text-red-600'}`}
                    >
                      {crop.margin.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                    ${crop.area > 0 ? (crop.profit / crop.area).toFixed(2) : '0.00'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Season Summary */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">ملخص الموسم</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {data.seasons.map((season) => (
            <div
              key={season.season}
              className="border border-gray-100 dark:border-gray-700 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">{season.seasonAr}</h4>
                <Calendar className="w-5 h-5 text-sahool-600" />
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">الإيرادات:</span>
                  <span className="font-medium text-green-600">
                    ${(season.revenue / 1000).toFixed(1)}K
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">التكاليف:</span>
                  <span className="font-medium text-red-600">
                    ${(season.costs / 1000).toFixed(1)}K
                  </span>
                </div>
                <div className="flex justify-between border-t border-gray-100 dark:border-gray-700 pt-2">
                  <span className="text-gray-900 dark:text-gray-100 font-medium">الربح:</span>
                  <span className="font-bold text-blue-600">
                    ${(season.profit / 1000).toFixed(1)}K
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">المحاصيل:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {season.crops}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
