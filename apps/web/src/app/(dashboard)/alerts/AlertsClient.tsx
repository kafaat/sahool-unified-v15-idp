"use client";

import React, { useState, useMemo, useCallback } from "react";
import {
  Bell,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Search,
  Wifi,
  WifiOff,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useToast } from "@/components/ui/toast";
import {
  useAlerts,
  useAlertStats,
  useAcknowledgeAlert,
  useResolveAlert,
  useDismissAlert,
  useAlertStream,
} from "@/features/alerts";
import type {
  Alert,
  AlertSeverity,
  AlertStatus,
  AlertFilters,
} from "@/features/alerts";

const severityFilters: Array<{
  value: AlertSeverity | "all";
  label: string;
  labelAr: string;
}> = [
  { value: "all", label: "All Severity", labelAr: "جميع المستويات" },
  { value: "emergency", label: "Emergency", labelAr: "طوارئ" },
  { value: "critical", label: "Critical", labelAr: "حرج" },
  { value: "warning", label: "Warning", labelAr: "تحذير" },
  { value: "info", label: "Info", labelAr: "معلومات" },
];

const statusFilters: Array<{
  value: AlertStatus | "all";
  label: string;
  labelAr: string;
}> = [
  { value: "all", label: "All Status", labelAr: "جميع الحالات" },
  { value: "active", label: "Active", labelAr: "نشط" },
  { value: "acknowledged", label: "Acknowledged", labelAr: "تم الإقرار" },
  { value: "resolved", label: "Resolved", labelAr: "تم الحل" },
  { value: "dismissed", label: "Dismissed", labelAr: "تم التجاهل" },
];

