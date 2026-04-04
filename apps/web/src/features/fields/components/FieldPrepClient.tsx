'use client';

/**
 * Field Preparation Client Component
 * تحضير الحقل — سير عمل التحضير قبل الزراعة
 *
 * Pre-season field preparation workflow with 7 steps:
 * Soil Analysis -> Primary Tillage -> Secondary Tillage ->
 * Land Leveling -> Base Fertilization -> Irrigation Setup -> Establishment Irrigation
 */

import { useState, useMemo, useCallback } from 'react';
import {
  CheckCircle2,
  Circle,
  Clock,
  Loader2,
  ChevronDown,
  ChevronRight,
  FlaskConical,
  Tractor,
  Layers,
  Ruler,
  Sprout,
  Droplets,
  Save,
  Printer,
  DollarSign,
  CalendarDays,
  ExternalLink,
  Wheat,
  Info,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type StepStatus = 'completed' | 'in_progress' | 'pending';

interface PrepStep {
  id: number;
  titleAr: string;
  titleEn: string;
  status: StepStatus;
  date?: string;
  details: Record<string, string>;
  recommendationAr?: string;
  costSar?: number;
  linkLabel?: string;
  linkHref?: string;
}

interface FieldOption {
  id: string;
  nameAr: string;
  areaHa: number;
}

interface SeasonOption {
  id: string;
  labelAr: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const STATUS_CONFIG: Record<StepStatus, { labelAr: string; icon: typeof CheckCircle2; color: string; bgColor: string; borderColor: string }> = {
  completed: {
    labelAr: 'مكتمل', icon: CheckCircle2, color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-900/20', borderColor: 'border-green-200 dark:border-green-800',
  },
  in_progress: {
    labelAr: 'قيد التنفيذ', icon: Loader2, color: 'text-amber-600 dark:text-amber-400',
    bgColor: 'bg-amber-50 dark:bg-amber-900/20', borderColor: 'border-amber-200 dark:border-amber-800',
  },
  pending: {
    labelAr: 'قيد الانتظار', icon: Clock, color: 'text-gray-400 dark:text-gray-500',
    bgColor: 'bg-gray-50 dark:bg-gray-800/50', borderColor: 'border-gray-200 dark:border-gray-700',
  },
};

const STEP_ICONS = [FlaskConical, Tractor, Layers, Ruler, Sprout, Droplets, Droplets];

const FIELDS: FieldOption[] = [
  { id: 'FIELD-003', nameAr: 'حقل القمح', areaHa: 8.5 },
  { id: 'FIELD-001', nameAr: 'حقل الشعير', areaHa: 5.2 },
  { id: 'FIELD-007', nameAr: 'حقل الطماطم', areaHa: 3.0 },
  { id: 'FIELD-012', nameAr: 'حقل النخيل', areaHa: 12.0 },
];

const SEASONS: SeasonOption[] = [
  { id: 'winter-2026', labelAr: 'شتاء 2026' },
  { id: 'summer-2026', labelAr: 'صيف 2026' },
  { id: 'winter-2027', labelAr: 'شتاء 2027' },
];

const INITIAL_STEPS: PrepStep[] = [
  {
    id: 1, titleAr: 'تحليل التربة', titleEn: 'Soil Analysis', status: 'completed', date: '2026-09-15',
    details: { 'pH': '7.2', 'النيتروجين (N)': '22 ppm', 'الفوسفور (P)': '18 ppm', 'البوتاسيوم (K)': '180 ppm', 'الملوحة (EC)': '1.8 dS/m', 'المادة العضوية': '1.4%' },
    recommendationAr: 'إضافة يوريا 46 كجم/هكتار لتعويض نقص النيتروجين', costSar: 350,
    linkLabel: 'عرض تقرير التحليل الكامل', linkHref: '/soil-analysis',
  },
  {
    id: 2, titleAr: 'حراثة أولية', titleEn: 'Primary Tillage', status: 'completed', date: '2026-09-20',
    details: { 'العمق': '30 سم', 'المعدة': 'جرار + محراث قرصي', 'عدد التمريرات': '2', 'اتجاه الحراثة': 'متقاطع' },
    recommendationAr: 'تفكيك التربة المتماسكة وقلب المخلفات النباتية', costSar: 400,
  },
  {
    id: 3, titleAr: 'حراثة ثانية (تنعيم)', titleEn: 'Secondary Tillage', status: 'completed', date: '2026-09-25',
    details: { 'العمق': '15 سم', 'المعدة': 'روتوفيتور', 'حجم الكتل': 'أقل من 5 سم', 'حالة التربة': 'رطوبة مناسبة' },
    recommendationAr: 'تنعيم التربة لتهيئة مرقد بذرة مثالي', costSar: 300,
  },
  {
    id: 4, titleAr: 'تسوية الأرض', titleEn: 'Land Leveling', status: 'in_progress',
    details: { 'الانحدار المطلوب': '0.1 - 0.2%', 'الطريقة': 'تسوية ليزرية', 'فرق الارتفاع الحالي': '18 سم', 'حجم القطع': '245 م\u00B3', 'حجم الردم': '238 م\u00B3' },
    costSar: 600, linkLabel: 'عرض خريطة التسوية', linkHref: '/terrain',
  },
  {
    id: 5, titleAr: 'تسميد أساسي', titleEn: 'Base Fertilization', status: 'pending',
    details: { 'DAP (18-46-0)': '50 كجم/هكتار', 'سلفات بوتاسيوم': '30 كجم/هكتار', 'سوبر فوسفات': '25 كجم/هكتار', 'طريقة الإضافة': 'نثر قبل الحراثة النهائية' },
    recommendationAr: 'إضافة الأسمدة الأساسية لتوفير العناصر الغذائية خلال المراحل الأولى من النمو', costSar: 450,
  },
  {
    id: 6, titleAr: 'تجهيز شبكة الري', titleEn: 'Irrigation Network Setup', status: 'pending',
    details: { 'النوع': 'تنقيط', 'عدد الخطوط': '12', 'المسافة بين الخطوط': '30 سم', 'المسافة بين النقاطات': '20 سم', 'تصريف النقاط': '4 لتر/ساعة', 'ضغط التشغيل': '1.5 بار' },
    costSar: 250,
  },
  {
    id: 7, titleAr: 'ري تأسيسي', titleEn: 'Establishment Irrigation', status: 'pending',
    details: { 'الكمية': '40 مم', 'المدة المتوقعة': '6 ساعات', 'الهدف': 'ترطيب العمق الجذري (0-40 سم)', 'رطوبة التربة المستهدفة': '75% من السعة الحقلية' },
    recommendationAr: 'ري عميق لتأسيس رطوبة كافية قبل الزراعة مباشرة', costSar: 150,
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function FieldPrepClient() {
  const [selectedField, setSelectedField] = useState(FIELDS[0]!.id);
  const [selectedSeason, setSelectedSeason] = useState(SEASONS[0]!.id);
  const [steps, setSteps] = useState<PrepStep[]>(INITIAL_STEPS);
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set([4]));

  const field = useMemo(() => (FIELDS.find((f) => f.id === selectedField) ?? FIELDS[0])!, [selectedField]);
  const completedCount = useMemo(() => steps.filter((s) => s.status === 'completed').length, [steps]);
  const progressPercent = useMemo(() => Math.round((completedCount / steps.length) * 100), [completedCount, steps.length]);
  const totalCostPerHa = useMemo(() => steps.reduce((sum, s) => sum + (s.costSar ?? 0), 0), [steps]);
  const totalCost = useMemo(() => totalCostPerHa * field.areaHa, [totalCostPerHa, field.areaHa]);
  const spentSoFar = useMemo(
    () => steps.filter((s) => s.status === 'completed').reduce((sum, s) => sum + (s.costSar ?? 0) * field.areaHa, 0),
    [steps, field.areaHa],
  );

  const toggleExpand = useCallback((stepId: number) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      next.has(stepId) ? next.delete(stepId) : next.add(stepId);
      return next;
    });
  }, []);

  const toggleStepStatus = useCallback((stepId: number) => {
    setSteps((prev) =>
      prev.map((step) => {
        if (step.id !== stepId) return step;
        const nextStatus: StepStatus = step.status === 'pending' ? 'in_progress' : step.status === 'in_progress' ? 'completed' : 'pending';
        return { ...step, status: nextStatus, date: nextStatus === 'completed' ? new Date().toISOString().split('T')[0] : step.date };
      }),
    );
  }, []);

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-5">
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">تحضير الحقل — Field Preparation</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">الخطوات الأساسية قبل الزراعة</p>
      </div>

      <main className="p-6 space-y-6 max-w-4xl mx-auto">
        {/* Selectors */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">الحقل</label>
            <div className="relative">
              <select
                value={selectedField}
                onChange={(e) => setSelectedField(e.target.value)}
                className="w-full appearance-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 py-2.5 pr-4 pl-10 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {FIELDS.map((f) => (
                  <option key={f.id} value={f.id}>{f.nameAr} — {f.areaHa} هكتار</option>
                ))}
              </select>
              <Wheat className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">الموسم</label>
            <div className="relative">
              <select
                value={selectedSeason}
                onChange={(e) => setSelectedSeason(e.target.value)}
                className="w-full appearance-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 py-2.5 pr-4 pl-10 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {SEASONS.map((s) => (
                  <option key={s.id} value={s.id}>{s.labelAr}</option>
                ))}
              </select>
              <CalendarDays className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">التقدم الإجمالي</span>
            <span className="text-sm font-bold text-green-600 dark:text-green-400">{progressPercent}% مكتمل</span>
          </div>
          <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ease-out ${progressPercent === 100 ? 'bg-green-500' : progressPercent >= 50 ? 'bg-green-400' : 'bg-amber-400'}`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
            <span>{completedCount} من {steps.length} خطوات مكتملة</span>
            <span>{field.nameAr} — {field.areaHa} هكتار</span>
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-3">
          {steps.map((step) => {
            const config = STATUS_CONFIG[step.status];
            const StatusIcon = config.icon;
            const StepIcon = STEP_ICONS[step.id - 1] ?? Circle;
            const isExpanded = expandedSteps.has(step.id);

            return (
              <div key={step.id} className={`rounded-xl border transition-all duration-200 ${config.borderColor} ${config.bgColor}`}>
                <button
                  onClick={() => toggleExpand(step.id)}
                  className="w-full flex items-center gap-3 p-4 text-right"
                >
                  <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${
                    step.status === 'completed' ? 'bg-green-100 dark:bg-green-900/40' : step.status === 'in_progress' ? 'bg-amber-100 dark:bg-amber-900/40' : 'bg-gray-100 dark:bg-gray-700'
                  }`}>
                    <StepIcon className={`w-5 h-5 ${config.color}`} />
                  </div>

                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                      الخطوة {step.id}: {step.titleAr}
                    </h3>
                    <div className="flex items-center gap-2 mt-0.5">
                      <StatusIcon className={`w-3.5 h-3.5 ${config.color} ${step.status === 'in_progress' ? 'animate-spin' : ''}`} />
                      <span className={`text-xs font-medium ${config.color}`}>{config.labelAr}</span>
                      {step.date && (
                        <>
                          <span className="text-xs text-gray-400">|</span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">تاريخ: {step.date}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {step.costSar && (
                    <span className="hidden sm:inline-flex items-center gap-1 text-xs font-medium text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 rounded-full px-2.5 py-1">
                      <DollarSign className="w-3 h-3" />
                      {step.costSar.toLocaleString()} ريال/هـ
                    </span>
                  )}

                  {isExpanded ? <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" /> : <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />}
                </button>

                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-200 dark:border-gray-700 pt-3 mr-13">
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-2">
                      {Object.entries(step.details).map(([key, value]) => (
                        <div key={key}>
                          <dt className="text-xs text-gray-500 dark:text-gray-400">{key}</dt>
                          <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{value}</dd>
                        </div>
                      ))}
                    </div>

                    {step.recommendationAr && (
                      <div className="mt-3 flex items-start gap-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-100 dark:border-blue-800">
                        <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="text-xs font-medium text-blue-700 dark:text-blue-300 mb-0.5">التوصية</p>
                          <p className="text-sm text-blue-600 dark:text-blue-400">{step.recommendationAr}</p>
                        </div>
                      </div>
                    )}

                    <div className="mt-3 flex items-center justify-between flex-wrap gap-2">
                      {step.linkLabel && step.linkHref && (
                        <a href={step.linkHref} className="inline-flex items-center gap-1.5 text-xs font-medium text-green-600 dark:text-green-400 hover:underline">
                          <ExternalLink className="w-3.5 h-3.5" />
                          {step.linkLabel}
                        </a>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleStepStatus(step.id); }}
                        className={`inline-flex items-center gap-1.5 text-xs font-medium rounded-lg px-3 py-1.5 transition-colors ${
                          step.status === 'completed'
                            ? 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-300'
                            : step.status === 'in_progress'
                              ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300 hover:bg-green-200'
                              : 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300 hover:bg-amber-200'
                        }`}
                      >
                        {step.status === 'pending' && <><Loader2 className="w-3.5 h-3.5" />بدء التنفيذ</>}
                        {step.status === 'in_progress' && <><CheckCircle2 className="w-3.5 h-3.5" />تعليم كمكتمل</>}
                        {step.status === 'completed' && <><Circle className="w-3.5 h-3.5" />إعادة فتح</>}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Cost Estimation */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-2 mb-3">
            <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">التكلفة التقديرية</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">لكل هكتار</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{totalCostPerHa.toLocaleString()} ريال</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">إجمالي الحقل ({field.areaHa} هـ)</p>
              <p className="text-lg font-bold text-green-700 dark:text-green-300">{totalCost.toLocaleString()} ريال</p>
            </div>
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">المصروف حتى الآن</p>
              <p className="text-lg font-bold text-blue-700 dark:text-blue-300">{spentSoFar.toLocaleString()} ريال</p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3 print:hidden">
          <button
            onClick={() => alert('تم حفظ التقدم بنجاح')}
            className="inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-medium bg-green-600 text-white hover:bg-green-700 transition-colors"
          >
            <Save className="w-4 h-4" />
            حفظ التقدم
          </button>
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-medium bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <Printer className="w-4 h-4" />
            طباعة قائمة المهام
          </button>
        </div>
      </main>
    </div>
  );
}
