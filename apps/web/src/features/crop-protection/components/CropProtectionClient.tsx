'use client';

/**
 * Crop Protection Client Component
 * مكون حماية المحاصيل — الأمراض والآفات وبرنامج الرش
 */

import React, { useState, useMemo } from 'react';
import {
  Bug,
  Shield,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Wind,
  Thermometer,
  Droplets,
  Clock,
  MapPin,
  Leaf,
  Target,
  TrendingUp,
  TrendingDown,
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
  phi: number;
  costPerHectare: number;
  areaHectares: number;
  status: 'scheduled' | 'completed' | 'postponed' | 'cancelled';
}

// ---------------------------------------------------------------------------
// Mock Data
// ---------------------------------------------------------------------------

const DISEASES: Disease[] = [
  { id: 'd1', nameAr: 'صدأ الأوراق', nameEn: 'Leaf Rust', crop: 'قمح', severity: 'high', affectedFields: 4, lastDetected: '2026-04-02', treatmentStatus: 'in_progress', affectedAreaPct: 15 },
  { id: 'd2', nameAr: 'اللفحة المتأخرة', nameEn: 'Late Blight', crop: 'طماطم', severity: 'critical', affectedFields: 2, lastDetected: '2026-04-03', treatmentStatus: 'untreated', affectedAreaPct: 25 },
  { id: 'd3', nameAr: 'البياض الدقيقي', nameEn: 'Powdery Mildew', crop: 'خيار', severity: 'medium', affectedFields: 3, lastDetected: '2026-03-30', treatmentStatus: 'treated', affectedAreaPct: 8 },
  { id: 'd4', nameAr: 'تبقع الأوراق', nameEn: 'Leaf Spot', crop: 'ذرة', severity: 'low', affectedFields: 1, lastDetected: '2026-03-28', treatmentStatus: 'monitoring', affectedAreaPct: 3 },
  { id: 'd5', nameAr: 'الفيوزاريوم', nameEn: 'Fusarium Wilt', crop: 'قمح', severity: 'high', affectedFields: 2, lastDetected: '2026-04-01', treatmentStatus: 'in_progress', affectedAreaPct: 12 },
];

const PESTS: Pest[] = [
  { id: 'p1', nameAr: 'حشرة المن', nameEn: 'Aphid', crop: 'قمح', riskLevel: 'high', threshold: '25 حشرة/نبتة', actionRequired: true, ipmStrategy: 'مكافحة بيولوجية + كيميائية', lastScouting: '2026-04-02', populationTrend: 'increasing' },
  { id: 'p2', nameAr: 'الذبابة البيضاء', nameEn: 'Whitefly', crop: 'طماطم', riskLevel: 'medium', threshold: '10 حشرات/ورقة', actionRequired: false, ipmStrategy: 'مصائد لاصقة + أعداء طبيعية', lastScouting: '2026-04-01', populationTrend: 'stable' },
  { id: 'p3', nameAr: 'دودة الحشد الخريفية', nameEn: 'Fall Armyworm', crop: 'ذرة', riskLevel: 'critical', threshold: '3 يرقات/نبتة', actionRequired: true, ipmStrategy: 'رش طوارئ + مراقبة مكثفة', lastScouting: '2026-04-03', populationTrend: 'increasing' },
  { id: 'p4', nameAr: 'سوسة النخيل الحمراء', nameEn: 'Red Palm Weevil', crop: 'نخيل', riskLevel: 'critical', threshold: 'اكتشاف واحد', actionRequired: true, ipmStrategy: 'حقن + مصائد فرمونية', lastScouting: '2026-03-31', populationTrend: 'stable' },
  { id: 'p5', nameAr: 'خنفساء الحبوب', nameEn: 'Grain Beetle', crop: 'شعير', riskLevel: 'low', threshold: '5 حشرات/كجم', actionRequired: false, ipmStrategy: 'تهوية المخزن + نظافة', lastScouting: '2026-03-29', populationTrend: 'decreasing' },
];

