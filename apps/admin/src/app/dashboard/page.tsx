'use client';

// Sahool Admin Dashboard - Main Page
// الصفحة الرئيسية للوحة تحكم سهول - غرفة العمليات المركزية

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import AlertBadge from '@/components/ui/AlertBadge';
import { fetchDashboardStats, fetchFarms, fetchDiagnoses } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { DashboardStats, Farm, DiagnosisRecord } from '@/types';
import {
  MapPin,
  Leaf,
  Bug,
  AlertTriangle,
  TrendingUp,
  Activity,
  Calendar,
  Eye,
  Users,
  DollarSign,
  Droplets,
  Sun,
} from 'lucide-react';
import Link from 'next/link';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from 'recharts';

// Dynamic import for map (no SSR)
const FarmsMap = dynamic(() => import('@/components/maps/FarmsMap'), {
  ssr: false,
  loading: () => (
    <div className="h-[400px] bg-gray-100 animate-pulse rounded-xl flex items-center justify-center">
      <p className="text-gray-500">جاري تحميل الخريطة...</p>
    </div>
  ),
});

// Chart colors
const CHART_COLORS = {
  primary: '#2E7D32',
  secondary: '#4CAF50',
  accent: '#81C784',
  warning: '#FF9800',
  danger: '#F44336',
  info: '#2196F3',
};

const PIE_COLORS = ['#2E7D32', '#4CAF50', '#81C784', '#A5D6A7', '#C8E6C9'];

// Mock data for charts
const yieldTrendData = [
  { month: 'يناير', yield: 120, forecast: 115 },
  { month: 'فبراير', yield: 140, forecast: 135 },
  { month: 'مارس', yield: 280, forecast: 250 },
  { month: 'أبريل', yield: 320, forecast: 300 },
  { month: 'مايو', yield: 180, forecast: 190 },
  { month: 'يونيو', yield: 95, forecast: 100 },
];

const cropDistributionData = [
  { name: 'قمح', value: 35 },
  { name: 'بن', value: 25 },
  { name: 'قات', value: 20 },
  { name: 'فواكه', value: 12 },
  { name: 'خضروات', value: 8 },
];

