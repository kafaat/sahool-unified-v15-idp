"use client";

import React, { useState, useMemo } from "react";
import {
  BellOff,
  Check,
  CheckCheck,
  Clock,
  Search,
  Settings,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useToast } from "@/components/ui/toast";
import {
  useNotifications,
  useUnreadCount,
  useMarkRead,
  useMarkAllRead,
} from "@/features/notifications";
import type {
  NotificationType,
  NotificationPriority,
  NotificationFilters,
} from "@/features/notifications";

const typeFilters: Array<{
  value: NotificationType | "all";
  label: string;
  labelAr: string;
}> = [
  { value: "all", label: "All", labelAr: "الكل" },
  { value: "alert", label: "Alerts", labelAr: "تنبيهات" },
  { value: "warning", label: "Warnings", labelAr: "تحذيرات" },
  { value: "info", label: "Info", labelAr: "معلومات" },
  { value: "success", label: "Success", labelAr: "نجاح" },
];

const readFilters: Array<{
  value: "all" | "unread" | "read";
  label: string;
  labelAr: string;
}> = [
  { value: "all", label: "All", labelAr: "الكل" },
  { value: "unread", label: "Unread", labelAr: "غير مقروء" },
  { value: "read", label: "Read", labelAr: "مقروء" },
];

/**
 * Group notifications by date: Today / Yesterday / Older
 */
function groupByDate<
  T extends { createdAt: string },
>(items: T[]): { label: string; labelAr: string; items: T[] }[] {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 86400000);

  const groups: { label: string; labelAr: string; items: T[] }[] = [
    { label: "Today", labelAr: "اليوم", items: [] },
    { label: "Yesterday", labelAr: "أمس", items: [] },
    { label: "Older", labelAr: "أقدم", items: [] },
  ];

  for (const item of items) {
    const date = new Date(item.createdAt);
    if (date >= today) {
      groups[0]!.items.push(item);
    } else if (date >= yesterday) {
      groups[1]!.items.push(item);
    } else {
      groups[2]!.items.push(item);
    }
  }

  return groups.filter((g) => g.items.length > 0);
}

