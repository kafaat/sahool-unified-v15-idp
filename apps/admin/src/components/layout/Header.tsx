"use client";

/**
 * Admin Header
 * رأس الصفحة مع دعم الوضع الداكن
 */

import { useState, useEffect, useRef } from "react";
import { Bell, Search, LogOut, Settings, HelpCircle, X } from "lucide-react";
import { useAuth } from "@/stores/auth.store";
import ThemeToggle from "@/components/ui/ThemeToggle";
import Breadcrumbs from "@/components/ui/Breadcrumbs";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface HeaderProps {
  title: string;
  subtitle?: string;
  showBreadcrumbs?: boolean;
  showSearch?: boolean;
  actions?: React.ReactNode;
}

export default function Header({
  title,
  subtitle,
  showBreadcrumbs = true,
  showSearch = true,
  actions,
}: HeaderProps) {
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [showSearchOverlay, setShowSearchOverlay] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationsRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout();
  };

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target as Node)
      ) {
        setShowUserMenu(false);
      }
      if (
        notificationsRef.current &&
        !notificationsRef.current.contains(event.target as Node)
      ) {
        setShowNotifications(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Mock notifications
  const notifications = [
    {
      id: 1,
      type: "alert",
      title: "تنبيه جفاف",
      message: "حقل القمح يحتاج للري",
      time: "منذ 5 دقائق",
      unread: true,
    },
    {
      id: 2,
      type: "success",
      title: "تم الحصاد",
      message: "اكتمل حصاد حقل الشعير",
      time: "منذ ساعة",
      unread: true,
    },
    {
      id: 3,
      type: "info",
      title: "تحديث النظام",
      message: "تم تحديث النظام بنجاح",
      time: "منذ 3 ساعات",
      unread: false,
    },
  ];

  const unreadCount = notifications.filter((n) => n.unread).length;

  return (
    <header className="sticky top-0 z-30 bg-white dark:bg-gray-900 border-b border-gray-100 dark:border-gray-800">
      {/* Main header row */}
      <div className="h-16 flex items-center justify-between px-6">
        {/* Left side - Title and Breadcrumbs */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-4">
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100 truncate">
                {title}
              </h1>
              {subtitle && (
                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Right side - Actions */}
        <div className="flex items-center gap-2">
          {/* Custom actions */}
          {actions}

          {/* Search */}
          {showSearch && (
            <>
              {/* Desktop search */}
              <div className="hidden md:block relative" suppressHydrationWarning>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="بحث..."
                  aria-label="بحث في لوحة التحكم"
                  className="w-64 pl-10 pr-4 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:border-transparent bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                />
                <Search
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
                  aria-hidden="true"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <X className="w-3 h-3 text-gray-400" />
                  </button>
                )}
              </div>

              {/* Mobile search button */}
              <button
                onClick={() => setShowSearchOverlay(true)}
                className="md:hidden p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                aria-label="بحث"
              >
                <Search className="w-5 h-5" />
              </button>
            </>
          )}

          {/* Theme Toggle */}
          <ThemeToggle variant="dropdown" />

          {/* Notifications */}
          <div ref={notificationsRef} className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              aria-label="التنبيهات"
              aria-expanded={showNotifications}
              className="relative p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              suppressHydrationWarning
            >
              <Bell className="w-5 h-5" aria-hidden="true" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 flex items-center justify-center min-w-[18px] h-[18px] text-xs font-bold bg-red-500 text-white rounded-full px-1">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notifications dropdown */}
            {showNotifications && (
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
            )}
          </div>

          {/* User Menu */}
          <div ref={userMenuRef} className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              aria-expanded={showUserMenu}
              aria-haspopup="true"
              aria-label="قائمة المستخدم"
              className="flex items-center gap-2 p-1.5 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
              suppressHydrationWarning
            >
              <div className="w-8 h-8 bg-sahool-100 dark:bg-sahool-900/50 rounded-lg flex items-center justify-center">
                <span className="text-sahool-700 dark:text-sahool-300 font-bold text-sm">
                  {user?.name_ar?.charAt(0) || user?.name?.charAt(0) || "م"}
                </span>
              </div>
              <span className="hidden sm:block text-sm font-medium max-w-[120px] truncate">
                {user?.name_ar || user?.name || "مستخدم"}
              </span>
            </button>

            {/* User dropdown */}
            {showUserMenu && (
              <div
                role="menu"
                aria-label="خيارات المستخدم"
                className="absolute left-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50 animate-in fade-in slide-in-from-top-2"
              >
                <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {user?.name_ar || user?.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {user?.email}
                  </p>
                </div>

                <div className="py-1">
                  <Link
                    href="/settings"
                    role="menuitem"
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                    <span>الإعدادات</span>
                  </Link>
                  <Link
                    href="/support"
                    role="menuitem"
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <HelpCircle className="w-4 h-4" />
                    <span>المساعدة</span>
                  </Link>
                </div>

                <div className="border-t border-gray-100 dark:border-gray-700 py-1">
                  <button
                    onClick={handleLogout}
                    role="menuitem"
                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    suppressHydrationWarning
                  >
                    <LogOut className="w-4 h-4" aria-hidden="true" />
                    <span>تسجيل الخروج</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Breadcrumbs row */}
      {showBreadcrumbs && (
        <div className="px-6 py-2 border-t border-gray-50 dark:border-gray-800">
          <Breadcrumbs />
        </div>
      )}

      {/* Mobile search overlay */}
      {showSearchOverlay && (
        <div className="fixed inset-0 z-50 bg-black/50 md:hidden">
          <div className="bg-white dark:bg-gray-900 p-4">
            <div className="flex items-center gap-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="بحث..."
                  autoFocus
                  className="w-full pl-10 pr-4 py-3 text-base border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:border-transparent bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                />
                <Search
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                  aria-hidden="true"
                />
              </div>
              <button
                onClick={() => setShowSearchOverlay(false)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