const weeklyActivityData = [
  { day: 'السبت', diagnoses: 12, irrigations: 8, alerts: 3 },
  { day: 'الأحد', diagnoses: 18, irrigations: 12, alerts: 5 },
  { day: 'الاثنين', diagnoses: 15, irrigations: 10, alerts: 2 },
  { day: 'الثلاثاء', diagnoses: 22, irrigations: 15, alerts: 4 },
  { day: 'الأربعاء', diagnoses: 19, irrigations: 11, alerts: 6 },
  { day: 'الخميس', diagnoses: 25, irrigations: 14, alerts: 3 },
  { day: 'الجمعة', diagnoses: 8, irrigations: 5, alerts: 1 },
];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [recentDiagnoses, setRecentDiagnoses] = useState<DiagnosisRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFarm, setSelectedFarm] = useState<Farm | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, farmsData, diagnosesData] = await Promise.all([
          fetchDashboardStats(),
          fetchFarms(),
          fetchDiagnoses({ limit: 5 }),
        ]);
        setStats(statsData);
        setFarms(farmsData);
        setRecentDiagnoses(diagnosesData.slice(0, 5));
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const handleFarmClick = (farm: Farm) => {
    setSelectedFarm(farm);
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <Header title="لوحة التحكم" subtitle="نظرة عامة على المنصة" />
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 animate-pulse rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <Header title="لوحة التحكم" subtitle="نظرة عامة على المنصة" />

      {/* Statistics Cards */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="إجمالي المزارع"
          value={stats?.totalFarms || 0}
          icon={MapPin}
          trend={{ value: 12, isPositive: true }}
          iconColor="text-blue-600"
        />
        <StatCard
          title="المساحة الإجمالية"
          value={stats?.totalArea?.toFixed(1) || '0'}
          suffix="هكتار"
          icon={Leaf}
          trend={{ value: 8, isPositive: true }}
          iconColor="text-green-600"
        />
        <StatCard
          title="التشخيصات هذا الأسبوع"
          value={stats?.weeklyDiagnoses || 0}
          icon={Bug}
          trend={{ value: 23, isPositive: true }}
          iconColor="text-purple-600"
        />
        <StatCard
          title="تنبيهات حرجة"
          value={stats?.criticalAlerts || 0}
          icon={AlertTriangle}
          iconColor="text-red-600"
        />
      </div>

      {/* Second Row - More Stats */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="متوسط صحة المحاصيل"
          value={`${stats?.avgHealthScore?.toFixed(1) || '0'}%`}
          icon={Activity}
          iconColor="text-emerald-600"
        />
        <StatCard
          title="قيد المراجعة"
          value={stats?.pendingReviews || 0}
          icon={Eye}
          iconColor="text-amber-600"
        />
        <StatCard
          title="المزارع النشطة"
          value={stats?.activeFarms || 0}
          icon={TrendingUp}
          iconColor="text-cyan-600"
        />
      </div>

      {/* Charts Row */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Yield Trend Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900">توقعات الإنتاجية (طن)</h3>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">آخر 6 أشهر</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={yieldTrendData}>
                <defs>
                  <linearGradient id="yieldGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                    direction: 'rtl',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="yield"
                  stroke={CHART_COLORS.primary}
                  fill="url(#yieldGradient)"
                  strokeWidth={2}
                  name="الإنتاج الفعلي"
                />
                <Line
                  type="monotone"
                  dataKey="forecast"
                  stroke={CHART_COLORS.warning}
                  strokeDasharray="5 5"
                  strokeWidth={2}
                  dot={false}
                  name="التوقعات"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weekly Activity Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900">نشاط الأسبوع</h3>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full bg-sahool-600"></span>
                تشخيصات
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                ري
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full bg-red-500"></span>
                تنبيهات
              </span>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyActivityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                    direction: 'rtl',
                  }}
                />
                <Bar dataKey="diagnoses" fill={CHART_COLORS.primary} radius={[4, 4, 0, 0]} name="تشخيصات" />
                <Bar dataKey="irrigations" fill={CHART_COLORS.info} radius={[4, 4, 0, 0]} name="عمليات ري" />
                <Bar dataKey="alerts" fill={CHART_COLORS.danger} radius={[4, 4, 0, 0]} name="تنبيهات" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Third Row - Crop Distribution and Quick Stats */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Crop Distribution Pie Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="font-bold text-gray-900 mb-4">توزيع المحاصيل</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={cropDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {cropDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Performance Metrics */}
        <div className="lg:col-span-2 bg-gradient-to-br from-sahool-600 to-sahool-700 p-6 rounded-xl shadow-sm text-white">
          <h3 className="font-bold mb-4">أداء المنصة اليوم</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
              <Users className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-2xl font-bold">1,240</p>
              <p className="text-xs opacity-80">مزارع نشط</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
              <DollarSign className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-2xl font-bold">$42K</p>
              <p className="text-xs opacity-80">مبيعات اليوم</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
              <Droplets className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-2xl font-bold">156</p>
              <p className="text-xs opacity-80">عملية ري</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
              <Sun className="w-6 h-6 mb-2 opacity-80" />
              <p className="text-2xl font-bold">28°</p>
              <p className="text-xs opacity-80">متوسط الحرارة</p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-white/20">
            <div className="flex items-center justify-between text-sm">
              <span className="opacity-80">نسبة النمو الشهري</span>
              <span className="font-bold text-green-300">+12.5%</span>
            </div>
            <div className="mt-2 h-2 bg-white/20 rounded-full overflow-hidden">
              <div className="h-full w-3/4 bg-green-400 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Map and Recent Activity */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Farms Map */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-4 border-b border-gray-100 flex items-center justify-between">
            <h2 className="font-bold text-gray-900">خريطة المزارع</h2>
            <Link
              href="/farms"
              className="text-sm text-sahool-600 hover:text-sahool-700 font-medium"
            >
              عرض الكل ←
            </Link>
          </div>
          <div className="h-[400px]">
            <FarmsMap
              farms={farms}
              onFarmClick={handleFarmClick}
              selectedFarmId={selectedFarm?.id}
              showHealthOverlay={true}
            />
          </div>
        </div>

        {/* Recent Diagnoses */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="p-4 border-b border-gray-100 flex items-center justify-between">
            <h2 className="font-bold text-gray-900">أحدث التشخيصات</h2>
            <Link
              href="/diseases"
              className="text-sm text-sahool-600 hover:text-sahool-700 font-medium"
            >
              عرض الكل ←
            </Link>
          </div>
          <div className="divide-y divide-gray-100">
            {recentDiagnoses.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                لا توجد تشخيصات حديثة
              </div>
            ) : (
              recentDiagnoses.map((diagnosis) => (
                <div key={diagnosis.id} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                      <Bug className="w-6 h-6 text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {diagnosis.diseaseNameAr}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {diagnosis.farmName}
                      </p>
                      <div className="mt-1 flex items-center gap-2">
                        <AlertBadge severity={diagnosis.severity} />
                        <span className="text-xs text-gray-400">
                          {formatDate(diagnosis.diagnosedAt)}
                        </span>
                      </div>
                    </div>
                    <div className="text-left">
                      <span className="text-lg font-bold text-gray-900">
                        {diagnosis.confidence.toFixed(0)}%
                      </span>
                      <p className="text-xs text-gray-500">دقة</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Selected Farm Detail (if any) */}
      {selectedFarm && (
        <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-lg text-gray-900">{selectedFarm.nameAr}</h2>
            <button
              onClick={() => setSelectedFarm(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">المحافظة</p>
              <p className="font-medium">{selectedFarm.governorate}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">المساحة</p>
              <p className="font-medium">{selectedFarm.area.toFixed(1)} هكتار</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">المحاصيل</p>
              <p className="font-medium">{selectedFarm.crops.join(', ')}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">مستوى الصحة</p>
              <p className="font-bold text-sahool-600">{selectedFarm.healthScore}%</p>
            </div>
          </div>
          <div className="mt-4 flex gap-3">
            <Link
              href={`/farms/${selectedFarm.id}`}
              className="px-4 py-2 bg-sahool-600 text-white rounded-lg text-sm font-medium hover:bg-sahool-700 transition-colors"
            >
              عرض التفاصيل
            </Link>
            <Link
              href={`/diseases?farmId=${selectedFarm.id}`}
              className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              عرض التشخيصات
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
