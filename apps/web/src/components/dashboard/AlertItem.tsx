/**
 * SAHOOL Alert Item Component
 * عنصر التنبيه
 */

import React from "react";
import { Alert as AlertType, AlertSeverity } from "../../types";

interface AlertItemProps {
  alert: AlertType;
  onDismiss?: (id: string) => void;
  onAction?: (url: string) => void;
}

const severityConfig: Record<
  AlertSeverity,
  {
    icon: string;
    bgColor: string;
    borderColor: string;
    iconColor: string;
  }
> = {
  info: {
    icon: "ℹ️",
    bgColor: "bg-blue-50",
    borderColor: "border-blue-200",
    iconColor: "text-blue-500",
  },
  warning: {
    icon: "⚠️",
    bgColor: "bg-yellow-50",
    borderColor: "border-yellow-200",
    iconColor: "text-yellow-500",
  },
  critical: {
    icon: "🚨",
    bgColor: "bg-red-50",
    borderColor: "border-red-200",
    iconColor: "text-red-500",
  },
  emergency: {
    icon: "🆘",
    bgColor: "bg-red-100",
    borderColor: "border-red-400",
    iconColor: "text-red-700",
  },
};

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "الآن";
  if (diffMins < 60) return `منذ ${diffMins} دقيقة`;
  if (diffHours < 24) return `منذ ${diffHours} ساعة`;
  return `منذ ${diffDays} يوم`;
}

export const AlertItem = React.memo<AlertItemProps>(function AlertItem({
  alert,
  onDismiss,
  onAction,
}) {
  const config = severityConfig[alert.severity];
  const timeAgo = formatTimeAgo(alert.createdAt);

  return (
    <div
      className={`
        p-4 rounded-lg border-r-4
        ${config.bgColor} ${config.borderColor}
        ${alert.read ? "opacity-60" : ""}
        transition-all duration-200
      `}
      role="article"
      aria-label={`تنبيه: ${alert.titleAr} - ${alert.messageAr}`}
    >
      <div className="flex items-start gap-3">
        <div className={`text-xl ${config.iconColor}`} aria-hidden="true">
          {config.icon}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-semibold text-gray-900">{alert.titleAr}</h4>
            {onDismiss && (
              <button
                onClick={() => onDismiss(alert.id)}
                className="p-1 rounded-full hover:bg-gray-200 transition-colors text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-400"
                aria-label={`إغلاق تنبيه: ${alert.titleAr}`}
              >
                ✕
              </button>
            )}
          </div>

          <p className="text-sm text-gray-600 mt-1">{alert.messageAr}</p>

          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-500">
              {timeAgo}
              {alert.fieldName && ` • ${alert.fieldName}`}
            </span>

            {alert.actionUrl && (
              <button
                onClick={() => onAction?.(alert.actionUrl!)}
                className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label={`عرض تفاصيل: ${alert.titleAr}`}
              >
                <span>التفاصيل</span>
                <span aria-hidden="true">↗</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

export default AlertItem;
