"use client";

// Alerts Management Page - Dynamic with Full CRUD
// صفحة إدارة التنبيهات - ديناميكية مع جميع عمليات CRUD

import { useEffect, useState, useMemo, useCallback } from "react";
import Header from "@/components/layout/Header";
import DataTable from "@/components/ui/DataTable";
import { formatDate, cn } from "@/lib/utils";
import {
  Bell,
  CloudRain,
  Bug,
  Droplets,
  Thermometer,
  AlertTriangle,
  Info,
  Plus,
  RefreshCw,
  Eye,
  Check,
  CheckCheck,
  Trash2,
  X,
  Save,
} from "lucide-react";
import { logger } from "../../lib/logger";
import { 
  alertService, 
  type Alert, 
  type CreateAlertData,
} from "@/lib/api";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [_searchQuery] = useState(""); // Reserved for future search feature
  const [typeFilter, setTypeFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadAlerts = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await alertService.getAll({
        page,
        limit: 20,
        type: typeFilter || undefined,
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
      });

      setAlerts(response.data);
      setTotalPages(response.meta.totalPages);
    } catch (error) {
      logger.error("Failed to load alerts:", error);
      setAlerts([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, typeFilter, severityFilter, statusFilter]);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  // CRUD Handlers
  async function handleCreate(data: CreateAlertData) {
    setIsSubmitting(true);
    try {
      await alertService.create(data);
      await loadAlerts();
      setShowCreateModal(false);
      logger.info("Alert created successfully");
    } catch (error) {
      logger.error("Failed to create alert:", error);
      alert("فشل إنشاء التنبيه. يرجى المحاولة مرة أخرى.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleAcknowledge(id: string) {
    try {
      await alertService.acknowledge(id);
      await loadAlerts();
      logger.info("Alert acknowledged successfully");
    } catch (error) {
      logger.error("Failed to acknowledge alert:", error);
      alert("فشل إقرار التنبيه. يرجى المحاولة مرة أخرى.");
    }
  }

  async function handleResolve(id: string, resolution?: string) {
    try {
      await alertService.resolve(id, resolution);
      await loadAlerts();
      logger.info("Alert resolved successfully");
      setShowDetailsModal(false);
      setSelectedAlert(null);
    } catch (error) {
      logger.error("Failed to resolve alert:", error);
      alert("فشل حل التنبيه. يرجى المحاولة مرة أخرى.");
    }
  }

  async function handleDelete(id: string) {
    setIsSubmitting(true);
    try {
      await alertService.delete(id);
      await loadAlerts();
      setShowDeleteModal(false);
      setSelectedAlert(null);
      logger.info("Alert deleted successfully");
    } catch (error) {
      logger.error("Failed to delete alert:", error);
      alert("فشل حذف التنبيه. يرجى المحاولة مرة أخرى.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const stats = useMemo(() => ({
    total: alerts.length,
    unread: alerts.filter((a) => a.status === "unread").length,
    critical: alerts.filter((a) => a.severity === "critical").length,
    acknowledged: alerts.filter((a) => a.status === "acknowledged").length,
  }), [alerts]);

  const getAlertIcon = (type: Alert["type"]) => {
    const icons = {
      weather: CloudRain,
      disease: Bug,
      pest: Bug,
      irrigation: Droplets,
      sensor: Thermometer,
      system: AlertTriangle,
    };
    return icons[type] || AlertTriangle;
  };

  const getAlertTypeLabel = (type: Alert["type"]) => {
    const labels = {
      weather: "طقس",
      disease: "مرض",
      pest: "آفات",
      irrigation: "ري",
      sensor: "مستشعر",
      system: "نظام",
    };
    return labels[type] || type;
  };

  const getSeverityColor = (severity: Alert["severity"]) => {
    const colors = {
      info: "bg-blue-100 text-blue-800 border-blue-200",
      warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
      critical: "bg-red-100 text-red-800 border-red-200",
    };
    return colors[severity];
  };

  const getSeverityLabel = (severity: Alert["severity"]) => {
    const labels = {
      info: "معلومات",
      warning: "تحذير",
      critical: "حرج",
    };
    return labels[severity];
  };

  const getSeverityIcon = (severity: Alert["severity"]) => {
    const icons = {
      info: Info,
      warning: AlertTriangle,
      critical: AlertTriangle,
    };
    return icons[severity];
  };

  const getStatusLabel = (status: Alert["status"]) => {
    const labels = {
      unread: "غير مقروء",
      read: "مقروء",
      acknowledged: "تم الإقرار",
      resolved: "تم الحل",
    };
    return labels[status];
  };

  const getStatusColor = (status: Alert["status"]) => {
    const colors = {
      unread: "bg-red-100 text-red-800",
      read: "bg-blue-100 text-blue-800",
      acknowledged: "bg-yellow-100 text-yellow-800",
      resolved: "bg-green-100 text-green-800",
    };
    return colors[status];
  };

  const columns = [
    {
      key: "type",
      header: "النوع",
      render: (alert: Alert) => {
        const Icon = getAlertIcon(alert.type);
        const SeverityIcon = getSeverityIcon(alert.severity);
        return (
          <div className="flex items-center gap-3">
            <div className={cn(
              "w-10 h-10 rounded-full flex items-center justify-center border-2",
              getSeverityColor(alert.severity)
            )}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <p className="font-medium text-gray-900">{getAlertTypeLabel(alert.type)}</p>
              <div className="flex items-center gap-1 text-xs">
                <SeverityIcon className="w-3 h-3" />
                <span>{getSeverityLabel(alert.severity)}</span>
              </div>
            </div>
          </div>
        );
      },
    },
    {
      key: "message",
      header: "الرسالة",
      render: (alert: Alert) => (
        <div>
          <p className="font-medium text-gray-900">{alert.titleAr}</p>
          <p className="text-sm text-gray-600 line-clamp-2">{alert.messageAr}</p>
        </div>
      ),
    },
    {
      key: "field",
      header: "الحقل",
      render: (alert: Alert) => (
        <span className="text-gray-700">{alert.fieldName || "عام"}</span>
      ),
    },
    {
      key: "status",
      header: "الحالة",
      render: (alert: Alert) => (
        <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getStatusColor(alert.status))}>
          {getStatusLabel(alert.status)}
        </span>
      ),
    },
    {
      key: "createdAt",
      header: "التاريخ",
      render: (alert: Alert) => (
        <span className="text-sm text-gray-600">{formatDate(alert.createdAt)}</span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (alert: Alert) => (
        <div className="flex items-center gap-1">
          <button 
            onClick={(e) => {
              e.stopPropagation();
              setSelectedAlert(alert);
              setShowDetailsModal(true);
            }}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="عرض التفاصيل"
          >
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          {alert.status === "unread" && (
            <button 
              onClick={(e) => {
                e.stopPropagation();
                handleAcknowledge(alert.id);
              }}
              className="p-2 hover:bg-yellow-50 rounded-lg transition-colors"
              title="إقرار"
            >
              <Check className="w-4 h-4 text-yellow-600" />
            </button>
          )}
          {alert.status !== "resolved" && (
            <button 
              onClick={(e) => {
                e.stopPropagation();
                handleResolve(alert.id);
              }}
              className="p-2 hover:bg-green-50 rounded-lg transition-colors"
              title="حل"
            >
              <CheckCheck className="w-4 h-4 text-green-600" />
            </button>
          )}
          <button 
            onClick={(e) => {
              e.stopPropagation();
              setSelectedAlert(alert);
              setShowDeleteModal(true);
            }}
            className="p-2 hover:bg-red-50 rounded-lg transition-colors"
            title="حذف"
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      ),
      className: "w-40",
    },
  ];

  return (
    <div className="p-6">
      <Header title="إدارة التنبيهات والإشعارات" subtitle={`${alerts.length} تنبيه`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Bell className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-500">إجمالي التنبيهات</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.unread}</p>
              <p className="text-sm text-gray-500">غير مقروء</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.critical}</p>
              <p className="text-sm text-gray-500">حرج</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Check className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.acknowledged}</p>
              <p className="text-sm text-gray-500">تم الإقرار</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white rounded-xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الأنواع</option>
            <option value="weather">طقس</option>
            <option value="disease">مرض</option>
            <option value="pest">آفات</option>
            <option value="irrigation">ري</option>
            <option value="sensor">مستشعر</option>
            <option value="system">نظام</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل المستويات</option>
            <option value="info">معلومات</option>
            <option value="warning">تحذير</option>
            <option value="critical">حرج</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="unread">غير مقروء</option>
            <option value="read">مقروء</option>
            <option value="acknowledged">تم الإقرار</option>
            <option value="resolved">تم الحل</option>
          </select>

          <button
            onClick={loadAlerts}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            title="تحديث"
          >
            <RefreshCw className={cn("w-5 h-5 text-gray-600", isLoading && "animate-spin")} />
          </button>
          <button 
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            إنشاء تنبيه
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white rounded-xl border border-gray-100 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-12 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={alerts}
            keyExtractor={(alert) => alert.id}
            emptyMessage="لا يوجد تنبيهات"
          />
        )}
      </div>

      {/* Create Alert Modal */}
      {showCreateModal && (
        <AlertFormModal
          title="إنشاء تنبيه جديد"
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreate}
          isSubmitting={isSubmitting}
        />
      )}

      {/* Alert Details Modal */}
      {showDetailsModal && selectedAlert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-gray-900">تفاصيل التنبيه</h3>
              <button
                onClick={() => {
                  setShowDetailsModal(false);
                  setSelectedAlert(null);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-500">النوع والمستوى</label>
                <div className="flex items-center gap-3 mt-1">
                  <span className="px-3 py-1 bg-gray-100 rounded-lg text-sm">
                    {getAlertTypeLabel(selectedAlert.type)}
                  </span>
                  <span className={cn(
                    "px-3 py-1 rounded-lg text-sm font-medium",
                    getSeverityColor(selectedAlert.severity)
                  )}>
                    {getSeverityLabel(selectedAlert.severity)}
                  </span>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">العنوان</label>
                <p className="text-lg font-medium text-gray-900 mt-1">{selectedAlert.titleAr}</p>
                <p className="text-sm text-gray-600">{selectedAlert.title}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">الرسالة</label>
                <p className="text-gray-900 mt-1">{selectedAlert.messageAr}</p>
                <p className="text-sm text-gray-600 mt-1">{selectedAlert.message}</p>
              </div>

              {selectedAlert.fieldName && (
                <div>
                  <label className="text-sm font-medium text-gray-500">الحقل</label>
                  <p className="text-gray-900 mt-1">{selectedAlert.fieldName}</p>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-gray-500">المصدر</label>
                <p className="text-gray-900 mt-1">{selectedAlert.source}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">التاريخ</label>
                <p className="text-gray-900 mt-1">{formatDate(selectedAlert.createdAt)}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">الحالة</label>
                <p className="mt-1">
                  <span className={cn("px-3 py-1 rounded-full text-sm font-medium", getStatusColor(selectedAlert.status))}>
                    {getStatusLabel(selectedAlert.status)}
                  </span>
                </p>
              </div>

              {selectedAlert.status !== "resolved" && (
                <div className="flex gap-3 pt-4 border-t">
                  {selectedAlert.status === "unread" && (
                    <button
                      onClick={() => handleAcknowledge(selectedAlert.id)}
                      className="flex-1 px-4 py-2 border border-yellow-300 bg-yellow-50 text-yellow-700 rounded-lg hover:bg-yellow-100 transition-colors"
                    >
                      <Check className="w-4 h-4 inline mr-2" />
                      إقرار
                    </button>
                  )}
                  <button
                    onClick={() => handleResolve(selectedAlert.id)}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <CheckCheck className="w-4 h-4 inline mr-2" />
                    حل
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && selectedAlert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold text-gray-900 mb-4">تأكيد الحذف</h3>
            <p className="text-gray-600 mb-6">
              هل أنت متأكد من حذف التنبيه <strong>{selectedAlert.titleAr}</strong>؟
              هذا الإجراء لا يمكن التراجع عنه.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setSelectedAlert(null);
                }}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                إلغاء
              </button>
              <button
                onClick={() => handleDelete(selectedAlert.id)}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? "جاري الحذف..." : "حذف"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            السابق
          </button>
          <span className="px-4 py-2 text-gray-600">
            صفحة {page} من {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            التالي
          </button>
        </div>
      )}
    </div>
  );
}

// Alert Form Modal Component
function AlertFormModal({
  title,
  onClose,
  onSubmit,
  isSubmitting,
}: {
  title: string;
  onClose: () => void;
  onSubmit: (data: CreateAlertData) => void;
  isSubmitting: boolean;
}) {
  const [formData, setFormData] = useState<CreateAlertData>({
    type: "system",
    severity: "info",
    title: "",
    titleAr: "",
    message: "",
    messageAr: "",
    source: "admin",
    fieldId: "",
    metadata: {},
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900">{title}</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                النوع
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as Alert["type"] })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
              >
                <option value="weather">طقس</option>
                <option value="disease">مرض</option>
                <option value="pest">آفات</option>
                <option value="irrigation">ري</option>
                <option value="sensor">مستشعر</option>
                <option value="system">نظام</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                المستوى
              </label>
              <select
                value={formData.severity}
                onChange={(e) => setFormData({ ...formData, severity: e.target.value as Alert["severity"] })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
              >
                <option value="info">معلومات</option>
                <option value="warning">تحذير</option>
                <option value="critical">حرج</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              العنوان (عربي)
            </label>
            <input
              type="text"
              required
              value={formData.titleAr}
              onChange={(e) => setFormData({ ...formData, titleAr: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              العنوان (English)
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              الرسالة (عربي)
            </label>
            <textarea
              required
              rows={3}
              value={formData.messageAr}
              onChange={(e) => setFormData({ ...formData, messageAr: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              الرسالة (English)
            </label>
            <textarea
              required
              rows={3}
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              معرف الحقل (اختياري)
            </label>
            <input
              type="text"
              value={formData.fieldId}
              onChange={(e) => setFormData({ ...formData, fieldId: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
              placeholder="field-123"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" />
              {isSubmitting ? "جاري الإنشاء..." : "إنشاء"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
