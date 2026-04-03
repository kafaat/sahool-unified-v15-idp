'use client';

// Reports Page - Report Generation & Viewing
// صفحة التقارير — إنشاء وعرض التقارير

import { useState, useCallback } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { cn } from '@/lib/utils';
import {
  FileText,
  BarChart3,
  Leaf,
  Droplets,
  Bug,
  TrendingUp,
  Globe,
  Download,
  Eye,
  Share2,
  Plus,
  Calendar,
  MapPin,
  CheckSquare,
  X,
  Loader2,
  FileSpreadsheet,
  FileDown,
  Map,
} from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// أنواع البيانات
// ═══════════════════════════════════════════════════════════════════════════

type ReportTypeKey =
  | 'monthly_performance'
  | 'crop_health'
  | 'irrigation'
  | 'pest'
  | 'yield'
  | 'soil';

type ReportStatus = 'completed' | 'processing' | 'failed' | 'scheduled';
type ExportFormat = 'pdf' | 'excel' | 'geojson';

interface ReportType {
  key: ReportTypeKey;
  title_ar: string;
  title_en: string;
  description_ar: string;
  icon: React.ElementType;
  iconColor: string;
  bgColor: string;
}

interface RecentReport {
  id: string;
  name_ar: string;
  name_en: string;
  type: ReportTypeKey;
  date: string;
  fields: number;
  status: ReportStatus;
  format: ExportFormat;
  size_mb: number;
}

