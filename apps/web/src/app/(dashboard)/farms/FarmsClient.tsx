'use client';

import React, { useState, useMemo } from 'react';
import { Building2, Plus, Search, MapPin, Droplets, Users, AlertTriangle, X } from 'lucide-react';
import { useFarms, useFarmStats, useUpdateFarm } from '@/features/farms';
import type { Farm, FarmStatus } from '@/features/farms';

const statusConfig: Record<FarmStatus, { color: string; labelAr: string }> = {
  active: { color: 'bg-green-100 text-green-800', labelAr: 'نشطة' },
  inactive: { color: 'bg-gray-100 text-gray-800', labelAr: 'غير نشطة' },
  seasonal: { color: 'bg-blue-100 text-blue-800', labelAr: 'موسمية' },
};

export default function FarmsClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null);
  const [editName, setEditName] = useState('');
  const [editNameAr, setEditNameAr] = useState('');
  const { data: farms = [], isLoading, error } = useFarms();
  const { data: stats } = useFarmStats();
  const updateFarm = useUpdateFarm();

  const filteredFarms = useMemo(() => {
    if (!searchTerm) return farms;
    const term = searchTerm.toLowerCase();
    return farms.filter(
      (f) =>
        f.name.toLowerCase().includes(term) ||
        f.nameAr.includes(searchTerm) ||
        f.locationAr.includes(searchTerm)
    );
  }, [farms, searchTerm]);

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
          <p className="text-red-600">فشل في تحميل بيانات المزارع</p>
          <p className="text-gray-500 text-sm">Failed to load farms data</p>
        </div>
      </div>
    );
  }

  const handleOpenEdit = (farm: Farm) => {
    setEditingFarm(farm);
    setEditName(farm.name);
    setEditNameAr(farm.nameAr);
  };

  const handleSaveEdit = () => {
    if (!editingFarm) return;
    updateFarm.mutate(
      { id: editingFarm.id, data: { name: editName, nameAr: editNameAr } },
      { onSuccess: () => setEditingFarm(null) }
    );
  };

  return (
    <div className="space-y-6">
      {/* Edit Dialog */}
      {editingFarm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative">
            <button onClick={() => setEditingFarm(null)} className="absolute top-3 left-3 text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-bold text-gray-900 mb-4">تعديل المزرعة</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الاسم (EN)</label>
                <input value={editName} onChange={(e) => setEditName(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الاسم (AR)</label>
                <input value={editNameAr} onChange={(e) => setEditNameAr(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" dir="rtl" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setEditingFarm(null)} className="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50">إلغاء</button>
              <button onClick={handleSaveEdit} disabled={updateFarm.isPending} className="px-4 py-2 text-sm text-white bg-sahool-green-600 rounded-lg hover:bg-sahool-green-700 disabled:opacity-50">
                {updateFarm.isPending ? 'جاري الحفظ...' : 'حفظ'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المزارع</h1>
          <p className="text-gray-500 mt-1">Farm Management</p>
        </div>
        <button
          disabled
          title="قريباً - Coming soon"
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-4 h-4" />
          <span>إضافة مزرعة</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي المزارع</div>
          <div className="text-2xl font-bold text-gray-900">
            {stats?.totalFarms ?? farms.length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">مزارع نشطة</div>
          <div className="text-2xl font-bold text-green-600">{stats?.activeFarms ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">المساحة الكلية</div>
          <div className="text-2xl font-bold text-blue-600">{stats?.totalAreaHa ?? 0} هـ</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">المساحة المزروعة</div>
          <div className="text-2xl font-bold text-sahool-green-600">
            {stats?.cultivatedAreaHa ?? 0} هـ
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي العمال</div>
          <div className="text-2xl font-bold text-purple-600">{stats?.totalWorkers ?? 0}</div>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="بحث في المزارع..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
        />
      </div>

      {/* Farm Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredFarms.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">لا توجد مزارع</div>
        ) : (
          filteredFarms.map((farm) => {
            const st = statusConfig[farm.status];
            return (
              <div
                key={farm.id}
                className="bg-white rounded-lg border hover:shadow-md transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                        <Building2 className="w-6 h-6 text-sahool-green-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{farm.nameAr}</h3>
                        <p className="text-sm text-gray-500">{farm.name}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${st.color}`}>
                      {st.labelAr}
                    </span>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span>{farm.locationAr}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Droplets className="w-4 h-4 text-blue-400" />
                      <span>{farm.waterSourceAr}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Users className="w-4 h-4 text-gray-400" />
                      <span>{farm.workersCount} عامل</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t grid grid-cols-3 gap-2 text-center">
                    <div>
                      <div className="text-lg font-bold text-gray-900">{farm.totalAreaHa}</div>
                      <div className="text-xs text-gray-500">هكتار كلي</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-sahool-green-600">
                        {farm.cultivatedAreaHa}
                      </div>
                      <div className="text-xs text-gray-500">مزروع</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-blue-600">{farm.fieldsCount}</div>
                      <div className="text-xs text-gray-500">حقل</div>
                    </div>
                  </div>
                </div>
                <div className="px-6 py-3 bg-gray-50 border-t flex justify-between">
                  <button
                    onClick={() => handleOpenEdit(farm)}
                    className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                  >
                    عرض التفاصيل
                  </button>
                  <button
                    onClick={() => handleOpenEdit(farm)}
                    className="text-gray-500 hover:text-gray-700 text-sm"
                  >
                    تعديل
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
