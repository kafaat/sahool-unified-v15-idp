"use client";

// Inventory Management Page
// صفحة إدارة المخزون

import { useEffect, useState, useMemo, useCallback } from "react";
import Header from "@/components/layout/Header";
import DataTable from "@/components/ui/DataTable";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import { useToast } from "@/components/ui/Toast";
import { formatDate, cn } from "@/lib/utils";
import {
  Package,
  Search,
  RefreshCw,
  Download,
  Eye,
  Edit2,
  Trash2,
  Plus,
  X,
  AlertTriangle,
  TrendingDown,
  Warehouse,
} from "lucide-react";
import { logger } from "../../lib/logger";
import { MOCK_INVENTORY } from "./inventory.mock";
import type { InventoryItem } from "./inventory.mock";

type ModalMode = "view" | "create" | "edit";

const CATEGORY_OPTIONS = [
  { value: "seeds", label: "بذور" },
  { value: "fertilizers", label: "أسمدة" },
  { value: "pesticides", label: "مبيدات" },
  { value: "equipment", label: "معدات" },
];

const STATUS_OPTIONS = [
  { value: "in_stock", label: "متوفر" },
  { value: "low_stock", label: "مخزون منخفض" },
  { value: "out_of_stock", label: "نفذ" },
  { value: "expired", label: "منتهي الصلاحية" },
];

// Module-scope status helpers with frozen lookup tables to avoid
// re-creating objects on every render and to remove useCallback overhead.
const STATUS_LABELS: Readonly<Record<InventoryItem["status"], string>> = Object.freeze({
  in_stock: "متوفر",
  low_stock: "مخزون منخفض",
  out_of_stock: "نفذ",
  expired: "منتهي الصلاحية",
});

const STATUS_COLORS: Readonly<Record<InventoryItem["status"], string>> = Object.freeze({
  in_stock: "bg-green-100 text-green-800",
  low_stock: "bg-yellow-100 text-yellow-800",
  out_of_stock: "bg-red-100 text-red-800",
  expired: "bg-gray-100 text-gray-800",
});

function getStatusLabel(status: InventoryItem["status"]): string {
  return STATUS_LABELS[status];
}

function getStatusColor(status: InventoryItem["status"]): string {
  return STATUS_COLORS[status];
}

const EMPTY_FORM: Omit<InventoryItem, "id" | "lastUpdated"> = {
  name: "",
  nameAr: "",
  category: "seeds",
  categoryAr: "بذور",
  farmId: "",
  farmName: "",
  farmNameAr: "",
  quantity: 0,
  unit: "كيلو",
  minQuantity: 0,
  value: 0,
  currency: "SAR",
  status: "in_stock",
};

