"use client";

import React, { useState, useEffect } from "react";
import { Package, Plus, Search, Filter, ArrowUpDown, AlertTriangle } from "lucide-react";

interface InventoryItem {
  id: string;
  name: string;
  nameAr: string;
  category: string;
  quantity: number;
  unit: string;
  minStock: number;
  location: string;
  lastUpdated: string;
  status: "in_stock" | "low_stock" | "out_of_stock";
}

const mockInventory: InventoryItem[] = [
  {
    id: "1",
    name: "NPK Fertilizer",
    nameAr: "سماد NPK",
    category: "fertilizers",
    quantity: 500,
    unit: "kg",
    minStock: 100,
    location: "Warehouse A",
    lastUpdated: "2026-01-25",
    status: "in_stock",
  },
  {
    id: "2",
    name: "Wheat Seeds",
    nameAr: "بذور القمح",
    category: "seeds",
    quantity: 50,
    unit: "kg",
    minStock: 100,
    location: "Warehouse B",
    lastUpdated: "2026-01-24",
    status: "low_stock",
  },
  {
    id: "3",
    name: "Pesticide A",
    nameAr: "مبيد حشري أ",
    category: "pesticides",
    quantity: 0,
    unit: "liters",
    minStock: 20,
    location: "Warehouse A",
    lastUpdated: "2026-01-23",
    status: "out_of_stock",
  },
];

const categories = [
  { value: "all", label: "All Categories", labelAr: "جميع الفئات" },
  { value: "fertilizers", label: "Fertilizers", labelAr: "الأسمدة" },
  { value: "seeds", label: "Seeds", labelAr: "البذور" },
  { value: "pesticides", label: "Pesticides", labelAr: "المبيدات" },
  { value: "equipment", label: "Equipment", labelAr: "المعدات" },
];

export default function InventoryClient() {
  const [inventory, setInventory] = useState<InventoryItem[]>(mockInventory);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setIsLoading(false), 500);
  }, []);

  const filteredInventory = inventory.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.nameAr.includes(searchTerm);
    const matchesCategory =
      selectedCategory === "all" || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getStatusBadge = (status: InventoryItem["status"]) => {
    const styles = {
      in_stock: "bg-green-100 text-green-800",
      low_stock: "bg-yellow-100 text-yellow-800",
      out_of_stock: "bg-red-100 text-red-800",
    };
    const labels = {
      in_stock: "متوفر",
      low_stock: "مخزون منخفض",
      out_of_stock: "نفذ المخزون",
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const lowStockCount = inventory.filter((i) => i.status === "low_stock").length;
  const outOfStockCount = inventory.filter((i) => i.status === "out_of_stock").length;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المخزون</h1>
          <p className="text-gray-500 mt-1">Inventory Management</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors">
          <Plus className="w-4 h-4" />
          <span>إضافة عنصر</span>
        </button>
      </div>

      {/* Alerts */}
      {(lowStockCount > 0 || outOfStockCount > 0) && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span className="font-medium text-amber-800">
              تنبيه المخزون: {lowStockCount} عناصر منخفضة، {outOfStockCount} نفذت
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي العناصر</div>
          <div className="text-2xl font-bold text-gray-900">{inventory.length}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">متوفر</div>
          <div className="text-2xl font-bold text-green-600">
            {inventory.filter((i) => i.status === "in_stock").length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">مخزون منخفض</div>
          <div className="text-2xl font-bold text-yellow-600">{lowStockCount}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">نفذ المخزون</div>
          <div className="text-2xl font-bold text-red-600">{outOfStockCount}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في المخزون..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {categories.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.labelAr}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">العنصر</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الفئة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الكمية</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الموقع</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredInventory.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                        <Package className="w-5 h-5 text-sahool-green-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{item.nameAr}</div>
                        <div className="text-sm text-gray-500">{item.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {categories.find((c) => c.value === item.category)?.labelAr}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {item.quantity} {item.unit}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{item.location}</td>
                  <td className="px-4 py-3">{getStatusBadge(item.status)}</td>
                  <td className="px-4 py-3">
                    <button className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium">
                      تعديل
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
