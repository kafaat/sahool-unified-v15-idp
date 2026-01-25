"use client";

import React, { useState, useMemo } from "react";
import {
  Bell,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Search,
} from "lucide-react";

type AlertType = "warning" | "critical" | "info" | "success";
type AlertStatus = "active" | "acknowledged" | "resolved";

interface Alert {
  id: string;
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  type: AlertType;
  status: AlertStatus;
  fieldId?: string;
  fieldName?: string;
  createdAt: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
}

// Mock data
const mockAlerts: Alert[] = [
  {
    id: "1",
    title: "Low Soil Moisture",
    titleAr: "انخفاض رطوبة التربة",
    message: "Field A3 soil moisture dropped below 25%",
    messageAr: "انخفضت رطوبة التربة في الحقل A3 إلى أقل من 25%",
    type: "warning",
    status: "active",
    fieldId: "field-a3",
    fieldName: "الحقل A3",
    createdAt: "2025-01-25T08:30:00Z",
  },
  {
    id: "2",
    title: "Pest Detection",
    titleAr: "اكتشاف آفات",
    message: "Possible pest infestation detected in wheat field",
    messageAr: "تم اكتشاف إصابة محتملة بالآفات في حقل القمح",
    type: "critical",
    status: "active",
    fieldId: "field-b1",
    fieldName: "حقل القمح",
    createdAt: "2025-01-25T07:15:00Z",
  },
  {
    id: "3",
    title: "Irrigation Complete",
    titleAr: "اكتمال الري",
    message: "Scheduled irrigation for Field C2 completed successfully",
    messageAr: "اكتمل الري المجدول للحقل C2 بنجاح",
    type: "success",
    status: "resolved",
    fieldId: "field-c2",
    fieldName: "الحقل C2",
    createdAt: "2025-01-25T06:00:00Z",
    resolvedAt: "2025-01-25T06:45:00Z",
  },
  {
    id: "4",
    title: "Weather Warning",
    titleAr: "تحذير طقس",
    message: "High temperatures expected over the next 3 days",
    messageAr: "متوقع ارتفاع درجات الحرارة خلال الأيام الثلاثة القادمة",
    type: "warning",
    status: "acknowledged",
    createdAt: "2025-01-24T18:00:00Z",
    acknowledgedAt: "2025-01-24T19:30:00Z",
  },
  {
    id: "5",
    title: "Sensor Offline",
    titleAr: "الحساس غير متصل",
    message: "IoT sensor in Field D1 is not responding",
    messageAr: "حساس إنترنت الأشياء في الحقل D1 لا يستجيب",
    type: "critical",
    status: "active",
    fieldId: "field-d1",
    fieldName: "الحقل D1",
    createdAt: "2025-01-25T09:00:00Z",
  },
];

const typeFilters: Array<{ value: AlertType | "all"; label: string; labelAr: string }> = [
  { value: "all", label: "All Types", labelAr: "جميع الأنواع" },
  { value: "critical", label: "Critical", labelAr: "حرج" },
  { value: "warning", label: "Warning", labelAr: "تحذير" },
  { value: "info", label: "Info", labelAr: "معلومات" },
  { value: "success", label: "Success", labelAr: "نجاح" },
];

const statusFilters: Array<{ value: AlertStatus | "all"; label: string; labelAr: string }> = [
  { value: "all", label: "All Status", labelAr: "جميع الحالات" },
  { value: "active", label: "Active", labelAr: "نشط" },
  { value: "acknowledged", label: "Acknowledged", labelAr: "تم الإقرار" },
  { value: "resolved", label: "Resolved", labelAr: "تم الحل" },
];

export default function AlertsClient() {
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState<AlertType | "all">("all");
  const [statusFilter, setStatusFilter] = useState<AlertStatus | "all">("all");

  const filteredAlerts = useMemo(() => {
    return mockAlerts.filter((alert) => {
      const matchesSearch =
        !searchTerm ||
        alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.titleAr.includes(searchTerm) ||
        alert.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.messageAr.includes(searchTerm);

      const matchesType = typeFilter === "all" || alert.type === typeFilter;
      const matchesStatus = statusFilter === "all" || alert.status === statusFilter;

      return matchesSearch && matchesType && matchesStatus;
    });
  }, [searchTerm, typeFilter, statusFilter]);

  const getTypeIcon = (type: AlertType) => {
    switch (type) {
      case "critical":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      default:
        return <Bell className="w-5 h-5 text-blue-500" />;
    }
  };

  const getTypeBadge = (type: AlertType) => {
    const styles = {
      critical: "bg-red-100 text-red-800",
      warning: "bg-yellow-100 text-yellow-800",
      info: "bg-blue-100 text-blue-800",
      success: "bg-green-100 text-green-800",
    };
    const labels = {
      critical: "حرج",
      warning: "تحذير",
      info: "معلومات",
      success: "نجاح",
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[type]}`}>
        {labels[type]}
      </span>
    );
  };

  const getStatusBadge = (status: AlertStatus) => {
    const styles = {
      active: "bg-red-100 text-red-800",
      acknowledged: "bg-yellow-100 text-yellow-800",
      resolved: "bg-green-100 text-green-800",
    };
    const labels = {
      active: "نشط",
      acknowledged: "تم الإقرار",
      resolved: "تم الحل",
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("ar-SA", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const activeCount = mockAlerts.filter((a) => a.status === "active").length;
  const criticalCount = mockAlerts.filter((a) => a.type === "critical" && a.status === "active").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">التنبيهات</h1>
          <p className="text-gray-500 mt-1">Alerts & Notifications</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
            {activeCount} نشط
          </span>
          {criticalCount > 0 && (
            <span className="px-3 py-1 bg-red-600 text-white rounded-full text-sm font-medium">
              {criticalCount} حرج
            </span>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Bell className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي التنبيهات</div>
              <div className="text-xl font-bold text-gray-900">{mockAlerts.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <XCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">حرجة</div>
              <div className="text-xl font-bold text-red-600">{criticalCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تحذيرات</div>
              <div className="text-xl font-bold text-yellow-600">
                {mockAlerts.filter((a) => a.type === "warning").length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تم الحل</div>
              <div className="text-xl font-bold text-green-600">
                {mockAlerts.filter((a) => a.status === "resolved").length}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في التنبيهات..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as AlertType | "all")}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {typeFilters.map((filter) => (
            <option key={filter.value} value={filter.value}>
              {filter.labelAr}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as AlertStatus | "all")}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {statusFilters.map((filter) => (
            <option key={filter.value} value={filter.value}>
              {filter.labelAr}
            </option>
          ))}
        </select>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="bg-white rounded-lg border p-8 text-center text-gray-500">
            لا توجد تنبيهات مطابقة للبحث
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-white rounded-lg border p-4 hover:shadow-md transition-shadow ${
                alert.status === "active" && alert.type === "critical"
                  ? "border-red-300 bg-red-50"
                  : ""
              }`}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 mt-1">{getTypeIcon(alert.type)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <h3 className="font-semibold text-gray-900">{alert.titleAr}</h3>
                    {getTypeBadge(alert.type)}
                    {getStatusBadge(alert.status)}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{alert.messageAr}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(alert.createdAt)}
                    </span>
                    {alert.fieldName && (
                      <span className="text-sahool-green-600 font-medium">
                        {alert.fieldName}
                      </span>
                    )}
                  </div>
                </div>
                {alert.status === "active" && (
                  <div className="flex gap-2">
                    <button className="px-3 py-1 text-sm bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700">
                      إقرار
                    </button>
                    <button className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                      حل
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
