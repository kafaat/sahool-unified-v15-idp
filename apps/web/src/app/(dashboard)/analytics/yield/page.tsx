'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Wheat,
  TrendingUp,
  Scale,
  MapPin,
  BarChart3,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  Layers,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import DemoBanner from '@/components/common/DemoBanner';

const statsCards = [
  {
    title: 'إجمالي الإنتاج',
    value: '186.5 طن',
    change: '+14%',
    trend: 'up' as const,
    icon: Wheat,
    color: 'bg-amber-500',
  },
  {
    title: 'متوسط الإنتاجية',
    value: '4.8 طن/هكتار',
    change: '+0.6',
    trend: 'up' as const,
    icon: TrendingUp,
    color: 'bg-green-500',
  },
  {
    title: 'أعلى إنتاجية',
    value: '6.2 طن/هكتار',
    change: '+0.4',
    trend: 'up' as const,
    icon: Scale,
    color: 'bg-blue-500',
  },
  {
    title: 'عدد الحقول المحصودة',
    value: '8 / 12',
    change: '+2',
    trend: 'up' as const,
    icon: MapPin,
    color: 'bg-purple-500',
  },
];

const yieldData = [
  { field: 'حقل القمح - شمال', crop: 'قمح - سخا 95', area: '5.2 هكتار', targetYield: '5.5 طن/هكتار', actualYield: '5.1 طن/هكتار', total: '26.5 طن', efficiency: '93%', season: 'شتوي 2025/26', quality: 'درجة أولى' },
  { field: 'حقل القمح - جنوب', crop: 'قمح - جميزة 12', area: '3.8 هكتار', targetYield: '5.0 طن/هكتار', actualYield: '4.6 طن/هكتار', total: '17.5 طن', efficiency: '92%', season: 'شتوي 2025/26', quality: 'درجة أولى' },
  { field: 'حقل الشعير', crop: 'شعير - جيزة 138', area: '4.5 هكتار', targetYield: '4.2 طن/هكتار', actualYield: '3.9 طن/هكتار', total: '17.6 طن', efficiency: '93%', season: 'شتوي 2025/26', quality: 'درجة ثانية' },
  { field: 'حقل الطماطم', crop: 'طماطم - هجين 010', area: '2.1 هكتار', targetYield: '30 طن/هكتار', actualYield: '28.5 طن/هكتار', total: '59.9 طن', efficiency: '95%', season: 'صيفي مبكر 2026', quality: 'درجة أولى' },
  { field: 'حقل البرسيم', crop: 'برسيم - مسقاوي', area: '6.0 هكتار', targetYield: '14 طن/هكتار', actualYield: '12.3 طن/هكتار', total: '73.8 طن', efficiency: '88%', season: 'شتوي 2025/26', quality: 'جيد' },
  { field: 'حقل النخيل', crop: 'نخيل - سكري', area: '8.2 هكتار', targetYield: '9 طن/هكتار', actualYield: '7.8 طن/هكتار', total: '63.96 طن', efficiency: '87%', season: 'سنوي', quality: 'ممتاز' },
];

const qualityColor: Record<string, string> = {
  'درجة أولى': 'bg-green-100 text-green-800',
  'درجة ثانية': 'bg-blue-100 text-blue-800',
  'ممتاز': 'bg-emerald-100 text-emerald-800',
  'جيد': 'bg-yellow-100 text-yellow-800',
};

export default function YieldAnalyticsPage() {
  const [dateRange, setDateRange] = useState('season');
  const [cropFilter, setCropFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiYieldData] = useState<typeof yieldData | null>(null);

  const fetchData = useCallback(async () => {
    // NOTE: No dedicated analytics API for yield data yet.
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

  const displayData = apiYieldData ?? yieldData;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-green-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-500">جاري تحميل بيانات الإنتاجية...</p>
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
      <DemoBanner />
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تحليلات الإنتاجية</h1>
          <p className="text-gray-500 mt-1">تتبع وتحليل إنتاجية المحاصيل عبر الحقول والمواسم المختلفة</p>
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
            <option value="alfalfa">البرسيم</option>
            <option value="palm">النخيل</option>
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="season">الموسم الحالي</option>
            <option value="year">السنة الحالية</option>
            <option value="2years">آخر سنتين</option>
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
          <BarChart3 className="h-5 w-5 text-amber-600" />
          <h2 className="text-lg font-semibold text-gray-900">اتجاه الإنتاجية عبر المواسم</h2>
        </div>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <div className="text-center">
            <Layers className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="text-gray-400 mt-2">مخطط اتجاه الإنتاجية - قريبا</p>
          </div>
        </div>
      </div>

      {/* Yield Table */}
      <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">تفاصيل الإنتاجية</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-4 py-3 text-right font-medium">الحقل</th>
                <th className="px-4 py-3 text-right font-medium">المحصول / الصنف</th>
                <th className="px-4 py-3 text-right font-medium">المساحة</th>
                <th className="px-4 py-3 text-right font-medium">المستهدف</th>
                <th className="px-4 py-3 text-right font-medium">الفعلي</th>
                <th className="px-4 py-3 text-right font-medium">الإجمالي</th>
                <th className="px-4 py-3 text-right font-medium">الكفاءة</th>
                <th className="px-4 py-3 text-right font-medium">الموسم</th>
                <th className="px-4 py-3 text-right font-medium">الجودة</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {displayData.map((row) => (
                <tr key={row.field} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-900">{row.field}</td>
                  <td className="px-4 py-3 text-gray-600">{row.crop}</td>
                  <td className="px-4 py-3 text-gray-600">{row.area}</td>
                  <td className="px-4 py-3 text-gray-500">{row.targetYield}</td>
                  <td className="px-4 py-3 text-gray-900 font-medium">{row.actualYield}</td>
                  <td className="px-4 py-3 text-gray-900 font-bold">{row.total}</td>
                  <td className="px-4 py-3">
                    <span className={`font-medium ${parseInt(row.efficiency) >= 90 ? 'text-green-600' : 'text-yellow-600'}`}>
                      {row.efficiency}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{row.season}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${qualityColor[row.quality] || 'bg-gray-100 text-gray-800'}`}>
                      {row.quality}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
