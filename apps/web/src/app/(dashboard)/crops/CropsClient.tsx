'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Sprout, Plus, Search, AlertTriangle, Leaf, Sun, Droplets } from 'lucide-react';
import { useCrops, useCropStats } from '@/features/crops';
import type { CropCategory, CropStage } from '@/features/crops';

const categoryLabels: Record<CropCategory, string> = {
  cereals: 'حبوب',
  vegetables: 'خضروات',
  fruits: 'فواكه',
  legumes: 'بقوليات',
  forage: 'أعلاف',
  industrial: 'صناعية',
};

const stageConfig: Record<CropStage, { color: string; labelAr: string }> = {
  germination: { color: 'bg-amber-100 text-amber-800', labelAr: 'إنبات' },
  seedling: { color: 'bg-lime-100 text-lime-800', labelAr: 'بادرة' },
  vegetative: { color: 'bg-green-100 text-green-800', labelAr: 'نمو خضري' },
  flowering: { color: 'bg-pink-100 text-pink-800', labelAr: 'إزهار' },
  fruiting: { color: 'bg-orange-100 text-orange-800', labelAr: 'إثمار' },
  maturity: { color: 'bg-yellow-100 text-yellow-800', labelAr: 'نضج' },
  harvest: { color: 'bg-red-100 text-red-800', labelAr: 'حصاد' },
};

const categories: Array<{ value: CropCategory | 'all'; labelAr: string }> = [
  { value: 'all', labelAr: 'جميع الفئات' },
  { value: 'cereals', labelAr: 'حبوب' },
  { value: 'vegetables', labelAr: 'خضروات' },
  { value: 'fruits', labelAr: 'فواكه' },
  { value: 'legumes', labelAr: 'بقوليات' },
  { value: 'forage', labelAr: 'أعلاف' },
  { value: 'industrial', labelAr: 'صناعية' },
];

function getHealthColor(score: number): string {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-yellow-600';
  return 'text-red-600';
}

export default function CropsClient() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<CropCategory | 'all'>('all');

  const {
    data: crops = [],
    isLoading,
    error,
  } = useCrops(selectedCategory !== 'all' ? { category: selectedCategory } : undefined);
  const { data: stats } = useCropStats();

  const filteredCrops = useMemo(() => {
    if (!searchTerm) return crops;
    const term = searchTerm.toLowerCase();
    return crops.filter(
      (c) =>
        c.name.toLowerCase().includes(term) ||
        c.nameAr.includes(searchTerm) ||
        c.variety.toLowerCase().includes(term)
    );
  }, [crops, searchTerm]);

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
          <p className="text-red-600">فشل في تحميل بيانات المحاصيل</p>
          <p className="text-gray-500 text-sm">Failed to load crops data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المحاصيل</h1>
          <p className="text-gray-500 mt-1">Crop Management</p>
        </div>
        <button
          disabled
          title="قريباً - Coming soon"
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-4 h-4" />
          <span>إضافة محصول</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي المحاصيل</div>
          <div className="text-2xl font-bold text-gray-900">
            {stats?.totalCrops ?? crops.length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">المساحة الكلية</div>
          <div className="text-2xl font-bold text-blue-600">{stats?.totalAreaHa ?? 0} هـ</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">متوسط الصحة</div>
          <div className={`text-2xl font-bold ${getHealthColor(stats?.averageHealth ?? 0)}`}>
            {stats?.averageHealth ?? 0}%
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Leaf className="w-3.5 h-3.5" /> حبوب
          </div>
          <div className="text-2xl font-bold text-amber-600">{stats?.byCategory?.cereals ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Sun className="w-3.5 h-3.5" /> فواكه
          </div>
          <div className="text-2xl font-bold text-orange-600">{stats?.byCategory?.fruits ?? 0}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في المحاصيل..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value as CropCategory | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {categories.map((c) => (
            <option key={c.value} value={c.value}>
              {c.labelAr}
            </option>
          ))}
        </select>
      </div>

      {/* Crop Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredCrops.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">لا توجد محاصيل</div>
        ) : (
          filteredCrops.map((crop) => {
            const stage = stageConfig[crop.currentStage];
            return (
              <div
                key={crop.id}
                className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                      <Sprout className="w-5 h-5 text-sahool-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{crop.nameAr}</h3>
                      <p className="text-sm text-gray-500">
                        {crop.varietyAr} ({crop.variety})
                      </p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${stage.color}`}>
                    {stage.labelAr}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                  <div className="flex items-center gap-2 text-gray-600">
                    <span className="text-gray-400">الحقل:</span> {crop.fieldNameAr}
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <span className="text-gray-400">المساحة:</span> {crop.areaHa} هـ
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <span className="text-gray-400">الفئة:</span> {categoryLabels[crop.category]}
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Droplets className="w-3.5 h-3.5 text-blue-400" /> {crop.irrigationTypeAr}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t">
                  <div className="flex items-center gap-4 text-sm">
                    <span className={`font-semibold ${getHealthColor(crop.healthScore)}`}>
                      صحة: {crop.healthScore}%
                    </span>
                    {crop.ndvi !== undefined && (
                      <span className="text-gray-500">NDVI: {crop.ndvi.toFixed(2)}</span>
                    )}
                  </div>
                  <button
                    onClick={() => router.push(`/crops/${crop.id}`)}
                    className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                  >
                    تفاصيل
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
