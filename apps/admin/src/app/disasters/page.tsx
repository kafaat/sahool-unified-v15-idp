"use client";

// Disaster Reports Page
// صفحة تقارير الكوارث

import { useEffect, useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import DataTable from "@/components/ui/DataTable";
import { formatDate, cn } from "@/lib/utils";
import {
  AlertTriangle,
  Search,
  RefreshCw,
  Download,
  Eye,
  CloudRain,
  Thermometer,
  Bug,
  Flame,
  Wind,
  MapPin,
  DollarSign,
} from "lucide-react";
import { logger } from "../../lib/logger";
import { MOCK_REPORTS } from "./disasters.mock";
import type { DisasterReport } from "./disasters.mock";

type DisasterType = DisasterReport["type"];

export default function DisastersPage() {
  const [reports, setReports] = useState<DisasterReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    loadReports();
  }, []);

  async function loadReports() {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setReports(MOCK_REPORTS);
    } catch (error) {
      logger.error("Failed to load disaster reports:", error);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredReports = useMemo(() => {
    return reports.filter((r) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !r.locationAr.includes(query) &&
          !r.descriptionAr.includes(query)
        ) {
          return false;
        }
      }
      if (typeFilter && r.type !== typeFilter) return false;
      if (statusFilter && r.status !== statusFilter) return false;
      return true;
    });
  }, [reports, searchQuery, typeFilter, statusFilter]);

  const stats = useMemo(() => ({
    total: reports.length,
    active: reports.filter((r) => r.status === "active").length,
    totalDamage: reports.reduce((acc, r) => acc + r.damageEstimate, 0),
    affectedFarms: reports.filter(r => r.status === "active").reduce((acc, r) => acc + r.affectedFarms, 0),
  }), [reports]);

  const getTypeIcon = (type: DisasterType) => {
    const icons: Record<DisasterType, React.ReactNode> = {
      flood: <CloudRain className="w-5 h-5" />,
      drought: <Thermometer className="w-5 h-5" />,
      frost: <Thermometer className="w-5 h-5" />,
      pest: <Bug className="w-5 h-5" />,
      disease: <Bug className="w-5 h-5" />,
      storm: <Wind className="w-5 h-5" />,
      fire: <Flame className="w-5 h-5" />,
    };
    return icons[type];
  };

  const getSeverityLabel = (severity: DisasterReport["severity"]) => {
    const labels: Record<DisasterReport["severity"], string> = {
      minor: "طفيف",
      moderate: "متوسط",
      severe: "شديد",
      catastrophic: "كارثي",
    };
    return labels[severity];
  };

  const getSeverityColor = (severity: DisasterReport["severity"]) => {
    const colors: Record<DisasterReport["severity"], string> = {
      minor: "bg-yellow-100 text-yellow-800",
      moderate: "bg-orange-100 text-orange-800",
      severe: "bg-red-100 text-red-800",
      catastrophic: "bg-purple-100 text-purple-800",
    };
    return colors[severity];
  };

  const getStatusLabel = (status: DisasterReport["status"]) => {
    const labels: Record<DisasterReport["status"], string> = {
      active: "نشط",
      monitoring: "قيد المراقبة",
      resolved: "تم الحل",
      closed: "مغلق",
    };
    return labels[status];
  };

  const getStatusColor = (status: DisasterReport["status"]) => {
    const colors: Record<DisasterReport["status"], string> = {
      active: "bg-red-100 text-red-800",
      monitoring: "bg-blue-100 text-blue-800",
      resolved: "bg-green-100 text-green-800",
      closed: "bg-gray-100 text-gray-800",
    };
    return colors[status];
  };

  const columns = [
    {
      key: "type",
      header: "النوع",
      render: (report: DisasterReport) => (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center text-red-600">
            {getTypeIcon(report.type)}
          </div>
          <span className="font-medium text-gray-900">{report.typeAr}</span>
        </div>
      ),
    },
    {
      key: "location",
      header: "الموقع",
      render: (report: DisasterReport) => (
        <div className="flex items-center gap-1 text-gray-700">
          <MapPin className="w-4 h-4 text-gray-400" />
          {report.locationAr}
        </div>
      ),
    },
    {
      key: "impact",
      header: "التأثير",
      render: (report: DisasterReport) => (
        <div className="text-sm">
          <p className="text-gray-900">{report.affectedFarms} مزرعة</p>
          <p className="text-gray-500">{report.affectedArea} هكتار</p>
        </div>
      ),
    },
    {
      key: "damage",
      header: "الأضرار",
      render: (report: DisasterReport) => (
        <span className="font-medium text-red-600">
          {report.damageEstimate.toLocaleString()} {report.currency}
        </span>
      ),
    },
    {
      key: "severity",
      header: "الشدة",
      render: (report: DisasterReport) => (
        <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getSeverityColor(report.severity))}>
          {getSeverityLabel(report.severity)}
        </span>
      ),
    },
    {
      key: "status",
      header: "الحالة",
      render: (report: DisasterReport) => (
        <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getStatusColor(report.status))}>
          {getStatusLabel(report.status)}
        </span>
      ),
    },
    {
      key: "date",
      header: "التاريخ",
      render: (report: DisasterReport) => (
        <span className="text-gray-500 text-sm">{formatDate(report.reportedAt)}</span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (_report: DisasterReport) => (
        <button disabled className="p-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed" title="عرض (قريبًا)">
          <Eye className="w-4 h-4 text-gray-500" />
        </button>
      ),
      className: "w-16",
    },
  ];

  return (
    <div className="p-6">
      <Header title="تقارير الكوارث" subtitle={`${reports.length} تقرير`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-500">إجمالي التقارير</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.active}</p>
              <p className="text-sm text-gray-500">نشط حالياً</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{(stats.totalDamage / 1000000).toFixed(1)}M</p>
              <p className="text-sm text-gray-500">إجمالي الأضرار (SAR)</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <MapPin className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.affectedFarms}</p>
              <p className="text-sm text-gray-500">مزارع متأثرة (نشط)</p>
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
              placeholder="بحث بالموقع أو الوصف..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الأنواع</option>
            <option value="drought">جفاف</option>
            <option value="flood">فيضان</option>
            <option value="frost">صقيع</option>
            <option value="pest">آفات</option>
            <option value="disease">أمراض</option>
            <option value="storm">عاصفة</option>
            <option value="fire">حريق</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="active">نشط</option>
            <option value="monitoring">قيد المراقبة</option>
            <option value="resolved">تم الحل</option>
            <option value="closed">مغلق</option>
          </select>

          <button
            onClick={loadReports}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className={cn("w-5 h-5 text-gray-600", isLoading && "animate-spin")} />
          </button>
          <button
            disabled
            className="p-2 border border-gray-200 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="تصدير (قريبًا)"
          >
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
            data={filteredReports}
            keyExtractor={(report) => report.id}
            emptyMessage="لا توجد تقارير مطابقة للبحث"
          />
        )}
      </div>
    </div>
  );
}
