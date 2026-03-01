"use client";

/**
 * SAHOOL Alert Panel Component
 * لوحة التنبيهات
 */

import React, { useState } from "react";
import { Alert as AlertType } from "../../types";
import { AlertItem } from "./AlertItem";

interface AlertPanelProps {
  alerts: AlertType[];
  onDismiss?: (id: string) => void;
  onDismissAll?: () => void;
  onAction?: (url: string) => void;
  maxVisible?: number;
}

export const AlertPanel = React.memo<AlertPanelProps>(function AlertPanel({
  alerts,
  onDismiss,
  onDismissAll,
  onAction,
  maxVisible = 5,
}) {
  const [filter, setFilter] = useState<"all" | "unread">("unread");

  const filteredAlerts =
    filter === "unread" ? alerts.filter((a) => !a.read) : alerts;

  const visibleAlerts = filteredAlerts.slice(0, maxVisible);
  const unreadCount = alerts.filter((a) => !a.read).length;

  return (
    <div
      className="bg-white rounded-xl shadow-sm border border-gray-200"
      role="region"
      aria-label="لوحة التنبيهات"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl" aria-hidden="true">
              🔔
            </span>
            <h3 className="font-semibold text-gray-900">التنبيهات</h3>
            {unreadCount > 0 && (
              <span
                className="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-600 rounded-full"
                aria-label={`${unreadCount} تنبيهات غير مقروءة`}
              >
                {unreadCount}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setFilter(filter === "all" ? "unread" : "all")}
              className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label={
                filter === "all" ? "عرض غير المقروءة فقط" : "عرض جميع التنبيهات"
              }
              title={filter === "all" ? "غير المقروءة فقط" : "عرض الكل"}
            >
              🔽
            </button>

            {unreadCount > 0 && onDismissAll && (
              <button
                type="button"
                onClick={onDismissAll}
                className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="تعيين جميع التنبيهات كمقروءة"
                title="تعيين الكل كمقروء"
              >
                ✓✓
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Alert List */}
      <div
        className="p-4 space-y-3 max-h-96 overflow-y-auto"
        role="list"
        aria-label="قائمة التنبيهات"
      >
        {visibleAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500" role="status">
            <span className="text-4xl opacity-20" aria-hidden="true">
              🔔
            </span>
            <p className="mt-2">لا توجد تنبيهات</p>
          </div>
        ) : (
          visibleAlerts.map((alert) => (
            <AlertItem
              key={alert.id}
              alert={alert}
              onDismiss={onDismiss}
              onAction={onAction}
            />
          ))
        )}
      </div>

      {/* Footer */}
      {filteredAlerts.length > maxVisible && (
        <div className="p-3 border-t border-gray-100 text-center">
          <button
            type="button"
            className="text-sm text-blue-600 hover:text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label={`عرض جميع التنبيهات - ${filteredAlerts.length} تنبيه`}
          >
            عرض كل التنبيهات ({filteredAlerts.length})
          </button>
        </div>
      )}
    </div>
  );
});

export default AlertPanel;
