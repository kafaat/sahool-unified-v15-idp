'use client';

// Smart Irrigation Dashboard - الري الذكي
// AI-powered irrigation scheduling and water conservation

import { useEffect, useState } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import DataTable from '@/components/ui/DataTable';
import { API_URLS, apiClient } from '@/lib/api';
import { API_PATHS } from '@/config/api';
import { cn } from '@/lib/utils';
import { logger } from '@/lib/logger';
import {
  Droplets,
  Calendar,
  Clock,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Leaf,
  BarChart3,
  Gauge,
  CloudRain,
} from 'lucide-react';

// Types
interface IrrigationSchedule {
  schedule_id: string;
  field_id: string;
  crop: string;
  crop_name_ar: string;
  irrigation_date: string;
  start_time: string;
  duration_minutes: number;
  water_amount_liters: number;
  water_amount_m3: number;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  urgency_ar: string;
  method: string;
  method_ar: string;
  reasoning_ar: string;
  weather_adjusted: boolean;
  savings_percent: number;
}

interface IrrigationPlan {
  plan_id: string;
  field_id: string;
  crop: string;
  crop_name_ar: string;
  growth_stage: string;
  growth_stage_ar: string;
  area_hectares: number;
  current_water_need_mm: number;
  daily_et_mm: number;
  schedules: IrrigationSchedule[];
  total_water_m3: number;
  estimated_cost_yer: number;
  water_savings_m3: number;
  recommendations_ar: string[];
  alerts_ar: string[];
}

interface WaterBalance {
  field_id: string;
  date: string;
  et_mm: number;
  rainfall_mm: number;
  irrigation_mm: number;
  water_deficit_mm: number;
  cumulative_deficit_mm: number;
}

interface IrrigationMethod {
  id: string;
  name_ar: string;
  efficiency_percent: number;
}

interface CropInfo {
  id: string;
  name_ar: string;
  water_requirements_mm_day: Record<string, number>;
}

const URGENCY_COLORS = {
  low: 'bg-green-100 text-green-700 border-green-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  high: 'bg-orange-100 text-orange-700 border-orange-200',
  critical: 'bg-red-100 text-red-700 border-red-200',
};

const URGENCY_ICONS = {
  low: CheckCircle,
  medium: Clock,
  high: AlertTriangle,
  critical: AlertTriangle,
};

// Deterministic helpers for mock data (no Math.random() — avoids security warnings)
function deterministicValue(index: number, min: number, max: number): number {
  const normalized = ((index * 7 + 13) % 100) / 100;
  return min + normalized * (max - min);
}

function selectByIndex<T>(arr: readonly T[], index: number): T {
  return arr[index % arr.length]!;
}

// Mock data generators
function generateMockPlan(): IrrigationPlan {
  const crops = [
    { id: 'tomato', ar: 'طماطم' },
    { id: 'wheat', ar: 'قمح' },
    { id: 'coffee', ar: 'بن' },
    { id: 'banana', ar: 'موز' },
    { id: 'date_palm', ar: 'نخيل' },
  ] as const;
  const stages = [
    { id: 'seedling', ar: 'شتلة' },
    { id: 'vegetative', ar: 'نمو خضري' },
    { id: 'flowering', ar: 'إزهار' },
    { id: 'fruiting', ar: 'إثمار' },
  ] as const;
  const urgencies: Array<'low' | 'medium' | 'high' | 'critical'> = [
    'low',
    'medium',
    'high',
    'critical',
  ];
  const methods = [
    { id: 'drip', ar: 'ري بالتنقيط' },
    { id: 'sprinkler', ar: 'ري رشاش' },
    { id: 'flood', ar: 'ري غمر' },
  ] as const;

  const selectedCrop = selectByIndex(crops, 1);
  const selectedStage = selectByIndex(stages, 2);
  const selectedMethod = selectByIndex(methods, 0);
  const urgency = selectByIndex(urgencies, 2);

  const schedules: IrrigationSchedule[] = Array.from({ length: 3 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() + i);
    return {
      schedule_id: `sch-${i + 1}`,
      field_id: 'field-1',
      crop: selectedCrop.id,
      crop_name_ar: selectedCrop.ar,
      irrigation_date: date.toISOString().split('T')[0] ?? '',
      start_time: '06:00',
      duration_minutes: 45 + Math.floor(deterministicValue(i, 0, 30)),
      water_amount_liters: 5000 + Math.floor(deterministicValue(i + 3, 0, 3000)),
      water_amount_m3: 5 + deterministicValue(i + 5, 0, 3),
      urgency,
      urgency_ar:
        urgency === 'critical'
          ? 'حرج'
          : urgency === 'high'
            ? 'عالي'
            : urgency === 'medium'
              ? 'متوسط'
              : 'منخفض',
      method: selectedMethod.id,
      method_ar: selectedMethod.ar,
      reasoning_ar: `${selectedCrop.ar} في مرحلة ${selectedStage.ar} يحتاج ري منتظم`,
      weather_adjusted: i % 2 === 0,
      savings_percent: deterministicValue(i + 7, 0, 30),
    };
  });

  return {
    plan_id: 'plan-1',
    field_id: 'field-1',
    crop: selectedCrop.id,
    crop_name_ar: selectedCrop.ar,
    growth_stage: selectedStage.id,
    growth_stage_ar: selectedStage.ar,
    area_hectares: 2.5,
    current_water_need_mm: 15 + deterministicValue(0, 0, 10),
    daily_et_mm: 5 + deterministicValue(1, 0, 3),
    schedules,
    total_water_m3: 15 + deterministicValue(2, 0, 10),
    estimated_cost_yer: 2500 + Math.floor(deterministicValue(3, 0, 1500)),
    water_savings_m3: deterministicValue(4, 0, 5),
    recommendations_ar: [
      '💧 كفاءة الري الحالية: 85%',
      '🌡️ ري في الصباح الباكر فقط لتقليل التبخر',
      '💡 التحويل للري بالتنقيط يوفر حتى 45% من المياه',
    ],
    alerts_ar: urgency === 'critical' ? ['🚨 المحصول يحتاج ري عاجل!'] : [],
  };
}

