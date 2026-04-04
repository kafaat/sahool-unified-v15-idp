'use client';

import React, { useState, useMemo } from 'react';
import {
  Search,
  Sprout,
  Droplets,
  Thermometer,
  Sun,
  Star,
  Calendar,
  MapPin,
  Package,
  AlertTriangle,
} from 'lucide-react';

type CropCategory = 'cereals' | 'vegetables' | 'fruits' | 'legumes' | 'fodder';
type DroughtTolerance = 'high' | 'medium' | 'low';

interface SeedVariety {
  id: string;
  name: string;
  nameAr: string;
  crop: string;
  cropAr: string;
  category: CropCategory;
  maturityDays: number;
  yieldPotential: string;
  yieldPotentialAr: string;
  droughtTolerance: DroughtTolerance;
  optimalTempMin: number;
  optimalTempMax: number;
  waterRequirement: string;
  waterRequirementAr: string;
  plantingSeason: string;
  plantingSeasonAr: string;
  region: string;
  regionAr: string;
  rating: number;
  stockKg: number;
  pricePerKg: number;
  recommended: boolean;
}

const mockSeeds: SeedVariety[] = [
  {
    id: 'seed-001',
    name: 'Sakha 95',
    nameAr: 'سخا 95',
    crop: 'Wheat',
    cropAr: 'القمح',
    category: 'cereals',
    maturityDays: 145,
    yieldPotential: '6.5 t/ha',
    yieldPotentialAr: '6.5 طن/هـ',
    droughtTolerance: 'medium',
    optimalTempMin: 15,
    optimalTempMax: 25,
    waterRequirement: '450-650 mm',
    waterRequirementAr: '450-650 مم',
    plantingSeason: 'Nov - Dec',
    plantingSeasonAr: 'نوفمبر - ديسمبر',
    region: 'Arabian Peninsula',
    regionAr: 'شبه الجزيرة العربية',
    rating: 4.5,
    stockKg: 2500,
    pricePerKg: 12,
    recommended: true,
  },
  {
    id: 'seed-002',
    name: 'Barhi',
    nameAr: 'برحي',
    crop: 'Date Palm',
    cropAr: 'نخيل التمر',
    category: 'fruits',
    maturityDays: 180,
    yieldPotential: '120 kg/tree',
    yieldPotentialAr: '120 كجم/شجرة',
    droughtTolerance: 'high',
    optimalTempMin: 25,
    optimalTempMax: 45,
    waterRequirement: '200-300 L/day',
    waterRequirementAr: '200-300 لتر/يوم',
    plantingSeason: 'Feb - Mar',
    plantingSeasonAr: 'فبراير - مارس',
    region: 'Gulf Region',
    regionAr: 'منطقة الخليج',
    rating: 4.8,
    stockKg: 500,
    pricePerKg: 85,
    recommended: true,
  },
  {
    id: 'seed-003',
    name: 'GS-12',
    nameAr: 'جي إس-12',
    crop: 'Tomato',
    cropAr: 'الطماطم',
    category: 'vegetables',
    maturityDays: 75,
    yieldPotential: '80 t/ha',
    yieldPotentialAr: '80 طن/هـ',
    droughtTolerance: 'low',
    optimalTempMin: 20,
    optimalTempMax: 30,
    waterRequirement: '600-800 mm',
    waterRequirementAr: '600-800 مم',
    plantingSeason: 'Sep - Oct',
    plantingSeasonAr: 'سبتمبر - أكتوبر',
    region: 'Greenhouse',
    regionAr: 'الصوب الزراعية',
    rating: 4.2,
    stockKg: 120,
    pricePerKg: 350,
    recommended: false,
  },
  {
    id: 'seed-004',
    name: 'Giza 843',
    nameAr: 'جيزة 843',
    crop: 'Faba Bean',
    cropAr: 'الفول',
    category: 'legumes',
    maturityDays: 130,
    yieldPotential: '3.5 t/ha',
    yieldPotentialAr: '3.5 طن/هـ',
    droughtTolerance: 'medium',
    optimalTempMin: 12,
    optimalTempMax: 22,
    waterRequirement: '300-500 mm',
    waterRequirementAr: '300-500 مم',
    plantingSeason: 'Oct - Nov',
    plantingSeasonAr: 'أكتوبر - نوفمبر',
    region: 'Nile Valley',
    regionAr: 'وادي النيل',
    rating: 3.9,
    stockKg: 800,
    pricePerKg: 18,
    recommended: false,
  },
  {
    id: 'seed-005',
    name: 'Hail Barley',
    nameAr: 'شعير حائل',
    crop: 'Barley',
    cropAr: 'الشعير',
    category: 'cereals',
    maturityDays: 110,
    yieldPotential: '4.5 t/ha',
    yieldPotentialAr: '4.5 طن/هـ',
    droughtTolerance: 'high',
    optimalTempMin: 10,
    optimalTempMax: 25,
    waterRequirement: '350-500 mm',
    waterRequirementAr: '350-500 مم',
    plantingSeason: 'Nov - Dec',
    plantingSeasonAr: 'نوفمبر - ديسمبر',
    region: 'Northern Arabia',
    regionAr: 'شمال الجزيرة',
    rating: 4.3,
    stockKg: 1800,
    pricePerKg: 9,
    recommended: true,
  },
  {
    id: 'seed-006',
    name: 'Rhodes Grass',
    nameAr: 'حشيشة رودس',
    crop: 'Fodder',
    cropAr: 'علف',
    category: 'fodder',
    maturityDays: 60,
    yieldPotential: '15 t/ha/cut',
    yieldPotentialAr: '15 طن/هـ/حشة',
    droughtTolerance: 'high',
    optimalTempMin: 20,
    optimalTempMax: 40,
    waterRequirement: '500-700 mm',
    waterRequirementAr: '500-700 مم',
    plantingSeason: 'Mar - Apr',
    plantingSeasonAr: 'مارس - أبريل',
    region: 'Arabian Peninsula',
    regionAr: 'شبه الجزيرة العربية',
    rating: 4.0,
    stockKg: 3000,
    pricePerKg: 6,
    recommended: false,
  },
];

