"use client";

import React, { useState, useMemo } from "react";
import { Satellite, MapPin, Layers, TrendingUp, Download, AlertTriangle } from "lucide-react";
import { useSatelliteFields, useSatelliteStats } from "@/features/satellite";
import type { SatelliteField, IndexType } from "@/features/satellite";

const indexTypes: Array<{ value: IndexType; label: string; labelAr: string }> = [
  { value: "ndvi", label: "NDVI", labelAr: "مؤشر الغطاء النباتي" },
  { value: "ndwi", label: "NDWI", labelAr: "مؤشر المياه" },
  { value: "evi", label: "EVI", labelAr: "مؤشر الغطاء المحسن" },
  { value: "savi", label: "SAVI", labelAr: "مؤشر الغطاء المعدل للتربة" },
  { value: "ndre", label: "NDRE", labelAr: "مؤشر الحافة الحمراء" },
  { value: "lai", label: "LAI", labelAr: "مؤشر مساحة الأوراق" },
];

export default function SatelliteClient() {
  const [selectedIndex, setSelectedIndex] = useState<IndexType>("ndvi");
  const [selectedField, setSelectedField] = useState<string | null>(null);

  // Fetch data using React Query hooks
  const { data: fields = [], isLoading, error } = useSatelliteFields();
  const { data: stats } = useSatelliteStats();

  const getHealthColor = (status: SatelliteField["healthStatus"]) => {
    const colors: Record<SatelliteField["healthStatus"], string> = {
      excellent: "text-green-700 bg-green-100",
      good: "text-green-600 bg-green-50",
      moderate: "text-yellow-600 bg-yellow-100",
      poor: "text-orange-600 bg-orange-100",
      critical: "text-red-600 bg-red-100",
    };
    return colors[status];
  };

  const getHealthLabel = (status: SatelliteField["healthStatus"]) => {
    const labels: Record<SatelliteField["healthStatus"], string> = {
      excellent: "ممتاز",
      good: "جيد",
      moderate: "متوسط",
      poor: "ضعيف",
      critical: "حرج",
    };
    return labels[status];
  };

  const avgNdvi = useMemo(() => {
    if (fields.length === 0) return "0.00";
    return (fields.reduce((acc, f) => acc + f.indices.ndvi, 0) / fields.length).toFixed(2);
  }, [fields]);

  const totalArea = useMemo(() => {
    return fields.reduce((acc, f) => acc + f.area, 0).toFixed(1);
  }, [fields]);

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
          <p className="text-red-600">فشل في تحميل بيانات الأقمار الصناعية</p>
          <p className="text-gray-500 text-sm">Failed to load satellite data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تحليل الأقمار الصناعية</h1>
          <p className="text-gray-500 mt-1">Satellite Imagery & Vegetation Analysis</p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedIndex}
            onChange={(e) => setSelectedIndex(e.target.value as IndexType)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          >
            {indexTypes.map((idx) => (
              <option key={idx.value} value={idx.value}>
                {idx.labelAr} ({idx.label})
              </option>
            ))}
          </select>
          <button className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors">
            <Download className="w-4 h-4" />
            <span>تصدير</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Satellite className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">آخر التقاط</div>
              <div className="text-lg font-bold text-gray-900">{stats?.lastCapture ?? "2026-01-24"}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متوسط NDVI</div>
              <div className="text-lg font-bold text-green-600">{stats?.averageNdvi?.toFixed(2) ?? avgNdvi}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <MapPin className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">الحقول المراقبة</div>
              <div className="text-lg font-bold text-purple-600">{stats?.totalFields ?? fields.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
              <Layers className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">المساحة الكلية</div>
              <div className="text-lg font-bold text-amber-600">
                {stats?.totalArea?.toFixed(1) ?? totalArea} هـ
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Placeholder */}
        <div className="lg:col-span-2 bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">خريطة الأقمار الصناعية</h2>
          </div>
          <div className="aspect-video bg-gradient-to-br from-green-200 via-green-300 to-green-400 flex items-center justify-center">
            <div className="text-center">
              <Satellite className="w-16 h-16 text-green-700 mx-auto mb-4" />
              <p className="text-green-800 font-medium">خريطة تفاعلية للأقمار الصناعية</p>
              <p className="text-green-700 text-sm">Sentinel-2 / Landsat-8</p>
            </div>
          </div>
          <div className="p-4 flex justify-between items-center text-sm">
            <span className="text-gray-500">المصدر: Sentinel-2 L2A</span>
            <div className="flex gap-3 flex-wrap">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span>&lt; 0.15</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-orange-500" />
                <span>0.15 - 0.3</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <span>0.3 - 0.5</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-green-400" />
                <span>0.5 - 0.7</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-green-600" />
                <span>&gt; 0.7</span>
              </div>
            </div>
          </div>
        </div>

        {/* Fields List */}
        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">الحقول</h2>
          </div>
          <div className="divide-y max-h-[500px] overflow-y-auto">
            {fields.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                لا توجد حقول مراقبة
              </div>
            ) : (
              fields.map((field) => (
                <div
                  key={field.id}
                  className={`p-4 cursor-pointer transition-colors ${
                    selectedField === field.id ? "bg-sahool-green-50" : "hover:bg-gray-50"
                  }`}
                  onClick={() => setSelectedField(field.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-medium text-gray-900">{field.fieldNameAr}</h3>
                      <p className="text-sm text-gray-500">{field.fieldName}</p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getHealthColor(field.healthStatus)}`}>
                      {getHealthLabel(field.healthStatus)}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500">NDVI:</span>
                      <span className="font-medium mr-1">{field.indices.ndvi.toFixed(2)}</span>
                      <span className={field.indices.ndviChange >= 0 ? "text-green-600" : "text-red-600"}>
                        ({field.indices.ndviChange >= 0 ? "+" : ""}{field.indices.ndviChange.toFixed(2)})
                      </span>
                    </div>
                    <div className="text-gray-500">
                      {field.area} هكتار
                    </div>
                  </div>

                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          field.indices.ndvi >= 0.7 ? "bg-green-600" : field.indices.ndvi >= 0.5 ? "bg-green-400" : field.indices.ndvi >= 0.3 ? "bg-yellow-500" : field.indices.ndvi >= 0.15 ? "bg-orange-500" : "bg-red-500"
                        }`}
                        style={{ width: `${Math.max(field.indices.ndvi, 0) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