function generateMockWaterBalance(): {
  summary: Record<string, number>;
  daily_data: WaterBalance[];
} {
  const dailyData: WaterBalance[] = Array.from({ length: 14 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (14 - i - 1));
    return {
      field_id: 'field-1',
      date: date.toISOString().split('T')[0] ?? '',
      et_mm: 4 + deterministicValue(i, 0, 4),
      rainfall_mm: i % 7 === 0 ? deterministicValue(i, 0, 15) : 0,
      irrigation_mm: i % 3 === 0 ? deterministicValue(i + 2, 0, 30) : 0,
      water_deficit_mm: deterministicValue(i + 4, 0, 3),
      cumulative_deficit_mm: deterministicValue(i + 6, 0, 20),
    };
  });

  return {
    summary: {
      total_et_mm: dailyData.reduce((acc, d) => acc + d.et_mm, 0),
      total_rainfall_mm: dailyData.reduce((acc, d) => acc + d.rainfall_mm, 0),
      total_irrigation_mm: dailyData.reduce((acc, d) => acc + d.irrigation_mm, 0),
      cumulative_deficit_mm: dailyData[dailyData.length - 1]?.cumulative_deficit_mm ?? 0,
    },
    daily_data: dailyData,
  };
}

function generateMockMethods(): IrrigationMethod[] {
  return [
    { id: 'drip', name_ar: 'ري بالتنقيط', efficiency_percent: 90 },
    { id: 'sprinkler', name_ar: 'ري رشاش', efficiency_percent: 75 },
    { id: 'furrow', name_ar: 'ري أخدود', efficiency_percent: 60 },
    { id: 'flood', name_ar: 'ري غمر', efficiency_percent: 50 },
    { id: 'traditional', name_ar: 'ري تقليدي', efficiency_percent: 45 },
  ];
}

function generateMockCrops(): CropInfo[] {
  return [
    {
      id: 'tomato',
      name_ar: 'طماطم',
      water_requirements_mm_day: {
        seedling: 2.5,
        vegetative: 4.5,
        flowering: 6.0,
      },
    },
    {
      id: 'wheat',
      name_ar: 'قمح',
      water_requirements_mm_day: {
        seedling: 2.0,
        vegetative: 4.0,
        flowering: 5.5,
      },
    },
    {
      id: 'coffee',
      name_ar: 'بن',
      water_requirements_mm_day: {
        seedling: 3.0,
        vegetative: 4.0,
        flowering: 5.0,
      },
    },
    {
      id: 'banana',
      name_ar: 'موز',
      water_requirements_mm_day: {
        seedling: 4.0,
        vegetative: 6.0,
        flowering: 7.0,
      },
    },
    {
      id: 'date_palm',
      name_ar: 'نخيل',
      water_requirements_mm_day: {
        seedling: 5.0,
        vegetative: 8.0,
        flowering: 10.0,
      },
    },
  ];
}