const SPRAY_SCHEDULE: SpraySchedule[] = [
  { id: 'sp1', fieldName: 'حقل القمح الشمالي', product: 'بروبيكونازول 25%', targetAr: 'صدأ الأوراق', scheduledDate: '2026-04-05', weatherSuitable: true, windSpeed: 8, temperature: 24, humidity: 55, phi: 30, costPerHectare: 120, areaHectares: 5.2, status: 'scheduled' },
  { id: 'sp2', fieldName: 'حقل الطماطم', product: 'مانكوزيب 80%', targetAr: 'اللفحة المتأخرة', scheduledDate: '2026-04-04', weatherSuitable: false, windSpeed: 22, temperature: 28, humidity: 70, phi: 14, costPerHectare: 85, areaHectares: 3.0, status: 'postponed' },
  { id: 'sp3', fieldName: 'حقل الذرة', product: 'إيمامكتين بنزوات 5%', targetAr: 'دودة الحشد', scheduledDate: '2026-04-04', weatherSuitable: true, windSpeed: 6, temperature: 26, humidity: 45, phi: 7, costPerHectare: 150, areaHectares: 6.7, status: 'scheduled' },
  { id: 'sp4', fieldName: 'بستان النخيل', product: 'إيمامكتين بنزوات 5%', targetAr: 'سوسة النخيل', scheduledDate: '2026-04-03', weatherSuitable: true, windSpeed: 10, temperature: 30, humidity: 40, phi: 21, costPerHectare: 200, areaHectares: 8.5, status: 'completed' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const TABS = [
  { id: 'diseases', label: 'الأمراض', icon: Leaf },
  { id: 'pests', label: 'الآفات', icon: Bug },
  { id: 'spray', label: 'برنامج الرش', icon: Calendar },
] as const;

type TabId = (typeof TABS)[number]['id'];

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700',
};

const SEVERITY_LABELS: Record<string, string> = {
  critical: 'حرج',
  high: 'مرتفع',
  medium: 'متوسط',
  low: 'منخفض',
};

const TREATMENT_LABELS: Record<string, string> = {
  untreated: 'غير معالج',
  in_progress: 'قيد العلاج',
  treated: 'تم العلاج',
  monitoring: 'مراقبة',
};

const TREATMENT_STYLES: Record<string, string> = {
  untreated: 'bg-red-100 text-red-700',
  in_progress: 'bg-blue-100 text-blue-700',
  treated: 'bg-green-100 text-green-700',
  monitoring: 'bg-purple-100 text-purple-700',
};

const SPRAY_STATUS_LABELS: Record<string, string> = {
  scheduled: 'مجدول',
  completed: 'مكتمل',
  postponed: 'مؤجل',
  cancelled: 'ملغي',
};

const SPRAY_STATUS_STYLES: Record<string, string> = {
  scheduled: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  postponed: 'bg-yellow-100 text-yellow-700',
  cancelled: 'bg-red-100 text-red-700',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CropProtectionClient() {
  const [activeTab, setActiveTab] = useState<TabId>('diseases');
  const [_searchQuery, _setSearchQuery] = useState('');

  const stats = useMemo(() => ({
    totalDiseases: DISEASES.length,
    criticalDiseases: DISEASES.filter((d) => d.severity === 'critical').length,
    totalPests: PESTS.length,
    actionRequired: PESTS.filter((p) => p.actionRequired).length,
    scheduledSprays: SPRAY_SCHEDULE.filter((s) => s.status === 'scheduled').length,
    completedSprays: SPRAY_SCHEDULE.filter((s) => s.status === 'completed').length,
  }), []);

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">حماية المحاصيل</h1>
        <p className="text-sm text-gray-500 mt-1">
          إدارة الأمراض والآفات وبرنامج الرش الوقائي والعلاجي
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <Leaf className="w-5 h-5 text-red-500" />
            <span className="text-sm text-gray-500">أمراض نشطة</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalDiseases}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="text-sm text-gray-500">حرجة</span>
          </div>
          <p className="text-2xl font-bold text-red-600 mt-1">{stats.criticalDiseases}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <Bug className="w-5 h-5 text-orange-500" />
            <span className="text-sm text-gray-500">آفات مرصودة</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalPests}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-red-500" />
            <span className="text-sm text-gray-500">تتطلب إجراء</span>
          </div>
          <p className="text-2xl font-bold text-orange-600 mt-1">{stats.actionRequired}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-500" />
            <span className="text-sm text-gray-500">رش مجدول</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.scheduledSprays}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="text-sm text-gray-500">رش مكتمل</span>
          </div>
          <p className="text-2xl font-bold text-green-600 mt-1">{stats.completedSprays}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-green-700 shadow-sm font-medium'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Diseases Tab */}
      {activeTab === 'diseases' && (
        <div className="space-y-3">
          {DISEASES.map((disease) => (
            <div key={disease.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    disease.severity === 'critical' ? 'bg-red-100' : disease.severity === 'high' ? 'bg-orange-100' : 'bg-yellow-100'
                  }`}>
                    <Leaf className={`w-6 h-6 ${
                      disease.severity === 'critical' ? 'text-red-600' : disease.severity === 'high' ? 'text-orange-600' : 'text-yellow-600'
                    }`} />
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">{disease.nameAr}</p>
                    <p className="text-sm text-gray-500">{disease.nameEn} - {disease.crop}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-left text-sm">
                    <p className="text-gray-500">{disease.affectedFields} حقول متأثرة</p>
                    <p className="text-gray-500">{disease.affectedAreaPct}% مساحة مصابة</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${SEVERITY_STYLES[disease.severity]}`}>
                    {SEVERITY_LABELS[disease.severity]}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${TREATMENT_STYLES[disease.treatmentStatus]}`}>
                    {TREATMENT_LABELS[disease.treatmentStatus]}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pests Tab */}
      {activeTab === 'pests' && (
        <div className="space-y-3">
          {PESTS.map((pest) => (
            <div key={pest.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    pest.riskLevel === 'critical' ? 'bg-red-100' : pest.riskLevel === 'high' ? 'bg-orange-100' : 'bg-yellow-100'
                  }`}>
                    <Bug className={`w-6 h-6 ${
                      pest.riskLevel === 'critical' ? 'text-red-600' : pest.riskLevel === 'high' ? 'text-orange-600' : 'text-yellow-600'
                    }`} />
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">{pest.nameAr}</p>
                    <p className="text-sm text-gray-500">{pest.nameEn} - {pest.crop}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1 text-sm">
                    {pest.populationTrend === 'increasing' ? (
                      <TrendingUp className="w-4 h-4 text-red-500" />
                    ) : pest.populationTrend === 'decreasing' ? (
                      <TrendingDown className="w-4 h-4 text-green-500" />
                    ) : (
                      <span className="w-4 h-4 text-gray-400">--</span>
                    )}
                    <span className={
                      pest.populationTrend === 'increasing' ? 'text-red-600' :
                      pest.populationTrend === 'decreasing' ? 'text-green-600' : 'text-gray-500'
                    }>
                      {pest.populationTrend === 'increasing' ? 'متزايد' :
                       pest.populationTrend === 'decreasing' ? 'متناقص' : 'مستقر'}
                    </span>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${SEVERITY_STYLES[pest.riskLevel]}`}>
                    {SEVERITY_LABELS[pest.riskLevel]}
                  </span>
                  {pest.actionRequired && (
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                      يتطلب إجراء
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-6 text-sm text-gray-500 border-t pt-3">
                <span>العتبة: {pest.threshold}</span>
                <span>الاستراتيجية: {pest.ipmStrategy}</span>
                <span>آخر فحص: {pest.lastScouting}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Spray Schedule Tab */}
      {activeTab === 'spray' && (
        <div className="space-y-3">
          {SPRAY_SCHEDULE.map((spray) => (
            <div key={spray.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="font-bold text-gray-900">{spray.fieldName}</p>
                  <p className="text-sm text-gray-500">{spray.product} - {spray.targetAr}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-600">{spray.scheduledDate}</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${SPRAY_STATUS_STYLES[spray.status]}`}>
                    {SPRAY_STATUS_LABELS[spray.status]}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-6 text-sm border-t pt-3">
                <div className="flex items-center gap-1">
                  {spray.weatherSuitable ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-red-500" />
                  )}
                  <span className={spray.weatherSuitable ? 'text-green-600' : 'text-red-600'}>
                    {spray.weatherSuitable ? 'طقس مناسب' : 'طقس غير مناسب'}
                  </span>
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                  <Wind className="w-4 h-4" />
                  <span>{spray.windSpeed} كم/س</span>
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                  <Thermometer className="w-4 h-4" />
                  <span>{spray.temperature} درجة</span>
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                  <Droplets className="w-4 h-4" />
                  <span>{spray.humidity}%</span>
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                  <Clock className="w-4 h-4" />
                  <span>PHI: {spray.phi} يوم</span>
                </div>
                <div className="text-gray-500">
                  التكلفة: {(spray.costPerHectare * spray.areaHectares).toLocaleString('ar-SA')} ريال
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
