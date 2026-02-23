"use client";

/**
 * User Menu Dropdown for Web Dashboard
 * القائمة المنسدلة للمستخدم
 *
 * Lazy-loaded: Only rendered when the user clicks on their profile button.
 */

import { User, LogOut, Settings } from "lucide-react";

interface UserMenuDropdownProps {
  userName?: string;
  userEmail?: string;
  onProfileClick: () => void;
  onSettingsClick: () => void;
  onLogout: () => void;
  onClose: () => void;
  profileLabel: string;
  settingsLabel: string;
  logoutLabel: string;
}

export default function UserMenuDropdown({
  userName,
  userEmail,
  onProfileClick,
  onSettingsClick,
  onLogout,
  onClose,
  profileLabel,
  settingsLabel,
  logoutLabel,
}: UserMenuDropdownProps) {
  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-10"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Menu */}
      <div
        className="absolute end-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-20"
        role="menu"
        aria-label="قائمة خيارات المستخدم"
      >
        <div className="px-4 py-3 border-b border-gray-200">
          <div className="font-medium text-gray-900">
            {userName}
          </div>
          <div className="text-sm text-gray-500">{userEmail}</div>
        </div>

        <div className="py-2">
          <button
            onClick={onProfileClick}
            className="w-full flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors focus:outline-none focus:bg-gray-100"
            role="menuitem"
            aria-label={profileLabel}
          >
            <User className="w-4 h-4" />
            <div className="text-start">
              <div className="text-sm font-medium">{profileLabel}</div>
            </div>
          </button>

          <button
            onClick={onSettingsClick}
            className="w-full flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors focus:outline-none focus:bg-gray-100"
            role="menuitem"
            aria-label={settingsLabel}
          >
            <Settings className="w-4 h-4" />
            <div className="text-start">
              <div className="text-sm font-medium">{settingsLabel}</div>
            </div>
          </button>
        </div>

        <div className="border-t border-gray-200 pt-2">
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 transition-colors focus:outline-none focus:bg-red-50"
            role="menuitem"
            aria-label={logoutLabel}
          >
            <LogOut className="w-4 h-4" />
            <div className="text-start">
              <div className="text-sm font-medium">{logoutLabel}</div>
            </div>
          </button>
        </div>
      </div>
    </>
  );
}
