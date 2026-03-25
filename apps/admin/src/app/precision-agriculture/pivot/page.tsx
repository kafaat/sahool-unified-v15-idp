'use client';

// Center Pivot Irrigation Management - الري المحوري
// Valley-style pivot management with VRI zones

import { useEffect, useState } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import { cn } from '@/lib/utils';
import {
  Droplets,
  Play,
  Pause,
  RotateCw,
  Settings,
  PlusCircle,
  BarChart3,
  Grid3X3,
  RefreshCw,
  Calendar,
} from 'lucide-react';

// Types
interface PivotSystem {
  id: string;
  name: string;
  name_ar: string;
  field_id: string;
  field_name_ar: string;
  status: 'running' | 'stopped' | 'maintenance' | 'scheduled';
  current_angle: number;
  speed_percent: number;
  direction: 'clockwise' | 'counterclockwise';
  area_hectares: number;
  length_meters: number;
  spans_count: number;
  sectors_count: number;
  vri_zones_count: number;
  water_usage_m3: number;
  last_irrigation: string;
  next_scheduled: string | null;
  application_rate_mm_hr: number;
  efficiency_percent: number;
}

interface PivotStatistics {
  total_pivots: number;
  active_pivots: number;
  total_area_hectares: number;
  water_usage_today_m3: number;
  water_savings_percent: number;
  average_efficiency: number;
}

const STATUS_COLORS = {
  running: 'bg-green-100 text-green-700 border-green-200',
  stopped: 'bg-gray-100 text-gray-700 border-gray-200',
  maintenance: 'bg-orange-100 text-orange-700 border-orange-200',
  scheduled: 'bg-blue-100 text-blue-700 border-blue-200',
};

const STATUS_LABELS = {
  running: 'يعمل',
  stopped: 'متوقف',
  maintenance: 'صيانة',
  scheduled: 'مجدول',
};

// Mock data generators
function generateMockPivots(): PivotSystem[] {
  return [
    {
      id: 'pivot-001',
      name: 'Main Pivot - North',
      name_ar: 'المحوري الرئيسي - الشمال',
      field_id: 'field-001',
      field_name_ar: 'حقل القمح الشمالي',
      status: 'running',
      current_angle: 127,
      speed_percent: 75,
      direction: 'clockwise',
      area_hectares: 52.5,
      length_meters: 410,
      spans_count: 7,
      sectors_count: 8,
      vri_zones_count: 56,
      water_usage_m3: 1250,
      last_irrigation: new Date().toISOString(),
      next_scheduled: null,
      application_rate_mm_hr: 6.5,
      efficiency_percent: 92,
    },
    {
      id: 'pivot-002',
      name: 'East Field Pivot',
      name_ar: 'محوري الحقل الشرقي',
      field_id: 'field-002',
      field_name_ar: 'حقل الذرة الشرقي',
      status: 'stopped',
      current_angle: 0,
      speed_percent: 0,
      direction: 'clockwise',
      area_hectares: 35.2,
      length_meters: 335,
      spans_count: 6,
      sectors_count: 6,
      vri_zones_count: 36,
      water_usage_m3: 0,
      last_irrigation: new Date(Date.now() - 86400000).toISOString(),
      next_scheduled: new Date(Date.now() + 3600000).toISOString(),
      application_rate_mm_hr: 5.8,
      efficiency_percent: 88,
    },
    {
      id: 'pivot-003',
      name: 'South Quarter Pivot',
      name_ar: 'محوري الربع الجنوبي',
      field_id: 'field-003',
      field_name_ar: 'حقل البرسيم الجنوبي',
      status: 'scheduled',
      current_angle: 45,
      speed_percent: 0,
      direction: 'counterclockwise',
      area_hectares: 42.8,
      length_meters: 370,
      spans_count: 7,
      sectors_count: 8,
      vri_zones_count: 56,
      water_usage_m3: 0,
      last_irrigation: new Date(Date.now() - 172800000).toISOString(),
      next_scheduled: new Date(Date.now() + 7200000).toISOString(),
      application_rate_mm_hr: 6.2,
      efficiency_percent: 90,
    },
  ];
}

function generateMockStatistics(pivots: PivotSystem[]): PivotStatistics {
  const activePivots = pivots.filter((p) => p.status === 'running').length;
  const totalArea = pivots.reduce((sum, p) => sum + p.area_hectares, 0);
  const waterUsage = pivots.reduce((sum, p) => sum + p.water_usage_m3, 0);
  const avgEfficiency =
    pivots.length > 0
      ? pivots.reduce((sum, p) => sum + p.efficiency_percent, 0) / pivots.length
      : 0;

  return {
    total_pivots: pivots.length,
    active_pivots: activePivots,
    total_area_hectares: totalArea,
    water_usage_today_m3: waterUsage,
    water_savings_percent: 22,
    average_efficiency: avgEfficiency,
  };
}