export default function IrrigationPage() {
  const [plan, setPlan] = useState<IrrigationPlan | null>(null);
  const [waterBalance, setWaterBalance] = useState<{
    summary: Record<string, number>;
    daily_data: WaterBalance[];
  } | null>(null);
  const [methods, setMethods] = useState<IrrigationMethod[]>([]);
  const [crops, setCrops] = useState<CropInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<'schedule' | 'balance' | 'efficiency'>('schedule');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setIsLoading(true);
    try {
      // Try to fetch from API
      const [planRes, balanceRes, methodsRes, cropsRes] = await Promise.all([
        apiClient
          .post(`${API_URLS.irrigation}${API_PATHS.irrigation.calculate}`, {
            field_id: 'field-1',
            crop: 'tomato',
            growth_stage: 'vegetative',
            area_hectares: 2.5,
            soil_type: 'loamy',
            irrigation_method: 'drip',
          })
          .catch((err) => {
            logger.error('Failed to fetch irrigation plan:', err);
            return null;
          }),
        apiClient.get(`${API_URLS.irrigation}${API_PATHS.irrigation.waterBalance('field-1')}`).catch((err) => {
          logger.error('Failed to fetch water balance:', err);
          return null;
        }),
        apiClient.get(`${API_URLS.irrigation}${API_PATHS.irrigation.methods}`).catch((err) => {
          logger.error('Failed to fetch irrigation methods:', err);
          return null;
        }),
        apiClient.get(`${API_URLS.irrigation}${API_PATHS.irrigation.crops}`).catch((err) => {
          logger.error('Failed to fetch crops:', err);
          return null;
        }),
      ]);

      setPlan(planRes?.data || generateMockPlan());
      setWaterBalance(balanceRes?.data || generateMockWaterBalance());
      setMethods(methodsRes?.data?.methods || generateMockMethods());
      setCrops(cropsRes?.data?.crops || generateMockCrops());
    } catch {
      // Use mock data
      setPlan(generateMockPlan());
      setWaterBalance(generateMockWaterBalance());
      setMethods(generateMockMethods());
      setCrops(generateMockCrops());
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="p-6">
      <Header title="الري الذكي" subtitle="جدولة الري وتوفير المياه بالذكاء الاصطناعي" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="إجمالي المياه"
          value={plan?.total_water_m3.toFixed(1) || '0'}
          suffix="م³"
          icon={Droplets}
          iconColor="text-blue-600"
        />

        <StatCard
          title="وفر المياه"
          value={plan?.water_savings_m3.toFixed(1) || '0'}
          suffix="م³"
          icon={TrendingDown}
          iconColor="text-green-600"
        />

        <StatCard
          title="التبخر اليومي"
          value={plan?.daily_et_mm.toFixed(1) || '0'}
          suffix="ملم"
          icon={BarChart3}
          iconColor="text-amber-600"
        />

        <StatCard
          title="التكلفة المتوقعة"
          value={plan?.estimated_cost_yer.toLocaleString() || '0'}
          suffix="ر.ي"
          icon={Gauge}
          iconColor="text-purple-600"
        />
      </div>

      {/* Tabs */}
      <div className="mt-6 flex gap-2 bg-gray-100 dark:bg-gray-700 rounded-lg p-1 w-fit">
        {[
          { id: 'schedule', label: 'جدول الري', icon: Calendar },
          { id: 'balance', label: 'الميزان المائي', icon: CloudRain },
          { id: 'efficiency', label: 'كفاءة الري', icon: Gauge },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedTab(tab.id as typeof selectedTab)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-md text-sm transition-colors',
              selectedTab === tab.id
                ? 'bg-white shadow-sm text-sahool-600'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Refresh Button */}
      <div className="mt-4 flex justify-end">
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          تحديث
        </button>
      </div>

      {/* Content */}
      <div className="mt-6">
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="bg-gray-100 dark:bg-gray-700 animate-pulse rounded-xl h-32" />
            ))}
          </div>
        ) : selectedTab === 'schedule' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Schedule List */}
            <div className="lg:col-span-2 space-y-4">
              {plan?.schedules.map((schedule, index) => {
                const UrgencyIcon = URGENCY_ICONS[schedule.urgency];
                return (
                  <div
                    key={schedule.schedule_id}
                    className={cn(
                      'bg-white dark:bg-gray-800 rounded-xl border-2 p-5 transition-all',
                      schedule.urgency === 'critical' && 'border-red-200 bg-red-50/50',
                      schedule.urgency === 'high' && 'border-orange-200 bg-orange-50/50',
                      schedule.urgency !== 'critical' &&
                        schedule.urgency !== 'high' &&
                        'border-gray-100 dark:border-gray-700'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className={cn(
                            'p-3 rounded-lg',
                            schedule.urgency === 'critical'
                              ? 'bg-red-100'
                              : schedule.urgency === 'high'
                                ? 'bg-orange-100'
                                : 'bg-sahool-100'
                          )}
                        >
                          <Droplets
                            className={cn(
                              'w-6 h-6',
                              schedule.urgency === 'critical'
                                ? 'text-red-600'
                                : schedule.urgency === 'high'
                                  ? 'text-orange-600'
                                  : 'text-sahool-600'
                            )}
                          />
                        </div>
                        <div>
                          <h3 className="font-bold text-gray-900 dark:text-gray-100">
                            {schedule.crop_name_ar} - اليوم {index + 1}
                          </h3>
                          <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2 mt-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(schedule.irrigation_date).toLocaleDateString('ar-YE')}
                            <Clock className="w-3 h-3 mr-2" />
                            {schedule.start_time}
                          </p>
                        </div>
                      </div>
                      <span
                        className={cn(
                          'px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1',
                          URGENCY_COLORS[schedule.urgency]
                        )}
                      >
                        <UrgencyIcon className="w-3 h-3" />
                        {schedule.urgency_ar}
                      </span>
                    </div>

                    <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                      <div className="bg-gray-50 dark:bg-gray-950 rounded-lg p-3">
                        <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                          {schedule.duration_minutes} دقيقة
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">المدة</p>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-950 rounded-lg p-3">
                        <p className="text-lg font-bold text-blue-600">
                          {schedule.water_amount_m3.toFixed(1)} م³
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">كمية المياه</p>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-950 rounded-lg p-3">
                        <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                          {schedule.method_ar}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">الطريقة</p>
                      </div>
                    </div>

                    <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                      {schedule.reasoning_ar}
                    </p>

                    {schedule.weather_adjusted && (
                      <div className="mt-2 flex items-center gap-2 text-xs text-green-600">
                        <CloudRain className="w-3 h-3" />
                        تم تعديل الجدول حسب توقعات الطقس
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Recommendations & Alerts */}
            <div className="space-y-4">
              {/* Alerts */}
              {plan?.alerts_ar && plan.alerts_ar.length > 0 && (
                <div className="bg-red-50 rounded-xl border border-red-200 p-4">
                  <h4 className="font-bold text-red-700 mb-2 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    تنبيهات
                  </h4>
                  <ul className="space-y-2">
                    {plan.alerts_ar.map((alert, i) => (
                      <li key={i} className="text-sm text-red-600">
                        {alert}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
                <h4 className="font-bold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                  <Leaf className="w-4 h-4 text-sahool-600" />
                  التوصيات
                </h4>
                <ul className="space-y-2">
                  {plan?.recommendations_ar.map((rec, i) => (
                    <li
                      key={i}
                      className="text-sm text-gray-600 dark:text-gray-400 p-2 bg-gray-50 dark:bg-gray-950 rounded"
                    >
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Crop Info */}
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
                <h4 className="font-bold text-gray-900 dark:text-gray-100 mb-3">معلومات المحصول</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">المحصول:</span>
                    <span className="font-medium">{plan?.crop_name_ar}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">مرحلة النمو:</span>
                    <span className="font-medium">{plan?.growth_stage_ar}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">المساحة:</span>
                    <span className="font-medium">{plan?.area_hectares} هكتار</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">الاحتياج المائي:</span>
                    <span className="font-medium">
                      {plan?.current_water_need_mm.toFixed(1)} ملم
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : selectedTab === 'balance' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Water Balance Chart */}
            <div className="lg:col-span-2">
              <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">
                الميزان المائي - آخر 14 يوم
              </h3>
              <DataTable
                columns={[
                  {
                    key: 'date',
                    header: 'التاريخ',
                    render: (day: WaterBalance) => (
                      <span className="font-medium">
                        {new Date(day.date).toLocaleDateString('ar-YE', {
                          weekday: 'short',
                          day: 'numeric',
                        })}
                      </span>
                    ),
                  },
                  {
                    key: 'et_mm',
                    header: 'التبخر',
                    render: (day: WaterBalance) => (
                      <span className="text-red-600">{day.et_mm.toFixed(1)} ملم</span>
                    ),
                  },
                  {
                    key: 'rainfall_mm',
                    header: 'الأمطار',
                    render: (day: WaterBalance) => (
                      <span className="text-blue-600">{day.rainfall_mm.toFixed(1)} ملم</span>
                    ),
                  },
                  {
                    key: 'irrigation_mm',
                    header: 'الري',
                    render: (day: WaterBalance) => (
                      <span className="text-green-600">{day.irrigation_mm.toFixed(1)} ملم</span>
                    ),
                  },
                  {
                    key: 'water_deficit_mm',
                    header: 'العجز',
                    render: (day: WaterBalance) => (
                      <span
                        className={cn(
                          day.water_deficit_mm > 2
                            ? 'text-red-600 font-medium'
                            : 'text-gray-600 dark:text-gray-400'
                        )}
                      >
                        {day.water_deficit_mm.toFixed(1)} ملم
                      </span>
                    ),
                  },
                ]}
                data={waterBalance?.daily_data.slice(-7) || []}
                keyExtractor={(day) => day.date}
                isLoading={isLoading}
                emptyMessage="لا توجد بيانات"
              />
            </div>

            {/* Summary */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6">
              <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">ملخص الفترة</h3>
              <div className="space-y-4">
                <div className="p-3 bg-red-50 rounded-lg">
                  <div className="flex items-center gap-2 text-red-600 mb-1">
                    <TrendingUp className="w-4 h-4" />
                    <span className="text-sm font-medium">التبخر الكلي</span>
                  </div>
                  <p className="text-2xl font-bold text-red-700">
                    {(waterBalance?.summary.total_et_mm ?? 0).toFixed(1)} ملم
                  </p>
                </div>

                <div className="p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center gap-2 text-blue-600 mb-1">
                    <CloudRain className="w-4 h-4" />
                    <span className="text-sm font-medium">الأمطار الكلية</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-700">
                    {(waterBalance?.summary.total_rainfall_mm ?? 0).toFixed(1)} ملم
                  </p>
                </div>

                <div className="p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2 text-green-600 mb-1">
                    <Droplets className="w-4 h-4" />
                    <span className="text-sm font-medium">الري الكلي</span>
                  </div>
                  <p className="text-2xl font-bold text-green-700">
                    {(waterBalance?.summary.total_irrigation_mm ?? 0).toFixed(1)} ملم
                  </p>
                </div>

                <div
                  className={cn(
                    'p-3 rounded-lg',
                    (waterBalance?.summary.cumulative_deficit_mm || 0) > 20
                      ? 'bg-red-50'
                      : 'bg-gray-50 dark:bg-gray-950'
                  )}
                >
                  <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400 mb-1">
                    <TrendingDown className="w-4 h-4" />
                    <span className="text-sm font-medium">العجز التراكمي</span>
                  </div>
                  <p
                    className={cn(
                      'text-2xl font-bold',
                      (waterBalance?.summary.cumulative_deficit_mm || 0) > 20
                        ? 'text-red-700'
                        : 'text-gray-700 dark:text-gray-300'
                    )}
                  >
                    {(waterBalance?.summary.cumulative_deficit_mm ?? 0).toFixed(1)} ملم
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Irrigation Methods */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6">
              <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">كفاءة طرق الري</h3>
              <div className="space-y-3">
                {methods.map((method) => (
                  <div key={method.id} className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className="font-medium">{method.name_ar}</span>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {method.efficiency_percent}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className={cn(
                            'h-2 rounded-full',
                            method.efficiency_percent >= 80
                              ? 'bg-green-500'
                              : method.efficiency_percent >= 60
                                ? 'bg-amber-500'
                                : 'bg-red-500'
                          )}
                          style={{ width: `${method.efficiency_percent}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 p-4 bg-sahool-50 rounded-lg">
                <p className="text-sm text-sahool-700">
                  💡 <strong>نصيحة:</strong> التحويل للري بالتنقيط يمكن أن يوفر حتى 45% من استهلاك
                  المياه مقارنة بالري التقليدي
                </p>
              </div>
            </div>

            {/* Supported Crops */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6">
              <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">المحاصيل المدعومة</h3>
              <div className="grid grid-cols-2 gap-3">
                {crops.map((crop) => (
                  <div key={crop.id} className="p-3 bg-gray-50 dark:bg-gray-950 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Leaf className="w-4 h-4 text-green-600" />
                      <span className="font-medium">{crop.name_ar}</span>
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                      {Object.entries(crop.water_requirements_mm_day)
                        .slice(0, 2)
                        .map(([stage, value]) => (
                          <div key={stage} className="flex justify-between">
                            <span>
                              {stage === 'seedling'
                                ? 'شتلة'
                                : stage === 'vegetative'
                                  ? 'نمو'
                                  : 'إزهار'}
                              :
                            </span>
                            <span className="text-blue-600">{value} ملم/يوم</span>
                          </div>
                        ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