export default function AlertsClient() {
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState<
    AlertSeverity | "all"
  >("all");
  const [statusFilter, setStatusFilter] = useState<AlertStatus | "all">(
    "all",
  );

  // Build API filters
  const apiFilters: AlertFilters = useMemo(() => {
    const filters: AlertFilters = {};
    if (severityFilter !== "all") filters.severity = severityFilter;
    if (statusFilter !== "all") filters.status = statusFilter;
    if (searchTerm.trim()) filters.search = searchTerm.trim();
    return filters;
  }, [severityFilter, statusFilter, searchTerm]);

  // Query hooks
  const {
    data: alerts = [],
    isLoading,
    isError,
    refetch,
  } = useAlerts(apiFilters);
  const { data: stats } = useAlertStats();

  // Mutation hooks
  const acknowledgeAlert = useAcknowledgeAlert();
  const resolveAlert = useResolveAlert();
  const dismissAlert = useDismissAlert();

  // Real-time stream
  const handleStreamAlert = useCallback(
    (alert: Alert) => {
      showToast({
        type: alert.severity === "critical" || alert.severity === "emergency"
          ? "error"
          : "info",
        messageAr: `تنبيه جديد: ${alert.titleAr}`,
        message: `New alert: ${alert.title}`,
      });
    },
    [showToast],
  );

  const { isConnected } = useAlertStream(handleStreamAlert);

  // Action handlers
  const handleAcknowledge = async (id: string) => {
    try {
      await acknowledgeAlert.mutateAsync(id);
      showToast({
        type: "success",
        messageAr: "تم الإقرار بالتنبيه",
        message: "Alert acknowledged",
      });
    } catch {
      showToast({
        type: "error",
        messageAr: "فشل في الإقرار بالتنبيه",
        message: "Failed to acknowledge alert",
      });
    }
  };

  const handleResolve = async (id: string) => {
    try {
      await resolveAlert.mutateAsync({ id });
      showToast({
        type: "success",
        messageAr: "تم حل التنبيه",
        message: "Alert resolved",
      });
    } catch {
      showToast({
        type: "error",
        messageAr: "فشل في حل التنبيه",
        message: "Failed to resolve alert",
      });
    }
  };

  const handleDismiss = async (id: string) => {
    try {
      await dismissAlert.mutateAsync({ id });
      showToast({
        type: "success",
        messageAr: "تم تجاهل التنبيه",
        message: "Alert dismissed",
      });
    } catch {
      showToast({
        type: "error",
        messageAr: "فشل في تجاهل التنبيه",
        message: "Failed to dismiss alert",
      });
    }
  };

  const getSeverityIcon = (severity: AlertSeverity) => {
    switch (severity) {
      case "emergency":
      case "critical":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Bell className="w-5 h-5 text-blue-500" />;
    }
  };

  const getSeverityBadge = (severity: AlertSeverity) => {
    const styles: Record<AlertSeverity, string> = {
      emergency: "bg-red-200 text-red-900",
      critical: "bg-red-100 text-red-800",
      warning: "bg-yellow-100 text-yellow-800",
      info: "bg-blue-100 text-blue-800",
    };
    const labels: Record<AlertSeverity, string> = {
      emergency: "طوارئ",
      critical: "حرج",
      warning: "تحذير",
      info: "معلومات",
    };
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${styles[severity]}`}
      >
        {labels[severity]}
      </span>
    );
  };

  const getStatusBadge = (status: AlertStatus) => {
    const styles: Record<AlertStatus, string> = {
      active: "bg-red-100 text-red-800",
      acknowledged: "bg-yellow-100 text-yellow-800",
      resolved: "bg-green-100 text-green-800",
      dismissed: "bg-gray-100 text-gray-800",
    };
    const labels: Record<AlertStatus, string> = {
      active: "نشط",
      acknowledged: "تم الإقرار",
      resolved: "تم الحل",
      dismissed: "تم التجاهل",
    };
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}
      >
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

  const activeCount = stats?.byStatus?.active ?? 0;
  const criticalCount =
    (stats?.bySeverity?.critical ?? 0) + (stats?.bySeverity?.emergency ?? 0);
  const warningCount = stats?.bySeverity?.warning ?? 0;
  const resolvedCount = stats?.byStatus?.resolved ?? 0;
  const totalCount = stats?.total ?? alerts.length;

  const isMutating =
    acknowledgeAlert.isPending ||
    resolveAlert.isPending ||
    dismissAlert.isPending;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">التنبيهات</h1>
          <p className="text-gray-500 mt-1">Alerts & Notifications</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Stream connection status */}
          <span
            className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
              isConnected
                ? "bg-green-100 text-green-700"
                : "bg-gray-100 text-gray-500"
            }`}
          >
            {isConnected ? (
              <Wifi className="w-3 h-3" />
            ) : (
              <WifiOff className="w-3 h-3" />
            )}
            {isConnected ? "مباشر" : "غير متصل"}
          </span>
          <button
            onClick={() => refetch()}
            className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
            title="تحديث"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </button>
          {activeCount > 0 && (
            <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
              {activeCount} نشط
            </span>
          )}
          {criticalCount > 0 && (
            <span className="px-3 py-1 bg-red-600 text-white rounded-full text-sm font-medium">
              {criticalCount} حرج
            </span>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5 cursor-default">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Bell className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي التنبيهات</div>
              <div className="text-xl font-bold text-gray-900 animate-count-up">
                {totalCount}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5 cursor-default">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center ${criticalCount > 0 ? "animate-pulse-dot" : ""}`}>
              <XCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">حرجة</div>
              <div className="text-xl font-bold text-red-600 animate-count-up">
                {criticalCount}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5 cursor-default">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تحذيرات</div>
              <div className="text-xl font-bold text-yellow-600 animate-count-up">
                {warningCount}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5 cursor-default">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">تم الحل</div>
              <div className="text-xl font-bold text-green-600 animate-count-up">
                {resolvedCount}
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
          value={severityFilter}
          onChange={(e) =>
            setSeverityFilter(e.target.value as AlertSeverity | "all")
          }
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {severityFilters.map((filter) => (
            <option key={filter.value} value={filter.value}>
              {filter.labelAr}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) =>
            setStatusFilter(e.target.value as AlertStatus | "all")
          }
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {statusFilters.map((filter) => (
            <option key={filter.value} value={filter.value}>
              {filter.labelAr}
            </option>
          ))}
        </select>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-sahool-green-600 animate-spin" />
          <span className="mr-3 text-gray-500">جاري تحميل التنبيهات...</span>
        </div>
      )}

      {/* Error State */}
      {isError && !isLoading && (
        <div className="bg-red-50 rounded-lg border border-red-200 p-6 text-center">
          <XCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-700 font-medium">فشل في تحميل التنبيهات</p>
          <p className="text-red-500 text-sm mt-1">Failed to load alerts</p>
          <button
            onClick={() => refetch()}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
          >
            إعادة المحاولة
          </button>
        </div>
      )}

      {/* Alerts List */}
      {!isLoading && !isError && (
        <div className="space-y-4">
          {alerts.length === 0 ? (
            <div className="bg-white rounded-lg border p-8 text-center text-gray-500">
              <Bell className="w-10 h-10 mx-auto mb-3 text-gray-300" />
              <p>لا توجد تنبيهات مطابقة للبحث</p>
              <p className="text-xs mt-1">No matching alerts found</p>
            </div>
          ) : (
            alerts.map((alert, index) => (
              <div
                key={alert.id}
                className={`bg-white rounded-lg border p-4 hover:shadow-md transition-all duration-300 animate-slide-in-up ${
                  alert.status === "active" &&
                  (alert.severity === "critical" ||
                    alert.severity === "emergency")
                    ? "border-red-300 bg-red-50"
                    : ""
                }`}
                style={{ animationDelay: `${index * 50}ms`, animationFillMode: "both" }}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 mt-1">
                    {getSeverityIcon(alert.severity)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <h3 className="font-semibold text-gray-900">
                        {alert.titleAr}
                      </h3>
                      {getSeverityBadge(alert.severity)}
                      {getStatusBadge(alert.status)}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      {alert.messageAr}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatDate(alert.createdAt)}
                      </span>
                      {alert.fieldNameAr && (
                        <span className="text-sahool-green-600 font-medium">
                          {alert.fieldNameAr}
                        </span>
                      )}
                      {alert.fieldName && !alert.fieldNameAr && (
                        <span className="text-sahool-green-600 font-medium">
                          {alert.fieldName}
                        </span>
                      )}
                    </div>
                  </div>
                  {alert.status === "active" && (
                    <div className="flex gap-2 flex-shrink-0">
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={isMutating}
                        className="px-3 py-1 text-sm bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 disabled:opacity-50"
                      >
                        إقرار
                      </button>
                      <button
                        onClick={() => handleResolve(alert.id)}
                        disabled={isMutating}
                        className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                      >
                        حل
                      </button>
                      <button
                        onClick={() => handleDismiss(alert.id)}
                        disabled={isMutating}
                        className="px-3 py-1 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg disabled:opacity-50"
                        title="تجاهل"
                      >
                        ✕
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
