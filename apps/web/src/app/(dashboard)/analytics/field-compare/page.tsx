'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  GitCompareArrows,
  TrendingUp,
  Droplets,
  Leaf,
  BarChart3,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { analyticsApi } from '@/features/analytics/api';
import type { AnalyticsFilters } from '@/features/analytics/types';
import { ApiError } from '@/lib/api/safe-fetch';

interface ComparisonRow {
  field: string;
  area: string;
  yield: string;
  ndvi: number;
  irrigation: string;
  cost: string;
  status: string;
}

const statusColor: Record<string, string> = {
  'ممتاز': 'bg-green-100 text-green-800',
  'جيد': 'bg-blue-100 text-blue-800',
  'متوسط': 'bg-yellow-100 text-yellow-800',
};

export default function FieldComparePage() {
  const [dateRange, setDateRange] = useState('month');
  const [cropFilter, setCropFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [comparisonData, setComparisonData] = useState<ComparisonRow[]>([]);
  const [stats, setStats] = useState({ fields: 0, avgYield: '0', efficiency: '0%', ndvi: '0' });

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [comparison, summary] = await Promise.all([
        analyticsApi.getComparison('fields', 'yield', {
          period: dateRange as AnalyticsFilters['period'],
          cropTypes: cropFilter !== 'all' ? [cropFilter] : undefined,
        }),
        analyticsApi.getSummary({ period: dateRange as AnalyticsFilters['period'] }),
      ]);
      // Map comparison data if available
      if (comparison && Array.isArray((comparison as any).items)) {
        setComparisonData((comparison as any).items);
      }
      if (summary) {
        setStats({
          fields: (summary as any).totalFields ?? 0,
          avgYield: (summary as any).avgYield ?? '0',
          efficiency: (summary as any).irrigationEfficiency ?? '0%',
          ndvi: (summary as any).avgNdvi ?? '0',
        });
      }
    } catch (err) {
      const message = err instanceof ApiError ? err.messageAr : 'فشل في جلب بيانات المقارنة';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [dateRange, cropFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const statsCards = [
    {
      title: 'عدد الحقول المقارنة',
      value: String(stats.fields || comparisonData.length),
      change: '+3',
      trend: 'up' as const,
      icon: GitCompareArrows,
      color: 'bg-blue-500',
    },
    {
      title: 'متوسط الإنتاجية',
      value: `${stats.avgYield} طن/هكتار`,
      change: '+12%',
      trend: 'up' as const,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      title: 'كفاءة الري',
      value: String(stats.efficiency),
      change: '-3%',
      trend: 'down' as const,
      icon: Droplets,
      color: 'bg-cyan-500',
    },
    {
      title: 'صحة المحاصيل',
      value: `${stats.ndvi} NDVI`,
      change: '+0.05',
      trend: 'up' as const,
      icon: Leaf,
      color: 'bg-emerald-500',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-500">جاري تحميل بيانات المقارنة...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">خطأ في تحميل البيانات</h3>
          <p className="text-gray-500 mb-4">{error}</p>
          <button onClick={fetchData} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">مقارنة الحقول</h1>
          <p className="text-gray-500 mt-1">مقارنة أداء الحقول المختلفة من حيث الإنتاجية وكفاءة الموارد</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={cropFilter}
            onChange={(e) => setCropFilter(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="all">جميع المحاصيل</option>
            <option value="wheat">القمح</option>
            <option value="barley">الشعير</option>
            <option value="tomato">الطماطم</option>
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="week">آخر أسبوع</option>
            <option value="month">آخر شهر</option>
            <option value="quarter">آخر 3 أشهر</option>
            <option value="year">آخر سنة</option>
          </select>
          <button className="flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 transition-colors">
            <Download className="h-4 w-4" />
            تصدير
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((card) => (
          <div key={card.title} className="rounded-xl bg-white p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div className={`rounded-lg ${card.color} p-2.5`}>
                <card.icon className="h-5 w-5 text-white" />
              </div>
              <span className={`flex items-center text-sm font-medium ${card.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {card.change}
                {card.trend === 'up' ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
              </span>
            </div>
            <p className="mt-3 text-2xl font-bold text-gray-900">{card.value}</p>
            <p className="text-sm text-gray-500">{card.title}</p>
          </div>
        ))}
      </div>

      {/* Chart Placeholder */}
      <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-100">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="h-5 w-5 text-green-600" />
          <h2 className="text-lg font-semibold text-gray-900">مخطط مقارنة الحقول</h2>
        </div>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <div className="text-center">
            <BarChart3 className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="text-gray-400 mt-2">مخطط المقارنة البيانية - قريبا</p>
          </div>
        </div>
      </div>

      {/* Comparison Table */}
      <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">جدول مقارنة الحقول</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-5 py-3 text-right font-medium">الحقل</th>
                <th className="px-5 py-3 text-right font-medium">المساحة</th>
                <th className="px-5 py-3 text-right font-medium">الإنتاجية</th>
                <th className="px-5 py-3 text-right font-medium">NDVI</th>
                <th className="px-5 py-3 text-right font-medium">كفاءة الري</th>
                <th className="px-5 py-3 text-right font-medium">التكلفة/هكتار</th>
                <th className="px-5 py-3 text-right font-medium">الحالة</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {comparisonData.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-8 text-center text-gray-500">
                    لا توجد بيانات مقارنة متاحة
                  </td>
                </tr>
              ) : (
                comparisonData.map((row) => (
                  <tr key={row.field} className="hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3 font-medium text-gray-900">{row.field}</td>
                    <td className="px-5 py-3 text-gray-600">{row.area}</td>
                    <td className="px-5 py-3 text-gray-600">{row.yield}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-16 rounded-full bg-gray-200">
                          <div className="h-2 rounded-full bg-green-500" style={{ width: `${row.ndvi * 100}%` }} />
                        </div>
                        <span className="text-gray-600">{row.ndvi}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-gray-600">{row.irrigation}</td>
                    <td className="px-5 py-3 text-gray-600">{row.cost}</td>
                    <td className="px-5 py-3">
                      <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor[row.status] || 'bg-gray-100 text-gray-800'}`}>
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
