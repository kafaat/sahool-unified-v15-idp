"use client";

// Inventory Management Page
// صفحة إدارة المخزون

import { useEffect, useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import DataTable from "@/components/ui/DataTable";
import { formatDate, cn } from "@/lib/utils";
import {
  Package,
  Search,
  RefreshCw,
  Download,
  Eye,
  AlertTriangle,
  TrendingDown,
  Warehouse,
} from "lucide-react";
import { logger } from "../../lib/logger";
import { MOCK_INVENTORY } from "./inventory.mock";
import type { InventoryItem } from "./inventory.mock";

export default function InventoryPage() {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    loadInventory();
  }, []);

  async function loadInventory() {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setInventory(MOCK_INVENTORY);
    } catch (error) {
      logger.error("Failed to load inventory:", error);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredInventory = useMemo(() => {
    return inventory.filter((item) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !item.name.toLowerCase().includes(query) &&
          !item.nameAr.includes(query) &&
          !item.farmNameAr.includes(query)
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

  const getStatusLabel = (status: InventoryItem["status"]) => {
    const labels: Record<InventoryItem["status"], string> = {
      in_stock: "متوفر",
      low_stock: "مخزون منخفض",
      out_of_stock: "نفذ",
      expired: "منتهي الصلاحية",
    };
    return labels[status];
  };

  const getStatusColor = (status: InventoryItem["status"]) => {
    const colors: Record<InventoryItem["status"], string> = {
      in_stock: "bg-green-100 text-green-800",
      low_stock: "bg-yellow-100 text-yellow-800",
      out_of_stock: "bg-red-100 text-red-800",
      expired: "bg-gray-100 text-gray-800",
    };
    return colors[status];
  };

  const columns = [
    {
      key: "name",
      header: "الصنف",
      render: (item: InventoryItem) => (
        <div>
          <p className="font-medium text-gray-900">{item.nameAr}</p>
          <p className="text-xs text-gray-500">{item.categoryAr}</p>
        </div>
      ),
    },
    {
      key: "farm",
      header: "المزرعة",
      render: (item: InventoryItem) => (
        <span className="text-gray-700">{item.farmNameAr}</span>
      ),
    },
    {
      key: "quantity",
      header: "الكمية",
      render: (item: InventoryItem) => (
        <div>
          <span className={cn(
            "font-medium",
            item.quantity <= item.minQuantity ? "text-red-600" : "text-gray-900"
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
        <span className="font-medium text-gray-900">
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
        <span className="text-gray-500 text-sm">{formatDate(item.lastUpdated)}</span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (_item: InventoryItem) => (
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="عرض">
          <Eye className="w-4 h-4 text-gray-500" />
        </button>
      ),
      className: "w-16",
    },
  ];

  return (
    <div className="p-6">
      <Header title="إدارة المخزون" subtitle={`${inventory.length} صنف`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.totalItems}</p>
              <p className="text-sm text-gray-500">إجمالي الأصناف</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Warehouse className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.totalValue.toLocaleString()}</p>
              <p className="text-sm text-gray-500">إجمالي القيمة (SAR)</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <TrendingDown className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.lowStock}</p>
              <p className="text-sm text-gray-500">مخزون منخفض</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.outOfStock}</p>
              <p className="text-sm text-gray-500">نفذ</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white rounded-xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالصنف أو المزرعة..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
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
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="in_stock">متوفر</option>
            <option value="low_stock">مخزون منخفض</option>
            <option value="out_of_stock">نفذ</option>
            <option value="expired">منتهي الصلاحية</option>
          </select>

          <button
            onClick={loadInventory}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className={cn("w-5 h-5 text-gray-600", isLoading && "animate-spin")} />
          </button>
          <button className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white rounded-xl border border-gray-100 p-8">
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
    </div>
  );
}
