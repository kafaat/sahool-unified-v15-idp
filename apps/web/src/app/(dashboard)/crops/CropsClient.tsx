"use client";

import React, { useState, useMemo } from "react";
import { Sprout, Plus, Search, AlertTriangle, Leaf, Sun, Droplets, Loader2 } from "lucide-react";
import { useCrops, useCropStats, useCreateCrop } from "@/features/crops";
import type { CropCategory, CropStage, CropFormData } from "@/features/crops";
import { useToast } from "@/components/ui/toast";
import { Modal } from "@/components/ui/modal";

const categoryLabels: Record<CropCategory, string> = {
  cereals: "حبوب",
  vegetables: "خضروات",
  fruits: "فواكه",
  legumes: "بقوليات",
  forage: "أعلاف",
  industrial: "صناعية",
};

const stageConfig: Record<CropStage, { color: string; labelAr: string }> = {
  germination: { color: "bg-amber-100 text-amber-800", labelAr: "إنبات" },
  seedling: { color: "bg-lime-100 text-lime-800", labelAr: "بادرة" },
  vegetative: { color: "bg-green-100 text-green-800", labelAr: "نمو خضري" },
  flowering: { color: "bg-pink-100 text-pink-800", labelAr: "إزهار" },
  fruiting: { color: "bg-orange-100 text-orange-800", labelAr: "إثمار" },
  maturity: { color: "bg-yellow-100 text-yellow-800", labelAr: "نضج" },
  harvest: { color: "bg-red-100 text-red-800", labelAr: "حصاد" },
};

const categories: Array<{ value: CropCategory | "all"; labelAr: string }> = [
  { value: "all", labelAr: "جميع الفئات" },
  { value: "cereals", labelAr: "حبوب" },
  { value: "vegetables", labelAr: "خضروات" },
  { value: "fruits", labelAr: "فواكه" },
  { value: "legumes", labelAr: "بقوليات" },
  { value: "forage", labelAr: "أعلاف" },
  { value: "industrial", labelAr: "صناعية" },
];

function getHealthColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-yellow-600";
  return "text-red-600";
}

export default function CropsClient() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<CropCategory | "all">("all");
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedCropId, setSelectedCropId] = useState<string | null>(null);

  const { data: crops = [], isLoading, error } = useCrops(
    selectedCategory !== "all" ? { category: selectedCategory } : undefined
  );
  const { data: stats } = useCropStats();
  const createCrop = useCreateCrop();
  const { showToast } = useToast();

  const handleCreateCrop = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const data: CropFormData = {
      name: fd.get("name") as string,
      nameAr: fd.get("nameAr") as string,
      variety: fd.get("variety") as string || "",
      varietyAr: fd.get("varietyAr") as string || "",
      category: fd.get("category") as CropCategory,
      fieldId: fd.get("fieldId") as string || "",
      plantingDate: fd.get("plantingDate") as string || "",
      expectedHarvestDate: fd.get("expectedHarvestDate") as string || "",
      areaHa: Number(fd.get("areaHa")) || 0,
      irrigationType: fd.get("irrigationType") as string || "",
      irrigationTypeAr: fd.get("irrigationTypeAr") as string || "",
    };
    try {
      await createCrop.mutateAsync(data);
      setShowAddModal(false);
      showToast({ type: "success", message: "Crop added successfully", messageAr: "تم إضافة المحصول بنجاح" });
    } catch {
      showToast({ type: "error", message: "Failed to add crop", messageAr: "فشل في إضافة المحصول" });
    }
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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المحاصيل</h1>
          <p className="text-gray-500 mt-1">Crop Management</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
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
          <div className="text-2xl font-bold text-gray-900">{stats?.totalCrops ?? crops.length}</div>
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
          onChange={(e) => setSelectedCategory(e.target.value as CropCategory | "all")}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {categories.map((c) => (
            <option key={c.value} value={c.value}>{c.labelAr}</option>
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
              <div key={crop.id} className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                      <Sprout className="w-5 h-5 text-sahool-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{crop.nameAr}</h3>
                      <p className="text-sm text-gray-500">{crop.varietyAr} ({crop.variety})</p>
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
                    onClick={() => setSelectedCropId(crop.id)}
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
      {/* Crop Detail Modal */}
      {selectedCropId && (() => {
        const crop = crops.find((c) => c.id === selectedCropId);
        if (!crop) return null;
        const stage = stageConfig[crop.currentStage];
        return (
          <Modal isOpen onClose={() => setSelectedCropId(null)} titleAr="تفاصيل المحصول" title="Crop Details">
            <div className="p-6 space-y-4">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                  <Sprout className="w-6 h-6 text-sahool-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{crop.nameAr}</h3>
                  <p className="text-sm text-gray-500">{crop.name} - {crop.variety}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${stage.color}`}>{stage.labelAr}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-gray-500">الصنف:</span> {crop.varietyAr}</div>
                <div><span className="text-gray-500">الفئة:</span> {categoryLabels[crop.category]}</div>
                <div><span className="text-gray-500">الحقل:</span> {crop.fieldNameAr}</div>
                <div><span className="text-gray-500">المساحة:</span> {crop.areaHa} هكتار</div>
                <div><span className="text-gray-500">الري:</span> {crop.irrigationTypeAr}</div>
                <div className={getHealthColor(crop.healthScore)}><span className="text-gray-500">الصحة:</span> {crop.healthScore}%</div>
                {crop.ndvi !== undefined && <div><span className="text-gray-500">NDVI:</span> {crop.ndvi.toFixed(2)}</div>}
                <div><span className="text-gray-500">الزراعة:</span> {crop.plantingDate ? new Date(crop.plantingDate).toLocaleDateString("ar-SA") : "غير محدد"}</div>
              </div>
              <button onClick={() => setSelectedCropId(null)} className="w-full mt-4 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">إغلاق</button>
            </div>
          </Modal>
        );
      })()}

      {/* Add Crop Modal */}
      <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} titleAr="إضافة محصول" title="Add Crop">
        <form onSubmit={handleCreateCrop} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">اسم المحصول (عربي) *</label>
              <input name="nameAr" required className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Crop Name (EN) *</label>
              <input name="name" required className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الصنف (عربي)</label>
              <input name="varietyAr" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Variety (EN)</label>
              <input name="variety" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الفئة *</label>
              <select name="category" required className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500">
                {categories.filter(c => c.value !== "all").map(c => (
                  <option key={c.value} value={c.value}>{c.labelAr}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المساحة (هكتار) *</label>
              <input name="areaHa" type="number" step="0.01" min="0.01" required className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الزراعة</label>
              <input name="plantingDate" type="date" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">موعد الحصاد المتوقع</label>
              <input name="expectedHarvestDate" type="date" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
          </div>
          <input type="hidden" name="fieldId" value="" />
          <input type="hidden" name="irrigationType" value="" />
          <input type="hidden" name="irrigationTypeAr" value="" />
          <div className="flex gap-3 justify-end pt-4 border-t">
            <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">إلغاء</button>
            <button type="submit" disabled={createCrop.isPending} className="px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 disabled:opacity-50 flex items-center gap-2">
              {createCrop.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              إضافة المحصول
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