export default function InventoryPage() {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>("view");
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [formData, setFormData] = useState(EMPTY_FORM);

  // Delete confirmation
  const [deleteTarget, setDeleteTarget] = useState<InventoryItem | null>(null);

  const { toast } = useToast();

  const loadInventory = useCallback(async () => {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setInventory(MOCK_INVENTORY);
    } catch (error) {
      logger.error("Failed to load inventory:", error);
      toast.error("Failed to load inventory", "فشل تحميل المخزون");
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    loadInventory();
  }, [loadInventory]);

  const filteredInventory = useMemo(() => {
    return inventory.filter((item) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !item.name.toLowerCase().includes(query) &&
          !item.nameAr.toLowerCase().includes(query) &&
          !item.farmNameAr.toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (categoryFilter && item.category !== categoryFilter) return false;
      if (statusFilter && item.status !== statusFilter) return false;
      return true;
    });
  }, [inventory, searchQuery, categoryFilter, statusFilter]);

  const stats = useMemo(() => ({
    totalItems: inventory.length,
    totalValue: inventory.reduce((acc, item) => acc + item.value, 0),
    lowStock: inventory.filter((item) => item.status === "low_stock").length,
    outOfStock: inventory.filter((item) => item.status === "out_of_stock").length,
  }), [inventory]);

  // Modal handlers
  const openCreate = useCallback(() => {
    setFormData(EMPTY_FORM);
    setSelectedItem(null);
    setModalMode("create");
    setModalOpen(true);
  }, []);

  const openEdit = useCallback((item: InventoryItem) => {
    setFormData({
      name: item.name,
      nameAr: item.nameAr,
      category: item.category,
      categoryAr: item.categoryAr,
      farmId: item.farmId,
      farmName: item.farmName,
      farmNameAr: item.farmNameAr,
      quantity: item.quantity,
      unit: item.unit,
      minQuantity: item.minQuantity,
      value: item.value,
      currency: item.currency,
      status: item.status,
      expiryDate: item.expiryDate,
    });
    setSelectedItem(item);
    setModalMode("edit");
    setModalOpen(true);
  }, []);

  const openView = useCallback((item: InventoryItem) => {
    setSelectedItem(item);
    setModalMode("view");
    setModalOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setModalOpen(false);
    setSelectedItem(null);
  }, []);

  const handleSave = useCallback(() => {
    if (!formData.nameAr.trim()) {
      toast.warning("Missing field", "يرجى إدخال اسم الصنف");
      return;
    }

    const now = new Date().toISOString().split("T")[0] as string;

    if (modalMode === "create") {
      const newItem: InventoryItem = {
        ...formData,
        id: crypto.randomUUID(),
        lastUpdated: now,
      };
      setInventory((prev) => [...prev, newItem]);
      toast.success("Item added", "تمت إضافة الصنف بنجاح");
    } else if (modalMode === "edit" && selectedItem) {
      const updated: InventoryItem = { ...selectedItem, ...formData, lastUpdated: now };
      setInventory((prev) =>
        prev.map((item) =>
          item.id === selectedItem.id ? updated : item
        )
      );
      toast.success("Item updated", "تم تحديث الصنف بنجاح");
    }
    closeModal();
  }, [formData, modalMode, selectedItem, closeModal, toast]);

  const handleDelete = useCallback(() => {
    if (!deleteTarget) return;
    setInventory((prev) => prev.filter((item) => item.id !== deleteTarget.id));
    toast.success("Item deleted", "تم حذف الصنف بنجاح");
    setDeleteTarget(null);
  }, [deleteTarget, toast]);

  const handleExportCSV = useCallback(() => {
    const headers = ["الصنف", "الفئة", "المزرعة", "الكمية", "الوحدة", "القيمة", "الحالة", "آخر تحديث"];
    // RFC 4180: wrap fields containing commas, quotes, or newlines
    const escapeCSV = (val: string | number): string => {
      const s = String(val);
      if (s.includes(",") || s.includes('"') || s.includes("\n")) {
        return `"${s.replace(/"/g, '""')}"`;
      }
      return s;
    };
    const rows = filteredInventory.map((item) => [
      item.nameAr,
      item.categoryAr,
      item.farmNameAr,
      item.quantity,
      item.unit,
      item.value,
      getStatusLabel(item.status),
      item.lastUpdated,
    ]);
    const bom = "\uFEFF";
    const csv = bom + [headers.map(escapeCSV).join(","), ...rows.map((r) => r.map(escapeCSV).join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `inventory-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.info("Export complete", "تم تصدير البيانات");
  }, [filteredInventory, toast]);

  const updateField = useCallback(<K extends keyof typeof EMPTY_FORM>(key: K, value: (typeof EMPTY_FORM)[K]) => {
    setFormData((prev) => {
      const next = { ...prev, [key]: value };
      // Auto-sync categoryAr when category changes
      if (key === "category") {
        const match = CATEGORY_OPTIONS.find((o) => o.value === value);
        if (match) next.categoryAr = match.label;
      }
      return next;
    });
  }, []);

  const columns = [
    {
      key: "name",
      header: "الصنف",
      render: (item: InventoryItem) => (
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100">{item.nameAr}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{item.categoryAr}</p>
        </div>
      ),
    },
    {
      key: "farm",
      header: "المزرعة",
      render: (item: InventoryItem) => (
        <span className="text-gray-700 dark:text-gray-300">{item.farmNameAr}</span>
      ),
    },
    {
      key: "quantity",
      header: "الكمية",
      render: (item: InventoryItem) => (
        <div>
          <span className={cn(
            "font-medium",
            item.quantity <= item.minQuantity ? "text-red-600" : "text-gray-900 dark:text-gray-100"
          )}>
            {item.quantity} {item.unit}
          </span>
          {item.quantity <= item.minQuantity && (
            <p className="text-xs text-red-500">الحد الأدنى: {item.minQuantity}</p>
          )}
        </div>
      ),
    },
    {
      key: "value",
      header: "القيمة",
      render: (item: InventoryItem) => (
        <span className="font-medium text-gray-900 dark:text-gray-100">
          {item.value.toLocaleString()} {item.currency}
        </span>
      ),
    },
    {
      key: "status",
      header: "الحالة",
      render: (item: InventoryItem) => (
        <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getStatusColor(item.status))}>
          {getStatusLabel(item.status)}
        </span>
      ),
    },
    {
      key: "lastUpdated",
      header: "آخر تحديث",
      render: (item: InventoryItem) => (
        <span className="text-gray-500 dark:text-gray-400 text-sm">{formatDate(item.lastUpdated)}</span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (item: InventoryItem) => (
        <div className="flex items-center gap-1">
          <button
            onClick={() => openView(item)}
            className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="عرض"
            aria-label={`عرض ${item.nameAr}`}
          >
            <Eye className="w-4 h-4 text-gray-500 dark:text-gray-400" />
          </button>
          <button
            onClick={() => openEdit(item)}
            className="p-1.5 hover:bg-blue-50 rounded-lg transition-colors"
            title="تعديل"
            aria-label={`تعديل ${item.nameAr}`}
          >
            <Edit2 className="w-4 h-4 text-blue-500" />
          </button>
          <button
            onClick={() => setDeleteTarget(item)}
            className="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
            title="حذف"
            aria-label={`حذف ${item.nameAr}`}
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      ),
      className: "w-28",
    },
  ];

  return (
    <div className="p-6">
      <Header title="إدارة المخزون" subtitle={`${inventory.length} صنف`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.totalItems}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الأصناف</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Warehouse className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.totalValue.toLocaleString()}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي القيمة (SAR)</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <TrendingDown className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.lowStock}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مخزون منخفض</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.outOfStock}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">نفذ</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters + Actions */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالصنف أو المزرعة..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
              aria-label="بحث في المخزون"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            aria-label="تصفية حسب الفئة"
          >
            <option value="">كل الفئات</option>
            <option value="seeds">بذور</option>
            <option value="fertilizers">أسمدة</option>
            <option value="pesticides">مبيدات</option>
            <option value="equipment">معدات</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            aria-label="تصفية حسب الحالة"
          >
            <option value="">كل الحالات</option>
            <option value="in_stock">متوفر</option>
            <option value="low_stock">مخزون منخفض</option>
            <option value="out_of_stock">نفذ</option>
            <option value="expired">منتهي الصلاحية</option>
          </select>

          <button
            onClick={loadInventory}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            aria-label="تحديث البيانات"
          >
            <RefreshCw className={cn("w-5 h-5 text-gray-600 dark:text-gray-400", isLoading && "animate-spin")} />
          </button>
          <button
            onClick={handleExportCSV}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            aria-label="تصدير CSV"
          >
            <Download className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
          <button
            onClick={openCreate}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>إضافة صنف</span>
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredInventory}
            keyExtractor={(item) => item.id}
            emptyMessage="لا توجد أصناف مطابقة للبحث"
          />
        )}
      </div>

      {/* Create/Edit/View Modal */}
      {modalOpen && (
        <div
          className="fixed inset-0 z-[9998] flex items-center justify-center"
          role="dialog"
          aria-modal="true"
          aria-labelledby="inventory-modal-title"
          onKeyDown={(e) => { if (e.key === "Escape") closeModal(); }}
        >
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={closeModal} />
          <div className="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-lg w-full mx-4 animate-scale-in max-h-[85vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-800 z-10">
              <h2 id="inventory-modal-title" className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {modalMode === "create" && "إضافة صنف جديد"}
                {modalMode === "edit" && "تعديل الصنف"}
                {modalMode === "view" && "تفاصيل الصنف"}
              </h2>
              <button
                autoFocus
                onClick={closeModal}
                className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                aria-label="إغلاق"
              >
                <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>

            {/* Body */}
            <div className="p-6 space-y-4">
              {modalMode === "view" && selectedItem ? (
                <div className="space-y-4">
                  <DetailRow label="الاسم (عربي)" value={selectedItem.nameAr} />
                  <DetailRow label="الاسم (إنجليزي)" value={selectedItem.name} />
                  <DetailRow label="الفئة" value={selectedItem.categoryAr} />
                  <DetailRow label="المزرعة" value={selectedItem.farmNameAr} />
                  <DetailRow label="الكمية" value={`${selectedItem.quantity} ${selectedItem.unit}`} />
                  <DetailRow label="الحد الأدنى" value={`${selectedItem.minQuantity} ${selectedItem.unit}`} />
                  <DetailRow label="القيمة" value={`${selectedItem.value.toLocaleString()} ${selectedItem.currency}`} />
                  <DetailRow
                    label="الحالة"
                    value={
                      <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getStatusColor(selectedItem.status))}>
                        {getStatusLabel(selectedItem.status)}
                      </span>
                    }
                  />
                  <DetailRow label="آخر تحديث" value={formatDate(selectedItem.lastUpdated)} />
                  {selectedItem.expiryDate && (
                    <DetailRow label="تاريخ الانتهاء" value={formatDate(selectedItem.expiryDate)} />
                  )}
                </div>
              ) : (
                <>
                  <FormField label="اسم الصنف (عربي)" required>
                    <input
                      type="text"
                      value={formData.nameAr}
                      onChange={(e) => updateField("nameAr", e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                      placeholder="مثال: سماد NPK"
                    />
                  </FormField>
                  <FormField label="اسم الصنف (إنجليزي)">
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => updateField("name", e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                      placeholder="e.g. NPK Fertilizer"
                    />
                  </FormField>
                  <div className="grid grid-cols-2 gap-4">
                    <FormField label="الفئة">
                      <select
                        value={formData.category}
                        onChange={(e) => updateField("category", e.target.value as InventoryItem["category"])}
                        className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                      >
                        {CATEGORY_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                    </FormField>
                    <FormField label="الحالة">
                      <select
                        value={formData.status}
                        onChange={(e) => updateField("status", e.target.value as InventoryItem["status"])}
                        className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                      >
                        {STATUS_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                    </FormField>
                  </div>
                  <FormField label="اسم المزرعة">
                    <input
                      type="text"
                      value={formData.farmNameAr}
                      onChange={(e) => updateField("farmNameAr", e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                      placeholder="مثال: مزرعة الراشد"
                    />
                  </FormField>
                  <div className="grid grid-cols-3 gap-4">
                    <FormField label="الكمية">
                      <input
                        type="number"
                        min={0}
                        value={formData.quantity}
                        onChange={(e) => updateField("quantity", Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                      />
                    </FormField>
                    <FormField label="الوحدة">
                      <input
                        type="text"
                        value={formData.unit}
                        onChange={(e) => updateField("unit", e.target.value)}
                        className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                      />
                    </FormField>
                    <FormField label="الحد الأدنى">
                      <input
                        type="number"
                        min={0}
                        value={formData.minQuantity}
                        onChange={(e) => updateField("minQuantity", Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                      />
                    </FormField>
                  </div>
                  <FormField label="القيمة (SAR)">
                    <input
                      type="number"
                      min={0}
                      value={formData.value}
                      onChange={(e) => updateField("value", Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                    />
                  </FormField>
                </>
              )}
            </div>

            {/* Footer */}
            {modalMode !== "view" && (
              <div className="flex gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={closeModal}
                  className="flex-1 px-4 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
                >
                  إلغاء
                </button>
                <button
                  onClick={handleSave}
                  className="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-sahool-600 rounded-lg hover:bg-sahool-700 transition"
                >
                  {modalMode === "create" ? "إضافة" : "حفظ التعديلات"}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        title="Delete Item"
        titleAr="حذف الصنف"
        message={`Are you sure you want to delete "${deleteTarget?.name}"?`}
        messageAr={`هل أنت متأكد من حذف "${deleteTarget?.nameAr}"؟`}
        confirmLabel="Delete"
        confirmLabelAr="حذف"
        variant="danger"
      />
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
      <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{value}</span>
    </div>
  );
}

function FormField({ label, required, children }: { label: string; required?: boolean; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label}
        {required && <span className="text-red-500 mr-1">*</span>}
      </label>
      {children}
    </div>
  );
}
