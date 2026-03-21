"use client";

import React, { useState, useMemo } from "react";
import {
  TrendingUp,
  Search,
  BarChart3,
  Wheat,
  Calendar,
  Target,
} from "lucide-react";

interface YieldRecord {
  id: string;
  fieldId: string;
  fieldName: string;
  cropType: string;
  cropTypeAr: string;
  season: string;
  seasonAr: string;
  expectedYield: number;
  actualYield?: number;
  unit: string;
  harvestDate?: string;
  status: "growing" | "harvested" | "predicted";
}

const mockYields: YieldRecord[] = [
  {
    id: "1",
    fieldId: "field-1",
    fieldName: "الحقل الشمالي",
    cropType: "Wheat",
    cropTypeAr: "قمح",
    season: "Winter 2024-25",
    seasonAr: "شتاء 2024-25",
    expectedYield: 4.5,
    actualYield: 4.8,
    unit: "طن/هكتار",
    harvestDate: "2025-01-15",
    status: "harvested",
  },
  {
    id: "2",
    fieldId: "field-2",
    fieldName: "الحقل الجنوبي",
    cropType: "Barley",
    cropTypeAr: "شعير",
    season: "Winter 2024-25",
    seasonAr: "شتاء 2024-25",
    expectedYield: 3.8,
    unit: "طن/هكتار",
    status: "growing",
  },
  {
    id: "3",
    fieldId: "field-3",
    fieldName: "حقل القمح",
    cropType: "Wheat",
    cropTypeAr: "قمح",
    season: "Winter 2024-25",
    seasonAr: "شتاء 2024-25",
    expectedYield: 5.2,
    unit: "طن/هكتار",
    status: "predicted",
  },
  {
    id: "4",
    fieldId: "field-4",
    fieldName: "بستان النخيل",
    cropType: "Date Palm",
    cropTypeAr: "نخيل",
    season: "2024",
    seasonAr: "2024",
    expectedYield: 80,
    actualYield: 85,
    unit: "كجم/شجرة",
    harvestDate: "2024-10-20",
    status: "harvested",
  },
  {
    id: "5",
    fieldId: "field-5",
    fieldName: "الصوب الزراعية",
    cropType: "Tomato",
    cropTypeAr: "طماطم",
    season: "Winter 2024-25",
    seasonAr: "شتاء 2024-25",
    expectedYield: 120,
    unit: "طن/هكتار",
    status: "growing",
  },
];

export default function YieldClient() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filteredYields = useMemo(() => {
    return mockYields.filter((record) => {
      const matchesSearch =
        !searchTerm ||
        record.fieldName.includes(searchTerm) ||
        record.cropTypeAr.includes(searchTerm);
      const matchesStatus = statusFilter === "all" || record.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [searchTerm, statusFilter]);

  const getStatusBadge = (status: YieldRecord["status"]) => {
    const styles = {
      growing: "bg-green-100 text-green-800",
      harvested: "bg-blue-100 text-blue-800",
      predicted: "bg-yellow-100 text-yellow-800",
    };
    const labels = {
      growing: "ينمو",
      harvested: "تم الحصاد",
      predicted: "متوقع",
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const getYieldComparison = (expected: number, actual?: number) => {
    if (!actual) return null;
    const diff = ((actual - expected) / expected) * 100;
    const isPositive = diff >= 0;
    return (
      <span className={`text-sm font-medium ${isPositive ? "text-green-600" : "text-red-600"}`}>
        {isPositive ? "+" : ""}{diff.toFixed(1)}%
      </span>
    );
  };

  const harvestedCount = mockYields.filter((r) => r.status === "harvested").length;
  const growingCount = mockYields.filter((r) => r.status === "growing").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تتبع المحصول</h1>
          <p className="text-gray-500 mt-1">Yield Tracking</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
              <Wheat className="w-5 h-5 text-sahool-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي الحقول</div>
              <div className="text-xl font-bold text-gray-900">{mockYields.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">ينمو حالياً</div>
              <div className="text-xl font-bold text-green-600">{growingCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تم الحصاد</div>
              <div className="text-xl font-bold text-blue-600">{harvestedCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متوسط الأداء</div>
              <div className="text-xl font-bold text-yellow-600">+8%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Placeholder */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">تحليل المحصول</h2>
          <BarChart3 className="w-5 h-5 text-gray-400" />
        </div>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
          <p className="text-gray-500">الرسم البياني للمحصول</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث عن حقل أو محصول..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الحالات</option>
          <option value="growing">ينمو</option>
          <option value="harvested">تم الحصاد</option>
          <option value="predicted">متوقع</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحقل</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المحصول</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الموسم</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المتوقع</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الفعلي</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الأداء</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredYields.map((record) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                        <Wheat className="w-5 h-5 text-sahool-green-600" />
                      </div>
                      <div className="font-medium text-gray-900">{record.fieldName}</div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{record.cropTypeAr}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{record.seasonAr}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {record.expectedYield} {record.unit}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {record.actualYield ? `${record.actualYield} ${record.unit}` : "-"}
                  </td>
                  <td className="px-4 py-3">
                    {getYieldComparison(record.expectedYield, record.actualYield) || "-"}
                  </td>
                  <td className="px-4 py-3">{getStatusBadge(record.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