function PivotVisualization({ pivot }: { pivot: PivotSystem }) {
  const sectors = Array.from({ length: pivot.sectors_count }, (_, i) => ({
    id: `sector_${i}`,
    startAngle: (i * 360) / pivot.sectors_count,
    endAngle: ((i + 1) * 360) / pivot.sectors_count,
    color: `hsl(${120 + i * 15}, 70%, ${50 + (i % 2) * 10}%)`,
  }));

  return (
    <div className="relative aspect-square max-w-[180px] mx-auto">
      <svg viewBox="0 0 200 200" className="w-full h-full">
        {/* Background circle */}
        <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" strokeWidth="2" />

        {/* Sectors */}
        {sectors.map((sector) => {
          const startRad = ((sector.startAngle - 90) * Math.PI) / 180;
          const endRad = ((sector.endAngle - 90) * Math.PI) / 180;
          const x1 = 100 + 85 * Math.cos(startRad);
          const y1 = 100 + 85 * Math.sin(startRad);
          const x2 = 100 + 85 * Math.cos(endRad);
          const y2 = 100 + 85 * Math.sin(endRad);
          const largeArc = sector.endAngle - sector.startAngle > 180 ? 1 : 0;

          return (
            <path
              key={sector.id}
              d={`M 100 100 L ${x1} ${y1} A 85 85 0 ${largeArc} 1 ${x2} ${y2} Z`}
              fill={sector.color}
              fillOpacity={0.6}
              stroke="#fff"
              strokeWidth="1"
            />
          );
        })}

        {/* Center point */}
        <circle cx="100" cy="100" r="8" fill="#1e40af" />

        {/* Pivot arm */}
        {pivot.status === 'running' && (
          <g>
            <line
              x1="100"
              y1="100"
              x2={100 + 80 * Math.cos(((pivot.current_angle - 90) * Math.PI) / 180)}
              y2={100 + 80 * Math.sin(((pivot.current_angle - 90) * Math.PI) / 180)}
              stroke="#1e40af"
              strokeWidth="4"
              strokeLinecap="round"
            >
              <animateTransform
                attributeName="transform"
                type="rotate"
                from={`${pivot.current_angle} 100 100`}
                to={`${pivot.current_angle + 360} 100 100`}
                dur="60s"
                repeatCount="indefinite"
              />
            </line>
          </g>
        )}

        {/* Status indicator */}
        <circle cx="100" cy="100" r="4" fill={pivot.status === 'running' ? '#22c55e' : '#9ca3af'} />

        {/* Angle indicator */}
        <text x="100" y="170" textAnchor="middle" className="text-xs fill-gray-500">
          {pivot.current_angle}°
        </text>
      </svg>
    </div>
  );
}

