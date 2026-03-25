'use client';

/**
 * Admin Header
 * رأس الصفحة مع دعم الوضع الداكن
 *
 * Optimized: Notification dropdown, user menu dropdown, and mobile search overlay
 * are lazy-loaded via next/dynamic since they are hidden by default.
 */

import { useState, useEffect, useRef, useMemo, Suspense } from 'react';
import { Bell, Search, X } from 'lucide-react';
import { useAuth } from '@/stores/auth.store';
import { useNotifications } from '@/hooks/api/use-notifications';
import ThemeToggle from '@/components/ui/ThemeToggle';
import Breadcrumbs from '@/components/ui/Breadcrumbs';
import dynamic from 'next/dynamic';

// Lazy-load dropdown panels -- they are only visible after user interaction
const NotificationsDropdown = dynamic(() => import('@/components/layout/NotificationsDropdown'), {
  ssr: false,
});

const UserMenuDropdown = dynamic(() => import('@/components/layout/UserMenuDropdown'), {
  ssr: false,
});

const MobileSearchOverlay = dynamic(() => import('@/components/layout/MobileSearchOverlay'), {
  ssr: false,
});

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
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchOverlay, setShowSearchOverlay] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationsRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout();
  };

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
      if (notificationsRef.current && !notificationsRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch real notifications from API (auto-refreshes every 30s)
  const { data: apiNotifications } = useNotifications({ limit: 10 });

  const notifications = useMemo(
    () =>
      (apiNotifications ?? []).map((n) => ({
        id: n.id,
        type: n.type,
        title: n.title,
        message: n.message,
        time: n.createdAt,
        unread: !n.read,
      })),
    [apiNotifications]
  );

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
                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{subtitle}</p>
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
                    type="button"
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                    aria-label="مسح البحث"
                  >
                    <X className="w-3 h-3 text-gray-400" />
                  </button>
                )}
              </div>

              {/* Mobile search button */}
              <button
                type="button"
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
              type="button"
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

            {/* Notifications dropdown - lazy loaded */}
            {showNotifications && (
              <Suspense fallback={null}>
                <NotificationsDropdown notifications={notifications} unreadCount={unreadCount} />
              </Suspense>
            )}
          </div>

          {/* User Menu */}
          <div ref={userMenuRef} className="relative">
            <button
              type="button"
              onClick={() => setShowUserMenu(!showUserMenu)}
              aria-expanded={showUserMenu}
              aria-haspopup="true"
              aria-label="قائمة المستخدم"
              className="flex items-center gap-2 p-1.5 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
              suppressHydrationWarning
            >
              <div className="w-8 h-8 bg-sahool-100 dark:bg-sahool-900/50 rounded-lg flex items-center justify-center">
                <span className="text-sahool-700 dark:text-sahool-300 font-bold text-sm">
                  {user?.name_ar?.charAt(0) || user?.name?.charAt(0) || 'م'}
                </span>
              </div>
              <span className="hidden sm:block text-sm font-medium max-w-[120px] truncate">
                {user?.name_ar || user?.name || 'مستخدم'}
              </span>
            </button>

            {/* User dropdown - lazy loaded */}
            {showUserMenu && (
              <Suspense fallback={null}>
                <UserMenuDropdown
                  userName={user?.name_ar || user?.name}
                  userEmail={user?.email}
                  onLogout={handleLogout}
                />
              </Suspense>
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

      {/* Mobile search overlay - lazy loaded */}
      {showSearchOverlay && (
        <Suspense fallback={null}>
          <MobileSearchOverlay
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onClose={() => setShowSearchOverlay(false)}
          />
        </Suspense>
      )}
    </header>
  );
}
