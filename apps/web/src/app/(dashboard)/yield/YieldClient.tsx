"use client";

import React, { useState, useMemo } from "react";
import {
  TrendingUp,
  Search,
  BarChart3,
  Wheat,
  Calendar,
  Target,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import { useYieldAnalysis } from "@/features/analytics";
import type { YieldData } from "@/features/analytics";

type YieldStatus = "growing" | "harvested" | "predicted";

function getYieldStatus(record: YieldData): YieldStatus {
  if (record.harvestDate) return "harvested";
  if (record.variance !== 0) return "predicted";
  return "growing";
}

export default function YieldClient() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const { data: yieldData = [], isLoading, error } = useYieldAnalysis();

  const filteredYields = useMemo(() => {
    return yieldData.filter((record) => {
      const matchesSearch =
        !searchTerm ||
        record.fieldNameAr.includes(searchTerm) ||
        record.fieldName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        record.cropTypeAr.includes(searchTerm);
      const status = getYieldStatus(record);
      const matchesStatus = statusFilter === "all" || status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [yieldData, searchTerm, statusFilter]);

  const getStatusBadge = (status: YieldStatus) => {
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

  const getYieldComparison = (variance: number) => {
    if (variance === 0) return null;
    const isPositive = variance >= 0;
    return (
      <span className={`text-sm font-medium ${isPositive ? "text-green-600" : "text-red-600"}`}>
        {isPositive ? "+" : ""}{variance.toFixed(1)}%
      </span>
    );
  };

  const harvestedCount = yieldData.filter((r) => getYieldStatus(r) === "harvested").length;
  const growingCount = yieldData.filter((r) => getYieldStatus(r) === "growing").length;
  const avgVariance = yieldData.length > 0
    ? yieldData.reduce((sum, r) => sum + r.variance, 0) / yieldData.length
    : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات المحصول</p>
          <p className="text-gray-500 text-sm">Failed to load yield data</p>
        </div>
      </div>
    );
  }

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
              <div className="text-xl font-bold text-gray-900">{yieldData.length}</div>
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
              <div className="text-xl font-bold text-yellow-600">
                {avgVariance >= 0 ? "+" : ""}{avgVariance.toFixed(1)}%
              </div>
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
              {filteredYields.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    لا توجد بيانات محصول
                  </td>
                </tr>
              ) : (
                filteredYields.map((record) => {
                  const status = getYieldStatus(record);
                  return (
                    <tr key={record.fieldId} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                            <Wheat className="w-5 h-5 text-sahool-green-600" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{record.fieldNameAr}</div>
                            <div className="text-sm text-gray-500">{record.fieldName}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{record.cropTypeAr}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{record.season}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {record.expectedYield.toLocaleString()} كجم
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {record.totalYield > 0 ? `${record.totalYield.toLocaleString()} كجم` : "-"}
                      </td>
                      <td className="px-4 py-3">
                        {getYieldComparison(record.variance) || "-"}
                      </td>
                      <td className="px-4 py-3">{getStatusBadge(status)}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
