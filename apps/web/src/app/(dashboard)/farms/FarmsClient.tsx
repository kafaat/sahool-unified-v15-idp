"use client";

import React, { useState, useMemo } from "react";
import { Building2, Plus, Search, MapPin, Droplets, Users, AlertTriangle, Loader2 } from "lucide-react";
import { useFarms, useFarmStats, useCreateFarm } from "@/features/farms";
import type { FarmStatus, FarmFormData } from "@/features/farms";
import { useToast } from "@/components/ui/toast";
import { Modal } from "@/components/ui/modal";

const statusConfig: Record<FarmStatus, { color: string; labelAr: string }> = {
  active: { color: "bg-green-100 text-green-800", labelAr: "نشطة" },
  inactive: { color: "bg-gray-100 text-gray-800", labelAr: "غير نشطة" },
  seasonal: { color: "bg-blue-100 text-blue-800", labelAr: "موسمية" },
};

export default function FarmsClient() {
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedFarmId, setSelectedFarmId] = useState<string | null>(null);
  const { data: farms = [], isLoading, error } = useFarms();
  const { data: stats } = useFarmStats();
  const createFarm = useCreateFarm();
  const { showToast } = useToast();

  const handleCreateFarm = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const data: FarmFormData = {
      name: formData.get("name") as string,
      nameAr: formData.get("nameAr") as string,
      location: formData.get("location") as string || "",
      locationAr: formData.get("locationAr") as string || "",
      region: formData.get("region") as string || "",
      regionAr: formData.get("regionAr") as string || "",
      totalAreaHa: Number(formData.get("totalAreaHa")) || 0,
      waterSource: formData.get("waterSource") as string || "",
      waterSourceAr: formData.get("waterSourceAr") as string || "",
    };
    try {
      await createFarm.mutateAsync(data);
      setShowAddModal(false);
      showToast({ type: "success", message: "Farm created successfully", messageAr: "تم إنشاء المزرعة بنجاح" });
    } catch {
      showToast({ type: "error", message: "Failed to create farm", messageAr: "فشل في إنشاء المزرعة" });
    }
  };

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المزارع</h1>
          <p className="text-gray-500 mt-1">Farm Management</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>إضافة مزرعة</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي المزارع</div>
          <div className="text-2xl font-bold text-gray-900">{stats?.totalFarms ?? farms.length}</div>
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
          <div className="text-2xl font-bold text-sahool-green-600">{stats?.cultivatedAreaHa ?? 0} هـ</div>
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
              <div key={farm.id} className="bg-white rounded-lg border hover:shadow-md transition-shadow">
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
                      <div className="text-lg font-bold text-sahool-green-600">{farm.cultivatedAreaHa}</div>
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
                    onClick={() => setSelectedFarmId(farm.id)}
                    className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                  >
                    عرض التفاصيل
                  </button>
                  <button
                    onClick={() => {
                      setSelectedFarmId(farm.id);
                      showToast({ type: "info", message: "View details to edit", messageAr: "اعرض التفاصيل للتعديل" });
                    }}
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
      {/* Farm Detail Panel */}
      {selectedFarmId && (() => {
        const farm = farms.find((f) => f.id === selectedFarmId);
        if (!farm) return null;
        return (
          <Modal isOpen onClose={() => setSelectedFarmId(null)} titleAr="تفاصيل المزرعة" title="Farm Details">
            <div className="p-6 space-y-4">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-sahool-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{farm.nameAr}</h3>
                  <p className="text-sm text-gray-500">{farm.name}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-gray-500">الموقع:</span> {farm.locationAr}</div>
                <div><span className="text-gray-500">المنطقة:</span> {farm.regionAr}</div>
                <div><span className="text-gray-500">المساحة:</span> {farm.totalAreaHa} هكتار</div>
                <div><span className="text-gray-500">مزروع:</span> {farm.cultivatedAreaHa} هكتار</div>
                <div><span className="text-gray-500">الحقول:</span> {farm.fieldsCount}</div>
                <div><span className="text-gray-500">العمال:</span> {farm.workersCount}</div>
                <div><span className="text-gray-500">مصدر المياه:</span> {farm.waterSourceAr}</div>
                <div><span className="text-gray-500">الحالة:</span> {statusConfig[farm.status].labelAr}</div>
              </div>
              <button onClick={() => setSelectedFarmId(null)} className="w-full mt-4 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
                إغلاق
              </button>
            </div>
          </Modal>
        );
      })()}

      {/* Add Farm Modal */}
      <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} titleAr="إضافة مزرعة" title="Add Farm">
        <form onSubmit={handleCreateFarm} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">اسم المزرعة (عربي) *</label>
              <input name="nameAr" required className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="مزرعة..." />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Farm Name (EN) *</label>
              <input name="name" required className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="Farm..." />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الموقع (عربي)</label>
              <input name="locationAr" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location (EN)</label>
              <input name="location" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المنطقة (عربي)</label>
              <input name="regionAr" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Region (EN)</label>
              <input name="region" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المساحة (هكتار) *</label>
              <input name="totalAreaHa" type="number" step="0.01" min="0.01" required className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">مصدر المياه (عربي)</label>
              <input name="waterSourceAr" className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
            </div>
          </div>
          <input type="hidden" name="waterSource" value="" />
          <div className="flex gap-3 justify-end pt-4 border-t">
            <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">إلغاء</button>
            <button type="submit" disabled={createFarm.isPending} className="px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 disabled:opacity-50 flex items-center gap-2">
              {createFarm.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              إضافة المزرعة
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