const categoryLabels: Record<CropCategory, string> = {
  cereals: 'حبوب',
  vegetables: 'خضروات',
  fruits: 'فواكه',
  legumes: 'بقوليات',
  fodder: 'أعلاف',
};

export default function SeedsClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<CropCategory | 'all'>('all');
  const [recommendedOnly, setRecommendedOnly] = useState(false);

  const filteredSeeds = useMemo(() => {
    return mockSeeds.filter((seed) => {
      const matchesSearch =
        !searchTerm ||
        seed.nameAr.includes(searchTerm) ||
        seed.cropAr.includes(searchTerm) ||
        seed.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = categoryFilter === 'all' || seed.category === categoryFilter;
      const matchesRecommended = !recommendedOnly || seed.recommended;
      return matchesSearch && matchesCategory && matchesRecommended;
    });
  }, [searchTerm, categoryFilter, recommendedOnly]);

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

  const lowStockCount = mockSeeds.filter((s) => s.stockKg < 200).length;

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">كتالوج البذور</h1>
          <p className="text-gray-500 mt-1">Seed Catalog</p>
        </div>
      </div>

      {/* Low stock alert */}
      {lowStockCount > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span className="font-medium text-amber-800">
              {lowStockCount} صنف مخزونه منخفض ويحتاج إعادة طلب
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Sprout className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الأصناف</div>
              <div className="text-xl font-bold text-gray-900">{mockSeeds.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Star className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">موصى بها</div>
              <div className="text-xl font-bold text-yellow-600">
                {mockSeeds.filter((s) => s.recommended).length}
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
              <div className="text-sm text-gray-500">إجمالي المخزون</div>
              <div className="text-xl font-bold text-blue-600">
                {(mockSeeds.reduce((s, v) => s + v.stockKg, 0) / 1000).toFixed(1)} طن
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
                {mockSeeds.filter((s) => s.droughtTolerance === 'high').length}
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSeeds.map((seed) => (
          <div key={seed.id} className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow relative">
            {seed.recommended && (
              <div className="absolute top-3 left-3 flex items-center gap-1 px-2 py-0.5 bg-yellow-50 text-yellow-700 rounded text-xs font-medium">
                <Star className="w-3 h-3" />
                موصى به
              </div>
            )}
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                  {categoryLabels[seed.category]}
                </span>
              </div>
              <h3 className="font-bold text-gray-900 text-lg">{seed.nameAr}</h3>
              <p className="text-sm text-gray-500">{seed.cropAr} - {seed.name}</p>
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
                  <span>الإنتاجية</span>
                </div>
                <span className="font-medium">{seed.yieldPotentialAr}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Droplets className="w-4 h-4" />
                  <span>احتياج مائي</span>
                </div>
                <span className="font-medium">{seed.waterRequirementAr}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <Thermometer className="w-4 h-4" />
                  <span>الحرارة المثلى</span>
                </div>
                <span className="font-medium">{seed.optimalTempMin}-{seed.optimalTempMax}°C</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500">تحمل الجفاف</span>
                {getToleranceBadge(seed.droughtTolerance)}
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-500">
                  <MapPin className="w-4 h-4" />
                  <span>المنطقة</span>
                </div>
                <span className="font-medium">{seed.regionAr}</span>
              </div>
            </div>

            <div className="pt-3 border-t flex justify-between items-center">
              <div className="text-sm">
                <span className="text-gray-500">المخزون: </span>
                <span className={`font-medium ${seed.stockKg < 200 ? 'text-red-600' : 'text-gray-900'}`}>
                  {seed.stockKg} كجم
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
