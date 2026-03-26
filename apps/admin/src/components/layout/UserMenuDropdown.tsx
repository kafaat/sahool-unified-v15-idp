'use client';

/**
 * User Menu Dropdown
 * القائمة المنسدلة للمستخدم
 *
 * Lazy-loaded: Only rendered when the user clicks on their profile avatar.
 */

import { Settings, HelpCircle, LogOut } from 'lucide-react';
import Link from 'next/link';

interface UserMenuDropdownProps {
  userName?: string;
  userEmail?: string;
  onLogout: () => void;
}

export default function UserMenuDropdown({ userName, userEmail, onLogout }: UserMenuDropdownProps) {
  return (
    <div
      role="menu"
      aria-label="خيارات المستخدم"
      className="absolute left-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50 animate-in fade-in slide-in-from-top-2"
    >
      <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{userName}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{userEmail}</p>
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
          type="button"
          onClick={onLogout}
          role="menuitem"
          className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          suppressHydrationWarning
        >
          <LogOut className="w-4 h-4" aria-hidden="true" />
          <span>تسجيل الخروج</span>
        </button>
      </div>
    </div>
  );
}
