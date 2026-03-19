"use client";

// Marketplace Management Page
// صفحة إدارة السوق

import { useEffect, useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import DataTable from "@/components/ui/DataTable";
import { cn } from "@/lib/utils";
import {
  Search,
  RefreshCw,
  Download,
  Eye,
  CheckCircle,
  XCircle,
  Package,
  TrendingUp,
  Filter,
} from "lucide-react";
import { logger } from "../../lib/logger";
import { MOCK_PRODUCTS } from "./marketplace.mock";
import type { Product } from "./marketplace.mock";

export default function MarketplacePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    loadProducts();
  }, []);

  async function loadProducts() {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setProducts(MOCK_PRODUCTS);
    } catch (error) {
      logger.error("Failed to load products:", error);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !p.name.toLowerCase().includes(query) &&
          !p.nameAr.toLowerCase().includes(query) &&
          !p.sellerAr.toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (categoryFilter && p.category !== categoryFilter) return false;
      if (statusFilter && p.status !== statusFilter) return false;
      return true;
    });
  }, [products, searchQuery, categoryFilter, statusFilter]);

  const stats = useMemo(() => ({
    total: products.length,
    active: products.filter((p) => p.status === "active").length,
    pending: products.filter((p) => p.status === "pending").length,
    totalOrders: products.reduce((acc, p) => acc + p.orders, 0),
  }), [products]);

  const getStatusLabel = (status: Product["status"]) => {
    const labels: Record<Product["status"], string> = {
      active: "نشط",
      pending: "قيد المراجعة",
      rejected: "مرفوض",
      sold_out: "نفذ",
    };
    return labels[status];
  };

  const getStatusColor = (status: Product["status"]) => {
    const colors: Record<Product["status"], string> = {
      active: "bg-green-100 text-green-800",
      pending: "bg-yellow-100 text-yellow-800",
      rejected: "bg-red-100 text-red-800",
      sold_out: "bg-gray-100 text-gray-800",
    };
    return colors[status];
  };

  const columns = [
    {
      key: "name",
      header: "المنتج",
      render: (product: Product) => (
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
            <Package className="w-6 h-6 text-gray-400 dark:text-gray-500" />
          </div>
          <div>
            <p className="font-medium text-gray-900 dark:text-gray-100">{product.nameAr}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{product.categoryAr}</p>
          </div>
        </div>
      ),
    },
    {
      key: "seller",
      header: "البائع",
      render: (product: Product) => (
        <span className="text-gray-700 dark:text-gray-300">{product.sellerAr}</span>
      ),
    },
    {
      key: "price",
      header: "السعر",
      render: (product: Product) => (
        <span className="font-medium text-gray-900 dark:text-gray-100">
          {product.price} {product.currency} / {product.unit}
        </span>
      ),
    },
    {
      key: "quantity",
      header: "الكمية",
      render: (product: Product) => (
        <span className={cn("text-gray-700 dark:text-gray-300", product.quantity === 0 && "text-red-600")}>
          {product.quantity}
        </span>
      ),
    },
    {
      key: "stats",
      header: "الإحصائيات",
      render: (product: Product) => (
        <div className="text-sm">
          <span className="text-gray-500 dark:text-gray-400">{product.views} مشاهدة</span>
          <span className="mx-2">•</span>
          <span className="text-sahool-600 font-medium">{product.orders} طلب</span>
        </div>
      ),
    },
    {
      key: "status",
      header: "الحالة",
      render: (product: Product) => (
        <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getStatusColor(product.status))}>
          {getStatusLabel(product.status)}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (product: Product) => (
        <div className="flex items-center gap-1">
          <button disabled className="p-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed" title="عرض (قريبًا)">
            <Eye className="w-4 h-4 text-gray-500 dark:text-gray-400" />
          </button>
          {product.status === "pending" && (
            <>
              <button disabled className="p-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed" title="قبول (قريبًا)">
                <CheckCircle className="w-4 h-4 text-green-500" />
              </button>
              <button disabled className="p-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed" title="رفض (قريبًا)">
                <XCircle className="w-4 h-4 text-red-500" />
              </button>
            </>
          )}
        </div>
      ),
      className: "w-32",
    },
  ];

  return (
    <div className="p-6">
      <Header title="إدارة السوق" subtitle={`${products.length} منتج`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي المنتجات</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.active}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">نشط</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Filter className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.pending}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">قيد المراجعة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.totalOrders}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الطلبات</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالاسم أو البائع..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
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
          >
            <option value="">كل الحالات</option>
            <option value="active">نشط</option>
            <option value="pending">قيد المراجعة</option>
            <option value="rejected">مرفوض</option>
            <option value="sold_out">نفذ</option>
          </select>

          <button
            onClick={loadProducts}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <RefreshCw className={cn("w-5 h-5 text-gray-600 dark:text-gray-400", isLoading && "animate-spin")} />
          </button>
          <button
            disabled
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="تصدير (قريبًا)"
          >
            <Download className="w-5 h-5 text-gray-600 dark:text-gray-400" />
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
            data={filteredProducts}
            keyExtractor={(product) => product.id}
            emptyMessage="لا توجد منتجات مطابقة للبحث"
          />
        )}
      </div>
    </div>
  );
}
