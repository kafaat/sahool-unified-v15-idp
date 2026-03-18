/**
 * Notifications Dropdown Panel
 * قائمة التنبيهات المنسدلة
 *
 * Lazy-loaded: Only rendered when the user opens the notifications panel.
 */

import { cn } from "@/lib/utils";
import Link from "next/link";

interface Notification {
  id: string | number;
  type: string;
  title: string;
  message: string;
  time: string;
  unread: boolean;
}

interface NotificationsDropdownProps {
  notifications: Notification[];
  unreadCount: number;
}

export default function NotificationsDropdown({
  notifications,
  unreadCount,
}: NotificationsDropdownProps) {
  return (
    <div className="absolute left-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50 animate-in fade-in slide-in-from-top-2">
      <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
        <h3 className="font-bold text-gray-900 dark:text-gray-100">
          التنبيهات
        </h3>
        {unreadCount > 0 && (
          <span className="text-xs text-sahool-600 dark:text-sahool-400">
            {unreadCount} جديد
          </span>
        )}
      </div>
      <div className="max-h-80 overflow-y-auto">
        {notifications.length === 0 && (
          <div className="px-4 py-6 text-center text-gray-500 dark:text-gray-400 text-sm">
            لا توجد تنبيهات جديدة
          </div>
        )}
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={cn(
              "px-4 py-3 border-b border-gray-50 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer",
              notification.unread && "bg-sahool-50/50 dark:bg-sahool-900/10"
            )}
          >
            <div className="flex items-start gap-3">
              <div
                className={cn(
                  "w-2 h-2 rounded-full mt-2 flex-shrink-0",
                  notification.type === "alert" && "bg-red-500",
                  notification.type === "success" && "bg-green-500",
                  notification.type === "info" && "bg-blue-500"
                )}
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {notification.title}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                  {notification.message}
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  {notification.time}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
      <Link
        href="/alerts"
        className="block px-4 py-3 text-center text-sm text-sahool-600 dark:text-sahool-400 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
      >
        عرض كل التنبيهات
      </Link>
    </div>
  );
}