interface GenerateFormData {
  reportType: ReportTypeKey | '';
  dateFrom: string;
  dateTo: string;
  selectedFields: string[];
  includeNdvi: boolean;
  includeWeather: boolean;
  includeYield: boolean;
  includeSoil: boolean;
  includePests: boolean;
  exportFormat: ExportFormat;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// الثوابت
// ═══════════════════════════════════════════════════════════════════════════

const REPORT_TYPES: ReportType[] = [
  {
    key: 'monthly_performance',
    title_ar: 'تقرير الأداء الشهري',
    title_en: 'Monthly Performance',
    description_ar: 'ملخص شامل لأداء المزرعة والحقول خلال الشهر',
    icon: BarChart3,
    iconColor: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
  },
  {
    key: 'crop_health',
    title_ar: 'تقرير صحة المحاصيل',
    title_en: 'Crop Health',
    description_ar: 'تحليل NDVI وحالة النمو والأمراض المكتشفة',
    icon: Leaf,
    iconColor: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
  },
  {
    key: 'irrigation',
    title_ar: 'تقرير الري',
    title_en: 'Irrigation',
    description_ar: 'استهلاك المياه وكفاءة الري والجدولة',
    icon: Droplets,
    iconColor: 'text-cyan-600',
    bgColor: 'bg-cyan-50 dark:bg-cyan-900/20',
  },
  {
    key: 'pest',
    title_ar: 'تقرير الآفات',
    title_en: 'Pest Report',
    description_ar: 'رصد الآفات والأمراض وخطط المكافحة المتكاملة',
    icon: Bug,
    iconColor: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
  },
  {
    key: 'yield',
    title_ar: 'تقرير الإنتاجية',
    title_en: 'Yield Report',
    description_ar: 'تحليل الإنتاجية المتوقعة والفعلية ومقارنة المواسم',
    icon: TrendingUp,
    iconColor: 'text-amber-600',
    bgColor: 'bg-amber-50 dark:bg-amber-900/20',
  },
  {
    key: 'soil',
    title_ar: 'تقرير التربة',
    title_en: 'Soil Report',
    description_ar: 'تحليل خصائص التربة والملوحة والعناصر الغذائية',
    icon: Globe,
    iconColor: 'text-emerald-700',
    bgColor: 'bg-emerald-50 dark:bg-emerald-900/20',
  },
];

const MOCK_FIELDS = [
  { id: 'FIELD-001', name_ar: 'حقل القمح الشمالي' },
  { id: 'FIELD-002', name_ar: 'حقل الشعير الغربي' },
  { id: 'FIELD-003', name_ar: 'بستان النخيل' },
  { id: 'FIELD-004', name_ar: 'حقل الطماطم' },
  { id: 'FIELD-005', name_ar: 'حقل البرسيم' },
  { id: 'FIELD-006', name_ar: 'حقل الخيار' },
];

const MOCK_RECENT_REPORTS: RecentReport[] = [
  {
    id: 'RPT-001',
    name_ar: 'تقرير الأداء - مارس 2026',
    name_en: 'Performance Report - March 2026',
    type: 'monthly_performance',
    date: '2026-03-31',
    fields: 6,
    status: 'completed',
    format: 'pdf',
    size_mb: 2.4,
  },
  {
    id: 'RPT-002',
    name_ar: 'تقرير صحة المحاصيل - الربع الأول',
    name_en: 'Crop Health Q1 Report',
    type: 'crop_health',
    date: '2026-03-28',
    fields: 4,
    status: 'completed',
    format: 'pdf',
    size_mb: 5.1,
  },
  {
    id: 'RPT-003',
    name_ar: 'تقرير الري الأسبوعي',
    name_en: 'Weekly Irrigation Report',
    type: 'irrigation',
    date: '2026-03-25',
    fields: 3,
    status: 'processing',
    format: 'excel',
    size_mb: 0,
  },
  {
    id: 'RPT-004',
    name_ar: 'تقرير رصد الآفات - فبراير',
    name_en: 'Pest Monitoring - February',
    type: 'pest',
    date: '2026-02-28',
    fields: 5,
    status: 'completed',
    format: 'pdf',
    size_mb: 3.7,
  },
  {
    id: 'RPT-005',
    name_ar: 'تقرير تحليل التربة - الحقل 3',
    name_en: 'Soil Analysis - Field 3',
    type: 'soil',
    date: '2026-02-15',
    fields: 1,
    status: 'failed',
    format: 'geojson',
    size_mb: 0,
  },
];

const INITIAL_FORM: GenerateFormData = {
  reportType: '',
  dateFrom: '',
  dateTo: '',
  selectedFields: [],
  includeNdvi: true,
  includeWeather: true,
  includeYield: false,
  includeSoil: false,
  includePests: false,
  exportFormat: 'pdf',
};

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// دوال مساعدة
// ═══════════════════════════════════════════════════════════════════════════

function getReportTypeLabel(key: ReportTypeKey): string {
  return REPORT_TYPES.find((r) => r.key === key)?.title_ar ?? key;
}

function getStatusConfig(status: ReportStatus) {
  switch (status) {
    case 'completed':
      return { label: 'مكتمل', color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' };
    case 'processing':
      return { label: 'قيد المعالجة', color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' };
    case 'failed':
      return { label: 'فشل', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' };
    case 'scheduled':
      return { label: 'مجدول', color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' };
  }
}

function getFormatIcon(format: ExportFormat) {
  switch (format) {
    case 'pdf':
      return FileDown;
    case 'excel':
      return FileSpreadsheet;
    case 'geojson':
      return Map;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// المكون الرئيسي
// ═══════════════════════════════════════════════════════════════════════════

export default function ReportsPage() {
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [formData, setFormData] = useState<GenerateFormData>(INITIAL_FORM);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedTypeCard, setSelectedTypeCard] = useState<ReportTypeKey | null>(null);

  const handleOpenForm = useCallback((typeKey?: ReportTypeKey) => {
    setFormData({
      ...INITIAL_FORM,
      reportType: typeKey ?? '',
    });
    setSelectedTypeCard(typeKey ?? null);
    setShowGenerateForm(true);
  }, []);

  const handleCloseForm = useCallback(() => {
    setShowGenerateForm(false);
    setFormData(INITIAL_FORM);
    setSelectedTypeCard(null);
  }, []);

  const handleFieldToggle = useCallback((fieldId: string) => {
    setFormData((prev) => ({
      ...prev,
      selectedFields: prev.selectedFields.includes(fieldId)
        ? prev.selectedFields.filter((f) => f !== fieldId)
        : [...prev.selectedFields, fieldId],
    }));
  }, []);

  const handleGenerate = useCallback(async () => {
    if (!formData.reportType || !formData.dateFrom || !formData.dateTo) return;
    setIsGenerating(true);
    // Simulate report generation
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsGenerating(false);
    handleCloseForm();
  }, [formData, handleCloseForm]);

  // ─── Stats ──────────────────────────────────────────────────────────────
  const completedCount = MOCK_RECENT_REPORTS.filter((r) => r.status === 'completed').length;
  const processingCount = MOCK_RECENT_REPORTS.filter((r) => r.status === 'processing').length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950" dir="rtl">
      <Header
        title="التقارير — Reports"
        subtitle="إنشاء وإدارة التقارير الزراعية"
        actions={
          <button
            type="button"
            onClick={() => handleOpenForm()}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 hover:bg-sahool-700 text-white rounded-xl text-sm font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>إنشاء تقرير</span>
          </button>
        }
      />

      <main className="p-6 space-y-8 max-w-7xl mx-auto">
        {/* ── Summary Stats ──────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="إجمالي التقارير"
            value={MOCK_RECENT_REPORTS.length}
            icon={FileText}
            iconColor="text-sahool-600"
          />
          <StatCard
            title="تقارير مكتملة"
            value={completedCount}
            icon={CheckSquare}
            iconColor="text-green-600"
            trend={{ value: 12, isPositive: true }}
          />
          <StatCard
            title="قيد المعالجة"
            value={processingCount}
            icon={Loader2}
            iconColor="text-blue-600"
          />
          <StatCard
            title="أنواع التقارير"
            value={REPORT_TYPES.length}
            icon={BarChart3}
            iconColor="text-amber-600"
          />
        </div>

        {/* ── Report Type Cards (2x3 grid) ───────────────────────────── */}
        <section>
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
            أنواع التقارير
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {REPORT_TYPES.map((type) => {
              const Icon = type.icon;
              const isSelected = selectedTypeCard === type.key;
              return (
                <button
                  key={type.key}
                  type="button"
                  onClick={() => handleOpenForm(type.key)}
                  className={cn(
                    'relative flex flex-col items-center gap-3 p-6 rounded-xl border transition-all text-center',
                    'hover:shadow-md hover:border-sahool-300 dark:hover:border-sahool-600',
                    isSelected
                      ? 'border-sahool-500 ring-2 ring-sahool-200 dark:ring-sahool-800 shadow-md'
                      : 'border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800'
                  )}
                >
                  <div className={cn('p-4 rounded-xl', type.bgColor)}>
                    <Icon className={cn('w-8 h-8', type.iconColor)} />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 dark:text-gray-100 text-sm">
                      {type.title_ar}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {type.title_en}
                    </p>
                  </div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 leading-relaxed">
                    {type.description_ar}
                  </p>
                </button>
              );
            })}
          </div>
        </section>

        {/* ── Recent Reports Table ────────────────────────────────────── */}
        <section>
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
            التقارير الأخيرة
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                    <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                      اسم التقرير
                    </th>
                    <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                      النوع
                    </th>
                    <th className="text-right px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                      التاريخ
                    </th>
                    <th className="text-center px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                      الحقول
                    </th>
                    <th className="text-center px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                      الصيغة
                    </th>
                    <th className="text-center px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                      الحالة
                    </th>
                    <th className="text-center px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                      الإجراءات
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {MOCK_RECENT_REPORTS.map((report) => {
                    const statusCfg = getStatusConfig(report.status);
                    const FormatIcon = getFormatIcon(report.format);
                    return (
                      <tr
                        key={report.id}
                        className="border-b border-gray-50 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                      >
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-gray-400 shrink-0" />
                            <div>
                              <p className="font-medium text-gray-900 dark:text-gray-100">
                                {report.name_ar}
                              </p>
                              <p className="text-xs text-gray-400">{report.id}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-gray-600 dark:text-gray-300">
                          {getReportTypeLabel(report.type)}
                        </td>
                        <td className="px-4 py-3 text-gray-600 dark:text-gray-300">
                          {new Date(report.date).toLocaleDateString('ar-SA')}
                        </td>
                        <td className="px-4 py-3 text-center text-gray-600 dark:text-gray-300">
                          {report.fields}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                            <FormatIcon className="w-3.5 h-3.5" />
                            {report.format.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span
                            className={cn(
                              'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                              statusCfg.color
                            )}
                          >
                            {statusCfg.label}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-center gap-1">
                            <button
                              type="button"
                              title="تحميل"
                              disabled={report.status !== 'completed'}
                              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                            <button
                              type="button"
                              title="عرض"
                              disabled={report.status !== 'completed'}
                              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              type="button"
                              title="مشاركة"
                              disabled={report.status !== 'completed'}
                              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            >
                              <Share2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>

      {/* ── Generate Report Modal ─────────────────────────────────────── */}
      {showGenerateForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
            dir="rtl"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-700">
              <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                إنشاء تقرير جديد
              </h2>
              <button
                type="button"
                onClick={handleCloseForm}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="px-6 py-5 space-y-6">
              {/* Report Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  نوع التقرير <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.reportType}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      reportType: e.target.value as ReportTypeKey,
                    }))
                  }
                  className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
                >
                  <option value="">اختر نوع التقرير...</option>
                  {REPORT_TYPES.map((t) => (
                    <option key={t.key} value={t.key}>
                      {t.title_ar} — {t.title_en}
                    </option>
                  ))}
                </select>
              </div>

              {/* Date Range */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Calendar className="w-4 h-4 inline-block ml-1" />
                    من تاريخ <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.dateFrom}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, dateFrom: e.target.value }))
                    }
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Calendar className="w-4 h-4 inline-block ml-1" />
                    إلى تاريخ <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.dateTo}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, dateTo: e.target.value }))
                    }
                    className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Field Selector (multi-select) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <MapPin className="w-4 h-4 inline-block ml-1" />
                  الحقول
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {MOCK_FIELDS.map((field) => {
                    const isChecked = formData.selectedFields.includes(field.id);
                    return (
                      <label
                        key={field.id}
                        className={cn(
                          'flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer text-sm transition-colors',
                          isChecked
                            ? 'border-sahool-400 bg-sahool-50 dark:bg-sahool-900/20 dark:border-sahool-600'
                            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                        )}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => handleFieldToggle(field.id)}
                          className="rounded border-gray-300 text-sahool-600 focus:ring-sahool-500"
                        />
                        <span className="text-gray-700 dark:text-gray-300">{field.name_ar}</span>
                        <span className="text-xs text-gray-400 mr-auto">{field.id}</span>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Include Options */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <CheckSquare className="w-4 h-4 inline-block ml-1" />
                  تضمين في التقرير
                </label>
                <div className="flex flex-wrap gap-3">
                  {[
                    { key: 'includeNdvi' as const, label: 'NDVI', labelAr: 'مؤشر الغطاء النباتي' },
                    { key: 'includeWeather' as const, label: 'Weather', labelAr: 'الطقس' },
                    { key: 'includeYield' as const, label: 'Yield', labelAr: 'الإنتاجية' },
                    { key: 'includeSoil' as const, label: 'Soil', labelAr: 'التربة' },
                    { key: 'includePests' as const, label: 'Pests', labelAr: 'الآفات' },
                  ].map((opt) => (
                    <label
                      key={opt.key}
                      className={cn(
                        'flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer text-sm transition-colors',
                        formData[opt.key]
                          ? 'border-sahool-400 bg-sahool-50 dark:bg-sahool-900/20 dark:border-sahool-600'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                      )}
                    >
                      <input
                        type="checkbox"
                        checked={formData[opt.key]}
                        onChange={() =>
                          setFormData((prev) => ({ ...prev, [opt.key]: !prev[opt.key] }))
                        }
                        className="rounded border-gray-300 text-sahool-600 focus:ring-sahool-500"
                      />
                      <span className="text-gray-700 dark:text-gray-300">{opt.labelAr}</span>
                      <span className="text-xs text-gray-400">({opt.label})</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Export Format */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  صيغة التصدير
                </label>
                <div className="flex gap-3">
                  {(
                    [
                      { value: 'pdf' as ExportFormat, label: 'PDF', icon: FileDown },
                      { value: 'excel' as ExportFormat, label: 'Excel', icon: FileSpreadsheet },
                      { value: 'geojson' as ExportFormat, label: 'GeoJSON', icon: Map },
                    ] as const
                  ).map((fmt) => {
                    const FmtIcon = fmt.icon;
                    return (
                      <button
                        key={fmt.value}
                        type="button"
                        onClick={() =>
                          setFormData((prev) => ({ ...prev, exportFormat: fmt.value }))
                        }
                        className={cn(
                          'flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-all',
                          formData.exportFormat === fmt.value
                            ? 'border-sahool-500 bg-sahool-50 dark:bg-sahool-900/20 text-sahool-700 dark:text-sahool-300 ring-2 ring-sahool-200 dark:ring-sahool-800'
                            : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-500'
                        )}
                      >
                        <FmtIcon className="w-4 h-4" />
                        {fmt.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 dark:border-gray-700">
              <button
                type="button"
                onClick={handleCloseForm}
                className="px-5 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                إلغاء
              </button>
              <button
                type="button"
                onClick={handleGenerate}
                disabled={
                  isGenerating || !formData.reportType || !formData.dateFrom || !formData.dateTo
                }
                className={cn(
                  'flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-white transition-colors',
                  'bg-sahool-600 hover:bg-sahool-700 disabled:opacity-50 disabled:cursor-not-allowed'
                )}
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    جارٍ الإنشاء...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    إنشاء التقرير
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
