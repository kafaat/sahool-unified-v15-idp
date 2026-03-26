'use client';

import React, { useState, useMemo } from 'react';
import { Calendar, Plus, Search, AlertTriangle, TrendingUp, DollarSign } from 'lucide-react';
import { useSeasons, useSeasonStats } from '@/features/seasons';
import type { SeasonStatus, SeasonType } from '@/features/seasons';

const statusConfig: Record<SeasonStatus, { color: string; labelAr: string }> = {
  planning: { color: 'bg-blue-100 text-blue-800', labelAr: 'تخطيط' },
  active: { color: 'bg-green-100 text-green-800', labelAr: 'نشط' },
  harvesting: { color: 'bg-orange-100 text-orange-800', labelAr: 'حصاد' },
  completed: { color: 'bg-gray-100 text-gray-800', labelAr: 'مكتمل' },
  cancelled: { color: 'bg-red-100 text-red-800', labelAr: 'ملغي' },
};

const typeLabelsAr: Record<SeasonType, string> = {
  winter: 'شتوي',
  summer: 'صيفي',
  spring: 'ربيعي',
  fall: 'خريفي',
};

const statusOptions: Array<{ value: SeasonStatus | 'all'; labelAr: string }> = [
  { value: 'all', labelAr: 'جميع الحالات' },
  { value: 'planning', labelAr: 'تخطيط' },
  { value: 'active', labelAr: 'نشط' },
  { value: 'harvesting', labelAr: 'حصاد' },
  { value: 'completed', labelAr: 'مكتمل' },
];

export default function SeasonsClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<SeasonStatus | 'all'>('all');

  const {
    data: seasons = [],
    isLoading,
    error,
  } = useSeasons(selectedStatus !== 'all' ? { status: selectedStatus } : undefined);
  const { data: stats } = useSeasonStats();

  const filteredSeasons = useMemo(() => {
    if (!searchTerm) return seasons;
    const term = searchTerm.toLowerCase();
    return seasons.filter(
      (s) =>
        s.name.toLowerCase().includes(term) ||
        s.nameAr.includes(searchTerm) ||
        s.farmNameAr.includes(searchTerm)
    );
  }, [seasons, searchTerm]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات المواسم</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المواسم</h1>
          <p className="text-gray-500 mt-1">Season Management</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors">
          <Plus className="w-4 h-4" />
          <span>موسم جديد</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي المواسم</div>
          <div className="text-2xl font-bold text-gray-900">
            {stats?.totalSeasons ?? seasons.length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">مواسم نشطة</div>
          <div className="text-2xl font-bold text-green-600">{stats?.activeSeasons ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">مكتملة</div>
          <div className="text-2xl font-bold text-blue-600">{stats?.completedSeasons ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <TrendingUp className="w-3.5 h-3.5" /> معدل الإنتاج
          </div>
          <div className="text-2xl font-bold text-sahool-green-600">
            {stats?.averageYieldRate ?? 0}%
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <DollarSign className="w-3.5 h-3.5" /> الميزانية
          </div>
          <div className="text-2xl font-bold text-purple-600">
            {((stats?.totalBudgetSar ?? 0) / 1000).toFixed(0)}K
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في المواسم..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
          />
        </div>
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value as SeasonStatus | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {statusOptions.map((o) => (
            <option key={o.value} value={o.value}>
              {o.labelAr}
            </option>
          ))}
        </select>
      </div>

      {/* Season Cards */}
      <div className="space-y-4">
        {filteredSeasons.length === 0 ? (
          <div className="text-center py-12 text-gray-500">لا توجد مواسم</div>
        ) : (
          filteredSeasons.map((season) => {
            const st = statusConfig[season.status];
            const budgetPercent =
              season.budgetSar > 0 ? Math.round((season.spentSar / season.budgetSar) * 100) : 0;
            return (
              <div
                key={season.id}
                className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-sahool-green-600" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-900">{season.nameAr}</h3>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium ${st.color}`}
                        >
                          {st.labelAr}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500">
                        {season.farmNameAr} | {typeLabelsAr[season.type]} | {season.startDate} →{' '}
                        {season.endDate}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 text-sm">
                    <div className="text-center">
                      <div className="font-bold text-gray-900">{season.cropsCount}</div>
                      <div className="text-gray-500">محصول</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-gray-900">{season.fieldsCount}</div>
                      <div className="text-gray-500">حقل</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-gray-900">{season.totalAreaHa}</div>
                      <div className="text-gray-500">هكتار</div>
                    </div>
                    {season.actualYieldTons !== undefined ? (
                      <div className="text-center">
                        <div className="font-bold text-sahool-green-600">
                          {season.actualYieldTons}t
                        </div>
                        <div className="text-gray-500">الإنتاج</div>
                      </div>
                    ) : (
                      <div className="text-center">
                        <div className="font-bold text-blue-600">{season.targetYieldTons}t</div>
                        <div className="text-gray-500">المستهدف</div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Progress Bars */}
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>التقدم</span>
                      <span>{season.progress}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-sahool-green-500 rounded-full transition-all"
                        style={{ width: `${season.progress}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>الميزانية</span>
                      <span>
                        {season.spentSar.toLocaleString()} / {season.budgetSar.toLocaleString()}{' '}
                        ريال
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${budgetPercent > 90 ? 'bg-red-500' : 'bg-blue-500'}`}
                        style={{ width: `${Math.min(budgetPercent, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