export default function NotificationsClient() {
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState<NotificationType | "all">(
    "all",
  );
  const [readFilter, setReadFilter] = useState<"all" | "unread" | "read">(
    "all",
  );

  // Build API filters
  const apiFilters: NotificationFilters = useMemo(() => {
    const filters: NotificationFilters = {};
    if (typeFilter !== "all") filters.type = typeFilter;
    if (readFilter === "unread") filters.read = false;
    if (readFilter === "read") filters.read = true;
    return filters;
  }, [typeFilter, readFilter]);

  // Query hooks
  const {
    data: notifications = [],
    isLoading,
    isError,
    refetch,
  } = useNotifications(apiFilters);
  const { data: unreadCount = 0 } = useUnreadCount();

  // Mutation hooks
  const markRead = useMarkRead();
  const markAllRead = useMarkAllRead();

  // Local search filtering (search is client-side for responsiveness)
  const filteredNotifications = useMemo(() => {
    if (!searchTerm.trim()) return notifications;
    const term = searchTerm.toLowerCase();
    return notifications.filter(
      (n) =>
        n.title.toLowerCase().includes(term) ||
        n.titleAr.includes(searchTerm) ||
        n.message.toLowerCase().includes(term) ||
        n.messageAr.includes(searchTerm),
    );
  }, [notifications, searchTerm]);

  // Group filtered notifications by date
  const groupedNotifications = useMemo(
    () => groupByDate(filteredNotifications),
    [filteredNotifications],
  );

  const handleMarkRead = async (id: string) => {
    try {
      await markRead.mutateAsync(id);
      showToast({
        type: "success",
        messageAr: "تم تحديد الإشعار كمقروء",
        message: "Marked as read",
      });
    } catch {
      showToast({
        type: "error",
        messageAr: "فشل في تحديد الإشعار كمقروء",
        message: "Failed to mark as read",
      });
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllRead.mutateAsync();
      showToast({
        type: "success",
        messageAr: "تم تحديد جميع الإشعارات كمقروءة",
        message: "All notifications marked as read",
      });
    } catch {
      showToast({
        type: "error",
        messageAr: "فشل في تحديد الإشعارات كمقروءة",
        message: "Failed to mark all as read",
      });
    }
  };

  const getTypeIcon = (type: NotificationType) => {
    switch (type) {
      case "alert":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "system":
        return <Settings className="w-5 h-5 text-purple-500" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getPriorityBadge = (priority: NotificationPriority) => {
    const styles: Record<NotificationPriority, string> = {
      urgent: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
      high: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
      medium:
        "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
      low: "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
    };
    const labels: Record<NotificationPriority, string> = {
      urgent: "عاجل",
      high: "مرتفع",
      medium: "متوسط",
      low: "منخفض",
    };
    return (
      <span
        className={`px-2 py-0.5 rounded-full text-xs font-medium ${styles[priority]}`}
      >
        {labels[priority]}
      </span>
    );
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);

    if (diffMin < 1) return "الآن";
    if (diffMin < 60) return `منذ ${diffMin} دقيقة`;
    if (diffHour < 24) return `منذ ${diffHour} ساعة`;
    if (diffDay < 7) return `منذ ${diffDay} يوم`;

    return date.toLocaleDateString("ar-SA", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            الإشعارات
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Notifications</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            title="تحديث"
          >
            <RefreshCw
              className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`}
            />
          </button>
          {unreadCount > 0 && (
            <>
              <span className="px-3 py-1 bg-sahool-green-100 dark:bg-green-900/30 text-sahool-green-800 dark:text-green-400 rounded-full text-sm font-medium">
                {unreadCount} غير مقروء
              </span>
              <button
                onClick={handleMarkAllRead}
                disabled={markAllRead.isPending}
                className="flex items-center gap-1 px-3 py-1 text-sm bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 disabled:opacity-50"
              >
                <CheckCheck className="w-4 h-4" />
                <span>قراءة الكل</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
          <input
            type="text"
            placeholder="بحث في الإشعارات..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500 placeholder:text-gray-400 dark:placeholder:text-gray-500"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) =>
            setTypeFilter(e.target.value as NotificationType | "all")
          }
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {typeFilters.map((filter) => (
            <option key={filter.value} value={filter.value}>
              {filter.labelAr}
            </option>
          ))}
        </select>
        <select
          value={readFilter}
          onChange={(e) =>
            setReadFilter(e.target.value as "all" | "unread" | "read")
          }
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {readFilters.map((filter) => (
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
          <span className="mr-3 text-gray-500 dark:text-gray-400">
            جاري تحميل الإشعارات...
          </span>
        </div>
      )}

      {/* Error State */}
      {isError && !isLoading && (
        <div className="bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800 p-6 text-center">
          <XCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-700 dark:text-red-400 font-medium">
            فشل في تحميل الإشعارات
          </p>
          <p className="text-red-500 dark:text-red-400 text-sm mt-1">
            Failed to load notifications
          </p>
          <button
            onClick={() => refetch()}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
          >
            إعادة المحاولة
          </button>
        </div>
      )}

      {/* Notifications List - Grouped */}
      {!isLoading && !isError && (
        <div className="space-y-6">
          {filteredNotifications.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8 text-center text-gray-500 dark:text-gray-400">
              <BellOff className="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
              <p>لا توجد إشعارات</p>
              <p className="text-xs mt-1">No notifications found</p>
            </div>
          ) : (
            groupedNotifications.map((group) => (
              <div key={group.label}>
                {/* Group Header */}
                <div className="flex items-center gap-3 mb-3">
                  <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400">
                    {group.labelAr}
                  </h2>
                  <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    {group.items.length}
                  </span>
                </div>

                {/* Notification Items */}
                <div className="space-y-2">
                  {group.items.map((notification, index) => (
                    <div
                      key={notification.id}
                      className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-sm transition-all cursor-pointer animate-slide-in-up ${
                        !notification.read
                          ? "border-r-4 border-r-sahool-green-500 bg-sahool-green-50/30 dark:bg-green-900/10"
                          : ""
                      }`}
                      style={{
                        animationDelay: `${index * 40}ms`,
                        animationFillMode: "both",
                      }}
                      onClick={() => {
                        if (!notification.read)
                          handleMarkRead(notification.id);
                      }}
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 mt-0.5">
                          {getTypeIcon(notification.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <h3
                              className={`text-sm ${
                                !notification.read
                                  ? "font-bold text-gray-900 dark:text-white"
                                  : "font-medium text-gray-700 dark:text-gray-300"
                              }`}
                            >
                              {notification.titleAr}
                            </h3>
                            {getPriorityBadge(notification.priority)}
                            {!notification.read && (
                              <span className="w-2 h-2 bg-sahool-green-500 rounded-full animate-pulse-dot" />
                            )}
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                            {notification.messageAr}
                          </p>
                          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500 dark:text-gray-400">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDate(notification.createdAt)}
                            </span>
                          </div>
                        </div>
                        {!notification.read && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMarkRead(notification.id);
                            }}
                            disabled={markRead.isPending}
                            className="flex-shrink-0 p-1.5 text-gray-400 dark:text-gray-500 hover:text-sahool-green-600 dark:hover:text-green-400 rounded-lg hover:bg-sahool-green-50 dark:hover:bg-green-900/30"
                            title="تحديد كمقروء"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
