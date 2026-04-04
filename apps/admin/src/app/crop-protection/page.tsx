// @ts-nocheck
'use client';

// Crop Protection Management Page
// صفحة إدارة حماية المحاصيل — الأمراض والآفات وبرنامج الرش

import { useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import { cn, formatDate } from '@/lib/utils';
import {
  Bug,
  Shield,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Search,
  FileText,
  ClipboardCheck,
  Wind,
  Thermometer,
  Droplets,
  Clock,
  MapPin,
  Leaf,
  Target,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Disease {
  id: string;
  nameAr: string;
  nameEn: string;
  crop: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  affectedFields: number;
  lastDetected: string;
  treatmentStatus: 'untreated' | 'in_progress' | 'treated' | 'monitoring';
  affectedAreaPct: number;
}

interface Pest {
  id: string;
  nameAr: string;
  nameEn: string;
  crop: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  threshold: string;
  actionRequired: boolean;
  ipmStrategy: string;
  lastScouting: string;
  populationTrend: 'increasing' | 'stable' | 'decreasing';
}

interface SpraySchedule {
  id: string;
  fieldName: string;
  product: string;
  targetAr: string;
  scheduledDate: string;
  weatherSuitable: boolean;
  windSpeed: number;
  temperature: number;
  humidity: number;
  phi: number; // Pre-Harvest Interval in days
  costPerHectare: number;
  areHectares: number;
  status: 'scheduled' | 'completed' | 'postponed' | 'cancelled';
}

// ---------------------------------------------------------------------------
// Mock Data
// ---------------------------------------------------------------------------

const DISEASES: Disease[] = [
  {
    id: 'd1',
    nameAr: 'صدأ الأوراق',
    nameEn: 'Leaf Rust',
    crop: 'قمح',
    severity: 'high',
    affectedFields: 4,
    lastDetected: '2026-03-30',
    treatmentStatus: 'in_progress',
    affectedAreaPct: 22,
  },
  {
    id: 'd2',
    nameAr: 'اللفحة المتأخرة',
    nameEn: 'Late Blight',
    crop: 'طماطم',
    severity: 'critical',
    affectedFields: 2,
    lastDetected: '2026-04-01',
    treatmentStatus: 'untreated',
    affectedAreaPct: 35,
  },
  {
    id: 'd3',
    nameAr: 'البياض الدقيقي',
    nameEn: 'Powdery Mildew',
    crop: 'خيار',
    severity: 'medium',
    affectedFields: 3,
    lastDetected: '2026-03-28',
    treatmentStatus: 'treated',
    affectedAreaPct: 10,
  },
  {
    id: 'd4',
    nameAr: 'تبقع الأوراق',
    nameEn: 'Leaf Spot',
    crop: 'شعير',
    severity: 'low',
    affectedFields: 1,
    lastDetected: '2026-03-25',
    treatmentStatus: 'monitoring',
    affectedAreaPct: 5,
  },
  {
    id: 'd5',
    nameAr: 'الذبول الفيوزاري',
    nameEn: 'Fusarium Wilt',
    crop: 'طماطم',
    severity: 'high',
    affectedFields: 2,
    lastDetected: '2026-04-02',
    treatmentStatus: 'in_progress',
    affectedAreaPct: 18,
  },
  {
    id: 'd6',
    nameAr: 'العفن الرمادي',
    nameEn: 'Gray Mold (Botrytis)',
    crop: 'فراولة',
    severity: 'medium',
    affectedFields: 1,
    lastDetected: '2026-03-27',
    treatmentStatus: 'treated',
    affectedAreaPct: 8,
  },
  {
    id: 'd7',
    nameAr: 'تبرقش الأوراق',
    nameEn: 'Mosaic Virus',
    crop: 'خيار',
    severity: 'critical',
    affectedFields: 3,
    lastDetected: '2026-04-03',
    treatmentStatus: 'untreated',
    affectedAreaPct: 40,
  },
  {
    id: 'd8',
    nameAr: 'التفحم السائب',
    nameEn: 'Loose Smut',
    crop: 'قمح',
    severity: 'low',
    affectedFields: 1,
    lastDetected: '2026-03-20',
    treatmentStatus: 'monitoring',
    affectedAreaPct: 3,
  },
];

const PESTS: Pest[] = [
  {
    id: 'p1',
    nameAr: 'سوسة النخيل الحمراء',
    nameEn: 'Red Palm Weevil',
    crop: 'نخيل',
    riskLevel: 'critical',
    threshold: '1 حشرة / مصيدة',
    actionRequired: true,
    ipmStrategy: 'مصائد فرمونية + حقن جذعي بالإيمامكتين بنزوات',
    lastScouting: '2026-04-02',
    populationTrend: 'increasing',
  },
  {
    id: 'p2',
    nameAr: 'المن الأخضر',
    nameEn: 'Green Aphid',
    crop: 'قمح',
    riskLevel: 'high',
    threshold: '50 حشرة / نبات',
    actionRequired: true,
    ipmStrategy: 'أعداء طبيعية (أبو العيد) + رش بالإيميداكلوبريد عند تجاوز العتبة',
    lastScouting: '2026-04-01',
    populationTrend: 'increasing',
  },
  {
    id: 'p3',
    nameAr: 'الذبابة البيضاء',
    nameEn: 'Whitefly',
    crop: 'طماطم',
    riskLevel: 'medium',
    threshold: '10 حشرات / ورقة',
    actionRequired: false,
    ipmStrategy: 'مصائد صفراء لاصقة + مكافحة بيولوجية (إنكارسيا)',
    lastScouting: '2026-03-30',
    populationTrend: 'stable',
  },
  {
    id: 'p4',
    nameAr: 'دودة الثمار',
    nameEn: 'Fruit Borer',
    crop: 'طماطم',
    riskLevel: 'high',
    threshold: '5% إصابة ثمار',
    actionRequired: true,
    ipmStrategy: 'مصائد ضوئية + رش بالباسيلس ثورينجيينسيس (Bt)',
    lastScouting: '2026-04-01',
    populationTrend: 'increasing',
  },
  {
    id: 'p5',
    nameAr: 'العنكبوت الأحمر',
    nameEn: 'Red Spider Mite',
    crop: 'خيار',
    riskLevel: 'medium',
    threshold: '5 أفراد / ورقة',
    actionRequired: false,
    ipmStrategy: 'مفترسات (فايتوسيلس) + رش بالأباميكتين عند الضرورة',
    lastScouting: '2026-03-29',
    populationTrend: 'stable',
  },
  {
    id: 'p6',
    nameAr: 'الجراد الصحراوي',
    nameEn: 'Desert Locust',
    crop: 'جميع المحاصيل',
    riskLevel: 'low',
    threshold: 'تجمعات صغيرة',
    actionRequired: false,
    ipmStrategy: 'مراقبة الأسراب + تنسيق مع وزارة الزراعة',
    lastScouting: '2026-03-25',
    populationTrend: 'decreasing',
  },
];

const SPRAY_SCHEDULE: SpraySchedule[] = [
  {
    id: 's1',
    fieldName: 'حقل القمح الشمالي',
    product: 'بروبيكونازول 25% EC',
    targetAr: 'صدأ الأوراق',
    scheduledDate: '2026-04-05',
    weatherSuitable: true,
    windSpeed: 8,
    temperature: 24,
    humidity: 55,
    phi: 30,
    costPerHectare: 320,
    areHectares: 5.2,
    status: 'scheduled',
  },
  {
    id: 's2',
    fieldName: 'حقل الطماطم - القطاع أ',
    product: 'كلوروثالونيل 72% WP',
    targetAr: 'اللفحة المتأخرة',
    scheduledDate: '2026-04-04',
    weatherSuitable: false,
    windSpeed: 22,
    temperature: 30,
    humidity: 40,
    phi: 7,
    costPerHectare: 450,
    areHectares: 2.0,
    status: 'postponed',
  },
  {
    id: 's3',
    fieldName: 'بيت محمي الخيار 3',
    product: 'أباميكتين 1.8% EC',
    targetAr: 'العنكبوت الأحمر',
    scheduledDate: '2026-04-03',
    weatherSuitable: true,
    windSpeed: 5,
    temperature: 26,
    humidity: 65,
    phi: 3,
    costPerHectare: 280,
    areHectares: 0.5,
    status: 'completed',
  },
  {
    id: 's4',
    fieldName: 'حقل الشعير الغربي',
    product: 'إيميداكلوبريد 20% SL',
    targetAr: 'المن الأخضر',
    scheduledDate: '2026-04-06',
    weatherSuitable: true,
    windSpeed: 10,
    temperature: 22,
    humidity: 50,
    phi: 21,
    costPerHectare: 180,
    areHectares: 3.8,
    status: 'scheduled',
  },
  {
    id: 's5',
    fieldName: 'بستان النخيل - القطاع ب',
    product: 'إيمامكتين بنزوات 5% SG',
    targetAr: 'سوسة النخيل الحمراء',
    scheduledDate: '2026-04-04',
    weatherSuitable: true,
    windSpeed: 6,
    temperature: 28,
    humidity: 45,
    phi: 14,
    costPerHectare: 850,
    areHectares: 4.0,
    status: 'scheduled',
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

type Severity = 'low' | 'medium' | 'high' | 'critical';

const SEVERITY_CONFIG: Record<Severity, { label: string; bg: string; text: string }> = {
  low: { label: 'منخفض', bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400' },
  medium: { label: 'متوسط', bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-400' },
  high: { label: 'مرتفع', bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-700 dark:text-orange-400' },
  critical: { label: 'حرج', bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400' },
};

const TREATMENT_STATUS_CONFIG: Record<string, { label: string; bg: string; text: string }> = {
  untreated: { label: 'لم يعالج', bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400' },
  in_progress: { label: 'قيد العلاج', bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400' },
  treated: { label: 'تم العلاج', bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400' },
  monitoring: { label: 'مراقبة', bg: 'bg-gray-100 dark:bg-gray-700/50', text: 'text-gray-700 dark:text-gray-400' },
};

const SPRAY_STATUS_CONFIG: Record<string, { label: string; bg: string; text: string }> = {
  scheduled: { label: 'مجدول', bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400' },
  completed: { label: 'مكتمل', bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400' },
  postponed: { label: 'مؤجل', bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-400' },
  cancelled: { label: 'ملغى', bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400' },
};

const TREND_CONFIG: Record<string, { label: string; icon: string; color: string }> = {
  increasing: { label: 'تصاعدي', icon: '↑', color: 'text-red-600' },
  stable: { label: 'مستقر', icon: '→', color: 'text-yellow-600' },
  decreasing: { label: 'تنازلي', icon: '↓', color: 'text-green-600' },
};

function SeverityBadge({ severity }: { severity: Severity }) {
  const config = SEVERITY_CONFIG[severity];
  return (
    <span className={cn('px-2.5 py-1 rounded-full text-xs font-semibold', config.bg, config.text)}>
      {config.label}
    </span>
  );
}

function StatusBadge({ status, configMap }: { status: string; configMap: Record<string, { label: string; bg: string; text: string }> }) {
  const config = configMap[status] ?? { label: status, bg: 'bg-gray-100', text: 'text-gray-700' };
  return (
    <span className={cn('px-2.5 py-1 rounded-full text-xs font-semibold', config.bg, config.text)}>
      {config.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------------

type TabKey = 'diseases' | 'pests' | 'spray';

const TABS: { key: TabKey; label: string; icon: typeof Bug }[] = [
  { key: 'diseases', label: 'الأمراض', icon: Bug },
  { key: 'pests', label: 'الآفات', icon: Target },
  { key: 'spray', label: 'برنامج الرش', icon: Spray },
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function DiseasesTab({ diseases }: { diseases: Disease[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700">
            <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">المرض</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">المحصول</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">الخطورة</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">الحقول المصابة</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">المساحة المصابة</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">آخر اكتشاف</th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">حالة العلاج</th>
          </tr>
        </thead>
        <tbody>
          {diseases.map((disease) => (
            <tr
              key={disease.id}
              className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <td className="py-3 px-4">
                <div>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">{disease.nameAr}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{disease.nameEn}</p>
                </div>
              </td>
              <td className="py-3 px-4">
                <span className="inline-flex items-center gap-1 text-gray-700 dark:text-gray-300">
                  <Leaf className="w-3.5 h-3.5" />
                  {disease.crop}
                </span>
              </td>
              <td className="py-3 px-4">
                <SeverityBadge severity={disease.severity} />
              </td>
              <td className="py-3 px-4 text-gray-700 dark:text-gray-300">
                <span className="inline-flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" />
                  {disease.affectedFields}
                </span>
              </td>
              <td className="py-3 px-4">
                <div className="flex items-center gap-2">
                  <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={cn(
                        'h-full rounded-full',
                        disease.affectedAreaPct >= 30 ? 'bg-red-500' : disease.affectedAreaPct >= 15 ? 'bg-orange-500' : 'bg-yellow-500'
                      )}
                      style={{ width: `${Math.min(disease.affectedAreaPct, 100)}%` }}
                    />
                  </div>
                  <span className="text-gray-700 dark:text-gray-300 text-xs">{disease.affectedAreaPct}%</span>
                </div>
              </td>
              <td className="py-3 px-4 text-gray-700 dark:text-gray-300">
                <span className="inline-flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {formatDate(disease.lastDetected)}
                </span>
              </td>
              <td className="py-3 px-4">
                <StatusBadge status={disease.treatmentStatus} configMap={TREATMENT_STATUS_CONFIG} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PestsTab({ pests }: { pests: Pest[] }) {
  return (
    <div className="space-y-4">
      {/* RPW Priority Alert */}
      {pests.some((p) => p.id === 'p1' && p.riskLevel === 'critical') && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-bold text-red-800 dark:text-red-300 text-base">
              تنبيه حرج: سوسة النخيل الحمراء (Red Palm Weevil)
            </h4>
            <p className="text-sm text-red-700 dark:text-red-400 mt-1">
              تم رصد اتجاه تصاعدي في أعداد سوسة النخيل. يجب اتخاذ إجراء فوري خلال 24-48 ساعة.
              التأخير قد يؤدي لخسارة الأشجار المصابة بالكامل.
            </p>
            <p className="text-xs text-red-600 dark:text-red-500 mt-2 font-medium">
              القيمة المعرضة للخطر: 45,000 ريال | تكلفة العلاج: 5,400 ريال | العائد: 733%
            </p>
          </div>
        </div>
      )}

      {/* Pests Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">الآفة</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">المحصول</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">مستوى الخطر</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">عتبة التدخل</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">الاتجاه</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">إجراء مطلوب</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">استراتيجية الإدارة المتكاملة</th>
            </tr>
          </thead>
          <tbody>
            {pests.map((pest) => {
              const trend = TREND_CONFIG[pest.populationTrend];
              return (
                <tr
                  key={pest.id}
                  className={cn(
                    'border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors',
                    pest.riskLevel === 'critical' && 'bg-red-50/50 dark:bg-red-900/10'
                  )}
                >
                  <td className="py-3 px-4">
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">{pest.nameAr}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{pest.nameEn}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-gray-700 dark:text-gray-300">
                      <Leaf className="w-3.5 h-3.5" />
                      {pest.crop}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <SeverityBadge severity={pest.riskLevel} />
                  </td>
                  <td className="py-3 px-4 text-gray-700 dark:text-gray-300 text-xs">
                    {pest.threshold}
                  </td>
                  <td className="py-3 px-4">
                    <span className={cn('inline-flex items-center gap-1 text-xs font-medium', trend?.color)}>
                      <span className="text-base">{trend?.icon}</span>
                      {trend?.label}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {pest.actionRequired ? (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-red-700 dark:text-red-400 bg-red-100 dark:bg-red-900/30 px-2 py-1 rounded-full">
                        <AlertTriangle className="w-3 h-3" />
                        مطلوب
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-green-700 dark:text-green-400 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded-full">
                        <CheckCircle className="w-3 h-3" />
                        مراقبة
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-xs text-gray-600 dark:text-gray-400 max-w-xs">
                    {pest.ipmStrategy}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SprayProgramTab({ schedules }: { schedules: SpraySchedule[] }) {
  const totalCost = schedules
    .filter((s) => s.status !== 'cancelled')
    .reduce((sum, s) => sum + s.costPerHectare * s.areHectares, 0);

  return (
    <div className="space-y-6">
      {/* Cost Summary */}
      <div className="bg-gradient-to-l from-sahool-50 to-sahool-100 dark:from-sahool-900/20 dark:to-sahool-800/20 border border-sahool-200 dark:border-sahool-800 rounded-xl p-4 flex items-center justify-between">
        <div>
          <p className="text-sm text-sahool-700 dark:text-sahool-400">إجمالي تكلفة الرش المتوقعة</p>
          <p className="text-2xl font-bold text-sahool-800 dark:text-sahool-200">
            {totalCost.toLocaleString('ar-YE')} ريال
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-sahool-600 dark:text-sahool-400">
          <Calendar className="w-4 h-4" />
          <span>{schedules.filter((s) => s.status === 'scheduled').length} عمليات مجدولة</span>
        </div>
      </div>

      {/* Schedule Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {schedules.map((spray) => (
          <div
            key={spray.id}
            className={cn(
              'bg-white dark:bg-gray-800 border rounded-xl p-5 transition-all hover:shadow-md',
              spray.weatherSuitable
                ? 'border-gray-200 dark:border-gray-700'
                : 'border-amber-300 dark:border-amber-700'
            )}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="font-bold text-gray-900 dark:text-gray-100">{spray.fieldName}</h4>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  الهدف: {spray.targetAr}
                </p>
              </div>
              <StatusBadge status={spray.status} configMap={SPRAY_STATUS_CONFIG} />
            </div>

            {/* Product */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 mb-3">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">المنتج</p>
              <p className="font-medium text-gray-800 dark:text-gray-200 text-sm">{spray.product}</p>
            </div>

            {/* Weather + Details Grid */}
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Calendar className="w-4 h-4 flex-shrink-0" />
                <span>{formatDate(spray.scheduledDate)}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Clock className="w-4 h-4 flex-shrink-0" />
                <span>PHI: {spray.phi} يوم</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Wind className="w-4 h-4 flex-shrink-0" />
                <span>{spray.windSpeed} كم/س</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Thermometer className="w-4 h-4 flex-shrink-0" />
                <span>{spray.temperature}&#176;م</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Droplets className="w-4 h-4 flex-shrink-0" />
                <span>رطوبة: {spray.humidity}%</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <MapPin className="w-4 h-4 flex-shrink-0" />
                <span>{spray.areHectares} هكتار</span>
              </div>
            </div>

            {/* Weather Suitability */}
            <div
              className={cn(
                'flex items-center gap-2 text-sm font-medium rounded-lg px-3 py-2',
                spray.weatherSuitable
                  ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400'
                  : 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400'
              )}
            >
              {spray.weatherSuitable ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>الطقس مناسب للرش</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-4 h-4" />
                  <span>الطقس غير مناسب — سرعة الرياح عالية</span>
                </>
              )}
            </div>

            {/* Cost */}
            <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between text-sm">
              <span className="text-gray-500 dark:text-gray-400">التكلفة المقدرة</span>
              <span className="font-bold text-gray-900 dark:text-gray-100">
                {(spray.costPerHectare * spray.areHectares).toLocaleString('ar-YE')} ريال
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function CropProtectionPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('diseases');

  // Compute KPIs
  const stats = useMemo(() => {
    const activeThreats = DISEASES.filter((d) => d.treatmentStatus === 'untreated' || d.treatmentStatus === 'in_progress').length
      + PESTS.filter((p) => p.actionRequired).length;
    const fieldsAtRisk = new Set(DISEASES.filter((d) => d.severity === 'high' || d.severity === 'critical').flatMap((d) => Array.from({ length: d.affectedFields }, (_, i) => `${d.id}-${i}`))).size;
    const sprayWindows = SPRAY_SCHEDULE.filter((s) => s.status === 'scheduled' && s.weatherSuitable).length;
    const lastScouting = PESTS.reduce((latest, p) => {
      const d = new Date(p.lastScouting);
      return d > latest ? d : latest;
    }, new Date(0));

    return { activeThreats, fieldsAtRisk, sprayWindows, lastScouting };
  }, []);

  return (
    <div className="p-6" dir="rtl">
      {/* Header */}
      <Header
        title="حماية المحاصيل — Crop Protection"
        subtitle="إدارة الأمراض والآفات وبرنامج الرش"
      />

      {/* Quick Actions */}
      <div className="mt-6 flex flex-wrap gap-3">
        <button className="inline-flex items-center gap-2 px-4 py-2.5 bg-sahool-600 text-white rounded-xl text-sm font-medium hover:bg-sahool-700 transition-colors shadow-sm">
          <Search className="w-4 h-4" />
          تشخيص
        </button>
        <button className="inline-flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-xl text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
          <Spray className="w-4 h-4" />
          رش
        </button>
        <button className="inline-flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-xl text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
          <ClipboardCheck className="w-4 h-4" />
          فحص
        </button>
        <button className="inline-flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-xl text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
          <FileText className="w-4 h-4" />
          تقرير
        </button>
      </div>

      {/* KPI Stats */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="التهديدات النشطة"
          value={stats.activeThreats}
          icon={AlertTriangle}
          iconColor="text-red-600"
          trend={{ value: 12, isPositive: false }}
        />
        <StatCard
          title="الحقول المعرضة للخطر"
          value={stats.fieldsAtRisk}
          icon={Shield}
          iconColor="text-orange-600"
          trend={{ value: 8, isPositive: false }}
        />
        <StatCard
          title="نوافذ الرش المتاحة"
          value={stats.sprayWindows}
          icon={Spray}
          iconColor="text-blue-600"
        />
        <StatCard
          title="آخر فحص ميداني"
          value={formatDate(stats.lastScouting)}
          icon={Calendar}
          iconColor="text-sahool-600"
        />
      </div>

      {/* Tabs */}
      <div className="mt-8">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex gap-1" aria-label="تبويبات حماية المحاصيل">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={cn(
                    'flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors',
                    isActive
                      ? 'border-sahool-600 text-sahool-700 dark:text-sahool-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  )}
                  aria-selected={isActive}
                  role="tab"
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
          {activeTab === 'diseases' && <DiseasesTab diseases={DISEASES} />}
          {activeTab === 'pests' && <PestsTab pests={PESTS} />}
          {activeTab === 'spray' && <SprayProgramTab schedules={SPRAY_SCHEDULE} />}
        </div>
      </div>
    </div>
  );
}
