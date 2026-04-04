'use client';

import { useState } from 'react';
import {
  CalendarDays,
  FileText,
  TrendingUp,
  CloudRain,
  BarChart3,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  Printer,
  Share2,
  ChevronDown,
  Leaf,
} from 'lucide-react';

const statsCards = [
  {
    title: 'إجمالي التقارير',
    value: '24',
    change: '+4',
    trend: 'up' as const,
    icon: FileText,
    color: 'bg-blue-500',
  },
  {
    title: 'الإنتاجية الموسمية',
    value: '186.5 طن',
    change: '+14%',
    trend: 'up' as const,
    icon: TrendingUp,
    color: 'bg-green-500',
  },
  {
    title: 'هطول الأمطار الموسمي',
    value: '125 مم',
    change: '-18%',
    trend: 'down' as const,
    icon: CloudRain,
    color: 'bg-cyan-500',
  },
  {
    title: 'صحة المحاصيل',
    value: '0.71 NDVI',
    change: '+0.06',
    trend: 'up' as const,
    icon: Leaf,
    color: 'bg-emerald-500',
  },
];

const reportData = [
  { id: 'SR-2026-W', title: 'تقرير الموسم الشتوي 2025/2026', season: 'شتوي', period: 'نوفمبر 2025 - أبريل 2026', status: 'جاري', crops: 'قمح، شعير، برسيم', fields: 8, yield: '142.6 طن', revenue: '245,300 ريال', generated: '2026-04-01' },
  { id: 'SR-2025-S', title: 'تقرير الموسم الصيفي 2025', season: 'صيفي', period: 'مايو - أكتوبر 2025', status: 'مكتمل', crops: 'طماطم، خيار، ذرة', fields: 5, yield: '198.4 طن', revenue: '312,800 ريال', generated: '2025-11-15' },
  { id: 'SR-2025-W', title: 'تقرير الموسم الشتوي 2024/2025', season: 'شتوي', period: 'نوفمبر 2024 - أبريل 2025', status: 'مكتمل', crops: 'قمح، شعير', fields: 6, yield: '125.0 طن', revenue: '198,500 ريال', generated: '2025-05-10' },
  { id: 'SR-2024-S', title: 'تقرير الموسم الصيفي 2024', season: 'صيفي', period: 'مايو - أكتوبر 2024', status: 'مكتمل', crops: 'طماطم، بطيخ', fields: 4, yield: '165.2 طن', revenue: '256,100 ريال', generated: '2024-11-20' },
  { id: 'SR-2024-W', title: 'تقرير الموسم الشتوي 2023/2024', season: 'شتوي', period: 'نوفمبر 2023 - أبريل 2024', status: 'مكتمل', crops: 'قمح، شعير، برسيم', fields: 7, yield: '110.8 طن', revenue: '175,200 ريال', generated: '2024-05-08' },
  { id: 'SR-2026-SP', title: 'تقرير الموسم الصيفي المبكر 2026', season: 'صيفي مبكر', period: 'فبراير - يونيو 2026', status: 'مسودة', crops: 'طماطم', fields: 2, yield: '-', revenue: '-', generated: '2026-04-03' },
];

const statusColor: Record<string, string> = {
  'مكتمل': 'bg-green-100 text-green-800',
  'جاري': 'bg-blue-100 text-blue-800',
  'مسودة': 'bg-gray-100 text-gray-800',
};

const seasonColor: Record<string, string> = {
  'شتوي': 'bg-sky-100 text-sky-800',
  'صيفي': 'bg-amber-100 text-amber-800',
  'صيفي مبكر': 'bg-orange-100 text-orange-800',
};

export default function SeasonalReportsPage() {
  const [seasonFilter, setSeasonFilter] = useState('all');
  const [yearFilter, setYearFilter] = useState('all');

  const filtered = reportData.filter((row) => {
    if (seasonFilter !== 'all' && row.season !== seasonFilter) return false;
    if (yearFilter !== 'all' && !row.id.includes(yearFilter)) return false;
    return true;
  });

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">التقارير الموسمية</h1>
          <p className="text-gray-500 mt-1">تقارير شاملة عن أداء المواسم الزراعية وتحليل الإنتاجية والإيرادات</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={seasonFilter}
            onChange={(e) => setSeasonFilter(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="all">جميع المواسم</option>
            <option value="شتوي">شتوي</option>
            <option value="صيفي">صيفي</option>
            <option value="صيفي مبكر">صيفي مبكر</option>
          </select>
          <select
            value={yearFilter}
            onChange={(e) => setYearFilter(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="all">جميع السنوات</option>
            <option value="2026">2026</option>
            <option value="2025">2025</option>
            <option value="2024">2024</option>
          </select>
          <button className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <Printer className="h-4 w-4" />
            طباعة
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 transition-colors">
            <Download className="h-4 w-4" />
            تصدير PDF
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
          <BarChart3 className="h-5 w-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">مقارنة أداء المواسم</h2>
        </div>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <div className="text-center">
            <CalendarDays className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="text-gray-400 mt-2">مخطط مقارنة المواسم - قريبا</p>
          </div>
        </div>
      </div>

      {/* Reports Table */}
      <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">سجل التقارير الموسمية ({filtered.length})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-4 py-3 text-right font-medium">الرمز</th>
                <th className="px-4 py-3 text-right font-medium">العنوان</th>
                <th className="px-4 py-3 text-right font-medium">الموسم</th>
                <th className="px-4 py-3 text-right font-medium">الفترة</th>
                <th className="px-4 py-3 text-right font-medium">الحالة</th>
                <th className="px-4 py-3 text-right font-medium">المحاصيل</th>
                <th className="px-4 py-3 text-right font-medium">الحقول</th>
                <th className="px-4 py-3 text-right font-medium">الإنتاج</th>
                <th className="px-4 py-3 text-right font-medium">الإيرادات</th>
                <th className="px-4 py-3 text-right font-medium">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{row.id}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">{row.title}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${seasonColor[row.season] || 'bg-gray-100 text-gray-800'}`}>
                      {row.season}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{row.period}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor[row.status]}`}>
                      {row.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">{row.crops}</td>
                  <td className="px-4 py-3 text-gray-600 text-center">{row.fields}</td>
                  <td className="px-4 py-3 text-gray-900 font-medium">{row.yield}</td>
                  <td className="px-4 py-3 text-green-700 font-medium">{row.revenue}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button className="rounded p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors" title="تحميل">
                        <Download className="h-4 w-4" />
                      </button>
                      <button className="rounded p-1 text-gray-400 hover:text-green-600 hover:bg-green-50 transition-colors" title="مشاركة">
                        <Share2 className="h-4 w-4" />
                      </button>
                    </div>
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
