'use client';

// Sahool Admin Dashboard - Main Page
// الصفحة الرئيسية للوحة تحكم سهول

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
} from 'lucide-react';
import Link from 'next/link';

// Dynamic import for map (no SSR)
const FarmsMap = dynamic(() => import('@/components/maps/FarmsMap'), {
  ssr: false,
  loading: () => (
    <div className="h-[400px] bg-gray-100 animate-pulse rounded-xl flex items-center justify-center">
      <p className="text-gray-500">جاري تحميل الخريطة...</p>
    </div>
  ),
});

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
