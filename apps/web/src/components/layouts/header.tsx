'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Bell, User, LogOut, Settings, ChevronDown } from 'lucide-react';
import { useAuth } from '@/stores/auth.store';
import { Badge } from '@/components/ui/badge';
import { clsx } from 'clsx';
import { ThemeToggle } from '@/components/ui/ThemeToggle';

export const Header = React.memo(function Header() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Close menu on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (showUserMenu && !target.closest('[data-user-menu]')) {
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [showUserMenu]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <header className="h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 flex items-center justify-between">
      {/* Left section */}
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-gray-900">
          مرحباً، {user?.name_ar || user?.name}
        </h2>
        <Badge variant="success" size="sm">
          {user?.role}
        </Badge>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-4">
        {/* Theme Toggle */}
        <ThemeToggle />

        {/* Notifications */}
        <button
          className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="التنبيهات - لديك إشعارات جديدة"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 end-1 w-2 h-2 bg-red-500 rounded-full" aria-label="إشعارات جديدة" />
        </button>

        {/* User Menu */}
        <div className="relative" data-user-menu>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="قائمة المستخدم"
            aria-expanded={showUserMenu}
            aria-haspopup="true"
          >
            <div className="w-8 h-8 bg-sahool-green-600 rounded-full flex items-center justify-center text-white font-semibold">
              {user?.name_ar?.[0] || user?.name?.[0] || 'U'}
            </div>
            <div className="text-start hidden sm:block">
              <div className="text-sm font-medium text-gray-900">
                {user?.name_ar || user?.name}
              </div>
              <div className="text-xs text-gray-500">{user?.email}</div>
            </div>
            <ChevronDown
              className={clsx(
                'w-4 h-4 text-gray-400 transition-transform',
                showUserMenu && 'rotate-180'
              )}
            />
          </button>

          {/* Dropdown Menu */}
          {showUserMenu && (
            <>
              {/* Overlay */}
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowUserMenu(false)}
                aria-hidden="true"
              />

              {/* Menu */}
              <div className="absolute end-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-20" role="menu" aria-label="قائمة خيارات المستخدم">
                <div className="px-4 py-3 border-b border-gray-200">
                  <div className="font-medium text-gray-900">
                    {user?.name_ar || user?.name}
                  </div>
                  <div className="text-sm text-gray-500">{user?.email}</div>
                </div>

                <div className="py-2">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      router.push('/dashboard/profile');
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors focus:outline-none focus:bg-gray-100"
                    role="menuitem"
                    aria-label="الانتقال إلى الملف الشخصي"
                  >
                    <User className="w-4 h-4" />
                    <div className="text-start">
                      <div className="text-sm font-medium">الملف الشخصي</div>
                      <div className="text-xs text-gray-500">Profile</div>
                    </div>
                  </button>

                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      router.push('/dashboard/settings');
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors focus:outline-none focus:bg-gray-100"
                    role="menuitem"
                    aria-label="الانتقال إلى الإعدادات"
                  >
                    <Settings className="w-4 h-4" />
                    <div className="text-start">
                      <div className="text-sm font-medium">الإعدادات</div>
                      <div className="text-xs text-gray-500">Settings</div>
                    </div>
                  </button>
                </div>

                <div className="border-t border-gray-200 pt-2">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 transition-colors focus:outline-none focus:bg-red-50"
                    role="menuitem"
                    aria-label="تسجيل الخروج من الحساب"
                  >
                    <LogOut className="w-4 h-4" />
                    <div className="text-start">
                      <div className="text-sm font-medium">تسجيل الخروج</div>
                      <div className="text-xs opacity-70">Logout</div>
                    </div>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
});
