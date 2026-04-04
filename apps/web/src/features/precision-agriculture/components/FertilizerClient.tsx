'use client';

import React, { useState, useMemo } from 'react';
import {
  Search,
  Beaker,
  Leaf,
  Calculator,
  Calendar,
  AlertTriangle,
  TrendingUp,
  Droplets,
  Package,
  CheckCircle,
  Clock,
  Target,
} from 'lucide-react';

type NutrientType = 'nitrogen' | 'phosphorus' | 'potassium' | 'micronutrient';
type ApplicationMethod = 'broadcast' | 'fertigation' | 'foliar' | 'band';
type ApplicationStatus = 'scheduled' | 'applied' | 'overdue' | 'skipped';

interface FertilizerPlan {
  id: string;
  fieldName: string;
  fieldNameAr: string;
  crop: string;
  cropAr: string;
  growthStage: string;
  growthStageAr: string;
  product: string;
  productAr: string;
  nutrientType: NutrientType;
  ratePerHa: number;
  unit: string;
  method: ApplicationMethod;
  status: ApplicationStatus;
  scheduledDate: string;
  appliedDate: string | null;
  costPerHa: number;
  soilTestN: number;
  soilTestP: number;
  soilTestK: number;
  targetYield: number;
}

const mockPlans: FertilizerPlan[] = [
  {
    id: 'fert-001',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    crop: 'Wheat',
    cropAr: 'القمح',
    growthStage: 'Tillering',
    growthStageAr: 'التفريع',
    product: 'Urea 46%',
    productAr: 'يوريا 46%',
    nutrientType: 'nitrogen',
    ratePerHa: 46,
    unit: 'كجم/هـ',
    method: 'broadcast',
    status: 'scheduled',
    scheduledDate: '2026-04-06',
    appliedDate: null,
    costPerHa: 115,
    soilTestN: 18,
    soilTestP: 28,
    soilTestK: 155,
    targetYield: 6.5,
  },
  {
    id: 'fert-002',
    fieldName: 'Wheat Field',
    fieldNameAr: 'حقل القمح',
    crop: 'Wheat',
    cropAr: 'القمح',
    growthStage: 'Booting',
    growthStageAr: 'التبويب',
    product: 'DAP 18-46',
    productAr: 'داب 18-46',
    nutrientType: 'phosphorus',
    ratePerHa: 100,
    unit: 'كجم/هـ',
    method: 'band',
    status: 'applied',
    scheduledDate: '2026-03-28',
    appliedDate: '2026-03-28',
    costPerHa: 280,
    soilTestN: 22,
    soilTestP: 12,
    soilTestK: 140,
    targetYield: 5.8,
  },
  {
    id: 'fert-003',
    fieldName: 'Greenhouse',
    fieldNameAr: 'الصوب الزراعية',
    crop: 'Tomato',
    cropAr: 'الطماطم',
    growthStage: 'Fruiting',
    growthStageAr: 'الإثمار',
    product: 'KNO3',
    productAr: 'نترات البوتاسيوم',
    nutrientType: 'potassium',
    ratePerHa: 35,
    unit: 'كجم/هـ',
    method: 'fertigation',
    status: 'overdue',
    scheduledDate: '2026-04-02',
    appliedDate: null,
    costPerHa: 195,
    soilTestN: 30,
    soilTestP: 22,
    soilTestK: 85,
    targetYield: 80,
  },
  {
    id: 'fert-004',
    fieldName: 'Palm Grove',
    fieldNameAr: 'بستان النخيل',
    crop: 'Date Palm',
    cropAr: 'نخيل التمر',
    growthStage: 'Fruit Development',
    growthStageAr: 'تطور الثمار',
    product: 'Iron Chelate',
    productAr: 'حديد مخلبي',
    nutrientType: 'micronutrient',
    ratePerHa: 5,
    unit: 'كجم/هـ',
    method: 'foliar',
    status: 'applied',
    scheduledDate: '2026-03-30',
    appliedDate: '2026-03-31',
    costPerHa: 320,
    soilTestN: 25,
    soilTestP: 18,
    soilTestK: 200,
    targetYield: 120,
  },
  {
    id: 'fert-005',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    crop: 'Barley',
    cropAr: 'الشعير',
    growthStage: 'Heading',
    growthStageAr: 'الإسبال',
    product: 'Ammonium Sulfate',
    productAr: 'سلفات الأمونيوم',
    nutrientType: 'nitrogen',
    ratePerHa: 55,
    unit: 'كجم/هـ',
    method: 'broadcast',
    status: 'skipped',
    scheduledDate: '2026-04-01',
    appliedDate: null,
    costPerHa: 98,
    soilTestN: 32,
    soilTestP: 20,
    soilTestK: 160,
    targetYield: 4.5,
  },
  {
    id: 'fert-006',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    crop: 'Wheat',
    cropAr: 'القمح',
    growthStage: 'Heading',
    growthStageAr: 'الإسبال',
    product: 'Zinc Sulfate',
    productAr: 'كبريتات الزنك',
    nutrientType: 'micronutrient',
    ratePerHa: 8,
    unit: 'كجم/هـ',
    method: 'foliar',
    status: 'scheduled',
    scheduledDate: '2026-04-10',
    appliedDate: null,
    costPerHa: 45,
    soilTestN: 18,
    soilTestP: 28,
    soilTestK: 155,
    targetYield: 6.5,
  },
];

