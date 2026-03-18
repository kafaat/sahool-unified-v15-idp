"use client";

// Logistics Management Page
// صفحة إدارة اللوجستيات

import { useEffect, useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import DataTable from "@/components/ui/DataTable";
import { formatDate, cn } from "@/lib/utils";
import {
  Truck,
  Search,
  RefreshCw,
  Download,
  Eye,
  MapPin,
  Package,
  Clock,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { logger } from "../../lib/logger";
import { MOCK_SHIPMENTS } from "./logistics.mock";
import type { Shipment } from "./logistics.mock";

export default function LogisticsPage() {
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    loadShipments();
  }, []);

  async function loadShipments() {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setShipments(MOCK_SHIPMENTS);
    } catch (error) {
      logger.error("Failed to load shipments:", error);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredShipments = useMemo(() => {
    return shipments.filter((s) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !s.trackingNumber.toLowerCase().includes(query) &&
          !s.destinationAr.toLowerCase().includes(query) &&
          !s.receiverAr.toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (statusFilter && s.status !== statusFilter) return false;
      return true;
    });
  }, [shipments, searchQuery, statusFilter]);

  const stats = useMemo(() => ({
    total: shipments.length,
    inTransit: shipments.filter((s) => s.status === "in_transit").length,
    delivered: shipments.filter((s) => s.status === "delivered").length,
    delayed: shipments.filter((s) => s.status === "delayed").length,
  }), [shipments]);

  const getStatusLabel = (status: Shipment["status"]) => {
    const labels: Record<Shipment["status"], string> = {
      pending: "قيد الانتظار",
      in_transit: "في الطريق",
      delivered: "تم التسليم",
      delayed: "متأخر",
      cancelled: "ملغي",
    };
    return labels[status];
  };

  const getStatusColor = (status: Shipment["status"]) => {
    const colors: Record<Shipment["status"], string> = {
      pending: "bg-yellow-100 text-yellow-800",
      in_transit: "bg-blue-100 text-blue-800",
      delivered: "bg-green-100 text-green-800",
      delayed: "bg-red-100 text-red-800",
      cancelled: "bg-gray-100 text-gray-800",
    };
    return colors[status];
  };

  const getStatusIcon = (status: Shipment["status"]) => {
    const icons: Record<Shipment["status"], React.ReactNode> = {
      pending: <Clock className="w-4 h-4" />,
      in_transit: <Truck className="w-4 h-4" />,
      delivered: <CheckCircle className="w-4 h-4" />,
      delayed: <AlertCircle className="w-4 h-4" />,
      cancelled: <AlertCircle className="w-4 h-4" />,
    };
    return icons[status];
  };

  const columns = [
    {
      key: "tracking",
      header: "رقم التتبع",
      render: (shipment: Shipment) => (
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100 font-mono">{shipment.trackingNumber}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{formatDate(shipment.createdAt)}</p>
        </div>
      ),
    },
    {
      key: "route",
      header: "المسار",
      render: (shipment: Shipment) => (
        <div className="text-sm">
          <p className="text-gray-500 dark:text-gray-400">من: {shipment.originAr}</p>
          <p className="text-gray-900 dark:text-gray-100 font-medium">إلى: {shipment.destinationAr}</p>
        </div>
      ),
    },
    {
      key: "receiver",
      header: "المستلم",
      render: (shipment: Shipment) => (
        <span className="text-gray-700 dark:text-gray-300">{shipment.receiverAr}</span>
      ),
    },
    {
      key: "details",
      header: "التفاصيل",
      render: (shipment: Shipment) => (
        <div className="text-sm">
          <span className="text-gray-600 dark:text-gray-400">{shipment.weight} كجم</span>
          <span className="mx-2">•</span>
          <span className="text-gray-600 dark:text-gray-400">{shipment.items} قطعة</span>
        </div>
      ),
    },
    {
      key: "delivery",
      header: "التسليم",
      render: (shipment: Shipment) => (
        <div className="text-sm">
          <p className="text-gray-500 dark:text-gray-400">المتوقع: {formatDate(shipment.estimatedDelivery)}</p>
          {shipment.actualDelivery && (
            <p className="text-green-600">الفعلي: {formatDate(shipment.actualDelivery)}</p>
          )}
        </div>
      ),
    },
    {
      key: "status",
      header: "الحالة",
      render: (shipment: Shipment) => (
        <span className={cn(
          "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
          getStatusColor(shipment.status)
        )}>
          {getStatusIcon(shipment.status)}
          {getStatusLabel(shipment.status)}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (_shipment: Shipment) => (
        <div className="flex items-center gap-1">
          <button disabled className="p-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed" title="عرض (قريبًا)">
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          <button disabled className="p-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed" title="تتبع (قريبًا)">
            <MapPin className="w-4 h-4 text-blue-500" />
          </button>
        </div>
      ),
      className: "w-24",
    },
  ];

  return (
    <div className="p-6">
      <Header title="إدارة اللوجستيات" subtitle={`${shipments.length} شحنة`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الشحنات</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <Truck className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.inTransit}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">في الطريق</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.delivered}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">تم التسليم</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.delayed}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متأخر</p>
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
              placeholder="بحث برقم التتبع أو الوجهة..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="pending">قيد الانتظار</option>
            <option value="in_transit">في الطريق</option>
            <option value="delivered">تم التسليم</option>
            <option value="delayed">متأخر</option>
            <option value="cancelled">ملغي</option>
          </select>

          <button
            onClick={loadShipments}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <RefreshCw className={cn("w-5 h-5 text-gray-600 dark:text-gray-300", isLoading && "animate-spin")} />
          </button>
          <button
            disabled
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="تصدير (قريبًا)"
          >
            <Download className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredShipments}
            keyExtractor={(shipment) => shipment.id}
            emptyMessage="لا توجد شحنات مطابقة للبحث"
          />
        )}
      </div>
    </div>
  );
}