export default function PivotIrrigationPage() {
  const [pivots, setPivots] = useState<PivotSystem[]>([]);
  const [statistics, setStatistics] = useState<PivotStatistics | null>(null);
  const [selectedPivot, setSelectedPivot] = useState<PivotSystem | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      const mockPivots = generateMockPivots();
      setPivots(mockPivots);
      setStatistics(generateMockStatistics(mockPivots));
      setSelectedPivot(mockPivots[0] ?? null);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="p-6">
      <Header
        title="الري المحوري"
        subtitle="إدارة أنظمة الري المحوري على طراز Valley مع مناطق VRI"
      />

      {/* Statistics Cards */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="إجمالي المحاور"
          value={statistics?.total_pivots || 0}
          icon={Grid3X3}
          iconColor="text-blue-600"
        />
        <StatCard
          title="محاور نشطة"
          value={statistics?.active_pivots || 0}
          icon={Play}
          iconColor="text-green-600"
        />
        <StatCard
          title="استهلاك اليوم"
          value={statistics?.water_usage_today_m3?.toLocaleString() || '0'}
          suffix="م³"
          icon={Droplets}
          iconColor="text-cyan-600"
        />
        <StatCard
          title="توفير المياه"
          value={statistics?.water_savings_percent || 0}
          suffix="%"
          icon={BarChart3}
          iconColor="text-purple-600"
        />
      </div>

      {/* Refresh Button */}
      <div className="mt-4 flex justify-between items-center">
        <button
          disabled
          className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="قريبًا"
        >
          <PlusCircle className="w-4 h-4" />
          إضافة محوري جديد
        </button>
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          تحديث
        </button>
      </div>

      {/* Main Content */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pivot List */}
        <div className="space-y-4">
          <h3 className="font-bold text-gray-900 dark:text-gray-100">المحاور المسجلة</h3>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-40 bg-gray-100 dark:bg-gray-700 animate-pulse rounded-xl"
                />
              ))}
            </div>
          ) : (
            pivots.map((pivot) => (
              <div
                key={pivot.id}
                onClick={() => setSelectedPivot(pivot)}
                className={cn(
                  'bg-white dark:bg-gray-800 rounded-xl border-2 p-4 cursor-pointer transition-all',
                  selectedPivot?.id === pivot.id
                    ? 'border-sahool-500 ring-2 ring-sahool-100'
                    : 'border-gray-100 dark:border-gray-700 hover:border-gray-200 dark:hover:border-gray-600'
                )}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-bold text-gray-900 dark:text-gray-100">{pivot.name_ar}</h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {pivot.field_name_ar}
                    </p>
                  </div>
                  <span
                    className={cn(
                      'px-2 py-1 rounded-full text-xs font-medium',
                      STATUS_COLORS[pivot.status]
                    )}
                  >
                    {STATUS_LABELS[pivot.status]}
                  </span>
                </div>

                <PivotVisualization pivot={pivot} />

                <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">المساحة:</span>
                    <span className="font-medium mr-1">{pivot.area_hectares} هـ</span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">الكفاءة:</span>
                    <span className="font-medium mr-1">{pivot.efficiency_percent}%</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Pivot Details */}
        <div className="lg:col-span-2 space-y-6">
          {selectedPivot ? (
            <>
              {/* Control Panel */}
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-gray-900 dark:text-gray-100">لوحة التحكم</h3>
                  <span
                    className={cn(
                      'px-3 py-1 rounded-full text-sm font-medium',
                      STATUS_COLORS[selectedPivot.status]
                    )}
                  >
                    {STATUS_LABELS[selectedPivot.status]}
                  </span>
                </div>

                <div className="flex flex-wrap gap-3 mb-6">
                  <button
                    disabled
                    className={cn(
                      'flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
                      selectedPivot.status === 'running'
                        ? 'bg-red-100 text-red-700 hover:bg-red-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    )}
                    title="قريبًا"
                  >
                    {selectedPivot.status === 'running' ? (
                      <>
                        <Pause className="w-4 h-4" />
                        إيقاف
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        تشغيل
                      </>
                    )}
                  </button>

                  <button
                    disabled
                    className="flex items-center gap-2 px-5 py-2.5 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="قريبًا"
                  >
                    <RotateCw className="w-4 h-4" />
                    عكس الاتجاه
                  </button>

                  <button
                    disabled
                    className="flex items-center gap-2 px-5 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="قريبًا"
                  >
                    <Settings className="w-4 h-4" />
                    الإعدادات
                  </button>
                </div>

                {/* Speed Control */}
                <div className="mb-4">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                    سرعة الدوران: {selectedPivot.speed_percent}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={selectedPivot.speed_percent}
                    className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-sahool-600"
                    readOnly
                  />
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-950 rounded-lg">
                    <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {selectedPivot.spans_count}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">الأبراج</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-950 rounded-lg">
                    <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {selectedPivot.sectors_count}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">القطاعات</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-950 rounded-lg">
                    <p className="text-lg font-bold text-blue-600">
                      {selectedPivot.vri_zones_count}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">مناطق VRI</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-950 rounded-lg">
                    <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {selectedPivot.application_rate_mm_hr}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">ملم/ساعة</p>
                  </div>
                </div>
              </div>

              {/* Sectors Grid */}
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6">
                <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">
                  القطاعات ومناطق VRI
                </h3>
                <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
                  {Array.from({ length: selectedPivot.sectors_count }, (_, i) => (
                    <div
                      key={i}
                      className={cn(
                        'p-3 rounded-lg text-center border transition-colors cursor-pointer',
                        i < 3
                          ? 'bg-green-50 border-green-200 hover:bg-green-100'
                          : 'bg-gray-50 dark:bg-gray-950 border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
                      )}
                    >
                      <p className="font-bold text-sm">Q{i + 1}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {(i * 360) / selectedPivot.sectors_count}°-
                        {((i + 1) * 360) / selectedPivot.sectors_count}°
                      </p>
                      <p className="text-xs text-green-600 mt-1">100%</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6">
                <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">النشاط الأخير</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-950 rounded-lg">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Play className="w-4 h-4 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-sm">بدأ دورة الري</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(selectedPivot.last_irrigation).toLocaleString('ar-SA')}
                      </p>
                    </div>
                  </div>

                  {selectedPivot.next_scheduled && (
                    <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <Calendar className="w-4 h-4 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">الري القادم مجدول</p>
                        <p className="text-xs text-blue-600">
                          {new Date(selectedPivot.next_scheduled).toLocaleString('ar-SA')}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-950 rounded-lg">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <BarChart3 className="w-4 h-4 text-purple-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-sm">تحديث خريطة VRI</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">منذ يومين</p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-12 text-center">
              <Grid3X3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                اختر محوري
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                اختر محوري من القائمة لعرض التفاصيل والتحكم
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
