"use client";

/**
 * Web Dashboard Header
 * رأس الصفحة للوحة التحكم
 *
 * Optimized: User menu dropdown is lazy-loaded via next/dynamic since it is
 * hidden by default and only shown after the user clicks their profile button.
 */

import React, { useState, useEffect, Suspense } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { Bell, ChevronDown } from "lucide-react";
import { useAuth } from "@/stores/auth.store";
import { Badge } from "@/components/ui/badge";
import { LocaleSwitcher } from "@/components/common/LocaleSwitcher";
import { clsx } from "clsx";
import dynamic from "next/dynamic";
import ThemeToggle from "@/components/ui/ThemeToggle";

// Lazy-load the user menu dropdown -- only shown on click interaction
const UserMenuDropdown = dynamic(
  () => import("@/components/layouts/UserMenuDropdown"),
  { ssr: false },
);

export const Header = React.memo(function Header() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const t = useTranslations("common");
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Close menu on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (showUserMenu && !target.closest("[data-user-menu]")) {
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener("click", handleClickOutside);
    }

    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, [showUserMenu]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  return (
    <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 flex items-center justify-between transition-colors">
      {/* Left section */}
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          {t("welcomeMessage")}, {user?.name_ar || user?.name}
        </h2>
        <Badge variant="success" size="sm">
          {user?.role}
        </Badge>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-4">
        {/* Locale Switcher */}
        <LocaleSwitcher />

        {/* Theme Toggle */}
        <ThemeToggle variant="dropdown" />

        {/* Notifications */}
        <button
          type="button"
          onClick={() => router.push("/notifications")}
          className="relative p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label={t("notifications") || "Notifications"}
        >
          <Bell className="w-5 h-5" />
          <span
            className="absolute top-1 end-1 w-2 h-2 bg-red-500 rounded-full"
            aria-label={t("newNotifications") || "New notifications"}
          />
        </button>

        {/* User Menu */}
        <div className="relative" data-user-menu>
          <button
            type="button"
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="قائمة المستخدم"
            aria-expanded={showUserMenu}
            aria-haspopup="true"
          >
            <div className="w-8 h-8 bg-sahool-green-600 rounded-full flex items-center justify-center text-white font-semibold">
              {user?.name_ar?.[0] || user?.name?.[0] || "U"}
            </div>
            <div className="text-start hidden sm:block">
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {user?.name_ar || user?.name}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">{user?.email}</div>
            </div>
            <ChevronDown
              className={clsx(
                "w-4 h-4 text-gray-400 transition-transform",
                showUserMenu && "rotate-180",
              )}
            />
          </button>

          {/* Dropdown Menu - lazy loaded */}
          {showUserMenu && (
            <Suspense fallback={null}>
              <UserMenuDropdown
                userName={user?.name_ar || user?.name}
                userEmail={user?.email}
                onProfileClick={() => {
                  setShowUserMenu(false);
                  router.push("/dashboard/profile");
                }}
                onSettingsClick={() => {
                  setShowUserMenu(false);
                  router.push("/dashboard/settings");
                }}
                onLogout={handleLogout}
                onClose={() => setShowUserMenu(false)}
                profileLabel={t("profile")}
                settingsLabel={t("settings")}
                logoutLabel={t("logout")}
              />
            </Suspense>
          )}
        </div>
      </div>
    </header>
  );
});
