// @ts-nocheck - Temporary fix for lucide-react types with React 19
'use client';

// Modern Header with Blur Effect
// رأس الصفحة الحديث بتأثير الضبابية

import { useState, useEffect } from 'react';
import {
  Bell,
  Search,
  LogOut,
  User,
  Moon,
  Sun,
  Settings,
  ChevronDown,
  Sparkles,
  X,
} from 'lucide-react';
import { getUser, logout, User as UserType } from '@/lib/auth';
import { cn } from '@/lib/utils';

interface ModernHeaderProps {
  title: string;
  subtitle?: string;
}

export default function ModernHeader({ title, subtitle }: ModernHeaderProps) {
  const [user, setUser] = useState<UserType | null>(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    setUser(getUser());

    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedTheme === 'dark' || (!savedTheme && systemPrefersDark);

    setIsDark(shouldBeDark);
    if (shouldBeDark) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  }, []);

  const handleLogout = () => {
    logout();
  };

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);

    if (newTheme) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
    }
  };

  // Mock notifications
  const notifications = [
    { id: 1, title: 'تنبيه جديد من المزرعة #124', time: 'منذ 5 دقائق', unread: true },
    { id: 2, title: 'تحديث حالة المستشعر', time: 'منذ ساعة', unread: true },
    { id: 3, title: 'تقرير يومي جاهز', time: 'منذ ساعتين', unread: false },
  ];

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <header className="sticky top-0 h-20 glass-header flex items-center justify-between px-6 z-40 animate-slide-up">
      {/* Title Section */}
      <div className="flex-1">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold gradient-text flex items-center gap-2">
            {title}
            <Sparkles className="w-5 h-5 text-sahool-500 animate-pulse" />
          </h1>
        </div>
        {subtitle && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{subtitle}</p>
        )}
      </div>

      {/* Actions Section */}
      <div className="flex items-center gap-3">
        {/* Search Bar */}
        <div className={cn(
          "relative transition-all duration-300",
          searchFocused ? "w-80" : "w-64"
        )}>
          <div className={cn(
            "glass-strong rounded-xl overflow-hidden transition-all duration-300",
            searchFocused && "ring-2 ring-sahool-500 shadow-lg"
          )}>
            <input
              type="text"
              placeholder="بحث..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
              className={cn(
                "w-full pl-10 pr-4 py-2.5 text-sm bg-transparent",
                "focus:outline-none transition-all duration-300",
                "text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              )}
            />
            {searchQuery ? (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            ) : (
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            )}
          </div>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className={cn(
            "p-3 rounded-xl glass-strong transition-all duration-300",
            "hover:glass hover:scale-110 active:scale-95",
            "text-gray-600 dark:text-gray-300"
          )}
          title={isDark ? "الوضع النهاري" : "الوضع الليلي"}
        >
          {isDark ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className={cn(
              "p-3 rounded-xl glass-strong transition-all duration-300 relative",
              "hover:glass hover:scale-110 active:scale-95",
              "text-gray-600 dark:text-gray-300",
              showNotifications && "ring-2 ring-sahool-500"
            )}
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-5 h-5 bg-gradient-to-br from-red-500 to-red-600 rounded-full text-white text-xs font-bold flex items-center justify-center shadow-lg animate-pulse">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute left-0 mt-2 w-80 glass-strong rounded-xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 py-2 animate-scale-in">
              <div className="px-4 py-3 border-b border-gray-200/50 dark:border-gray-700/50">
                <h3 className="font-semibold text-gray-900 dark:text-white">الإشعارات</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  لديك {unreadCount} إشعارات جديدة
                </p>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {notifications.map((notification) => (
                  <button
                    key={notification.id}
                    className={cn(
                      "w-full px-4 py-3 text-right transition-all duration-200",
                      "hover:glass",
                      notification.unread && "bg-sahool-50/50 dark:bg-sahool-900/20"
                    )}
                  >
                    <div className="flex items-start gap-3">
                      {notification.unread && (
                        <div className="w-2 h-2 rounded-full bg-sahool-500 mt-2 animate-pulse" />
                      )}
                      <div className="flex-1">
                        <p className={cn(
                          "text-sm",
                          notification.unread
                            ? "font-semibold text-gray-900 dark:text-white"
                            : "text-gray-600 dark:text-gray-400"
                        )}>
                          {notification.title}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          {notification.time}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <div className="px-4 py-2 border-t border-gray-200/50 dark:border-gray-700/50">
                <button className="text-sm text-sahool-600 dark:text-sahool-400 hover:text-sahool-700 dark:hover:text-sahool-300 font-medium transition-colors">
                  عرض جميع الإشعارات
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className={cn(
              "flex items-center gap-3 px-4 py-2 rounded-xl glass-strong",
              "transition-all duration-300 hover:glass hover:scale-105",
              "text-gray-700 dark:text-gray-200",
              showUserMenu && "ring-2 ring-sahool-500 scale-105"
            )}
          >
            <div className="relative">
              <div className="w-9 h-9 gradient-sahool rounded-xl flex items-center justify-center shadow-lg">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full" />
            </div>

            {user && (
              <div className="text-right">
                <span className="text-sm font-semibold block">
                  {user.name_ar || user.name}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  متصل
                </span>
              </div>
            )}

            <ChevronDown className={cn(
              "w-4 h-4 transition-transform duration-300",
              showUserMenu && "rotate-180"
            )} />
          </button>

          {/* User Dropdown */}
          {showUserMenu && (
            <div className="absolute left-0 mt-2 w-56 glass-strong rounded-xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 py-2 animate-scale-in">
              <div className="px-4 py-3 border-b border-gray-200/50 dark:border-gray-700/50">
                <p className="text-sm font-semibold text-gray-900 dark:text-white">
                  {user?.name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {user?.email}
                </p>
              </div>

              <div className="py-1">
                <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:glass transition-all">
                  <User className="w-4 h-4" />
                  <span>الملف الشخصي</span>
                </button>

                <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:glass transition-all">
                  <Settings className="w-4 h-4" />
                  <span>الإعدادات</span>
                </button>
              </div>

              <div className="pt-1 border-t border-gray-200/50 dark:border-gray-700/50">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:glass hover:text-red-700 dark:hover:text-red-300 transition-all"
                >
                  <LogOut className="w-4 h-4" />
                  <span>تسجيل الخروج</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Background gradient effect */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-sahool-500 to-transparent opacity-50" />
    </header>
  );
}