const nutrientLabels: Record<NutrientType, { label: string; color: string }> = {
  nitrogen: { label: 'نيتروجين (N)', color: 'bg-blue-100 text-blue-800' },
  phosphorus: { label: 'فوسفور (P)', color: 'bg-orange-100 text-orange-800' },
  potassium: { label: 'بوتاسيوم (K)', color: 'bg-purple-100 text-purple-800' },
  micronutrient: { label: 'عنصر صغرى', color: 'bg-teal-100 text-teal-800' },
};

const methodLabels: Record<ApplicationMethod, string> = {
  broadcast: 'نثر',
  fertigation: 'تسميد بالري',
  foliar: 'رش ورقي',
  band: 'سطور',
};

export default function FertilizerClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | 'all'>('all');
  const [nutrientFilter, setNutrientFilter] = useState<NutrientType | 'all'>('all');

  const filteredPlans = useMemo(() => {
    return mockPlans.filter((plan) => {
      const matchesSearch =
        !searchTerm ||
        plan.fieldNameAr.includes(searchTerm) ||
        plan.productAr.includes(searchTerm) ||
        plan.cropAr.includes(searchTerm);
      const matchesStatus = statusFilter === 'all' || plan.status === statusFilter;
      const matchesNutrient = nutrientFilter === 'all' || plan.nutrientType === nutrientFilter;
      return matchesSearch && matchesStatus && matchesNutrient;
    });
  }, [searchTerm, statusFilter, nutrientFilter]);

  const getStatusBadge = (status: ApplicationStatus) => {
    const styles: Record<ApplicationStatus, string> = {
      scheduled: 'bg-blue-100 text-blue-800',
      applied: 'bg-green-100 text-green-800',
      overdue: 'bg-red-100 text-red-800',
      skipped: 'bg-gray-100 text-gray-800',
    };
    const labels: Record<ApplicationStatus, string> = {
      scheduled: 'مجدول',
      applied: 'مطبق',
      overdue: 'متأخر',
      skipped: 'تم تخطيه',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const getStatusIcon = (status: ApplicationStatus) => {
    if (status === 'applied') return <CheckCircle className="w-4 h-4 text-green-500" />;
    if (status === 'overdue') return <AlertTriangle className="w-4 h-4 text-red-500" />;
    if (status === 'scheduled') return <Clock className="w-4 h-4 text-blue-500" />;
    return <Target className="w-4 h-4 text-gray-400" />;
  };

  const getNutrientBar = (n: number, p: number, k: number) => {
    const nThreshold = 25, pThreshold = 20, kThreshold = 150;
    return (
      <div className="flex gap-2 text-xs">
        <span className={`px-1.5 py-0.5 rounded ${n < nThreshold ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
          N:{n}
        </span>
        <span className={`px-1.5 py-0.5 rounded ${p < pThreshold ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
          P:{p}
        </span>
        <span className={`px-1.5 py-0.5 rounded ${k < kThreshold ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
          K:{k}
        </span>
      </div>
    );
  };

  const overdueCount = mockPlans.filter((p) => p.status === 'overdue').length;
  const appliedCount = mockPlans.filter((p) => p.status === 'applied').length;
  const totalCost = mockPlans.filter((p) => p.status === 'applied').reduce((s, p) => s + p.costPerHa, 0);

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة الأسمدة</h1>
          <p className="text-gray-500 mt-1">Fertilizer Management</p>
        </div>
        <button
          disabled
          title="قريبا - Coming soon"
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Calculator className="w-4 h-4" />
          حاسبة العناصر
        </button>
      </div>

      {/* Overdue alert */}
      {overdueCount > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-medium text-red-800">
              {overdueCount} تطبيق سماد متأخر عن الموعد المحدد
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Beaker className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الخطط</div>
              <div className="text-xl font-bold text-gray-900">{mockPlans.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تم التطبيق</div>
              <div className="text-xl font-bold text-blue-600">{appliedCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متأخر</div>
              <div className="text-xl font-bold text-red-600">{overdueCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي التكلفة</div>
              <div className="text-xl font-bold text-purple-600">{totalCost} ريال/هـ</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث بالحقل أو المنتج أو المحصول..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ApplicationStatus | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع الحالات</option>
          <option value="scheduled">مجدول</option>
          <option value="applied">مطبق</option>
          <option value="overdue">متأخر</option>
          <option value="skipped">تم تخطيه</option>
        </select>
        <select
          value={nutrientFilter}
          onChange={(e) => setNutrientFilter(e.target.value as NutrientType | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع العناصر</option>
          <option value="nitrogen">نيتروجين</option>
          <option value="phosphorus">فوسفور</option>
          <option value="potassium">بوتاسيوم</option>
          <option value="micronutrient">عناصر صغرى</option>
        </select>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredPlans.map((plan) => (
          <div
            key={plan.id}
            className={`bg-white rounded-lg border p-5 hover:shadow-md transition-shadow ${
              plan.status === 'overdue' ? 'border-red-300' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-medium text-gray-900">{plan.productAr}</h3>
                <p className="text-sm text-gray-500">{plan.fieldNameAr} - {plan.cropAr}</p>
              </div>
              <div className="flex items-center gap-1">
                {getStatusIcon(plan.status)}
                {getStatusBadge(plan.status)}
              </div>
            </div>

            <div className="mb-3">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${nutrientLabels[plan.nutrientType].color}`}>
                {nutrientLabels[plan.nutrientType].label}
              </span>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Leaf className="w-4 h-4" />
                  <span>مرحلة النمو</span>
                </div>
                <span className="font-medium">{plan.growthStageAr}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Package className="w-4 h-4" />
                  <span>المعدل</span>
                </div>
                <span className="font-medium">{plan.ratePerHa} {plan.unit}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Droplets className="w-4 h-4" />
                  <span>طريقة التطبيق</span>
                </div>
                <span className="font-medium">{methodLabels[plan.method]}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500">تحليل التربة</span>
                {getNutrientBar(plan.soilTestN, plan.soilTestP, plan.soilTestK)}
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Target className="w-4 h-4" />
                  <span>الإنتاجية المستهدفة</span>
                </div>
                <span className="font-medium">{plan.targetYield} طن/هـ</span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t flex justify-between items-center">
              <div className="flex items-center gap-1 text-xs text-gray-400">
                <Calendar className="w-3 h-3" />
                <span>{new Date(plan.scheduledDate).toLocaleDateString('ar-SA')}</span>
              </div>
              <span className="font-bold text-green-700">{plan.costPerHa} ريال/هـ</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
