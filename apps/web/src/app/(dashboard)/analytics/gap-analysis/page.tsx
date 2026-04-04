'use client';

import { useState } from 'react';
import {
  Target,
  AlertTriangle,
  CheckCircle2,
  TrendingDown,
  BarChart3,
  Calendar,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  Search,
} from 'lucide-react';

const statsCards = [
  {
    title: 'إجمالي الفجوات المكتشفة',
    value: '23',
    change: '-5',
    trend: 'down' as const,
    icon: Target,
    color: 'bg-orange-500',
  },
  {
    title: 'فجوات حرجة',
    value: '4',
    change: '-2',
    trend: 'down' as const,
    icon: AlertTriangle,
    color: 'bg-red-500',
  },
  {
    title: 'فجوات تم إغلاقها',
    value: '38',
    change: '+8',
    trend: 'up' as const,
    icon: CheckCircle2,
    color: 'bg-green-500',
  },
  {
    title: 'خسائر الإنتاجية المقدرة',
    value: '15%',
    change: '-3%',
    trend: 'down' as const,
    icon: TrendingDown,
    color: 'bg-purple-500',
  },
];

const gapData = [
  { id: 'GAP-001', category: 'الري', field: 'حقل القمح - شمال', severity: 'حرج', gap: 'نقص مياه 25%', target: '100 م³/يوم', actual: '75 م³/يوم', impact: 'انخفاض إنتاجية 18%', action: 'تعديل جدول الري' },
  { id: 'GAP-002', category: 'التسميد', field: 'حقل الشعير', severity: 'متوسط', gap: 'نقص نيتروجين', target: '25 جزء/مليون', actual: '18 جزء/مليون', impact: 'اصفرار الأوراق', action: 'إضافة يوريا 46 كغ/هكتار' },
  { id: 'GAP-003', category: 'صحة النبات', field: 'حقل الطماطم', severity: 'منخفض', gap: 'NDVI منخفض', target: '0.75', actual: '0.68', impact: 'تأخر النمو', action: 'فحص ميداني' },
  { id: 'GAP-004', category: 'التربة', field: 'حقل النخيل', severity: 'حرج', gap: 'ملوحة عالية', target: '< 4 dS/m', actual: '6.2 dS/m', impact: 'تراجع الإنتاج 22%', action: 'غسيل تربة عاجل' },
  { id: 'GAP-005', category: 'الآفات', field: 'حقل القمح - جنوب', severity: 'متوسط', gap: 'إصابة حشرية', target: '< 5% إصابة', actual: '12% إصابة', impact: 'تلف أوراق', action: 'مكافحة متكاملة' },
  { id: 'GAP-006', category: 'العمالة', field: 'حقل البرسيم', severity: 'منخفض', gap: 'تأخر الحصاد', target: 'الأسبوع 12', actual: 'الأسبوع 14', impact: 'انخفاض جودة', action: 'جدولة عمالة إضافية' },
];

const severityColor: Record<string, string> = {
  'حرج': 'bg-red-100 text-red-800',
  'متوسط': 'bg-yellow-100 text-yellow-800',
  'منخفض': 'bg-blue-100 text-blue-800',
};

export default function GapAnalysisPage() {
  const [dateRange, setDateRange] = useState('month');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = gapData.filter((row) => {
    if (severityFilter !== 'all' && row.severity !== severityFilter) return false;
    if (searchTerm && !row.field.includes(searchTerm) && !row.category.includes(searchTerm)) return false;
    return true;
  });

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تحليل الفجوات</h1>
          <p className="text-gray-500 mt-1">تحديد الفجوات بين الأداء الفعلي والمستهدف في العمليات الزراعية</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="all">جميع المستويات</option>
            <option value="حرج">حرج</option>
            <option value="متوسط">متوسط</option>
            <option value="منخفض">منخفض</option>
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-green-500"
          >
            <option value="week">آخر أسبوع</option>
            <option value="month">آخر شهر</option>
            <option value="quarter">آخر 3 أشهر</option>
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
          <BarChart3 className="h-5 w-5 text-orange-600" />
          <h2 className="text-lg font-semibold text-gray-900">توزيع الفجوات حسب الفئة</h2>
        </div>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <div className="text-center">
            <BarChart3 className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="text-gray-400 mt-2">مخطط توزيع الفجوات - قريبا</p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="البحث في الفجوات..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full rounded-lg border border-gray-300 py-2 pr-10 pl-4 text-sm focus:ring-2 focus:ring-green-500"
        />
      </div>

      {/* Gap Table */}
      <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">تفاصيل الفجوات ({filtered.length})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-4 py-3 text-right font-medium">الرمز</th>
                <th className="px-4 py-3 text-right font-medium">الفئة</th>
                <th className="px-4 py-3 text-right font-medium">الحقل</th>
                <th className="px-4 py-3 text-right font-medium">الخطورة</th>
                <th className="px-4 py-3 text-right font-medium">المستهدف</th>
                <th className="px-4 py-3 text-right font-medium">الفعلي</th>
                <th className="px-4 py-3 text-right font-medium">التأثير</th>
                <th className="px-4 py-3 text-right font-medium">الإجراء المقترح</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{row.id}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">{row.category}</td>
                  <td className="px-4 py-3 text-gray-600">{row.field}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${severityColor[row.severity]}`}>
                      {row.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{row.target}</td>
                  <td className="px-4 py-3 text-gray-600">{row.actual}</td>
                  <td className="px-4 py-3 text-gray-600">{row.impact}</td>
                  <td className="px-4 py-3 text-gray-600">{row.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
