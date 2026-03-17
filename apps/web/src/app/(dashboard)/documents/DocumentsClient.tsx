"use client";

import React, { useState, useMemo } from "react";
import {
  FileText, Plus, Search, AlertTriangle, Download, Trash2,
  Shield, FileCheck, File, Clock,
} from "lucide-react";
import { useDocuments, useDocumentStats } from "@/features/documents";
import type { DocumentCategory, DocumentStatus } from "@/features/documents";

const categoryConfig: Record<DocumentCategory, { labelAr: string; icon: React.ElementType; color: string }> = {
  compliance: { labelAr: "امتثال", icon: Shield, color: "text-blue-600" },
  permits: { labelAr: "تصاريح", icon: FileCheck, color: "text-green-600" },
  contracts: { labelAr: "عقود", icon: FileText, color: "text-purple-600" },
  reports: { labelAr: "تقارير", icon: File, color: "text-orange-600" },
  certificates: { labelAr: "شهادات", icon: FileCheck, color: "text-yellow-600" },
  maps: { labelAr: "خرائط", icon: File, color: "text-cyan-600" },
  invoices: { labelAr: "فواتير", icon: File, color: "text-pink-600" },
  other: { labelAr: "أخرى", icon: File, color: "text-gray-600" },
};

const statusConfig: Record<DocumentStatus, { color: string; labelAr: string }> = {
  draft: { color: "bg-gray-100 text-gray-800", labelAr: "مسودة" },
  active: { color: "bg-green-100 text-green-800", labelAr: "نشط" },
  expired: { color: "bg-red-100 text-red-800", labelAr: "منتهي" },
  archived: { color: "bg-yellow-100 text-yellow-800", labelAr: "مؤرشف" },
};

const categoryOptions: Array<{ value: DocumentCategory | "all"; labelAr: string }> = [
  { value: "all", labelAr: "جميع الفئات" },
  { value: "compliance", labelAr: "امتثال" },
  { value: "permits", labelAr: "تصاريح" },
  { value: "contracts", labelAr: "عقود" },
  { value: "reports", labelAr: "تقارير" },
  { value: "certificates", labelAr: "شهادات" },
  { value: "maps", labelAr: "خرائط" },
  { value: "invoices", labelAr: "فواتير" },
];

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentsClient() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<DocumentCategory | "all">("all");

  const { data: documents = [], isLoading, error } = useDocuments(
    selectedCategory !== "all" ? { category: selectedCategory } : undefined
  );
  const { data: stats } = useDocumentStats();

  const filteredDocs = useMemo(() => {
    if (!searchTerm) return documents;
    const term = searchTerm.toLowerCase();
    return documents.filter(
      (d) =>
        d.title.toLowerCase().includes(term) ||
        d.titleAr.includes(searchTerm) ||
        d.tags.some((t) => t.toLowerCase().includes(term))
    );
  }, [documents, searchTerm]);

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
          <p className="text-red-600">فشل في تحميل الوثائق</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">الوثائق</h1>
          <p className="text-gray-500 mt-1">Documents & Records</p>
        </div>
        <button
          disabled
          title="قريباً - Coming soon"
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-4 h-4" />
          <span>رفع وثيقة</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي الوثائق</div>
          <div className="text-2xl font-bold text-gray-900">{stats?.totalDocuments ?? documents.length}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">نشطة</div>
          <div className="text-2xl font-bold text-green-600">{stats?.activeDocuments ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Clock className="w-3.5 h-3.5" /> تنتهي قريباً
          </div>
          <div className="text-2xl font-bold text-yellow-600">{stats?.expiringDocuments ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">الحجم الكلي</div>
          <div className="text-2xl font-bold text-blue-600">{stats?.totalSizeMb ?? 0} MB</div>
        </div>
      </div>

      {/* Expiry Alert */}
      {(stats?.expiringDocuments ?? 0) > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span className="font-medium text-amber-800">
              تنبيه: {stats?.expiringDocuments} وثيقة تنتهي صلاحيتها خلال 30 يوم
            </span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في الوثائق..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value as DocumentCategory | "all")}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {categoryOptions.map((c) => (
            <option key={c.value} value={c.value}>{c.labelAr}</option>
          ))}
        </select>
      </div>

      {/* Document List */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الوثيقة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الفئة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المزرعة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحجم</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">تاريخ الانتهاء</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    لا توجد وثائق
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => {
                  const cat = categoryConfig[doc.category];
                  const st = statusConfig[doc.status];
                  const CatIcon = cat.icon;
                  return (
                    <tr key={doc.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <CatIcon className={`w-5 h-5 ${cat.color}`} />
                          <div>
                            <div className="font-medium text-gray-900">{doc.titleAr}</div>
                            <div className="text-xs text-gray-500">{doc.fileName}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{cat.labelAr}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{doc.farmNameAr || "—"}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{formatFileSize(doc.fileSize)}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${st.color}`}>
                          {st.labelAr}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {doc.expiryDate
                          ? new Date(doc.expiryDate).toLocaleDateString("ar-SA")
                          : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <button className="p-1.5 text-sahool-green-600 hover:bg-sahool-green-50 rounded">
                            <Download className="w-4 h-4" />
                          </button>
                          <button className="p-1.5 text-red-500 hover:bg-red-50 rounded">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
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
