'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  DollarSign,
  TrendingUp,
  PieChart,
  BarChart3,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  Wallet,
  Receipt,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import DemoBanner from '@/components/common/DemoBanner';

/** Parse a percentage string like "25%" and clamp to [0, 100]. */
function clampPct(value: string): string {
  const n = parseFloat(value);
  if (!Number.isFinite(n)) return '0%';
  return `${Math.min(Math.max(n, 0), 100)}%`;
}

const statsCards = [
  {
    title: 'إجمالي الإيرادات',
    value: '285,400 ريال',
    change: '+18%',
    trend: 'up' as const,
    icon: DollarSign,
    color: 'bg-green-500',
  },
  {
    title: 'إجمالي التكاليف',
    value: '142,800 ريال',
    change: '+5%',
    trend: 'up' as const,
    icon: Receipt,
    color: 'bg-red-500',
  },
  {
    title: 'صافي الربح',
    value: '142,600 ريال',
    change: '+32%',
    trend: 'up' as const,
    icon: Wallet,
    color: 'bg-emerald-500',
  },
  {
    title: 'هامش الربح',
    value: '49.9%',
    change: '+5.2%',
    trend: 'up' as const,
    icon: PieChart,
    color: 'bg-purple-500',
  },
];

const profitData = [
  { field: 'حقل القمح - شمال', crop: 'قمح', revenue: '52,000', cost: '22,400', profit: '29,600', margin: '56.9%', roi: '132%', trend: 'up' },
  { field: 'حقل الشعير', crop: 'شعير', revenue: '31,200', cost: '15,800', profit: '15,400', margin: '49.4%', roi: '97%', trend: 'up' },
  { field: 'حقل الطماطم', crop: 'طماطم', revenue: '89,500', cost: '42,100', profit: '47,400', margin: '52.9%', roi: '113%', trend: 'up' },
  { field: 'حقل البرسيم', crop: 'برسيم', revenue: '38,200', cost: '18,600', profit: '19,600', margin: '51.3%', roi: '105%', trend: 'down' },
  { field: 'حقل النخيل', crop: 'نخيل', revenue: '74,500', cost: '43,900', profit: '30,600', margin: '41.1%', roi: '70%', trend: 'up' },
];

const costBreakdown = [
  { category: 'المياه والري', amount: '35,700 ريال', percentage: '25%' },
  { category: 'الأسمدة', amount: '28,560 ريال', percentage: '20%' },
  { category: 'العمالة', amount: '42,840 ريال', percentage: '30%' },
  { category: 'المبيدات', amount: '14,280 ريال', percentage: '10%' },
  { category: 'المعدات', amount: '12,852 ريال', percentage: '9%' },
  { category: 'أخرى', amount: '8,568 ريال', percentage: '6%' },
];

export default function ProfitabilityPage() {
  const [dateRange, setDateRange] = useState('season');
  const [viewMode, setViewMode] = useState<'fields' | 'costs'>('fields');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiProfitData] = useState<typeof profitData | null>(null);

  const fetchData = useCallback(async () => {
    // NOTE: No dedicated analytics API for profitability data yet.
    // Using local sample data until backend endpoint is available.
    try {
      setError(null);
      setLoading(false);
    } catch (err) {
      setError(String(err));
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-500">جاري تحميل بيانات الربحية...</p>
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

  const displayProfitData = apiProfitData ?? profitData;

  return (
    <div className="space-y-6" dir="rtl">
      <DemoBanner />
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تحليل الربحية</h1>
          <p className="text-gray-500 mt-1">تحليل الإيرادات والتكاليف وهوامش الربح لكل حقل ومحصول</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="month">آخر شهر</option>
            <option value="quarter">آخر ربع</option>
            <option value="season">الموسم الحالي</option>
            <option value="year">السنة الحالية</option>
          </select>
          <button className="flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 transition-colors">
            <Download className="h-4 w-4" />
            تصدير التقرير
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
          <h2 className="text-lg font-semibold text-gray-900">اتجاه الربحية الشهري</h2>
        </div>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <div className="text-center">
            <TrendingUp className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="text-gray-400 mt-2">مخطط اتجاه الربحية - قريبا</p>
          </div>
        </div>
      </div>

      {/* Toggle View */}
      <div className="flex gap-2">
        <button
          onClick={() => setViewMode('fields')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${viewMode === 'fields' ? 'bg-green-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'}`}
        >
          ربحية الحقول
        </button>
        <button
          onClick={() => setViewMode('costs')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${viewMode === 'costs' ? 'bg-green-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'}`}
        >
          تفصيل التكاليف
        </button>
      </div>

      {/* Tables */}
      <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        {viewMode === 'fields' ? (
          <>
            <div className="p-5 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900">ربحية الحقول</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="px-5 py-3 text-right font-medium">الحقل</th>
                    <th className="px-5 py-3 text-right font-medium">المحصول</th>
                    <th className="px-5 py-3 text-right font-medium">الإيرادات</th>
                    <th className="px-5 py-3 text-right font-medium">التكاليف</th>
                    <th className="px-5 py-3 text-right font-medium">الربح</th>
                    <th className="px-5 py-3 text-right font-medium">الهامش</th>
                    <th className="px-5 py-3 text-right font-medium">العائد ROI</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {displayProfitData.map((row) => (
                    <tr key={row.field} className="hover:bg-gray-50 transition-colors">
                      <td className="px-5 py-3 font-medium text-gray-900">{row.field}</td>
                      <td className="px-5 py-3 text-gray-600">{row.crop}</td>
                      <td className="px-5 py-3 text-green-600 font-medium">{row.revenue}</td>
                      <td className="px-5 py-3 text-red-600">{row.cost}</td>
                      <td className="px-5 py-3 text-gray-900 font-bold">{row.profit}</td>
                      <td className="px-5 py-3 text-gray-600">{row.margin}</td>
                      <td className="px-5 py-3">
                        <span className="flex items-center gap-1 text-green-600 font-medium">
                          {row.roi}
                          {row.trend === 'up' ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3 text-red-500" />}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <>
            <div className="p-5 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900">تفصيل التكاليف</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="px-5 py-3 text-right font-medium">الفئة</th>
                    <th className="px-5 py-3 text-right font-medium">المبلغ</th>
                    <th className="px-5 py-3 text-right font-medium">النسبة</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {costBreakdown.map((row) => (
                    <tr key={row.category} className="hover:bg-gray-50 transition-colors">
                      <td className="px-5 py-3 font-medium text-gray-900">{row.category}</td>
                      <td className="px-5 py-3 text-gray-600">{row.amount}</td>
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-24 rounded-full bg-gray-200">
                            <div className="h-2 rounded-full bg-green-500" style={{ width: clampPct(row.percentage) }} />
                          </div>
                          <span className="text-gray-600">{row.percentage}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
