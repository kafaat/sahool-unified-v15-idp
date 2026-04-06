'use client';

import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Search,
  Sprout,
  Sun,
  Star,
  Calendar,
  MapPin,
  Package,
  AlertTriangle,
  Loader2,
} from 'lucide-react';
import { seedsApi } from '@/features/seeds/api';
import type { Seed } from '@/features/seeds/api';

type CropCategory = 'cereals' | 'vegetables' | 'fruits' | 'legumes' | 'fodder';
type DroughtTolerance = 'high' | 'medium' | 'low';



export default function SeedsClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<CropCategory | 'all'>('all');
  const [recommendedOnly, setRecommendedOnly] = useState(false);

  const { data: seeds, isLoading, error } = useQuery({
    queryKey: ['seeds', categoryFilter !== 'all' ? categoryFilter : undefined],
    queryFn: () => seedsApi.getSeeds(categoryFilter !== 'all' ? categoryFilter : undefined),
    staleTime: 1000 * 60 * 5,
  });

  const filteredSeeds = useMemo(() => {
    if (!seeds) return [];
    return seeds.filter((seed: Seed) => {
      const matchesSearch =
        !searchTerm ||
        (seed.nameAr ?? '').includes(searchTerm) ||
        (seed.cropType ?? '').includes(searchTerm) ||
        seed.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRecommended = !recommendedOnly || seed.available;
      return matchesSearch && matchesRecommended;
    });
  }, [seeds, searchTerm, recommendedOnly]);

  const getToleranceBadge = (tolerance: DroughtTolerance) => {
    const styles: Record<DroughtTolerance, string> = {
      high: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-red-100 text-red-800',
    };
    const labels: Record<DroughtTolerance, string> = { high: 'عالية', medium: 'متوسطة', low: 'منخفضة' };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[tolerance]}`}>
        {labels[tolerance]}
      </span>
    );
  };

  const allSeeds = seeds ?? [];
  const availableCount = allSeeds.filter((s: Seed) => s.available).length;
  const highDroughtCount = allSeeds.filter((s: Seed) => s.droughtTolerance === 'high').length;

  if (error) {
    return (
      <div className="space-y-6" dir="rtl">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-700 font-medium">فشل في تحميل كتالوج البذور</p>
          <p className="text-red-500 text-sm mt-1">Failed to load seed catalog</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">كتالوج البذور</h1>
          <p className="text-gray-500 mt-1">Seed Catalog</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Sprout className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الأصناف</div>
              <div className="text-xl font-bold text-gray-900">{isLoading ? '...' : allSeeds.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Star className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متوفرة</div>
              <div className="text-xl font-bold text-yellow-600">
                {isLoading ? '...' : availableCount}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متوسط سعر الكيلو</div>
              <div className="text-xl font-bold text-blue-600">
                {isLoading ? '...' : allSeeds.length > 0
                  ? (allSeeds.reduce((s: number, v: Seed) => s + v.pricePerKg, 0) / allSeeds.length).toFixed(0)
                  : 0} ريال
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Sun className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">مقاوم للجفاف</div>
              <div className="text-xl font-bold text-purple-600">
                {isLoading ? '...' : highDroughtCount}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث عن صنف بذور..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value as CropCategory | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع الفئات</option>
          <option value="cereals">حبوب</option>
          <option value="vegetables">خضروات</option>
          <option value="fruits">فواكه</option>
          <option value="legumes">بقوليات</option>
          <option value="fodder">أعلاف</option>
        </select>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={recommendedOnly}
            onChange={(e) => setRecommendedOnly(e.target.checked)}
            className="rounded border-gray-300 text-green-600 focus:ring-green-500"
          />
          <span className="text-gray-700">الموصى بها فقط</span>
        </label>
      </div>

      {/* Seeds Grid */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-green-600" />
          <span className="mr-2 text-gray-500">جاري التحميل...</span>
        </div>
      )}
      {!isLoading && filteredSeeds.length === 0 && (
        <div className="bg-white rounded-lg border p-10 text-center text-gray-500">
          لا توجد بذور مطابقة للبحث
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSeeds.map((seed: Seed) => (
          <div key={seed.id} className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow relative">
            {seed.available && (
              <div className="absolute top-3 left-3 flex items-center gap-1 px-2 py-0.5 bg-yellow-50 text-yellow-700 rounded text-xs font-medium">
                <Star className="w-3 h-3" />
                متوفر
              </div>
            )}
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                  {seed.cropType}
                </span>
              </div>
              <h3 className="font-bold text-gray-900 text-lg">{seed.nameAr}</h3>
              <p className="text-sm text-gray-500">{seed.variety} - {seed.name}</p>
            </div>

            <div className="space-y-2 text-sm mb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Calendar className="w-4 h-4" />
                  <span>فترة النضج</span>
                </div>
                <span className="font-medium">{seed.maturityDays} يوم</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Sprout className="w-4 h-4" />
                  <span>معدل الإنبات</span>
                </div>
                <span className="font-medium">{seed.germinationRate}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500">تحمل الجفاف</span>
                {getToleranceBadge(seed.droughtTolerance)}
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <MapPin className="w-4 h-4" />
                  <span>المنشأ</span>
                </div>
                <span className="font-medium">{seed.origin}</span>
              </div>
              {seed.recommendedRegions.length > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-500">المناطق</span>
                  <span className="font-medium text-xs">{seed.recommendedRegions.join(', ')}</span>
                </div>
              )}
            </div>

            <div className="pt-3 border-t flex justify-between items-center">
              <div className="text-sm">
                <span className="text-gray-500">الحالة: </span>
                <span className={`font-medium ${seed.available ? 'text-green-600' : 'text-red-600'}`}>
                  {seed.available ? 'متوفر' : 'غير متوفر'}
                </span>
              </div>
              <span className="font-bold text-green-700">{seed.pricePerKg} ريال/كجم</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
