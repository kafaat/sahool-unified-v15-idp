'use client';

import React, { useState, useMemo } from 'react';
import { Sprout, Plus, Search, AlertTriangle, Leaf, Sun, Droplets, ChevronDown, ChevronUp, X } from 'lucide-react';
import { useCrops, useCropStats, useCreateCrop } from '@/features/crops';
import type { CropCategory, CropStage, CropFormData } from '@/features/crops';

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
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<CropCategory | 'all'>('all');
  const [expandedCropId, setExpandedCropId] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newCrop, setNewCrop] = useState<Omit<CropFormData, 'expectedHarvestDate' | 'irrigationType' | 'irrigationTypeAr'>>({ name: '', nameAr: '', variety: '', varietyAr: '', category: 'cereals' as CropCategory, fieldId: '', plantingDate: '', areaHa: 0 });

  const {
    data: crops = [],
    isLoading,
    error,
  } = useCrops(selectedCategory !== 'all' ? { category: selectedCategory } : undefined);
  const { data: stats } = useCropStats();
  const createCrop = useCreateCrop();

  const handleCreateCrop = () => {
    // Basic required-field guard — backend CropFormData expects these populated
    if (
      !newCrop.name.trim() ||
      !newCrop.nameAr.trim() ||
      !newCrop.fieldId.trim() ||
      !newCrop.plantingDate ||
      newCrop.areaHa <= 0
    ) {
      return;
    }
    createCrop.mutate(
      { ...newCrop, expectedHarvestDate: '', irrigationType: '', irrigationTypeAr: '' },
      {
        onSuccess: () => {
          setShowCreateDialog(false);
          setNewCrop({ name: '', nameAr: '', variety: '', varietyAr: '', category: 'cereals', fieldId: '', plantingDate: '', areaHa: 0 });
        },
      }
    );
  };

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
      {/* Create Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative max-h-[90vh] overflow-y-auto">
            <button onClick={() => setShowCreateDialog(false)} className="absolute top-3 left-3 text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-bold text-gray-900 mb-4">إضافة محصول جديد</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">اسم المحصول (EN)</label>
                <input value={newCrop.name} onChange={(e) => setNewCrop({ ...newCrop, name: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">اسم المحصول (AR)</label>
                <input value={newCrop.nameAr} onChange={(e) => setNewCrop({ ...newCrop, nameAr: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" dir="rtl" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الصنف (EN)</label>
                <input value={newCrop.variety} onChange={(e) => setNewCrop({ ...newCrop, variety: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الصنف (AR)</label>
                <input value={newCrop.varietyAr} onChange={(e) => setNewCrop({ ...newCrop, varietyAr: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" dir="rtl" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الفئة</label>
                <select value={newCrop.category} onChange={(e) => setNewCrop({ ...newCrop, category: e.target.value as CropCategory })} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500">
                  {categories.filter((c) => c.value !== 'all').map((c) => (
                    <option key={c.value} value={c.value}>{c.labelAr}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">معرّف الحقل</label>
                <input value={newCrop.fieldId} onChange={(e) => setNewCrop({ ...newCrop, fieldId: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="FIELD-001" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">المساحة (هكتار)</label>
                <input type="number" min={0} value={newCrop.areaHa} onChange={(e) => setNewCrop({ ...newCrop, areaHa: Number(e.target.value) })} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الزراعة</label>
                <input type="date" value={newCrop.plantingDate} onChange={(e) => setNewCrop({ ...newCrop, plantingDate: e.target.value })} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowCreateDialog(false)} className="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50">إلغاء</button>
              <button onClick={handleCreateCrop} disabled={createCrop.isPending || !newCrop.name.trim() || !newCrop.nameAr.trim() || !newCrop.fieldId.trim() || !newCrop.plantingDate || newCrop.areaHa <= 0} className="px-4 py-2 text-sm text-white bg-sahool-green-600 rounded-lg hover:bg-sahool-green-700 disabled:opacity-50">
                {createCrop.isPending ? 'جاري الإنشاء...' : 'إنشاء'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المحاصيل</h1>
          <p className="text-gray-500 mt-1">Crop Management</p>
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors"
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
                    onClick={() => setExpandedCropId(expandedCropId === crop.id ? null : crop.id)}
                    className="flex items-center gap-1 text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                  >
                    تفاصيل
                    {expandedCropId === crop.id ? (
                      <ChevronUp className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>

                {expandedCropId === crop.id && (
                  <div className="mt-3 pt-3 border-t text-sm text-gray-600 space-y-1">
                    <p><span className="text-gray-400">المحصول:</span> {crop.nameAr} ({crop.varietyAr})</p>
                    <p><span className="text-gray-400">الحقل:</span> {crop.fieldNameAr}</p>
                    <p><span className="text-gray-400">المرحلة:</span> {stageConfig[crop.currentStage].labelAr}</p>
                    <p><span className="text-gray-400">الصحة:</span> {crop.healthScore}%</p>
                    {crop.ndvi !== undefined && (
                      <p><span className="text-gray-400">NDVI:</span> {crop.ndvi.toFixed(2)}</p>
                    )}
                    <p><span className="text-gray-400">المساحة:</span> {crop.areaHa} هـ</p>
                    <p><span className="text-gray-400">الري:</span> {crop.irrigationTypeAr}</p>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
